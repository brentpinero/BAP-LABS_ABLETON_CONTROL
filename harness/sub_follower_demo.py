"""
sub_follower_demo.py — show that the Sub Follower is wired up and in time, without
touching the user's routing. The devices route themselves; this script only READS the
result and (optionally) measures it.

  python sub_follower_demo.py                 # report: Sends, the Sub Follow track, the sub
  python sub_follower_demo.py --null A SUB    # + null test: track A vs sub track SUB

The null test needs the Null Probe device (build_null_probe_device.py) in the User Library;
it adds a temporary SFT_NULL track and removes it. The sub must play the same patch and
notes as the source for the null to reach ~ -120 dB (see probe_follow_timing.py).
"""

import argparse
import sys
import time

from live_client import LiveClient
from probe_device_inputs import log
from probe_follow_timing import measure, new_track
from swap_ears_to_biquad import find_uri
from sub_follower_core import find_track


def report(c):
    n = int(c.send("get_session_info").get("track_count", 0))
    sends, followers = [], []
    for i in range(n):
        ti = c.send("get_track_info", {"track_index": i})
        for d in ti.get("devices", []):
            if "Sub Send" in d["name"]:
                io = {"track_index": i, "device_index": d["index"], "io_index": 0}
                inp = c.send("get_device_midi_io", dict(io))["ios"][0]
                out = c.send("get_device_midi_io", dict(io, direction="out"))["ios"][0]
                sends.append((i, ti["name"], inp.get("routing_type"), inp.get("routing_channel"),
                              out.get("routing_type")))
            elif "Sub Follower" in d["name"]:
                r = c.send("get_track_output_routing", {"track_index": i})
                followers.append((i, ti["name"], r.get("output_routing_type"),
                                  r.get("output_routing_channel")))
    for i, name, src, tap, dest in sends:
        log("Sub Send on %2d %-24s pulls %s / %s  -> %s" % (i, repr(name), src, tap, dest))
    for i, name, dest, chan in followers:
        log("Sub Follower on %2d %-20s -> %s / %s" % (i, repr(name), dest, chan))
    if not sends:
        log("no Sub Send devices found")
    if not followers:
        log("no Sub Follower found")
    return sends, followers


def null_test(c, src_ref, sub_ref):
    tracks = [dict(c.send("get_track_info", {"track_index": i}), index=i)
              for i in range(int(c.send("get_session_info")["track_count"]))]
    idx = {"SFT_A": find_track(tracks, src_ref), "SFT_SUB": find_track(tracks, sub_ref)}
    idx["SFT_NULL"] = new_track(c, "audio", "SFT_NULL", find_uri(c, "bap labs null probe"),
                                settle=2.0)
    try:
        measure(c, idx, "follow", "SFT_A", "SFT_SUB")
    finally:
        c.send("stop_playback")
        c.send("delete_track", {"track_index": idx["SFT_NULL"]}); time.sleep(0.3)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--null", nargs=2, metavar=("SOURCE", "SUB"),
                    help="null-test a source track against the sub track (names or indices)")
    args = ap.parse_args()
    with LiveClient(timeout=40) as c:
        report(c)
        if args.null:
            null_test(c, *args.null)
    return 0


if __name__ == "__main__":
    sys.exit(main())
