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
     "id": "obj-udp",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 0,
     "outlettype": [],
     "patching_rect": [
      500.0,
      300.0,
      130.0,
      22.0
     ],
     "text": "udpsend 127.0.0.1 9888"
    }
   },
   {
    "box": {
     "id": "min1",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "midiin"
    }
   },
   {
    "box": {
     "id": "mparse1",
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
      200.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "midiparse"
    }
   },
   {
    "box": {
     "id": "mpre1",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      360.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "prepend /midiprobe/in/1"
    }
   },
   {
    "box": {
     "id": "min2",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      160.0,
      130.0,
      22.0
     ],
     "text": "midiin"
    }
   },
   {
    "box": {
     "id": "mparse2",
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
      200.0,
      160.0,
      130.0,
      22.0
     ],
     "text": "midiparse"
    }
   },
   {
    "box": {
     "id": "mpre2",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      360.0,
      160.0,
      130.0,
      22.0
     ],
     "text": "prepend /midiprobe/in/2"
    }
   },
   {
    "box": {
     "id": "min3",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      220.0,
      130.0,
      22.0
     ],
     "text": "midiin"
    }
   },
   {
    "box": {
     "id": "mparse3",
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
      200.0,
      220.0,
      130.0,
      22.0
     ],
     "text": "midiparse"
    }
   },
   {
    "box": {
     "id": "mpre3",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      360.0,
      220.0,
      130.0,
      22.0
     ],
     "text": "prepend /midiprobe/in/3"
    }
   },
   {
    "box": {
     "id": "min4",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      280.0,
      130.0,
      22.0
     ],
     "text": "midiin"
    }
   },
   {
    "box": {
     "id": "mparse4",
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
      200.0,
      280.0,
      130.0,
      22.0
     ],
     "text": "midiparse"
    }
   },
   {
    "box": {
     "id": "mpre4",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      360.0,
      280.0,
      130.0,
      22.0
     ],
     "text": "prepend /midiprobe/in/4"
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
      340.0,
      130.0,
      22.0
     ],
     "text": "midiout"
    }
   },
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
      60.0,
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
      120.0,
      130.0,
      22.0
     ],
     "text": "plugout~"
    }
   },
   {
    "box": {
     "id": "ui-lbl",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "MIDI IO PROBE",
     "patching_rect": [
      500.0,
      400.0,
      120.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      2.0,
      120.0,
      12.0
     ]
    }
   }
  ],
  "lines": [
   {
    "patchline": {
     "source": [
      "min1",
      0
     ],
     "destination": [
      "mparse1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "mparse1",
      0
     ],
     "destination": [
      "mpre1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "mpre1",
      0
     ],
     "destination": [
      "obj-udp",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "min2",
      0
     ],
     "destination": [
      "mparse2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "mparse2",
      0
     ],
     "destination": [
      "mpre2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "mpre2",
      0
     ],
     "destination": [
      "obj-udp",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "min3",
      0
     ],
     "destination": [
      "mparse3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "mparse3",
      0
     ],
     "destination": [
      "mpre3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "mpre3",
      0
     ],
     "destination": [
      "obj-udp",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "min4",
      0
     ],
     "destination": [
      "mparse4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "mparse4",
      0
     ],
     "destination": [
      "mpre4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "mpre4",
      0
     ],
     "destination": [
      "obj-udp",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "min1",
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
   }
  ],
  "openinpresentation": 1
 }
}