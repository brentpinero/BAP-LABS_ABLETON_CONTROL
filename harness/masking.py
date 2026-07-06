"""
masking.py — comparative spectral-masking analysis across submix nodes.

Masking is inherently PAIRWISE and only meaningful between things that play at
once, so we compute it where mixing decisions live: on the GROUPS (submixes) and
the MASTER, comparatively — "does the kick clash with the bass?", "is the synth
masking the top end of the hi-hats?" — not across every raw track pair (noise).

Two views:
  * pairs             — group-vs-group contested bands (who clashes, and where).
  * master_congestion — per band, how many groups are crowding it (mix fullness).

Loudness-weighted: each node's per-band fraction is scaled by its linear RMS so a
quiet track never false-flags a clash. Resolution-agnostic: band count/names come
from the scheme id in bands.py — this code never hardcodes 7.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import bands as _bands


@dataclass
class Node:
    """A submix node's current spectral state (a group, the master, or a track)."""
    id: str
    name: str
    role: str                       # "track" | "group" | "master" | "return"
    bands: List[float]              # per-band energy fraction (sums ~1), scheme-length
    rms_db: float = 0.0             # node loudness; used to weight the fractions
    group_id: str = "-1"

    def band_abs(self) -> List[float]:
        """Loudness-weighted per-band energy (fraction × linear RMS)."""
        lin = 10.0 ** (self.rms_db / 20.0) if self.rms_db > -120 else 0.0
        return [b * lin for b in self.bands]


def masking_between(a: Node, b: Node, scheme_id: str = _bands.DEFAULT_SCHEME,
                    floor: float = 1e-3) -> dict:
    """Contested bands between two nodes. Works for any pair (groups OR tracks),
    so element-level queries ('kick vs bass') use the same math as group-vs-group."""
    aa, bb = a.band_abs(), b.band_abs()
    names = _bands.band_names(scheme_id)
    contested = []
    for i in range(min(len(aa), len(bb))):
        shared = min(aa[i], bb[i])          # both loud in this band == clash
        if shared > floor:
            contested.append({"band": names[i] if i < len(names) else f"band{i}",
                              "index": i, "a": aa[i], "b": bb[i], "contested": shared})
    contested.sort(key=lambda c: -c["contested"])
    return {
        "a": a.name, "b": b.name,
        "score": round(sum(c["contested"] for c in contested), 6),
        "bands": contested,
        "top_band": contested[0]["band"] if contested else None,
    }


def compute_masking(nodes: List[Node], scheme_id: str = _bands.DEFAULT_SCHEME,
                    participants=("group", "master"), floor: float = 1e-3,
                    max_pairs: int = 20, congestion_frac: float = 0.10,
                    audible_db: float = -50.0) -> dict:
    """Group-vs-group clash pairs + per-band master congestion.

    participants:     which node roles take part in the pairwise clash view
                      (default groups + master; pass ('group','track') to include
                      individual tracks for finer-grained queries).
    congestion_frac:  a group counts toward a band's congestion only if that band
                      is >= this fraction of the group's OWN energy (relative, so
                      it doesn't saturate the way an absolute floor does).
    audible_db:       groups quieter than this don't count toward congestion.
    """
    groups = [n for n in nodes if n.role in participants and n.role != "master"]

    # --- pairwise clash between groups ---
    pairs = []
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            m = masking_between(groups[i], groups[j], scheme_id, floor)
            if m["score"] > 0:
                pairs.append(m)
    pairs.sort(key=lambda p: -p["score"])
    pairs = pairs[:max_pairs]

    # --- per-band master congestion: how many groups crowd each band ---
    names = _bands.band_names(scheme_id)
    nb = _bands.n_bands(scheme_id)
    congestion = []
    for i in range(nb):
        # "present" = this band is a notable part of the group's own spectrum
        # (relative), and the group is audible — so congestion doesn't saturate.
        present = [g.name for g in groups
                   if g.rms_db > audible_db and i < len(g.bands)
                   and g.bands[i] >= congestion_frac]
        congestion.append({
            "band": names[i], "index": i,
            "groups_present": present, "congestion": len(present),
        })

    return {
        "scheme": scheme_id,
        "n_bands": nb,
        "pairs": pairs,                      # sorted worst-clash first
        "master_congestion": congestion,
        "summary": _summarize(pairs, congestion),
    }


def _summarize(pairs: list, congestion: list) -> str:
    if not pairs:
        return "No significant group clashes detected."
    worst = pairs[0]
    parts = [f"Worst clash: {worst['a']} vs {worst['b']} in the "
             f"{worst['top_band']} ({len(worst['bands'])} contested bands)."]
    crowded = max(congestion, key=lambda c: c["congestion"]) if congestion else None
    if crowded and crowded["congestion"] >= 3:
        parts.append(f"{crowded['band']} is crowded ({crowded['congestion']} groups).")
    return " ".join(parts)
