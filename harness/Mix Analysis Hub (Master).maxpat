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
     "id": "obj-title",
     "maxclass": "comment",
     "numinlets": 1,
     "numoutlets": 0,
     "patching_rect": [
      20.0,
      10.0,
      500.0,
      28.0
     ],
     "text": "MIX ANALYSIS HUB (MASTER) v3 METERS - pure /mix/levels+stereo+spectrum metering, biquad bank, OSC @ 9880. NO js/LiveAPI (master node synthesized in the daemon); transport LOM-sourced",
     "fontsize": 18.0,
     "fontface": 1
    }
   },
   {
    "box": {
     "id": "obj-subtitle",
     "maxclass": "comment",
     "numinlets": 1,
     "numoutlets": 0,
     "patching_rect": [
      20.0,
      40.0,
      500.0,
      20.0
     ],
     "text": "live.thisdevice -> live.path -> observer. @initial 1 auto-outputs. OSC 9880."
    }
   },
   {
    "box": {
     "id": "obj-plugin-in-L",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      50.0,
      100.0,
      55.0,
      22.0
     ],
     "text": "plugin~ 1"
    }
   },
   {
    "box": {
     "id": "obj-plugin-in-R",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      120.0,
      100.0,
      55.0,
      22.0
     ],
     "text": "plugin~ 2"
    }
   },
   {
    "box": {
     "id": "obj-plugout",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 0,
     "patching_rect": [
      50.0,
      750.0,
      65.0,
      22.0
     ],
     "text": "plugout~"
    }
   },
   {
    "box": {
     "id": "obj-transport-label",
     "maxclass": "comment",
     "numinlets": 1,
     "numoutlets": 0,
     "patching_rect": [
      700.0,
      50.0,
      300.0,
      20.0
     ],
     "text": "\u2500\u2500 TRANSPORT \u2500\u2500",
     "fontface": 1
    }
   },
   {
    "box": {
     "id": "obj-loadbang-tempo",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 3,
     "outlettype": [
      "",
      "",
      ""
     ],
     "patching_rect": [
      1060.0,
      50.0,
      90.0,
      22.0
     ],
     "text": "live.thisdevice"
    }
   },
   {
    "box": {
     "id": "obj-toggle",
     "maxclass": "toggle",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "int"
     ],
     "patching_rect": [
      700.0,
      240.0,
      24.0,
      24.0
     ],
     "parameter_enable": 1,
     "int": 1,
     "saved_attribute_attributes": {
      "valueof": {
       "parameter_longname": "Enable OSC",
       "parameter_shortname": "Enable",
       "parameter_type": 2,
       "parameter_mmax": 1.0,
       "parameter_initial_enable": 1,
       "parameter_initial": [
        1
       ]
      }
     }
    }
   },
   {
    "box": {
     "id": "obj-enable-label",
     "maxclass": "comment",
     "numinlets": 1,
     "numoutlets": 0,
     "patching_rect": [
      730.0,
      242.0,
      100.0,
      20.0
     ],
     "text": "Enable OSC"
    }
   },
   {
    "box": {
     "id": "obj-section-levels",
     "maxclass": "comment",
     "numinlets": 1,
     "numoutlets": 0,
     "patching_rect": [
      50.0,
      140.0,
      200.0,
      20.0
     ],
     "text": "\u2500\u2500 LEVEL ANALYSIS \u2500\u2500",
     "fontface": 1
    }
   },
   {
    "box": {
     "id": "obj-rms-l",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      50.0,
      170.0,
      130.0,
      22.0
     ],
     "text": "average~ 2048 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-rms-r",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      170.0,
      130.0,
      22.0
     ],
     "text": "average~ 2048 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-atodb-rms-l",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      50.0,
      200.0,
      55.0,
      22.0
     ],
     "text": "atodb~"
    }
   },
   {
    "box": {
     "id": "obj-atodb-rms-r",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      200.0,
      55.0,
      22.0
     ],
     "text": "atodb~"
    }
   },
   {
    "box": {
     "id": "obj-snapshot-rms-l",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      50.0,
      230.0,
      85.0,
      22.0
     ],
     "text": "snapshot~ 33"
    }
   },
   {
    "box": {
     "id": "obj-snapshot-rms-r",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      200.0,
      230.0,
      85.0,
      22.0
     ],
     "text": "snapshot~ 33"
    }
   },
   {
    "box": {
     "id": "obj-peak-l",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      350.0,
      170.0,
      80.0,
      22.0
     ],
     "text": "peakamp~ 30"
    }
   },
   {
    "box": {
     "id": "obj-peak-r",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      450.0,
      170.0,
      80.0,
      22.0
     ],
     "text": "peakamp~ 30"
    }
   },
   {
    "box": {
     "id": "obj-atodb-peak-l",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      350.0,
      200.0,
      45.0,
      22.0
     ],
     "text": "atodb"
    }
   },
   {
    "box": {
     "id": "obj-atodb-peak-r",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      450.0,
      200.0,
      45.0,
      22.0
     ],
     "text": "atodb"
    }
   },
   {
    "box": {
     "id": "obj-section-stereo",
     "maxclass": "comment",
     "numinlets": 1,
     "numoutlets": 0,
     "patching_rect": [
      50.0,
      280.0,
      200.0,
      20.0
     ],
     "text": "\u2500\u2500 STEREO ANALYSIS \u2500\u2500",
     "fontface": 1
    }
   },
   {
    "box": {
     "id": "obj-mult-lr",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      50.0,
      310.0,
      35.0,
      22.0
     ],
     "text": "*~"
    }
   },
   {
    "box": {
     "id": "obj-avg-corr",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      50.0,
      340.0,
      90.0,
      22.0
     ],
     "text": "average~ 4096"
    }
   },
   {
    "box": {
     "id": "obj-snapshot-corr",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      50.0,
      370.0,
      85.0,
      22.0
     ],
     "text": "snapshot~ 33"
    }
   },
   {
    "box": {
     "id": "obj-mid",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      310.0,
      35.0,
      22.0
     ],
     "text": "+~"
    }
   },
   {
    "box": {
     "id": "obj-mid-scale",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      340.0,
      55.0,
      22.0
     ],
     "text": "*~ 0.5"
    }
   },
   {
    "box": {
     "id": "obj-mid-abs",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      370.0,
      45.0,
      22.0
     ],
     "text": "abs~"
    }
   },
   {
    "box": {
     "id": "obj-avg-mid",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      200.0,
      400.0,
      90.0,
      22.0
     ],
     "text": "average~ 4096"
    }
   },
   {
    "box": {
     "id": "obj-snapshot-mid",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      200.0,
      430.0,
      85.0,
      22.0
     ],
     "text": "snapshot~ 33"
    }
   },
   {
    "box": {
     "id": "obj-side",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      320.0,
      310.0,
      35.0,
      22.0
     ],
     "text": "-~"
    }
   },
   {
    "box": {
     "id": "obj-side-scale",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      320.0,
      340.0,
      55.0,
      22.0
     ],
     "text": "*~ 0.5"
    }
   },
   {
    "box": {
     "id": "obj-side-abs",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      320.0,
      370.0,
      45.0,
      22.0
     ],
     "text": "abs~"
    }
   },
   {
    "box": {
     "id": "obj-avg-side",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      320.0,
      400.0,
      90.0,
      22.0
     ],
     "text": "average~ 4096"
    }
   },
   {
    "box": {
     "id": "obj-snapshot-side",
     "maxclass": "newobj",
     "numinlets": 2,
     "numoutlets": 1,
     "outlettype": [
      "float"
     ],
     "patching_rect": [
      320.0,
      430.0,
      85.0,
      22.0
     ],
     "text": "snapshot~ 33"
    }
   },
   {
    "box": {
     "id": "obj-section-osc",
     "maxclass": "comment",
     "numinlets": 1,
     "numoutlets": 0,
     "patching_rect": [
      50.0,
      480.0,
      200.0,
      20.0
     ],
     "text": "\u2500\u2500 OSC OUTPUT (port 9880) \u2500\u2500",
     "fontface": 1
    }
   },
   {
    "box": {
     "id": "obj-pack-levels",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      50.0,
      510.0,
      200.0,
      22.0
     ],
     "text": "pack f f f f f f"
    }
   },
   {
    "box": {
     "id": "obj-prepend-levels",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      50.0,
      540.0,
      100.0,
      22.0
     ],
     "text": "prepend /mix/levels"
    }
   },
   {
    "box": {
     "id": "obj-pack-stereo",
     "maxclass": "newobj",
     "numinlets": 3,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      50.0,
      580.0,
      100.0,
      22.0
     ],
     "text": "pack f f f"
    }
   },
   {
    "box": {
     "id": "obj-prepend-stereo",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      50.0,
      610.0,
      100.0,
      22.0
     ],
     "text": "prepend /mix/stereo"
    }
   },
   {
    "box": {
     "id": "obj-udpsend",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 0,
     "patching_rect": [
      50.0,
      700.0,
      150.0,
      22.0
     ],
     "text": "udpsend 127.0.0.1 9880"
    }
   },
   {
    "box": {
     "id": "obj-spec-pak",
     "maxclass": "newobj",
     "numinlets": 7,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1040.0,
      600.0,
      160.0,
      22.0
     ],
     "text": "pak 0. 0. 0. 0. 0. 0. 0."
    }
   },
   {
    "box": {
     "id": "obj-mix-spec-prep",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1040.0,
      632.0,
      180.0,
      22.0
     ],
     "text": "prepend /mix/spectrum"
    }
   },
   {
    "box": {
     "id": "obj-bp-0",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      620.0,
      180.0,
      300.0,
      22.0
     ],
     "text": "biquad~ 0.00243104 0.00000000 -0.00243104 -1.99429289 0.99431718"
    }
   },
   {
    "box": {
     "id": "obj-avg-0",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      940.0,
      180.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-snap-0",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1020.0,
      204.0,
      90.0,
      22.0
     ],
     "text": "snapshot~ 50"
    }
   },
   {
    "box": {
     "id": "obj-bp-1",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      620.0,
      220.0,
      300.0,
      22.0
     ],
     "text": "biquad~ 0.00285943 0.00000000 -0.00285943 -1.99134251 0.99148804"
    }
   },
   {
    "box": {
     "id": "obj-avg-1",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      940.0,
      220.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-snap-1",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1020.0,
      244.0,
      90.0,
      22.0
     ],
     "text": "snapshot~ 50"
    }
   },
   {
    "box": {
     "id": "obj-bp-2",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      620.0,
      260.0,
      300.0,
      22.0
     ],
     "text": "biquad~ 0.00854401 0.00000000 -0.00854401 -1.96692455 0.96776332"
    }
   },
   {
    "box": {
     "id": "obj-avg-2",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      940.0,
      260.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-snap-2",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1020.0,
      284.0,
      90.0,
      22.0
     ],
     "text": "snapshot~ 50"
    }
   },
   {
    "box": {
     "id": "obj-bp-3",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      620.0,
      300.0,
      300.0,
      22.0
     ],
     "text": "biquad~ 0.06796147 0.00000000 -0.06796147 -1.77738344 0.79008656"
    }
   },
   {
    "box": {
     "id": "obj-avg-3",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      940.0,
      300.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-snap-3",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1020.0,
      324.0,
      90.0,
      22.0
     ],
     "text": "snapshot~ 50"
    }
   },
   {
    "box": {
     "id": "obj-bp-4",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      620.0,
      340.0,
      300.0,
      22.0
     ],
     "text": "biquad~ 0.13726380 0.00000000 -0.13726380 -1.38302346 0.57044656"
    }
   },
   {
    "box": {
     "id": "obj-avg-4",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      940.0,
      340.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-snap-4",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1020.0,
      364.0,
      90.0,
      22.0
     ],
     "text": "snapshot~ 50"
    }
   },
   {
    "box": {
     "id": "obj-bp-5",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      620.0,
      380.0,
      300.0,
      22.0
     ],
     "text": "biquad~ 0.16991817 0.00000000 -0.16991817 -0.53207291 0.50301502"
    }
   },
   {
    "box": {
     "id": "obj-avg-5",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      940.0,
      380.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-snap-5",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1020.0,
      404.0,
      90.0,
      22.0
     ],
     "text": "snapshot~ 50"
    }
   },
   {
    "box": {
     "id": "obj-bp-6",
     "maxclass": "newobj",
     "numinlets": 6,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      620.0,
      420.0,
      300.0,
      22.0
     ],
     "text": "biquad~ 0.17194508 0.00000000 -0.17194508 0.98427293 0.65610984"
    }
   },
   {
    "box": {
     "id": "obj-avg-6",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      940.0,
      420.0,
      150.0,
      22.0
     ],
     "text": "average~ 1024 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-snap-6",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      1020.0,
      444.0,
      90.0,
      22.0
     ],
     "text": "snapshot~ 50"
    }
   },
   {
    "box": {
     "id": "obj-onset-env",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      "signal"
     ],
     "patching_rect": [
      620.0,
      560.0,
      170.0,
      22.0
     ],
     "text": "average~ 256 @mode rms"
    }
   },
   {
    "box": {
     "id": "obj-onset-snap",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      588.0,
      110.0,
      22.0
     ],
     "text": "snapshot~ 5"
    }
   },
   {
    "box": {
     "id": "obj-onset-prep",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "patching_rect": [
      620.0,
      616.0,
      150.0,
      22.0
     ],
     "text": "prepend /mix/onset"
    }
   },
   {
    "box": {
     "id": "obj-onset-udp",
     "maxclass": "newobj",
     "numinlets": 1,
     "numoutlets": 0,
     "outlettype": [],
     "patching_rect": [
      620.0,
      644.0,
      170.0,
      22.0
     ],
     "text": "udpsend 127.0.0.1 9887"
    }
   },
   {
    "box": {
     "id": "obj-ui-header",
     "maxclass": "comment",
     "fontsize": 9.0,
     "text": "MIX ANALYSIS \u2014 MASTER",
     "patching_rect": [
      40.0,
      740.0,
      300.0,
      14.0
     ],
     "presentation": 1,
     "presentation_rect": [
      6.0,
      2.0,
      300.0,
      14.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-0",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      40.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      6.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-0",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "L",
     "patching_rect": [
      40.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      3.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-1",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      70.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      28.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-1",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "R",
     "patching_rect": [
      70.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      25.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-2",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      100.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      50.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-2",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "S",
     "patching_rect": [
      100.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      47.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-3",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      130.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      72.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-3",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "sub",
     "patching_rect": [
      130.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      69.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-4",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      160.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      94.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-4",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "low",
     "patching_rect": [
      160.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      91.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-5",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      190.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      116.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-5",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "low_mid",
     "patching_rect": [
      190.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      113.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-6",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      220.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      138.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-6",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "mid",
     "patching_rect": [
      220.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      135.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-7",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      250.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      160.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-7",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "hi_mid",
     "patching_rect": [
      250.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      157.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-8",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      280.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      182.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-8",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "presence",
     "patching_rect": [
      280.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      179.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-9",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      310.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      204.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-9",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "air",
     "patching_rect": [
      310.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      201.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-meter-10",
     "maxclass": "live.meter~",
     "numinlets": 1,
     "numoutlets": 1,
     "outlettype": [
      ""
     ],
     "interval": 50,
     "parameter_enable": 0,
     "patching_rect": [
      340.0,
      770.0,
      14.0,
      122.0
     ],
     "presentation": 1,
     "presentation_rect": [
      226.0,
      18.0,
      14.0,
      122.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-mlabel-10",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "fast",
     "patching_rect": [
      340.0,
      800.0,
      28.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      223.0,
      144.0,
      28.0,
      16.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-corr",
     "maxclass": "flonum",
     "numinlets": 1,
     "numoutlets": 2,
     "outlettype": [
      "",
      "bang"
     ],
     "parameter_enable": 0,
     "cantchange": 1,
     "patching_rect": [
      40.0,
      830.0,
      48.0,
      18.0
     ],
     "presentation": 1,
     "presentation_rect": [
      258.0,
      18.0,
      48.0,
      18.0
     ]
    }
   },
   {
    "box": {
     "id": "obj-ui-corr-label",
     "maxclass": "comment",
     "fontsize": 8.0,
     "text": "corr",
     "patching_rect": [
      100.0,
      830.0,
      48.0,
      16.0
     ],
     "presentation": 1,
     "presentation_rect": [
      258.0,
      38.0,
      48.0,
      16.0
     ]
    }
   }
  ],
  "lines": [
   {
    "patchline": {
     "source": [
      "obj-plugin-in-L",
      0
     ],
     "destination": [
      "obj-plugout",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-R",
      0
     ],
     "destination": [
      "obj-plugout",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-L",
      0
     ],
     "destination": [
      "obj-rms-l",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-R",
      0
     ],
     "destination": [
      "obj-rms-r",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-rms-l",
      0
     ],
     "destination": [
      "obj-atodb-rms-l",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-rms-r",
      0
     ],
     "destination": [
      "obj-atodb-rms-r",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-atodb-rms-l",
      0
     ],
     "destination": [
      "obj-snapshot-rms-l",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-atodb-rms-r",
      0
     ],
     "destination": [
      "obj-snapshot-rms-r",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-L",
      0
     ],
     "destination": [
      "obj-peak-l",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-R",
      0
     ],
     "destination": [
      "obj-peak-r",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-peak-l",
      0
     ],
     "destination": [
      "obj-atodb-peak-l",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-peak-r",
      0
     ],
     "destination": [
      "obj-atodb-peak-r",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-L",
      0
     ],
     "destination": [
      "obj-mult-lr",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-R",
      0
     ],
     "destination": [
      "obj-mult-lr",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mult-lr",
      0
     ],
     "destination": [
      "obj-avg-corr",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-corr",
      0
     ],
     "destination": [
      "obj-snapshot-corr",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-L",
      0
     ],
     "destination": [
      "obj-mid",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-R",
      0
     ],
     "destination": [
      "obj-mid",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid",
      0
     ],
     "destination": [
      "obj-mid-scale",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-mid-abs",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-abs",
      0
     ],
     "destination": [
      "obj-avg-mid",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-mid",
      0
     ],
     "destination": [
      "obj-snapshot-mid",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-L",
      0
     ],
     "destination": [
      "obj-side",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-R",
      0
     ],
     "destination": [
      "obj-side",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-side",
      0
     ],
     "destination": [
      "obj-side-scale",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-side-scale",
      0
     ],
     "destination": [
      "obj-side-abs",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-side-abs",
      0
     ],
     "destination": [
      "obj-avg-side",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-side",
      0
     ],
     "destination": [
      "obj-snapshot-side",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snapshot-rms-l",
      0
     ],
     "destination": [
      "obj-pack-levels",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snapshot-rms-r",
      0
     ],
     "destination": [
      "obj-pack-levels",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-atodb-peak-l",
      0
     ],
     "destination": [
      "obj-pack-levels",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-atodb-peak-r",
      0
     ],
     "destination": [
      "obj-pack-levels",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snapshot-mid",
      0
     ],
     "destination": [
      "obj-pack-levels",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snapshot-side",
      0
     ],
     "destination": [
      "obj-pack-levels",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pack-levels",
      0
     ],
     "destination": [
      "obj-prepend-levels",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prepend-levels",
      0
     ],
     "destination": [
      "obj-udpsend",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snapshot-corr",
      0
     ],
     "destination": [
      "obj-pack-stereo",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snapshot-mid",
      0
     ],
     "destination": [
      "obj-pack-stereo",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snapshot-side",
      0
     ],
     "destination": [
      "obj-pack-stereo",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-pack-stereo",
      0
     ],
     "destination": [
      "obj-prepend-stereo",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-prepend-stereo",
      0
     ],
     "destination": [
      "obj-udpsend",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-spec-pak",
      0
     ],
     "destination": [
      "obj-mix-spec-prep",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mix-spec-prep",
      0
     ],
     "destination": [
      "obj-udpsend",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-bp-0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-bp-0",
      0
     ],
     "destination": [
      "obj-avg-0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-0",
      0
     ],
     "destination": [
      "obj-snap-0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snap-0",
      0
     ],
     "destination": [
      "obj-spec-pak",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-bp-1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-bp-1",
      0
     ],
     "destination": [
      "obj-avg-1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-1",
      0
     ],
     "destination": [
      "obj-snap-1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snap-1",
      0
     ],
     "destination": [
      "obj-spec-pak",
      1
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-bp-2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-bp-2",
      0
     ],
     "destination": [
      "obj-avg-2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-2",
      0
     ],
     "destination": [
      "obj-snap-2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snap-2",
      0
     ],
     "destination": [
      "obj-spec-pak",
      2
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-bp-3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-bp-3",
      0
     ],
     "destination": [
      "obj-avg-3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-3",
      0
     ],
     "destination": [
      "obj-snap-3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snap-3",
      0
     ],
     "destination": [
      "obj-spec-pak",
      3
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-bp-4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-bp-4",
      0
     ],
     "destination": [
      "obj-avg-4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-4",
      0
     ],
     "destination": [
      "obj-snap-4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snap-4",
      0
     ],
     "destination": [
      "obj-spec-pak",
      4
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-bp-5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-bp-5",
      0
     ],
     "destination": [
      "obj-avg-5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-5",
      0
     ],
     "destination": [
      "obj-snap-5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snap-5",
      0
     ],
     "destination": [
      "obj-spec-pak",
      5
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-bp-6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-bp-6",
      0
     ],
     "destination": [
      "obj-avg-6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-6",
      0
     ],
     "destination": [
      "obj-snap-6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snap-6",
      0
     ],
     "destination": [
      "obj-spec-pak",
      6
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-mid-scale",
      0
     ],
     "destination": [
      "obj-onset-env",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-onset-env",
      0
     ],
     "destination": [
      "obj-onset-snap",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-onset-snap",
      0
     ],
     "destination": [
      "obj-onset-prep",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-onset-prep",
      0
     ],
     "destination": [
      "obj-onset-udp",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-loadbang-tempo",
      0
     ],
     "destination": [
      "obj-toggle",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-L",
      0
     ],
     "destination": [
      "obj-ui-meter-0",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-plugin-in-R",
      0
     ],
     "destination": [
      "obj-ui-meter-1",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-side-scale",
      0
     ],
     "destination": [
      "obj-ui-meter-2",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-0",
      0
     ],
     "destination": [
      "obj-ui-meter-3",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-1",
      0
     ],
     "destination": [
      "obj-ui-meter-4",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-2",
      0
     ],
     "destination": [
      "obj-ui-meter-5",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-3",
      0
     ],
     "destination": [
      "obj-ui-meter-6",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-4",
      0
     ],
     "destination": [
      "obj-ui-meter-7",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-5",
      0
     ],
     "destination": [
      "obj-ui-meter-8",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-avg-6",
      0
     ],
     "destination": [
      "obj-ui-meter-9",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-onset-env",
      0
     ],
     "destination": [
      "obj-ui-meter-10",
      0
     ]
    }
   },
   {
    "patchline": {
     "source": [
      "obj-snapshot-corr",
      0
     ],
     "destination": [
      "obj-ui-corr",
      0
     ]
    }
   }
  ],
  "openinpresentation": 1
 }
}