"""
bands.py — the single source of truth for spectral-band resolution.

Both the live listening path (Max device → mix_analysis_bridge → live_ears cache)
and the offline scorer (sandbox/reference_targets, audio_metrics) must speak the
SAME band language or the fast and slow perception paths disagree. Define it once
here; import it everywhere.

RESOLUTION IS SWAPPABLE BY DESIGN. A "scheme" is a named, ordered list of
(name, lo_hz, hi_hz) bands. We start at 7 named bands (`v1_7band`) but expect to
revisit resolution as we learn what masking decisions actually need. To change it:

  * add a new scheme to SCHEMES (e.g. `v2_10band`),
  * point the Max device / analysis at its id,

…and nothing downstream breaks: every cached spectrum records its `band_scheme`
id and its length, and all consumers read the band COUNT from the data (never a
hardcoded 7). `describe`/masking look band names up from the scheme id at runtime.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

Band = Tuple[str, float, float]     # (name, lo_hz, hi_hz)
Scheme = List[Band]

# --- scheme registry -------------------------------------------------------
# Named regions chosen to match how mixing is actually discussed:
#   sub/low = weight & clash zone; low-mid = "mud"; mid = body/box;
#   hi-mid = presence/harshness; presence = clarity/air edge; air = sheen.
SCHEMES: Dict[str, Scheme] = {
    "v1_7band": [
        ("sub",      20.0,    60.0),
        ("low",      60.0,   120.0),
        ("low_mid",  120.0,  350.0),
        ("mid",      350.0, 2000.0),
        ("hi_mid",   2000.0, 6000.0),
        ("presence", 6000.0, 12000.0),
        ("air",      12000.0, 20000.0),
    ],
    # Example future higher-resolution scheme — not active, shown so the
    # expansion path is concrete. Add real schemes here as needed.
    # "v2_10band": [ ... 10 bands ... ],
}

DEFAULT_SCHEME = "v1_7band"


# --- accessors (never hardcode band count anywhere else) -------------------
def scheme(scheme_id: str = DEFAULT_SCHEME) -> Scheme:
    if scheme_id not in SCHEMES:
        raise KeyError(f"unknown band scheme {scheme_id!r}; known: {list(SCHEMES)}")
    return SCHEMES[scheme_id]


def band_names(scheme_id: str = DEFAULT_SCHEME) -> List[str]:
    return [b[0] for b in scheme(scheme_id)]


def band_edges(scheme_id: str = DEFAULT_SCHEME) -> List[Tuple[float, float]]:
    return [(lo, hi) for _n, lo, hi in scheme(scheme_id)]


def n_bands(scheme_id: str = DEFAULT_SCHEME) -> int:
    return len(scheme(scheme_id))


def validate(vector, scheme_id: str = DEFAULT_SCHEME) -> bool:
    """True iff a spectrum vector's length matches the scheme's band count."""
    return len(vector) == n_bands(scheme_id)


def name_of(index: int, scheme_id: str = DEFAULT_SCHEME) -> str:
    names = band_names(scheme_id)
    return names[index] if 0 <= index < len(names) else f"band{index}"


# --- offline energy extraction (used by the render/scoring path) -----------
def band_energies(audio, sr: int, scheme_id: str = DEFAULT_SCHEME) -> List[float]:
    """Fraction of spectral energy per band for a (mono or stereo) signal.

    Mirrors the live device's job so offline stems and live audio produce
    comparable vectors. numpy is imported lazily so importing this module stays
    dependency-free for the OSC bridge.
    """
    import numpy as np

    mono = audio.mean(axis=1) if getattr(audio, "ndim", 1) == 2 else audio
    n = min(len(mono), sr * 30)                      # cap analysis at 30 s
    spec = np.abs(np.fft.rfft(mono[:n] * np.hanning(n))) ** 2
    freqs = np.fft.rfftfreq(n, 1 / sr)
    energies = [float(spec[(freqs >= lo) & (freqs < hi)].sum())
                for lo, hi in band_edges(scheme_id)]
    total = sum(energies) or 1.0
    return [e / total for e in energies]
