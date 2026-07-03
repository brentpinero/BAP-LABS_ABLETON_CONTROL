"""
groove.py — deterministic humanizer (score/performance separation, GrooVAE-informed).

Models compose ON-GRID (fewer tokens, robust JSON for small models); the engine
applies groove — swing, velocity contour, bounded microtiming — as a separate
deterministic layer before rendering/scoring. Genre defaults come from
ableton_knowledge.GENRES; the model or user can override params per session.

apply_groove is pure and seeded: identical (notes, params) -> identical output,
which keeps render-pool cache keys stable across loop iterations.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

import numpy as np

from project_state import K  # re-exported ableton_knowledge

# genres that sit "behind the beat" get a lazy push (in beats at 16th resolution)
_LAID_BACK = {"boom_bap": 0.015, "rnb": 0.020, "lofi": 0.025}


def default_params(genre: str, role: str) -> Dict[str, Any]:
    prof = K.genre_profile(genre)
    gkey = prof["_key"]
    return {
        "swing": float(prof.get("swing", 0.0)),        # fraction of an 8th, applied to offbeat 8ths
        "velocity_jitter": 6.0 if role == "drums" else 4.0,   # σ, MIDI velocity units
        "accent": 12.0 if role == "drums" else 8.0,    # downbeat boost
        "push": _LAID_BACK.get(gkey, 0.0),             # constant behind-the-beat offset (beats)
        "timing_jitter": 0.006 if role == "drums" else 0.004,  # σ, beats (bounded below)
    }


def _rng_for(notes: List[Dict[str, Any]], role: str, seed: int) -> np.random.Generator:
    h = hashlib.sha256(f"{role}|{seed}|{len(notes)}".encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "big"))


def apply_groove(notes: List[Dict[str, Any]], genre: str, role: str,
                 params: Optional[Dict[str, Any]] = None, seed: int = 0) -> List[Dict[str, Any]]:
    """Return a new note list with swing/velocity/microtiming applied. Pure + seeded."""
    if not notes:
        return []
    p = default_params(genre, role)
    if params:
        p.update({k: v for k, v in params.items() if k in p})
    rng = _rng_for(notes, role, seed)

    out = []
    for n in sorted(notes, key=lambda x: (float(x.get("start_time", 0)), int(x.get("pitch", 60)))):
        t = float(n.get("start_time", 0.0))
        vel = float(n.get("velocity", 100))

        # swing: delay offbeat 8ths (position .5 within the beat) by swing * 0.5 beats
        frac = t % 1.0
        if abs(frac - 0.5) < 1e-3 and p["swing"] > 0:
            t += p["swing"] * 0.5

        # behind-the-beat push (skip bar downbeats so the '1' stays anchored)
        if p["push"] > 0 and (t % 4.0) > 1e-3:
            t += p["push"]

        # bounded micro-timing jitter (never before the grid slot's audibility window)
        jit = float(np.clip(rng.normal(0.0, p["timing_jitter"]), -0.02, 0.03))
        t = max(0.0, t + jit)

        # velocity: accent grid + jitter
        if abs((float(n.get("start_time", 0.0)) % 1.0)) < 1e-3:      # on-beat accent
            vel += p["accent"] * (1.0 if (float(n.get("start_time", 0.0)) % 4.0) < 1e-3 else 0.5)
        else:                                                          # offbeats sit back
            vel -= p["accent"] * 0.4
        vel += rng.normal(0.0, p["velocity_jitter"])

        m = dict(n)
        m["start_time"] = round(t, 4)
        m["velocity"] = int(np.clip(round(vel), 1, 127))
        out.append(m)
    return out
