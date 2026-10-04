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
      400.0,
      20.0,
      130.0,
      22.0
     ],
     "text": "midiin"
    }
   },
   {
    "box": {
     "id": "obj-ctlin",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "outlettype": [
      "int",
      "int",
      "int"
     ],
     "patching_rect": [
      40.0,
      20.0,
      130.0,
      22.0
     ],
     "text": "ctlin"
    }
   },
   {
    "box": {
     "id": "obj-ctlnum",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      140.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "int"
    }
   },
   {
    "box": {
     "id": "obj-vtrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      "int"
     ],
     "patching_rect": [
      40.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "t b i"
    }
   },
   {
    "box": {
     "id": "obj-packcv",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      40.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "pack 0 0"
    }
   },
   {
    "box": {
     "id": "obj-ntrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      ""
     ],
     "patching_rect": [
      40.0,
      140.0,
      130.0,
      22.0
     ],
     "text": "t b l"
    }
   },
   {
    "box": {
     "id": "obj-held",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "bang"
     ],
     "patching_rect": [
      140.0,
      180.0,
      130.0,
      22.0
     ],
     "text": "table ---sfheld"
    }
   },
   {
    "box": {
     "id": "obj-scan",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "outlettype": [
      "bang",
      "bang",
      "int"
     ],
     "patching_rect": [
      40.0,
      220.0,
      130.0,
      22.0
     ],
     "text": "t b b 999"
    }
   },
   {
    "box": {
     "id": "obj-uzi",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 3,
     "outlettype": [
      "bang",
      "bang",
      "int"
     ],
     "patching_rect": [
      140.0,
      260.0,
      130.0,
      22.0
     ],
     "text": "uzi 120 0"
    }
   },
   {
    "box": {
     "id": "obj-heldread",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "bang"
     ],
     "patching_rect": [
      240.0,
      300.0,
      130.0,
      22.0
     ],
     "text": "table ---sfheld"
    }
   },
   {
    "box": {
     "id": "obj-nonzero",
     "maxclass": "newobj",
     "numinlets": 3,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "int"
     ],
     "patching_rect": [
      240.0,
      340.0,
      130.0,
      22.0
     ],
     "text": "split 1 128"
    }
   },
   {
    "box": {
     "id": "obj-min",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "int"
     ],
     "patching_rect": [
      240.0,
      380.0,
      130.0,
      22.0
     ],
     "text": "minimum 999"
    }
   },
   {
    "box": {
     "id": "obj-best",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      420.0,
      130.0,
      22.0
     ],
     "text": "int 999"
    }
   },
   {
    "box": {
     "id": "obj-decode",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      40.0,
      460.0,
      130.0,
      22.0
     ],
     "text": "expr ($i1 >= 999) * -1 + ($i1 < 999) * ($i1 - 1)"
    }
   },
   {
    "box": {
     "id": "obj-fold",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      40.0,
      500.0,
      130.0,
      22.0
     ],
     "text": "expr ($i1 < 0) * -1 + ($i1 >= 0) * ($i2 + (($i1 - $i2) % 12 + 12) % 12)"
    }
   },
   {
    "box": {
     "id": "obj-change",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "outlettype": [
      "",
      "int",
      "int"
     ],
     "patching_rect": [
      40.0,
      540.0,
      130.0,
      22.0
     ],
     "text": "change -1"
    }
   },
   {
    "box": {
     "id": "obj-emit",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "int"
     ],
     "patching_rect": [
      40.0,
      580.0,
      130.0,
      22.0
     ],
     "text": "t i i"
    }
   },
   {
    "box": {
     "id": "obj-ison",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      ""
     ],
     "patching_rect": [
      260.0,
      620.0,
      130.0,
      22.0
     ],
     "text": "sel -1"
    }
   },
   {
    "box": {
     "id": "obj-packon",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      260.0,
      660.0,
      130.0,
      22.0
     ],
     "text": "pack 0 100"
    }
   },
   {
    "box": {
     "id": "obj-prevtrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "bang"
     ],
     "patching_rect": [
      40.0,
      620.0,
      130.0,
      22.0
     ],
     "text": "t i b"
    }
   },
   {
    "box": {
     "id": "obj-prev",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      660.0,
      130.0,
      22.0
     ],
     "text": "int -1"
    }
   },
   {
    "box": {
     "id": "obj-wason",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      ""
     ],
     "patching_rect": [
      40.0,
      700.0,
      130.0,
      22.0
     ],
     "text": "sel -1"
    }
   },
   {
    "box": {
     "id": "obj-packoff",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      40.0,
      740.0,
      130.0,
      22.0
     ],
     "text": "pack 0 0"
    }
   },
   {
    "box": {
     "id": "obj-format",
     "maxclass": "newobj",
     "numinlets": 7,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      780.0,
      130.0,
      22.0
     ],
     "text": "midiformat"
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
      820.0,
      130.0,
      22.0
     ],
     "text": "midiout"
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
      420.0,
      460.0,
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
      8.0,
      40.0,
      44.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-fltrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      "int"
     ],
     "patching_rect": [
      420.0,
      500.0,
      130.0,
      22.0
     ],
     "text": "t b i"
    }
   },
   {
    "box": {
     "id": "obj-reset",
     "maxclass": "live.text",
     "mode": 0,
     "text": "Reset",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "patching_rect": [
      560.0,
      100.0,
      44.0,
      16.0
     ],
     "parameter_enable": 1,
     "varname": "Reset",
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_type": 2,
       "parameter_mmax": 1,
       "parameter_enum": [
        "val1",
        "val2"
       ],
       "parameter_invisible": 2,
       "parameter_longname": "Reset",
       "parameter_shortname": "Reset"
      }
     },
     "presentation": 1,
     "presentation_rect": [
      8.0,
      84.0,
      44.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-rtrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      "bang"
     ],
     "patching_rect": [
      560.0,
      140.0,
      130.0,
      22.0
     ],
     "text": "t b b"
    }
   },
   {
    "box": {
     "id": "obj-clear",
     "maxclass": "message",
     "text": "clear",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      560.0,
      180.0,
      60.0,
      22.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-analyze",
     "maxclass": "live.text",
     "mode": 0,
     "text": "Analyze",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "patching_rect": [
      560.0,
      220.0,
      44.0,
      16.0
     ],
     "parameter_enable": 1,
     "varname": "Analyze",
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_type": 2,
       "parameter_mmax": 1,
       "parameter_enum": [
        "val1",
        "val2"
       ],
       "parameter_invisible": 2,
       "parameter_longname": "Analyze",
       "parameter_shortname": "Analyze"
      }
     },
     "presentation": 1,
     "presentation_rect": [
      60.0,
      40.0,
      44.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-rescan",
     "maxclass": "live.text",
     "mode": 0,
     "text": "Rescan",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "patching_rect": [
      560.0,
      260.0,
      44.0,
      16.0
     ],
     "parameter_enable": 1,
     "varname": "Rescan",
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_type": 2,
       "parameter_mmax": 1,
       "parameter_enum": [
        "val1",
        "val2"
       ],
       "parameter_invisible": 2,
       "parameter_longname": "Rescan",
       "parameter_shortname": "Rescan"
      }
     },
     "presentation": 1,
     "presentation_rect": [
      60.0,
      84.0,
      44.0,
      16.0
     ]
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
      700.0,
      300.0,
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
      700.0,
      340.0,
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
     "code": "inlets = 1;\r\noutlets = 2;                      // 0: value for a parameter, 1: status text\r\nvar tracksObserver = null, pending = null;\r\n\r\nfunction status(s) { outlet(1, s); post(\"[Sub Follower] \" + s + \"\\n\"); }\r\nfunction jsonProp(api, prop) { return JSON.parse(String(api.get(prop)))[prop]; }\r\nfunction ownTrack() {\r\n    var m = String(new LiveAPI(null, \"this_device\").unquotedpath)\r\n        .match(/^(live_set tracks (\\d+))/);\r\n    return m ? { path: m[1], index: parseInt(m[2], 10) } : null;\r\n}\r\n// The routing entry (from a device's available list) that IS the track at trackPath: a\r\n// track is never offered to itself, so among same-named entries it is the one whose\r\n// identifier the track's own chooser (availProp) does not list.\r\nfunction trackEntry(trackPath, candidates, availProp) {\r\n    var track = new LiveAPI(null, trackPath);\r\n    var name = String(track.get(\"name\")), theirs = {};\r\n    jsonProp(track, availProp).forEach(function (t) { theirs[t.identifier] = 1; });\r\n    var named = candidates.filter(function (c) { return c.display_name === name; });\r\n    for (var i = 0; i < named.length; i++) if (!theirs[named[i].identifier]) return named[i];\r\n    return named[0] || null;\r\n}\r\nfunction setChannel(api, availProp, prop, wanted) {\r\n    var chans = jsonProp(api, availProp);\r\n    for (var i = 0; i < chans.length; i++) {\r\n        if (chans[i].display_name === wanted) { api.set(prop, chans[i]); return true; }\r\n    }\r\n    return false;\r\n}\r\nfunction eachDevice(fn) {          // fn(trackIndex, devicePath, deviceName)\r\n    var n = new LiveAPI(null, \"live_set\").getcount(\"tracks\");\r\n    for (var i = 0; i < n; i++) {\r\n        var tp = \"live_set tracks \" + i, nd = new LiveAPI(null, tp).getcount(\"devices\");\r\n        for (var d = 0; d < nd; d++) {\r\n            var dp = tp + \" devices \" + d;\r\n            fn(i, dp, String(new LiveAPI(null, dp).get(\"name\")));\r\n        }\r\n    }\r\n}\r\nfunction watch() {                 // re-run configure() when tracks are added/removed/moved\r\n    if (tracksObserver) return;\r\n    tracksObserver = new LiveAPI(function () {\r\n        if (pending) pending.cancel();\r\n        pending = new Task(function () { pending = null; configure(); });\r\n        pending.schedule(600);     // never change the set from inside a notification\r\n    }, \"live_set\");\r\n    tracksObserver.property = \"tracks\";\r\n}\r\nfunction bang() { configure(); watch(); }\r\nfunction rescan() { configure(); }\r\n\r\nvar BAND_LO = 28, BAND_HI = 38, FLOOR_MIN = 24, FLOOR_MAX = 31;\r\nvar W_RANGE = 1.0, W_JUMP = 0.5, EPS = 1e-6;\r\nvar NAMES = [\"C\", \"C#\", \"D\", \"D#\", \"E\", \"F\", \"F#\", \"G\", \"G#\", \"A\", \"A#\", \"B\"];\r\n\r\nfunction noteName(p) { return NAMES[((p % 12) + 12) % 12] + (Math.floor(p / 12) - 2); }\r\nfunction noteHz(p) { return 440 * Math.pow(2, (p - 69) / 12); }\r\nfunction fold(p, floor) { return floor + (((p - floor) % 12) + 12) % 12; }\r\n\r\nfunction sendTracks() {                     // tracks carrying a Sub Send, by index\r\n    var out = [];\r\n    eachDevice(function (i, dp, name) {\r\n        if (name.indexOf(\"Sub Send\") !== -1 && out.indexOf(i) === -1) out.push(i);\r\n    });\r\n    return out;\r\n}\r\n\r\nfunction configure() {\r\n    try {\r\n        var me = ownTrack();\r\n        if (!me) { status(\"drop Sub Follower on an empty MIDI track\"); return; }\r\n        var track = new LiveAPI(null, me.path);\r\n        track.set(\"arm\", 0);\r\n        track.set(\"current_monitoring_state\", 0);           // In: hear the Sends\r\n        if (/^\\d+-MIDI$/.test(String(track.get(\"name\")))) track.set(\"name\", \"Sub Follow\");\r\n\r\n        // Sub track = this track's own MIDI To chooser. Default: first MIDI track with\r\n        // an instrument whose name contains \"sub\"; the user can change it in Live's I/O.\r\n        var cur = jsonProp(track, \"output_routing_type\");\r\n        var types = jsonProp(track, \"available_output_routing_types\");\r\n        var isTrack = function (entry) {\r\n            var n = new LiveAPI(null, \"live_set\").getcount(\"tracks\");\r\n            for (var i = 0; i < n; i++) {\r\n                var t = new LiveAPI(null, \"live_set tracks \" + i);\r\n                if (i !== me.index && String(t.get(\"name\")) === entry.display_name &&\r\n                    Number(t.get(\"has_midi_input\")) === 1 && t.getcount(\"devices\") > 0) return true;\r\n            }\r\n            return false;\r\n        };\r\n        if (!isTrack(cur)) {\r\n            var pick = null;\r\n            for (var i = 0; i < types.length && !pick; i++) {\r\n                if (/sub/i.test(types[i].display_name) && isTrack(types[i])) pick = types[i];\r\n            }\r\n            if (!pick) { status(\"set this track's MIDI To = your sub track\"); return; }\r\n            track.set(\"output_routing_type\", pick);\r\n            cur = pick;\r\n        }\r\n        var chans = jsonProp(track, \"available_output_routing_channels\"), inst = null;\r\n        for (var c = 0; c < chans.length; c++) if (chans[c].display_name !== \"Track In\") inst = chans[c];\r\n        if (!inst) { status(cur.display_name + \" has no instrument to receive notes\"); return; }\r\n        track.set(\"output_routing_channel\", inst);           // bypasses monitoring\r\n\r\n        // Point every Sub Send at this track.\r\n        var count = 0;\r\n        eachDevice(function (i, dp, name) {\r\n            if (name.indexOf(\"Sub Send\") === -1) return;\r\n            var out = new LiveAPI(null, dp + \" midi_outputs 0\");\r\n            var dest = trackEntry(me.path, jsonProp(out, \"available_routing_types\"),\r\n                                  \"available_output_routing_types\");\r\n            if (!dest) return;\r\n            out.set(\"routing_type\", dest);\r\n            setChannel(out, \"available_routing_channels\", \"routing_channel\", \"Track In\");\r\n            count++;\r\n        });\r\n        status(\"following \" + count + \" track(s) -> \" + cur.display_name + \" / \" + inst.display_name);\r\n    } catch (e) { status(\"error: \" + e); }\r\n}\r\n\r\n// ---- auto octave: same scoring as sub_follower_core.py (mono line, range + jump cost)\r\nfunction monoLine(notes) {\r\n    notes = notes.filter(function (n) { return n.duration > EPS; })\r\n                 .sort(function (a, b) { return a.start - b.start; });\r\n    var times = {}, i;\r\n    notes.forEach(function (n) { times[n.start] = 1; times[n.start + n.duration] = 1; });\r\n    var ts = Object.keys(times).map(Number).sort(function (a, b) { return a - b; });\r\n    var line = [], held = [], nxt = 0;\r\n    for (i = 0; i + 1 < ts.length; i++) {\r\n        var t0 = ts[i], t1 = ts[i + 1];\r\n        if (t1 - t0 <= EPS) continue;\r\n        while (nxt < notes.length && notes[nxt].start <= t0 + EPS) {\r\n            held.push({ pitch: notes[nxt].pitch, end: notes[nxt].start + notes[nxt].duration }); nxt++;\r\n        }\r\n        held = held.filter(function (h) { return h.end >= t1 - EPS; });\r\n        if (!held.length) continue;\r\n        var low = Math.min.apply(null, held.map(function (h) { return h.pitch; }));\r\n        var last = line[line.length - 1];\r\n        if (last && last.pitch === low && Math.abs(last.start + last.duration - t0) <= EPS) {\r\n            last.duration = t1 - last.start;\r\n        } else line.push({ pitch: low, start: t0, duration: t1 - t0 });\r\n    }\r\n    return line;\r\n}\r\nfunction scoreFloor(line, floor) {\r\n    var total = 0, outside = 0, moves = 0, jumps = 0, prev = null;\r\n    line.forEach(function (seg) {\r\n        var p = fold(seg.pitch, floor);\r\n        total += seg.duration;\r\n        outside += Math.max(BAND_LO - p, p - BAND_HI, 0) * seg.duration;\r\n        if (prev !== null && p !== prev) { moves++; if (Math.abs(p - prev) > 6) jumps++; }\r\n        prev = p;\r\n    });\r\n    var rc = total > 0 ? outside / total : 0, jc = moves ? jumps / moves : 0;\r\n    return { floor: floor, cost: W_RANGE * rc + W_JUMP * jc };\r\n}\r\nfunction chooseFloor(notes) {\r\n    var line = monoLine(notes), best = null;\r\n    for (var f = FLOOR_MIN; f <= FLOOR_MAX; f++) {\r\n        var s = scoreFloor(line, f);\r\n        if (!best || s.cost < best.cost - EPS ||\r\n            (Math.abs(s.cost - best.cost) <= EPS && Math.abs(f - BAND_LO) < Math.abs(best.floor - BAND_LO))) best = s;\r\n    }\r\n    return best.floor;\r\n}\r\nfunction analyze() {\r\n    try {\r\n        var notes = [];\r\n        sendTracks().forEach(function (i) {\r\n            var t = new LiveAPI(null, \"live_set tracks \" + i), nc = t.getcount(\"arrangement_clips\");\r\n            for (var c = 0; c < nc; c++) {\r\n                var clip = new LiveAPI(null, \"live_set tracks \" + i + \" arrangement_clips \" + c);\r\n                if (Number(clip.get(\"is_midi_clip\")) !== 1) continue;\r\n                var start = Number(clip.get(\"start_time\")), len = Number(clip.get(\"length\"));\r\n                var got = JSON.parse(String(clip.call(\"get_notes_extended\", 0, 128, 0, len)));\r\n                (got.notes || []).forEach(function (n) {\r\n                    if (!n.mute) notes.push({ pitch: n.pitch, start: start + n.start_time, duration: n.duration });\r\n                });\r\n            }\r\n        });\r\n        if (!notes.length) { status(\"no arrangement notes on the Sub Send tracks\"); return; }\r\n        var floor = chooseFloor(notes);\r\n        outlet(0, floor);\r\n        status(\"Floor \" + noteName(floor) + \" (\" + noteHz(floor).toFixed(1) + \" Hz) from \" + notes.length + \" notes\");\r\n    } catch (e) { status(\"analyze error: \" + e); }\r\n}",
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
      700.0,
      380.0,
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
      1140.0,
      380.0,
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
      1140.0,
      420.0,
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
     "id": "msg-obj-analyze",
     "maxclass": "message",
     "text": "analyze",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1140.0,
      460.0,
      60.0,
      22.0
     ]
    }
   },
   {
    "box": {
     "id": "msg-obj-rescan",
     "maxclass": "message",
     "text": "rescan",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1140.0,
      500.0,
      60.0,
      22.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-title",
     "maxclass": "comment",
     "fontsize": 9.0,
     "text": "SUB FOLLOWER",
     "patching_rect": [
      560.0,
      300.0,
      120.0,
      14.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      2.0,
      120.0,
      14.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-floor",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Floor (lowest note)",
     "patching_rect": [
      560.0,
      330.0,
      110.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      24.0,
      110.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-reset",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Clear held",
     "patching_rect": [
      560.0,
      360.0,
      50.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      68.0,
      50.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-hint",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "MIDI To = your sub track",
     "patching_rect": [
      560.0,
      390.0,
      124.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      110.0,
      24.0,
      124.0,
      16.0
     ]
    }
   }
  ],
  "lines": [
   {
    "patchline": {
     "source": [
      "obj-ctlin",
      1
     ],
     "destination": [
      "obj-ctlnum",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ctlin",
      0
     ],
     "destination": [
      "obj-vtrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-vtrig",
      1
     ],
     "destination": [
      "obj-packcv",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-vtrig",
      0
     ],
     "destination": [
      "obj-ctlnum",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ctlnum",
      0
     ],
     "destination": [
      "obj-packcv",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-packcv",
      0
     ],
     "destination": [
      "obj-ntrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ntrig",
      1
     ],
     "destination": [
      "obj-held",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ntrig",
      0
     ],
     "destination": [
      "obj-scan",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-scan",
      2
     ],
     "destination": [
      "obj-best",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-scan",
      2
     ],
     "destination": [
      "obj-min",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-scan",
      1
     ],
     "destination": [
      "obj-uzi",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-scan",
      0
     ],
     "destination": [
      "obj-best",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-uzi",
      2
     ],
     "destination": [
      "obj-heldread",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-heldread",
      0
     ],
     "destination": [
      "obj-nonzero",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-nonzero",
      0
     ],
     "destination": [
      "obj-min",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-min",
      0
     ],
     "destination": [
      "obj-best",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-min",
      0
     ],
     "destination": [
      "obj-min",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-best",
      0
     ],
     "destination": [
      "obj-decode",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-decode",
      0
     ],
     "destination": [
      "obj-fold",
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
      "obj-change",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-change",
      0
     ],
     "destination": [
      "obj-emit",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-emit",
      1
     ],
     "destination": [
      "obj-ison",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ison",
      1
     ],
     "destination": [
      "obj-packon",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-packon",
      0
     ],
     "destination": [
      "obj-format",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-emit",
      0
     ],
     "destination": [
      "obj-prevtrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prevtrig",
      1
     ],
     "destination": [
      "obj-prev",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prevtrig",
      0
     ],
     "destination": [
      "obj-prev",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prev",
      0
     ],
     "destination": [
      "obj-wason",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-wason",
      1
     ],
     "destination": [
      "obj-packoff",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-packoff",
      0
     ],
     "destination": [
      "obj-format",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-format",
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
      "obj-floor",
      0
     ],
     "destination": [
      "obj-fltrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-fltrig",
      1
     ],
     "destination": [
      "obj-fold",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-fltrig",
      0
     ],
     "destination": [
      "obj-scan",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-reset",
      0
     ],
     "destination": [
      "obj-rtrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-rtrig",
      1
     ],
     "destination": [
      "obj-clear",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-clear",
      0
     ],
     "destination": [
      "obj-held",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-rtrig",
      0
     ],
     "destination": [
      "obj-scan",
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
      "obj-analyze",
      0
     ],
     "destination": [
      "msg-obj-analyze",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "msg-obj-analyze",
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
      "obj-rescan",
      0
     ],
     "destination": [
      "msg-obj-rescan",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "msg-obj-rescan",
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
      0
     ],
     "destination": [
      "obj-floor",
      0
     ]
    }
   }
  ],
  "openinpresentation": 1
 }
}