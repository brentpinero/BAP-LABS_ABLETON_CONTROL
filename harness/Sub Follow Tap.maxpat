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
     "text": "table ---tapheld"
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
     "text": "table ---tapheld"
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
      50.0,
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
     "id": "obj-emit",
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
     "id": "obj-slotoff",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      240.0,
      660.0,
      130.0,
      22.0
     ],
     "text": "int 0"
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
      240.0,
      700.0,
      130.0,
      22.0
     ],
     "text": "pack 0 0"
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
      40.0,
      660.0,
      130.0,
      22.0
     ],
     "text": "sel -1"
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
      700.0,
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
      740.0,
      130.0,
      22.0
     ],
     "text": "minimum 127"
    }
   },
   {
    "box": {
     "id": "obj-ontrig",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "bang",
      "int"
     ],
     "patching_rect": [
      40.0,
      780.0,
      130.0,
      22.0
     ],
     "text": "t b i"
    }
   },
   {
    "box": {
     "id": "obj-sloton",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      40.0,
      820.0,
      130.0,
      22.0
     ],
     "text": "int 0"
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
      40.0,
      860.0,
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
      900.0,
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
      940.0,
      130.0,
      22.0
     ],
     "text": "midiout"
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
      50.0,
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
       "parameter_mmax": 127.0,
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
     "id": "ui-title",
     "maxclass": "comment",
     "fontsize": 9.0,
     "text": "SUB FOLLOW TAP",
     "patching_rect": [
      700.0,
      300.0,
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
     "text": "Follow",
     "patching_rect": [
      700.0,
      330.0,
      60.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      30.0,
      26.0,
      60.0,
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
      360.0,
      40.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      56.0,
      64.0,
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
      "obj-slotoff",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-slotoff",
      0
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
      "obj-emit",
      0
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
      "obj-ontrig",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ontrig",
      1
     ],
     "destination": [
      "obj-packon",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-ontrig",
      0
     ],
     "destination": [
      "obj-sloton",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-sloton",
      0
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
      "obj-slotoff",
      1
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
      "obj-sloton",
      1
     ]
    }
   }
  ],
  "openinpresentation": 1
 }
}