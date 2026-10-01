"""
probe_device_midi_io.py — the gate for the Sub Follower device shape: how much MIDI
can ONE M4L audio effect pull from other tracks through DeviceIO (device.midi_inputs),
and can it push MIDI to the sub track (device.midi_outputs)?

Answers, on the MIDI IO Probe device (build_midi_probe_device.py, 4 x [midiin]):
  P1  how many midi_inputs / midi_outputs does the device expose? (docs say 1 / 1)
  P2  which sources and tap points are offered (Pre FX / Post FX), and which
      destinations/channels for the output (is the sub track's instrument listed)?
  P3  do notes actually ARRIVE, and on which [midiin]? (/midiprobe/in/<k> OSC :9888)

The verdict picks the Sub Follower shape:
  several independent inputs -> single hub device
  one input                  -> tap stack (one tap device per source on a hub track)
  none / nothing arrives     -> relay tracks

Requires the get/set_device_midi_io Remote Script commands — app-bundle sync + Live
restart first. Put the probe device on any track of a set whose MIDI tracks have clips.

Run:  python probe_device_midi_io.py --enumerate-only
      python probe_device_midi_io.py [--dest "Sub"]
Routing changes are restored and playback is stopped on exit.
"""

import argparse
import socket
import struct
import sys
import time

from live_client import LiveClient

PROBE_NAME = "MIDI IO Probe"
OSC_PORT = 9888
PROBE_SECONDS = 8.0


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def parse_osc(data):
    """(address, [int|float args]) from one OSC packet (udpsend int/float args)."""
    i = data.index(b"\x00"); addr = data[:i].decode()
    j = (i + 4) & ~3
    k = data.index(b"\x00", j); tags = data[j:k].decode()
    p = (k + 4) & ~3
    vals = []
    for t in tags[1:]:
        if t == "i":
            vals.append(struct.unpack(">i", data[p:p+4])[0]); p += 4
        elif t == "f":
            vals.append(struct.unpack(">f", data[p:p+4])[0]); p += 4
    return addr, vals


def summarize_hits(messages):
    """{input k: set of pitches} from (address, [pitch, velocity]) note-on messages."""
    hits = {}
    for addr, vals in messages:
        if not addr.startswith("/midiprobe/in/") or len(vals) < 2 or vals[1] <= 0:
            continue
        hits.setdefault(int(addr.rsplit("/", 1)[1]), set()).add(int(vals[0]))
    return hits


def independent_inputs(routed, hits):
    """How many routed inputs carry ONLY their own source's notes.

    routed: {input k: set of pitches its source plays}. One port shared by every
    [midiin] shows the SAME notes on all inputs, so when every good input heard an
    identical set they count as one (pick sources with different notes to tell)."""
    good = [k for k, expected in routed.items()
            if hits.get(k) and hits[k] <= expected]
    if len(good) >= 2 and len({frozenset(hits[k]) for k in good}) == 1:
        return 1
    return len(good)


def verdict(n_inputs, n_independent):
    """Sub Follower device shape from the probe result."""
    if n_inputs >= 2 and n_independent >= 2:
        return "SINGLE HUB — one device pulls several tracks' MIDI independently"
    if n_inputs >= 1 and n_independent >= 1:
        return "TAP STACK — one MIDI input per device; one tap device per source"
    return "RELAY TRACKS — device MIDI pull unusable; route with helper tracks"


def find_probe(c):
    """(track_index, device_index) of the MIDI IO Probe device."""
    n = int(c.send("get_session_info").get("track_count", 0))
    for i in range(n):
        try:
            ti = c.send("get_track_info", {"track_index": i})
        except Exception:
            continue
        for d in ti.get("devices", []):
            if PROBE_NAME in (d.get("name") or ""):
                log("found probe on track %d (%r)" % (i, ti.get("name")))
                return i, d["index"]
    raise SystemExit("no track carrying a '%s' device found" % PROBE_NAME)


def midi_sources(c, exclude, limit):
    """[(track_index, name, pitches)] for MIDI tracks that have arrangement notes."""
    out = []
    n = int(c.send("get_session_info").get("track_count", 0))
    for i in range(n):
        if i == exclude or len(out) >= limit:
            continue
        try:
            ti = c.send("get_track_info", {"track_index": i})
        except Exception:
            continue
        if ti.get("kind") != "regular" or not ti.get("is_midi_track"):
            continue
        pitches = set()
        for clip in ti.get("arrangement_clips", [])[:4]:
            try:
                notes = c.send("get_arrangement_clip_notes",
                               {"track_index": i, "clip_index": clip["index"]})
                pitches.update(int(nt["pitch"]) for nt in notes.get("notes", []))
            except Exception:
                continue
        if pitches:
            out.append((i, ti.get("name"), pitches))
    return out


def sniff(seconds):
    """Every OSC message on the probe port during the window."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", OSC_PORT)); s.settimeout(1.0)
    msgs = []
    t0 = time.time()
    while time.time() - t0 < seconds:
        try:
            msgs.append(parse_osc(s.recvfrom(4096)[0]))
        except socket.timeout:
            continue
    s.close()
    return msgs


def describe(c, ti_idx, dev_idx, direction):
    """Log one direction's IO list; returns the command result."""
    info = c.send("get_device_midi_io", {"track_index": ti_idx, "device_index": dev_idx,
                                          "direction": direction})
    attr = "midi_outputs" if direction == "out" else "midi_inputs"
    if not info.get("has_" + attr):
        log("%s NOT exposed. io-like attrs: %s" % (attr, info.get("io_like_attrs")))
        return info
    io0 = info["ios"][0] if info.get("ios") else {}
    log("%s: io_count = %d" % (attr, info["io_count"]))
    log("  IO0 current: type=%r channel=%r" %
        (io0.get("routing_type"), io0.get("routing_channel")))
    types = io0.get("available_routing_types", [])
    log("  IO0 options (%d): %s%s" % (len(types), types[:12], " ..." if len(types) > 12 else ""))
    log("  IO0 channels: %s" % io0.get("available_routing_channels"))
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enumerate-only", action="store_true",
                    help="P1-P2 only: no routing changes, no playback")
    ap.add_argument("--dest", default="",
                    help="track name to route the device's MIDI output to (sub track)")
    args = ap.parse_args()

    with LiveClient(timeout=40) as c:
        ti_idx, dev_idx = find_probe(c)
        ins = describe(c, ti_idx, dev_idx, "in")
        outs = describe(c, ti_idx, dev_idx, "out")
        n_inputs = int(ins.get("io_count", 0)) if ins.get("has_midi_inputs") else 0

        if args.enumerate_only or n_inputs == 0:
            log("VERDICT: %s" % (verdict(n_inputs, 0) if n_inputs == 0 else
                                 "enumerate-only: %d MIDI input(s), no signal test" % n_inputs))
            return 0

        # P3: one distinct source per input, roll playback, see which [midiin] hears what
        sources = midi_sources(c, ti_idx, n_inputs)
        if not sources:
            log("no MIDI track with arrangement notes found — add clips and re-run")
            return 1
        saved, routed = {}, {}
        for io_i, (src_idx, name, pitches) in enumerate(sources):
            cur = c.send("get_device_midi_io", {"track_index": ti_idx, "device_index": dev_idx,
                                                 "io_index": io_i})
            saved[io_i] = cur["ios"][0].get("routing_type")
            r = c.send("set_device_midi_io", {"track_index": ti_idx, "device_index": dev_idx,
                                              "io_index": io_i, "source_index": src_idx})
            routed[io_i + 1] = pitches            # [midiin] k is 1-based in the OSC address
            log("set midi input %d -> %s: %s" % (io_i, name, r))
            after = c.send("get_device_midi_io", {"track_index": ti_idx, "device_index": dev_idx,
                                                   "io_index": io_i})
            log("  tap points on %s: %s" %
                (name, after["ios"][0].get("available_routing_channels")))

        if args.dest and outs.get("has_midi_outputs") and outs.get("io_count"):
            r = c.send("set_device_midi_io", {"track_index": ti_idx, "device_index": dev_idx,
                                              "io_index": 0, "direction": "out",
                                              "source_name": args.dest})
            log("set midi output 0 -> %s: %s" % (args.dest, r))
            after = c.send("get_device_midi_io", {"track_index": ti_idx, "device_index": dev_idx,
                                                   "io_index": 0, "direction": "out"})
            log("  output channels on %s: %s" %
                (args.dest, after["ios"][0].get("available_routing_channels")))

        log("starting playback; sniffing %gs of /midiprobe OSC" % PROBE_SECONDS)
        c.send("start_playback")
        hits = summarize_hits(sniff(PROBE_SECONDS))
        c.send("stop_playback")
        log("playback stopped")
        for k in sorted(routed):
            log("  input %d: expected %d pitches, heard %s"
                % (k, len(routed[k]), sorted(hits.get(k, set()))))

        for io_i, prev in saved.items():
            if prev:
                try:
                    c.send("set_device_midi_io", {"track_index": ti_idx, "device_index": dev_idx,
                                                  "io_index": io_i, "source_name": prev})
                    log("restored midi input %d -> %s" % (io_i, prev))
                except Exception as e:
                    log("restore input %d failed (%s) — set it manually to %r" % (io_i, e, prev))

        n_ind = independent_inputs(routed, hits)
        log("VERDICT: %s" % verdict(n_inputs, n_ind))
        return 0 if n_ind else 1


if __name__ == "__main__":
    sys.exit(main())
