"""
fidelity.py — the measurement instrument for "does headless mirror Ableton?"

Pure numpy/scipy math, no Live, no pedalboard. Given two renders of the same
material (headless proxy vs Ableton Freeze ground truth), it aligns them
(cross-correlation — this is what stands in for plugin-delay-compensation,
which neither pedalboard nor DawDreamer performs), gain-matches, and reports:

  null_depth_db   how completely the two cancel (>=40 dB ~ identical,
                  20-40 dB ~ close/minor state drift, <20 dB ~ diverged)
  latency_samples the alignment offset found
  gain_delta_db   least-squares level difference (reported, not judged)
  band_diff_db    per-band dB difference across 8 log bands (20 Hz-16 kHz)
  lufs_delta      integrated-loudness difference
  resampled       True if SR conversion was required (caps claimable null depth)

The Registry stores per-plugin measurements as DESCRIPTIVE evidence — labels,
not policy. The approval UI plays the archived A/B pairs; the user's ears are
the judge. Stock Ableton devices are registered as "live_only" permanently.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import soundfile as sf
from scipy.signal import correlate

_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = _ROOT / "sandbox" / "fidelity_registry.json"
FIDELITY_AUDIO_DIR = _ROOT / "sandbox_sessions" / "_fidelity"

# 8 log-spaced analysis bands (Hz)
BANDS = [(20, 60), (60, 120), (120, 250), (250, 500),
         (500, 1000), (1000, 2000), (2000, 4000), (4000, 16000)]

MAX_LAG_S = 0.5          # search window for alignment
ALIGN_WINDOW_S = 5.0     # correlate over at most this many seconds


def _mono(x: np.ndarray) -> np.ndarray:
    return x.mean(axis=1) if x.ndim == 2 else x


def stereo_width(x: np.ndarray) -> float:
    """side/mid RMS ratio (0 = mono, ~1 = fully decorrelated L/R)."""
    if x.ndim != 2 or x.shape[1] < 2:
        return 0.0
    mid = (x[:, 0] + x[:, 1]) / 2
    side = (x[:, 0] - x[:, 1]) / 2
    rm = float(np.sqrt(np.mean(mid ** 2)))
    return float(np.sqrt(np.mean(side ** 2)) / rm) if rm > 1e-9 else 0.0


def normalize(audio: np.ndarray, sr: int, target_sr: int) -> tuple[np.ndarray, bool]:
    """Mono float64 at target_sr. Returns (audio, resampled_flag)."""
    mono = _mono(np.asarray(audio, dtype="float64"))
    if sr == target_sr:
        return mono, False
    import librosa
    return librosa.resample(mono, orig_sr=sr, target_sr=target_sr), True


def align(a: np.ndarray, b: np.ndarray, sr: int,
          max_lag_s: float = MAX_LAG_S) -> tuple[int, np.ndarray]:
    """Find b's lag relative to a via FFT cross-correlation; return (lag, b shifted
    onto a's timeline). Positive lag = b arrives later (e.g. plugin latency)."""
    n = min(len(a), len(b), int(ALIGN_WINDOW_S * sr))
    max_lag = int(max_lag_s * sr)
    corr = correlate(a[:n], b[:n], mode="full", method="fft")
    center = n - 1
    lo, hi = center - max_lag, center + max_lag + 1
    # scipy convention: peak left of center when b lags a — negate so that
    # POSITIVE lag = "b arrives later" (plugin latency), matching intuition
    lag = -int(np.argmax(np.abs(corr[lo:hi])) - max_lag)
    # lag > 0: b is DELAYED vs a -> shift b earlier
    if lag > 0:
        b_al = b[lag:]
    elif lag < 0:
        b_al = np.concatenate([np.zeros(-lag), b])
    else:
        b_al = b
    return lag, b_al


def gain_match(a: np.ndarray, b: np.ndarray) -> tuple[float, np.ndarray]:
    """Least-squares scalar match of b to a. Returns (gain_delta_db, b_scaled)."""
    n = min(len(a), len(b))
    denom = float(np.dot(b[:n], b[:n]))
    if denom < 1e-12:
        return 0.0, b
    alpha = float(np.dot(a[:n], b[:n])) / denom
    if alpha <= 1e-9:  # anti-correlated/silent — don't invert
        return 0.0, b
    return 20.0 * np.log10(alpha), b * alpha


def null_depth_db(a: np.ndarray, b: np.ndarray) -> float:
    """20*log10(rms(a)/rms(a-b)) over the overlap. Higher = more identical."""
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    a, b = a[:n], b[:n]
    rms_a = float(np.sqrt(np.mean(a ** 2)))
    rms_diff = float(np.sqrt(np.mean((a - b) ** 2)))
    if rms_a < 1e-9:
        return 0.0
    if rms_diff < 1e-9:
        return 120.0  # numerically identical
    return float(np.clip(20.0 * np.log10(rms_a / rms_diff), -20.0, 120.0))


def band_rms_diff(a: np.ndarray, b: np.ndarray, sr: int) -> list[float]:
    """Per-band dB difference (a vs b) via FFT magnitude in fixed bands."""
    n = min(len(a), len(b))
    win = np.hanning(n)
    fa = np.abs(np.fft.rfft(a[:n] * win))
    fb = np.abs(np.fft.rfft(b[:n] * win))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    out = []
    for lo, hi in BANDS:
        m = (freqs >= lo) & (freqs < hi)
        ra = float(np.sqrt(np.mean(fa[m] ** 2))) if m.any() else 0.0
        rb = float(np.sqrt(np.mean(fb[m] ** 2))) if m.any() else 0.0
        if ra < 1e-9 or rb < 1e-9:
            out.append(0.0)
        else:
            out.append(round(20.0 * np.log10(ra / rb), 2))
    return out


def lufs_delta(a: np.ndarray, b: np.ndarray, sr: int) -> Optional[float]:
    try:
        import pyloudnorm
        meter = pyloudnorm.Meter(sr)
        la = meter.integrated_loudness(a[:, None] if a.ndim == 1 else a)
        lb = meter.integrated_loudness(b[:, None] if b.ndim == 1 else b)
        if not (np.isfinite(la) and np.isfinite(lb)):
            return None
        return round(float(la - lb), 3)
    except Exception:
        return None


def label_for(null_db: float, resampled: bool,
              band_diff_db: list | None = None,
              lufs_delta: float | None = None) -> str:
    """Descriptive label — evidence, not policy.

    Synths with RANDOM oscillator/unison phase (Serum init, most supersaws)
    never null even against themselves in Ableton — waveform cancellation is
    the wrong lens there. When the null fails but the spectrum and loudness
    agree, the honest verdict is spectral-match, not diverged."""
    cap = 38.0 if resampled else 120.0  # resampling caps honest identity claims
    nd = min(null_db, cap)
    if nd >= 40.0:
        return "measured-identical"
    if nd >= 20.0:
        return "measured-close"
    if band_diff_db is not None and lufs_delta is not None:
        if max(abs(b) for b in band_diff_db) <= 3.0 and abs(lufs_delta) <= 1.5:
            return "spectral-match"
    return "diverged"


def compare(headless_wav: str | Path, live_wav: str | Path,
            target_sr: int = 44100) -> Dict[str, Any]:
    """Full comparison of two renders of the same material."""
    ha, hsr = sf.read(str(headless_wav), dtype="float64", always_2d=False)
    la, lsr = sf.read(str(live_wav), dtype="float64", always_2d=False)
    ch_a = ha.shape[1] if ha.ndim == 2 else 1
    ch_b = la.shape[1] if la.ndim == 2 else 1
    width_a, width_b = stereo_width(ha), stereo_width(la)
    a, ra = normalize(ha, hsr, target_sr)
    b, rb = normalize(la, lsr, target_sr)
    resampled = ra or rb

    lag, b_al = align(a, b, target_sr)
    gain_db, b_matched = gain_match(a, b_al)
    nd = null_depth_db(a, b_matched)
    bands = band_rms_diff(a, b_matched, target_sr)
    ld = lufs_delta(a, b_matched, target_sr)
    label = label_for(nd, resampled, band_diff_db=bands, lufs_delta=ld)
    # a stereo-vs-mono signal path (e.g. a wide instrument mono'd on the track)
    # summs differently — flag it so a width difference isn't read as a bad patch
    channel_mismatch = (ch_a != ch_b) or abs(width_a - width_b) > 0.3
    if label == "diverged" and channel_mismatch:
        # tonal check on the mid channel only (removes the width variable)
        mid_nd = null_depth_db(a, b_matched)  # a,b already mono (mid) here
        if max(abs(x) for x in bands[3:]) <= 4.0 and (ld is None or abs(ld) <= 2.0):
            label = "channel-mismatch"
    return {
        "null_depth_db": round(nd, 2),
        "latency_samples": lag,
        "gain_delta_db": round(gain_db, 3),
        "band_diff_db": bands,
        "lufs_delta": ld,
        "resampled": resampled,
        "channels": [ch_a, ch_b],
        "stereo_width": [round(width_a, 3), round(width_b, 3)],
        "duration_s": round(min(len(a), len(b_matched)) / target_sr, 2),
        "label": label,
    }


def params_hash(params: Optional[Dict[str, Any]], preset: str = "") -> str:
    payload = json.dumps(params or {}, sort_keys=True) + "|" + preset
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


class Registry:
    """Per-plugin fidelity measurements (descriptive evidence for UI + selection)."""

    def __init__(self, path: Path = REGISTRY_PATH):
        self.path = Path(path)
        self.data: Dict[str, Any] = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text())
            except Exception:
                self.data = {}

    @staticmethod
    def key(plugin_name: str, preset: str = "", params: Optional[dict] = None) -> str:
        base = plugin_name.replace(" ", "_").lower()
        return f"{base}:{params_hash(params, preset)}"

    def record(self, plugin_name: str, plugin_path: str, fmt: str,
               results: Dict[str, Any], preset: str = "",
               params: Optional[dict] = None,
               audio_pair: Optional[Dict[str, str]] = None) -> str:
        k = self.key(plugin_name, preset, params)
        self.data[k] = {
            "plugin": plugin_name, "path": plugin_path, "format": fmt,
            "preset": preset, "params_hash": params_hash(params, preset),
            "results": results, "label": results.get("label", "unmeasured"),
            "audio_pair": audio_pair or {},
            "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.save()
        return k

    def record_live_only(self, device_name: str) -> str:
        """Stock Ableton devices: permanently unmirrorable headless."""
        k = f"ableton_{device_name.replace(' ', '_').lower()}:stock"
        self.data[k] = {
            "plugin": device_name, "path": "", "format": "ableton-stock",
            "preset": "", "params_hash": "", "results": {},
            "label": "live_only", "audio_pair": {},
            "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.save()
        return k

    def best_label(self, plugin_name: str) -> str:
        """Best measurement label recorded for a plugin (any preset/params)."""
        labels = [v["label"] for v in self.data.values()
                  if v.get("plugin", "").lower() == plugin_name.lower()]
        for pref in ("measured-identical", "measured-close", "diverged", "live_only"):
            if pref in labels:
                return pref
        return "unmeasured"

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=1))
