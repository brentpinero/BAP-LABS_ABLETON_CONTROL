"""
probe_follow_timing.py — the TIMING gate for the Sub Follower: when an M4L audio effect
forwards one track's MIDI to another track (DeviceIO midi_inputs -> midi_outputs), does
the destination play in time with the source, and which monitor state does it need?

Method: a null test. Source and destination carry the SAME default instrument, so the
forwarded notes should produce identical audio. The Null Probe device
(build_null_probe_device.py) reports RMS of A, B and A - B; a sample-accurate follow
nulls, a lag leaves a residual that converts to milliseconds.

Cases, on a throwaway scene this script builds and removes (never save the set):
  same     A vs A            sanity: the probe itself nulls
  native   A vs A2           two tracks, identical clips: Live's own sync + the
                             instrument being deterministic (the baseline to beat)
  lagged   A vs LAG          notes ~1 ms late: proves the null test SEES a lag
  auto     A vs SUB          forwarded MIDI, sub monitor = Auto
  in       A vs SUB          forwarded MIDI, sub monitor = In

Needs both probe devices compiled into the User Library and the get/set_device_midi_io
Remote Script commands. Run:  python probe_follow_timing.py
"""

import math
import sys
import time

import probe_device_midi_io
from live_client import LiveClient
from probe_device_inputs import log
from sub_follower_core import note_hz
from swap_ears_to_biquad import find_uri

OSC_PORT = 9889
SECONDS = 6.0
PITCHES = [36, 38]
NAMES = ["SFT_A", "SFT_A2", "SFT_LAG", "SFT_SUB", "SFT_TAP", "SFT_NULL"]
LAG_BEATS = 0.002           # known-lag control: notes this much late (~1 ms at 113 BPM)
MONITOR_IN, MONITOR_AUTO = 0, 1


def residual(samples):
    """(level_a, level_b, ratio) from [(a, b, diff)] RMS samples; ratio is the energy
    of A - B relative to A (0 = perfect null, ~1.41 = unrelated signals)."""
    ea = sum(a * a for a, _, _ in samples)
    eb = sum(b * b for _, b, _ in samples)
    ed = sum(d * d for _, _, d in samples)
    n = max(len(samples), 1)
    ratio = math.sqrt(ed / ea) if ea > 0 else float("nan")
    return math.sqrt(ea / n), math.sqrt(eb / n), ratio


def delay_ms(ratio, hz):
    """Lag implied by a null residual between two equal sines: |a - b| / |a| =
    2 sin(pi f d). Only meaningful when both levels match."""
    return math.asin(min(ratio, 2.0) / 2.0) / (math.pi * hz) * 1000.0


def count(c):
    return int(c.send("get_session_info").get("track_count", 0))


def new_track(c, kind, name, uri=None, settle=1.0):
    c.send("create_%s_track" % kind, {"index": -1}); time.sleep(0.4)
    idx = count(c) - 1
    c.send("set_track_name", {"track_index": idx, "name": name})
    if uri:
        c.send("load_browser_item", {"track_index": idx, "item_uri": uri}); time.sleep(settle)
    return idx


def setup(c):
    items = c.send("get_browser_items_at_path", {"path": "instruments"}).get("items", [])
    inst = next(it["uri"] for it in items if it.get("name") == "Operator")
    tap_uri = find_uri(c, "bap labs midi io probe")
    null_uri = find_uri(c, "bap labs null probe")
    if not tap_uri or not null_uri:
        raise SystemExit("probe devices not found in the User Library browser")
    notes = [{"pitch": PITCHES[b % 2], "start_time": float(b), "duration": 0.5,
              "velocity": 100} for b in range(32)]
    idx = {}
    for name, shift in (("SFT_A", 0.0), ("SFT_A2", 0.0), ("SFT_LAG", LAG_BEATS)):
        idx[name] = new_track(c, "midi", name, inst)
        c.send("create_arrangement_clip", {"track_index": idx[name], "start_time": 0.0,
                                           "length": 32.0})
        c.send("add_notes_to_arrangement_clip",
               {"track_index": idx[name], "clip_index": 0,
                "notes": [dict(n, start_time=n["start_time"] + shift) for n in notes]})
    idx["SFT_SUB"] = new_track(c, "midi", "SFT_SUB", inst)
    idx["SFT_TAP"] = new_track(c, "audio", "SFT_TAP", tap_uri, settle=2.0)
    idx["SFT_NULL"] = new_track(c, "audio", "SFT_NULL", null_uri, settle=2.0)
    log("scene: %s" % idx)
    return idx


def teardown(c):
    for i in range(count(c) - 1, -1, -1):
        if c.send("get_track_info", {"track_index": i}).get("name") in NAMES:
            c.send("delete_track", {"track_index": i}); time.sleep(0.3)
    log("teardown done; track count %d" % count(c))


def sniff(seconds):
    """[(a, b, diff)] RMS samples the Null Probe emitted during the window."""
    return [tuple(v[:3]) for addr, v in probe_device_midi_io.sniff(seconds, OSC_PORT)
            if addr == "/nullprobe" and len(v) >= 3]


def measure(c, idx, label, a, b):
    """Point the null probe's A/B inputs at tracks a/b, play from the top, report."""
    for io, src in ((1, a), (2, b)):
        c.send("set_device_audio_input", {"track_index": idx["SFT_NULL"], "device_index": 0,
                                          "io_index": io, "source_index": idx[src]})
    c.send("set_current_position", {"position": 0.0})
    c.send("start_playback")
    time.sleep(0.5)
    la, lb, ratio = residual(sniff(SECONDS))
    c.send("stop_playback")
    hz = sum(note_hz(p) for p in PITCHES) / len(PITCHES)
    lag = delay_ms(ratio, hz) if lb > 0.2 * la else float("nan")
    log("%-7s %s vs %s: level A %.4f  B %.4f  residual %.4f (%.1f dB)  lag ~%.2f ms"
        % (label, a, b, la, lb, ratio,
           20 * math.log10(ratio) if ratio > 0 else -120.0, lag))
    return {"label": label, "level_a": la, "level_b": lb, "ratio": ratio, "lag_ms": lag}


def main():
    with LiveClient(timeout=40) as c:
        idx = setup(c)
        try:
            tap = {"track_index": idx["SFT_TAP"], "device_index": 0}
            r = c.send("set_device_midi_io", dict(tap, io_index=0, source_index=idx["SFT_A"],
                                                  channel="Post FX"))
            log("tap input  -> %s" % r)
            r = c.send("set_device_midi_io", dict(tap, io_index=0, direction="out",
                                                  source_index=idx["SFT_SUB"],
                                                  channel="Track In"))
            log("tap output -> %s" % r)

            tempo = float(c.send("get_session_info").get("tempo", 120.0))
            log("known-lag control: SFT_LAG is %.2f ms late" % (LAG_BEATS * 60000.0 / tempo))
            results = [measure(c, idx, "same", "SFT_A", "SFT_A"),
                       measure(c, idx, "native", "SFT_A", "SFT_A2"),
                       measure(c, idx, "lagged", "SFT_A", "SFT_LAG")]
            for label, state in (("auto", MONITOR_AUTO), ("in", MONITOR_IN)):
                c.send("set_track_monitor", {"track_index": idx["SFT_SUB"], "state": state})
                results.append(measure(c, idx, label, "SFT_A", "SFT_SUB"))
        finally:
            c.send("stop_playback")
            teardown(c)

        heard = [r for r in results if r["label"] in ("auto", "in")
                 and r["level_b"] > 0.2 * r["level_a"]]
        if not heard:
            log("VERDICT: forwarded MIDI never sounded on the sub track")
            return 1
        best = min(heard, key=lambda r: r["ratio"])
        log("VERDICT: sub sounds with monitor=%s; residual %.4f, lag ~%.2f ms "
            "(native baseline residual %.4f)"
            % (best["label"], best["ratio"], best["lag_ms"], results[1]["ratio"]))
        return 0


if __name__ == "__main__":
    sys.exit(main())
