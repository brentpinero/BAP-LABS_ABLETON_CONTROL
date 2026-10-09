"""
build_sub_print_device.py — generate "BAP Labs Sub Print": a MIDI effect for the sub track.
Press Print (or the key you map to it with Live's Cmd+K) and every MIDI note from the
tracks in the Bass group is copied into clips on this track, as plain editable clips named
"Sub <- Bass". Re-printing replaces only those clips; anything else on the track stays.
Optional "Mono + fold": keep the lowest sounding note and fold it into the octave above
Floor (same rule as the Sub Follower).

Nothing real-time, no routing, nothing on the bass tracks. The work is done by an embedded
v8 script through Live's API (read notes with get_all_notes_extended, write with
create_midi_clip / add_new_notes). Arrangement view only.

Run: python build_sub_print_device.py     (then wrap with maxpat_to_amxd.py)
"""

import json
from pathlib import Path

import device_ui
import sub_follower_core as sf
from build_probe_device import box, line
from build_sub_follower_device import message

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
OUT = HERE / "Sub Print.maxpat"
CLIP_NAME = "Sub <- Bass"

JS = r"""
inlets = 1;
outlets = 2;                      // 0: unused, 1: status text
var CLIP_NAME = "%(clip)s", EPS = 1e-6;
var foldMode = 0, floor = %(band_lo)d;
var NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

function status(s) { outlet(1, s); post("[Sub Print] " + s + "\n"); }
function foldmode(v) { foldMode = Number(v); }
function floorval(v) { floor = Number(v); }
function noteName(p) { return NAMES[((p %% 12) + 12) %% 12] + (Math.floor(p / 12) - 2); }
function fold(p) { return floor + (((p - floor) %% 12) + 12) %% 12; }
function num(api, prop) { return Number(api.get(prop)); }

function bang() { status("ready: map a key to Print (Cmd+K)"); }

function ownTrack() {
    var m = String(new LiveAPI(null, "this_device").unquotedpath)
        .match(/^(live_set tracks (\d+))/);
    return m ? { path: m[1], index: parseInt(m[2], 10) } : null;
}
function parentIndex(trackPath) {                  // group track index or -1
    var g = new LiveAPI(null, trackPath).get("group_track");
    if (!(g && g.length >= 2 && String(g[0]) === "id" && Number(g[1]) > 0)) return -1;
    var m = String(new LiveAPI(null, "id " + g[1]).unquotedpath).match(/tracks (\d+)/);
    return m ? Number(m[1]) : -1;
}
function bassTracks(me) {                           // MIDI tracks inside the Bass group
    var n = new LiveAPI(null, "live_set").getcount("tracks"), group = -1, i;
    for (i = 0; i < n && group < 0; i++) {
        var t = new LiveAPI(null, "live_set tracks " + i);
        if (Number(t.get("is_foldable")) === 1 && /bass/i.test(String(t.get("name")))) group = i;
    }
    if (group < 0) return null;
    var out = [];
    for (i = 0; i < n; i++) {
        if (i === me.index) continue;
        var t2 = new LiveAPI(null, "live_set tracks " + i);
        if (Number(t2.get("has_midi_input")) !== 1 || Number(t2.get("is_foldable")) === 1) continue;
        var p = i, inside = false, guard = 0;
        while (p >= 0 && guard++ < 16) { p = parentIndex("live_set tracks " + p); if (p === group) inside = true; }
        if (inside) out.push(i);
    }
    return { group: group, tracks: out };
}

// Every note of a track's arrangement clips in absolute song beats, loops unrolled.
function trackNotes(ti, notes, regions) {
    var tp = "live_set tracks " + ti, nc = new LiveAPI(null, tp).getcount("arrangement_clips");
    for (var c = 0; c < nc; c++) {
        var clip = new LiveAPI(null, tp + " arrangement_clips " + c);
        if (num(clip, "is_midi_clip") !== 1 || num(clip, "muted") === 1) continue;
        var start = num(clip, "start_time"), end = num(clip, "end_time");
        var marker = num(clip, "start_marker"), looping = num(clip, "looping") === 1;
        var ls = num(clip, "loop_start"), le = num(clip, "loop_end");
        var all = JSON.parse(String(clip.call("get_all_notes_extended"))).notes || [];
        regions.push([start, end]);
        // playback segments: [from, to) in clip time, starting at song time `at`
        var segs = [], at = start;
        if (looping) {
            var from = marker;
            while (at < end - EPS) {
                var to = Math.min(le, from + (end - at));
                if (to <= from + EPS) { from = ls; if (le - ls <= EPS) break; continue; }
                segs.push({ from: from, to: to, at: at });
                at += to - from; from = ls;
                if (le - ls <= EPS) break;
            }
        } else segs.push({ from: marker, to: marker + (end - start), at: start });
        all.forEach(function (n) {
            if (n.mute) return;
            segs.forEach(function (s) {
                if (n.start_time >= s.from - EPS && n.start_time < s.to - EPS) {
                    var abs = s.at + (n.start_time - s.from);
                    notes.push({ pitch: n.pitch, start: abs, velocity: n.velocity,
                                 duration: Math.min(n.duration, s.to - n.start_time, end - abs) });
                }
            });
        });
    }
}

function monoLine(notes) {                           // lowest sounding note wins
    notes = notes.filter(function (n) { return n.duration > EPS; })
                 .sort(function (a, b) { return a.start - b.start; });
    var times = {};
    notes.forEach(function (n) { times[n.start] = 1; times[n.start + n.duration] = 1; });
    var ts = Object.keys(times).map(Number).sort(function (a, b) { return a - b; });
    var line = [], held = [], nxt = 0;
    for (var i = 0; i + 1 < ts.length; i++) {
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
        } else line.push({ pitch: low, start: t0, duration: t1 - t0, velocity: 100 });
    }
    return line;
}

function mergeRegions(regions) {
    regions.sort(function (a, b) { return a[0] - b[0]; });
    var out = [];
    regions.forEach(function (r) {
        var last = out[out.length - 1];
        if (last && r[0] <= last[1] + EPS) last[1] = Math.max(last[1], r[1]);
        else out.push([r[0], r[1]]);
    });
    return out;
}

function print() {
    try {
        var me = ownTrack();
        if (!me) { status("put Sub Print on your sub MIDI track"); return; }
        var src = bassTracks(me);
        if (!src) { status("no group track with 'bass' in its name"); return; }
        var notes = [], regions = [];
        src.tracks.forEach(function (ti) { trackNotes(ti, notes, regions); });
        if (!notes.length) { status("no notes in the Bass group's arrangement clips"); return; }
        if (foldMode) {
            notes = monoLine(notes).map(function (n) {
                return { pitch: fold(n.pitch), start: n.start, duration: n.duration, velocity: 100 };
            });
        }
        // replace what we printed last time, nothing else
        var track = new LiveAPI(null, me.path), old = [];
        for (var c = 0; c < track.getcount("arrangement_clips"); c++) {
            var cl = new LiveAPI(null, me.path + " arrangement_clips " + c);
            if (String(cl.get("name")) === CLIP_NAME) old.push(cl.id);
        }
        old.forEach(function (id) { track.call("delete_clip", "id", id); });

        var made = 0;
        mergeRegions(regions).forEach(function (r) {
            var start = r[0], len = r[1] - r[0];
            track.call("create_midi_clip", start, len);
            var clip = null, n = track.getcount("arrangement_clips");
            for (var k = 0; k < n && !clip; k++) {
                var cand = new LiveAPI(null, me.path + " arrangement_clips " + k);
                if (Math.abs(num(cand, "start_time") - start) < 1e-3 &&
                    String(cand.get("name")) !== CLIP_NAME) clip = cand;
            }
            if (!clip) return;
            clip.set("name", CLIP_NAME);
            var inside = notes.filter(function (n) { return n.start >= start - EPS && n.start < r[1] - EPS; })
                .map(function (n) {
                    return { pitch: n.pitch, start_time: Math.max(0, n.start - start),
                             duration: Math.min(n.duration, r[1] - n.start), velocity: n.velocity };
                });
            if (inside.length) clip.call("add_new_notes", { notes: inside });
            made++;
        });
        status("printed " + notes.length + " notes from " + src.tracks.length + " track(s) into "
               + made + " clip(s)" + (foldMode ? ", mono, floor " + noteName(floor) : ""));
    } catch (e) { status("error: " + e); }
}
""" % {"clip": CLIP_NAME, "band_lo": sf.BAND_LO}


def build():
    boxes, lines = [], []
    B, L = boxes.append, lines.append
    B(box("obj-midiin", "midiin", 40, 20, 1, 1, ["int"]))         # the sub's own MIDI passes
    B(box("obj-midiout", "midiout", 40, 60, 1, 0, []))
    L(line("obj-midiin", 0, "obj-midiout", 0))

    B(box("obj-thisdev", "live.thisdevice", 300, 20, 1, 3, ["bang", "int", "int"]))
    B(box("obj-defer", "deferlow", 300, 60, 1, 1, [""]))
    B(device_ui.codebox("obj-js", JS, 300, 100, inlets=1, outlets=2))
    B(box("obj-setstat", "prepend set", 740, 100, 1, 1, [""]))
    B(device_ui.pstatus("ui-status", "...", 4.0, 148.0, 230.0, x=740, y=140))
    L(line("obj-thisdev", 0, "obj-defer", 0))
    L(line("obj-defer", 0, "obj-js", 0))
    L(line("obj-js", 1, "obj-setstat", 0))
    L(line("obj-setstat", 0, "ui-status", 0))

    # Print: a visible (key- and MIDI-mappable) button
    b = device_ui.pbutton("obj-print", "Print", "Print", 8.0, 24.0, pw=80.0, ph=40.0, x=740, y=200)
    del b["box"]["saved_attribute_attributes"]["valueof"]["parameter_invisible"]
    B(b)
    B(message("msg-print", "print", 740, 250))
    L(line("obj-print", 0, "msg-print", 0))
    L(line("msg-print", 0, "obj-js", 0))

    B(device_ui.ptoggle("obj-fold", "Mono + fold", 100.0, 24.0, initial=0, x=900, y=200))
    B(box("obj-foldmsg", "prepend foldmode", 900, 240, 1, 1, [""]))
    L(line("obj-fold", 0, "obj-foldmsg", 0))
    L(line("obj-foldmsg", 0, "obj-js", 0))
    B(device_ui.pintbox("obj-floor", "Floor", 12, 47, sf.BAND_LO, 100.0, 48.0, x=900, y=300,
                        note=True))
    B(box("obj-floormsg", "prepend floorval", 900, 340, 1, 1, [""]))
    L(line("obj-floor", 0, "obj-floormsg", 0))
    L(line("obj-floormsg", 0, "obj-js", 0))

    B(device_ui.plabel("ui-title", "SUB PRINT", 4.0, 2.0, 96.0, 14.0, fontsize=9.0, x=740, y=400))
    B(device_ui.plabel("ui-fold", "Mono + fold", 122.0, 26.0, 80.0, x=740, y=430))
    B(device_ui.plabel("ui-floor", "Floor", 148.0, 50.0, 40.0, x=740, y=460))
    B(device_ui.plabel("ui-hint", "Bass group -> this track", 8.0, 70.0, 160.0, x=740, y=490))
    return boxes, lines


def main():
    d = json.loads(BASE.read_text())
    d["patcher"]["boxes"], d["patcher"]["lines"] = build()
    device_ui.enable_presentation(d["patcher"])
    OUT.write_text(json.dumps(d, indent=1))
    json.loads(OUT.read_text())
    print("wrote %s: %d boxes, %d lines"
          % (OUT.name, len(d["patcher"]["boxes"]), len(d["patcher"]["lines"])))


if __name__ == "__main__":
    main()
