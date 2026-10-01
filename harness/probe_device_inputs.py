"""
probe_device_inputs.py — the make-or-break gate for the CAPTURE-TRACK-FREE analysis
substrate: can the aggregator device PULL audio from arbitrary tracks via the Live 10+
DeviceIO routing API (device audio_inputs), instead of being fed by routed capture
tracks?

Documented precedent (Audio Routes / Multi Analyser) demonstrates 16 stereo inputs per
device; our aggregator declares 32 pairs — this probe answers, on the REAL device:
  P1  does the python LOM expose device.audio_inputs at all?
  P2  how many IOs does the 64ch aggregator expose (32? 16? +main-in)?
  P3  do groups / returns / master appear as routable sources?
  P4  does audio actually ARRIVE on the pair we set (nonzero /agg/ch OSC), and which
      io_index maps to which OSC channel?

Requires the DeviceIO Remote Script commands (get_device_audio_inputs /
set_device_audio_input) — app-bundle sync + Live restart first.

Run:  python probe_device_inputs.py            # enumerate + live signal probe
      python probe_device_inputs.py --enumerate-only
All routing changes are restored and playback is stopped on exit.
"""

import argparse
import socket
import struct
import sys
import time

from live_client import LiveClient

AGG_TRACK = "AGG_ANALYSIS_0"
OSC_PORT = 9886
PROBE_SECONDS = 8.0


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def parse_osc(data):
    """(address, [float|int args]) from one OSC packet as udpsend emits it."""
    i = data.index(b"\x00"); addr = data[:i].decode()
    j = (i + 4) & ~3
    k = data.index(b"\x00", j); tags = data[j:k].decode()
    p = (k + 4) & ~3
    vals = []
    for t in tags[1:]:
        if t in "fi":
            vals.append(struct.unpack(">" + t, data[p:p+4])[0]); p += 4
    return addr, vals


def find_aggregator(c):
    """(track_index, device_index) of the first Aggregator device, wherever it
    lives (track renames don't survive an unsaved restart — match by device)."""
    n = int(c.send("get_session_info").get("track_count", 0))
    for i in range(n):
        try:
            ti = c.send("get_track_info", {"track_index": i})
        except Exception:
            continue
        for di, d in enumerate(ti.get("devices", [])):
            name = d.get("name") if isinstance(d, dict) else d
            if "Aggregator" in (name or ""):
                log("found aggregator on track %d (%r)" % (i, ti.get("name")))
                return i, di
    raise SystemExit("no track carrying an Aggregator device found")


def pick_sources(c):
    """One regular track, one group, one return name from the live set."""
    n = int(c.send("get_session_info").get("track_count", 0))
    regular = group = None
    for i in range(n):
        try:
            ti = c.send("get_track_info", {"track_index": i})
        except Exception:
            continue
        kind = ti.get("kind", "regular")
        if regular is None and kind == "regular" and ti.get("name") != AGG_TRACK:
            regular = (i, ti.get("name"))
        if group is None and kind == "group":
            group = (i, ti.get("name"))
    return regular, group


def sniff_hot_channels(seconds):
    """Set of /agg/ch/<k> indices with any nonzero value during the window."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", OSC_PORT)); s.settimeout(1.0)
    hot = {}
    t0 = time.time()
    while time.time() - t0 < seconds:
        try:
            a, v = parse_osc(s.recvfrom(4096)[0])
        except socket.timeout:
            continue
        if a.startswith("/agg/ch/") and any(x > 1e-6 for x in v):
            ch = int(a.split("/")[3])
            hot[ch] = [round(x, 5) for x in v]
    s.close()
    return hot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enumerate-only", action="store_true",
                    help="P1-P3 only: no routing changes, no playback")
    args = ap.parse_args()

    with LiveClient(timeout=40) as c:
        ti_idx, dev_idx = find_aggregator(c)
        log("aggregator = track %d device %d" % (ti_idx, dev_idx))

        # P1 + P2: enumerate
        info = c.send("get_device_audio_inputs",
                      {"track_index": ti_idx, "device_index": dev_idx})
        if not info.get("has_audio_inputs"):
            log("P1 FAIL: no device.audio_inputs. io-like attrs: %s"
                % info.get("io_like_attrs"))
            log("VERDICT: BLOCKED — python LOM does not expose DeviceIO on this device")
            return 1
        io_count = info["io_count"]
        io0 = info["ios"][0] if info.get("ios") else {}
        types = io0.get("available_routing_types", [])
        log("P1 PASS: audio_inputs exposed")
        log("P2: io_count = %d (aggregator declares 32 pairs + main in)" % io_count)
        log("IO0 current: type=%r channel=%r" %
            (io0.get("routing_type"), io0.get("routing_channel")))
        log("IO0 available sources: %d  channels: %d" %
            (len(types), io0.get("available_routing_channel_count", 0)))

        # P3: source coverage by kind
        regular, group = pick_sources(c)
        have = {"regular": regular and regular[1] in types,
                "group": group and (group[1] in types),
                "return-ish": any(t.startswith(("A-", "B-", "C-")) for t in types),
                "master-ish": any("Master" in t or "Main" in t for t in types)}
        log("P3 source visibility in IO0 options: %s" % have)
        log("IO0 sample of options: %s%s" %
            (types[:12], " ..." if len(types) > 12 else ""))

        if args.enumerate_only:
            log("enumerate-only: stopping before routing changes")
            return 0

        # P4: point two IOs at real sources, roll playback, watch which gch light up.
        # io 0 is usually the device's MAIN input (the track's own chain) — probe
        # ios 1 and 2, which should be plugin~ pairs 2 and 3 (gch 1 and 2).
        probes = []
        if regular:
            probes.append((1, {"source_index": regular[0]}, regular[1]))
        if group:
            probes.append((2, {"source_name": group[1]}, group[1]))
        saved = {}
        chans = io0.get("available_routing_channels", [])
        tap = next((ch for ch in ("Post Mixer", "Post FX") if ch in chans),
                   None)
        for io_i, src, label in probes:
            cur = c.send("get_device_audio_inputs",
                         {"track_index": ti_idx, "device_index": dev_idx,
                          "io_index": io_i})
            saved[io_i] = cur["ios"][0].get("routing_type")
            req = {"track_index": ti_idx, "device_index": dev_idx, "io_index": io_i}
            req.update(src)
            if tap:
                req["channel"] = tap
            r = c.send("set_device_audio_input", req)
            log("P4 set io %d -> %s (%s): %s" % (io_i, label, tap or "default tap", r))

        log("starting playback; sniffing %gs of /agg OSC" % PROBE_SECONDS)
        c.send("start_playback")
        time.sleep(1.0)
        hot = sniff_hot_channels(PROBE_SECONDS)
        c.send("stop_playback")
        log("playback stopped; hot channels: %s" % sorted(hot))
        for ch in sorted(hot):
            log("  gch %d: %s" % (ch, hot[ch]))

        # restore: point probed IOs back at their previous source
        for io_i, prev in saved.items():
            if prev:
                try:
                    c.send("set_device_audio_input",
                           {"track_index": ti_idx, "device_index": dev_idx,
                            "io_index": io_i, "source_name": prev})
                    log("restored io %d -> %s" % (io_i, prev))
                except Exception as e:
                    log("restore io %d failed (%s) — set it manually to %r"
                        % (io_i, e, prev))

        ok = bool(hot)
        log("VERDICT: %s" % (
            "GATE PASSED — device-pull routing feeds the aggregator (io->gch map above); "
            "capture tracks are obsolete" if ok else
            "no signal arrived — check io->pair mapping / tap point / Remote Script log"))
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
