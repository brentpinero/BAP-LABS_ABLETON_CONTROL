"""
measure.py — the measurements the Phase 0 audio-quality spec is written in.

Pure numpy/scipy; no Live, no plugins. Reuses the existing instruments instead
of duplicating them:
  harness/loudness.py   BS.1770 loudness + true peak (called here at 16x; its
                        4x default under-reads by up to 0.40 dB)
  sandbox/fidelity.py   cross-correlation alignment, gain match, null depth

Adds what the spec needs and the repo lacked: pan-law fit, sample-rate-converter
sweep analysis, THD+N, clip-edge fade length, limiter overshoot, and an
unclipped residual level for summing-precision tests.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.ndimage import maximum_filter1d
from scipy.signal import fftconvolve

_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(_ROOT / "harness"), str(_ROOT / "sandbox")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fidelity  # noqa: E402
import loudness  # noqa: E402

TRUE_PEAK_OVERSAMPLE = 16
FLOOR_DB = -400.0


def _db(x: float) -> float:
    return FLOOR_DB if x <= 0.0 else float(max(FLOOR_DB, 20.0 * np.log10(x)))


# --- level / peak -----------------------------------------------------------
def true_peak_dbtp(audio: np.ndarray, sr: int) -> float:
    """True peak (dBTP) at 16x. On faded tones up to 0.49*fs the existing meter
    is within 0.04 dB at 16x but under-reads by up to 0.40 dB at its 4x default."""
    return loudness.true_peak_dbtp(audio, sr, oversample=TRUE_PEAK_OVERSAMPLE)


def limiter_overshoot_db(audio: np.ndarray, sr: int, ceiling_db: float) -> float:
    """How far the true peak exceeds the limiter's ceiling (<= 0 means it held)."""
    return true_peak_dbtp(audio, sr) - ceiling_db


def residual_dbfs(a: np.ndarray, b: np.ndarray) -> float:
    """RMS of (a - b) in dBFS over the overlap, unclipped (fidelity.null_depth_db
    saturates at 120 dB; summing-precision targets sit at -140 dBFS and below)."""
    n = min(len(a), len(b))
    d = np.asarray(a[:n], dtype=np.float64) - np.asarray(b[:n], dtype=np.float64)
    return _db(float(np.sqrt(np.mean(d ** 2)))) if n else FLOOR_DB


def latency_samples(ref: np.ndarray, out: np.ndarray, sr: int,
                    max_lag_s: float = 2.0) -> int:
    """Samples by which `out` trails `ref` (positive = out is late)."""
    lag, _ = fidelity.align(_mono(ref), _mono(out), sr, max_lag_s=max_lag_s)
    return lag


def _mono(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return x.mean(axis=1) if x.ndim == 2 else x


# --- sine fitting: exact tone level, and everything that isn't the tone ------
def sine_fit(x: np.ndarray, sr: int, freq: float) -> Tuple[float, np.ndarray]:
    """Least-squares fit of a sinusoid at `freq`. Returns (amplitude, residual).
    Exact for any segment length, so no FFT window or bin-centring is needed."""
    x = np.asarray(x, dtype=np.float64)
    t = np.arange(len(x)) / sr
    basis = np.column_stack([np.sin(2 * np.pi * freq * t), np.cos(2 * np.pi * freq * t)])
    coef, *_ = np.linalg.lstsq(basis, x, rcond=None)
    return float(np.hypot(*coef)), x - basis @ coef


def tone_level_db(x: np.ndarray, sr: int, freq: float) -> float:
    return _db(sine_fit(x, sr, freq)[0])


def thd_n_db(x: np.ndarray, sr: int, freq: float) -> float:
    """THD+N in dB relative to the fundamental: everything left after removing
    the fitted fundamental (and DC), as an RMS ratio."""
    amp, resid = sine_fit(x, sr, freq)
    resid = resid - resid.mean()
    fund_rms = amp / np.sqrt(2.0)
    return FLOOR_DB if fund_rms <= 0 else _db(float(np.sqrt(np.mean(resid ** 2))) / fund_rms)


# --- pan law ----------------------------------------------------------------
def pan_gains(law: str, p: float) -> Tuple[float, float]:
    """Linear (left, right) gains for pan position p in [-1, 1] under a named law.
    Names read '<curve>_<centre dB>_<hard-pan dB>'."""
    theta = (p + 1.0) * np.pi / 4.0
    if law == "sin_-3_0":            # constant power, centre cut (Cubase/Pro Tools default)
        return float(np.cos(theta)), float(np.sin(theta))
    if law == "sin_0_+3":            # constant power, sides boosted (Live default)
        return float(np.sqrt(2) * np.cos(theta)), float(np.sqrt(2) * np.sin(theta))
    if law == "linear_-6_0":
        return (1.0 - p) / 2.0, (1.0 + p) / 2.0
    if law == "linear_0_+6":
        return 1.0 - p, 1.0 + p
    if law == "sqrt_-4.5_0":         # geometric mean of -3 dB and -6 dB laws
        return (float(np.sqrt(np.cos(theta) * (1.0 - p) / 2.0)),
                float(np.sqrt(np.sin(theta) * (1.0 + p) / 2.0)))
    if law == "balance_0_0":         # no compensation: only the far side is cut
        return min(1.0, 1.0 - p), min(1.0, 1.0 + p)
    raise ValueError(f"unknown pan law: {law}")


PAN_LAWS = ("sin_-3_0", "sin_0_+3", "linear_-6_0", "linear_0_+6", "sqrt_-4.5_0", "balance_0_0")


def fit_pan_law(positions: Sequence[float], left_db: Sequence[float],
                right_db: Sequence[float], floor_db: float = -60.0) -> Dict[str, object]:
    """Which named law best explains measured per-channel gains (dB re the
    unpanned source)? Returns the best law and each law's worst-case error.
    Channels a law predicts below `floor_db` are skipped (hard-panned side)."""
    errors: Dict[str, float] = {}
    for law in PAN_LAWS:
        worst = 0.0
        for p, l_db, r_db in zip(positions, left_db, right_db):
            for want, got in zip(pan_gains(law, p), (l_db, r_db)):
                want_db = _db(want)
                if want_db < floor_db:
                    continue
                worst = max(worst, abs(got - want_db))
        errors[law] = round(worst, 3)
    best = min(errors, key=errors.get)
    return {"law": best, "max_error_db": errors[best], "errors_db": errors}


# --- sample-rate-converter sweep ---------------------------------------------
def analyse_src_sweep(out: np.ndarray, sr_out: int, f_start: float, f_end: float,
                      seconds: float, level_db: float) -> Dict[str, float]:
    """Read a converter's quality off a linear sweep it has resampled to sr_out.

    The sweep's instantaneous frequency is linear in time, so its amplitude over
    time IS the magnitude response. Amplitude is a Hann-weighted short-time RMS
    (a Hilbert envelope smears the loud passband into the silent stopband and
    hides aliasing below about -30 dB). Reports:
      passband_ripple_db  max-min of the response from 20 Hz to 20 kHz (or 0.45*sr_out)
      alias_db            loudest output while the INPUT frequency is above the
                          new Nyquist (plus a transition margin), in dB re the
                          sweep level: content that should have been removed
    `out` must already be time-aligned so the sweep starts at sample 0."""
    out = _mono(out)
    amp = 10.0 ** (level_db / 20.0)
    n = min(len(out), int(round(seconds * sr_out)))
    win = np.hanning(1024)
    env = np.sqrt(2.0 * np.maximum(fftconvolve(out[:n] ** 2, win / win.sum(), mode="same"), 0.0))
    freq = f_start + (f_end - f_start) * (np.arange(n) / sr_out) / seconds
    edge = int(0.05 * sr_out)                      # window end effects + sub-100 Hz start
    valid = np.zeros(n, dtype=bool)
    valid[edge:n - edge] = True

    nyq = sr_out / 2.0
    pass_mask = valid & (freq >= 20.0) & (freq <= min(20000.0, 0.45 * sr_out))
    stop_mask = valid & (freq >= 1.1 * nyq)
    resp_db = 20.0 * np.log10(np.maximum(env[pass_mask], 1e-20) / amp)
    result = {"passband_ripple_db": round(float(resp_db.max() - resp_db.min()), 4),
              "passband_min_db": round(float(resp_db.min()), 4)}
    if stop_mask.any():
        result["alias_db"] = round(_db(float(env[stop_mask].max()) / amp), 2)
    return result


# --- clip-edge fade -----------------------------------------------------------
def edge_fade_ms(x: np.ndarray, sr: int, freq: float, start_db: float = -40.0,
                 settle_db: float = -0.5) -> float:
    """Length of the fade-in on a steady tone of `freq`: time for its envelope to
    rise from `start_db` to `settle_db` relative to the steady level. A hard
    (unfaded) edge reads close to 0. The envelope is the peak over one period
    of the tone — a Hilbert envelope leaks the tone into the silence before it
    and reads a hard edge as a multi-millisecond fade."""
    period = max(2, int(round(sr / freq)))
    env = maximum_filter1d(np.abs(_mono(x)), size=period)
    steady = float(np.median(env[len(env) // 2:]))
    if steady <= 0:
        return 0.0
    above_start = np.nonzero(env >= steady * 10.0 ** (start_db / 20.0))[0]
    above_settle = np.nonzero(env >= steady * 10.0 ** (settle_db / 20.0))[0]
    if not above_start.size or not above_settle.size:
        return 0.0
    return max(0.0, float(above_settle[0] - above_start[0]) * 1000.0 / sr)


# --- convenience ---------------------------------------------------------------
def stereo_tone_gains_db(stereo: np.ndarray, sr: int, freq: float,
                         source_level_db: float) -> List[float]:
    """[left, right] gain in dB applied to a tone of known level (pan-law probe).
    Uses the middle half of the capture so edge fades and transients are ignored."""
    stereo = np.asarray(stereo, dtype=np.float64)
    if stereo.ndim == 1:
        stereo = np.column_stack([stereo, stereo])
    n = len(stereo)
    mid = stereo[n // 4: 3 * n // 4]
    return [round(tone_level_db(mid[:, ch], sr, freq) - source_level_db, 3) for ch in (0, 1)]
