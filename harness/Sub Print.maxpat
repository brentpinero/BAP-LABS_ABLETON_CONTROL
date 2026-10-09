{
 "patcher": {
  "fileversion": 1,
  "appversion": {
   "major": 8,
   "minor": 6,
   "revision": 0,
   "architecture": "x64",
   "modernui": 1
  },
  "classnamespace": "box",
  "rect": [
   50.0,
   50.0,
   1400.0,
   900.0
  ],
  "gridsize": [
   15.0,
   15.0
  ],
  "boxes": [
   {
    "box": {
     "id": "obj-midiin",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      20.0,
      130.0,
      22.0
     ],
     "text": "midiin"
    }
   },
   {
    "box": {
     "id": "obj-midiout",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 0,
     "outlettype": [],
     "patching_rect": [
      40.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "midiout"
    }
   },
   {
    "box": {
     "id": "obj-thisdev",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "outlettype": [
      "bang",
      "int",
      "int"
     ],
     "patching_rect": [
      300.0,
      20.0,
      130.0,
      22.0
     ],
     "text": "live.thisdevice"
    }
   },
   {
    "box": {
     "id": "obj-defer",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "deferlow"
    }
   },
   {
    "box": {
     "id": "obj-js",
     "maxclass": "v8.codebox",
     "filename": "none",
     "code": "inlets = 1;\r\noutlets = 2;                      // 0: unused, 1: status text\r\nvar CLIP_NAME = \"Sub <- Bass\", EPS = 1e-6;\r\nvar foldMode = 1, floor = 28;\r\nvar NAMES = [\"C\", \"C#\", \"D\", \"D#\", \"E\", \"F\", \"F#\", \"G\", \"G#\", \"A\", \"A#\", \"B\"];\r\n\r\nfunction status(s) { outlet(1, s); post(\"[Sub Print] \" + s + \"\\n\"); }\r\nfunction foldmode(v) { foldMode = Number(v); }\r\nfunction floorval(v) { floor = Number(v); }\r\nfunction noteName(p) { return NAMES[((p % 12) + 12) % 12] + (Math.floor(p / 12) - 2); }\r\nfunction fold(p) { return floor + (((p - floor) % 12) + 12) % 12; }\r\nfunction num(api, prop) { return Number(api.get(prop)); }\r\n\r\nfunction bang() { status(\"ready: map a key to Print (Cmd+K)\"); }\r\n\r\nfunction ownTrack() {\r\n    var m = String(new LiveAPI(null, \"this_device\").unquotedpath)\r\n        .match(/^(live_set tracks (\\d+))/);\r\n    return m ? { path: m[1], index: parseInt(m[2], 10) } : null;\r\n}\r\nfunction parentIndex(trackPath) {                  // group track index or -1\r\n    var g = new LiveAPI(null, trackPath).get(\"group_track\");\r\n    if (!(g && g.length >= 2 && String(g[0]) === \"id\" && Number(g[1]) > 0)) return -1;\r\n    var m = String(new LiveAPI(null, \"id \" + g[1]).unquotedpath).match(/tracks (\\d+)/);\r\n    return m ? Number(m[1]) : -1;\r\n}\r\nfunction bassTracks(me) {                           // MIDI tracks inside the Bass group\r\n    var n = new LiveAPI(null, \"live_set\").getcount(\"tracks\"), group = -1, i;\r\n    for (i = 0; i < n && group < 0; i++) {\r\n        var t = new LiveAPI(null, \"live_set tracks \" + i);\r\n        if (Number(t.get(\"is_foldable\")) === 1 && /bass/i.test(String(t.get(\"name\")))) group = i;\r\n    }\r\n    if (group < 0) return null;\r\n    var out = [];\r\n    for (i = 0; i < n; i++) {\r\n        if (i === me.index) continue;\r\n        var t2 = new LiveAPI(null, \"live_set tracks \" + i);\r\n        if (Number(t2.get(\"has_midi_input\")) !== 1 || Number(t2.get(\"is_foldable\")) === 1) continue;\r\n        var p = i, inside = false, guard = 0;\r\n        while (p >= 0 && guard++ < 16) { p = parentIndex(\"live_set tracks \" + p); if (p === group) inside = true; }\r\n        if (inside) out.push(i);\r\n    }\r\n    return { group: group, tracks: out };\r\n}\r\n\r\n// Every note of a track's arrangement clips in absolute song beats, loops unrolled.\r\nfunction trackNotes(ti, notes, regions) {\r\n    var tp = \"live_set tracks \" + ti, nc = new LiveAPI(null, tp).getcount(\"arrangement_clips\");\r\n    for (var c = 0; c < nc; c++) {\r\n        var clip = new LiveAPI(null, tp + \" arrangement_clips \" + c);\r\n        if (num(clip, \"is_midi_clip\") !== 1 || num(clip, \"muted\") === 1) continue;\r\n        var start = num(clip, \"start_time\"), end = num(clip, \"end_time\");\r\n        var marker = num(clip, \"start_marker\"), looping = num(clip, \"looping\") === 1;\r\n        var ls = num(clip, \"loop_start\"), le = num(clip, \"loop_end\");\r\n        var all = JSON.parse(String(clip.call(\"get_all_notes_extended\"))).notes || [];\r\n        regions.push([start, end]);\r\n        // playback segments: [from, to) in clip time, starting at song time `at`\r\n        var segs = [], at = start;\r\n        if (looping) {\r\n            var from = marker;\r\n            while (at < end - EPS) {\r\n                var to = Math.min(le, from + (end - at));\r\n                if (to <= from + EPS) { from = ls; if (le - ls <= EPS) break; continue; }\r\n                segs.push({ from: from, to: to, at: at });\r\n                at += to - from; from = ls;\r\n                if (le - ls <= EPS) break;\r\n            }\r\n        } else segs.push({ from: marker, to: marker + (end - start), at: start });\r\n        all.forEach(function (n) {\r\n            if (n.mute) return;\r\n            segs.forEach(function (s) {\r\n                if (n.start_time >= s.from - EPS && n.start_time < s.to - EPS) {\r\n                    var abs = s.at + (n.start_time - s.from);\r\n                    notes.push({ pitch: n.pitch, start: abs, velocity: n.velocity,\r\n                                 duration: Math.min(n.duration, s.to - n.start_time, end - abs) });\r\n                }\r\n            });\r\n        });\r\n    }\r\n}\r\n\r\nfunction monoLine(notes) {                           // lowest sounding note wins\r\n    notes = notes.filter(function (n) { return n.duration > EPS; })\r\n                 .sort(function (a, b) { return a.start - b.start; });\r\n    var times = {};\r\n    notes.forEach(function (n) { times[n.start] = 1; times[n.start + n.duration] = 1; });\r\n    var ts = Object.keys(times).map(Number).sort(function (a, b) { return a - b; });\r\n    var line = [], held = [], nxt = 0;\r\n    for (var i = 0; i + 1 < ts.length; i++) {\r\n        var t0 = ts[i], t1 = ts[i + 1];\r\n        if (t1 - t0 <= EPS) continue;\r\n        while (nxt < notes.length && notes[nxt].start <= t0 + EPS) {\r\n            held.push({ pitch: notes[nxt].pitch, end: notes[nxt].start + notes[nxt].duration }); nxt++;\r\n        }\r\n        held = held.filter(function (h) { return h.end >= t1 - EPS; });\r\n        if (!held.length) continue;\r\n        var low = Math.min.apply(null, held.map(function (h) { return h.pitch; }));\r\n        var last = line[line.length - 1];\r\n        if (last && last.pitch === low && Math.abs(last.start + last.duration - t0) <= EPS) {\r\n            last.duration = t1 - last.start;\r\n        } else line.push({ pitch: low, start: t0, duration: t1 - t0, velocity: 100 });\r\n    }\r\n    return line;\r\n}\r\n\r\nfunction mergeRegions(regions) {\r\n    regions.sort(function (a, b) { return a[0] - b[0]; });\r\n    var out = [];\r\n    regions.forEach(function (r) {\r\n        var last = out[out.length - 1];\r\n        if (last && r[0] <= last[1] + EPS) last[1] = Math.max(last[1], r[1]);\r\n        else out.push([r[0], r[1]]);\r\n    });\r\n    return out;\r\n}\r\n\r\nfunction print() {\r\n    try {\r\n        var me = ownTrack();\r\n        if (!me) { status(\"put Sub Print on your sub MIDI track\"); return; }\r\n        var src = bassTracks(me);\r\n        if (!src) { status(\"no group track with 'bass' in its name\"); return; }\r\n        var notes = [], regions = [];\r\n        src.tracks.forEach(function (ti) { trackNotes(ti, notes, regions); });\r\n        if (!notes.length) { status(\"no notes in the Bass group's arrangement clips\"); return; }\r\n        if (foldMode) {\r\n            notes = monoLine(notes).map(function (n) {\r\n                return { pitch: fold(n.pitch), start: n.start, duration: n.duration, velocity: 100 };\r\n            });\r\n        }\r\n        // replace what we printed last time, nothing else\r\n        var track = new LiveAPI(null, me.path), old = [];\r\n        for (var c = 0; c < track.getcount(\"arrangement_clips\"); c++) {\r\n            var cl = new LiveAPI(null, me.path + \" arrangement_clips \" + c);\r\n            if (String(cl.get(\"name\")) === CLIP_NAME) old.push(cl.id);\r\n        }\r\n        old.forEach(function (id) { track.call(\"delete_clip\", \"id\", id); });\r\n\r\n        var made = 0;\r\n        mergeRegions(regions).forEach(function (r) {\r\n            var start = r[0], len = r[1] - r[0];\r\n            track.call(\"create_midi_clip\", start, len);\r\n            var clip = null, n = track.getcount(\"arrangement_clips\");\r\n            for (var k = 0; k < n && !clip; k++) {\r\n                var cand = new LiveAPI(null, me.path + \" arrangement_clips \" + k);\r\n                if (Math.abs(num(cand, \"start_time\") - start) < 1e-3 &&\r\n                    String(cand.get(\"name\")) !== CLIP_NAME) clip = cand;\r\n            }\r\n            if (!clip) return;\r\n            clip.set(\"name\", CLIP_NAME);\r\n            var inside = notes.filter(function (n) { return n.start >= start - EPS && n.start < r[1] - EPS; })\r\n                .map(function (n) {\r\n                    return { pitch: n.pitch, start_time: Math.max(0, n.start - start),\r\n                             duration: Math.min(n.duration, r[1] - n.start), velocity: n.velocity };\r\n                });\r\n            if (inside.length) clip.call(\"add_new_notes\", { notes: inside });\r\n            made++;\r\n        });\r\n        status(\"printed \" + notes.length + \" notes from \" + src.tracks.length + \" track(s) into \"\r\n               + made + \" clip(s)\" + (foldMode ? \", mono, floor \" + noteName(floor) : \"\"));\r\n    } catch (e) { status(\"error: \" + e); }\r\n}",
     "fontface": 0,
     "fontname": "Menlo",
     "fontsize": 11.0,
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "patching_rect": [
      300.0,
      100.0,
      420.0,
      240.0
     ],
     "saved_object_attributes": {
      "parameter_enable": 0
     }
    }
   },
   {
    "box": {
     "id": "obj-setstat",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      740.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "prepend set"
    }
   },
   {
    "box": {
     "id": "ui-status",
     "maxclass": "message",
     "text": "...",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      740.0,
      140.0,
      230.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      148.0,
      230.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-print",
     "maxclass": "live.text",
     "mode": 0,
     "text": "Print",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "patching_rect": [
      740.0,
      200.0,
      80.0,
      40.0
     ],
     "parameter_enable": 1,
     "varname": "Print",
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_type": 2,
       "parameter_mmax": 1,
       "parameter_enum": [
        "val1",
        "val2"
       ],
       "parameter_longname": "Print",
       "parameter_shortname": "Print"
      }
     },
     "presentation": 1,
     "presentation_rect": [
      8.0,
      24.0,
      80.0,
      40.0
     ]
    }
   },
   {
    "box": {
     "id": "msg-print",
     "maxclass": "message",
     "text": "print",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      740.0,
      250.0,
      60.0,
      22.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-fold",
     "maxclass": "live.toggle",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      900.0,
      200.0,
      18.0,
      18.0
     ],
     "parameter_enable": 1,
     "varname": "Mono + fold",
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_type": 2,
       "parameter_mmax": 1,
       "parameter_enum": [
        "off",
        "on"
       ],
       "parameter_initial": [
        1
       ],
       "parameter_initial_enable": 1,
       "parameter_longname": "Mono + fold",
       "parameter_shortname": "Mono + fold"
      }
     },
     "presentation": 1,
     "presentation_rect": [
      100.0,
      24.0,
      18.0,
      18.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-foldmsg",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      900.0,
      240.0,
      130.0,
      22.0
     ],
     "text": "prepend foldmode"
    }
   },
   {
    "box": {
     "id": "obj-floor",
     "maxclass": "live.numbox",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      "float"
     ],
     "patching_rect": [
      900.0,
      300.0,
      44.0,
      16.0
     ],
     "parameter_enable": 1,
     "varname": "Floor",
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_type": 1,
       "parameter_unitstyle": 8,
       "parameter_mmin": 12.0,
       "parameter_mmax": 47.0,
       "parameter_initial": [
        28
       ],
       "parameter_initial_enable": 1,
       "parameter_longname": "Floor",
       "parameter_shortname": "Floor"
      }
     },
     "presentation": 1,
     "presentation_rect": [
      100.0,
      48.0,
      44.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-floormsg",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      900.0,
      340.0,
      130.0,
      22.0
     ],
     "text": "prepend floorval"
    }
   },
   {
    "box": {
     "id": "ui-title",
     "maxclass": "comment",
     "fontsize": 9.0,
     "text": "SUB PRINT",
     "patching_rect": [
      740.0,
      400.0,
      96.0,
      14.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      2.0,
      96.0,
      14.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-fold",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Mono + fold",
     "patching_rect": [
      740.0,
      430.0,
      80.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      122.0,
      26.0,
      80.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-floor",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Floor",
     "patching_rect": [
      740.0,
      460.0,
      40.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      148.0,
      50.0,
      40.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-hint",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Bass group -> this track",
     "patching_rect": [
      740.0,
      490.0,
      160.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      8.0,
      70.0,
      160.0,
      16.0
     ]
    }
   }
  ],
  "lines": [
   {
    "patchline": {
     "source": [
      "obj-midiin",
      0
     ],
     "destination": [
      "obj-midiout",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-thisdev",
      0
     ],
     "destination": [
      "obj-defer",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-defer",
      0
     ],
     "destination": [
      "obj-js",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-js",
      1
     ],
     "destination": [
      "obj-setstat",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-setstat",
      0
     ],
     "destination": [
      "ui-status",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-print",
      0
     ],
     "destination": [
      "msg-print",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "msg-print",
      0
     ],
     "destination": [
      "obj-js",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-fold",
      0
     ],
     "destination": [
      "obj-foldmsg",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-foldmsg",
      0
     ],
     "destination": [
      "obj-js",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-floor",
      0
     ],
     "destination": [
      "obj-floormsg",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-floormsg",
      0
     ],
     "destination": [
      "obj-js",
      0
     ]
    }
   }
  ],
  "openinpresentation": 1
 }
}