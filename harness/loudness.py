"""
loudness.py — perceived loudness + dynamics metrics (the mastering/mix currency the
7-band + RMS/peak layer was missing).

Operates on a rendered audio array (mono (N,) or stereo (N,2)) + sample rate — the
same interface shape as bands.band_energies — so it runs on stems/renders from the
sandbox render node and doubles as OFFLINE GOLD LABELS for the probing/eval harness.

What it computes:
  - Integrated / short-term / momentary LUFS  (ITU-R BS.1770 K-weighting + gating, via pyloudnorm)
  - LRA (loudness range, EBU Tech 3342)       — macro-dynamics
  - True-peak dBTP (4x oversampled)           — catches inter-sample overs sample-peak misses
  - Sample peak dBFS, RMS dBFS
  - Crest factor, PLR (peak-to-loudness), PSR (peak-to-short-term-loudness)

Why: RMS != perceived loudness; streaming normalizes to LUFS (Spotify -14, YT, Tidal),
R128 caps true-peak at -1 dBTP, and PLR/PSR say how over-compressed a track is. We
already stream peak+RMS but never formed the ratio — this closes that P0 gap.
"""

from __future__ import annotations

import numpy as np

SILENCE_DB = -120.0


def _stereo(audio: np.ndarray) -> np.ndarray:
    """-> float array shape (N, 2). Mono is duplicated to L=R."""
    a = np.asarray(audio, dtype=np.float64)
    if a.ndim == 1:
        a = np.column_stack([a, a])
    elif a.ndim == 2 and a.shape[0] < a.shape[1]:
        a = a.T                                   # (2, N) -> (N, 2)
    if a.shape[1] == 1:
        a = np.column_stack([a[:, 0], a[:, 0]])
    return a[:, :2]


def _db(x: float) -> float:
    return SILENCE_DB if x <= 1e-12 else float(20.0 * np.log10(x))


# --- LUFS (BS.1770) via pyloudnorm ----------------------------------------
def _meter(sr: int):
    import pyloudnorm as pyln
    return pyln.Meter(int(sr))                    # BS.1770-4 K-weighting + gating


def integrated_lufs(audio: np.ndarray, sr: int) -> float:
    a = _stereo(audio)
    if len(a) < int(0.4 * sr):
        return SILENCE_DB
    try:
        val = _meter(sr).integrated_loudness(a)
    except Exception:
        return SILENCE_DB
    return SILENCE_DB if not np.isfinite(val) else float(val)


def _windowed_lufs(audio: np.ndarray, sr: int, win_s: float, hop_s: float) -> np.ndarray:
    """K-weighted loudness per sliding window (LUFS). Used for momentary/short-term/LRA."""
    import pyloudnorm as pyln
    a = _stereo(audio)
    w, h = int(win_s * sr), max(1, int(hop_s * sr))
    if len(a) < w:
        return np.array([])
    meter = pyln.Meter(int(sr))
    out = []
    for start in range(0, len(a) - w + 1, h):
        seg = a[start:start + w]
        try:
            l = meter.integrated_loudness(seg)    # single window: block-gating ~ no-op
        except Exception:
            l = SILENCE_DB
        out.append(l if np.isfinite(l) else SILENCE_DB)
    return np.array(out, dtype=np.float64)


def momentary_lufs_max(audio: np.ndarray, sr: int) -> float:
    s = _windowed_lufs(audio, sr, 0.4, 0.1)       # 400 ms window
    return float(s.max()) if s.size else SILENCE_DB


def short_term_lufs_series(audio: np.ndarray, sr: int) -> np.ndarray:
    return _windowed_lufs(audio, sr, 3.0, 0.1)    # 3 s window, 100 ms hop


def loudness_range(audio: np.ndarray, sr: int) -> float:
    """LRA (LU) per EBU Tech 3342: gated short-term loudness distribution, P95 - P10."""
    st = short_term_lufs_series(audio, sr)
    st = st[st > -70.0]                            # absolute gate
    if st.size < 2:
        return 0.0
    rel_gate = st.mean() - 20.0                    # relative gate (EBU 3342)
    st = st[st >= rel_gate]
    if st.size < 2:
        return 0.0
    return float(np.percentile(st, 95) - np.percentile(st, 10))


# --- peaks / dynamics ------------------------------------------------------
def sample_peak_dbfs(audio: np.ndarray) -> float:
    a = _stereo(audio)
    return _db(float(np.max(np.abs(a))) if a.size else 0.0)


def true_peak_dbtp(audio: np.ndarray, sr: int, oversample: int = 4) -> float:
    """Inter-sample true peak (dBTP) via polyphase oversampling (ITU-R BS.1770 Annex 2)."""
    from scipy.signal import resample_poly
    a = _stereo(audio)
    if a.size == 0:
        return SILENCE_DB
    peak = 0.0
    for ch in range(a.shape[1]):
        up = resample_poly(a[:, ch], oversample, 1)
        peak = max(peak, float(np.max(np.abs(up))))
    return _db(peak)


def rms_dbfs(audio: np.ndarray) -> float:
    a = _stereo(audio)
    if a.size == 0:
        return SILENCE_DB
    return _db(float(np.sqrt(np.mean(a ** 2))))


def analyze(audio: np.ndarray, sr: int) -> dict:
    """Full loudness+dynamics report for a render/stem. All dB/LU floats."""
    lufs_i = integrated_lufs(audio, sr)
    st = short_term_lufs_series(audio, sr)
    st_max = float(st.max()) if st.size else SILENCE_DB
    tp = true_peak_dbtp(audio, sr)
    sp = sample_peak_dbfs(audio)
    rms = rms_dbfs(audio)
    crest = sp - rms                               # dB
    # PLR = true-peak minus integrated loudness; PSR = true-peak minus loudest short-term.
    plr = (tp - lufs_i) if lufs_i > SILENCE_DB else 0.0
    psr = (tp - st_max) if st_max > SILENCE_DB else 0.0
    return {
        "lufs_integrated": round(lufs_i, 2),
        "lufs_short_term_max": round(st_max, 2),
        "lufs_momentary_max": round(momentary_lufs_max(audio, sr), 2),
        "lra": round(loudness_range(audio, sr), 2),
        "true_peak_dbtp": round(tp, 2),
        "sample_peak_dbfs": round(sp, 2),
        "rms_dbfs": round(rms, 2),
        "crest_factor_db": round(crest, 2),
        "plr_db": round(plr, 2),
        "psr_db": round(psr, 2),
        "over_minus1_dbtp": bool(tp > -1.0),       # R128 true-peak ceiling breach
    }
