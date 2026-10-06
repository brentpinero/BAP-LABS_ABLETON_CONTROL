"""
profile.py — the engine-agnostic probes of the Phase 0 feedback loop.

A probe knows nothing about Live or any engine. It asks a *target* to play a
clip and hands the captured master output to measure.py. The same probes run
against the reference (Live, via live_profile.LiveTarget) and against every
candidate (ref_engine.RefEngine today, the real engine later); the per-metric
gap between the two profiles is the work list.

Target protocol:
    target.sr                                   project sample rate
    target.play(wav, position_beats, pan, seconds) -> stereo float array (N, 2)
        master output from position 0 for `seconds`, with the clip (unwarped)
        placed at `position_beats` on a track panned to `pan` in [-1, 1].
        Tempo is TEMPO (120 BPM, 4/4), so one beat is 0.5 s.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(Path(__file__).resolve().parent), str(_ROOT / "sandbox")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fidelity  # noqa: E402
import measure  # noqa: E402
import signals  # noqa: E402

TEMPO = 120.0


class ProfileError(Exception):
    """A target cannot run the probes at all (stale Remote Script, real set open)."""


def probe_pan(target, work: Path, n_positions: int = 9, freq: float = 1000.0,
              level_db: float = -12.0) -> Dict[str, Any]:
    sr = target.sr
    wav = signals.write_wav(work / "pan_src.wav",
                            signals.fade(signals.sine(freq, 3.0, sr, level_db), sr), sr)
    positions = [round(float(p), 4) for p in np.linspace(-1.0, 1.0, n_positions)]
    left, right = [], []
    for p in positions:
        cap = target.play(wav, 0.0, p, 3.0)
        steady = cap[int(0.25 * sr): int(2.75 * sr)]            # inside the 3 s tone
        l_db, r_db = measure.stereo_tone_gains_db(steady, sr, freq, level_db)
        left.append(l_db)
        right.append(r_db)
    return {"positions": positions, "left_db": left, "right_db": right,
            "fit": measure.fit_pan_law(positions, left, right)}


def probe_unity(target, work: Path) -> Dict[str, Any]:
    """Unwarped clip at the project rate, pan centre, faders untouched: is
    playback a pure delay? Reports gain, latency and how deeply it nulls."""
    sr = target.sr
    src = signals.fade(signals.noise(3.0, sr, level_db=-20.0, seed=7), sr)
    out = target.play(signals.write_wav(work / "unity_src.wav", src, sr), 0.0, 0.0, 3.0)[:, 0]
    lag = measure.latency_samples(src, out, sr, max_lag_s=1.0)
    aligned = out[lag:] if lag >= 0 else np.concatenate([np.zeros(-lag), out])
    gain_db, matched = fidelity.gain_match(src, aligned[:len(src)])
    return {"latency_samples": int(lag), "gain_db": round(gain_db, 4),
            "residual_dbfs": round(measure.residual_dbfs(src, matched), 2),
            "source_rms_dbfs": -20.0}


def probe_edge_fade(target, work: Path) -> Dict[str, Any]:
    """Hard-edged tone placed mid-capture: how long is the fade the engine adds?
    (For Live this depends on the 'Create Fades on Clip Edges' preference.)"""
    sr = target.sr
    wav = signals.write_wav(work / "fade_src.wav", signals.sine(5000.0, 1.0, sr, -6.0), sr)
    cap = target.play(wav, 2.0, 0.0, 3.0)                     # clip starts at 1.0 s
    return {"fade_in_ms": round(measure.edge_fade_ms(
        cap[int(0.5 * sr): int(1.9 * sr), 0], sr, 5000.0), 3)}


def probe_src(target, work: Path) -> Dict[str, Any]:
    """Sweep stored at twice the project rate, so the engine must downsample it:
    passband flatness and how much above-Nyquist content folds back."""
    sr = target.sr
    file_sr = 2 * sr
    sweep = dict(f_start=20.0, f_end=float(sr), seconds=8.0, level_db=-6.0)
    src = signals.linear_sweep(sweep["f_start"], sweep["f_end"], sweep["seconds"],
                               file_sr, sweep["level_db"])
    out = target.play(signals.write_wav(work / "src_sweep.wav", src, file_sr), 0.0, 0.0, 9.0)[:, 0]
    # align on the part of the sweep that survives conversion (below 0.45 * sr)
    ref = signals.linear_sweep(sweep["f_start"], sweep["f_end"], sweep["seconds"],
                               sr, sweep["level_db"])
    ref[int(0.45 * sweep["seconds"] * sr):] = 0.0
    lag = measure.latency_samples(ref, out, sr, max_lag_s=1.0)
    result = measure.analyse_src_sweep(out[max(lag, 0):], sr, **sweep)
    result.update({"file_sr": file_sr, "project_sr": sr})
    return result


PROBES: Dict[str, Callable] = {"pan": probe_pan, "unity": probe_unity,
                               "edge_fade": probe_edge_fade, "src": probe_src}


def run_probes(target, out_dir: Path, name: str = "profile") -> Dict[str, Any]:
    """Run every probe against a target; one probe failing never loses the rest.
    Writes <out_dir>/<name>.json and returns the profile."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    profile: Dict[str, Any] = {"project_sr": target.sr}
    for key, probe in PROBES.items():
        try:
            profile[key] = probe(target, out_dir)
        except ProfileError:
            raise
        except Exception as e:  # noqa: BLE001
            profile[key] = {"error": f"{type(e).__name__}: {e}"}
    (out_dir / f"{name}.json").write_text(json.dumps(profile, indent=1))
    return profile
