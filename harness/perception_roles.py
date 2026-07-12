"""
perception_roles.py — canonicalize the variable N tracks into a FIXED set of mix
roles, so every perception frame has constant dimensionality regardless of project.

Groups already approximate roles (masking.py treats them as the mixing-decision
layer). Each track/group is mapped to one of a fixed role list; all nodes for a
role are aggregated into ONE canonical submix (preferring the group bus, which the
M4L device already measured). "other" is the catch-all so no node is dropped and
the shape never changes.

Canonical role aggregates carry structural role "group" (or "master" for the main
bus) so masking.compute_masking(participants=("group","master")) treats them as
submixes — the mix-role name lives in Node.name.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import bands as _bands
from content_roles import classify as classify_by_content
from masking import Node
from perception_config import cfg


@dataclass
class RoleAgg:
    role: str
    node: Node          # bands (fraction) + rms_db, for masking
    width: float        # aggregated stereo width side/(mid+side)
    peak_db: float = -120.0   # loudest member peak, for clip detection


def role_of(ts: Any, tracks: dict, role_map: list, return_role: str,
            scheme: str = _bands.DEFAULT_SCHEME) -> str:
    """Canonical mix role for one track-like object (has .kind/.group_id/.name).

    Name maps first (precise); if the name says nothing, fall back to the node's
    SPECTRAL SIGNATURE so ungrouped/generically-named projects still populate real
    role slots instead of collapsing every unnamed track into 'other'."""
    if ts.kind == "master":
        return "master"
    if ts.kind == "return":
        return return_role
    # walk up to the top-level group; use its name as the role-bearing name
    cur, seen = ts, 0
    while getattr(cur, "group_id", "-1") not in ("-1", None, "") and seen < 32:
        parent = tracks.get(str(cur.group_id))
        if parent is None:
            break                       # parent not yet known (startup) — use current name
        cur, seen = parent, seen + 1
    name = (cur.name or "").lower()
    for role, needles in role_map:
        if any(n in name for n in needles):
            return role
    # name told us nothing: infer from the audio itself (own spectrum first, then
    # the walked-up group's), so coverage never depends on the naming convention.
    for src in (ts, cur):
        bands = getattr(src, "bands", None)
        if bands:
            role = classify_by_content(bands, getattr(src, "rms_db", -30.0), scheme)
            if role != "other":
                return role
    return "other"


def _aggregate(states: list, mix_role: str, scheme: str) -> RoleAgg:
    """Collapse the TrackStates mapped to a role into one canonical submix.
    Prefer group busses; else loudness-weighted sum of member tracks."""
    B = _bands.n_bands(scheme)
    structural = "master" if mix_role == "master" else "group"
    groups = [s for s in states if s.kind == "group" and s.bands]
    src = groups if groups else [s for s in states if s.bands]
    if not src:
        return RoleAgg(mix_role, Node(id=mix_role, name=mix_role, role=structural,
                                      bands=[0.0] * B, rms_db=-120.0), 0.0, -120.0)

    absum, linsum, mid, side, peak = [0.0] * B, 0.0, 0.0, 0.0, -120.0
    for s in src:
        node = s.to_node()
        ba = node.band_abs()
        for i in range(min(B, len(ba))):
            absum[i] += ba[i]
        if node.rms_db > -120:
            linsum += 10.0 ** (node.rms_db / 20.0)
        mid += getattr(s, "mid_energy", 0.0) or 0.0
        side += getattr(s, "side_energy", 0.0) or 0.0
        peak = max(peak, getattr(s, "peak_l", -120.0), getattr(s, "peak_r", -120.0))
    total = sum(absum)
    fracs = [a / total for a in absum] if total > 0 else [0.0] * B
    rms_db = 20.0 * math.log10(linsum) if linsum > 0 else -120.0
    width = side / (mid + side) if (mid + side) > 0 else 0.0
    return RoleAgg(mix_role, Node(id=mix_role, name=mix_role, role=structural,
                                  bands=fracs, rms_db=rms_db), width, peak)


def canonical_aggs(tracks: dict, override: dict | None = None):
    """Return (aggs, unmapped): a fixed-length list of RoleAgg in config `roles`
    order, plus names that fell through to 'other'.

    `tracks` is the bridge's {track_id: TrackState} (exposes
    .name/.kind/.group_id/.bands/.rms_db/.mid_energy/.side_energy/.to_node()).
    """
    roles = cfg("roles", override)
    role_map = cfg("role_map", override)
    return_role = cfg("return_role", override)
    scheme = cfg("band_scheme", override)

    buckets: dict[str, list] = {r: [] for r in roles}
    unmapped: set[str] = set()
    for ts in tracks.values():
        r = role_of(ts, tracks, role_map, return_role, scheme)
        if r == "other" and ts.kind not in ("master", "return"):
            unmapped.add(ts.name)
        buckets.setdefault(r, []).append(ts)

    aggs = [_aggregate(buckets.get(r, []), r, scheme) for r in roles]
    return aggs, unmapped
