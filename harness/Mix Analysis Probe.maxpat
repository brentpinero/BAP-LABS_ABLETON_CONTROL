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
     "id": "p1",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      66.0,
      130.0,
      22.0
     ],
     "text": "plugin~ 1"
    }
   },
   {
    "box": {
     "id": "p2",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      92.0,
      130.0,
      22.0
     ],
     "text": "plugin~ 2"
    }
   },
   {
    "box": {
     "id": "p3",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      118.0,
      130.0,
      22.0
     ],
     "text": "plugin~ 3"
    }
   },
   {
    "box": {
     "id": "p4",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      144.0,
      130.0,
      22.0
     ],
     "text": "plugin~ 4"
    }
   },
   {
    "box": {
     "id": "p5",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      170.0,
      130.0,
      22.0
     ],
     "text": "plugin~ 5"
    }
   },
   {
    "box": {
     "id": "p6",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      196.0,
      130.0,
      22.0
     ],
     "text": "plugin~ 6"
    }
   },
   {
    "box": {
     "id": "p7",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      222.0,
      130.0,
      22.0
     ],
     "text": "plugin~ 7"
    }
   },
   {
    "box": {
     "id": "p8",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      248.0,
      130.0,
      22.0
     ],
     "text": "plugin~ 8"
    }
   },
   {
    "box": {
     "id": "obj-pak",
     "maxclass": "newobj",
     "numinlets": 4,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      500.0,
      300.0,
      130.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      500.0,
      332.0,
      130.0,
      22.0
     ],
     "text": "prepend /probe/pairs"
    }
   },
   {
    "box": {
     "id": "obj-udp",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 0,
     "outlettype": [],
     "patching_rect": [
      500.0,
      364.0,
      130.0,
      22.0
     ],
     "text": "udpsend 127.0.0.1 9885"
    }
   },
   {
    "box": {
     "id": "sum0",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      250.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "avg0",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      320.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "snap0",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      60.0,
      130.0,
      22.0
     ],
     "text": "snapshot~ 100"
    }
   },
   {
    "box": {
     "id": "sum1",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      250.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "avg1",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      320.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "snap1",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      100.0,
      130.0,
      22.0
     ],
     "text": "snapshot~ 100"
    }
   },
   {
    "box": {
     "id": "sum2",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      250.0,
      140.0,
      130.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "avg2",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      320.0,
      140.0,
      130.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "snap2",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      140.0,
      130.0,
      22.0
     ],
     "text": "snapshot~ 100"
    }
   },
   {
    "box": {
     "id": "sum3",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      250.0,
      180.0,
      130.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "avg3",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      320.0,
      180.0,
      130.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "snap3",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      180.0,
      130.0,
      22.0
     ],
     "text": "snapshot~ 100"
    }
   },
   {
    "box": {
     "id": "obj-out",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 0,
     "outlettype": [],
     "patching_rect": [
      40.0,
      300.0,
      130.0,
      22.0
     ],
     "text": "plugout~ 1 2"
    }
   },
   {
    "box": {
     "id": "obj-title",
     "maxclass": "comment",
     "patching_rect": [
      40.0,
      20.0,
      400.0,
      20.0
     ],
     "text": "MIX ANALYSIS PROBE - 4 input pairs -> per-pair RMS OSC :9885"
    }
   }
  ],
  "lines": [
   {
    "patchline": {
     "source": [
      "obj-pak",
      0
     ],
     "destination": [
      "obj-prep",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep",
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
      "p1",
      0
     ],
     "destination": [
      "sum0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p2",
      0
     ],
     "destination": [
      "sum0",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum0",
      0
     ],
     "destination": [
      "avg0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "avg0",
      0
     ],
     "destination": [
      "snap0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "snap0",
      0
     ],
     "destination": [
      "obj-pak",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p3",
      0
     ],
     "destination": [
      "sum1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p4",
      0
     ],
     "destination": [
      "sum1",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum1",
      0
     ],
     "destination": [
      "avg1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "avg1",
      0
     ],
     "destination": [
      "snap1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "snap1",
      0
     ],
     "destination": [
      "obj-pak",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p5",
      0
     ],
     "destination": [
      "sum2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p6",
      0
     ],
     "destination": [
      "sum2",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum2",
      0
     ],
     "destination": [
      "avg2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "avg2",
      0
     ],
     "destination": [
      "snap2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "snap2",
      0
     ],
     "destination": [
      "obj-pak",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p7",
      0
     ],
     "destination": [
      "sum3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p8",
      0
     ],
     "destination": [
      "sum3",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum3",
      0
     ],
     "destination": [
      "avg3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "avg3",
      0
     ],
     "destination": [
      "snap3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "snap3",
      0
     ],
     "destination": [
      "obj-pak",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p1",
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
      "p2",
      0
     ],
     "destination": [
      "obj-out",
      1
     ]
    }
   }
  ]
 }
}