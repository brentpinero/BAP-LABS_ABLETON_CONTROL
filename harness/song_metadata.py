"""
song_metadata.py — one-shot STATIC metadata dump of the Ableton set.

Annotates the signal chain the perception frames don't: per track, whether it's
audio or MIDI, its full (rack-recursed) device chain, each plugin's class +
classification, enabled/bypassed state, VST-partial flag, and every parameter's
current value + bounds + automation state. Written once to
`sandbox_sessions/metadata/<session>/song_metadata.json`.

This is the STATIC half (no playback needed) — the moving values over the song are
captured separately by the continuous sampler (perception_metadata.py). Both join to
the perception trajectory by track index / device path.

Drives ONE `get_all_device_parameters` (mode=full) Remote Script call; classification
reuses causal_dataset (classify_device / parameter_coverage). Requires Live open with
the AbletonMCP_Extended Remote Script RELOADED (the bulk command is new).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from causal_dataset import (NON_AUDIO_FAMILIES, classify_families, parameter_coverage,
                            sha256_file)
from live_client import LiveClient

_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = "sim.song-metadata.v1"

# Live wraps VST/AU plugins in these device classes and exposes only the params the
# producer configured into its view — so a small param count is EXPECTED, not a bug.
VST_CLASSES = {"PluginDevice", "AuPluginDevice"}
VST_PARTIAL_MAX = 12          # a VST exposing <= this many params is flagged vst_partial


def track_type(t: dict) -> str:
    """audio | midi | group | return | master (structural kinds win over in/out flags)."""
    kind = t.get("kind")
    if kind in ("master", "return", "group"):
        return kind
    if t.get("is_midi_track"):
        return "midi"
    if t.get("is_audio_track"):
        return "audio"
    return "unknown"


def _path_order(path: str) -> tuple:
    """(depth, chain_position, parent_path) from a device path.
    '3' -> (0, 3, None);  '2/0/1' -> (2, 1, '2/0')  (device 1 inside rack 2, chain 0)."""
    segs = str(path).split("/")
    chain_position = int(segs[-1]) if segs[-1].lstrip("r").isdigit() else 0
    depth = (len(segs) - 1) // 2                       # each rack level adds "<chain>/<dev>"
    parent = "/".join(segs[:-1]) or None
    return depth, chain_position, parent


def annotate_device(dev: dict, signal_order: int) -> dict:
    """Classify + summarize one device (from a mode=full snapshot entry).

    `signal_order` is the device's global left→right rank within the track (the chain
    processing order, flattening racks depth-first) — signal order matters: the same
    plugin sounds different earlier vs later in the chain."""
    name, cls = dev.get("name", ""), dev.get("class_name", "")
    params = dev.get("params", [])
    families = classify_families(name, cls)
    families = ["instrument" if f == "instrument_excluded" else f for f in families]
    is_vst = cls in VST_CLASSES
    on = next((p for p in params if p.get("name") == "Device On"), None)
    enabled = bool(on["value"]) if on else True
    automated = [p.get("name") for p in params if p.get("automation_state", 0)]
    depth, chain_position, parent = _path_order(dev.get("path", "0"))
    out = {
        "path": dev.get("path"),
        "signal_order": signal_order,                  # global chain order (left→right)
        "chain_position": chain_position,              # index among same-level siblings
        "depth": depth,                                # 0 = top-level, >0 = inside a rack
        "parent_path": parent,                         # containing rack path, or None
        "name": name,
        "class_name": cls,
        "families": families,                          # a device can be several families
        "classification": families[0],                 # primary (backward-compatible)
        "is_rack": "rack" in families,
        "is_vst": is_vst,
        "vst_partial": is_vst and len(params) <= VST_PARTIAL_MAX,
        "changes_audio": not any(f in NON_AUDIO_FAMILIES for f in families),
        "enabled": enabled,
        "n_params": len(params),
        "automated_params": automated,
        "params": [{"name": p.get("name"), "value": p.get("value"), "min": p.get("min"),
                    "max": p.get("max"), "automation_state": p.get("automation_state", 0)}
                   for p in params],
    }
    # For known FX families, note which params are family-relevant (reuse the causal
    # planner's coverage) — a helpful hint layer over the full param list.
    fx = {"eq_filter", "dynamics", "saturation_distortion", "stereo_modulation", "time_spatial"}
    relevant = [p.get("name") for fam in families if fam in fx
                for p in parameter_coverage(fam, params)["selected"]]
    if relevant:
        out["family_relevant_params"] = sorted(set(relevant))
    return out


def build_song_metadata(client, project_file=None) -> dict:
    """Full static metadata for the open set, from one bulk snapshot call."""
    si = client.send("get_session_info")
    snap = client.send("get_all_device_parameters", {"mode": "full"})
    tracks = []
    for t in snap.get("tracks", []):
        tracks.append({
            "track_index": t.get("track_index"),
            "name": t.get("track_name"),
            "kind": t.get("kind"),
            "track_type": track_type(t),
            "group_id": t.get("group_id", -1),      # parent group track index, or -1

            "n_devices": len(t.get("devices", [])),
            # the snapshot returns devices in chain order (depth-first); that list index
            # IS the global left→right signal order within the track.
            "devices": [annotate_device(d, i) for i, d in enumerate(t.get("devices", []))],
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": time.time(),
        "tempo": si.get("tempo"),
        "track_count": len(tracks),
        "project_file": ({"path": str(project_file), "sha256": sha256_file(project_file)}
                         if project_file else None),
        "note": "Static chain snapshot; moving parameter values over the song are in the "
                "companion params.jsonl (join by track_index + device path + param index).",
        "tracks": tracks,
    }


def _summary(meta: dict) -> str:
    dev = sum(t["n_devices"] for t in meta["tracks"])
    vst = sum(1 for t in meta["tracks"] for d in t["devices"] if d["is_vst"])
    partial = sum(1 for t in meta["tracks"] for d in t["devices"] if d["vst_partial"])
    autod = sum(len(d["automated_params"]) for t in meta["tracks"] for d in t["devices"])
    return (f"{meta['track_count']} tracks, {dev} devices ({vst} VST, {partial} vst_partial), "
            f"{autod} automated params")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Static per-track/plugin metadata dump of the open Ableton set.")
    ap.add_argument("--session", default=None, help="session id (default song_<epoch>)")
    ap.add_argument("--project-file", default=None, help="path to the .als for provenance hashing")
    ap.add_argument("--out", default=None, help="output dir (default sandbox_sessions/metadata/<session>)")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=9877)
    args = ap.parse_args(argv)

    client = LiveClient(host=args.host, port=args.port).connect()
    try:
        meta = build_song_metadata(client, args.project_file)
    finally:
        client.close()
    session = args.session or ("song_%d" % int(time.time()))
    out_dir = Path(args.out) if args.out else _ROOT / "sandbox_sessions" / "metadata" / session
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "song_metadata.json"
    path.write_text(json.dumps(meta, indent=1))
    print(f"[METADATA] {_summary(meta)} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
