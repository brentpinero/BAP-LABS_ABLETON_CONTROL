"""
enrich_sidecars.py — fold the Remote Script's full device detail into stem sidecars.

Each stem's sidecar (written by stem_ablation) records the per-RUNG state: which effects
were on/off for that capture. It does NOT carry the rich signal-chain context. This joins
the live Remote Script output (via song_metadata.build_song_metadata — the bulk
get_all_device_parameters snapshot + classify_families) into every sidecar so each stem is
fully self-describing for training:

  per device  -> parameter values (name/value/min/max/automation_state), classification +
                 families, is_vst / vst_partial, and any rack-nested devices
  per node    -> track_type (audio/midi/group/return/master) + group_id

The per-rung `enabled`/`ablatable` flags the sidecar already has are PRESERVED — only the
rung-independent chain metadata is merged in. Match is by track NAME (robust to the track
indices shifting between runs); the enrich source is the current (restored) mix, and the
ablation never changed parameters, so the captured values apply to every rung.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ENRICH_SCHEMA = "sim.causal-plugin.v2-enriched"


def build_name_index(song_meta: dict) -> dict:
    """{track_name: track-entry} from a song_metadata dump (last wins on duplicate names —
    same-named tracks are duplicates with identical chains)."""
    return {t["name"]: t for t in song_meta.get("tracks", [])}


def _top_level_and_racks(meta_devices: list):
    """Split a track's rack-recursed device list (each has a `path`) into top-level devices
    (path is a plain index like '2') and the nested children grouped under each top index."""
    tops, children = {}, {}
    for d in meta_devices:
        path = str(d.get("path", ""))
        if "/" not in path:
            tops[path] = d
        else:
            top = path.split("/", 1)[0]
            children.setdefault(top, []).append(d)
    return tops, children


def enrich_sidecar(sidecar: dict, track_meta: dict | None) -> dict:
    """Return a copy of `sidecar` with device parameters/classification + node type/group
    merged from `track_meta` (a song_metadata track entry). Missing metadata is a no-op."""
    out = json.loads(json.dumps(sidecar))            # deep copy
    out["schema_version"] = ENRICH_SCHEMA
    if not track_meta:
        out.setdefault("enrichment", {})["matched"] = False
        return out
    out["node"]["track_type"] = track_meta.get("track_type")
    out["node"]["group_id"] = track_meta.get("group_id")   # parent group index, or -1
    tops, children = _top_level_and_racks(track_meta.get("devices", []))
    for dev in out.get("devices", []):
        m = tops.get(str(dev.get("index")))
        if not m:
            continue
        # rung-independent chain detail (keep the sidecar's per-rung enabled/ablatable)
        dev["classification"] = m.get("classification")
        dev["families"] = m.get("families")
        dev["is_vst"] = m.get("is_vst")
        dev["vst_partial"] = m.get("vst_partial")
        dev["automated_params"] = m.get("automated_params")
        dev["params"] = m.get("params")
        if m.get("family_relevant_params"):
            dev["family_relevant_params"] = m["family_relevant_params"]
        kids = children.get(str(dev.get("index")))
        if kids:                                     # rack contents (e.g. sidechain rack)
            dev["rack_devices"] = [{"path": k.get("path"), "name": k.get("name"),
                                    "class_name": k.get("class_name"),
                                    "classification": k.get("classification"),
                                    "enabled": k.get("enabled"), "params": k.get("params")}
                                   for k in kids]
    out.setdefault("enrichment", {})["matched"] = True
    return out


def enrich_session(session_dir: str | Path, song_meta: dict) -> dict:
    """Enrich every stem sidecar (*.json except manifest.json) in a session dir in place.
    Returns {enriched, matched, unmatched:[names]}."""
    session_dir = Path(session_dir)
    by_name = build_name_index(song_meta)
    enriched = matched = 0
    unmatched = set()
    for jf in sorted(session_dir.glob("*.json")):
        if jf.name == "manifest.json":
            continue
        sc = json.loads(jf.read_text())
        name = sc.get("node", {}).get("name")
        tm = by_name.get(name)
        if tm is None:
            unmatched.add(name)
        else:
            matched += 1
        jf.write_text(json.dumps(enrich_sidecar(sc, tm), indent=1))
        enriched += 1
    return {"enriched": enriched, "matched": matched, "unmatched": sorted(unmatched)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Enrich stem sidecars with live Remote Script device detail.")
    ap.add_argument("session_dir", help="ablation session dir with stem *.json sidecars")
    ap.add_argument("--metadata", default=None,
                    help="path to a song_metadata.json to join (default: pull live from Ableton)")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=9877)
    args = ap.parse_args(argv)

    if args.metadata:
        song_meta = json.loads(Path(args.metadata).read_text())
    else:
        from live_client import LiveClient
        from song_metadata import build_song_metadata
        client = LiveClient(host=args.host, port=args.port).connect()
        try:
            song_meta = build_song_metadata(client)
        finally:
            client.close()
    res = enrich_session(args.session_dir, song_meta)
    print(f"[ENRICH] {res['enriched']} sidecars | {res['matched']} matched to a track"
          f" | {len(res['unmatched'])} unmatched: {res['unmatched'][:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
