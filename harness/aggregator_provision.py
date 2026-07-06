"""
aggregator_provision.py — the Phase 3 reconcile controller: turn a select_nodes
decision into live routing (capture tracks -> aggregator channels) + the bridge map.

Ties the pipeline together:
    select_nodes (which nodes)  ->  THIS (route them in)  ->  aggregator_bridge (OSC)

For each selected non-master node it creates a thin CAPTURE track (input = the node,
Post-FX + monitor In, NON-destructive: the node still reaches Master) whose OUTPUT is
routed to a specific input pair of the aggregator device. The bridge then maps that
channel -> a synthetic track-id so the perception layer sees the node.

v1 is NON-destructive validation: it does NOT remove the nodes' existing per-track
devices, so you can compare 'agg-<node>' against the real node before committing.
Pair 0 (Track In) is reserved (the aggregator track's own input); routable pairs are 1..N-1.

Modes:
    python aggregator_provision.py                 # DRY-RUN: print the plan
    python aggregator_provision.py --apply         # create capture tracks + route
    python aggregator_provision.py --teardown      # delete the capture tracks + AGG track

State (created tracks + bridge map) is persisted to sandbox_sessions/aggregator_state.json
so --teardown and the bridge can pick it up.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from live_client import LiveClient
from perception_select import gather_nodes, select_nodes, selection_summary
from swap_ears_to_biquad import find_uri

AGG_TRACK = "AGG_ANALYSIS"
CAP_PREFIX = "CAPX_"
STATE = Path(__file__).resolve().parent.parent / "sandbox_sessions" / "aggregator_state.json"


def _snapshot():
    try:
        return json.loads((STATE.parent / "live_ears.json").read_text())
    except Exception:
        return None


def plan(c, max_pairs=7):
    """Assign selected non-master nodes to aggregator input pairs (1..max_pairs)."""
    nodes = gather_nodes(c, _snapshot())
    sel = select_nodes(nodes)
    routable = [s for s in sel if s.get("kind") != "master"][:max_pairs]
    items = []
    for i, node in enumerate(routable):
        pair = i + 1                       # pair 0 reserved for the AGG track's own input
        items.append({
            "ref": node["ref"], "name": node["name"], "kind": node["kind"],
            "group_id": str(node.get("group_id", "-1")),
            "pair": pair, "channel": "%d/%d" % (2 * pair + 1, 2 * pair + 2),
            "osc_channel": pair, "reasons": node["reasons"],
        })
    return items, sel


def _ensure_aggregator(c, uri):
    n = int(c.send("get_session_info").get("track_count", 0))
    for i in range(n):
        try:
            ti = c.send("get_track_info", {"track_index": i})
            if ti.get("name") == AGG_TRACK and any("Aggregator" in d["name"] for d in ti.get("devices", [])):
                return i
        except Exception:
            pass
    c.send("create_audio_track", {"index": -1}); time.sleep(0.4)
    idx = int(c.send("get_session_info").get("track_count", 0)) - 1
    c.send("set_track_name", {"track_index": idx, "name": AGG_TRACK})
    c.send("load_browser_item", {"track_index": idx, "item_uri": uri}); time.sleep(1.3)
    return idx


def apply(c, items):
    uri = find_uri(c, "bap labs mix analysis aggregator")
    if not uri:
        raise RuntimeError("aggregator device not found in browser")
    agg = _ensure_aggregator(c, uri)
    caps, bmap = [], {}
    for it in items:
        c.send("create_audio_track", {"index": -1}); time.sleep(0.35)
        ci = int(c.send("get_session_info").get("track_count", 0)) - 1
        c.send("set_track_name", {"track_index": ci, "name": CAP_PREFIX + str(it["ref"])})
        c.send("set_track_input_routing", {"track_index": ci, "source_name": it["name"], "channel": "Post FX"})
        c.send("set_track_monitor", {"track_index": ci, "state": 0})
        r = c.send("set_track_output_routing", {"track_index": ci, "dest_name": AGG_TRACK, "channel": it["channel"]})
        ok = it["channel"].split("/")[0] in str(r.get("output_routing_channel", ""))
        caps.append(ci)
        bmap[it["osc_channel"]] = {"track_id": "agg-%s" % it["ref"], "name": it["name"],
                                   "kind": it["kind"], "group_id": it["group_id"]}
        print(f"  routed {it['name'][:22]:22s} -> pair {it['pair']} (ch {it['channel']}) "
              f"{'OK' if ok else 'CHANNEL?'}", flush=True)
    STATE.write_text(json.dumps({"agg_track": agg, "cap_tracks": caps,
                                 "map": {str(k): v for k, v in bmap.items()}}, indent=1))
    return bmap


def teardown(c):
    if not STATE.exists():
        print("no state file; nothing to tear down"); return
    st = json.loads(STATE.read_text())
    for ci in sorted(st.get("cap_tracks", []) + [st.get("agg_track")], reverse=True):
        if ci is None:
            continue
        try:
            c.send("delete_track", {"track_index": ci}); time.sleep(0.2)
        except Exception as e:
            print(f"  delete {ci} failed: {e}")
    STATE.unlink()
    print("torn down capture tracks + AGG track")


def main(argv):
    mode = "--apply" if "--apply" in argv else "--teardown" if "--teardown" in argv else "--dry-run"
    with LiveClient(timeout=40) as c:
        if mode == "--teardown":
            teardown(c); return 0
        items, sel = plan(c)
        print(f"selection: {len(sel)} nodes ({selection_summary(sel)}); "
              f"routing {len(items)} to the aggregator (master keeps its own device):\n")
        for it in items:
            print(f"  pair {it['pair']}  ch {it['channel']:5s}  {it['name'][:26]:26s} "
                  f"{it['kind']:7s} {it['reasons']}")
        if mode == "--dry-run":
            print("\ndry-run. Re-run with --apply to create capture tracks + route.")
            return 0
        print("\n[apply] creating capture tracks + routing...")
        apply(c, items)
        print(f"\napplied. Bridge map + state -> {STATE.name}. "
              f"Run the aggregator_bridge with this map to feed the perception layer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
