"""
profile.py — the engine-agnostic probes of the Phase 0 feedback loop.

A probe knows nothing about Live or any engine. It asks a *target* to play a
clip and hands the captured master output to measure.py. The same probes run
against the reference (Live, via live_profile.LiveTarget) and against every
candidate (ref_engine.RefEngine today, the real engine later); the per-metric
gap between the two profiles is the work list.

Target protocol:
    target.sr                                   project sample rate
    target.play(wav, position_beats, pan, seconds, warp_mode=None) -> (N, 2) floats
        the track's output from position 0 for `seconds`, with the clip placed at
        `position_beats` on a track panned to `pan` in [-1, 1]. Unwarped unless
        `warp_mode` names one of `target.warp_modes`, in which case the clip is
        warped at ratio 1:1 (clip tempo == set tempo) with that stretch mode.
        Tempo is TEMPO (120 BPM, 4/4), so one beat is 0.5 s.
    target.warp_modes        optional list of stretch-mode names
    target.limiter_specs     optional list of {"name", "uri", "params"}; with
    target.device(spec)      a context manager that inserts/removes the device
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


def probe_src(target, work: Path, level_db: float = -6.0) -> Dict[str, Any]:
    """Sweep stored at twice the project rate, so the engine must downsample it:
    passband flatness and how much above-Nyquist content folds back."""
    sr = target.sr
    file_sr = 2 * sr
    sweep = dict(f_start=20.0, f_end=float(sr), seconds=8.0, level_db=level_db)
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


def probe_warp(target, work: Path) -> Dict[str, Any]:
    """Warped clip whose tempo equals the set tempo (stretch ratio exactly 1:1),
    once per stretch mode the target offers (`target.warp_modes`): does the
    stretcher pass the audio through, or colour it even when it has nothing to
    do? Live documents that its Complex modes are never neutral; the spec says
    bypass at 1:1. Reports per mode: latency, gain, residual, null depth, and
    how much the clip's length changed (a non-zero value means the ratio was
    not 1:1 and the residual figure should be read with that in mind)."""
    modes = list(getattr(target, "warp_modes", []))
    if not modes:
        return {"skipped": "target offers no warp modes"}
    sr = target.sr
    src = signals.fade(signals.noise(3.0, sr, level_db=-20.0, seed=11), sr)
    wav = signals.write_wav(work / "warp_src.wav", src, sr)
    out: Dict[str, Any] = {}
    for mode in modes:
        cap = target.play(wav, 0.0, 0.0, 4.0, warp_mode=mode)[:, 0]
        lag = measure.latency_samples(src, cap, sr, max_lag_s=1.0)
        aligned = cap[lag:] if lag >= 0 else np.concatenate([np.zeros(-lag), cap])
        gain_db, matched = fidelity.gain_match(src, aligned[:len(src)])
        env = np.abs(aligned)
        above = np.nonzero(env > 10 ** (-60 / 20) * env.max())[0] if env.max() > 0 else np.array([0])
        out[str(mode)] = {"latency_samples": int(lag), "gain_db": round(gain_db, 3),
                          "residual_dbfs": round(measure.residual_dbfs(src, matched), 2),
                          "null_depth_db": round(fidelity.null_depth_db(src, matched), 2),
                          "length_error_ms": round((above[-1] + 1 - len(src)) * 1000.0 / sr, 2)}
    return out


def probe_limiter(target, work: Path) -> Dict[str, Any]:
    """True-peak behaviour of each limiter the target can insert
    (`target.limiter_specs`: [{"name", "uri", "params"}]). Self-calibrating: a
    0 dBFS steady sine far above the ceiling reads back AS the ceiling, so no
    parameter-to-dB mapping is needed. Then the fs/4 inter-sample stress tone
    (true peak 3 dB above its samples) and a noise burst report how far the
    16x-oversampled true peak exceeds that ceiling (section 4.3)."""
    specs = list(getattr(target, "limiter_specs", []))
    if not specs:
        return {"skipped": "target cannot insert limiters"}
    sr = target.sr
    sine = signals.write_wav(work / "lim_sine.wav", signals.fade(signals.sine(1000.0, 2.0, sr, 0.0), sr), sr)
    stress = signals.write_wav(work / "lim_isp.wav",
                               signals.fade(signals.isp_stress(2.0, sr, sample_peak_db=-0.5), sr), sr)
    burst = signals.write_wav(work / "lim_noise.wav", signals.fade(signals.noise(2.0, sr, -6.0, seed=5), sr), sr)
    out: Dict[str, Any] = {}
    for spec in specs:
        with target.device(spec):
            steady = target.play(sine, 0.0, 0.0, 2.5)[int(0.5 * sr): int(1.8 * sr), 0]
            ceiling_db = measure.loudness.sample_peak_dbfs(steady)
            tp_isp = measure.true_peak_dbtp(target.play(stress, 0.0, 0.0, 2.5)[:, 0], sr)
            tp_noise = measure.true_peak_dbtp(target.play(burst, 0.0, 0.0, 2.5)[:, 0], sr)
        out[spec["name"]] = {"ceiling_dbfs": round(ceiling_db, 3),
                             "isp_overshoot_db": round(tp_isp - ceiling_db, 3),
                             "noise_overshoot_db": round(tp_noise - ceiling_db, 3)}
    return out


def probe_pdc(target, work: Path) -> Dict[str, Any]:
    """Plugin delay compensation. Two tracks play the same clip; track B also
    carries a transparent device that reports latency (`target.latency_specs`).
    The target returns their SUM (`target.play_sum(wav, seconds, spec, mute_a)`).
    With compensation working, the sum with the device equals the sum without
    it; without compensation the two copies comb-filter. Reports per device: the
    device's own latency (B alone vs A alone), the sum's offset against the
    device-free sum, and the residual between them after gain matching."""
    specs = list(getattr(target, "latency_specs", []))
    if not specs or not hasattr(target, "play_sum"):
        return {"skipped": "target cannot sum two tracks with a latent device"}
    sr = target.sr
    wav = signals.write_wav(work / "pdc_src.wav",
                            signals.fade(signals.noise(2.0, sr, level_db=-30.0, seed=13), sr), sr)
    base = target.play_sum(wav, 2.5, None, mute_a=False)[:, 0]        # A + B, no device
    a_alone = target.play_sum(wav, 2.5, None, mute_a=False, mute_b=True)[:, 0]
    out: Dict[str, Any] = {}
    for spec in specs:
        b_alone = target.play_sum(wav, 2.5, spec, mute_a=True)[:, 0]
        both = target.play_sum(wav, 2.5, spec, mute_a=False)[:, 0]
        dev_lag = measure.latency_samples(a_alone, b_alone, sr, max_lag_s=1.0)
        sum_lag = measure.latency_samples(base, both, sr, max_lag_s=1.0)
        aligned = both[sum_lag:] if sum_lag >= 0 else np.concatenate([np.zeros(-sum_lag), both])
        gain_db, matched = fidelity.gain_match(base, aligned[:len(base)])
        resid = measure.residual_dbfs(base, matched)
        # Two valid strategies: render the latent track early (sum unshifted) or
        # delay every other track to match it (whole sum shifted by the latency).
        # Either way the two copies must still line up, which the residual shows.
        method = ("advance" if sum_lag == 0 else "delay-all" if abs(sum_lag - dev_lag) <= 1 else "mixed")
        out[spec["name"]] = {"device_latency_samples": int(dev_lag),
                             "sum_offset_samples": int(sum_lag),
                             "sum_gain_db": round(gain_db, 3),
                             "sum_residual_dbfs": round(resid, 2),
                             "method": method,
                             "compensated": bool(resid < -60.0 and method != "mixed")}
    return out


PROBES: Dict[str, Callable] = {"pan": probe_pan, "unity": probe_unity,
                               "edge_fade": probe_edge_fade, "src": probe_src,
                               "warp": probe_warp, "limiter": probe_limiter,
                               "pdc": probe_pdc}


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
