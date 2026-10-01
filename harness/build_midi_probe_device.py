"""
build_midi_probe_device.py — a MINIMAL M4L audio effect for the Sub Follower gate
probe: can ONE device pull MIDI from SEVERAL tracks through the Live 11+ DeviceIO
routing API (device.midi_inputs), the way the aggregator pulls audio through
device.audio_inputs?

Cycling '74 documents one routable MIDI input + one routable MIDI output per audio
effect. Our audio probe beat its documented ceiling (32 IOs vs 16), so this declares
N [midiin] objects and lets probe_device_midi_io.py count what Live really exposes.

Each [midiin] -> [midiparse] note list -> /midiprobe/in/<k> pitch velocity on OSC
:9888, so the probe can see WHICH input a routed source arrives on. [midiin] 1 is
also forwarded to [midiout] to test the routable MIDI output (device -> sub track).

Throwaway scaffolding, like build_probe_device.py. Run: python build_midi_probe_device.py
"""

import json
from pathlib import Path

import device_ui
from build_probe_device import box, line

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
OUT = HERE / "MIDI IO Probe.maxpat"
N_INPUTS = 4
OSC_PORT = 9888


def main():
    d = json.loads(BASE.read_text())
    p = d["patcher"]
    boxes, lines = [], []

    boxes.append(box("obj-udp", "udpsend 127.0.0.1 %d" % OSC_PORT, 500, 300, 1, 0, []))
    for k in range(1, N_INPUTS + 1):
        y = 40 + k * 60
        mi, mp, pre = "min%d" % k, "mparse%d" % k, "mpre%d" % k
        boxes.append(box(mi, "midiin", 40, y, 1, 1, ["int"]))
        boxes.append(box(mp, "midiparse", 200, y, 1, 8, [""] * 8))
        boxes.append(box(pre, "prepend /midiprobe/in/%d" % k, 360, y, 1, 1, [""]))
        lines.append(line(mi, 0, mp, 0))
        lines.append(line(mp, 0, pre, 0))       # outlet 0 = note list (pitch velocity)
        lines.append(line(pre, 0, "obj-udp", 0))

    # routable MIDI output: forward input 1 unchanged
    boxes.append(box("obj-midiout", "midiout", 40, 40 + (N_INPUTS + 1) * 60, 1, 0, []))
    lines.append(line("min1", 0, "obj-midiout", 0))

    # valid audio effect: pass the track's audio straight through
    boxes.append(box("obj-in", "plugin~", 700, 60, 2, 2, ["signal", "signal"]))
    boxes.append(box("obj-out", "plugout~", 700, 120, 2, 2, ["signal", "signal"]))
    lines.append(line("obj-in", 0, "obj-out", 0))
    lines.append(line("obj-in", 1, "obj-out", 1))

    boxes.append(device_ui.plabel("ui-lbl", "MIDI IO PROBE", 4.0, 2.0, 120.0, 12.0,
                                  x=500, y=400))
    device_ui.enable_presentation(p)

    p["boxes"], p["lines"] = boxes, lines
    OUT.write_text(json.dumps(d, indent=1))
    json.loads(OUT.read_text())   # validate round-trip
    print("wrote %s: %d boxes, %d lines (%d midiin, OSC :%d)"
          % (OUT.name, len(boxes), len(lines), N_INPUTS, OSC_PORT))


if __name__ == "__main__":
    main()
