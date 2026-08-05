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
      40.0,
      40.0,
      150.0,
      22.0
     ],
     "text": "udpsend 127.0.0.1 9886"
    }
   },
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
      90.0,
      150.0,
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
      110.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 2"
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
      140.0,
      90.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side0",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak0",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      290.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep0",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      314.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/0/spectrum"
    }
   },
   {
    "box": {
     "id": "ui-lbl0",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "c0",
     "patching_rect": [
      40.0,
      340.0,
      40.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      2.0,
      40.0,
      12.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-ms0",
     "maxclass": "multislider",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "parameter_enable": 0,
     "setminmax": [
      0.0,
      0.3
     ],
     "size": 8,
     "patching_rect": [
      80.0,
      340.0,
      40.0,
      144.0
     ],
     "presentation": 1,
     "presentation_rect": [
      4.0,
      16.0,
      40.0,
      144.0
     ]
    }
   },
   {
    "box": {
     "id": "bp0_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av0_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn0_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp0_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av0_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn0_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp0_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av0_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn0_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp0_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av0_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn0_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp0_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av0_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn0_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp0_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av0_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn0_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp0_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av0_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn0_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
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
      380.0,
      90.0,
      150.0,
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
      380.0,
      110.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 4"
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
      480.0,
      90.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side1",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      640.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak1",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      290.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep1",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      314.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/1/spectrum"
    }
   },
   {
    "box": {
     "id": "ui-lbl1",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "c1",
     "patching_rect": [
      380.0,
      340.0,
      40.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      48.0,
      2.0,
      40.0,
      12.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-ms1",
     "maxclass": "multislider",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "parameter_enable": 0,
     "setminmax": [
      0.0,
      0.3
     ],
     "size": 8,
     "patching_rect": [
      420.0,
      340.0,
      40.0,
      144.0
     ],
     "presentation": 1,
     "presentation_rect": [
      48.0,
      16.0,
      40.0,
      144.0
     ]
    }
   },
   {
    "box": {
     "id": "bp1_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av1_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn1_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp1_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av1_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn1_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp1_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av1_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn1_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp1_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av1_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn1_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp1_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av1_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn1_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp1_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av1_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn1_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp1_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av1_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn1_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
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
      720.0,
      90.0,
      150.0,
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
      720.0,
      110.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 6"
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
      820.0,
      90.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side2",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      980.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak2",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      290.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep2",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      314.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/2/spectrum"
    }
   },
   {
    "box": {
     "id": "ui-lbl2",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "c2",
     "patching_rect": [
      720.0,
      340.0,
      40.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      92.0,
      2.0,
      40.0,
      12.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-ms2",
     "maxclass": "multislider",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "parameter_enable": 0,
     "setminmax": [
      0.0,
      0.3
     ],
     "size": 8,
     "patching_rect": [
      760.0,
      340.0,
      40.0,
      144.0
     ],
     "presentation": 1,
     "presentation_rect": [
      92.0,
      16.0,
      40.0,
      144.0
     ]
    }
   },
   {
    "box": {
     "id": "bp2_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av2_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn2_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp2_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av2_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn2_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp2_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av2_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn2_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp2_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av2_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn2_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp2_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av2_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn2_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp2_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av2_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn2_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp2_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av2_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn2_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
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
      1060.0,
      90.0,
      150.0,
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
      1060.0,
      110.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 8"
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
      1160.0,
      90.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side3",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1320.0,
      114.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak3",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      290.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep3",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      314.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/3/spectrum"
    }
   },
   {
    "box": {
     "id": "ui-lbl3",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "c3",
     "patching_rect": [
      1060.0,
      340.0,
      40.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      136.0,
      2.0,
      40.0,
      12.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-ms3",
     "maxclass": "multislider",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "parameter_enable": 0,
     "setminmax": [
      0.0,
      0.3
     ],
     "size": 8,
     "patching_rect": [
      1100.0,
      340.0,
      40.0,
      144.0
     ],
     "presentation": 1,
     "presentation_rect": [
      136.0,
      16.0,
      40.0,
      144.0
     ]
    }
   },
   {
    "box": {
     "id": "bp3_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av3_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn3_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      130.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp3_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av3_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn3_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      152.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp3_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av3_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn3_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      174.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp3_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av3_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn3_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      196.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp3_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av3_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn3_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      218.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp3_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av3_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn3_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      240.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp3_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av3_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn3_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      262.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p9",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      350.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 9"
    }
   },
   {
    "box": {
     "id": "p10",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      370.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 10"
    }
   },
   {
    "box": {
     "id": "sum4",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      350.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side4",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak4",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      550.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep4",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      574.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/4/spectrum"
    }
   },
   {
    "box": {
     "id": "ui-lbl4",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "c4",
     "patching_rect": [
      40.0,
      600.0,
      40.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      180.0,
      2.0,
      40.0,
      12.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-ms4",
     "maxclass": "multislider",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "parameter_enable": 0,
     "setminmax": [
      0.0,
      0.3
     ],
     "size": 8,
     "patching_rect": [
      80.0,
      600.0,
      40.0,
      144.0
     ],
     "presentation": 1,
     "presentation_rect": [
      180.0,
      16.0,
      40.0,
      144.0
     ]
    }
   },
   {
    "box": {
     "id": "bp4_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av4_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn4_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp4_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av4_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn4_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp4_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av4_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn4_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp4_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av4_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn4_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp4_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av4_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn4_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp4_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av4_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn4_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp4_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av4_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn4_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p11",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      350.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 11"
    }
   },
   {
    "box": {
     "id": "p12",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      370.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 12"
    }
   },
   {
    "box": {
     "id": "sum5",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      350.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side5",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      640.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak5",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      550.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep5",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      574.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/5/spectrum"
    }
   },
   {
    "box": {
     "id": "ui-lbl5",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "c5",
     "patching_rect": [
      380.0,
      600.0,
      40.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      224.0,
      2.0,
      40.0,
      12.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-ms5",
     "maxclass": "multislider",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "parameter_enable": 0,
     "setminmax": [
      0.0,
      0.3
     ],
     "size": 8,
     "patching_rect": [
      420.0,
      600.0,
      40.0,
      144.0
     ],
     "presentation": 1,
     "presentation_rect": [
      224.0,
      16.0,
      40.0,
      144.0
     ]
    }
   },
   {
    "box": {
     "id": "bp5_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av5_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn5_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp5_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av5_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn5_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp5_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av5_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn5_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp5_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av5_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn5_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp5_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av5_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn5_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp5_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av5_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn5_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp5_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av5_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn5_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p13",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      350.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 13"
    }
   },
   {
    "box": {
     "id": "p14",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      370.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 14"
    }
   },
   {
    "box": {
     "id": "sum6",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      350.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side6",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      980.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak6",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      550.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep6",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      574.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/6/spectrum"
    }
   },
   {
    "box": {
     "id": "ui-lbl6",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "c6",
     "patching_rect": [
      720.0,
      600.0,
      40.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      268.0,
      2.0,
      40.0,
      12.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-ms6",
     "maxclass": "multislider",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "parameter_enable": 0,
     "setminmax": [
      0.0,
      0.3
     ],
     "size": 8,
     "patching_rect": [
      760.0,
      600.0,
      40.0,
      144.0
     ],
     "presentation": 1,
     "presentation_rect": [
      268.0,
      16.0,
      40.0,
      144.0
     ]
    }
   },
   {
    "box": {
     "id": "bp6_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av6_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn6_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp6_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av6_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn6_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp6_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av6_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn6_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp6_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av6_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn6_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp6_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av6_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn6_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp6_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av6_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn6_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp6_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av6_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn6_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p15",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      350.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 15"
    }
   },
   {
    "box": {
     "id": "p16",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      370.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 16"
    }
   },
   {
    "box": {
     "id": "sum7",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      350.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side7",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav7",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn7",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1320.0,
      374.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak7",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      550.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep7",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      574.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/7/spectrum"
    }
   },
   {
    "box": {
     "id": "ui-lbl7",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "c7",
     "patching_rect": [
      1060.0,
      600.0,
      40.0,
      12.0
     ],
     "presentation": 1,
     "presentation_rect": [
      312.0,
      2.0,
      40.0,
      12.0
     ]
    }
   },
   {
    "box": {
     "id": "ui-ms7",
     "maxclass": "multislider",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      ""
     ],
     "parameter_enable": 0,
     "setminmax": [
      0.0,
      0.3
     ],
     "size": 8,
     "patching_rect": [
      1100.0,
      600.0,
      40.0,
      144.0
     ],
     "presentation": 1,
     "presentation_rect": [
      312.0,
      16.0,
      40.0,
      144.0
     ]
    }
   },
   {
    "box": {
     "id": "bp7_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av7_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn7_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      390.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp7_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av7_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn7_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      412.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp7_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av7_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn7_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      434.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp7_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av7_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn7_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      456.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp7_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av7_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn7_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      478.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp7_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av7_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn7_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      500.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp7_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av7_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn7_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      522.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
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
      62.0,
      150.0,
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
      16.0,
      640.0,
      20.0
     ],
     "text": "MIX ANALYSIS AGGREGATOR - 8 pairs x 7-band biquad -> /agg/ch/<0..7>/spectrum :9886"
    }
   }
  ],
  "lines": [
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
      "p1",
      0
     ],
     "destination": [
      "side0",
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
      "side0",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side0",
      0
     ],
     "destination": [
      "sideav0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav0",
      0
     ],
     "destination": [
      "sidesn0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn0",
      0
     ],
     "destination": [
      "obj-pak0",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak0",
      0
     ],
     "destination": [
      "obj-prep0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep0",
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
      "obj-pak0",
      0
     ],
     "destination": [
      "ui-ms0",
      0
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
      "bp0_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp0_0",
      0
     ],
     "destination": [
      "av0_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av0_0",
      0
     ],
     "destination": [
      "sn0_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn0_0",
      0
     ],
     "destination": [
      "obj-pak0",
      0
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
      "bp0_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp0_1",
      0
     ],
     "destination": [
      "av0_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av0_1",
      0
     ],
     "destination": [
      "sn0_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn0_1",
      0
     ],
     "destination": [
      "obj-pak0",
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
      "bp0_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp0_2",
      0
     ],
     "destination": [
      "av0_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av0_2",
      0
     ],
     "destination": [
      "sn0_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn0_2",
      0
     ],
     "destination": [
      "obj-pak0",
      2
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
      "bp0_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp0_3",
      0
     ],
     "destination": [
      "av0_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av0_3",
      0
     ],
     "destination": [
      "sn0_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn0_3",
      0
     ],
     "destination": [
      "obj-pak0",
      3
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
      "bp0_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp0_4",
      0
     ],
     "destination": [
      "av0_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av0_4",
      0
     ],
     "destination": [
      "sn0_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn0_4",
      0
     ],
     "destination": [
      "obj-pak0",
      4
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
      "bp0_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp0_5",
      0
     ],
     "destination": [
      "av0_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av0_5",
      0
     ],
     "destination": [
      "sn0_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn0_5",
      0
     ],
     "destination": [
      "obj-pak0",
      5
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
      "bp0_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp0_6",
      0
     ],
     "destination": [
      "av0_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av0_6",
      0
     ],
     "destination": [
      "sn0_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn0_6",
      0
     ],
     "destination": [
      "obj-pak0",
      6
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
      "p3",
      0
     ],
     "destination": [
      "side1",
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
      "side1",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side1",
      0
     ],
     "destination": [
      "sideav1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav1",
      0
     ],
     "destination": [
      "sidesn1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn1",
      0
     ],
     "destination": [
      "obj-pak1",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak1",
      0
     ],
     "destination": [
      "obj-prep1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep1",
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
      "obj-pak1",
      0
     ],
     "destination": [
      "ui-ms1",
      0
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
      "bp1_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp1_0",
      0
     ],
     "destination": [
      "av1_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av1_0",
      0
     ],
     "destination": [
      "sn1_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn1_0",
      0
     ],
     "destination": [
      "obj-pak1",
      0
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
      "bp1_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp1_1",
      0
     ],
     "destination": [
      "av1_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av1_1",
      0
     ],
     "destination": [
      "sn1_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn1_1",
      0
     ],
     "destination": [
      "obj-pak1",
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
      "bp1_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp1_2",
      0
     ],
     "destination": [
      "av1_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av1_2",
      0
     ],
     "destination": [
      "sn1_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn1_2",
      0
     ],
     "destination": [
      "obj-pak1",
      2
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
      "bp1_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp1_3",
      0
     ],
     "destination": [
      "av1_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av1_3",
      0
     ],
     "destination": [
      "sn1_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn1_3",
      0
     ],
     "destination": [
      "obj-pak1",
      3
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
      "bp1_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp1_4",
      0
     ],
     "destination": [
      "av1_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av1_4",
      0
     ],
     "destination": [
      "sn1_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn1_4",
      0
     ],
     "destination": [
      "obj-pak1",
      4
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
      "bp1_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp1_5",
      0
     ],
     "destination": [
      "av1_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av1_5",
      0
     ],
     "destination": [
      "sn1_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn1_5",
      0
     ],
     "destination": [
      "obj-pak1",
      5
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
      "bp1_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp1_6",
      0
     ],
     "destination": [
      "av1_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av1_6",
      0
     ],
     "destination": [
      "sn1_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn1_6",
      0
     ],
     "destination": [
      "obj-pak1",
      6
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
      "p5",
      0
     ],
     "destination": [
      "side2",
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
      "side2",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side2",
      0
     ],
     "destination": [
      "sideav2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav2",
      0
     ],
     "destination": [
      "sidesn2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn2",
      0
     ],
     "destination": [
      "obj-pak2",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak2",
      0
     ],
     "destination": [
      "obj-prep2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep2",
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
      "obj-pak2",
      0
     ],
     "destination": [
      "ui-ms2",
      0
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
      "bp2_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp2_0",
      0
     ],
     "destination": [
      "av2_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av2_0",
      0
     ],
     "destination": [
      "sn2_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn2_0",
      0
     ],
     "destination": [
      "obj-pak2",
      0
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
      "bp2_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp2_1",
      0
     ],
     "destination": [
      "av2_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av2_1",
      0
     ],
     "destination": [
      "sn2_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn2_1",
      0
     ],
     "destination": [
      "obj-pak2",
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
      "bp2_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp2_2",
      0
     ],
     "destination": [
      "av2_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av2_2",
      0
     ],
     "destination": [
      "sn2_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn2_2",
      0
     ],
     "destination": [
      "obj-pak2",
      2
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
      "bp2_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp2_3",
      0
     ],
     "destination": [
      "av2_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av2_3",
      0
     ],
     "destination": [
      "sn2_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn2_3",
      0
     ],
     "destination": [
      "obj-pak2",
      3
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
      "bp2_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp2_4",
      0
     ],
     "destination": [
      "av2_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av2_4",
      0
     ],
     "destination": [
      "sn2_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn2_4",
      0
     ],
     "destination": [
      "obj-pak2",
      4
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
      "bp2_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp2_5",
      0
     ],
     "destination": [
      "av2_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av2_5",
      0
     ],
     "destination": [
      "sn2_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn2_5",
      0
     ],
     "destination": [
      "obj-pak2",
      5
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
      "bp2_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp2_6",
      0
     ],
     "destination": [
      "av2_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av2_6",
      0
     ],
     "destination": [
      "sn2_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn2_6",
      0
     ],
     "destination": [
      "obj-pak2",
      6
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
      "p7",
      0
     ],
     "destination": [
      "side3",
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
      "side3",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side3",
      0
     ],
     "destination": [
      "sideav3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav3",
      0
     ],
     "destination": [
      "sidesn3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn3",
      0
     ],
     "destination": [
      "obj-pak3",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak3",
      0
     ],
     "destination": [
      "obj-prep3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep3",
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
      "obj-pak3",
      0
     ],
     "destination": [
      "ui-ms3",
      0
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
      "bp3_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp3_0",
      0
     ],
     "destination": [
      "av3_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av3_0",
      0
     ],
     "destination": [
      "sn3_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn3_0",
      0
     ],
     "destination": [
      "obj-pak3",
      0
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
      "bp3_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp3_1",
      0
     ],
     "destination": [
      "av3_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av3_1",
      0
     ],
     "destination": [
      "sn3_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn3_1",
      0
     ],
     "destination": [
      "obj-pak3",
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
      "bp3_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp3_2",
      0
     ],
     "destination": [
      "av3_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av3_2",
      0
     ],
     "destination": [
      "sn3_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn3_2",
      0
     ],
     "destination": [
      "obj-pak3",
      2
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
      "bp3_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp3_3",
      0
     ],
     "destination": [
      "av3_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av3_3",
      0
     ],
     "destination": [
      "sn3_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn3_3",
      0
     ],
     "destination": [
      "obj-pak3",
      3
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
      "bp3_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp3_4",
      0
     ],
     "destination": [
      "av3_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av3_4",
      0
     ],
     "destination": [
      "sn3_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn3_4",
      0
     ],
     "destination": [
      "obj-pak3",
      4
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
      "bp3_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp3_5",
      0
     ],
     "destination": [
      "av3_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av3_5",
      0
     ],
     "destination": [
      "sn3_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn3_5",
      0
     ],
     "destination": [
      "obj-pak3",
      5
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
      "bp3_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp3_6",
      0
     ],
     "destination": [
      "av3_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av3_6",
      0
     ],
     "destination": [
      "sn3_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn3_6",
      0
     ],
     "destination": [
      "obj-pak3",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p9",
      0
     ],
     "destination": [
      "sum4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p10",
      0
     ],
     "destination": [
      "sum4",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p9",
      0
     ],
     "destination": [
      "side4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p10",
      0
     ],
     "destination": [
      "side4",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side4",
      0
     ],
     "destination": [
      "sideav4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav4",
      0
     ],
     "destination": [
      "sidesn4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn4",
      0
     ],
     "destination": [
      "obj-pak4",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak4",
      0
     ],
     "destination": [
      "obj-prep4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep4",
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
      "obj-pak4",
      0
     ],
     "destination": [
      "ui-ms4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum4",
      0
     ],
     "destination": [
      "bp4_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp4_0",
      0
     ],
     "destination": [
      "av4_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av4_0",
      0
     ],
     "destination": [
      "sn4_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn4_0",
      0
     ],
     "destination": [
      "obj-pak4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum4",
      0
     ],
     "destination": [
      "bp4_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp4_1",
      0
     ],
     "destination": [
      "av4_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av4_1",
      0
     ],
     "destination": [
      "sn4_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn4_1",
      0
     ],
     "destination": [
      "obj-pak4",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum4",
      0
     ],
     "destination": [
      "bp4_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp4_2",
      0
     ],
     "destination": [
      "av4_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av4_2",
      0
     ],
     "destination": [
      "sn4_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn4_2",
      0
     ],
     "destination": [
      "obj-pak4",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum4",
      0
     ],
     "destination": [
      "bp4_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp4_3",
      0
     ],
     "destination": [
      "av4_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av4_3",
      0
     ],
     "destination": [
      "sn4_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn4_3",
      0
     ],
     "destination": [
      "obj-pak4",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum4",
      0
     ],
     "destination": [
      "bp4_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp4_4",
      0
     ],
     "destination": [
      "av4_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av4_4",
      0
     ],
     "destination": [
      "sn4_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn4_4",
      0
     ],
     "destination": [
      "obj-pak4",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum4",
      0
     ],
     "destination": [
      "bp4_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp4_5",
      0
     ],
     "destination": [
      "av4_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av4_5",
      0
     ],
     "destination": [
      "sn4_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn4_5",
      0
     ],
     "destination": [
      "obj-pak4",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum4",
      0
     ],
     "destination": [
      "bp4_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp4_6",
      0
     ],
     "destination": [
      "av4_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av4_6",
      0
     ],
     "destination": [
      "sn4_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn4_6",
      0
     ],
     "destination": [
      "obj-pak4",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p11",
      0
     ],
     "destination": [
      "sum5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p12",
      0
     ],
     "destination": [
      "sum5",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p11",
      0
     ],
     "destination": [
      "side5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p12",
      0
     ],
     "destination": [
      "side5",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side5",
      0
     ],
     "destination": [
      "sideav5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav5",
      0
     ],
     "destination": [
      "sidesn5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn5",
      0
     ],
     "destination": [
      "obj-pak5",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak5",
      0
     ],
     "destination": [
      "obj-prep5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep5",
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
      "obj-pak5",
      0
     ],
     "destination": [
      "ui-ms5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum5",
      0
     ],
     "destination": [
      "bp5_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp5_0",
      0
     ],
     "destination": [
      "av5_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av5_0",
      0
     ],
     "destination": [
      "sn5_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn5_0",
      0
     ],
     "destination": [
      "obj-pak5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum5",
      0
     ],
     "destination": [
      "bp5_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp5_1",
      0
     ],
     "destination": [
      "av5_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av5_1",
      0
     ],
     "destination": [
      "sn5_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn5_1",
      0
     ],
     "destination": [
      "obj-pak5",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum5",
      0
     ],
     "destination": [
      "bp5_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp5_2",
      0
     ],
     "destination": [
      "av5_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av5_2",
      0
     ],
     "destination": [
      "sn5_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn5_2",
      0
     ],
     "destination": [
      "obj-pak5",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum5",
      0
     ],
     "destination": [
      "bp5_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp5_3",
      0
     ],
     "destination": [
      "av5_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av5_3",
      0
     ],
     "destination": [
      "sn5_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn5_3",
      0
     ],
     "destination": [
      "obj-pak5",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum5",
      0
     ],
     "destination": [
      "bp5_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp5_4",
      0
     ],
     "destination": [
      "av5_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av5_4",
      0
     ],
     "destination": [
      "sn5_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn5_4",
      0
     ],
     "destination": [
      "obj-pak5",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum5",
      0
     ],
     "destination": [
      "bp5_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp5_5",
      0
     ],
     "destination": [
      "av5_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av5_5",
      0
     ],
     "destination": [
      "sn5_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn5_5",
      0
     ],
     "destination": [
      "obj-pak5",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum5",
      0
     ],
     "destination": [
      "bp5_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp5_6",
      0
     ],
     "destination": [
      "av5_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av5_6",
      0
     ],
     "destination": [
      "sn5_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn5_6",
      0
     ],
     "destination": [
      "obj-pak5",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p13",
      0
     ],
     "destination": [
      "sum6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p14",
      0
     ],
     "destination": [
      "sum6",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p13",
      0
     ],
     "destination": [
      "side6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p14",
      0
     ],
     "destination": [
      "side6",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side6",
      0
     ],
     "destination": [
      "sideav6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav6",
      0
     ],
     "destination": [
      "sidesn6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn6",
      0
     ],
     "destination": [
      "obj-pak6",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak6",
      0
     ],
     "destination": [
      "obj-prep6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep6",
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
      "obj-pak6",
      0
     ],
     "destination": [
      "ui-ms6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum6",
      0
     ],
     "destination": [
      "bp6_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp6_0",
      0
     ],
     "destination": [
      "av6_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av6_0",
      0
     ],
     "destination": [
      "sn6_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn6_0",
      0
     ],
     "destination": [
      "obj-pak6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum6",
      0
     ],
     "destination": [
      "bp6_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp6_1",
      0
     ],
     "destination": [
      "av6_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av6_1",
      0
     ],
     "destination": [
      "sn6_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn6_1",
      0
     ],
     "destination": [
      "obj-pak6",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum6",
      0
     ],
     "destination": [
      "bp6_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp6_2",
      0
     ],
     "destination": [
      "av6_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av6_2",
      0
     ],
     "destination": [
      "sn6_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn6_2",
      0
     ],
     "destination": [
      "obj-pak6",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum6",
      0
     ],
     "destination": [
      "bp6_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp6_3",
      0
     ],
     "destination": [
      "av6_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av6_3",
      0
     ],
     "destination": [
      "sn6_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn6_3",
      0
     ],
     "destination": [
      "obj-pak6",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum6",
      0
     ],
     "destination": [
      "bp6_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp6_4",
      0
     ],
     "destination": [
      "av6_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av6_4",
      0
     ],
     "destination": [
      "sn6_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn6_4",
      0
     ],
     "destination": [
      "obj-pak6",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum6",
      0
     ],
     "destination": [
      "bp6_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp6_5",
      0
     ],
     "destination": [
      "av6_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av6_5",
      0
     ],
     "destination": [
      "sn6_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn6_5",
      0
     ],
     "destination": [
      "obj-pak6",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum6",
      0
     ],
     "destination": [
      "bp6_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp6_6",
      0
     ],
     "destination": [
      "av6_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av6_6",
      0
     ],
     "destination": [
      "sn6_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn6_6",
      0
     ],
     "destination": [
      "obj-pak6",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p15",
      0
     ],
     "destination": [
      "sum7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p16",
      0
     ],
     "destination": [
      "sum7",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p15",
      0
     ],
     "destination": [
      "side7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p16",
      0
     ],
     "destination": [
      "side7",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side7",
      0
     ],
     "destination": [
      "sideav7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav7",
      0
     ],
     "destination": [
      "sidesn7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn7",
      0
     ],
     "destination": [
      "obj-pak7",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak7",
      0
     ],
     "destination": [
      "obj-prep7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep7",
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
      "obj-pak7",
      0
     ],
     "destination": [
      "ui-ms7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum7",
      0
     ],
     "destination": [
      "bp7_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp7_0",
      0
     ],
     "destination": [
      "av7_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av7_0",
      0
     ],
     "destination": [
      "sn7_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn7_0",
      0
     ],
     "destination": [
      "obj-pak7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum7",
      0
     ],
     "destination": [
      "bp7_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp7_1",
      0
     ],
     "destination": [
      "av7_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av7_1",
      0
     ],
     "destination": [
      "sn7_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn7_1",
      0
     ],
     "destination": [
      "obj-pak7",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum7",
      0
     ],
     "destination": [
      "bp7_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp7_2",
      0
     ],
     "destination": [
      "av7_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av7_2",
      0
     ],
     "destination": [
      "sn7_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn7_2",
      0
     ],
     "destination": [
      "obj-pak7",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum7",
      0
     ],
     "destination": [
      "bp7_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp7_3",
      0
     ],
     "destination": [
      "av7_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av7_3",
      0
     ],
     "destination": [
      "sn7_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn7_3",
      0
     ],
     "destination": [
      "obj-pak7",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum7",
      0
     ],
     "destination": [
      "bp7_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp7_4",
      0
     ],
     "destination": [
      "av7_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av7_4",
      0
     ],
     "destination": [
      "sn7_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn7_4",
      0
     ],
     "destination": [
      "obj-pak7",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum7",
      0
     ],
     "destination": [
      "bp7_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp7_5",
      0
     ],
     "destination": [
      "av7_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av7_5",
      0
     ],
     "destination": [
      "sn7_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn7_5",
      0
     ],
     "destination": [
      "obj-pak7",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum7",
      0
     ],
     "destination": [
      "bp7_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp7_6",
      0
     ],
     "destination": [
      "av7_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av7_6",
      0
     ],
     "destination": [
      "sn7_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn7_6",
      0
     ],
     "destination": [
      "obj-pak7",
      6
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
  ],
  "openinpresentation": 1
 }
}