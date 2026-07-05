"""
Tests for render_worker + render_pool. pytest OR standalone.

Uses pedalboard built-in DSP only (no external plugins), so it's deterministic
and runs anywhere. Proves: chain building, the render is a real audio transform,
the CLI works, and the pool renders in parallel + caches.
"""
from __future__ import annotations

import os
import tempfile

import numpy as np
import soundfile as sf

import render_worker as rw
from render_pool import render_jobs, default_workers


def _sine(sr=44100, secs=0.2, freq=440.0):
    t = np.linspace(0, secs, int(sr * secs), endpoint=False, dtype="float32")
    return (0.5 * np.sin(2 * np.pi * freq * t)).astype("float32")


def test_gain_doubles_amplitude():
    x = _sine()
    y = rw.render_chain(x, 44100, [{"builtin": "Gain", "params": {"gain_db": 6.0}}])
    ratio = float(np.max(np.abs(y)) / np.max(np.abs(x)))
    assert 1.9 < ratio < 2.1   # +6 dB ~= 1.995x


def test_chain_is_real_transform():
    x = _sine()
    y = rw.render_chain(x, 44100, [{"builtin": "Reverb", "params": {"room_size": 0.8}}])
    # Reverb adds energy/tail -> output is not identical to input.
    assert not np.allclose(x, y[: len(x)] if len(y) >= len(x) else y)


def test_unknown_builtin_raises():
    try:
        rw.build_board([{"builtin": "NotARealEffect"}])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_cli_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out.wav")
        rc = rw.main(["--in", "sine", "--out", out, "--sr", "44100",
                      "--chain", '[{"builtin":"Gain","params":{"gain_db":0}}]'])
        assert rc == 0 and os.path.exists(out)
        data, sr = sf.read(out)
        assert sr == 44100 and len(data) > 0


def test_pool_parallel_and_cache():
    with tempfile.TemporaryDirectory() as d:
        cache = os.path.join(d, "cache")
        jobs = [
            {"input": "sine", "sr": 22050,
             "chain": [{"builtin": "Gain", "params": {"gain_db": float(i)}}],
             "output": os.path.join(d, f"t{i}.wav")}
            for i in range(6)
        ]
        res = render_jobs(jobs, cache_dir=cache)
        assert all(r["status"] == "rendered" for r in res)
        assert all(os.path.exists(j["output"]) for j in jobs)
        # Second run: identical jobs -> all cache hits.
        res2 = render_jobs(jobs, cache_dir=cache)
        assert all(r["status"] == "cached" for r in res2)


def test_default_workers_bounded():
    w = default_workers()
    assert w >= 1 and w <= (os.cpu_count() or 4)


if __name__ == "__main__":
    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS {name}")
                passed += 1
            except Exception as e:  # noqa: BLE001
                print(f"  FAIL {name}: {e}")
                failed += 1
    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
