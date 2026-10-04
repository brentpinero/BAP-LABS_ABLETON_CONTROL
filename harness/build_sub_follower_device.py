"""
build_sub_follower_device.py — generate the two Sub Follower devices (v2: drag-in, no code).

One sub track (Serum) follows the MIDI of every bass track live, folded into one octave,
mono (lowest note wins), with an automatable Follow switch per bass track. The sub track
itself is untouched and keeps playing its own clips.

  bass track:   instrument -> [Sub Send]  pulls its OWN track's notes (Pre FX), keeps the
                lowest held one, and sends it as a control change (CC <Slot>, value =
                pitch + 1, 0 = released) to the Sub Follow track
  Sub Follow:   a MIDI track with no instrument, monitor In: [Sub Follower] turns the CCs
                into one folded mono note line; the TRACK's output goes straight to the
                sub track's instrument (bypassing monitoring, so the sub keeps its clips)
  sub track:    nothing added

Why this shape (all measured in Live 12.4.6 with null tests, see probe_follow_timing.py):
  * an M4L audio effect has exactly one routable MIDI input/output, so one Send per track
  * notes delivered to a track's input need monitor In (own clips suppressed) or arming;
    delivery to the INSTRUMENT channel of the track does not
  * Live merges same-pitch notes from several sources; CC transport never collides
  * everything above is sample-accurate when the note path is plain Max objects

Both devices configure their own routing from an embedded v8.codebox (LiveAPI) when they
load and when tracks change. v8 runs on the low-priority thread, so it touches routing and
parameters only, never notes.

Run: python build_sub_follower_device.py     (then wrap with maxpat_to_amxd.py)
"""

import json
from pathlib import Path

import device_ui
import sub_follower_core as sf
from build_probe_device import box, line

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
SEND_OUT = HERE / "Sub Send.maxpat"
FOLLOWER_OUT = HERE / "Sub Follower.maxpat"
NONE = 999                  # "nothing held" sentinel for the follower's running minimum
MAX_SLOT = 120              # CC numbers 0..119 (120-127 are channel-mode messages)
SEND_NAME = "Sub Send"      # device names the scripts look for
FOLLOWER_NAME = "Sub Follower"

# Lowest held pitch+1 ($i1, NONE = nothing held) -> real pitch, or -1.
DECODE_EXPR = "expr ($i1 >= %d) * -1 + ($i1 < %d) * ($i1 - 1)" % (NONE, NONE)
# Fold pitch $i1 (-1 = nothing) into the octave above floor $i2. Comma-free on purpose
# (commas need escaping inside a Max object box).
FOLD_EXPR = "expr ($i1 < 0) * -1 + ($i1 >= 0) * ($i2 + (($i1 - $i2) % 12 + 12) % 12)"

# ---------------------------------------------------------------------------------------
# Embedded JavaScript (v8). Shared helpers + one bang() per device. Kept ES5-ish and small.
# ---------------------------------------------------------------------------------------
COMMON_JS = r"""
inlets = 1;
outlets = 2;                      // 0: value for a parameter, 1: status text
var tracksObserver = null, pending = null;

function status(s) { outlet(1, s); post("[%(tag)s] " + s + "\n"); }
function jsonProp(api, prop) { return JSON.parse(String(api.get(prop)))[prop]; }
function ownTrack() {
    var m = String(new LiveAPI(null, "this_device").unquotedpath)
        .match(/^(live_set tracks (\d+))/);
    return m ? { path: m[1], index: parseInt(m[2], 10) } : null;
}
// The routing entry (from a device's available list) that IS the track at trackPath: a
// track is never offered to itself, so among same-named entries it is the one whose
// identifier the track's own chooser (availProp) does not list.
function trackEntry(trackPath, candidates, availProp) {
    var track = new LiveAPI(null, trackPath);
    var name = String(track.get("name")), theirs = {};
    jsonProp(track, availProp).forEach(function (t) { theirs[t.identifier] = 1; });
    var named = candidates.filter(function (c) { return c.display_name === name; });
    for (var i = 0; i < named.length; i++) if (!theirs[named[i].identifier]) return named[i];
    return named[0] || null;
}
function setChannel(api, availProp, prop, wanted) {
    var chans = jsonProp(api, availProp);
    for (var i = 0; i < chans.length; i++) {
        if (chans[i].display_name === wanted) { api.set(prop, chans[i]); return true; }
    }
    return false;
}
function eachDevice(fn) {          // fn(trackIndex, devicePath, deviceName)
    var n = new LiveAPI(null, "live_set").getcount("tracks");
    for (var i = 0; i < n; i++) {
        var tp = "live_set tracks " + i, nd = new LiveAPI(null, tp).getcount("devices");
        for (var d = 0; d < nd; d++) {
            var dp = tp + " devices " + d;
            fn(i, dp, String(new LiveAPI(null, dp).get("name")));
        }
    }
}
function schedule() {              // never change the set from inside a notification
    if (pending) pending.cancel();
    pending = new Task(function () { pending = null; configure(); });
    pending.schedule(600);
}
function watch() {                 // re-run configure() when tracks are added/removed/moved
    if (tracksObserver) return;
    tracksObserver = new LiveAPI(schedule, "live_set");
    tracksObserver.property = "tracks";
}
function bang() { configure(); watch(); }
function rescan() { configure(); }
"""

SEND_JS = COMMON_JS % {"tag": SEND_NAME} + r"""
outlets = 3;                      // 2: "first setup done" flag (stored with the device)
var setupDone = 0;
function setupdone(v) { setupDone = v; }

// A Max for Live device cannot load another Max for Live device (Live's API inserts native
// devices only), so the Send cannot add the Sub Follower itself. On a FRESH drop it makes
// the empty "Sub Follow" track ready; the user drops Sub Follower on it once.
function ensureFollowTrack() {
    var song = new LiveAPI(null, "live_set"), n = song.getcount("tracks");
    for (var i = 0; i < n; i++) {
        if (String(new LiveAPI(null, "live_set tracks " + i).get("name")) === "Sub Follow") return;
    }
    song.call("create_midi_track", -1);
    var t = new LiveAPI(null, "live_set tracks " + n);
    t.set("name", "Sub Follow");
    t.set("arm", 0);
}

function configure() {
    try {
        var me = ownTrack();
        if (!me) { status("put Sub Send on a bass track"); return; }
        var inp = new LiveAPI(null, "this_device midi_inputs 0");
        var own = trackEntry(me.path, jsonProp(inp, "available_routing_types"),
                             "available_input_routing_types");
        if (!own) { status("this track is not routable"); return; }
        inp.set("routing_type", own);
        setChannel(inp, "available_routing_channels", "routing_channel", "Pre FX");
        outlet(0, me.index %% %(max_slot)d);                 // Slot = CC number
        var fol = null;
        eachDevice(function (i, dp, name) {
            if (!fol && name.indexOf("%(follower)s") !== -1) fol = "live_set tracks " + i;
        });
        if (!fol) {
            if (!setupDone) { ensureFollowTrack(); outlet(2, 1); }
            status("drop Sub Follower on the 'Sub Follow' track");
            return;
        }
        outlet(2, 1);
        var out = new LiveAPI(null, "this_device midi_outputs 0");
        var dest = trackEntry(fol, jsonProp(out, "available_routing_types"),
                              "available_output_routing_types");
        if (!dest) { status("Sub Follower track not routable"); return; }
        out.set("routing_type", dest);
        setChannel(out, "available_routing_channels", "routing_channel", "Track In");
        status("-> " + dest.display_name + "  (slot " + (me.index %% %(max_slot)d) + ")");
    } catch (e) { status("error: " + e); }
}
""" % {"max_slot": MAX_SLOT, "follower": FOLLOWER_NAME}

FOLLOWER_JS = COMMON_JS % {"tag": FOLLOWER_NAME} + r"""
var BAND_LO = %(band_lo)d, BAND_HI = %(band_hi)d, FLOOR_MIN = %(floor_min)d, FLOOR_MAX = %(floor_max)d;
var W_RANGE = %(w_range)s, W_JUMP = %(w_jump)s, EPS = 1e-6;
var NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
var outObserver = null;

function noteName(p) { return NAMES[((p %% 12) + 12) %% 12] + (Math.floor(p / 12) - 2); }
function noteHz(p) { return 440 * Math.pow(2, (p - 69) / 12); }
function fold(p, floor) { return floor + (((p - floor) %% 12) + 12) %% 12; }

function sendTracks() {                     // tracks carrying a Sub Send, by index
    var out = [];
    eachDevice(function (i, dp, name) {
        if (name.indexOf("%(send)s") !== -1 && out.indexOf(i) === -1) out.push(i);
    });
    return out;
}

function configure() {
    try {
        var me = ownTrack();
        if (!me) { status("drop Sub Follower on an empty MIDI track"); return; }
        var track = new LiveAPI(null, me.path);
        track.set("arm", 0);
        track.set("current_monitoring_state", 0);           // In: hear the Sends
        if (/^\d+-MIDI$/.test(String(track.get("name")))) track.set("name", "Sub Follow");
        if (!outObserver) {                 // finish setup when the user picks MIDI To
            outObserver = new LiveAPI(schedule, me.path);
            outObserver.property = "output_routing_type";
        }

        // Point every Sub Send at this track (independent of which sub is chosen).
        var count = 0;
        eachDevice(function (i, dp, name) {
            if (name.indexOf("%(send)s") === -1) return;
            var out = new LiveAPI(null, dp + " midi_outputs 0");
            var dest = trackEntry(me.path, jsonProp(out, "available_routing_types"),
                                  "available_output_routing_types");
            if (!dest) return;
            out.set("routing_type", dest);
            setChannel(out, "available_routing_channels", "routing_channel", "Track In");
            count++;
        });

        // Sub track = this track's own MIDI To chooser. Default: first MIDI track with
        // an instrument whose name contains "sub"; the user can change it in Live's I/O.
        var cur = jsonProp(track, "output_routing_type");
        var types = jsonProp(track, "available_output_routing_types");
        var isTrack = function (entry) {
            var n = new LiveAPI(null, "live_set").getcount("tracks");
            for (var i = 0; i < n; i++) {
                var t = new LiveAPI(null, "live_set tracks " + i);
                if (i !== me.index && String(t.get("name")) === entry.display_name &&
                    Number(t.get("has_midi_input")) === 1 && t.getcount("devices") > 0) return true;
            }
            return false;
        };
        if (!isTrack(cur)) {
            var pick = null;
            for (var i = 0; i < types.length && !pick; i++) {
                if (/sub/i.test(types[i].display_name) && isTrack(types[i])) pick = types[i];
            }
            if (!pick) {
                status(count + " Send(s) ready: set this track's MIDI To = your sub track");
                return;
            }
            track.set("output_routing_type", pick);
            cur = pick;
        }
        // Deliver to the INSTRUMENT (bypasses monitoring, so the sub keeps its own clips).
        // Multi-channel plug-ins list one entry per MIDI channel ("1-Serum 2" .. "16-..."):
        // take the first, and leave it alone if the user already chose an instrument entry.
        var chan = jsonProp(track, "output_routing_channel");
        if (chan.display_name === "Track In") {
            var chans = jsonProp(track, "available_output_routing_channels"), inst = null;
            for (var c = 0; c < chans.length && !inst; c++) {
                if (chans[c].display_name !== "Track In") inst = chans[c];
            }
            if (!inst) { status(cur.display_name + " has no instrument to receive notes"); return; }
            track.set("output_routing_channel", inst);
            chan = inst;
        }
        status("following " + count + " track(s) -> " + cur.display_name + " / " + chan.display_name);
    } catch (e) { status("error: " + e); }
}

// ---- auto octave: same scoring as sub_follower_core.py (mono line, range + jump cost)
function monoLine(notes) {
    notes = notes.filter(function (n) { return n.duration > EPS; })
                 .sort(function (a, b) { return a.start - b.start; });
    var times = {}, i;
    notes.forEach(function (n) { times[n.start] = 1; times[n.start + n.duration] = 1; });
    var ts = Object.keys(times).map(Number).sort(function (a, b) { return a - b; });
    var line = [], held = [], nxt = 0;
    for (i = 0; i + 1 < ts.length; i++) {
        var t0 = ts[i], t1 = ts[i + 1];
        if (t1 - t0 <= EPS) continue;
        while (nxt < notes.length && notes[nxt].start <= t0 + EPS) {
            held.push({ pitch: notes[nxt].pitch, end: notes[nxt].start + notes[nxt].duration }); nxt++;
        }
        held = held.filter(function (h) { return h.end >= t1 - EPS; });
        if (!held.length) continue;
        var low = Math.min.apply(null, held.map(function (h) { return h.pitch; }));
        var last = line[line.length - 1];
        if (last && last.pitch === low && Math.abs(last.start + last.duration - t0) <= EPS) {
            last.duration = t1 - last.start;
        } else line.push({ pitch: low, start: t0, duration: t1 - t0 });
    }
    return line;
}
function scoreFloor(line, floor) {
    var total = 0, outside = 0, moves = 0, jumps = 0, prev = null;
    line.forEach(function (seg) {
        var p = fold(seg.pitch, floor);
        total += seg.duration;
        outside += Math.max(BAND_LO - p, p - BAND_HI, 0) * seg.duration;
        if (prev !== null && p !== prev) { moves++; if (Math.abs(p - prev) > 6) jumps++; }
        prev = p;
    });
    var rc = total > 0 ? outside / total : 0, jc = moves ? jumps / moves : 0;
    return { floor: floor, cost: W_RANGE * rc + W_JUMP * jc };
}
function chooseFloor(notes) {
    var line = monoLine(notes), best = null;
    for (var f = FLOOR_MIN; f <= FLOOR_MAX; f++) {
        var s = scoreFloor(line, f);
        if (!best || s.cost < best.cost - EPS ||
            (Math.abs(s.cost - best.cost) <= EPS && Math.abs(f - BAND_LO) < Math.abs(best.floor - BAND_LO))) best = s;
    }
    return best.floor;
}
function analyze() {
    try {
        var notes = [];
        sendTracks().forEach(function (i) {
            var t = new LiveAPI(null, "live_set tracks " + i), nc = t.getcount("arrangement_clips");
            for (var c = 0; c < nc; c++) {
                var clip = new LiveAPI(null, "live_set tracks " + i + " arrangement_clips " + c);
                if (Number(clip.get("is_midi_clip")) !== 1) continue;
                var start = Number(clip.get("start_time")), len = Number(clip.get("length"));
                var got = JSON.parse(String(clip.call("get_notes_extended", 0, 128, 0, len)));
                (got.notes || []).forEach(function (n) {
                    if (!n.mute) notes.push({ pitch: n.pitch, start: start + n.start_time, duration: n.duration });
                });
            }
        });
        if (!notes.length) { status("no arrangement notes on the Sub Send tracks"); return; }
        var floor = chooseFloor(notes);
        outlet(0, floor);
        status("Floor " + noteName(floor) + " (" + noteHz(floor).toFixed(1) + " Hz) from " + notes.length + " notes");
    } catch (e) { status("analyze error: " + e); }
}
""" % {"send": SEND_NAME, "band_lo": sf.BAND_LO, "band_hi": sf.BAND_HI,
       "floor_min": sf.FLOOR_MIN, "floor_max": sf.FLOOR_MAX,
       "w_range": sf.W_RANGE, "w_jump": sf.W_JUMP}


def message(id_, text, x, y):
    return {"box": {"id": id_, "maxclass": "message", "text": text, "numinlets": 2,
                    "numoutlets": 1, "outlettype": [""],
                    "patching_rect": [float(x), float(y), 60.0, 22.0]}}


def lowest_held_scan(B, L, table, x=40, y=220):
    """Shared cluster: bang -> scan a held table (pitch -> velocity) ascending and stop at
    the first held pitch -> obj-lowest outputs it (-1 when nothing is held)."""
    B(box("obj-scan", "t b b -1", x, y, 1, 3, ["bang", "bang", "int"]))
    B(box("obj-uzi", "uzi 128 0", x + 100, y + 40, 2, 3, ["bang", "bang", "int"]))
    B(box("obj-itrig", "t i i", x + 200, y + 80, 1, 2, ["int", "int"]))
    B(box("obj-heldread", "table %s" % table, x + 300, y + 120, 2, 2, ["int", "bang"]))
    B(box("obj-isheld", "> 0", x + 300, y + 160, 2, 1, ["int"]))
    B(box("obj-hitgate", "gate 1", x + 200, y + 200, 2, 1, [""]))
    B(box("obj-hit", "t b i", x + 200, y + 240, 1, 2, ["bang", "int"]))
    B(message("obj-break", "break", x + 200, y + 280))
    B(box("obj-lowest", "int -1", x, y + 320, 2, 1, ["int"]))
    L(line("obj-scan", 2, "obj-lowest", 1))          # assume nothing held (-1)
    L(line("obj-scan", 1, "obj-uzi", 0))             # scan (runs to completion here)
    L(line("obj-scan", 0, "obj-lowest", 0))          # then output the result
    L(line("obj-uzi", 2, "obj-itrig", 0))
    L(line("obj-itrig", 1, "obj-heldread", 0))
    L(line("obj-heldread", 0, "obj-isheld", 0))
    L(line("obj-isheld", 0, "obj-hitgate", 0))
    L(line("obj-itrig", 0, "obj-hitgate", 1))
    L(line("obj-hitgate", 0, "obj-hit", 0))
    L(line("obj-hit", 1, "obj-lowest", 1))
    L(line("obj-hit", 0, "obj-break", 0))
    L(line("obj-break", 0, "obj-uzi", 0))


def self_config(B, L, js, x=700, y=300, buttons=(), outlets=2):
    """live.thisdevice -> deferlow -> v8.codebox; outlet 1 -> status line. `buttons`:
    [(box_id, message)] presentation buttons that send a message to the script."""
    B(box("obj-thisdev", "live.thisdevice", x, y, 1, 3, ["bang", "int", "int"]))
    B(box("obj-defer", "deferlow", x, y + 40, 1, 1, [""]))
    B(device_ui.codebox("obj-js", js, x, y + 80, inlets=1, outlets=outlets))
    B(box("obj-setstat", "prepend set", x + 440, y + 80, 1, 1, [""]))
    B(device_ui.pstatus("ui-status", "...", 4.0, 148.0, 230.0, x=x + 440, y=y + 120))
    L(line("obj-thisdev", 0, "obj-defer", 0))
    L(line("obj-defer", 0, "obj-js", 0))
    L(line("obj-js", 1, "obj-setstat", 0))
    L(line("obj-setstat", 0, "ui-status", 0))
    for n, (bid, msg) in enumerate(buttons):
        B(message("msg-" + bid, msg, x + 440, y + 160 + n * 40))
        L(line(bid, 0, "msg-" + bid, 0))
        L(line("msg-" + bid, 0, "obj-js", 0))


def build_send():
    """Audio effect on a bass track: its own notes -> lowest held pitch -> CC <Slot>."""
    boxes, lines = [], []
    B, L = boxes.append, lines.append

    B(box("obj-in", "plugin~", 700, 40, 2, 2, ["signal", "signal"]))
    B(box("obj-out", "plugout~", 700, 100, 2, 2, ["signal", "signal"]))
    L(line("obj-in", 0, "obj-out", 0))
    L(line("obj-in", 1, "obj-out", 1))

    # 1. own-track notes (routed Pre FX by the script) -> held table, gated by Follow
    B(box("obj-midiin", "midiin", 40, 20, 1, 1, ["int"]))
    B(box("obj-parse", "midiparse", 40, 60, 1, 8, [""] * 8))
    B(box("obj-gate", "gate 1 1", 40, 100, 2, 1, [""]))
    B(box("obj-ntrig", "t b l", 40, 140, 1, 2, ["bang", ""]))
    B(box("obj-held", "table ---sendheld", 140, 180, 2, 2, ["int", "bang"]))
    L(line("obj-midiin", 0, "obj-parse", 0))
    L(line("obj-parse", 0, "obj-gate", 1))
    L(line("obj-gate", 0, "obj-ntrig", 0))
    L(line("obj-ntrig", 1, "obj-held", 0))           # list "pitch velocity" stores
    lowest_held_scan(B, L, "---sendheld")
    L(line("obj-ntrig", 0, "obj-scan", 0))

    # 2. lowest pitch -> CC value (pitch + 1, or 0 when nothing is held), only on change
    B(box("obj-change", "change -1", 40, 580, 1, 3, ["", "int", "int"]))
    B(box("obj-plus1", "+ 1", 40, 620, 2, 1, ["int"]))
    B(box("obj-cap", "minimum 127", 40, 660, 2, 2, ["int", "int"]))
    B(box("obj-floor0", "maximum 0", 40, 700, 2, 1, [""]))
    B(box("obj-ctlout", "ctlout", 40, 740, 3, 0, []))
    L(line("obj-lowest", 0, "obj-change", 0))
    L(line("obj-change", 0, "obj-plus1", 0))
    L(line("obj-plus1", 0, "obj-cap", 0))
    L(line("obj-cap", 0, "obj-floor0", 0))
    L(line("obj-floor0", 0, "obj-ctlout", 0))

    # 3. controls. Follow off: close the gate, forget held notes, release (CC 0).
    B(device_ui.ptoggle("obj-follow", "Follow", 8.0, 24.0, x=500, y=20))
    B(box("obj-ftrig", "t i i", 500, 60, 1, 2, ["int", "int"]))
    B(box("obj-foff", "sel 0", 500, 100, 2, 2, ["bang", ""]))
    B(box("obj-ctrig", "t b b", 500, 140, 1, 2, ["bang", "bang"]))
    B(message("obj-clear", "clear", 500, 180))
    B(device_ui.pintbox("obj-slot", "Slot", 0, MAX_SLOT - 1, 0, 8.0, 64.0, x=500, y=660))
    L(line("obj-follow", 0, "obj-ftrig", 0))
    L(line("obj-ftrig", 1, "obj-gate", 0))
    L(line("obj-ftrig", 0, "obj-foff", 0))
    L(line("obj-foff", 0, "obj-ctrig", 0))
    L(line("obj-ctrig", 1, "obj-clear", 0))
    L(line("obj-clear", 0, "obj-held", 0))
    L(line("obj-ctrig", 0, "obj-scan", 0))
    L(line("obj-slot", 0, "obj-ctlout", 1))           # CC number
    self_config(B, L, SEND_JS, buttons=[("obj-rescan", "rescan")], outlets=3)
    B(device_ui.pbutton("obj-rescan", "Rescan", "Rescan", 60.0, 64.0, x=500, y=700))
    L(line("obj-js", 0, "obj-slot", 0))               # script sets Slot = track index

    # "first setup done": stored with the device (not automatable, not shown), so a set
    # that is reloaded never auto-creates another Sub Follow track.
    setup = device_ui.ptoggle("obj-setup", "Setup Done", 0.0, 0.0, initial=0, x=1140, y=520)
    setup["box"]["saved_attribute_attributes"]["valueof"]["parameter_invisible"] = 1
    del setup["box"]["presentation"], setup["box"]["presentation_rect"]
    B(setup)
    B(box("obj-setupmsg", "prepend setupdone", 1140, 560, 1, 1, [""]))
    L(line("obj-js", 2, "obj-setup", 0))
    L(line("obj-setup", 0, "obj-setupmsg", 0))
    L(line("obj-setupmsg", 0, "obj-js", 0))

    B(device_ui.plabel("ui-title", "SUB SEND", 4.0, 2.0, 96.0, 14.0, fontsize=9.0,
                       x=700, y=200))
    B(device_ui.plabel("ui-follow", "Follow this track", 30.0, 26.0, 120.0, x=700, y=230))
    B(device_ui.plabel("ui-slot", "Slot", 56.0, 48.0, 40.0, x=700, y=260))
    return boxes, lines


def build_follower():
    """MIDI effect on its own MIDI track: Sub Send CCs -> one folded mono note line."""
    boxes, lines = [], []
    B, L = boxes.append, lines.append

    # 1. CC in: table[controller] = value (pitch + 1 while that Send holds a note, else 0)
    B(box("obj-midiin", "midiin", 400, 20, 1, 1, ["int"]))      # present, not forwarded
    B(box("obj-ctlin", "ctlin", 40, 20, 1, 3, ["int", "int", "int"]))
    B(box("obj-ctlnum", "int", 140, 60, 2, 1, ["int"]))
    B(box("obj-vtrig", "t b i", 40, 60, 1, 2, ["bang", "int"]))
    B(box("obj-packcv", "pack 0 0", 40, 100, 2, 1, [""]))
    B(box("obj-ntrig", "t b l", 40, 140, 1, 2, ["bang", ""]))
    B(box("obj-held", "table ---sfheld", 140, 180, 2, 2, ["int", "bang"]))
    L(line("obj-ctlin", 1, "obj-ctlnum", 1))          # controller arrives before value
    L(line("obj-ctlin", 0, "obj-vtrig", 0))
    L(line("obj-vtrig", 1, "obj-packcv", 1))
    L(line("obj-vtrig", 0, "obj-ctlnum", 0))
    L(line("obj-ctlnum", 0, "obj-packcv", 0))         # list "controller value"
    L(line("obj-packcv", 0, "obj-ntrig", 0))
    L(line("obj-ntrig", 1, "obj-held", 0))

    # 2. LOWEST pitch across all Sends: running minimum of every non-zero entry
    B(box("obj-scan", "t b b %d" % NONE, 40, 220, 1, 3, ["bang", "bang", "int"]))
    B(box("obj-uzi", "uzi %d 0" % MAX_SLOT, 140, 260, 2, 3, ["bang", "bang", "int"]))
    B(box("obj-heldread", "table ---sfheld", 240, 300, 2, 2, ["int", "bang"]))
    B(box("obj-nonzero", "split 1 128", 240, 340, 3, 2, ["int", "int"]))
    B(box("obj-min", "minimum %d" % NONE, 240, 380, 2, 2, ["int", "int"]))
    B(box("obj-best", "int %d" % NONE, 40, 420, 2, 1, ["int"]))
    B(box("obj-decode", DECODE_EXPR, 40, 460, 1, 1, [""]))
    L(line("obj-ntrig", 0, "obj-scan", 0))
    L(line("obj-scan", 2, "obj-best", 1))             # start from "nothing held"
    L(line("obj-scan", 2, "obj-min", 1))
    L(line("obj-scan", 1, "obj-uzi", 0))
    L(line("obj-scan", 0, "obj-best", 0))
    L(line("obj-uzi", 2, "obj-heldread", 0))
    L(line("obj-heldread", 0, "obj-nonzero", 0))
    L(line("obj-nonzero", 0, "obj-min", 0))
    L(line("obj-min", 0, "obj-best", 1))              # carry the running minimum
    L(line("obj-min", 0, "obj-min", 1))
    L(line("obj-best", 0, "obj-decode", 0))

    # 3. fold into the octave above Floor; act only when the folded pitch changes
    B(box("obj-fold", FOLD_EXPR, 40, 500, 2, 1, [""]))
    B(box("obj-change", "change -1", 40, 540, 1, 3, ["", "int", "int"]))
    B(box("obj-emit", "t i i", 40, 580, 1, 2, ["int", "int"]))
    L(line("obj-decode", 0, "obj-fold", 0))
    L(line("obj-fold", 0, "obj-change", 0))
    L(line("obj-change", 0, "obj-emit", 0))

    # 4. new note ON first, then the previous note OFF (legato order for the synth)
    B(box("obj-ison", "sel -1", 260, 620, 2, 2, ["bang", ""]))
    B(box("obj-packon", "pack 0 100", 260, 660, 2, 1, [""]))
    B(box("obj-prevtrig", "t i b", 40, 620, 1, 2, ["int", "bang"]))
    B(box("obj-prev", "int -1", 40, 660, 2, 1, ["int"]))
    B(box("obj-wason", "sel -1", 40, 700, 2, 2, ["bang", ""]))
    B(box("obj-packoff", "pack 0 0", 40, 740, 2, 1, [""]))
    B(box("obj-format", "midiformat", 40, 780, 7, 1, ["int"]))
    B(box("obj-midiout", "midiout", 40, 820, 1, 0, []))
    L(line("obj-emit", 1, "obj-ison", 0))
    L(line("obj-ison", 1, "obj-packon", 0))
    L(line("obj-packon", 0, "obj-format", 0))
    L(line("obj-emit", 0, "obj-prevtrig", 0))
    L(line("obj-prevtrig", 1, "obj-prev", 0))         # emit the previous pitch...
    L(line("obj-prevtrig", 0, "obj-prev", 1))         # ...then remember the new one
    L(line("obj-prev", 0, "obj-wason", 0))
    L(line("obj-wason", 1, "obj-packoff", 0))
    L(line("obj-packoff", 0, "obj-format", 0))
    L(line("obj-format", 0, "obj-midiout", 0))

    # 5. controls: Floor refolds the sounding note; Reset forgets every held slot;
    #    Analyze picks Floor from the bass notes; Rescan re-routes.
    B(device_ui.pintbox("obj-floor", "Floor", 12, 47, sf.BAND_LO, 8.0, 40.0,
                        x=420, y=460, note=True))
    B(box("obj-fltrig", "t b i", 420, 500, 1, 2, ["bang", "int"]))
    B(device_ui.pbutton("obj-reset", "Reset", "Reset", 8.0, 84.0, x=560, y=100))
    B(box("obj-rtrig", "t b b", 560, 140, 1, 2, ["bang", "bang"]))
    B(message("obj-clear", "clear", 560, 180))
    B(device_ui.pbutton("obj-analyze", "Analyze", "Analyze", 60.0, 40.0, x=560, y=220))
    B(device_ui.pbutton("obj-rescan", "Rescan", "Rescan", 60.0, 84.0, x=560, y=260))
    L(line("obj-floor", 0, "obj-fltrig", 0))
    L(line("obj-fltrig", 1, "obj-fold", 1))
    L(line("obj-fltrig", 0, "obj-scan", 0))
    L(line("obj-reset", 0, "obj-rtrig", 0))
    L(line("obj-rtrig", 1, "obj-clear", 0))
    L(line("obj-clear", 0, "obj-held", 0))
    L(line("obj-rtrig", 0, "obj-scan", 0))
    self_config(B, L, FOLLOWER_JS, buttons=[("obj-analyze", "analyze"),
                                             ("obj-rescan", "rescan")])
    L(line("obj-js", 0, "obj-floor", 0))              # Analyze sets Floor

    B(device_ui.plabel("ui-title", "SUB FOLLOWER", 4.0, 2.0, 120.0, 14.0, fontsize=9.0,
                       x=560, y=300))
    B(device_ui.plabel("ui-floor", "Floor (lowest note)", 4.0, 24.0, 110.0, x=560, y=330))
    B(device_ui.plabel("ui-reset", "Clear held", 4.0, 68.0, 50.0, x=560, y=360))
    B(device_ui.plabel("ui-hint", "MIDI To = your sub track", 110.0, 24.0, 124.0,
                       x=560, y=390))
    return boxes, lines


def write(out, boxes, lines):
    d = json.loads(BASE.read_text())
    d["patcher"]["boxes"], d["patcher"]["lines"] = boxes, lines
    device_ui.enable_presentation(d["patcher"])
    out.write_text(json.dumps(d, indent=1))
    json.loads(out.read_text())   # validate round-trip
    print("wrote %s: %d boxes, %d lines" % (out.name, len(boxes), len(lines)))


def main():
    write(SEND_OUT, *build_send())
    write(FOLLOWER_OUT, *build_follower())


if __name__ == "__main__":
    main()
