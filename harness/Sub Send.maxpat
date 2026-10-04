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
     "id": "obj-in",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "signal",
      "signal"
     ],
     "patching_rect": [
      700.0,
      40.0,
      130.0,
      22.0
     ],
     "text": "plugin~"
    }
   },
   {
    "box": {
     "id": "obj-out",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "signal",
      "signal"
     ],
     "patching_rect": [
      700.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "plugout~"
    }
   },
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
     "id": "obj-parse",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 8,
     "outlettype": [
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      ""
     ],
     "patching_rect": [
      40.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "midiparse"
    }
   },
   {
    "box": {
     "id": "obj-gate",
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
     "text": "gate 1 1"
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
     "text": "table ---sendheld"
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
     "text": "t b b -1"
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
     "text": "uzi 128 0"
    }
   },
   {
    "box": {
     "id": "obj-itrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "int"
     ],
     "patching_rect": [
      240.0,
      300.0,
      130.0,
      22.0
     ],
     "text": "t i i"
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
      340.0,
      340.0,
      130.0,
      22.0
     ],
     "text": "table ---sendheld"
    }
   },
   {
    "box": {
     "id": "obj-isheld",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      340.0,
      380.0,
      130.0,
      22.0
     ],
     "text": "> 0"
    }
   },
   {
    "box": {
     "id": "obj-hitgate",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      240.0,
      420.0,
      130.0,
      22.0
     ],
     "text": "gate 1"
    }
   },
   {
    "box": {
     "id": "obj-hit",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      "int"
     ],
     "patching_rect": [
      240.0,
      460.0,
      130.0,
      22.0
     ],
     "text": "t b i"
    }
   },
   {
    "box": {
     "id": "obj-break",
     "maxclass": "message",
     "text": "break",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      240.0,
      500.0,
      60.0,
      22.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-lowest",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      540.0,
      130.0,
      22.0
     ],
     "text": "int -1"
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
      580.0,
      130.0,
      22.0
     ],
     "text": "change -1"
    }
   },
   {
    "box": {
     "id": "obj-plus1",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      620.0,
      130.0,
      22.0
     ],
     "text": "+ 1"
    }
   },
   {
    "box": {
     "id": "obj-cap",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "int"
     ],
     "patching_rect": [
      40.0,
      660.0,
      130.0,
      22.0
     ],
     "text": "minimum 127"
    }
   },
   {
    "box": {
     "id": "obj-floor0",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      40.0,
      700.0,
      130.0,
      22.0
     ],
     "text": "maximum 0"
    }
   },
   {
    "box": {
     "id": "obj-ctlout",
     "maxclass": "newobj",
     "numinlets": 3,
     "numoutlets": 0,
     "outlettype": [],
     "patching_rect": [
      40.0,
      740.0,
      130.0,
      22.0
     ],
     "text": "ctlout"
    }
   },
   {
    "box": {
     "id": "obj-follow",
     "maxclass": "live.toggle",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      500.0,
      20.0,
      18.0,
      18.0
     ],
     "parameter_enable": 1,
     "varname": "Follow",
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
       "parameter_longname": "Follow",
       "parameter_shortname": "Follow"
      }
     },
     "presentation": 1,
     "presentation_rect": [
      8.0,
      24.0,
      18.0,
      18.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ftrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "int",
      "int"
     ],
     "patching_rect": [
      500.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "t i i"
    }
   },
   {
    "box": {
     "id": "obj-foff",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      ""
     ],
     "patching_rect": [
      500.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "sel 0"
    }
   },
   {
    "box": {
     "id": "obj-ctrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      "bang"
     ],
     "patching_rect": [
      500.0,
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
      500.0,
      180.0,
      60.0,
      22.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-slot",
     "maxclass": "live.numbox",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      "float"
     ],
     "patching_rect": [
      500.0,
      660.0,
      44.0,
      16.0
     ],
     "parameter_enable": 1,
     "varname": "Slot",
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_type": 1,
       "parameter_unitstyle": 0,
       "parameter_mmin": 0.0,
       "parameter_mmax": 119.0,
       "parameter_initial": [
        0
       ],
       "parameter_initial_enable": 1,
       "parameter_longname": "Slot",
       "parameter_shortname": "Slot"
      }
     },
     "presentation": 1,
     "presentation_rect": [
      8.0,
      64.0,
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
     "code": "inlets = 1;\r\noutlets = 2;                      // 0: value for a parameter, 1: status text\r\nvar tracksObserver = null, pending = null;\r\n\r\nfunction status(s) { outlet(1, s); post(\"[Sub Send] \" + s + \"\\n\"); }\r\nfunction jsonProp(api, prop) { return JSON.parse(String(api.get(prop)))[prop]; }\r\nfunction ownTrack() {\r\n    var m = String(new LiveAPI(null, \"this_device\").unquotedpath)\r\n        .match(/^(live_set tracks (\\d+))/);\r\n    return m ? { path: m[1], index: parseInt(m[2], 10) } : null;\r\n}\r\n// The routing entry (from a device's available list) that IS the track at trackPath: a\r\n// track is never offered to itself, so among same-named entries it is the one whose\r\n// identifier the track's own chooser (availProp) does not list.\r\nfunction trackEntry(trackPath, candidates, availProp) {\r\n    var track = new LiveAPI(null, trackPath);\r\n    var name = String(track.get(\"name\")), theirs = {};\r\n    jsonProp(track, availProp).forEach(function (t) { theirs[t.identifier] = 1; });\r\n    var named = candidates.filter(function (c) { return c.display_name === name; });\r\n    for (var i = 0; i < named.length; i++) if (!theirs[named[i].identifier]) return named[i];\r\n    return named[0] || null;\r\n}\r\nfunction setChannel(api, availProp, prop, wanted) {\r\n    var chans = jsonProp(api, availProp);\r\n    for (var i = 0; i < chans.length; i++) {\r\n        if (chans[i].display_name === wanted) { api.set(prop, chans[i]); return true; }\r\n    }\r\n    return false;\r\n}\r\nfunction eachDevice(fn) {          // fn(trackIndex, devicePath, deviceName)\r\n    var n = new LiveAPI(null, \"live_set\").getcount(\"tracks\");\r\n    for (var i = 0; i < n; i++) {\r\n        var tp = \"live_set tracks \" + i, nd = new LiveAPI(null, tp).getcount(\"devices\");\r\n        for (var d = 0; d < nd; d++) {\r\n            var dp = tp + \" devices \" + d;\r\n            fn(i, dp, String(new LiveAPI(null, dp).get(\"name\")));\r\n        }\r\n    }\r\n}\r\nfunction schedule() {              // never change the set from inside a notification\r\n    if (pending) pending.cancel();\r\n    pending = new Task(function () { pending = null; configure(); });\r\n    pending.schedule(600);\r\n}\r\nfunction watch() {                 // re-run configure() when tracks are added/removed/moved\r\n    if (tracksObserver) return;\r\n    tracksObserver = new LiveAPI(schedule, \"live_set\");\r\n    tracksObserver.property = \"tracks\";\r\n}\r\nfunction bang() { configure(); watch(); }\r\nfunction rescan() { configure(); }\r\n\r\noutlets = 3;                      // 2: \"first setup done\" flag (stored with the device)\r\nvar setupDone = 0;\r\nfunction setupdone(v) { setupDone = v; }\r\n\r\n// A Max for Live device cannot load another Max for Live device (Live's API inserts native\r\n// devices only), so the Send cannot add the Sub Follower itself. On a FRESH drop it makes\r\n// the empty \"Sub Follow\" track ready; the user drops Sub Follower on it once.\r\nfunction ensureFollowTrack() {\r\n    var song = new LiveAPI(null, \"live_set\"), n = song.getcount(\"tracks\");\r\n    for (var i = 0; i < n; i++) {\r\n        if (String(new LiveAPI(null, \"live_set tracks \" + i).get(\"name\")) === \"Sub Follow\") return;\r\n    }\r\n    song.call(\"create_midi_track\", -1);\r\n    var t = new LiveAPI(null, \"live_set tracks \" + n);\r\n    t.set(\"name\", \"Sub Follow\");\r\n    t.set(\"arm\", 0);\r\n}\r\n\r\nfunction configure() {\r\n    try {\r\n        var me = ownTrack();\r\n        if (!me) { status(\"put Sub Send on a bass track\"); return; }\r\n        var inp = new LiveAPI(null, \"this_device midi_inputs 0\");\r\n        var own = trackEntry(me.path, jsonProp(inp, \"available_routing_types\"),\r\n                             \"available_input_routing_types\");\r\n        if (!own) { status(\"this track is not routable\"); return; }\r\n        inp.set(\"routing_type\", own);\r\n        setChannel(inp, \"available_routing_channels\", \"routing_channel\", \"Pre FX\");\r\n        outlet(0, me.index % 120);                 // Slot = CC number\r\n        var fol = null;\r\n        eachDevice(function (i, dp, name) {\r\n            if (!fol && name.indexOf(\"Sub Follower\") !== -1) fol = \"live_set tracks \" + i;\r\n        });\r\n        if (!fol) {\r\n            if (!setupDone) { ensureFollowTrack(); outlet(2, 1); }\r\n            status(\"drop Sub Follower on the 'Sub Follow' track\");\r\n            return;\r\n        }\r\n        outlet(2, 1);\r\n        var out = new LiveAPI(null, \"this_device midi_outputs 0\");\r\n        var dest = trackEntry(fol, jsonProp(out, \"available_routing_types\"),\r\n                              \"available_output_routing_types\");\r\n        if (!dest) { status(\"Sub Follower track not routable\"); return; }\r\n        out.set(\"routing_type\", dest);\r\n        setChannel(out, \"available_routing_channels\", \"routing_channel\", \"Track In\");\r\n        status(\"-> \" + dest.display_name + \"  (slot \" + (me.index % 120) + \")\");\r\n    } catch (e) { status(\"error: \" + e); }\r\n}",
     "fontface": 0,
     "fontname": "Menlo",
     "fontsize": 11.0,
     "numinlets": 1,
     "numoutlets": 3,
     "outlettype": [
      "",
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
      460.0,
      60.0,
      22.0
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
      500.0,
      700.0,
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
      64.0,
      44.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-setup",
     "maxclass": "live.toggle",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1140.0,
      520.0,
      18.0,
      18.0
     ],
     "parameter_enable": 1,
     "varname": "Setup Done",
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_type": 2,
       "parameter_mmax": 1,
       "parameter_enum": [
        "off",
        "on"
       ],
       "parameter_initial": [
        0
       ],
       "parameter_initial_enable": 1,
       "parameter_longname": "Setup Done",
       "parameter_shortname": "Setup Done",
       "parameter_invisible": 1
      }
     }
    }
   },
   {
    "box": {
     "id": "obj-setupmsg",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1140.0,
      560.0,
      130.0,
      22.0
     ],
     "text": "prepend setupdone"
    }
   },
   {
    "box": {
     "id": "ui-title",
     "maxclass": "comment",
     "fontsize": 9.0,
     "text": "SUB SEND",
     "patching_rect": [
      700.0,
      200.0,
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
     "id": "ui-follow",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Follow this track",
     "patching_rect": [
      700.0,
      230.0,
      120.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      30.0,
      26.0,
      120.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-slot",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Slot",
     "patching_rect": [
      700.0,
      260.0,
      40.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      56.0,
      48.0,
      40.0,
      16.0
     ]
    }
   }
  ],
  "lines": [
   {
    "patchline": {
     "source": [
      "obj-in",
      0
     ],
     "destination": [
      "obj-out",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-in",
      1
     ],
     "destination": [
      "obj-out",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-midiin",
      0
     ],
     "destination": [
      "obj-parse",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-parse",
      0
     ],
     "destination": [
      "obj-gate",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-gate",
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
      "obj-scan",
      2
     ],
     "destination": [
      "obj-lowest",
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
      "obj-lowest",
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
      "obj-itrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-itrig",
      1
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
      "obj-isheld",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-isheld",
      0
     ],
     "destination": [
      "obj-hitgate",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-itrig",
      0
     ],
     "destination": [
      "obj-hitgate",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-hitgate",
      0
     ],
     "destination": [
      "obj-hit",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-hit",
      1
     ],
     "destination": [
      "obj-lowest",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-hit",
      0
     ],
     "destination": [
      "obj-break",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-break",
      0
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
      "obj-lowest",
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
      "obj-plus1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plus1",
      0
     ],
     "destination": [
      "obj-cap",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-cap",
      0
     ],
     "destination": [
      "obj-floor0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-floor0",
      0
     ],
     "destination": [
      "obj-ctlout",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-follow",
      0
     ],
     "destination": [
      "obj-ftrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ftrig",
      1
     ],
     "destination": [
      "obj-gate",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ftrig",
      0
     ],
     "destination": [
      "obj-foff",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-foff",
      0
     ],
     "destination": [
      "obj-ctrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ctrig",
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
      "obj-ctrig",
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
      "obj-slot",
      0
     ],
     "destination": [
      "obj-ctlout",
      1
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
      "obj-slot",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-js",
      2
     ],
     "destination": [
      "obj-setup",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-setup",
      0
     ],
     "destination": [
      "obj-setupmsg",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-setupmsg",
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