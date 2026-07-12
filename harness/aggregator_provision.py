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
import os
import sys
import time
from pathlib import Path

from live_client import LiveClient
from perception_config import cfg
from perception_select import gather_nodes, select_nodes, selection_summary
from swap_ears_to_biquad import BIQUAD, find_uri

AGG_TRACK = "AGG_ANALYSIS"
CAP_PREFIX = "CAPX_"
STATE = Path(__file__).resolve().parent.parent / "sandbox_sessions" / "aggregator_state.json"


def _snapshot():
    try:
        return json.loads((STATE.parent / "live_ears.json").read_text())
    except Exception:
        return None


def _write_state(state):
    """Persist the provisioning state atomically (tmp + os.replace), so the ears
    daemon's ~2s hot-reload poll can never read a half-written file — same pattern the
    snapshot writer uses (live_ears._snapshot_writer)."""
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1))
    os.replace(tmp, STATE)


def plan(c, usable_pairs=None, max_instrument=None):
    """Allocate selected non-master nodes across as many aggregator devices as
    needed — coverage is capacity-driven, NOT name-gated, so ANY project structure
    up to `max_instrument` nodes is fully instrumented regardless of naming/grouping.

    Each device has `n_pairs` input pairs (cfg aggregator_channels, 32 = 64ch); pair 0
    is reserved for the device track's own input, leaving `usable` = n_pairs-1 routable
    pairs each. Node slot s -> device s//usable, local pair s%usable+1. The GLOBAL osc
    channel is device*n_pairs + local_pair, matching the per-device channel base baked
    into build_aggregator_device (so one OSC port serves all devices with no collision).

    Duplicate names are NO LONGER skipped: a leaf routes by source_index (its song
    index), which the Remote Script disambiguates by (name, occurrence). Nodes without
    a song index (returns) fall back to name routing, where names are unique anyway.

    Returns (items, sel, n_devices)."""
    n_pairs = int(cfg("aggregator_channels"))
    usable = int(usable_pairs) if usable_pairs is not None else n_pairs - 1
    cap = int(max_instrument) if max_instrument is not None else int(cfg("max_instrument"))

    nodes = gather_nodes(c, _snapshot())
    sel = select_nodes(nodes)                      # ranked; ties broken by energy then ref
    items = []
    for node in sel:
        if node.get("kind") == "master":
            continue                               # master keeps its own device
        if len(items) >= cap:
            break
        slot = len(items)
        device = slot // usable
        local_pair = slot % usable + 1             # 1..n_pairs-1 (0 reserved)
        ref = node["ref"]
        src_index = ref if isinstance(ref, int) and ref >= 0 else None
        items.append({
            "ref": ref, "name": node["name"], "kind": node["kind"],
            "group_id": str(node.get("group_id", "-1")),
            "device": device, "pair": local_pair,
            "channel": "%d/%d" % (2 * local_pair + 1, 2 * local_pair + 2),
            "osc_channel": device * n_pairs + local_pair,     # global (device base + pair)
            "source_index": src_index, "reasons": node["reasons"],
        })
    n_dev = (len(items) + usable - 1) // usable if items else 0
    return items, sel, n_dev


def _agg_device_uri(c, device, n_pairs):
    """Browser URI for device `device`'s aggregator variant. Device 0 uses the base-0
    device; device d>0 REQUIRES its own base-(d*n_pairs) variant (compiled from
    build_aggregator_device.py n_pairs <base>) — we never fall back to base-0 for d>0,
    which would make two devices emit the same channels and collide."""
    base = device * n_pairs
    if base == 0:
        uri = find_uri(c, "bap labs mix analysis aggregator")
    else:
        uri = find_uri(c, "mix analysis aggregator base%d" % base)
    if not uri:
        raise RuntimeError(
            "aggregator device for base %d not found in browser. Build+compile it: "
            "`python build_aggregator_device.py %d %d` then convert to .amxd."
            % (base, n_pairs, base))
    return uri


def _ensure_aggregators(c, n_dev, n_pairs):
    """Ensure `n_dev` aggregator tracks exist (AGG_ANALYSIS_0.._{n_dev-1}), each loaded
    with its base-matched device variant. Returns the list of track indices by device."""
    existing = {}
    n = int(c.send("get_session_info").get("track_count", 0))
    for i in range(n):
        try:
            ti = c.send("get_track_info", {"track_index": i})
            nm = ti.get("name", "")
            if nm.startswith(AGG_TRACK) and any("Aggregator" in d["name"] for d in ti.get("devices", [])):
                existing[nm] = i
        except Exception:
            pass
    tracks = []
    for d in range(n_dev):
        name = "%s_%d" % (AGG_TRACK, d)
        if name in existing:
            tracks.append(existing[name]); continue
        uri = _agg_device_uri(c, d, n_pairs)
        c.send("create_audio_track", {"index": -1}); time.sleep(0.4)
        idx = int(c.send("get_session_info").get("track_count", 0)) - 1
        c.send("set_track_name", {"track_index": idx, "name": name})
        c.send("load_browser_item", {"track_index": idx, "item_uri": uri}); time.sleep(1.3)
        tracks.append(idx)
    return tracks


def apply(c, items, n_dev):
    n_pairs = int(cfg("aggregator_channels"))
    agg_tracks = _ensure_aggregators(c, n_dev, n_pairs)
    caps, bmap = [], {}
    for it in items:
        c.send("create_audio_track", {"index": -1}); time.sleep(0.35)
        ci = int(c.send("get_session_info").get("track_count", 0)) - 1
        c.send("set_track_name", {"track_index": ci, "name": CAP_PREFIX + str(it["ref"])})
        # route by source_index (dup-name safe); returns/oddballs fall back to name.
        if it.get("source_index") is not None:
            ir = c.send("set_track_input_routing",
                        {"track_index": ci, "source_index": it["source_index"], "channel": "Post FX"})
        else:
            ir = c.send("set_track_input_routing",
                        {"track_index": ci, "source_name": it["name"], "channel": "Post FX"})
        c.send("set_track_monitor", {"track_index": ci, "state": 0})
        dest = "%s_%d" % (AGG_TRACK, it["device"])
        r = c.send("set_track_output_routing", {"track_index": ci, "dest_name": dest, "channel": it["channel"]})
        ok = it["channel"].split("/")[0] in str(r.get("output_routing_channel", ""))
        caps.append(ci)
        bmap[it["osc_channel"]] = {"track_id": "agg-%s" % it["ref"], "name": it["name"],
                                   "kind": it["kind"], "group_id": it["group_id"]}
        flag = "" if not ir.get("ambiguous") else " (name-ambiguous!)"
        print(f"  dev{it['device']} routed {str(it['name'])[:20]:20s} -> pair {it['pair']:2d} "
              f"(ch {it['channel']}) gch {it['osc_channel']:3d} {'OK' if ok else 'CHANNEL?'}{flag}",
              flush=True)
    _write_state({"agg_tracks": agg_tracks, "cap_tracks": caps,
                  "map": {str(k): v for k, v in bmap.items()}})
    return bmap


def commit(c):
    """DESTRUCTIVE: remove the per-track biquad device from every non-master track so
    the aggregator becomes the SOLE analysis source (master keeps its own device).
    Idempotent + resumable (a re-run only touches tracks that still have the device).
    Throttled so a mass device-delete doesn't stress Live."""
    n = int(c.send("get_session_info").get("track_count", 0))
    removed, failed, skipped = 0, [], 0
    for i in range(n):
        try:
            ti = c.send("get_track_info", {"track_index": i})
            guard = 0
            while guard < 4:
                idx = next((d["index"] for d in ti.get("devices", []) if d["name"] == BIQUAD), None)
                if idx is None:
                    break
                c.send("delete_device", {"track_index": i, "device_index": idx})
                time.sleep(0.4)
                ti = c.send("get_track_info", {"track_index": i})
                removed += 1
                guard += 1
            if guard == 0:
                skipped += 1
            if (i + 1) % 15 == 0:
                print(f"  [commit] {i + 1}/{n} tracks scanned, {removed} devices removed", flush=True)
        except Exception as e:
            failed.append((i, str(e)[:30]))
    print(f"[commit] removed {removed} per-track biquad devices "
          f"({skipped} tracks had none); failures {len(failed)}: {failed[:5]}")
    return removed, failed


def teardown(c):
    if not STATE.exists():
        print("no state file; nothing to tear down"); return
    st = json.loads(STATE.read_text())
    # agg_tracks (multi-device) or legacy single agg_track
    agg = st.get("agg_tracks") or ([st.get("agg_track")] if st.get("agg_track") is not None else [])
    for ci in sorted(st.get("cap_tracks", []) + list(agg), reverse=True):
        if ci is None:
            continue
        try:
            c.send("delete_track", {"track_index": ci}); time.sleep(0.2)
        except Exception as e:
            print(f"  delete {ci} failed: {e}")
    STATE.unlink()
    print("torn down capture tracks + AGG track")


def main(argv):
    mode = ("--apply" if "--apply" in argv else "--teardown" if "--teardown" in argv
            else "--commit" if "--commit" in argv else "--dry-run")
    with LiveClient(timeout=40) as c:
        if mode == "--teardown":
            teardown(c); return 0
        if mode == "--commit":
            print("[commit] removing per-track biquad devices on all non-master tracks "
                  "(aggregator becomes the sole source)...")
            commit(c); return 0
        items, sel, n_dev = plan(c)
        print(f"selection: {len(sel)} nodes ({selection_summary(sel)}); "
              f"instrumenting {len(items)} across {n_dev} aggregator device(s) "
              f"(master keeps its own device):\n")
        for it in items:
            print(f"  dev{it['device']} pair {it['pair']:2d}  gch {it['osc_channel']:3d}  "
                  f"{str(it['name'])[:24]:24s} {it['kind']:7s} "
                  f"{'idx%d' % it['source_index'] if it['source_index'] is not None else 'by-name':8s} "
                  f"{it['reasons']}")
        if n_dev > 1:
            print(f"\n  NOTE: {n_dev} devices needed. Device 0 = base-0 aggregator; devices 1..{n_dev-1} "
                  f"require compiled base variants (build_aggregator_device.py {cfg('aggregator_channels')} <base>).")
        if mode == "--dry-run":
            print("\ndry-run. Re-run with --apply to create capture tracks + route.")
            return 0
        print("\n[apply] creating capture tracks + routing...")
        apply(c, items, n_dev)
        print(f"\napplied. Bridge map + state -> {STATE.name}. "
              f"Run the aggregator_bridge with this map to feed the perception layer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
