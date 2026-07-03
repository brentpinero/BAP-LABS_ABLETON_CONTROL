"""
reference_targets.py — per-genre spectral/loudness targets (Matchering-informed).

The proven automatic-mixing approach is matching a REFERENCE, not absolute
rules: if the user drops wavs into sandbox_references/<genre>/, targets are the
corpus average (PSD band energies + LUFS). With no corpus, hand-tuned fallback
tables apply. All local, cached per genre.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
REFS_DIR = _ROOT / "sandbox_references"

# analysis bands (Hz): low / low-mid / mid / high
BANDS = [(20, 120), (120, 500), (500, 4000), (4000, 16000)]

# fallback: fraction of total energy per band + working-level master LUFS
_FALLBACK: Dict[str, Dict[str, Any]] = {
    "boom_bap": {"bands": [0.34, 0.30, 0.26, 0.10], "lufs": -12.0},
    "lofi":     {"bands": [0.32, 0.32, 0.26, 0.10], "lufs": -14.0},
    "trap":     {"bands": [0.42, 0.24, 0.22, 0.12], "lufs": -10.0},
    "house":    {"bands": [0.36, 0.26, 0.24, 0.14], "lufs": -10.0},
    "techno":   {"bands": [0.40, 0.24, 0.22, 0.14], "lufs": -9.0},
    "dnb":      {"bands": [0.40, 0.22, 0.24, 0.14], "lufs": -10.0},
    "rnb":      {"bands": [0.32, 0.30, 0.27, 0.11], "lufs": -12.0},
    "ambient":  {"bands": [0.28, 0.30, 0.28, 0.14], "lufs": -18.0},
    "pop":      {"bands": [0.32, 0.27, 0.27, 0.14], "lufs": -10.0},
}
_DEFAULT = {"bands": [0.33, 0.28, 0.26, 0.13], "lufs": -12.0}

_cache: Dict[str, Dict[str, Any]] = {}


def band_energies(audio: np.ndarray, sr: int) -> list[float]:
    """Fraction of spectral energy per band (mono input)."""
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    n = min(len(mono), sr * 30)  # cap analysis at 30 s
    spec = np.abs(np.fft.rfft(mono[:n] * np.hanning(n))) ** 2
    freqs = np.fft.rfftfreq(n, 1 / sr)
    energies = [float(spec[(freqs >= lo) & (freqs < hi)].sum()) for lo, hi in BANDS]
    total = sum(energies) or 1.0
    return [e / total for e in energies]


def targets_for(genre: str) -> Dict[str, Any]:
    """Corpus-derived targets when references exist, else the fallback table."""
    if genre in _cache:
        return _cache[genre]
    corpus = sorted((REFS_DIR / genre).glob("*.wav")) if (REFS_DIR / genre).exists() else []
    if corpus:
        bands_acc, lufs_acc = [], []
        try:
            import pyloudnorm
            for wav in corpus[:12]:
                audio, sr = sf.read(wav, dtype="float32", always_2d=True)
                bands_acc.append(band_energies(audio, sr))
                lufs_acc.append(pyloudnorm.Meter(sr).integrated_loudness(audio))
            t = {"bands": list(np.mean(bands_acc, axis=0)), "lufs": float(np.mean(lufs_acc)),
                 "source": f"corpus:{len(corpus)} files"}
        except Exception:
            t = {**_FALLBACK.get(genre, _DEFAULT), "source": "fallback (corpus read failed)"}
    else:
        t = {**_FALLBACK.get(genre, _DEFAULT), "source": "fallback table"}
    _cache[genre] = t
    return t
