"""
perception_select.py — adaptive provisioning brain (Phase 3, heuristic v1).

Decides WHICH nodes to instrument (give an analysis channel + include in masking),
instead of blanket-covering every track. This is the decision the aggregator's
capture-track reconcile loop then executes: selected nodes get routed into aggregator
channels; the rest are ignored. Works for grouped AND flat/ungrouped projects.

v1 is a deterministic heuristic ranked by priority, capped at the channel budget:
    master        — always (mix reference)
    groups        — always (masking backbone: comparative clash view lives here)
    focused node  — the user's current selection ("make THIS brighter")
    named leaves  — flat tracks whose name maps to a role (role_map) — kick/bass/vox/...
    loud leaves   — flat tracks above an energy threshold (once we have live levels)
    other leaves  — fill remaining budget by energy

A clean seam is left for a model-driven selector later (query intent + prelim audio):
it returns the same list[node] shape, so swapping it in is drop-in. The energy field
is optional (chicken/egg: a track's live level only exists once it has a device), so
initial selection works from structure+names alone and refines when energy arrives.
"""

from __future__ import annotations

from perception_config import cfg

# priority bands (higher = more likely to keep under a tight channel budget)
_P_MASTER, _P_GROUP, _P_FOCUS, _P_NAMED, _P_RETURN, _P_LOUD, _P_OTHER = 100, 90, 95, 60, 50, 30, 10


def _named_role(name: str, role_map) -> str | None:
    low = (name or "").lower()
    for role, needles in role_map:
        if any(n in low for n in needles):
            return role
    return None


def select_nodes(nodes, focus_ref=None, override=None) -> list:
    """Rank + cap a list of node descriptors for instrumentation.

    nodes: list of dicts {ref, name, kind, group_id?, rms_db?} (ref = a resolver ref:
           int index, -1 master, or 'return:N'). rms_db optional (None until measured).
    focus_ref: the currently-selected node's ref, if any.
    Returns the kept nodes (<= capacity), each annotated with {score, reasons},
    highest priority first.
    """
    role_map = cfg("role_map", override)
    cap = int(cfg("select_capacity", override))
    loud_db = float(cfg("select_energy_db", override))

    scored = []
    for nd in nodes:
        kind = nd.get("kind", "")
        rms = nd.get("rms_db")
        # small energy tiebreak in [0,1) so louder wins within a tier, never crosses tiers
        etie = 0.0 if rms is None else max(0.0, min(1.0, (rms + 60.0) / 60.0)) * 0.9
        reasons = []
        if kind == "master":
            score = _P_MASTER; reasons.append("master")
        elif kind == "group":
            score = _P_GROUP; reasons.append("group")
        elif kind == "return":
            score = _P_RETURN + etie; reasons.append("return")
        else:  # leaf audio/midi track
            role = _named_role(nd.get("name", ""), role_map)
            if role:
                score = _P_NAMED + etie; reasons.append("named:" + role)
            elif rms is not None and rms > loud_db:
                score = _P_LOUD + etie; reasons.append("loud")
            else:
                score = _P_OTHER + etie; reasons.append("other")
        # focus overrides everything (still instrument groups/master too)
        if focus_ref is not None and nd.get("ref") == focus_ref:
            score = max(score, _P_FOCUS) + 10
            reasons.append("focused")
        scored.append((score, nd, reasons))

    scored.sort(key=lambda x: (-x[0], str(x[1].get("ref"))))
    kept = scored[:cap]
    return [{**nd, "score": round(score, 3), "reasons": reasons}
            for score, nd, reasons in kept]


def gather_nodes(client, snapshot=None) -> list:
    """Build the node descriptor list from the live session (structure + names via the
    Remote Script; optional energy merged from a live_ears snapshot by name). This is
    the bootstrap for the chicken/egg: names/structure exist before any device, energy
    only after — so selection starts from structure and refines when levels arrive."""
    nodes = []
    n = int(client.send("get_session_info").get("track_count", 0))
    for i in range(n):
        try:
            ti = client.send("get_track_info", {"track_index": i})
            nodes.append({"ref": i, "name": ti.get("name"), "kind": ti.get("kind", "audio"),
                          "rms_db": None})
        except Exception:
            pass
    try:
        mi = client.send("get_track_info", {"track_index": -1})
        nodes.append({"ref": -1, "name": mi.get("name", "Master"), "kind": "master", "rms_db": None})
    except Exception:
        pass
    try:
        for k, r in enumerate(client.send("get_return_tracks").get("return_tracks", [])):
            nodes.append({"ref": "return:%d" % k, "name": r.get("name", "Return %d" % k),
                          "kind": "return", "rms_db": None})
    except Exception:
        pass
    if snapshot:
        by_name = {}
        for t in snapshot.get("per_track", {}).get("tracks", {}).values():
            if t.get("name"):
                by_name[t["name"].lower()] = t.get("rms_l")
        for nd in nodes:
            r = by_name.get((nd.get("name") or "").lower())
            if r is not None:
                nd["rms_db"] = r
    return nodes


def selection_summary(selected) -> str:
    by = {}
    for s in selected:
        tag = s["reasons"][0].split(":")[0]
        by[tag] = by.get(tag, 0) + 1
    return " ".join(f"{k}:{v}" for k, v in sorted(by.items(), key=lambda kv: -kv[1]))
