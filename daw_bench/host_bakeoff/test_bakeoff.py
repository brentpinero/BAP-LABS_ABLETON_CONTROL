"""Tests for the plugin-hosting bake-off harness.

Unit tests need nothing installed. The integration test runs both hosts on FabFilter Pro-Q 3
(VST3) and is skipped unless the hosts are built and the plugin is installed.
    python -m pytest daw_bench/host_bakeoff/test_bakeoff.py -v
"""
import json
import struct
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bakeoff  # noqa: E402

CLASS = "56534558667350736572756D20320000"


def test_vstpreset_layout():
    comp, cont = b"COMPONENT-STATE", b"CTRL"
    data = bakeoff.vstpreset(CLASS, comp, cont)
    assert data[:4] == b"VST3"
    assert struct.unpack("<i", data[4:8])[0] == 1
    assert data[8:40] == CLASS.encode()
    list_offset = struct.unpack("<q", data[40:48])[0]
    assert data[list_offset:list_offset + 4] == b"List"
    count = struct.unpack("<i", data[list_offset + 4:list_offset + 8])[0]
    assert count == 2
    entries = {}
    for i in range(count):
        e = data[list_offset + 8 + i * 20: list_offset + 28 + i * 20]
        off, size = struct.unpack("<qq", e[4:])
        entries[e[:4]] = data[off:off + size]
    assert entries == {b"Comp": comp, b"Cont": cont}


def test_vstpreset_without_controller():
    data = bakeoff.vstpreset(CLASS, b"abc", None)
    off = struct.unpack("<q", data[40:48])[0]
    assert struct.unpack("<i", data[off + 4:off + 8])[0] == 1


def _write(d: Path, a, b, c, dd):
    d.mkdir(parents=True, exist_ok=True)
    for k, x in zip("abcd", (a, b, c, dd)):
        sf.write(d / f"{k}.wav", np.stack([x, x], 1).astype("float32"), 48000, subtype="FLOAT")


def test_score_pass_and_restore_failure(tmp_path):
    x = np.sin(np.linspace(0, 100, 4800)) * 0.5
    _write(tmp_path / "ok", x, x, x * 0.5, x * 0.5)
    s = bakeoff.score({"ok": True, "load_ms": 1}, tmp_path / "ok")
    assert s["compatible"] and s["determinism_dbfs"] < -500 and s["restored"]

    _write(tmp_path / "bad", x, x, x * 0.5, x)          # restored instance lost the edit
    s = bakeoff.score({"ok": True, "load_ms": 1}, tmp_path / "bad")
    assert not s["restored"] and not s["compatible"]


def random_phase_tone(rng) -> np.ndarray:
    """A tone that starts at a random phase each render, like a free-running oscillator."""
    return np.sin(np.arange(4800) * 0.05 + rng.uniform(0, 6.28)) * 0.5


def test_score_noisy_plugin_that_keeps_the_edit(tmp_path):
    # Fresh instance with its own noise seed: d does not null against c, but keeps the edit.
    rng = np.random.default_rng(0)
    x = np.sin(np.linspace(0, 300, 4800)) * 0.5

    def noise():
        return rng.standard_normal(4800) * 3e-3

    a, b = x + noise(), x + noise()
    c = 0.5 * x + noise()                                 # edit: -6 dB
    d = 0.5 * x + noise()                                 # restored: same noise level, new seed
    _write(tmp_path / "n", a, b, c, d)
    s = bakeoff.score({"ok": True, "load_ms": 1}, tmp_path / "n")
    assert not s["deterministic"] and s["restored"] and not s["restore_inconclusive"]


def test_score_random_plugin_that_loses_the_edit(tmp_path):
    rng = np.random.default_rng(1)
    a, b, d = (random_phase_tone(rng) for _ in range(3))           # d: back to the default
    c = 0.25 * random_phase_tone(rng)                               # edit: -12 dB
    _write(tmp_path / "r", a, b, c, d)
    s = bakeoff.score({"ok": True, "load_ms": 1}, tmp_path / "r")
    assert not s["deterministic"] and not s["restored"]


def test_score_invisible_edit_is_inconclusive(tmp_path):
    rng = np.random.default_rng(2)
    _write(tmp_path / "i", *(random_phase_tone(rng) for _ in range(4)))   # the edit changed nothing
    s = bakeoff.score({"ok": True, "load_ms": 1}, tmp_path / "i")
    assert s["restore_inconclusive"]


def test_score_missing_audio_is_incompatible(tmp_path):
    s = bakeoff.score({"ok": False, "error": "load failed"}, tmp_path)
    assert s["compatible"] is False and s["loaded"] is False


def test_stimulus_and_notes(tmp_path):
    bakeoff.make_stimulus(tmp_path / "s.wav")
    x, sr = sf.read(tmp_path / "s.wav")
    assert sr == bakeoff.SR and x.shape == (bakeoff.SR * bakeoff.SECONDS, 2)
    assert 0.2 < np.max(np.abs(x)) <= 0.25 + 1e-6
    notes = bakeoff.chord_notes()
    assert all(n["start"] + n["dur"] < bakeoff.SR * bakeoff.SECONDS for n in notes)


def test_watch_freeze_ignores_old_wavs_and_cuts_at_clip(tmp_path):
    import os
    import threading
    freeze = tmp_path / "Freeze"
    freeze.mkdir()
    sf.write(freeze / "old.wav", np.zeros((48000, 2), "float32"), 48000)   # present before: ignored
    x = np.zeros((48000 * 20, 2), "float32")
    start = int(32 * 60 / 126 * 48000)                                     # beat 32 at 126 BPM
    x[start] = 1.0                                                          # marker at the clip start

    def freeze_track():
        sf.write(freeze / "new.wav", x, 48000, subtype="FLOAT")
        old = time.time() - 5
        os.utime(freeze / "new.wav", (old, old))                           # looks finished writing
    import time
    threading.Timer(0.3, freeze_track).start()
    cut = bakeoff.watch_freeze(freeze, 32, 126, tmp_path, window_s=2.0)
    y, sr = sf.read(cut)
    assert sr == 48000 and y.shape == (96000, 2) and y[0, 0] == 1.0


def test_plugin_list_shape():
    plugins = json.loads((bakeoff.HERE / "plugin_list.json").read_text())["plugins"]
    assert len(plugins) == 50
    for p in plugins:
        assert p["format"] in ("vst3", "au")
        if p["format"] == "au":
            assert len(p["au"]) == 3 and all(len(c) == 4 for c in p["au"])


PROQ = "/Library/Audio/Plug-Ins/VST3/FabFilter Pro-Q 3.vst3"
built = all(b.exists() for b in (bakeoff.HOST_RS, bakeoff.HELPER, bakeoff.HOST_CPP))


@pytest.mark.skipif(not (built and Path(PROQ).exists()), reason="hosts not built or Pro-Q 3 not installed")
def test_both_hosts_pass_and_agree(tmp_path):
    bakeoff.make_stimulus(tmp_path / "in.wav")
    job = bakeoff.job_for({"format": "vst3", "bundle": PROQ}, tmp_path / "in.wav")
    renders = {}
    for host in ("cpp", "rust"):
        d = tmp_path / host
        res = bakeoff.run_host(host, job, d, timeout=120)
        assert res["ok"], res
        assert bakeoff.score(res, d)["compatible"]
        renders[host] = sf.read(d / "a.wav")[0]
    # Same plugin, same input, same settings: the two hosts produce the same audio.
    assert bakeoff.peak_dbfs(renders["cpp"] - renders["rust"]) < -120
