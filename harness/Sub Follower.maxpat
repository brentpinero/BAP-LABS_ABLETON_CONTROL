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
      100.0,
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
      140.0,
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
      180.0,
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
      220.0,
      130.0,
      22.0
     ],
     "text": "uzi 128 0"
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
      260.0,
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
      300.0,
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
      340.0,
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
      380.0,
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
      420.0,
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
      460.0,
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
      500.0,
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
      540.0,
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
      580.0,
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
      620.0,
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
      580.0,
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
      620.0,
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
      660.0,
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
      700.0,
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
      740.0,
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
      780.0,
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
      420.0,
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
      460.0,
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
      50.0,
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
     "id": "ui-floor",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Floor (lowest note)",
     "patching_rect": [
      560.0,
      330.0,
      96.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      24.0,
      96.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-reset",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "Clear held notes",
     "patching_rect": [
      560.0,
      360.0,
      96.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      68.0,
      96.0,
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
   }
  ],
  "openinpresentation": 1
 }
}