"""
signals.py — deterministic test signals for the DAW measurement harness (Phase 0).

Every generator is pure numpy, seeded where random, and returns float64 so the
same array can be written to disk for a DAW to play and regenerated bit-for-bit
as the analysis reference. See docs/agentic_daw_research.md sections 3, 4, 12.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


def db_to_amp(db: float) -> float:
    return float(10.0 ** (db / 20.0))


def sine(freq: float, seconds: float, sr: int, level_db: float = -6.0,
         phase_deg: float = 0.0) -> np.ndarray:
    t = np.arange(int(round(seconds * sr))) / sr
    return db_to_amp(level_db) * np.sin(2 * np.pi * freq * t + np.deg2rad(phase_deg))


def linear_sweep(f_start: float, f_end: float, seconds: float, sr: int,
                 level_db: float = -6.0) -> np.ndarray:
    """Linear sine sweep (the Infinite Wave SRC test shape: instantaneous
    frequency maps linearly onto time, so the analyser can read response vs
    frequency straight off the envelope)."""
    t = np.arange(int(round(seconds * sr))) / sr
    k = (f_end - f_start) / seconds
    return db_to_amp(level_db) * np.sin(2 * np.pi * (f_start * t + 0.5 * k * t * t))


def isp_stress(seconds: float, sr: int, sample_peak_db: float = 0.0) -> np.ndarray:
    """fs/4 sine at 45 degrees: every sample lands at 0.707 of the waveform
    peak, so the true peak sits 3.01 dB ABOVE the sample peak. The standard
    worst-case signal for inter-sample-peak (true-peak) metering and limiting."""
    n = np.arange(int(round(seconds * sr)))
    amp = db_to_amp(sample_peak_db) * np.sqrt(2.0)
    return amp * np.sin(2 * np.pi * 0.25 * n + np.pi / 4)


def noise(seconds: float, sr: int, level_db: float = -20.0, seed: int = 0) -> np.ndarray:
    """Seeded white noise at an RMS level (broadband material for null tests)."""
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(int(round(seconds * sr)))
    return x * (db_to_amp(level_db) / np.sqrt(np.mean(x ** 2)))


def fade(audio: np.ndarray, sr: int, ms: float = 50.0) -> np.ndarray:
    """Raised-cosine fade in and out. An abrupt start is a click whose
    band-limited overshoot would be read as the signal's true peak."""
    n = int(ms * sr / 1000.0)
    ramp = 0.5 - 0.5 * np.cos(np.pi * np.arange(n) / n)
    out = np.array(audio, dtype=np.float64)
    out[:n] *= ramp
    out[-n:] *= ramp[::-1]
    return out


def write_wav(path: str | Path, audio: np.ndarray, sr: int) -> str:
    """32-bit float WAV, so the file itself adds no quantisation to a null test."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.asarray(audio, dtype="float32"), sr, subtype="FLOAT")
    return str(path)
