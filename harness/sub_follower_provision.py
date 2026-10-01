"""
sub_follower_provision.py — set up the Sub Follower on the open Live set: make one sub
track follow every MIDI track in the bass group.

What it builds (see build_sub_follower_device.py for why it has this shape):
  * a hub audio track SUB_FOLLOW_HUB with one Sub Follow Tap per bass track, each
    pulling that track's MIDI (Post FX) and sending it to the sub track's Track In.
    Each tap gets its own Slot (its position) and is renamed "Follow <track>"; its
    Follow switch is the automatable on/off.
  * the Sub Follower MIDI effect in front of the sub track's instrument, with Floor
    set by the auto-octave analysis of the bass group's arrangement notes.

Re-running --apply is safe: existing taps keep their source (matched by name and
occurrence, so their automation survives), new bass tracks get a new tap, and taps
whose source is gone are reported, not deleted.

Usage:
    python sub_follower_provision.py --sub "Sub" --dry-run
    python sub_follower_provision.py --sub "Sub" --apply      [--group Bass] [--floor 28]
    python sub_follower_provision.py --sub "Sub" --analyze    # re-pick Floor only
    python sub_follower_provision.py --sub "Sub" --teardown

Needs both devices in the User Library (BAP Labs Sub Follow Tap, BAP Labs Sub Follower)
and the Remote Script commands set_device_midi_io / set_device_name.
Limit: the analysis reads Arrangement clips only (no Session-clip note reader yet).
"""

import argparse
import sys
import time

import sub_follower_core as sf
from live_client import LiveClient, LiveError
from swap_ears_to_biquad import find_uri

HUB_TRACK = "SUB_FOLLOW_HUB"
TAP_DEVICE = "bap labs sub follow tap"
FOLLOWER_DEVICE = "bap labs sub follower"


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def gather(c):
    """get_track_info for every regular/group track, in session order."""
    tracks = []
    for i in range(int(c.send("get_session_info").get("track_count", 0))):
        try:
            ti = c.send("get_track_info", {"track_index": i})
        except Exception:
            continue
        ti["index"] = i
        tracks.append(ti)
    return tracks


def tap_sources(c, hub):
    """Source name of each tap on the hub track, in device order."""
    devices = c.send("get_track_info", {"track_index": hub}).get("devices", [])
    names = []
    for d in devices:
        io = c.send("get_device_midi_io", {"track_index": hub, "device_index": d["index"],
                                            "io_index": 0})
        names.append(io["ios"][0].get("routing_type", "") if io.get("ios") else "")
    return names


def read_notes(c, sources):
    """Every source's arrangement notes in absolute beats (clip start + note start)."""
    notes = []
    for idx, _ in sources:
        clips = c.send("get_arrangement_clips", {"track_index": idx}).get("clips", [])
        for clip in clips:
            if not clip.get("is_midi_clip"):
                continue
            got = c.send("get_arrangement_clip_notes",
                         {"track_index": idx, "clip_index": clip["index"]})
            notes += [{"pitch": int(n["pitch"]), "duration": float(n["duration"]),
                       "start": float(clip["start_time"]) + float(n["start_time"])}
                      for n in got.get("notes", []) if not n.get("mute")]
    return notes


def follower_index(c, sub):
    devices = c.send("get_track_info", {"track_index": sub}).get("devices", [])
    return next((d["index"] for d in devices if "Sub Follower" in d["name"]), None)


def analyze(c, sub, sources, floor=None):
    """Pick the fold floor from the sources' notes (or use `floor`) and set it."""
    fol = follower_index(c, sub)
    if fol is None:
        raise SystemExit("no Sub Follower device on the sub track — run --apply first")
    if floor is None:
        notes = read_notes(c, sources)
        if not notes:
            log("no arrangement notes in the bass group; Floor left unchanged")
            return None
        floor, scores = sf.choose_floor(notes)
        for s in scores:
            log("  floor %-3s (%.1f Hz): out-of-band %.2f  jumps %.2f  cost %.2f%s"
                % (sf.note_name(s["floor"]), sf.note_hz(s["floor"]), s["range_cost"],
                   s["jump_cost"], s["cost"], "  <- chosen" if s["floor"] == floor else ""))
        log("%d notes analysed" % len(notes))
    c.send("set_device_parameter_by_name", {"track_index": sub, "device_index": fol,
                                            "param_name": "Floor", "value": floor})
    log("Floor = %s (MIDI %d, %.1f Hz); sub plays %s..%s"
        % (sf.note_name(floor), floor, sf.note_hz(floor), sf.note_name(floor),
           sf.note_name(floor + 11)))
    return floor


def apply(c, tracks, sub, sources, floor=None):
    hub = next((t["index"] for t in tracks if t["name"] == HUB_TRACK), None)
    if hub is None:
        c.send("create_audio_track", {"index": -1}); time.sleep(0.4)
        hub = int(c.send("get_session_info").get("track_count", 0)) - 1
        c.send("set_track_name", {"track_index": hub, "name": HUB_TRACK})
        log("created hub track %d (%s)" % (hub, HUB_TRACK))

    existing = tap_sources(c, hub)
    keep, add, stale = sf.plan_taps(existing, sources)
    if add:
        tap_uri = find_uri(c, TAP_DEVICE)
        if not tap_uri:
            raise SystemExit("'%s' not found in the User Library browser" % TAP_DEVICE)
    for n, (idx, name) in enumerate(add):
        c.send("load_browser_item", {"track_index": hub, "item_uri": tap_uri}); time.sleep(1.5)
        keep.append((len(existing) + n, idx, name))

    for pos, idx, name in keep:
        tap = {"track_index": hub, "device_index": pos, "io_index": 0}
        c.send("set_device_midi_io", dict(tap, source_index=idx, channel="Post FX"))
        c.send("set_device_midi_io", dict(tap, direction="out", source_index=sub,
                                          channel="Track In"))
        c.send("set_device_parameter_by_name", {"track_index": hub, "device_index": pos,
                                                "param_name": "Slot", "value": pos})
        c.send("set_device_name", {"track_index": hub, "device_index": pos,
                                   "name": "Follow %s" % name})
        log("tap %d: %s (track %d) -> sub track %d" % (pos, name, idx, sub))
    for pos in stale:
        log("tap %d follows %r, which is no longer in the bass group (left in place)"
            % (pos, existing[pos]))

    if follower_index(c, sub) is None:
        uri = find_uri(c, FOLLOWER_DEVICE)
        if not uri:
            raise SystemExit("'%s' not found in the User Library browser" % FOLLOWER_DEVICE)
        try:
            c.send("load_browser_item", {"track_index": sub, "item_uri": uri})
        except LiveError as e:
            if "invisible" not in str(e):
                raise
            # Live cannot load onto a track hidden in a folded group: unfold its parents
            for g in reversed(sf.ancestors(tracks, sub)):
                c.send("fold_track", {"track_index": g, "fold": False})
                log("unfolded group track %d so the sub track is visible" % g)
            c.send("load_browser_item", {"track_index": sub, "item_uri": uri})
        time.sleep(1.5)
        log("loaded Sub Follower on sub track %d" % sub)
    analyze(c, sub, sources, floor)
    log("done: %d tap(s) on %s, %d new, %d stale" % (len(keep), HUB_TRACK, len(add), len(stale)))


def teardown(c, tracks, sub):
    fol = follower_index(c, sub)
    if fol is not None:
        c.send("delete_device", {"track_index": sub, "device_index": fol})
        log("removed Sub Follower from sub track %d" % sub)
    hub = next((t["index"] for t in tracks if t["name"] == HUB_TRACK), None)
    if hub is not None:
        c.send("delete_track", {"track_index": hub})
        log("deleted hub track %d (%s)" % (hub, HUB_TRACK))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--sub", required=True, help="sub track name or index")
    ap.add_argument("--group", default="bass", help="bass group name (substring)")
    ap.add_argument("--floor", type=int, help="set this fold floor (MIDI) instead of analysing")
    mode = ap.add_mutually_exclusive_group(required=True)
    for m in ("dry-run", "apply", "analyze", "teardown"):
        mode.add_argument("--" + m, action="store_true")
    args = ap.parse_args()

    with LiveClient(timeout=40) as c:
        tracks = gather(c)
        try:
            sub = sf.find_track(tracks, args.sub)
            hub = next((t["index"] for t in tracks if t["name"] == HUB_TRACK), None)
            group, sources = sf.find_sources(tracks, args.group, exclude=(sub, hub))
        except ValueError as e:
            raise SystemExit(str(e))
        names = {t["index"]: t["name"] for t in tracks}
        log("sub track: %d %r   bass group: %d %r   sources: %d"
            % (sub, names.get(sub), group, names.get(group), len(sources)))
        for idx, name in sources:
            log("  follows %d %r" % (idx, name))
        if not sources and not args.teardown:
            raise SystemExit("no MIDI tracks in the bass group to follow")

        if args.apply:
            apply(c, tracks, sub, sources, args.floor)
        elif args.analyze:
            analyze(c, sub, sources, args.floor)
        elif args.teardown:
            teardown(c, tracks, sub)
        else:
            log("dry run: nothing changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
