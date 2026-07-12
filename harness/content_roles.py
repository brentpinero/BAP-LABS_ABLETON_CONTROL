"""
content_roles.py — infer a mix role from a node's SPECTRAL SIGNATURE, so the
perception layer works on projects whose track names don't map to anything
(generic "Audio 7", numbered "Serum 2", non-English, or just idiosyncratic).

This is the fallback for perception_roles.role_of: names are tried first (precise
when present), and when a name yields "other" we classify by the audio itself. The
aggregator made instrumentation cheap, so coverage no longer depends on naming —
this is what turns a spectrum into one of the canonical role slots.

The classifier is deliberately COARSE and scheme-agnostic: it folds whatever band
scheme is active into five fixed frequency REGIONS (by each band's geometric
center in Hz, so a future 10-band scheme still works) and buckets by where the
energy sits. It can't tell a vocal from a lead synth (both mid-heavy) — that's what
the name tiebreak is for — but it reliably separates sub / bass / drums / hi-FX /
mid-tonal, which is far better than dumping every unnamed track into "other".
"""

from __future__ import annotations

import math

import bands as _bands

# fixed Hz regions the classifier reasons in (independent of the active band scheme)
_REGIONS = [
    ("low",     0.0,     120.0),     # sub + low: weight/clash zone
    ("lowmid",  120.0,   350.0),     # "mud" / body bottom
    ("mid",     350.0,   2000.0),    # body / vocal fundamentals
    ("himid",   2000.0,  6000.0),    # presence / attack
    ("hi",      6000.0,  1e9),       # air / sizzle
]


def region_energy(band_fracs, scheme=_bands.DEFAULT_SCHEME) -> dict:
    """Fold per-band energy fractions into the five fixed Hz regions, keyed by
    each band's geometric-center frequency. Scheme-agnostic by construction."""
    edges = _bands.band_edges(scheme)
    reg = {name: 0.0 for name, _lo, _hi in _REGIONS}
    for (lo, hi), f in zip(edges, band_fracs):
        center = math.sqrt(max(lo, 1.0) * hi)
        for name, rlo, rhi in _REGIONS:
            if rlo <= center < rhi:
                reg[name] += float(f)
                break
    return reg


def classify(band_fracs, rms_db: float = -30.0, scheme: str = _bands.DEFAULT_SCHEME,
             silent_db: float = -70.0) -> str:
    """Best-effort role from a spectrum alone: one of
    sub | bass | drums | vox | synth | fx | other.

    band_fracs: per-band energy fractions (sum ~1), active-scheme order.
    rms_db:     node loudness — a silent/near-silent node classifies as "other"
                (no reliable signature), never a bogus role.
    Returns "other" when there's no audible signal to judge.
    """
    if rms_db <= silent_db or not band_fracs or sum(band_fracs) <= 1e-9:
        return "other"
    r = region_energy(band_fracs, scheme)
    low, lowmid, mid, himid, hi = r["low"], r["lowmid"], r["mid"], r["himid"], r["hi"]
    low_tot = low + lowmid                       # everything below ~350 Hz

    # order matters: most distinctive signatures first, mid-tonal is the catch-all.
    if low >= 0.60 and lowmid <= 0.15 and (mid + himid + hi) <= 0.15:
        return "sub"                              # almost ALL sub/low, nothing above ~120 Hz
    if hi >= 0.45 and low <= 0.20:
        return "fx"                               # HF-dominant: air, noise, risers, cymbals
    if low >= 0.15 and (himid + hi) >= 0.20 and mid <= 0.55:
        return "drums"                            # broadband, both ends lit (kick+snare+hats)
    if low_tot >= 0.50 and hi <= 0.15:
        return "bass"                             # low-heavy body, little air
    if (mid + himid) >= 0.50 and low <= 0.25:
        return "vox"                              # midrange formant energy, modest lows
    return "synth"                                # remaining tonal/mid content
