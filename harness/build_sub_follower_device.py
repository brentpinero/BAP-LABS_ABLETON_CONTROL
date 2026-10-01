"""
build_sub_follower_device.py — generate the two Sub Follower devices.

The Sub Follower makes one sub track (Serum) play a mono, octave-folded line derived
from every MIDI track in the bass group. Live gives an M4L audio effect exactly ONE
routable MIDI input and output (gate probe: probe_device_midi_io.py), so the system is
a TAP STACK, measured sample-accurate by probe_follow_timing.py:

  hub track (audio):  one  Sub Follow Tap  per bass track
      [midiin <- bass track, Post FX] -> Follow gate -> this track's LOWEST held note
      -> sent as note number <Slot>, real pitch carried in the velocity -> sub track
  sub track:          Sub Follower (MIDI effect) -> Serum
      per-slot held pitches -> LOWEST across slots -> fold into one octave -> mono note

Why slots: Live merges every tap's notes on the sub track's input, and two sources
holding the SAME pitch become one note that the first note-off ends. Giving each tap
its own note number keeps sources distinct through that merge (and allows 128 taps).
The sub track must not play its own clips into the follower: it reads note numbers
as slots.

The taps must NOT sit on the sub track itself: a track feeding its own input is a
feedback route and Live delays it by an audio buffer.

Both note paths are plain Max objects. No js/v8: those run on Max's low-priority
thread and would smear note timing. Auto octave and routing live in the harness
(sub_follower_provision.py), which sets Slot and Floor.

Run: python build_sub_follower_device.py     (then wrap with maxpat_to_amxd.py)
"""

import json
from pathlib import Path

import device_ui
import sub_follower_core as sf
from build_probe_device import box, line

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
TAP_OUT = HERE / "Sub Follow Tap.maxpat"
FOLLOWER_OUT = HERE / "Sub Follower.maxpat"
NONE = 999          # "nothing held" sentinel for the follower's running minimum

# Lowest held pitch+1 ($i1, NONE = nothing held) -> real pitch, or -1.
DECODE_EXPR = "expr ($i1 >= %d) * -1 + ($i1 < %d) * ($i1 - 1)" % (NONE, NONE)
# Fold pitch $i1 (-1 = nothing) into the octave above floor $i2. Comma-free on
# purpose (commas need escaping inside a Max object box).
FOLD_EXPR = "expr ($i1 < 0) * -1 + ($i1 >= 0) * ($i2 + (($i1 - $i2) % 12 + 12) % 12)"


def message(id_, text, x, y):
    return {"box": {"id": id_, "maxclass": "message", "text": text, "numinlets": 2,
                    "numoutlets": 1, "outlettype": [""],
                    "patching_rect": [float(x), float(y), 50.0, 22.0]}}


def build_tap():
    """Audio effect on the hub track: reduce one bass track to its lowest held note and
    send it to the sub track as note <Slot> with velocity = pitch + 1."""
    boxes, lines = [], []
    B, L = boxes.append, lines.append

    B(box("obj-in", "plugin~", 700, 40, 2, 2, ["signal", "signal"]))
    B(box("obj-out", "plugout~", 700, 100, 2, 2, ["signal", "signal"]))
    L(line("obj-in", 0, "obj-out", 0))
    L(line("obj-in", 1, "obj-out", 1))

    # 1. this track's notes -> held table (pitch -> velocity, 0 = released)
    B(box("obj-midiin", "midiin", 40, 20, 1, 1, ["int"]))
    B(box("obj-parse", "midiparse", 40, 60, 1, 8, [""] * 8))
    B(box("obj-gate", "gate 1 1", 40, 100, 2, 1, [""]))
    B(box("obj-ntrig", "t b l", 40, 140, 1, 2, ["bang", ""]))
    B(box("obj-held", "table ---tapheld", 140, 180, 2, 2, ["int", "bang"]))
    L(line("obj-midiin", 0, "obj-parse", 0))
    L(line("obj-parse", 0, "obj-gate", 1))
    L(line("obj-gate", 0, "obj-ntrig", 0))
    L(line("obj-ntrig", 1, "obj-held", 0))          # list "pitch velocity" stores

    # 2. LOWEST held pitch: scan 0..127, stop at the first held one
    B(box("obj-scan", "t b b -1", 40, 220, 1, 3, ["bang", "bang", "int"]))
    B(box("obj-uzi", "uzi 128 0", 140, 260, 2, 3, ["bang", "bang", "int"]))
    B(box("obj-itrig", "t i i", 240, 300, 1, 2, ["int", "int"]))
    B(box("obj-heldread", "table ---tapheld", 340, 340, 2, 2, ["int", "bang"]))
    B(box("obj-isheld", "> 0", 340, 380, 2, 1, ["int"]))
    B(box("obj-hitgate", "gate 1", 240, 420, 2, 1, [""]))
    B(box("obj-hit", "t b i", 240, 460, 1, 2, ["bang", "int"]))
    B(message("obj-break", "break", 240, 500))
    B(box("obj-lowest", "int -1", 40, 540, 2, 1, ["int"]))
    L(line("obj-ntrig", 0, "obj-scan", 0))
    L(line("obj-scan", 2, "obj-lowest", 1))         # assume nothing held (-1)
    L(line("obj-scan", 1, "obj-uzi", 0))            # scan (runs to completion here)
    L(line("obj-scan", 0, "obj-lowest", 0))         # then output the result
    L(line("obj-uzi", 2, "obj-itrig", 0))
    L(line("obj-itrig", 1, "obj-heldread", 0))
    L(line("obj-heldread", 0, "obj-isheld", 0))
    L(line("obj-isheld", 0, "obj-hitgate", 0))
    L(line("obj-itrig", 0, "obj-hitgate", 1))
    L(line("obj-hitgate", 0, "obj-hit", 0))
    L(line("obj-hit", 1, "obj-lowest", 1))
    L(line("obj-hit", 0, "obj-break", 0))
    L(line("obj-break", 0, "obj-uzi", 0))

    # 3. when the lowest note changes: slot note OFF, then ON with velocity = pitch + 1
    B(box("obj-change", "change -1", 40, 580, 1, 3, ["", "int", "int"]))
    B(box("obj-emit", "t i b", 40, 620, 1, 2, ["int", "bang"]))
    B(box("obj-slotoff", "int 0", 240, 660, 2, 1, ["int"]))
    B(box("obj-packoff", "pack 0 0", 240, 700, 2, 1, [""]))
    B(box("obj-ison", "sel -1", 40, 660, 2, 2, ["bang", ""]))
    B(box("obj-plus1", "+ 1", 40, 700, 2, 1, ["int"]))
    B(box("obj-cap", "minimum 127", 40, 740, 2, 2, ["int", "int"]))
    B(box("obj-ontrig", "t b i", 40, 780, 1, 2, ["bang", "int"]))
    B(box("obj-sloton", "int 0", 40, 820, 2, 1, ["int"]))
    B(box("obj-packon", "pack 0 0", 40, 860, 2, 1, [""]))
    B(box("obj-format", "midiformat", 40, 900, 7, 1, ["int"]))
    B(box("obj-midiout", "midiout", 40, 940, 1, 0, []))
    L(line("obj-lowest", 0, "obj-change", 0))
    L(line("obj-change", 0, "obj-emit", 0))
    L(line("obj-emit", 1, "obj-slotoff", 0))        # first: release the slot note
    L(line("obj-slotoff", 0, "obj-packoff", 0))
    L(line("obj-packoff", 0, "obj-format", 0))
    L(line("obj-emit", 0, "obj-ison", 0))           # then: new lowest pitch, if any
    L(line("obj-ison", 1, "obj-plus1", 0))
    L(line("obj-plus1", 0, "obj-cap", 0))
    L(line("obj-cap", 0, "obj-ontrig", 0))
    L(line("obj-ontrig", 1, "obj-packon", 1))
    L(line("obj-ontrig", 0, "obj-sloton", 0))
    L(line("obj-sloton", 0, "obj-packon", 0))
    L(line("obj-packon", 0, "obj-format", 0))
    L(line("obj-format", 0, "obj-midiout", 0))

    # 4. controls. Follow off: close the gate, forget held notes, release the slot.
    B(device_ui.ptoggle("obj-follow", "Follow", 8.0, 24.0, x=500, y=20))
    B(box("obj-ftrig", "t i i", 500, 60, 1, 2, ["int", "int"]))
    B(box("obj-foff", "sel 0", 500, 100, 2, 2, ["bang", ""]))
    B(box("obj-ctrig", "t b b", 500, 140, 1, 2, ["bang", "bang"]))
    B(message("obj-clear", "clear", 500, 180))
    B(device_ui.pintbox("obj-slot", "Slot", 0, 127, 0, 8.0, 64.0, x=500, y=660))
    L(line("obj-follow", 0, "obj-ftrig", 0))
    L(line("obj-ftrig", 1, "obj-gate", 0))
    L(line("obj-ftrig", 0, "obj-foff", 0))
    L(line("obj-foff", 0, "obj-ctrig", 0))
    L(line("obj-ctrig", 1, "obj-clear", 0))
    L(line("obj-clear", 0, "obj-held", 0))
    L(line("obj-ctrig", 0, "obj-scan", 0))
    L(line("obj-slot", 0, "obj-slotoff", 1))
    L(line("obj-slot", 0, "obj-sloton", 1))

    B(device_ui.plabel("ui-title", "SUB FOLLOW TAP", 4.0, 2.0, 96.0, 14.0, fontsize=9.0,
                       x=700, y=300))
    B(device_ui.plabel("ui-follow", "Follow", 30.0, 26.0, 60.0, x=700, y=330))
    B(device_ui.plabel("ui-slot", "Slot", 56.0, 64.0, 40.0, x=700, y=360))
    return boxes, lines


def build_follower():
    """MIDI effect on the sub track: slot notes from the taps -> one folded mono line."""
    boxes, lines = [], []
    B, L = boxes.append, lines.append

    # 1. slot notes in: table[slot] = pitch + 1 while that tap holds a note, else 0
    B(box("obj-midiin", "midiin", 40, 20, 1, 1, ["int"]))
    B(box("obj-parse", "midiparse", 40, 60, 1, 8, [""] * 8))
    B(box("obj-ntrig", "t b l", 40, 100, 1, 2, ["bang", ""]))
    B(box("obj-held", "table ---sfheld", 140, 140, 2, 2, ["int", "bang"]))
    L(line("obj-midiin", 0, "obj-parse", 0))
    L(line("obj-parse", 0, "obj-ntrig", 0))
    L(line("obj-ntrig", 1, "obj-held", 0))          # list "slot velocity" stores

    # 2. LOWEST pitch across slots: running minimum of every non-zero entry
    B(box("obj-scan", "t b b %d" % NONE, 40, 180, 1, 3, ["bang", "bang", "int"]))
    B(box("obj-uzi", "uzi 128 0", 140, 220, 2, 3, ["bang", "bang", "int"]))
    B(box("obj-heldread", "table ---sfheld", 240, 260, 2, 2, ["int", "bang"]))
    B(box("obj-nonzero", "split 1 128", 240, 300, 3, 2, ["int", "int"]))
    B(box("obj-min", "minimum %d" % NONE, 240, 340, 2, 2, ["int", "int"]))
    B(box("obj-best", "int %d" % NONE, 40, 380, 2, 1, ["int"]))
    B(box("obj-decode", DECODE_EXPR, 40, 420, 1, 1, [""]))
    L(line("obj-ntrig", 0, "obj-scan", 0))
    L(line("obj-scan", 2, "obj-best", 1))           # start from "nothing held"
    L(line("obj-scan", 2, "obj-min", 1))
    L(line("obj-scan", 1, "obj-uzi", 0))            # scan (runs to completion here)
    L(line("obj-scan", 0, "obj-best", 0))           # then output the minimum
    L(line("obj-uzi", 2, "obj-heldread", 0))
    L(line("obj-heldread", 0, "obj-nonzero", 0))
    L(line("obj-nonzero", 0, "obj-min", 0))
    L(line("obj-min", 0, "obj-best", 1))            # carry the running minimum
    L(line("obj-min", 0, "obj-min", 1))
    L(line("obj-best", 0, "obj-decode", 0))

    # 3. fold into the octave above Floor; act only when the folded pitch changes
    B(box("obj-fold", FOLD_EXPR, 40, 460, 2, 1, [""]))
    B(box("obj-change", "change -1", 40, 500, 1, 3, ["", "int", "int"]))
    B(box("obj-emit", "t i i", 40, 540, 1, 2, ["int", "int"]))
    L(line("obj-decode", 0, "obj-fold", 0))
    L(line("obj-fold", 0, "obj-change", 0))
    L(line("obj-change", 0, "obj-emit", 0))

    # 4. new note ON first, then the previous note OFF (legato order for the synth)
    B(box("obj-ison", "sel -1", 260, 580, 2, 2, ["bang", ""]))
    B(box("obj-packon", "pack 0 100", 260, 620, 2, 1, [""]))
    B(box("obj-prevtrig", "t i b", 40, 580, 1, 2, ["int", "bang"]))
    B(box("obj-prev", "int -1", 40, 620, 2, 1, ["int"]))
    B(box("obj-wason", "sel -1", 40, 660, 2, 2, ["bang", ""]))
    B(box("obj-packoff", "pack 0 0", 40, 700, 2, 1, [""]))
    B(box("obj-format", "midiformat", 40, 740, 7, 1, ["int"]))
    B(box("obj-midiout", "midiout", 40, 780, 1, 0, []))
    L(line("obj-emit", 1, "obj-ison", 0))
    L(line("obj-ison", 1, "obj-packon", 0))
    L(line("obj-packon", 0, "obj-format", 0))
    L(line("obj-emit", 0, "obj-prevtrig", 0))
    L(line("obj-prevtrig", 1, "obj-prev", 0))       # emit the previous pitch...
    L(line("obj-prevtrig", 0, "obj-prev", 1))       # ...then remember the new one
    L(line("obj-prev", 0, "obj-wason", 0))
    L(line("obj-wason", 1, "obj-packoff", 0))
    L(line("obj-packoff", 0, "obj-format", 0))
    L(line("obj-format", 0, "obj-midiout", 0))

    # 5. controls: Floor refolds the sounding note; Reset forgets every held slot
    B(device_ui.pintbox("obj-floor", "Floor", 12, 47, sf.BAND_LO, 8.0, 40.0,
                        x=420, y=420, note=True))
    B(box("obj-fltrig", "t b i", 420, 460, 1, 2, ["bang", "int"]))
    B(device_ui.pbutton("obj-reset", "Reset", "Reset", 8.0, 84.0, x=560, y=100))
    B(box("obj-rtrig", "t b b", 560, 140, 1, 2, ["bang", "bang"]))
    B(message("obj-clear", "clear", 560, 180))
    L(line("obj-floor", 0, "obj-fltrig", 0))
    L(line("obj-fltrig", 1, "obj-fold", 1))
    L(line("obj-fltrig", 0, "obj-scan", 0))
    L(line("obj-reset", 0, "obj-rtrig", 0))
    L(line("obj-rtrig", 1, "obj-clear", 0))
    L(line("obj-clear", 0, "obj-held", 0))
    L(line("obj-rtrig", 0, "obj-scan", 0))

    B(device_ui.plabel("ui-title", "SUB FOLLOWER", 4.0, 2.0, 96.0, 14.0, fontsize=9.0,
                       x=560, y=300))
    B(device_ui.plabel("ui-floor", "Floor (lowest note)", 4.0, 24.0, 96.0, x=560, y=330))
    B(device_ui.plabel("ui-reset", "Clear held notes", 4.0, 68.0, 96.0, x=560, y=360))
    return boxes, lines


def write(out, boxes, lines):
    d = json.loads(BASE.read_text())
    d["patcher"]["boxes"], d["patcher"]["lines"] = boxes, lines
    device_ui.enable_presentation(d["patcher"])
    out.write_text(json.dumps(d, indent=1))
    json.loads(out.read_text())   # validate round-trip
    print("wrote %s: %d boxes, %d lines" % (out.name, len(boxes), len(lines)))


def main():
    write(TAP_OUT, *build_tap())
    write(FOLLOWER_OUT, *build_follower())


if __name__ == "__main__":
    main()
