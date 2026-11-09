"""
plughost_render.py — render MIDI through a VST3/AU instrument with plughost (no pedalboard).

Why: pedalboard cannot send a plugin a transport tempo, so tempo-synced patches (LFOs,
envelopes, delays) ran at the plugin's default tempo in every headless render — the cause of
the 6-14 dB Serum low-end gap against Ableton freezes. plughost's host (`host_rs`, built from
daw_bench/host_bakeoff) sends a playing transport at the song's tempo with every block, and
matches a Live freeze within +0.27 dB per band (daw_bench/host_bakeoff/RESULTS.md, finding 2).
The plugin runs in plughost's helper process, so a plugin crash fails this render, not ours.

plughost is MIT/Apache, so unlike render_worker.py this module needs no GPL process boundary.

Same contract as render_worker.render_midi for plugin instruments: notes in beats
(start_time, duration, pitch, velocity), bpm, sample rate, optional bars / tail / named params
/ native component state; returns float32 stereo audio shaped [frames, 2].

Binaries: build per daw_bench/host_bakeoff/README.md, or point PLUGHOST_HOST and
PLUGHOST_HELPER at them.
"""
from __future__ import annotations

import json
import os
import plistlib
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

import render_worker  # shared note clamps and render length (pedalboard is imported lazily there)

_ROOT = Path(__file__).resolve().parent.parent
BLOCK = 512
TIMEOUT_S = 300
PREROLL_S = 0.5     # silence before beat 0 so parameter smoothing settles (Serum ramps otherwise)
LATENCY_MARGIN = 8192  # extra frames rendered so a plugin's reported latency can be trimmed


def binaries() -> tuple[Path, Path]:
    """host_rs and its signed helper executable (env overrides, else the repo build)."""
    host = Path(os.environ.get("PLUGHOST_HOST", _ROOT / "build/host_rs/release/host_rs"))
    helper = Path(os.environ.get(
        "PLUGHOST_HELPER", _ROOT / "build/host_rs/PlughostHelper.app/Contents/MacOS/plughost-helper"))
    return host, helper


def available() -> bool:
    return all(p.exists() for p in binaries())


def parse_spec(instrument: str) -> dict:
    """render_worker instrument spec -> host_rs job fields.
    vst:<bundle.vst3>[::preset.vstpreset | ::name=<class name>]  |  au:<bundle.component>[...]"""
    kind, _, rest = instrument.partition(":")
    if kind not in ("vst", "au"):
        raise ValueError(f"plughost renders vst:/au: instruments, not {instrument!r}")
    path, _, extra = rest.partition("::")
    fields: dict = {}
    if extra.startswith("name="):
        fields["class_name"] = extra[5:]
    elif extra:
        fields["preset"] = extra
    if kind == "vst":
        fields.update(format="vst3", bundle=path)
    else:
        fields.update(format="au", au=au_codes(path))
    return fields


def au_codes(bundle: str) -> list[str]:
    """The first AudioComponents entry of an AU bundle: [type, subtype, manufacturer]."""
    with open(Path(bundle) / "Contents" / "Info.plist", "rb") as f:
        comp = plistlib.load(f)["AudioComponents"][0]
    return [comp["type"], comp["subtype"], comp["manufacturer"]]


def note_events(notes: list[dict], bpm: float, sr: int) -> list[dict]:
    """Beats -> host_rs note events in samples, with render_worker's clamps."""
    return [{"pitch": pitch, "start": round(t0 * sr), "dur": round((t1 - t0) * sr), "vel": vel}
            for pitch, vel, t0, t1 in render_worker._note_times(notes, bpm)]


def render_length(notes: list[dict], bpm: float, sr: int, bars: float | None, tail: float) -> int:
    """Frames to render: render_worker's musical length plus the tail."""
    return int(round((render_worker.musical_end(notes, bpm, bars) + tail) * sr))


def render_midi(notes: list[dict], bpm: float, instrument: str, sr: int,
                bars: float | None = None, tail_seconds: float = 1.0,
                params: dict | None = None,
                raw_component_state: bytes | None = None) -> np.ndarray:
    """Render notes through a plugin instrument with a transport at `bpm`. Raises RuntimeError
    with host_rs's error (stage and message) when the render fails."""
    host, helper = binaries()
    frames = render_length(notes, bpm, sr, bars, tail_seconds)
    with tempfile.TemporaryDirectory(prefix="plughost_render_") as tmp:
        tmp = Path(tmp)
        job = {**parse_spec(instrument), "sr": sr, "block": BLOCK, "notes": note_events(notes, bpm, sr),
               "bpm": bpm, "preroll_s": PREROLL_S, "stop_after": "a", "out_dir": str(tmp)}
        if raw_component_state:
            (tmp / "component_state.bin").write_bytes(raw_component_state)
            job["component_state"] = str(tmp / "component_state.bin")
        if params:
            job["params"] = params
        # Render the plugin's latency extra and trim it, so output starts at beat 0. The latency
        # is only known after load, so render a generous margin and trim what was reported.
        job["frames"] = frames + LATENCY_MARGIN
        (tmp / "job.json").write_text(json.dumps(job))
        proc = subprocess.run([str(host), str(tmp / "job.json"), str(helper)],
                              capture_output=True, text=True, timeout=TIMEOUT_S)
        result = json.loads((tmp / "result.json").read_text()) if (tmp / "result.json").exists() else {}
        if not result.get("ok"):
            raise RuntimeError(f"plughost render failed at {result.get('stage', '?')}: "
                               f"{result.get('error') or proc.stdout[-300:] or proc.returncode}")
        for skipped in result.get("params_skipped") or []:
            print(f"warning: param not applied: {skipped}", file=sys.stderr)
        latency = int(result.get("latency") or 0)
        if latency > LATENCY_MARGIN:
            raise RuntimeError(f"plugin latency {latency} exceeds the {LATENCY_MARGIN}-frame render margin")
        audio, _ = sf.read(tmp / "a.wav", dtype="float32", always_2d=True)
    return audio[latency:latency + frames]
