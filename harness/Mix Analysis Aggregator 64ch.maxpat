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
     "id": "p17",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      610.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 17"
    }
   },
   {
    "box": {
     "id": "p18",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      630.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 18"
    }
   },
   {
    "box": {
     "id": "sum8",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      610.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side8",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav8",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn8",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak8",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      810.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep8",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      834.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/8/spectrum"
    }
   },
   {
    "box": {
     "id": "bp8_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av8_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn8_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp8_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av8_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn8_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp8_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av8_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn8_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp8_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av8_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn8_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp8_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av8_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn8_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp8_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av8_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn8_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp8_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av8_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn8_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p19",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      610.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 19"
    }
   },
   {
    "box": {
     "id": "p20",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      630.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 20"
    }
   },
   {
    "box": {
     "id": "sum9",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      610.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side9",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav9",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn9",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      640.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak9",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      810.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep9",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      834.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/9/spectrum"
    }
   },
   {
    "box": {
     "id": "bp9_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av9_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn9_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp9_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av9_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn9_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp9_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av9_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn9_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp9_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av9_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn9_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp9_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av9_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn9_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp9_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av9_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn9_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp9_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av9_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn9_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p21",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      610.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 21"
    }
   },
   {
    "box": {
     "id": "p22",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      630.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 22"
    }
   },
   {
    "box": {
     "id": "sum10",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      610.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side10",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav10",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn10",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      980.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak10",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      810.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep10",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      834.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/10/spectrum"
    }
   },
   {
    "box": {
     "id": "bp10_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av10_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn10_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp10_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av10_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn10_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp10_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av10_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn10_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp10_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av10_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn10_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp10_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av10_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn10_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp10_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av10_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn10_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp10_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av10_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn10_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p23",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      610.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 23"
    }
   },
   {
    "box": {
     "id": "p24",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      630.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 24"
    }
   },
   {
    "box": {
     "id": "sum11",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      610.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side11",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav11",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn11",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1320.0,
      634.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak11",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      810.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep11",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      834.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/11/spectrum"
    }
   },
   {
    "box": {
     "id": "bp11_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av11_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn11_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      650.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp11_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av11_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn11_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      672.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp11_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av11_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn11_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      694.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp11_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av11_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn11_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      716.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp11_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av11_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn11_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      738.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp11_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av11_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn11_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      760.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp11_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av11_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn11_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      782.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p25",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      870.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 25"
    }
   },
   {
    "box": {
     "id": "p26",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      890.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 26"
    }
   },
   {
    "box": {
     "id": "sum12",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      870.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side12",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav12",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn12",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak12",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      1070.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep12",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      1094.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/12/spectrum"
    }
   },
   {
    "box": {
     "id": "bp12_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av12_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn12_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp12_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av12_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn12_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp12_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av12_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn12_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp12_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av12_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn12_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp12_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av12_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn12_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp12_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av12_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn12_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp12_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av12_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn12_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p27",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      870.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 27"
    }
   },
   {
    "box": {
     "id": "p28",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      890.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 28"
    }
   },
   {
    "box": {
     "id": "sum13",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      870.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side13",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav13",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn13",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      640.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak13",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      1070.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep13",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      1094.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/13/spectrum"
    }
   },
   {
    "box": {
     "id": "bp13_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av13_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn13_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp13_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av13_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn13_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp13_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av13_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn13_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp13_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av13_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn13_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp13_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av13_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn13_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp13_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av13_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn13_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp13_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av13_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn13_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p29",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      870.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 29"
    }
   },
   {
    "box": {
     "id": "p30",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      890.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 30"
    }
   },
   {
    "box": {
     "id": "sum14",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      870.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side14",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav14",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn14",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      980.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak14",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      1070.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep14",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      1094.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/14/spectrum"
    }
   },
   {
    "box": {
     "id": "bp14_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av14_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn14_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp14_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av14_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn14_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp14_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av14_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn14_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp14_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av14_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn14_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp14_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av14_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn14_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp14_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av14_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn14_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp14_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av14_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn14_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p31",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      870.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 31"
    }
   },
   {
    "box": {
     "id": "p32",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      890.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 32"
    }
   },
   {
    "box": {
     "id": "sum15",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      870.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side15",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav15",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn15",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1320.0,
      894.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak15",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      1070.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep15",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      1094.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/15/spectrum"
    }
   },
   {
    "box": {
     "id": "bp15_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av15_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn15_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      910.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp15_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av15_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn15_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      932.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp15_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av15_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn15_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      954.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp15_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av15_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn15_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      976.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp15_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av15_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn15_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      998.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp15_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av15_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn15_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1020.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp15_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av15_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn15_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1042.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p33",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      1130.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 33"
    }
   },
   {
    "box": {
     "id": "p34",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      1150.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 34"
    }
   },
   {
    "box": {
     "id": "sum16",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      1130.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side16",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav16",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn16",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak16",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      1330.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep16",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      1354.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/16/spectrum"
    }
   },
   {
    "box": {
     "id": "bp16_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av16_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn16_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp16_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av16_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn16_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp16_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av16_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn16_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp16_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av16_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn16_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp16_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av16_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn16_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp16_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av16_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn16_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp16_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av16_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn16_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p35",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      1130.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 35"
    }
   },
   {
    "box": {
     "id": "p36",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      1150.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 36"
    }
   },
   {
    "box": {
     "id": "sum17",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      1130.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side17",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav17",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn17",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      640.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak17",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      1330.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep17",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      1354.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/17/spectrum"
    }
   },
   {
    "box": {
     "id": "bp17_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av17_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn17_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp17_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av17_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn17_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp17_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av17_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn17_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp17_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av17_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn17_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp17_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av17_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn17_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp17_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av17_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn17_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp17_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av17_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn17_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p37",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      1130.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 37"
    }
   },
   {
    "box": {
     "id": "p38",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      1150.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 38"
    }
   },
   {
    "box": {
     "id": "sum18",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      1130.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side18",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav18",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn18",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      980.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak18",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      1330.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep18",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      1354.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/18/spectrum"
    }
   },
   {
    "box": {
     "id": "bp18_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av18_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn18_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp18_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av18_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn18_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp18_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av18_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn18_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp18_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av18_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn18_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp18_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av18_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn18_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp18_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av18_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn18_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp18_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av18_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn18_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p39",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      1130.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 39"
    }
   },
   {
    "box": {
     "id": "p40",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      1150.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 40"
    }
   },
   {
    "box": {
     "id": "sum19",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      1130.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side19",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav19",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn19",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1320.0,
      1154.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak19",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      1330.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep19",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      1354.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/19/spectrum"
    }
   },
   {
    "box": {
     "id": "bp19_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av19_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn19_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1170.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp19_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av19_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn19_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1192.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp19_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av19_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn19_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1214.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp19_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av19_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn19_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1236.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp19_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av19_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn19_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1258.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp19_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av19_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn19_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1280.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp19_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av19_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn19_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1302.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p41",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      1390.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 41"
    }
   },
   {
    "box": {
     "id": "p42",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      1410.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 42"
    }
   },
   {
    "box": {
     "id": "sum20",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      1390.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side20",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav20",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn20",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak20",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      1590.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep20",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      1614.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/20/spectrum"
    }
   },
   {
    "box": {
     "id": "bp20_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av20_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn20_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp20_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av20_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn20_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp20_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av20_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn20_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp20_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av20_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn20_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp20_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av20_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn20_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp20_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av20_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn20_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp20_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av20_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn20_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p43",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      1390.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 43"
    }
   },
   {
    "box": {
     "id": "p44",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      1410.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 44"
    }
   },
   {
    "box": {
     "id": "sum21",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      1390.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side21",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav21",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn21",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      640.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak21",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      1590.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep21",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      1614.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/21/spectrum"
    }
   },
   {
    "box": {
     "id": "bp21_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av21_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn21_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp21_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av21_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn21_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp21_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av21_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn21_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp21_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av21_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn21_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp21_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av21_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn21_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp21_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av21_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn21_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp21_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av21_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn21_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p45",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      1390.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 45"
    }
   },
   {
    "box": {
     "id": "p46",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      1410.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 46"
    }
   },
   {
    "box": {
     "id": "sum22",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      1390.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side22",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav22",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn22",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      980.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak22",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      1590.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep22",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      1614.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/22/spectrum"
    }
   },
   {
    "box": {
     "id": "bp22_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av22_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn22_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp22_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av22_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn22_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp22_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av22_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn22_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp22_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av22_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn22_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp22_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av22_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn22_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp22_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av22_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn22_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp22_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av22_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn22_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p47",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      1390.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 47"
    }
   },
   {
    "box": {
     "id": "p48",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      1410.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 48"
    }
   },
   {
    "box": {
     "id": "sum23",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      1390.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side23",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav23",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn23",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1320.0,
      1414.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak23",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      1590.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep23",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      1614.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/23/spectrum"
    }
   },
   {
    "box": {
     "id": "bp23_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av23_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn23_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1430.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp23_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av23_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn23_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1452.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp23_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av23_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn23_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1474.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp23_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av23_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn23_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1496.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp23_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av23_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn23_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1518.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp23_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av23_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn23_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1540.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp23_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av23_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn23_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1562.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p49",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      1650.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 49"
    }
   },
   {
    "box": {
     "id": "p50",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      1670.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 50"
    }
   },
   {
    "box": {
     "id": "sum24",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      1650.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side24",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav24",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn24",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak24",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      1850.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep24",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      1874.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/24/spectrum"
    }
   },
   {
    "box": {
     "id": "bp24_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av24_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn24_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp24_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av24_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn24_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp24_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av24_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn24_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp24_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av24_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn24_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp24_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av24_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn24_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp24_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av24_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn24_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp24_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av24_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn24_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p51",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      1650.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 51"
    }
   },
   {
    "box": {
     "id": "p52",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      1670.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 52"
    }
   },
   {
    "box": {
     "id": "sum25",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      1650.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side25",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav25",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn25",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      640.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak25",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      1850.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep25",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      1874.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/25/spectrum"
    }
   },
   {
    "box": {
     "id": "bp25_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av25_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn25_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp25_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av25_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn25_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp25_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av25_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn25_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp25_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av25_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn25_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp25_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av25_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn25_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp25_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av25_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn25_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp25_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av25_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn25_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p53",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      1650.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 53"
    }
   },
   {
    "box": {
     "id": "p54",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      1670.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 54"
    }
   },
   {
    "box": {
     "id": "sum26",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      1650.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side26",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav26",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn26",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      980.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak26",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      1850.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep26",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      1874.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/26/spectrum"
    }
   },
   {
    "box": {
     "id": "bp26_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av26_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn26_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp26_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av26_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn26_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp26_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av26_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn26_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp26_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av26_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn26_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp26_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av26_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn26_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp26_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av26_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn26_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp26_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av26_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn26_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p55",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      1650.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 55"
    }
   },
   {
    "box": {
     "id": "p56",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      1670.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 56"
    }
   },
   {
    "box": {
     "id": "sum27",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      1650.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side27",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav27",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn27",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1320.0,
      1674.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak27",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      1850.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep27",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      1874.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/27/spectrum"
    }
   },
   {
    "box": {
     "id": "bp27_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av27_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn27_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1690.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp27_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av27_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn27_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1712.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp27_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av27_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn27_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1734.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp27_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av27_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn27_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1756.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp27_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av27_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn27_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1778.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp27_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av27_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn27_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1800.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp27_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av27_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn27_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1822.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p57",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      1910.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 57"
    }
   },
   {
    "box": {
     "id": "p58",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      40.0,
      1930.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 58"
    }
   },
   {
    "box": {
     "id": "sum28",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      1910.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side28",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      140.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav28",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn28",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      300.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak28",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      2110.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep28",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      140.0,
      2134.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/28/spectrum"
    }
   },
   {
    "box": {
     "id": "bp28_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av28_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn28_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp28_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av28_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn28_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp28_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av28_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn28_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp28_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av28_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn28_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp28_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av28_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn28_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp28_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av28_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn28_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp28_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av28_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      240.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn28_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      280.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p59",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      1910.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 59"
    }
   },
   {
    "box": {
     "id": "p60",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      380.0,
      1930.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 60"
    }
   },
   {
    "box": {
     "id": "sum29",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      1910.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side29",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      480.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav29",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn29",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      640.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak29",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      2110.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep29",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      480.0,
      2134.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/29/spectrum"
    }
   },
   {
    "box": {
     "id": "bp29_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av29_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn29_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp29_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av29_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn29_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp29_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av29_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn29_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp29_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av29_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn29_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp29_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av29_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn29_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp29_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av29_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn29_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp29_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      540.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av29_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      580.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn29_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p61",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      1910.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 61"
    }
   },
   {
    "box": {
     "id": "p62",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      720.0,
      1930.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 62"
    }
   },
   {
    "box": {
     "id": "sum30",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      1910.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side30",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      820.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav30",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn30",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      980.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak30",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      2110.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep30",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      820.0,
      2134.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/30/spectrum"
    }
   },
   {
    "box": {
     "id": "bp30_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av30_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn30_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp30_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av30_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn30_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp30_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av30_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn30_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp30_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av30_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn30_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp30_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av30_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn30_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp30_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av30_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn30_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp30_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      880.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av30_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      920.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn30_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      960.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "p63",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      1910.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 63"
    }
   },
   {
    "box": {
     "id": "p64",
     "maxclass": "newobj",
     "numinlets": 0,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1060.0,
      1930.0,
      150.0,
      22.0
     ],
     "text": "plugin~ 64"
    }
   },
   {
    "box": {
     "id": "sum31",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      1910.0,
      150.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "side31",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1160.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "sideav31",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sidesn31",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1320.0,
      1934.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "obj-pak31",
     "maxclass": "newobj",
     "numinlets": 8,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      2110.0,
      150.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-prep31",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1160.0,
      2134.0,
      150.0,
      22.0
     ],
     "text": "prepend /agg/ch/31/spectrum"
    }
   },
   {
    "box": {
     "id": "bp31_0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "av31_0",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn31_0",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1950.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp31_1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "av31_1",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn31_1",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1972.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp31_2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "av31_2",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn31_2",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      1994.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp31_3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "av31_3",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn31_3",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      2016.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp31_4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "av31_4",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn31_4",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      2038.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp31_5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "av31_5",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn31_5",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      2060.0,
      150.0,
      22.0
     ],
     "text": "snapshot~ 60"
    }
   },
   {
    "box": {
     "id": "bp31_6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1220.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "av31_6",
     "maxclass": "newobj",
     "numinlets": 150,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      1260.0,
      2082.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "sn31_6",
     "maxclass": "newobj",
     "numinlets": 90,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1300.0,
      2082.0,
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
      600.0,
      20.0
     ],
     "text": "MIX ANALYSIS AGGREGATOR - 32 pairs x 7-band biquad -> /agg/ch/<k>/spectrum :9886"
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
      "p17",
      0
     ],
     "destination": [
      "sum8",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p18",
      0
     ],
     "destination": [
      "sum8",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p17",
      0
     ],
     "destination": [
      "side8",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p18",
      0
     ],
     "destination": [
      "side8",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side8",
      0
     ],
     "destination": [
      "sideav8",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav8",
      0
     ],
     "destination": [
      "sidesn8",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn8",
      0
     ],
     "destination": [
      "obj-pak8",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak8",
      0
     ],
     "destination": [
      "obj-prep8",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep8",
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
      "sum8",
      0
     ],
     "destination": [
      "bp8_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp8_0",
      0
     ],
     "destination": [
      "av8_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av8_0",
      0
     ],
     "destination": [
      "sn8_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn8_0",
      0
     ],
     "destination": [
      "obj-pak8",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum8",
      0
     ],
     "destination": [
      "bp8_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp8_1",
      0
     ],
     "destination": [
      "av8_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av8_1",
      0
     ],
     "destination": [
      "sn8_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn8_1",
      0
     ],
     "destination": [
      "obj-pak8",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum8",
      0
     ],
     "destination": [
      "bp8_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp8_2",
      0
     ],
     "destination": [
      "av8_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av8_2",
      0
     ],
     "destination": [
      "sn8_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn8_2",
      0
     ],
     "destination": [
      "obj-pak8",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum8",
      0
     ],
     "destination": [
      "bp8_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp8_3",
      0
     ],
     "destination": [
      "av8_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av8_3",
      0
     ],
     "destination": [
      "sn8_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn8_3",
      0
     ],
     "destination": [
      "obj-pak8",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum8",
      0
     ],
     "destination": [
      "bp8_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp8_4",
      0
     ],
     "destination": [
      "av8_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av8_4",
      0
     ],
     "destination": [
      "sn8_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn8_4",
      0
     ],
     "destination": [
      "obj-pak8",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum8",
      0
     ],
     "destination": [
      "bp8_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp8_5",
      0
     ],
     "destination": [
      "av8_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av8_5",
      0
     ],
     "destination": [
      "sn8_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn8_5",
      0
     ],
     "destination": [
      "obj-pak8",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum8",
      0
     ],
     "destination": [
      "bp8_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp8_6",
      0
     ],
     "destination": [
      "av8_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av8_6",
      0
     ],
     "destination": [
      "sn8_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn8_6",
      0
     ],
     "destination": [
      "obj-pak8",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p19",
      0
     ],
     "destination": [
      "sum9",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p20",
      0
     ],
     "destination": [
      "sum9",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p19",
      0
     ],
     "destination": [
      "side9",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p20",
      0
     ],
     "destination": [
      "side9",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side9",
      0
     ],
     "destination": [
      "sideav9",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav9",
      0
     ],
     "destination": [
      "sidesn9",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn9",
      0
     ],
     "destination": [
      "obj-pak9",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak9",
      0
     ],
     "destination": [
      "obj-prep9",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep9",
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
      "sum9",
      0
     ],
     "destination": [
      "bp9_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp9_0",
      0
     ],
     "destination": [
      "av9_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av9_0",
      0
     ],
     "destination": [
      "sn9_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn9_0",
      0
     ],
     "destination": [
      "obj-pak9",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum9",
      0
     ],
     "destination": [
      "bp9_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp9_1",
      0
     ],
     "destination": [
      "av9_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av9_1",
      0
     ],
     "destination": [
      "sn9_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn9_1",
      0
     ],
     "destination": [
      "obj-pak9",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum9",
      0
     ],
     "destination": [
      "bp9_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp9_2",
      0
     ],
     "destination": [
      "av9_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av9_2",
      0
     ],
     "destination": [
      "sn9_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn9_2",
      0
     ],
     "destination": [
      "obj-pak9",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum9",
      0
     ],
     "destination": [
      "bp9_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp9_3",
      0
     ],
     "destination": [
      "av9_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av9_3",
      0
     ],
     "destination": [
      "sn9_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn9_3",
      0
     ],
     "destination": [
      "obj-pak9",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum9",
      0
     ],
     "destination": [
      "bp9_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp9_4",
      0
     ],
     "destination": [
      "av9_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av9_4",
      0
     ],
     "destination": [
      "sn9_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn9_4",
      0
     ],
     "destination": [
      "obj-pak9",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum9",
      0
     ],
     "destination": [
      "bp9_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp9_5",
      0
     ],
     "destination": [
      "av9_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av9_5",
      0
     ],
     "destination": [
      "sn9_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn9_5",
      0
     ],
     "destination": [
      "obj-pak9",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum9",
      0
     ],
     "destination": [
      "bp9_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp9_6",
      0
     ],
     "destination": [
      "av9_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av9_6",
      0
     ],
     "destination": [
      "sn9_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn9_6",
      0
     ],
     "destination": [
      "obj-pak9",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p21",
      0
     ],
     "destination": [
      "sum10",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p22",
      0
     ],
     "destination": [
      "sum10",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p21",
      0
     ],
     "destination": [
      "side10",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p22",
      0
     ],
     "destination": [
      "side10",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side10",
      0
     ],
     "destination": [
      "sideav10",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav10",
      0
     ],
     "destination": [
      "sidesn10",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn10",
      0
     ],
     "destination": [
      "obj-pak10",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak10",
      0
     ],
     "destination": [
      "obj-prep10",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep10",
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
      "sum10",
      0
     ],
     "destination": [
      "bp10_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp10_0",
      0
     ],
     "destination": [
      "av10_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av10_0",
      0
     ],
     "destination": [
      "sn10_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn10_0",
      0
     ],
     "destination": [
      "obj-pak10",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum10",
      0
     ],
     "destination": [
      "bp10_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp10_1",
      0
     ],
     "destination": [
      "av10_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av10_1",
      0
     ],
     "destination": [
      "sn10_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn10_1",
      0
     ],
     "destination": [
      "obj-pak10",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum10",
      0
     ],
     "destination": [
      "bp10_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp10_2",
      0
     ],
     "destination": [
      "av10_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av10_2",
      0
     ],
     "destination": [
      "sn10_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn10_2",
      0
     ],
     "destination": [
      "obj-pak10",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum10",
      0
     ],
     "destination": [
      "bp10_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp10_3",
      0
     ],
     "destination": [
      "av10_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av10_3",
      0
     ],
     "destination": [
      "sn10_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn10_3",
      0
     ],
     "destination": [
      "obj-pak10",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum10",
      0
     ],
     "destination": [
      "bp10_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp10_4",
      0
     ],
     "destination": [
      "av10_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av10_4",
      0
     ],
     "destination": [
      "sn10_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn10_4",
      0
     ],
     "destination": [
      "obj-pak10",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum10",
      0
     ],
     "destination": [
      "bp10_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp10_5",
      0
     ],
     "destination": [
      "av10_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av10_5",
      0
     ],
     "destination": [
      "sn10_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn10_5",
      0
     ],
     "destination": [
      "obj-pak10",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum10",
      0
     ],
     "destination": [
      "bp10_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp10_6",
      0
     ],
     "destination": [
      "av10_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av10_6",
      0
     ],
     "destination": [
      "sn10_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn10_6",
      0
     ],
     "destination": [
      "obj-pak10",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p23",
      0
     ],
     "destination": [
      "sum11",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p24",
      0
     ],
     "destination": [
      "sum11",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p23",
      0
     ],
     "destination": [
      "side11",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p24",
      0
     ],
     "destination": [
      "side11",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side11",
      0
     ],
     "destination": [
      "sideav11",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav11",
      0
     ],
     "destination": [
      "sidesn11",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn11",
      0
     ],
     "destination": [
      "obj-pak11",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak11",
      0
     ],
     "destination": [
      "obj-prep11",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep11",
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
      "sum11",
      0
     ],
     "destination": [
      "bp11_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp11_0",
      0
     ],
     "destination": [
      "av11_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av11_0",
      0
     ],
     "destination": [
      "sn11_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn11_0",
      0
     ],
     "destination": [
      "obj-pak11",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum11",
      0
     ],
     "destination": [
      "bp11_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp11_1",
      0
     ],
     "destination": [
      "av11_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av11_1",
      0
     ],
     "destination": [
      "sn11_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn11_1",
      0
     ],
     "destination": [
      "obj-pak11",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum11",
      0
     ],
     "destination": [
      "bp11_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp11_2",
      0
     ],
     "destination": [
      "av11_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av11_2",
      0
     ],
     "destination": [
      "sn11_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn11_2",
      0
     ],
     "destination": [
      "obj-pak11",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum11",
      0
     ],
     "destination": [
      "bp11_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp11_3",
      0
     ],
     "destination": [
      "av11_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av11_3",
      0
     ],
     "destination": [
      "sn11_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn11_3",
      0
     ],
     "destination": [
      "obj-pak11",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum11",
      0
     ],
     "destination": [
      "bp11_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp11_4",
      0
     ],
     "destination": [
      "av11_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av11_4",
      0
     ],
     "destination": [
      "sn11_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn11_4",
      0
     ],
     "destination": [
      "obj-pak11",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum11",
      0
     ],
     "destination": [
      "bp11_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp11_5",
      0
     ],
     "destination": [
      "av11_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av11_5",
      0
     ],
     "destination": [
      "sn11_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn11_5",
      0
     ],
     "destination": [
      "obj-pak11",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum11",
      0
     ],
     "destination": [
      "bp11_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp11_6",
      0
     ],
     "destination": [
      "av11_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av11_6",
      0
     ],
     "destination": [
      "sn11_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn11_6",
      0
     ],
     "destination": [
      "obj-pak11",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p25",
      0
     ],
     "destination": [
      "sum12",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p26",
      0
     ],
     "destination": [
      "sum12",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p25",
      0
     ],
     "destination": [
      "side12",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p26",
      0
     ],
     "destination": [
      "side12",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side12",
      0
     ],
     "destination": [
      "sideav12",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav12",
      0
     ],
     "destination": [
      "sidesn12",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn12",
      0
     ],
     "destination": [
      "obj-pak12",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak12",
      0
     ],
     "destination": [
      "obj-prep12",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep12",
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
      "sum12",
      0
     ],
     "destination": [
      "bp12_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp12_0",
      0
     ],
     "destination": [
      "av12_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av12_0",
      0
     ],
     "destination": [
      "sn12_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn12_0",
      0
     ],
     "destination": [
      "obj-pak12",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum12",
      0
     ],
     "destination": [
      "bp12_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp12_1",
      0
     ],
     "destination": [
      "av12_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av12_1",
      0
     ],
     "destination": [
      "sn12_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn12_1",
      0
     ],
     "destination": [
      "obj-pak12",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum12",
      0
     ],
     "destination": [
      "bp12_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp12_2",
      0
     ],
     "destination": [
      "av12_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av12_2",
      0
     ],
     "destination": [
      "sn12_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn12_2",
      0
     ],
     "destination": [
      "obj-pak12",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum12",
      0
     ],
     "destination": [
      "bp12_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp12_3",
      0
     ],
     "destination": [
      "av12_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av12_3",
      0
     ],
     "destination": [
      "sn12_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn12_3",
      0
     ],
     "destination": [
      "obj-pak12",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum12",
      0
     ],
     "destination": [
      "bp12_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp12_4",
      0
     ],
     "destination": [
      "av12_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av12_4",
      0
     ],
     "destination": [
      "sn12_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn12_4",
      0
     ],
     "destination": [
      "obj-pak12",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum12",
      0
     ],
     "destination": [
      "bp12_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp12_5",
      0
     ],
     "destination": [
      "av12_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av12_5",
      0
     ],
     "destination": [
      "sn12_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn12_5",
      0
     ],
     "destination": [
      "obj-pak12",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum12",
      0
     ],
     "destination": [
      "bp12_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp12_6",
      0
     ],
     "destination": [
      "av12_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av12_6",
      0
     ],
     "destination": [
      "sn12_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn12_6",
      0
     ],
     "destination": [
      "obj-pak12",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p27",
      0
     ],
     "destination": [
      "sum13",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p28",
      0
     ],
     "destination": [
      "sum13",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p27",
      0
     ],
     "destination": [
      "side13",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p28",
      0
     ],
     "destination": [
      "side13",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side13",
      0
     ],
     "destination": [
      "sideav13",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav13",
      0
     ],
     "destination": [
      "sidesn13",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn13",
      0
     ],
     "destination": [
      "obj-pak13",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak13",
      0
     ],
     "destination": [
      "obj-prep13",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep13",
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
      "sum13",
      0
     ],
     "destination": [
      "bp13_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp13_0",
      0
     ],
     "destination": [
      "av13_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av13_0",
      0
     ],
     "destination": [
      "sn13_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn13_0",
      0
     ],
     "destination": [
      "obj-pak13",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum13",
      0
     ],
     "destination": [
      "bp13_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp13_1",
      0
     ],
     "destination": [
      "av13_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av13_1",
      0
     ],
     "destination": [
      "sn13_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn13_1",
      0
     ],
     "destination": [
      "obj-pak13",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum13",
      0
     ],
     "destination": [
      "bp13_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp13_2",
      0
     ],
     "destination": [
      "av13_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av13_2",
      0
     ],
     "destination": [
      "sn13_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn13_2",
      0
     ],
     "destination": [
      "obj-pak13",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum13",
      0
     ],
     "destination": [
      "bp13_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp13_3",
      0
     ],
     "destination": [
      "av13_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av13_3",
      0
     ],
     "destination": [
      "sn13_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn13_3",
      0
     ],
     "destination": [
      "obj-pak13",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum13",
      0
     ],
     "destination": [
      "bp13_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp13_4",
      0
     ],
     "destination": [
      "av13_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av13_4",
      0
     ],
     "destination": [
      "sn13_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn13_4",
      0
     ],
     "destination": [
      "obj-pak13",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum13",
      0
     ],
     "destination": [
      "bp13_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp13_5",
      0
     ],
     "destination": [
      "av13_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av13_5",
      0
     ],
     "destination": [
      "sn13_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn13_5",
      0
     ],
     "destination": [
      "obj-pak13",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum13",
      0
     ],
     "destination": [
      "bp13_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp13_6",
      0
     ],
     "destination": [
      "av13_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av13_6",
      0
     ],
     "destination": [
      "sn13_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn13_6",
      0
     ],
     "destination": [
      "obj-pak13",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p29",
      0
     ],
     "destination": [
      "sum14",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p30",
      0
     ],
     "destination": [
      "sum14",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p29",
      0
     ],
     "destination": [
      "side14",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p30",
      0
     ],
     "destination": [
      "side14",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side14",
      0
     ],
     "destination": [
      "sideav14",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav14",
      0
     ],
     "destination": [
      "sidesn14",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn14",
      0
     ],
     "destination": [
      "obj-pak14",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak14",
      0
     ],
     "destination": [
      "obj-prep14",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep14",
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
      "sum14",
      0
     ],
     "destination": [
      "bp14_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp14_0",
      0
     ],
     "destination": [
      "av14_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av14_0",
      0
     ],
     "destination": [
      "sn14_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn14_0",
      0
     ],
     "destination": [
      "obj-pak14",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum14",
      0
     ],
     "destination": [
      "bp14_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp14_1",
      0
     ],
     "destination": [
      "av14_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av14_1",
      0
     ],
     "destination": [
      "sn14_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn14_1",
      0
     ],
     "destination": [
      "obj-pak14",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum14",
      0
     ],
     "destination": [
      "bp14_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp14_2",
      0
     ],
     "destination": [
      "av14_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av14_2",
      0
     ],
     "destination": [
      "sn14_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn14_2",
      0
     ],
     "destination": [
      "obj-pak14",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum14",
      0
     ],
     "destination": [
      "bp14_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp14_3",
      0
     ],
     "destination": [
      "av14_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av14_3",
      0
     ],
     "destination": [
      "sn14_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn14_3",
      0
     ],
     "destination": [
      "obj-pak14",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum14",
      0
     ],
     "destination": [
      "bp14_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp14_4",
      0
     ],
     "destination": [
      "av14_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av14_4",
      0
     ],
     "destination": [
      "sn14_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn14_4",
      0
     ],
     "destination": [
      "obj-pak14",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum14",
      0
     ],
     "destination": [
      "bp14_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp14_5",
      0
     ],
     "destination": [
      "av14_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av14_5",
      0
     ],
     "destination": [
      "sn14_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn14_5",
      0
     ],
     "destination": [
      "obj-pak14",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum14",
      0
     ],
     "destination": [
      "bp14_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp14_6",
      0
     ],
     "destination": [
      "av14_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av14_6",
      0
     ],
     "destination": [
      "sn14_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn14_6",
      0
     ],
     "destination": [
      "obj-pak14",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p31",
      0
     ],
     "destination": [
      "sum15",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p32",
      0
     ],
     "destination": [
      "sum15",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p31",
      0
     ],
     "destination": [
      "side15",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p32",
      0
     ],
     "destination": [
      "side15",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side15",
      0
     ],
     "destination": [
      "sideav15",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav15",
      0
     ],
     "destination": [
      "sidesn15",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn15",
      0
     ],
     "destination": [
      "obj-pak15",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak15",
      0
     ],
     "destination": [
      "obj-prep15",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep15",
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
      "sum15",
      0
     ],
     "destination": [
      "bp15_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp15_0",
      0
     ],
     "destination": [
      "av15_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av15_0",
      0
     ],
     "destination": [
      "sn15_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn15_0",
      0
     ],
     "destination": [
      "obj-pak15",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum15",
      0
     ],
     "destination": [
      "bp15_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp15_1",
      0
     ],
     "destination": [
      "av15_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av15_1",
      0
     ],
     "destination": [
      "sn15_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn15_1",
      0
     ],
     "destination": [
      "obj-pak15",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum15",
      0
     ],
     "destination": [
      "bp15_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp15_2",
      0
     ],
     "destination": [
      "av15_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av15_2",
      0
     ],
     "destination": [
      "sn15_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn15_2",
      0
     ],
     "destination": [
      "obj-pak15",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum15",
      0
     ],
     "destination": [
      "bp15_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp15_3",
      0
     ],
     "destination": [
      "av15_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av15_3",
      0
     ],
     "destination": [
      "sn15_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn15_3",
      0
     ],
     "destination": [
      "obj-pak15",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum15",
      0
     ],
     "destination": [
      "bp15_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp15_4",
      0
     ],
     "destination": [
      "av15_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av15_4",
      0
     ],
     "destination": [
      "sn15_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn15_4",
      0
     ],
     "destination": [
      "obj-pak15",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum15",
      0
     ],
     "destination": [
      "bp15_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp15_5",
      0
     ],
     "destination": [
      "av15_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av15_5",
      0
     ],
     "destination": [
      "sn15_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn15_5",
      0
     ],
     "destination": [
      "obj-pak15",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum15",
      0
     ],
     "destination": [
      "bp15_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp15_6",
      0
     ],
     "destination": [
      "av15_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av15_6",
      0
     ],
     "destination": [
      "sn15_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn15_6",
      0
     ],
     "destination": [
      "obj-pak15",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p33",
      0
     ],
     "destination": [
      "sum16",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p34",
      0
     ],
     "destination": [
      "sum16",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p33",
      0
     ],
     "destination": [
      "side16",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p34",
      0
     ],
     "destination": [
      "side16",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side16",
      0
     ],
     "destination": [
      "sideav16",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav16",
      0
     ],
     "destination": [
      "sidesn16",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn16",
      0
     ],
     "destination": [
      "obj-pak16",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak16",
      0
     ],
     "destination": [
      "obj-prep16",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep16",
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
      "sum16",
      0
     ],
     "destination": [
      "bp16_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp16_0",
      0
     ],
     "destination": [
      "av16_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av16_0",
      0
     ],
     "destination": [
      "sn16_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn16_0",
      0
     ],
     "destination": [
      "obj-pak16",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum16",
      0
     ],
     "destination": [
      "bp16_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp16_1",
      0
     ],
     "destination": [
      "av16_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av16_1",
      0
     ],
     "destination": [
      "sn16_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn16_1",
      0
     ],
     "destination": [
      "obj-pak16",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum16",
      0
     ],
     "destination": [
      "bp16_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp16_2",
      0
     ],
     "destination": [
      "av16_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av16_2",
      0
     ],
     "destination": [
      "sn16_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn16_2",
      0
     ],
     "destination": [
      "obj-pak16",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum16",
      0
     ],
     "destination": [
      "bp16_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp16_3",
      0
     ],
     "destination": [
      "av16_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av16_3",
      0
     ],
     "destination": [
      "sn16_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn16_3",
      0
     ],
     "destination": [
      "obj-pak16",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum16",
      0
     ],
     "destination": [
      "bp16_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp16_4",
      0
     ],
     "destination": [
      "av16_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av16_4",
      0
     ],
     "destination": [
      "sn16_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn16_4",
      0
     ],
     "destination": [
      "obj-pak16",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum16",
      0
     ],
     "destination": [
      "bp16_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp16_5",
      0
     ],
     "destination": [
      "av16_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av16_5",
      0
     ],
     "destination": [
      "sn16_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn16_5",
      0
     ],
     "destination": [
      "obj-pak16",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum16",
      0
     ],
     "destination": [
      "bp16_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp16_6",
      0
     ],
     "destination": [
      "av16_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av16_6",
      0
     ],
     "destination": [
      "sn16_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn16_6",
      0
     ],
     "destination": [
      "obj-pak16",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p35",
      0
     ],
     "destination": [
      "sum17",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p36",
      0
     ],
     "destination": [
      "sum17",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p35",
      0
     ],
     "destination": [
      "side17",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p36",
      0
     ],
     "destination": [
      "side17",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side17",
      0
     ],
     "destination": [
      "sideav17",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav17",
      0
     ],
     "destination": [
      "sidesn17",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn17",
      0
     ],
     "destination": [
      "obj-pak17",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak17",
      0
     ],
     "destination": [
      "obj-prep17",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep17",
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
      "sum17",
      0
     ],
     "destination": [
      "bp17_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp17_0",
      0
     ],
     "destination": [
      "av17_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av17_0",
      0
     ],
     "destination": [
      "sn17_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn17_0",
      0
     ],
     "destination": [
      "obj-pak17",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum17",
      0
     ],
     "destination": [
      "bp17_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp17_1",
      0
     ],
     "destination": [
      "av17_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av17_1",
      0
     ],
     "destination": [
      "sn17_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn17_1",
      0
     ],
     "destination": [
      "obj-pak17",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum17",
      0
     ],
     "destination": [
      "bp17_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp17_2",
      0
     ],
     "destination": [
      "av17_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av17_2",
      0
     ],
     "destination": [
      "sn17_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn17_2",
      0
     ],
     "destination": [
      "obj-pak17",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum17",
      0
     ],
     "destination": [
      "bp17_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp17_3",
      0
     ],
     "destination": [
      "av17_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av17_3",
      0
     ],
     "destination": [
      "sn17_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn17_3",
      0
     ],
     "destination": [
      "obj-pak17",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum17",
      0
     ],
     "destination": [
      "bp17_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp17_4",
      0
     ],
     "destination": [
      "av17_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av17_4",
      0
     ],
     "destination": [
      "sn17_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn17_4",
      0
     ],
     "destination": [
      "obj-pak17",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum17",
      0
     ],
     "destination": [
      "bp17_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp17_5",
      0
     ],
     "destination": [
      "av17_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av17_5",
      0
     ],
     "destination": [
      "sn17_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn17_5",
      0
     ],
     "destination": [
      "obj-pak17",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum17",
      0
     ],
     "destination": [
      "bp17_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp17_6",
      0
     ],
     "destination": [
      "av17_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av17_6",
      0
     ],
     "destination": [
      "sn17_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn17_6",
      0
     ],
     "destination": [
      "obj-pak17",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p37",
      0
     ],
     "destination": [
      "sum18",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p38",
      0
     ],
     "destination": [
      "sum18",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p37",
      0
     ],
     "destination": [
      "side18",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p38",
      0
     ],
     "destination": [
      "side18",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side18",
      0
     ],
     "destination": [
      "sideav18",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav18",
      0
     ],
     "destination": [
      "sidesn18",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn18",
      0
     ],
     "destination": [
      "obj-pak18",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak18",
      0
     ],
     "destination": [
      "obj-prep18",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep18",
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
      "sum18",
      0
     ],
     "destination": [
      "bp18_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp18_0",
      0
     ],
     "destination": [
      "av18_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av18_0",
      0
     ],
     "destination": [
      "sn18_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn18_0",
      0
     ],
     "destination": [
      "obj-pak18",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum18",
      0
     ],
     "destination": [
      "bp18_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp18_1",
      0
     ],
     "destination": [
      "av18_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av18_1",
      0
     ],
     "destination": [
      "sn18_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn18_1",
      0
     ],
     "destination": [
      "obj-pak18",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum18",
      0
     ],
     "destination": [
      "bp18_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp18_2",
      0
     ],
     "destination": [
      "av18_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av18_2",
      0
     ],
     "destination": [
      "sn18_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn18_2",
      0
     ],
     "destination": [
      "obj-pak18",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum18",
      0
     ],
     "destination": [
      "bp18_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp18_3",
      0
     ],
     "destination": [
      "av18_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av18_3",
      0
     ],
     "destination": [
      "sn18_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn18_3",
      0
     ],
     "destination": [
      "obj-pak18",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum18",
      0
     ],
     "destination": [
      "bp18_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp18_4",
      0
     ],
     "destination": [
      "av18_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av18_4",
      0
     ],
     "destination": [
      "sn18_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn18_4",
      0
     ],
     "destination": [
      "obj-pak18",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum18",
      0
     ],
     "destination": [
      "bp18_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp18_5",
      0
     ],
     "destination": [
      "av18_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av18_5",
      0
     ],
     "destination": [
      "sn18_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn18_5",
      0
     ],
     "destination": [
      "obj-pak18",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum18",
      0
     ],
     "destination": [
      "bp18_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp18_6",
      0
     ],
     "destination": [
      "av18_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av18_6",
      0
     ],
     "destination": [
      "sn18_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn18_6",
      0
     ],
     "destination": [
      "obj-pak18",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p39",
      0
     ],
     "destination": [
      "sum19",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p40",
      0
     ],
     "destination": [
      "sum19",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p39",
      0
     ],
     "destination": [
      "side19",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p40",
      0
     ],
     "destination": [
      "side19",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side19",
      0
     ],
     "destination": [
      "sideav19",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav19",
      0
     ],
     "destination": [
      "sidesn19",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn19",
      0
     ],
     "destination": [
      "obj-pak19",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak19",
      0
     ],
     "destination": [
      "obj-prep19",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep19",
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
      "sum19",
      0
     ],
     "destination": [
      "bp19_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp19_0",
      0
     ],
     "destination": [
      "av19_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av19_0",
      0
     ],
     "destination": [
      "sn19_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn19_0",
      0
     ],
     "destination": [
      "obj-pak19",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum19",
      0
     ],
     "destination": [
      "bp19_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp19_1",
      0
     ],
     "destination": [
      "av19_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av19_1",
      0
     ],
     "destination": [
      "sn19_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn19_1",
      0
     ],
     "destination": [
      "obj-pak19",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum19",
      0
     ],
     "destination": [
      "bp19_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp19_2",
      0
     ],
     "destination": [
      "av19_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av19_2",
      0
     ],
     "destination": [
      "sn19_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn19_2",
      0
     ],
     "destination": [
      "obj-pak19",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum19",
      0
     ],
     "destination": [
      "bp19_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp19_3",
      0
     ],
     "destination": [
      "av19_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av19_3",
      0
     ],
     "destination": [
      "sn19_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn19_3",
      0
     ],
     "destination": [
      "obj-pak19",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum19",
      0
     ],
     "destination": [
      "bp19_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp19_4",
      0
     ],
     "destination": [
      "av19_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av19_4",
      0
     ],
     "destination": [
      "sn19_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn19_4",
      0
     ],
     "destination": [
      "obj-pak19",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum19",
      0
     ],
     "destination": [
      "bp19_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp19_5",
      0
     ],
     "destination": [
      "av19_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av19_5",
      0
     ],
     "destination": [
      "sn19_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn19_5",
      0
     ],
     "destination": [
      "obj-pak19",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum19",
      0
     ],
     "destination": [
      "bp19_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp19_6",
      0
     ],
     "destination": [
      "av19_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av19_6",
      0
     ],
     "destination": [
      "sn19_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn19_6",
      0
     ],
     "destination": [
      "obj-pak19",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p41",
      0
     ],
     "destination": [
      "sum20",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p42",
      0
     ],
     "destination": [
      "sum20",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p41",
      0
     ],
     "destination": [
      "side20",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p42",
      0
     ],
     "destination": [
      "side20",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side20",
      0
     ],
     "destination": [
      "sideav20",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav20",
      0
     ],
     "destination": [
      "sidesn20",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn20",
      0
     ],
     "destination": [
      "obj-pak20",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak20",
      0
     ],
     "destination": [
      "obj-prep20",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep20",
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
      "sum20",
      0
     ],
     "destination": [
      "bp20_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp20_0",
      0
     ],
     "destination": [
      "av20_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av20_0",
      0
     ],
     "destination": [
      "sn20_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn20_0",
      0
     ],
     "destination": [
      "obj-pak20",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum20",
      0
     ],
     "destination": [
      "bp20_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp20_1",
      0
     ],
     "destination": [
      "av20_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av20_1",
      0
     ],
     "destination": [
      "sn20_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn20_1",
      0
     ],
     "destination": [
      "obj-pak20",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum20",
      0
     ],
     "destination": [
      "bp20_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp20_2",
      0
     ],
     "destination": [
      "av20_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av20_2",
      0
     ],
     "destination": [
      "sn20_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn20_2",
      0
     ],
     "destination": [
      "obj-pak20",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum20",
      0
     ],
     "destination": [
      "bp20_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp20_3",
      0
     ],
     "destination": [
      "av20_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av20_3",
      0
     ],
     "destination": [
      "sn20_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn20_3",
      0
     ],
     "destination": [
      "obj-pak20",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum20",
      0
     ],
     "destination": [
      "bp20_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp20_4",
      0
     ],
     "destination": [
      "av20_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av20_4",
      0
     ],
     "destination": [
      "sn20_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn20_4",
      0
     ],
     "destination": [
      "obj-pak20",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum20",
      0
     ],
     "destination": [
      "bp20_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp20_5",
      0
     ],
     "destination": [
      "av20_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av20_5",
      0
     ],
     "destination": [
      "sn20_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn20_5",
      0
     ],
     "destination": [
      "obj-pak20",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum20",
      0
     ],
     "destination": [
      "bp20_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp20_6",
      0
     ],
     "destination": [
      "av20_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av20_6",
      0
     ],
     "destination": [
      "sn20_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn20_6",
      0
     ],
     "destination": [
      "obj-pak20",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p43",
      0
     ],
     "destination": [
      "sum21",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p44",
      0
     ],
     "destination": [
      "sum21",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p43",
      0
     ],
     "destination": [
      "side21",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p44",
      0
     ],
     "destination": [
      "side21",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side21",
      0
     ],
     "destination": [
      "sideav21",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav21",
      0
     ],
     "destination": [
      "sidesn21",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn21",
      0
     ],
     "destination": [
      "obj-pak21",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak21",
      0
     ],
     "destination": [
      "obj-prep21",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep21",
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
      "sum21",
      0
     ],
     "destination": [
      "bp21_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp21_0",
      0
     ],
     "destination": [
      "av21_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av21_0",
      0
     ],
     "destination": [
      "sn21_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn21_0",
      0
     ],
     "destination": [
      "obj-pak21",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum21",
      0
     ],
     "destination": [
      "bp21_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp21_1",
      0
     ],
     "destination": [
      "av21_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av21_1",
      0
     ],
     "destination": [
      "sn21_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn21_1",
      0
     ],
     "destination": [
      "obj-pak21",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum21",
      0
     ],
     "destination": [
      "bp21_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp21_2",
      0
     ],
     "destination": [
      "av21_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av21_2",
      0
     ],
     "destination": [
      "sn21_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn21_2",
      0
     ],
     "destination": [
      "obj-pak21",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum21",
      0
     ],
     "destination": [
      "bp21_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp21_3",
      0
     ],
     "destination": [
      "av21_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av21_3",
      0
     ],
     "destination": [
      "sn21_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn21_3",
      0
     ],
     "destination": [
      "obj-pak21",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum21",
      0
     ],
     "destination": [
      "bp21_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp21_4",
      0
     ],
     "destination": [
      "av21_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av21_4",
      0
     ],
     "destination": [
      "sn21_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn21_4",
      0
     ],
     "destination": [
      "obj-pak21",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum21",
      0
     ],
     "destination": [
      "bp21_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp21_5",
      0
     ],
     "destination": [
      "av21_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av21_5",
      0
     ],
     "destination": [
      "sn21_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn21_5",
      0
     ],
     "destination": [
      "obj-pak21",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum21",
      0
     ],
     "destination": [
      "bp21_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp21_6",
      0
     ],
     "destination": [
      "av21_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av21_6",
      0
     ],
     "destination": [
      "sn21_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn21_6",
      0
     ],
     "destination": [
      "obj-pak21",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p45",
      0
     ],
     "destination": [
      "sum22",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p46",
      0
     ],
     "destination": [
      "sum22",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p45",
      0
     ],
     "destination": [
      "side22",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p46",
      0
     ],
     "destination": [
      "side22",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side22",
      0
     ],
     "destination": [
      "sideav22",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav22",
      0
     ],
     "destination": [
      "sidesn22",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn22",
      0
     ],
     "destination": [
      "obj-pak22",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak22",
      0
     ],
     "destination": [
      "obj-prep22",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep22",
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
      "sum22",
      0
     ],
     "destination": [
      "bp22_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp22_0",
      0
     ],
     "destination": [
      "av22_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av22_0",
      0
     ],
     "destination": [
      "sn22_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn22_0",
      0
     ],
     "destination": [
      "obj-pak22",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum22",
      0
     ],
     "destination": [
      "bp22_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp22_1",
      0
     ],
     "destination": [
      "av22_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av22_1",
      0
     ],
     "destination": [
      "sn22_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn22_1",
      0
     ],
     "destination": [
      "obj-pak22",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum22",
      0
     ],
     "destination": [
      "bp22_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp22_2",
      0
     ],
     "destination": [
      "av22_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av22_2",
      0
     ],
     "destination": [
      "sn22_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn22_2",
      0
     ],
     "destination": [
      "obj-pak22",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum22",
      0
     ],
     "destination": [
      "bp22_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp22_3",
      0
     ],
     "destination": [
      "av22_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av22_3",
      0
     ],
     "destination": [
      "sn22_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn22_3",
      0
     ],
     "destination": [
      "obj-pak22",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum22",
      0
     ],
     "destination": [
      "bp22_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp22_4",
      0
     ],
     "destination": [
      "av22_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av22_4",
      0
     ],
     "destination": [
      "sn22_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn22_4",
      0
     ],
     "destination": [
      "obj-pak22",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum22",
      0
     ],
     "destination": [
      "bp22_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp22_5",
      0
     ],
     "destination": [
      "av22_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av22_5",
      0
     ],
     "destination": [
      "sn22_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn22_5",
      0
     ],
     "destination": [
      "obj-pak22",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum22",
      0
     ],
     "destination": [
      "bp22_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp22_6",
      0
     ],
     "destination": [
      "av22_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av22_6",
      0
     ],
     "destination": [
      "sn22_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn22_6",
      0
     ],
     "destination": [
      "obj-pak22",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p47",
      0
     ],
     "destination": [
      "sum23",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p48",
      0
     ],
     "destination": [
      "sum23",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p47",
      0
     ],
     "destination": [
      "side23",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p48",
      0
     ],
     "destination": [
      "side23",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side23",
      0
     ],
     "destination": [
      "sideav23",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav23",
      0
     ],
     "destination": [
      "sidesn23",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn23",
      0
     ],
     "destination": [
      "obj-pak23",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak23",
      0
     ],
     "destination": [
      "obj-prep23",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep23",
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
      "sum23",
      0
     ],
     "destination": [
      "bp23_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp23_0",
      0
     ],
     "destination": [
      "av23_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av23_0",
      0
     ],
     "destination": [
      "sn23_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn23_0",
      0
     ],
     "destination": [
      "obj-pak23",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum23",
      0
     ],
     "destination": [
      "bp23_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp23_1",
      0
     ],
     "destination": [
      "av23_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av23_1",
      0
     ],
     "destination": [
      "sn23_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn23_1",
      0
     ],
     "destination": [
      "obj-pak23",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum23",
      0
     ],
     "destination": [
      "bp23_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp23_2",
      0
     ],
     "destination": [
      "av23_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av23_2",
      0
     ],
     "destination": [
      "sn23_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn23_2",
      0
     ],
     "destination": [
      "obj-pak23",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum23",
      0
     ],
     "destination": [
      "bp23_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp23_3",
      0
     ],
     "destination": [
      "av23_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av23_3",
      0
     ],
     "destination": [
      "sn23_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn23_3",
      0
     ],
     "destination": [
      "obj-pak23",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum23",
      0
     ],
     "destination": [
      "bp23_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp23_4",
      0
     ],
     "destination": [
      "av23_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av23_4",
      0
     ],
     "destination": [
      "sn23_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn23_4",
      0
     ],
     "destination": [
      "obj-pak23",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum23",
      0
     ],
     "destination": [
      "bp23_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp23_5",
      0
     ],
     "destination": [
      "av23_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av23_5",
      0
     ],
     "destination": [
      "sn23_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn23_5",
      0
     ],
     "destination": [
      "obj-pak23",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum23",
      0
     ],
     "destination": [
      "bp23_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp23_6",
      0
     ],
     "destination": [
      "av23_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av23_6",
      0
     ],
     "destination": [
      "sn23_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn23_6",
      0
     ],
     "destination": [
      "obj-pak23",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p49",
      0
     ],
     "destination": [
      "sum24",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p50",
      0
     ],
     "destination": [
      "sum24",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p49",
      0
     ],
     "destination": [
      "side24",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p50",
      0
     ],
     "destination": [
      "side24",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side24",
      0
     ],
     "destination": [
      "sideav24",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav24",
      0
     ],
     "destination": [
      "sidesn24",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn24",
      0
     ],
     "destination": [
      "obj-pak24",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak24",
      0
     ],
     "destination": [
      "obj-prep24",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep24",
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
      "sum24",
      0
     ],
     "destination": [
      "bp24_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp24_0",
      0
     ],
     "destination": [
      "av24_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av24_0",
      0
     ],
     "destination": [
      "sn24_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn24_0",
      0
     ],
     "destination": [
      "obj-pak24",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum24",
      0
     ],
     "destination": [
      "bp24_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp24_1",
      0
     ],
     "destination": [
      "av24_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av24_1",
      0
     ],
     "destination": [
      "sn24_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn24_1",
      0
     ],
     "destination": [
      "obj-pak24",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum24",
      0
     ],
     "destination": [
      "bp24_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp24_2",
      0
     ],
     "destination": [
      "av24_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av24_2",
      0
     ],
     "destination": [
      "sn24_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn24_2",
      0
     ],
     "destination": [
      "obj-pak24",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum24",
      0
     ],
     "destination": [
      "bp24_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp24_3",
      0
     ],
     "destination": [
      "av24_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av24_3",
      0
     ],
     "destination": [
      "sn24_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn24_3",
      0
     ],
     "destination": [
      "obj-pak24",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum24",
      0
     ],
     "destination": [
      "bp24_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp24_4",
      0
     ],
     "destination": [
      "av24_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av24_4",
      0
     ],
     "destination": [
      "sn24_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn24_4",
      0
     ],
     "destination": [
      "obj-pak24",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum24",
      0
     ],
     "destination": [
      "bp24_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp24_5",
      0
     ],
     "destination": [
      "av24_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av24_5",
      0
     ],
     "destination": [
      "sn24_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn24_5",
      0
     ],
     "destination": [
      "obj-pak24",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum24",
      0
     ],
     "destination": [
      "bp24_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp24_6",
      0
     ],
     "destination": [
      "av24_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av24_6",
      0
     ],
     "destination": [
      "sn24_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn24_6",
      0
     ],
     "destination": [
      "obj-pak24",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p51",
      0
     ],
     "destination": [
      "sum25",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p52",
      0
     ],
     "destination": [
      "sum25",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p51",
      0
     ],
     "destination": [
      "side25",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p52",
      0
     ],
     "destination": [
      "side25",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side25",
      0
     ],
     "destination": [
      "sideav25",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav25",
      0
     ],
     "destination": [
      "sidesn25",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn25",
      0
     ],
     "destination": [
      "obj-pak25",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak25",
      0
     ],
     "destination": [
      "obj-prep25",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep25",
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
      "sum25",
      0
     ],
     "destination": [
      "bp25_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp25_0",
      0
     ],
     "destination": [
      "av25_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av25_0",
      0
     ],
     "destination": [
      "sn25_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn25_0",
      0
     ],
     "destination": [
      "obj-pak25",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum25",
      0
     ],
     "destination": [
      "bp25_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp25_1",
      0
     ],
     "destination": [
      "av25_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av25_1",
      0
     ],
     "destination": [
      "sn25_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn25_1",
      0
     ],
     "destination": [
      "obj-pak25",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum25",
      0
     ],
     "destination": [
      "bp25_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp25_2",
      0
     ],
     "destination": [
      "av25_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av25_2",
      0
     ],
     "destination": [
      "sn25_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn25_2",
      0
     ],
     "destination": [
      "obj-pak25",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum25",
      0
     ],
     "destination": [
      "bp25_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp25_3",
      0
     ],
     "destination": [
      "av25_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av25_3",
      0
     ],
     "destination": [
      "sn25_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn25_3",
      0
     ],
     "destination": [
      "obj-pak25",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum25",
      0
     ],
     "destination": [
      "bp25_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp25_4",
      0
     ],
     "destination": [
      "av25_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av25_4",
      0
     ],
     "destination": [
      "sn25_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn25_4",
      0
     ],
     "destination": [
      "obj-pak25",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum25",
      0
     ],
     "destination": [
      "bp25_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp25_5",
      0
     ],
     "destination": [
      "av25_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av25_5",
      0
     ],
     "destination": [
      "sn25_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn25_5",
      0
     ],
     "destination": [
      "obj-pak25",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum25",
      0
     ],
     "destination": [
      "bp25_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp25_6",
      0
     ],
     "destination": [
      "av25_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av25_6",
      0
     ],
     "destination": [
      "sn25_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn25_6",
      0
     ],
     "destination": [
      "obj-pak25",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p53",
      0
     ],
     "destination": [
      "sum26",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p54",
      0
     ],
     "destination": [
      "sum26",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p53",
      0
     ],
     "destination": [
      "side26",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p54",
      0
     ],
     "destination": [
      "side26",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side26",
      0
     ],
     "destination": [
      "sideav26",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav26",
      0
     ],
     "destination": [
      "sidesn26",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn26",
      0
     ],
     "destination": [
      "obj-pak26",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak26",
      0
     ],
     "destination": [
      "obj-prep26",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep26",
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
      "sum26",
      0
     ],
     "destination": [
      "bp26_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp26_0",
      0
     ],
     "destination": [
      "av26_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av26_0",
      0
     ],
     "destination": [
      "sn26_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn26_0",
      0
     ],
     "destination": [
      "obj-pak26",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum26",
      0
     ],
     "destination": [
      "bp26_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp26_1",
      0
     ],
     "destination": [
      "av26_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av26_1",
      0
     ],
     "destination": [
      "sn26_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn26_1",
      0
     ],
     "destination": [
      "obj-pak26",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum26",
      0
     ],
     "destination": [
      "bp26_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp26_2",
      0
     ],
     "destination": [
      "av26_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av26_2",
      0
     ],
     "destination": [
      "sn26_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn26_2",
      0
     ],
     "destination": [
      "obj-pak26",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum26",
      0
     ],
     "destination": [
      "bp26_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp26_3",
      0
     ],
     "destination": [
      "av26_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av26_3",
      0
     ],
     "destination": [
      "sn26_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn26_3",
      0
     ],
     "destination": [
      "obj-pak26",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum26",
      0
     ],
     "destination": [
      "bp26_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp26_4",
      0
     ],
     "destination": [
      "av26_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av26_4",
      0
     ],
     "destination": [
      "sn26_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn26_4",
      0
     ],
     "destination": [
      "obj-pak26",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum26",
      0
     ],
     "destination": [
      "bp26_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp26_5",
      0
     ],
     "destination": [
      "av26_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av26_5",
      0
     ],
     "destination": [
      "sn26_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn26_5",
      0
     ],
     "destination": [
      "obj-pak26",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum26",
      0
     ],
     "destination": [
      "bp26_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp26_6",
      0
     ],
     "destination": [
      "av26_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av26_6",
      0
     ],
     "destination": [
      "sn26_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn26_6",
      0
     ],
     "destination": [
      "obj-pak26",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p55",
      0
     ],
     "destination": [
      "sum27",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p56",
      0
     ],
     "destination": [
      "sum27",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p55",
      0
     ],
     "destination": [
      "side27",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p56",
      0
     ],
     "destination": [
      "side27",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side27",
      0
     ],
     "destination": [
      "sideav27",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav27",
      0
     ],
     "destination": [
      "sidesn27",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn27",
      0
     ],
     "destination": [
      "obj-pak27",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak27",
      0
     ],
     "destination": [
      "obj-prep27",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep27",
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
      "sum27",
      0
     ],
     "destination": [
      "bp27_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp27_0",
      0
     ],
     "destination": [
      "av27_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av27_0",
      0
     ],
     "destination": [
      "sn27_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn27_0",
      0
     ],
     "destination": [
      "obj-pak27",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum27",
      0
     ],
     "destination": [
      "bp27_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp27_1",
      0
     ],
     "destination": [
      "av27_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av27_1",
      0
     ],
     "destination": [
      "sn27_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn27_1",
      0
     ],
     "destination": [
      "obj-pak27",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum27",
      0
     ],
     "destination": [
      "bp27_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp27_2",
      0
     ],
     "destination": [
      "av27_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av27_2",
      0
     ],
     "destination": [
      "sn27_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn27_2",
      0
     ],
     "destination": [
      "obj-pak27",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum27",
      0
     ],
     "destination": [
      "bp27_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp27_3",
      0
     ],
     "destination": [
      "av27_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av27_3",
      0
     ],
     "destination": [
      "sn27_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn27_3",
      0
     ],
     "destination": [
      "obj-pak27",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum27",
      0
     ],
     "destination": [
      "bp27_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp27_4",
      0
     ],
     "destination": [
      "av27_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av27_4",
      0
     ],
     "destination": [
      "sn27_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn27_4",
      0
     ],
     "destination": [
      "obj-pak27",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum27",
      0
     ],
     "destination": [
      "bp27_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp27_5",
      0
     ],
     "destination": [
      "av27_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av27_5",
      0
     ],
     "destination": [
      "sn27_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn27_5",
      0
     ],
     "destination": [
      "obj-pak27",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum27",
      0
     ],
     "destination": [
      "bp27_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp27_6",
      0
     ],
     "destination": [
      "av27_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av27_6",
      0
     ],
     "destination": [
      "sn27_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn27_6",
      0
     ],
     "destination": [
      "obj-pak27",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p57",
      0
     ],
     "destination": [
      "sum28",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p58",
      0
     ],
     "destination": [
      "sum28",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p57",
      0
     ],
     "destination": [
      "side28",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p58",
      0
     ],
     "destination": [
      "side28",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side28",
      0
     ],
     "destination": [
      "sideav28",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav28",
      0
     ],
     "destination": [
      "sidesn28",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn28",
      0
     ],
     "destination": [
      "obj-pak28",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak28",
      0
     ],
     "destination": [
      "obj-prep28",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep28",
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
      "sum28",
      0
     ],
     "destination": [
      "bp28_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp28_0",
      0
     ],
     "destination": [
      "av28_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av28_0",
      0
     ],
     "destination": [
      "sn28_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn28_0",
      0
     ],
     "destination": [
      "obj-pak28",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum28",
      0
     ],
     "destination": [
      "bp28_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp28_1",
      0
     ],
     "destination": [
      "av28_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av28_1",
      0
     ],
     "destination": [
      "sn28_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn28_1",
      0
     ],
     "destination": [
      "obj-pak28",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum28",
      0
     ],
     "destination": [
      "bp28_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp28_2",
      0
     ],
     "destination": [
      "av28_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av28_2",
      0
     ],
     "destination": [
      "sn28_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn28_2",
      0
     ],
     "destination": [
      "obj-pak28",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum28",
      0
     ],
     "destination": [
      "bp28_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp28_3",
      0
     ],
     "destination": [
      "av28_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av28_3",
      0
     ],
     "destination": [
      "sn28_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn28_3",
      0
     ],
     "destination": [
      "obj-pak28",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum28",
      0
     ],
     "destination": [
      "bp28_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp28_4",
      0
     ],
     "destination": [
      "av28_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av28_4",
      0
     ],
     "destination": [
      "sn28_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn28_4",
      0
     ],
     "destination": [
      "obj-pak28",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum28",
      0
     ],
     "destination": [
      "bp28_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp28_5",
      0
     ],
     "destination": [
      "av28_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av28_5",
      0
     ],
     "destination": [
      "sn28_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn28_5",
      0
     ],
     "destination": [
      "obj-pak28",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum28",
      0
     ],
     "destination": [
      "bp28_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp28_6",
      0
     ],
     "destination": [
      "av28_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av28_6",
      0
     ],
     "destination": [
      "sn28_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn28_6",
      0
     ],
     "destination": [
      "obj-pak28",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p59",
      0
     ],
     "destination": [
      "sum29",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p60",
      0
     ],
     "destination": [
      "sum29",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p59",
      0
     ],
     "destination": [
      "side29",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p60",
      0
     ],
     "destination": [
      "side29",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side29",
      0
     ],
     "destination": [
      "sideav29",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav29",
      0
     ],
     "destination": [
      "sidesn29",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn29",
      0
     ],
     "destination": [
      "obj-pak29",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak29",
      0
     ],
     "destination": [
      "obj-prep29",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep29",
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
      "sum29",
      0
     ],
     "destination": [
      "bp29_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp29_0",
      0
     ],
     "destination": [
      "av29_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av29_0",
      0
     ],
     "destination": [
      "sn29_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn29_0",
      0
     ],
     "destination": [
      "obj-pak29",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum29",
      0
     ],
     "destination": [
      "bp29_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp29_1",
      0
     ],
     "destination": [
      "av29_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av29_1",
      0
     ],
     "destination": [
      "sn29_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn29_1",
      0
     ],
     "destination": [
      "obj-pak29",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum29",
      0
     ],
     "destination": [
      "bp29_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp29_2",
      0
     ],
     "destination": [
      "av29_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av29_2",
      0
     ],
     "destination": [
      "sn29_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn29_2",
      0
     ],
     "destination": [
      "obj-pak29",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum29",
      0
     ],
     "destination": [
      "bp29_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp29_3",
      0
     ],
     "destination": [
      "av29_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av29_3",
      0
     ],
     "destination": [
      "sn29_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn29_3",
      0
     ],
     "destination": [
      "obj-pak29",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum29",
      0
     ],
     "destination": [
      "bp29_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp29_4",
      0
     ],
     "destination": [
      "av29_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av29_4",
      0
     ],
     "destination": [
      "sn29_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn29_4",
      0
     ],
     "destination": [
      "obj-pak29",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum29",
      0
     ],
     "destination": [
      "bp29_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp29_5",
      0
     ],
     "destination": [
      "av29_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av29_5",
      0
     ],
     "destination": [
      "sn29_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn29_5",
      0
     ],
     "destination": [
      "obj-pak29",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum29",
      0
     ],
     "destination": [
      "bp29_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp29_6",
      0
     ],
     "destination": [
      "av29_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av29_6",
      0
     ],
     "destination": [
      "sn29_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn29_6",
      0
     ],
     "destination": [
      "obj-pak29",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p61",
      0
     ],
     "destination": [
      "sum30",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p62",
      0
     ],
     "destination": [
      "sum30",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p61",
      0
     ],
     "destination": [
      "side30",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p62",
      0
     ],
     "destination": [
      "side30",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side30",
      0
     ],
     "destination": [
      "sideav30",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav30",
      0
     ],
     "destination": [
      "sidesn30",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn30",
      0
     ],
     "destination": [
      "obj-pak30",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak30",
      0
     ],
     "destination": [
      "obj-prep30",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep30",
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
      "sum30",
      0
     ],
     "destination": [
      "bp30_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp30_0",
      0
     ],
     "destination": [
      "av30_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av30_0",
      0
     ],
     "destination": [
      "sn30_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn30_0",
      0
     ],
     "destination": [
      "obj-pak30",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum30",
      0
     ],
     "destination": [
      "bp30_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp30_1",
      0
     ],
     "destination": [
      "av30_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av30_1",
      0
     ],
     "destination": [
      "sn30_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn30_1",
      0
     ],
     "destination": [
      "obj-pak30",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum30",
      0
     ],
     "destination": [
      "bp30_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp30_2",
      0
     ],
     "destination": [
      "av30_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av30_2",
      0
     ],
     "destination": [
      "sn30_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn30_2",
      0
     ],
     "destination": [
      "obj-pak30",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum30",
      0
     ],
     "destination": [
      "bp30_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp30_3",
      0
     ],
     "destination": [
      "av30_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av30_3",
      0
     ],
     "destination": [
      "sn30_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn30_3",
      0
     ],
     "destination": [
      "obj-pak30",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum30",
      0
     ],
     "destination": [
      "bp30_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp30_4",
      0
     ],
     "destination": [
      "av30_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av30_4",
      0
     ],
     "destination": [
      "sn30_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn30_4",
      0
     ],
     "destination": [
      "obj-pak30",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum30",
      0
     ],
     "destination": [
      "bp30_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp30_5",
      0
     ],
     "destination": [
      "av30_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av30_5",
      0
     ],
     "destination": [
      "sn30_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn30_5",
      0
     ],
     "destination": [
      "obj-pak30",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum30",
      0
     ],
     "destination": [
      "bp30_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp30_6",
      0
     ],
     "destination": [
      "av30_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av30_6",
      0
     ],
     "destination": [
      "sn30_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn30_6",
      0
     ],
     "destination": [
      "obj-pak30",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p63",
      0
     ],
     "destination": [
      "sum31",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p64",
      0
     ],
     "destination": [
      "sum31",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p63",
      0
     ],
     "destination": [
      "side31",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "p64",
      0
     ],
     "destination": [
      "side31",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "side31",
      0
     ],
     "destination": [
      "sideav31",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sideav31",
      0
     ],
     "destination": [
      "sidesn31",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sidesn31",
      0
     ],
     "destination": [
      "obj-pak31",
      7
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pak31",
      0
     ],
     "destination": [
      "obj-prep31",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prep31",
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
      "sum31",
      0
     ],
     "destination": [
      "bp31_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp31_0",
      0
     ],
     "destination": [
      "av31_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av31_0",
      0
     ],
     "destination": [
      "sn31_0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn31_0",
      0
     ],
     "destination": [
      "obj-pak31",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum31",
      0
     ],
     "destination": [
      "bp31_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp31_1",
      0
     ],
     "destination": [
      "av31_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av31_1",
      0
     ],
     "destination": [
      "sn31_1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn31_1",
      0
     ],
     "destination": [
      "obj-pak31",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum31",
      0
     ],
     "destination": [
      "bp31_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp31_2",
      0
     ],
     "destination": [
      "av31_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av31_2",
      0
     ],
     "destination": [
      "sn31_2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn31_2",
      0
     ],
     "destination": [
      "obj-pak31",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum31",
      0
     ],
     "destination": [
      "bp31_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp31_3",
      0
     ],
     "destination": [
      "av31_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av31_3",
      0
     ],
     "destination": [
      "sn31_3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn31_3",
      0
     ],
     "destination": [
      "obj-pak31",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum31",
      0
     ],
     "destination": [
      "bp31_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp31_4",
      0
     ],
     "destination": [
      "av31_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av31_4",
      0
     ],
     "destination": [
      "sn31_4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn31_4",
      0
     ],
     "destination": [
      "obj-pak31",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum31",
      0
     ],
     "destination": [
      "bp31_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp31_5",
      0
     ],
     "destination": [
      "av31_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av31_5",
      0
     ],
     "destination": [
      "sn31_5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn31_5",
      0
     ],
     "destination": [
      "obj-pak31",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sum31",
      0
     ],
     "destination": [
      "bp31_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "bp31_6",
      0
     ],
     "destination": [
      "av31_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "av31_6",
      0
     ],
     "destination": [
      "sn31_6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "sn31_6",
      0
     ],
     "destination": [
      "obj-pak31",
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
  ]
 }
}