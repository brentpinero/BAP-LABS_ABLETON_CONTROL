"""
engine_bench.py — offline engine benchmarks (plan section 12.1, items 5–7).

Runs against any target with a `_render(clips, seconds)` method that renders a
multi-track job to a stereo array (tracktion_target.TracktionTarget today).

  offline_speed   N tracks of noise rendered offline: realtime multiple
  determinism     the same job rendered k times: byte-identical?
  summing         N identical tracks at -0.1 dBFS vs a double-precision reference

Run: python daw_bench/engine_bench.py --out sandbox_sessions/tracktion_bench
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure  # noqa: E402
import signals  # noqa: E402

_ROOT = Path(__file__).resolve().parent.parent


def _clips(wavs, pan: float = 0.0):
    return [{"file": str(w), "position_beats": 0.0, "pan": pan} for w in wavs]


def bench_offline_speed(target, work: Path, tracks: int = 64, seconds: float = 30.0) -> Dict[str, Any]:
    wavs = [signals.write_wav(work / f"speed_{i:02d}.wav",
                              signals.noise(seconds, target.sr, -30.0, seed=100 + i), target.sr)
            for i in range(tracks)]
    t0 = time.perf_counter()
    out = target._render(_clips(wavs), seconds)
    wall = time.perf_counter() - t0
    return {"tracks": tracks, "seconds": seconds, "wall_s": round(wall, 2),
            "realtime_multiple": round(seconds / wall, 1), "rendered_samples": int(len(out))}


def bench_determinism(target, work: Path, tracks: int = 16, seconds: float = 10.0, repeats: int = 5) -> Dict[str, Any]:
    wavs = [signals.write_wav(work / f"det_{i:02d}.wav",
                              signals.noise(seconds, target.sr, -30.0, seed=200 + i), target.sr)
            for i in range(tracks)]
    digests, first = [], None
    worst = measure.FLOOR_DB
    for _ in range(repeats):
        out = target._render(_clips(wavs), seconds)
        digests.append(hashlib.sha256(np.ascontiguousarray(out).tobytes()).hexdigest()[:16])
        if first is None:
            first = out
        else:
            worst = max(worst, measure.residual_dbfs(first[:, 0], out[:, 0]))
    return {"tracks": tracks, "repeats": repeats, "byte_identical": len(set(digests)) == 1,
            "worst_residual_dbfs": round(worst, 2), "digests": digests}


def bench_summing(target, work: Path, tracks: int = 100, seconds: float = 2.0) -> Dict[str, Any]:
    """N identical tracks summed in the engine vs the exact float64 sum. The
    engine renders to float32 WAV, so the floor is float32 quantisation of the
    SUM (about -150 dBFS relative), not the -140 dBFS gate on the mix bus itself."""
    src = signals.fade(signals.sine(1000.0, seconds, target.sr, -0.1), target.sr)
    wav = signals.write_wav(work / "sum_src.wav", src, target.sr)
    out = target._render(_clips([wav] * tracks), seconds)[:, 0]
    ref = tracks * src
    n = min(len(ref), len(out))
    lag = measure.latency_samples(ref, out, target.sr, max_lag_s=0.5)
    aligned = out[lag:] if lag >= 0 else np.concatenate([np.zeros(-lag), out])
    resid = measure.residual_dbfs(ref[:n], aligned[:n])
    peak = float(np.max(np.abs(aligned[:n])))
    return {"tracks": tracks, "expected_peak": round(tracks * 10 ** (-0.1 / 20), 3),
            "measured_peak": round(peak, 3), "residual_dbfs_re_fullscale": round(resid, 2),
            "residual_db_re_sum": round(resid - 20 * np.log10(tracks), 2), "lag_samples": int(lag)}


def bench_automation(target, work: Path, ramp_s: float = 1.0) -> Dict[str, Any]:
    """Automation resolution: a linear pan ramp over `ramp_s` on a steady fs/4
    tone (period 4 samples, so its peak envelope follows gain changes to within
    2 samples), rendered with the engine's -3 dB constant-power law and compared
    with that law's analytic curve. A block-based engine holds the pan for a whole
    buffer: the staircase shows up as the gain-update step length in samples and
    as the worst deviation from the smooth curve."""
    sr = target.sr
    f0 = sr / 4.0
    tone = signals.sine(f0, ramp_s + 0.5, sr, -12.0)
    wav = signals.write_wav(work / "auto_src.wav", tone, sr)
    out = target._render([{"file": str(wav), "position_beats": 0.0, "pan": -1.0,
                           "pan_from": -1.0, "pan_to": 1.0, "pan_ramp_s": ramp_s}],
                         ramp_s + 0.5, extra={"pan_law": "-3"})
    n = int(ramp_s * sr)
    env = [measure.maximum_filter1d(np.abs(out[:n, ch]), size=4) for ch in (0, 1)]
    p = -1.0 + 2.0 * np.arange(n) / n
    want = np.array([measure.pan_gains("sin_-3_0", float(x)) for x in p]) * 10 ** (-12.0 / 20)
    mid = slice(int(0.1 * n), int(0.9 * n))                 # away from the law's -inf ends
    err_db = [20 * np.log10(np.maximum(env[ch][mid], 1e-12) / np.maximum(want[mid, ch], 1e-12))
              for ch in (0, 1)]
    # gain-update step: distance between successive changes of the LEFT envelope,
    # ignoring the 2-sample jitter of the tone's own peaks
    e = env[0][mid]
    changes = np.nonzero(np.abs(np.diff(e)) > 1e-7 * float(np.max(e)))[0]
    gaps = np.diff(changes)
    gaps = gaps[gaps > 2]
    step = int(np.median(gaps)) if len(gaps) else 1
    return {"ramp_s": ramp_s, "law": "sin_-3_0", "tone_hz": f0,
            "worst_err_db": round(float(max(np.max(np.abs(err_db[0])), np.max(np.abs(err_db[1])))), 3),
            "gain_update_step_samples": step, "num_gain_changes": int(len(changes))}


BENCHES = {"offline_speed": bench_offline_speed, "determinism": bench_determinism,
           "summing": bench_summing, "automation": bench_automation}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(_ROOT / "sandbox_sessions" / "tracktion_bench"))
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--only", nargs="*", choices=list(BENCHES), default=None)
    args = ap.parse_args(argv)
    import tracktion_target as tt
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = tt.TracktionTarget(args.sr, keep_dir=out_dir / "takes")
    results: Dict[str, Any] = {"target": "tracktion", "sr": args.sr}
    for name in (args.only or BENCHES):
        try:
            results[name] = BENCHES[name](target, out_dir)
        except Exception as e:  # noqa: BLE001
            results[name] = {"error": f"{type(e).__name__}: {e}"}
        print(name, json.dumps(results[name])[:300], flush=True)
    (out_dir / "bench.json").write_text(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
