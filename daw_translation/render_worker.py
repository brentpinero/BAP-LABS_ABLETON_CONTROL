"""
render_worker.py — Headless audio render worker (spike S5 + sandbox MIDI mode).

Renders audio through an effect chain, and/or renders MIDI notes through an
instrument, using Spotify's `pedalboard` (JUCE/VST3+AU host). This file is the
GPL-isolation boundary: `pedalboard` is GPLv3, so the closed-source orchestrator
(render_pool.py) never imports it — it shells out to THIS file as a separate
process. Keep all pedalboard imports here.

A "chain" is a list of steps, each either:
  {"builtin": "Gain", "params": {"gain_db": 6.0}}        # pedalboard built-in DSP
  {"plugin": "/path/Plugin.vst3", "params": {"Drive": 0.5}}  # external VST3/AU

An "instrument" spec (for --midi mode) is one of:
  "fallback:<role>"                  # deterministic numpy proxy synth (midi_synth.py)
  "vst:/path/Instrument.vst3"        # external VST3 instrument, MIDI rendered by pedalboard
  "au:/path/Instrument.component"    # external AU instrument
  ...either plugin form may append "::/path/preset.vstpreset" to load a preset.

CLI (how the pool invokes it, one process per job):
    python render_worker.py --in in.wav --out out.wav --chain chain.json
    python render_worker.py --midi notes.json --bpm 88 --instrument fallback:drums --out out.wav
    python render_worker.py --midi notes.json --bpm 88 --instrument vst:/Library/Audio/Plug-Ins/VST3/Serum.vst3 --out out.wav
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import soundfile as sf

import midi_synth  # sibling module, numpy-only (no license concern)

# pedalboard (GPLv3) is imported LAZILY: fallback-synth renders with an empty FX
# chain never touch it, so they work in minimal environments too.
_pedalboard = None


def _pb():
    global _pedalboard
    if _pedalboard is None:
        import pedalboard as _pedalboard_mod
        _pedalboard = _pedalboard_mod
    return _pedalboard


def build_board(chain: list[dict]):
    """Turn a chain spec into a pedalboard.Pedalboard. Unknown params are skipped."""
    plugins = []
    for step in chain:
        if "builtin" in step:
            cls = getattr(_pb(), step["builtin"], None)
            if cls is None:
                raise ValueError(f"unknown builtin effect: {step['builtin']}")
            plugins.append(cls(**step.get("params", {})))
        elif "plugin" in step:
            plug = _pb().load_plugin(step["plugin"])
            for name, value in step.get("params", {}).items():
                if hasattr(plug, name):
                    try:
                        setattr(plug, name, value)
                    except Exception:  # noqa: BLE001  read-only / range — skip, don't crash
                        pass
            plugins.append(plug)
        else:
            raise ValueError(f"chain step needs 'builtin' or 'plugin': {step}")
    return _pb().Pedalboard(plugins)


def render_chain(audio: np.ndarray, sample_rate: int, chain: list[dict]) -> np.ndarray:
    """Render a mono/stereo float32 buffer through the chain. Pure function."""
    board = build_board(chain)
    return board(audio.astype("float32"), sample_rate)


def _sine(sample_rate: int = 44100, seconds: float = 1.0, freq: float = 440.0) -> np.ndarray:
    t = np.linspace(0, seconds, int(sample_rate * seconds), endpoint=False, dtype="float32")
    return (0.5 * np.sin(2 * np.pi * freq * t)).astype("float32")


def _load_notes(path: str) -> tuple[list[dict], float | None]:
    """Load notes from a JSON file. Accepts either a bare list of note dicts or
    {"notes": [...], "bpm"?: float, "bars"?: float} (bpm/bars ride along if present)."""
    with open(path, "r") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("notes", []), data.get("bars")
    return data, None


def _notes_to_midi_messages(notes: list[dict], bpm: float):
    """Note dicts (beats) -> mido messages with absolute times in seconds,
    the format pedalboard's ExternalPlugin instrument rendering accepts."""
    import mido  # local import: only needed for plugin instrument mode
    spb = 60.0 / max(1e-3, bpm)
    msgs = []
    for n in notes:
        pitch = max(0, min(127, int(n.get("pitch", 60))))
        vel = max(1, min(127, int(n.get("velocity", 100))))
        t0 = float(n.get("start_time", 0.0)) * spb
        t1 = t0 + max(0.02, float(n.get("duration", 0.25)) * spb)
        msgs.append(mido.Message("note_on", note=pitch, velocity=vel, time=t0))
        msgs.append(mido.Message("note_off", note=pitch, velocity=0, time=t1))
    msgs.sort(key=lambda m: m.time)
    return msgs


def render_midi(notes: list[dict], bpm: float, instrument: str, sr: int,
                bars: float | None = None, tail_seconds: float = 1.0,
                params: dict | None = None,
                raw_component_state: bytes | None = None) -> np.ndarray:
    """Render note dicts through an instrument spec. Returns float32 audio
    (mono for fallback, stereo [n,2] for plugins)."""
    if instrument.startswith("fallback:"):
        role = instrument.split(":", 1)[1] or "keys"
        return midi_synth.render_notes(notes, bpm, role=role, sr=sr,
                                       bars=bars, tail_seconds=tail_seconds)

    kind, _, rest = instrument.partition(":")
    if kind not in ("vst", "au"):
        raise ValueError(f"unknown instrument spec: {instrument!r} "
                         "(want fallback:<role>, vst:<path>[::preset], au:<path>[::preset])")
    plug_path, _, extra = rest.partition("::")
    preset, plugin_name = "", None
    if extra.startswith("name="):
        plugin_name = extra[5:]
    elif extra:
        preset = extra
    plug = (_pb().load_plugin(plug_path, plugin_name=plugin_name)
            if plugin_name else _pb().load_plugin(plug_path))
    if preset:
        try:
            plug.load_preset(preset)
        except Exception as e:  # noqa: BLE001 — preset failure shouldn't kill the render
            print(f"warning: preset load failed ({e}); rendering with default state",
                  file=sys.stderr)

    # native component-state transplant (e.g. a patch captured from a Live
    # project's .als ProcessorState) — the exact-state path; see juce_state.py
    if raw_component_state:
        import juce_state
        plug.raw_state = juce_state.swap_component(bytes(plug.raw_state),
                                                   raw_component_state)

    # named-param state transfer (same hasattr/setattr pattern as build_board);
    # this is the primary state mechanism — .fxp load_preset is unreliable (see
    # docs/fidelity_preflight.md)
    for name, value in (params or {}).items():
        if hasattr(plug, name):
            try:
                setattr(plug, name, value)
            except Exception:  # noqa: BLE001 — read-only/range params skipped
                pass

    msgs = _notes_to_midi_messages(notes, bpm)
    spb = 60.0 / max(1e-3, bpm)
    musical_end = (bars * 4.0 * spb) if bars is not None else (
        max((m.time for m in msgs), default=1.0))
    duration = musical_end + tail_seconds
    audio = plug(msgs, duration=duration, sample_rate=sr)
    return np.asarray(audio, dtype="float32").T if np.asarray(audio).ndim == 2 else np.asarray(audio, dtype="float32")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Headless render worker")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--in", dest="inp",
                     help="input wav path, or 'sine' to synthesize a test tone")
    src.add_argument("--midi", dest="midi",
                     help="notes JSON path ([{pitch,start_time,duration,velocity}] in beats)")
    ap.add_argument("--out", dest="out", required=True, help="output wav path")
    ap.add_argument("--chain", default="[]",
                    help="FX chain as a JSON string or a path to a .json file (default: none)")
    ap.add_argument("--sr", type=int, default=44100, help="sample rate")
    ap.add_argument("--bpm", type=float, default=120.0, help="tempo for --midi mode")
    ap.add_argument("--instrument", default="fallback:keys",
                    help="instrument spec for --midi mode (fallback:<role> | vst:<path>[::preset] | au:<path>[::preset])")
    ap.add_argument("--bars", type=float, default=None,
                    help="fix the musical length in bars (else derived from last note)")
    ap.add_argument("--tail-seconds", type=float, default=1.0,
                    help="silence/decay tail appended after the last bar")
    ap.add_argument("--params", default="",
                    help="named plugin-param dict as JSON string or path (state transfer)")
    ap.add_argument("--raw-state", default="",
                    help="path to a native component-state file (e.g. .als ProcessorState bytes)")
    args = ap.parse_args(argv)

    chain = json.loads(_read_maybe_file(args.chain))

    if args.midi:
        notes, bars_from_file = _load_notes(args.midi)
        params = json.loads(_read_maybe_file(args.params)) if args.params else None
        raw_cs = open(args.raw_state, "rb").read() if args.raw_state else None
        audio = render_midi(notes, args.bpm, args.instrument, args.sr,
                            bars=args.bars if args.bars is not None else bars_from_file,
                            tail_seconds=args.tail_seconds, params=params,
                            raw_component_state=raw_cs)
        sr = args.sr
    elif args.inp == "sine":
        audio, sr = _sine(args.sr), args.sr
    else:
        audio, sr = sf.read(args.inp, dtype="float32", always_2d=False)

    out = render_chain(audio, sr, chain) if chain else audio
    sf.write(args.out, out, sr)
    mode = f"midi[{args.instrument}]" if args.midi else "audio"
    print(f"rendered {args.out}  ({len(np.atleast_1d(out))} frames @ {sr}Hz, "
          f"{mode}, {len(chain)} fx step(s))")
    return 0


def _read_maybe_file(s: str) -> str:
    """Accept either an inline JSON string or a path to a JSON file."""
    stripped = s.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        return s
    with open(s, "r") as f:
        return f.read()


if __name__ == "__main__":
    sys.exit(main())
