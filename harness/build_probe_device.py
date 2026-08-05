"""
build_probe_device.py — a MINIMAL multi-input M4L device for the aggregator routing
probe. Declares 8 audio input channels (plugin~ 1..8 = 4 stereo pairs) so Live exposes
4 input pairs as OUTPUT-ROUTING CHANNELS on other tracks. Measures per-pair RMS and
sends it over OSC to :9885 so the routing test can confirm each pair receives the
RIGHT source independently (no summing / cross-talk).

This is throwaway scaffolding to validate the ONE make-or-break question before
committing to the real multichannel aggregator: can output_routing_channel enumerate +
select an individual plugin~ input pair via the Remote Script, and does signal arrive
on the pair we selected?

Reuses the proven base patcher's metadata; replaces its boxes/lines with the minimal
probe graph. Run: python build_probe_device.py
"""

import json
from pathlib import Path

import device_ui

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
OUT = HERE / "Mix Analysis Probe.maxpat"
NPAIRS = 4
OSC_PORT = 9885


def box(id_, text, x, y, ins, outs, outtypes):
    return {"box": {"id": id_, "maxclass": "newobj", "numinlets": ins,
                    "numoutlets": outs, "outlettype": list(outtypes),
                    "patching_rect": [float(x), float(y), 130.0, 22.0], "text": text}}


def line(src, so, dst, di):
    return {"patchline": {"source": [src, so], "destination": [dst, di]}}


def main():
    d = json.loads(BASE.read_text())
    p = d["patcher"]
    boxes, lines = [], []

    # 8 audio-input taps (plugin~ N = channel N; declaring up to 8 => 4 input pairs)
    for ch in range(1, 2 * NPAIRS + 1):
        boxes.append(box("p%d" % ch, "plugin~ %d" % ch, 40, 40 + ch * 26, 0, 1, ["signal"]))

    # per pair: sum L+R -> running RMS -> snapshot -> pak inlet
    pak = "pak " + " ".join(["0."] * NPAIRS)
    boxes.append(box("obj-pak", pak, 500, 300, NPAIRS, 1, [""]))
    boxes.append(box("obj-prep", "prepend /probe/pairs", 500, 332, 1, 1, [""]))
    boxes.append(box("obj-udp", "udpsend 127.0.0.1 %d" % OSC_PORT, 500, 364, 1, 0, []))
    lines.append(line("obj-pak", 0, "obj-prep", 0))
    lines.append(line("obj-prep", 0, "obj-udp", 0))

    for k in range(NPAIRS):
        lo, hi = 2 * k + 1, 2 * k + 2
        s, a, sn = "sum%d" % k, "avg%d" % k, "snap%d" % k
        boxes.append(box(s, "+~", 250, 60 + k * 40, 2, 1, ["signal"]))
        boxes.append(box(a, "average~ 1024 @mode rms", 320, 60 + k * 40, 1, 1, ["signal"]))
        boxes.append(box(sn, "snapshot~ 100", 480, 60 + k * 40, 1, 1, [""]))
        lines.append(line("p%d" % lo, 0, s, 0))
        lines.append(line("p%d" % hi, 0, s, 1))
        lines.append(line(s, 0, a, 0))
        lines.append(line(a, 0, sn, 0))
        lines.append(line(sn, 0, "obj-pak", k))

    # valid audio effect: pass pair 1 straight through
    boxes.append(box("obj-out", "plugout~ 1 2", 40, 40 + (2 * NPAIRS + 2) * 26, 2, 0, []))
    lines.append(line("p1", 0, "obj-out", 0))
    lines.append(line("p2", 0, "obj-out", 1))

    # title / comment
    boxes.append({"box": {"id": "obj-title", "maxclass": "comment",
                          "patching_rect": [40.0, 20.0, 400.0, 20.0],
                          "text": "MIX ANALYSIS PROBE - 4 input pairs -> per-pair RMS OSC :%d" % OSC_PORT}})

    # presentation meter: the 4 pair RMS values, from the same pak the OSC uses
    boxes.append(device_ui.plabel("ui-lbl", "PROBE pairs 1-4", 4.0, 2.0, 120.0,
                                  12.0, x=500, y=400))
    boxes.append(device_ui.mslider("ui-ms", NPAIRS, 4.0, 16.0, 120.0, 144.0,
                                   x=500, y=420))
    lines.append(line("obj-pak", 0, "ui-ms", 0))
    device_ui.enable_presentation(p)

    p["boxes"], p["lines"] = boxes, lines
    OUT.write_text(json.dumps(d, indent=1))
    json.loads(OUT.read_text())   # validate round-trip
    print("wrote %s: %d boxes, %d lines (%d input pairs, OSC :%d)"
          % (OUT.name, len(boxes), len(lines), NPAIRS, OSC_PORT))


if __name__ == "__main__":
    main()
