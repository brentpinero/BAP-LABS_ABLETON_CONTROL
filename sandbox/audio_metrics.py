"""
audio_metrics.py — Tier 1 (LUFS/spectral/masking) + Tier 2 (CLAP) audio scoring.

Tier 1 runs on every rendered iteration (seconds). Tier 2 (CLAP text↔audio
genre similarity) is lazy, optional, and gated — first use downloads ~1.7GB to
the local HF cache; everything stays on-device. Under fallback proxy synths
the loop already halves CLAP's weight (timbre isn't real).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import soundfile as sf

import reference_targets
from project_state import K


def _m(name, value, score, target, explain) -> Dict[str, Any]:
    return {"name": name, "value": round(float(value), 4),
            "score": round(float(max(0.0, min(1.0, score))), 4),
            "target": target, "explain": explain}


def _lufs(audio: np.ndarray, sr: int) -> Optional[float]:
    try:
        import pyloudnorm
        v = pyloudnorm.Meter(sr).integrated_loudness(
            audio if audio.ndim == 2 else audio[:, None])
        return None if not np.isfinite(v) else float(v)
    except Exception:
        return None


def score_tier1(session, record) -> Dict[str, Any]:
    """Analyze the rendered master + stems. Returns {'score': 0-1, 'metrics': [...]}."""
    metrics: List[Dict[str, Any]] = []
    master_path = record.audio.get("master")
    if not master_path or not Path(master_path).exists():
        return {"score": 0.0, "metrics": [_m("render", 0, 0, "master.wav exists",
                                             "No master render to analyze.")]}
    master, sr = sf.read(master_path, dtype="float32", always_2d=True)
    targets = reference_targets.targets_for(session.genre)

    # loudness vs genre working level
    lufs = _lufs(master, sr)
    if lufs is not None:
        want = targets["lufs"]
        diff = abs(lufs - want)
        metrics.append(_m("master_lufs", lufs, max(0.0, 1.0 - max(0.0, diff - 3.0) / 9.0),
                          f"~{want} LUFS ({targets['source']})",
                          "Master working level should sit near the genre's ballpark."))

    # clipping / true-peak-ish
    peak = float(np.max(np.abs(master)))
    metrics.append(_m("true_peak", peak, 1.0 if peak <= 0.985 else 0.2, "<= -0.1 dBFS",
                      "The master must not clip."))

    # spectral balance vs reference curve — only meaningful on fullish mixes;
    # a 2-part sketch shouldn't be judged against a finished-record curve
    n_stems = sum(1 for r in record.audio if r != "master")
    if n_stems >= 3:
        bands = reference_targets.band_energies(master, sr)
        want_bands = targets["bands"]
        dev = float(np.mean([abs(a - b) for a, b in zip(bands, want_bands)]))
        metrics.append(_m("spectral_balance", dev, max(0.0, 1.0 - dev / 0.18),
                          f"band mix ≈ {['%.2f' % b for b in want_bands]} ({targets['source']})",
                          "Low/low-mid/mid/high energy split should track the genre curve."))

    # crest factor (dynamics)
    rms = float(np.sqrt(np.mean(master ** 2))) or 1e-9
    crest = 20 * np.log10(peak / rms)
    metrics.append(_m("crest_factor", crest,
                      1.0 if 6 <= crest <= 20 else max(0.0, 1.0 - abs(crest - 13) / 13),
                      "6-20 dB", "Some dynamics — neither over-compressed nor all spikes."))

    # low-end masking between stems (two stems both heavy under 150 Hz = mud)
    low_share: Dict[str, float] = {}
    for role, path in record.audio.items():
        if role == "master" or not Path(path).exists():
            continue
        stem, ssr = sf.read(path, dtype="float32", always_2d=True)
        b = reference_targets.band_energies(stem, ssr)
        low_share[role] = b[0]
    heavy = [r for r, v in low_share.items() if v > 0.5]
    bass_like = {"bass", "drums"}
    intruders = [r for r in heavy if r not in bass_like]
    metrics.append(_m("low_end_masking", len(intruders),
                      1.0 if not intruders else max(0.0, 1.0 - 0.4 * len(intruders)),
                      "only bass/drums heavy below ~150 Hz",
                      (f"{', '.join(intruders)} crowd the low end — raise voicings or "
                       f"high-pass them.") if intruders else "Low end is owned by bass/drums."))

    score = sum(m["score"] for m in metrics) / len(metrics)
    return {"score": round(score, 4), "metrics": metrics}


# --- Tier 2: CLAP genre similarity (lazy, optional, local) -------------------
_CLAP = {"model": None, "processor": None}


def _clap():
    if _CLAP["model"] is None:
        from transformers import ClapModel, ClapProcessor  # heavy import, on demand
        _CLAP["model"] = ClapModel.from_pretrained("laion/clap-htsat-unfused")
        _CLAP["processor"] = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
    return _CLAP["model"], _CLAP["processor"]


def score_clap(session, record) -> Optional[Dict[str, Any]]:
    """cosine(master, genre prose) minus anti-prompt margin, mapped to 0-1."""
    master_path = record.audio.get("master")
    if not master_path or not Path(master_path).exists():
        return None
    try:
        import torch
        import librosa
        model, proc = _clap()
        audio, _ = librosa.load(master_path, sr=48000, mono=True, duration=20.0)
        st = K.STYLE.get(session.genre, {})
        pos = (f"a {session.genre.replace('_', ' ')} instrumental beat. "
               f"{st.get('feel', '')}")
        neg = "an amateur out-of-tune random MIDI demo with no groove"
        with torch.no_grad():
            a_in = proc(audios=[audio], sampling_rate=48000, return_tensors="pt")
            a_emb = model.get_audio_features(**a_in)
            t_in = proc(text=[pos, neg], return_tensors="pt", padding=True)
            t_emb = model.get_text_features(**t_in)
            a_emb = a_emb / a_emb.norm(dim=-1, keepdim=True)
            t_emb = t_emb / t_emb.norm(dim=-1, keepdim=True)
            sims = (a_emb @ t_emb.T)[0]
            margin = float(sims[0] - sims[1])
        return {"score": round(max(0.0, min(1.0, 0.5 + margin * 2.0)), 4),
                "margin": round(margin, 4), "pos_sim": round(float(sims[0]), 4)}
    except Exception:
        return None


def audio_scorer(session, record) -> Dict[str, Any]:
    """Injected into SandboxEngine: returns tier scores + detail for the critic."""
    out: Dict[str, Any] = {}
    t1 = score_tier1(session, record)
    out["audio"] = t1["score"]
    out["audio_detail"] = t1
    if getattr(session.config, "clap_enabled", False):
        # CLAP only on the first iteration and after the loop would end (expensive)
        n = len(session.iterations) + 1
        if n == 1 or n >= session.config.max_iterations:
            c = score_clap(session, record)
            if c:
                out["clap"] = c["score"]
                out["clap_detail"] = c
    return out
