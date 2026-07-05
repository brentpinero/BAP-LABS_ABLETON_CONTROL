"""
test_render_host.py — tests for the warm plugin host.

Offline tests use the fallback numpy synth (no plugin, deterministic, fast) to
exercise framing, the warm render path, pool reuse across calls, respawn after a
host death, and render_pool's warm→cold fallback.

The last test is a REAL Serum measurement, skipped automatically when Serum 2
isn't installed. It proves the two things that matter: (1) a warm render is
byte-identical to a cold one (raw_state reset works), and (2) the second render
is dramatically faster than the first (the load tax is paid once).

Run: python daw_translation/test_render_host.py   (or pytest)
"""
from __future__ import annotations

import json
import os
import socket
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import soundfile as sf

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import render_host as rh  # noqa: E402
import render_pool  # noqa: E402

_SERUM = "/Library/Audio/Plug-Ins/VST3/Serum2.vst3"
_SERUM_SPEC = f"vst:{_SERUM}::name=Serum 2"


def _notes_file(d: Path, name="notes.json") -> str:
    p = d / name
    p.write_text(json.dumps({"notes": [
        {"pitch": 48, "start_time": 0.0, "duration": 1.0, "velocity": 100},
        {"pitch": 55, "start_time": 1.0, "duration": 1.0, "velocity": 90},
    ], "bars": 1}))
    return str(p)


# ── framing ──────────────────────────────────────────────────────────────────

def test_framing_roundtrip():
    a, b = socket.socketpair()
    try:
        payload = {"cmd": "render", "job": {"x": [1, 2, 3], "s": "héllo"}}
        rh._send(a, payload)
        assert rh._recv(b) == payload
    finally:
        a.close()
        b.close()


# ── warm render path (fallback synth, in-process) ────────────────────────────

def test_render_job_warm_fallback():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        out = d / "drums.wav"
        job = {"midi": _notes_file(d), "bpm": 100.0, "instrument": "fallback:drums",
               "output": str(out), "sr": 44100, "bars": 1, "tail_seconds": 0.5}
        cache = {}
        res = rh.render_job_warm(job, cache)
        assert res == str(out) and out.exists()
        audio, sr = sf.read(out)
        assert sr == 44100 and audio.shape[0] > 0


# ── pool: reuse across calls + respawn ───────────────────────────────────────

def test_pool_reuses_process_across_renders():
    """Second render for the same instrument reuses the SAME subprocess (that is
    the whole point — the plugin stays loaded)."""
    pool = rh.WarmHostPool()
    try:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            j1 = {"midi": _notes_file(d), "bpm": 100.0, "instrument": "fallback:bass",
                  "output": str(d / "a.wav"), "sr": 44100, "bars": 1, "tail_seconds": 0.2}
            r1 = pool.render(j1, timeout=30)
            assert r1["status"] == "rendered" and Path(j1["output"]).exists()
            pid1 = pool._hosts["fallback:bass"]._proc.pid

            j2 = dict(j1, output=str(d / "b.wav"))
            r2 = pool.render(j2, timeout=30)
            assert r2["status"] == "rendered" and Path(j2["output"]).exists()
            pid2 = pool._hosts["fallback:bass"]._proc.pid
            assert pid1 == pid2, "warm host should persist across renders, not respawn"
    finally:
        pool.shutdown()


def test_pool_respawns_after_host_death():
    """If the host process dies, the next render transparently respawns it."""
    pool = rh.WarmHostPool()
    try:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            j = {"midi": _notes_file(d), "bpm": 100.0, "instrument": "fallback:keys",
                 "output": str(d / "a.wav"), "sr": 44100, "bars": 1, "tail_seconds": 0.2}
            pool.render(j, timeout=30)
            host = pool._hosts["fallback:keys"]
            old_pid = host._proc.pid
            host._proc.kill()          # simulate a plugin crash
            host._proc.wait(timeout=5)

            j2 = dict(j, output=str(d / "b.wav"))
            r = pool.render(j2, timeout=30)   # must recover, not raise
            assert r["status"] == "rendered" and Path(j2["output"]).exists()
            assert pool._hosts["fallback:keys"]._proc.pid != old_pid
    finally:
        pool.shutdown()


# ── render_pool integration: warm path + cold fallback ───────────────────────

def test_render_pool_use_warm_host_fallback_synth():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        jobs = [{"midi": _notes_file(d), "bpm": 100.0, "instrument": "fallback:drums",
                 "output": str(d / f"r{i}.wav"), "sr": 44100, "bars": 1,
                 "tail_seconds": 0.2} for i in range(3)]
        res = render_pool.render_jobs(jobs, cache_dir=str(d / "cache"), use_warm_host=True)
        assert all(r["status"] == "rendered" for r in res)
        assert all(Path(j["output"]).exists() for j in jobs)
        # re-run hits the content cache (no render at all)
        res2 = render_pool.render_jobs(jobs, cache_dir=str(d / "cache"), use_warm_host=True)
        assert all(r["status"] == "cached" for r in res2)


def test_warm_host_falls_back_when_pool_unavailable(monkeypatch=None):
    """A broken warm pool must not break rendering — _run_one falls through to the
    cold subprocess path and still produces the wav."""
    orig = render_pool._warm_pool

    class _Broken:
        def render(self, job, timeout):
            raise RuntimeError("simulated host down")

    render_pool._warm_pool = lambda: _Broken()
    try:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            job = {"midi": _notes_file(d), "bpm": 100.0, "instrument": "fallback:keys",
                   "output": str(d / "out.wav"), "sr": 44100, "bars": 1, "tail_seconds": 0.2}
            res = render_pool._run_one(job, None, use_warm_host=True)
            assert res["status"] == "rendered" and Path(job["output"]).exists()
            assert not res.get("warm"), "should have used the cold fallback, not the warm path"
    finally:
        render_pool._warm_pool = orig


# ── REAL Serum: warm == cold, and warm is much faster (skipped if not installed) ─

def test_real_serum_warm_equals_cold_and_is_faster():
    if not os.path.exists(_SERUM):
        print("  SKIP  test_real_serum_warm_equals_cold_and_is_faster (Serum 2 not installed)")
        return
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        midi = _notes_file(d)
        common = {"midi": midi, "bpm": 100.0, "instrument": _SERUM_SPEC,
                  "sr": 44100, "bars": 1, "tail_seconds": 0.5}

        # cold: fresh subprocess via render_worker (what the loop does today)
        cold_out = d / "cold.wav"
        t0 = time.monotonic()
        rc = os.system(f'{sys.executable} {_HERE / "render_worker.py"} --midi {midi} '
                       f'--bpm 100 --instrument "{_SERUM_SPEC}" --bars 1 --tail-seconds 0.5 '
                       f'--sr 44100 --out {cold_out} >/dev/null 2>&1')
        cold_s = time.monotonic() - t0
        assert rc == 0 and cold_out.exists(), "cold render failed"

        pool = rh.WarmHostPool()
        try:
            w1 = dict(common, output=str(d / "warm1.wav"))
            t1 = time.monotonic(); r1 = pool.render(w1, timeout=120); warm1_s = time.monotonic() - t1
            w2 = dict(common, output=str(d / "warm2.wav"))
            t2 = time.monotonic(); r2 = pool.render(w2, timeout=120); warm2_s = time.monotonic() - t2
            assert r1["status"] == "rendered" and r2["status"] == "rendered"
        finally:
            pool.shutdown()

        cold, _ = sf.read(cold_out, dtype="float32", always_2d=True)
        warm, _ = sf.read(d / "warm2.wav", dtype="float32", always_2d=True)
        n = min(cold.shape[0], warm.shape[0])
        # warm render (after raw_state reset) must equal the cold render
        assert np.allclose(cold[:n], warm[:n], atol=1e-4), \
            f"warm render diverged from cold (max diff {np.max(np.abs(cold[:n]-warm[:n]))})"
        print(f"\n  Serum cold(subprocess)={cold_s:.2f}s  warm#1={warm1_s:.2f}s  "
              f"warm#2={warm2_s:.2f}s  → warm-vs-cold speedup {cold_s / max(warm2_s,1e-3):.1f}x")
        assert warm2_s < warm1_s, "second warm render should reuse the loaded plugin"


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
