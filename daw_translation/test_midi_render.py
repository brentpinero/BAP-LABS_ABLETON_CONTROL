"""
test_midi_render.py — offline tests for the sandbox MIDI→audio render path.

Runs standalone (`python daw_translation/test_midi_render.py`) or under pytest.
No Ableton, no plugins required — plugin-instrument tests are gated behind the
SANDBOX_TEST_PLUGIN env var (set it to a .vst3/.component path to enable).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

import midi_synth  # noqa: E402
import render_pool  # noqa: E402

BPM = 88.0
SR = 44100


def _drum_notes():
    # one bar: kick beat 0, snare beat 1 & 3, hats 8ths
    notes = [{"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 118},
             {"pitch": 38, "start_time": 1.0, "duration": 0.5, "velocity": 110},
             {"pitch": 38, "start_time": 3.0, "duration": 0.5, "velocity": 110}]
    notes += [{"pitch": 42, "start_time": t / 2, "duration": 0.25, "velocity": 80}
              for t in range(8)]
    return notes


# --- fallback synth --------------------------------------------------------
def test_fallback_renders_nonzero_audio_of_correct_length():
    audio = midi_synth.render_notes(_drum_notes(), BPM, role="drums", sr=SR,
                                    bars=1, tail_seconds=0.5)
    expected = int((4 * 60.0 / BPM + 0.5) * SR)  # 1 bar + tail
    assert len(audio) == expected
    assert audio.dtype == np.float32
    assert float(np.max(np.abs(audio))) > 0.05, "render is silent"
    assert float(np.max(np.abs(audio))) <= 0.95, "render clips"


def test_kick_lands_at_beat_zero():
    audio = midi_synth.render_notes(
        [{"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 120}],
        BPM, role="drums", sr=SR, bars=1)
    head = float(np.sqrt(np.mean(audio[: int(0.1 * SR)] ** 2)))     # first 100ms
    late = float(np.sqrt(np.mean(audio[int(1.0 * SR): int(1.5 * SR)] ** 2)))
    assert head > 10 * max(late, 1e-9), "kick energy not at the downbeat"


def test_pitched_roles_render_and_differ():
    note = [{"pitch": 57, "start_time": 0.0, "duration": 2.0, "velocity": 100}]
    bass = midi_synth.render_notes(note, BPM, role="bass", sr=SR, bars=1)
    pad = midi_synth.render_notes(note, BPM, role="pad", sr=SR, bars=1)
    assert np.max(np.abs(bass)) > 0.01 and np.max(np.abs(pad)) > 0.01
    n = min(len(bass), len(pad))
    assert not np.allclose(bass[:n], pad[:n]), "roles should produce different voices"


def test_determinism():
    a = midi_synth.render_notes(_drum_notes(), BPM, role="drums", sr=SR, bars=1)
    b = midi_synth.render_notes(_drum_notes(), BPM, role="drums", sr=SR, bars=1)
    assert np.array_equal(a, b), "fallback synth must be deterministic"


# --- worker CLI + pool -----------------------------------------------------
def test_worker_cli_midi_fallback_and_pool_cache():
    with tempfile.TemporaryDirectory() as d:
        notes_path = os.path.join(d, "notes.json")
        Path(notes_path).write_text(json.dumps({"notes": _drum_notes(), "bars": 1}))
        job = {"midi": notes_path, "bpm": BPM, "instrument": "fallback:drums",
               "output": os.path.join(d, "out.wav"), "sr": SR}

        res1 = render_pool.render_jobs([job], cache_dir=os.path.join(d, "cache"))
        assert res1[0]["status"] == "rendered", res1[0]
        assert os.path.getsize(job["output"]) > 1000

        res2 = render_pool.render_jobs([job], cache_dir=os.path.join(d, "cache"))
        assert res2[0]["status"] == "cached", "identical notes must cache-hit"

        # change one note -> content hash changes -> re-render
        changed = _drum_notes()
        changed[0]["velocity"] = 90
        Path(notes_path).write_text(json.dumps({"notes": changed, "bars": 1}))
        res3 = render_pool.render_jobs([job], cache_dir=os.path.join(d, "cache"))
        assert res3[0]["status"] == "rendered", "changed notes must re-render"


def test_worker_cli_midi_with_fx_chain():
    with tempfile.TemporaryDirectory() as d:
        notes_path = os.path.join(d, "notes.json")
        Path(notes_path).write_text(json.dumps(_drum_notes()))
        out = os.path.join(d, "fx.wav")
        cmd = [sys.executable, str(_HERE / "render_worker.py"),
               "--midi", notes_path, "--bpm", str(BPM),
               "--instrument", "fallback:drums", "--out", out,
               "--chain", '[{"builtin":"Gain","params":{"gain_db":-6}}]']
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr[-500:]
        assert os.path.getsize(out) > 1000


def test_plugin_instrument_render():
    """Gated: set SANDBOX_TEST_PLUGIN=/path/Instrument.vst3 (or .component) to run."""
    plug = os.environ.get("SANDBOX_TEST_PLUGIN")
    if not plug:
        print("  SKIP  test_plugin_instrument_render (SANDBOX_TEST_PLUGIN not set)")
        return
    kind = "au" if plug.endswith(".component") else "vst"
    with tempfile.TemporaryDirectory() as d:
        notes_path = os.path.join(d, "notes.json")
        Path(notes_path).write_text(json.dumps(
            {"notes": [{"pitch": 60, "start_time": 0.0, "duration": 2.0, "velocity": 100}],
             "bars": 1}))
        out = os.path.join(d, "plug.wav")
        cmd = [sys.executable, str(_HERE / "render_worker.py"),
               "--midi", notes_path, "--bpm", "120",
               "--instrument", f"{kind}:{plug}", "--out", out]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        assert proc.returncode == 0, proc.stderr[-800:]
        import soundfile as sf
        audio, _ = sf.read(out)
        assert float(np.max(np.abs(audio))) > 0.001, "plugin rendered silence"


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
