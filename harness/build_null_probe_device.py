"""
build_null_probe_device.py — a MINIMAL M4L audio effect for the Sub Follower TIMING
gate: is MIDI forwarded through a device's routable MIDI output in time with its source?

It pulls two tracks' audio through DeviceIO (plugin~ 3 = A, plugin~ 5 = B) and reports
RMS of A, of B, and of A - B on OSC :9889 as /nullprobe a b diff. When A (a source
track) and B (the track fed by the forwarded MIDI) play the same patch on the same
notes, a sample-accurate follow nulls: diff ~ 0. Any lag leaves a residual that
probe_follow_timing.py converts to milliseconds.

Throwaway scaffolding, like build_probe_device.py. Run: python build_null_probe_device.py
"""

import json
from pathlib import Path

import device_ui
from build_probe_device import box, line

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
OUT = HERE / "Null Probe.maxpat"
OSC_PORT = 9889


def main():
    d = json.loads(BASE.read_text())
    p = d["patcher"]
    boxes, lines = [], []

    # declaring plugin~ 1..6 exposes two extra input pairs (3/4 = A, 5/6 = B)
    for ch in range(1, 7):
        boxes.append(box("p%d" % ch, "plugin~ %d" % ch, 40, 40 + ch * 26, 0, 1, ["signal"]))
    boxes.append(box("obj-diff", "-~", 250, 120, 2, 1, ["signal"]))
    lines.append(line("p3", 0, "obj-diff", 0))
    lines.append(line("p5", 0, "obj-diff", 1))

    boxes.append(box("obj-pak", "pak 0. 0. 0.", 500, 300, 3, 1, [""]))
    boxes.append(box("obj-prep", "prepend /nullprobe", 500, 332, 1, 1, [""]))
    boxes.append(box("obj-udp", "udpsend 127.0.0.1 %d" % OSC_PORT, 500, 364, 1, 0, []))
    lines.append(line("obj-pak", 0, "obj-prep", 0))
    lines.append(line("obj-prep", 0, "obj-udp", 0))

    for k, src in enumerate(("p3", "p5", "obj-diff")):       # a, b, a - b
        a, sn = "avg%d" % k, "snap%d" % k
        boxes.append(box(a, "average~ 2048 @mode rms", 320, 60 + k * 40, 1, 1, ["signal"]))
        boxes.append(box(sn, "snapshot~ 50", 480, 60 + k * 40, 1, 1, [""]))
        lines.append(line(src, 0, a, 0))
        lines.append(line(a, 0, sn, 0))
        lines.append(line(sn, 0, "obj-pak", k))

    # valid audio effect: pass the track's own audio straight through
    boxes.append(box("obj-out", "plugout~ 1 2", 40, 260, 2, 0, []))
    lines.append(line("p1", 0, "obj-out", 0))
    lines.append(line("p2", 0, "obj-out", 1))

    boxes.append(device_ui.plabel("ui-lbl", "NULL PROBE  A - B", 4.0, 2.0, 120.0, 12.0,
                                  x=500, y=400))
    device_ui.enable_presentation(p)

    p["boxes"], p["lines"] = boxes, lines
    OUT.write_text(json.dumps(d, indent=1))
    json.loads(OUT.read_text())   # validate round-trip
    print("wrote %s: %d boxes, %d lines (OSC :%d)" % (OUT.name, len(boxes), len(lines), OSC_PORT))


if __name__ == "__main__":
    main()
