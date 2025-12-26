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
		"rect": [50.0, 50.0, 1400.0, 900.0],
		"gridsize": [15.0, 15.0],
		"boxes": [
			{
				"box": {
					"id": "obj-title",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 10.0, 500.0, 28.0],
					"text": "MIX ANALYSIS HUB v19 - live.observer @initial 1 for tempo",
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
					"patching_rect": [20.0, 40.0, 500.0, 20.0],
					"text": "live.thisdevice -> live.path -> observer. @initial 1 auto-outputs. OSC 9880."
				}
			},
			{
				"box": {
					"id": "obj-plugin-in-L",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [50.0, 100.0, 55.0, 22.0],
					"text": "plugin~ 1"
				}
			},
			{
				"box": {
					"id": "obj-plugin-in-R",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [120.0, 100.0, 55.0, 22.0],
					"text": "plugin~ 2"
				}
			},
			{
				"box": {
					"id": "obj-plugout",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [50.0, 750.0, 65.0, 22.0],
					"text": "plugout~"
				}
			},
			{
				"box": {
					"id": "obj-transport-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [700.0, 50.0, 300.0, 20.0],
					"text": "── TRANSPORT ──",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-plugsync",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 9,
					"outlettype": ["int", "int", "float", "float", "", "float", "float", "int", "int"],
					"patching_rect": [700.0, 80.0, 300.0, 22.0],
					"text": "plugsync~"
				}
			},
			{
				"box": {
					"id": "obj-tempo-observer",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": ["", ""],
					"patching_rect": [850.0, 110.0, 220.0, 22.0],
					"text": "live.observer @property tempo @initial 1"
				}
			},
			{
				"box": {
					"id": "obj-live-path",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", ""],
					"patching_rect": [950.0, 80.0, 100.0, 22.0],
					"text": "live.path live_set"
				}
			},
			{
				"box": {
					"id": "obj-loadbang-tempo",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", ""],
					"patching_rect": [1060.0, 50.0, 90.0, 22.0],
					"text": "live.thisdevice"
				}
			},
			{
				"box": {
					"id": "obj-playing-snap",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["int"],
					"patching_rect": [700.0, 140.0, 70.0, 22.0],
					"text": "change"
				}
			},
			{
				"box": {
					"id": "obj-playing-i",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["int"],
					"patching_rect": [700.0, 170.0, 29.0, 22.0],
					"text": "i 0"
				}
			},
			{
				"box": {
					"id": "obj-beats-snap",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [780.0, 140.0, 55.0, 22.0],
					"text": "change"
				}
			},
			{
				"box": {
					"id": "obj-beats-f",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [780.0, 170.0, 35.0, 22.0],
					"text": "f 0."
				}
			},
			{
				"box": {
					"id": "obj-bar-calc",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["int"],
					"patching_rect": [780.0, 200.0, 29.0, 22.0],
					"text": "/ 4"
				}
			},
			{
				"box": {
					"id": "obj-beat-calc",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [820.0, 200.0, 29.0, 22.0],
					"text": "% 4"
				}
			},
			{
				"box": {
					"id": "obj-tempo-f",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [850.0, 170.0, 45.0, 22.0],
					"text": "f 120."
				}
			},
			{
				"box": {
					"id": "obj-toggle",
					"maxclass": "toggle",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["int"],
					"patching_rect": [700.0, 240.0, 24.0, 24.0],
					"parameter_enable": 1,
					"int": 1,
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "Enable OSC",
							"parameter_shortname": "Enable",
							"parameter_type": 2,
							"parameter_mmax": 1.0,
							"parameter_initial_enable": 1,
							"parameter_initial": [1]
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
					"patching_rect": [730.0, 242.0, 100.0, 20.0],
					"text": "Enable OSC"
				}
			},
			{
				"box": {
					"id": "obj-metro",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["bang"],
					"patching_rect": [700.0, 280.0, 71.0, 22.0],
					"text": "metro 33"
				}
			},
			{
				"box": {
					"id": "obj-trig-transport",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["bang", "bang", "bang"],
					"patching_rect": [700.0, 310.0, 100.0, 22.0],
					"text": "t b b b"
				}
			},
			{
				"box": {
					"id": "obj-pack-transport",
					"maxclass": "newobj",
					"numinlets": 5,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [700.0, 380.0, 180.0, 22.0],
					"text": "pack 0 120. 0 0. 100"
				}
			},
			{
				"box": {
					"id": "obj-prepend-transport",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [700.0, 410.0, 115.0, 22.0],
					"text": "prepend /mix/transport"
				}
			},
			{
				"box": {
					"id": "obj-section-levels",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [50.0, 140.0, 200.0, 20.0],
					"text": "── LEVEL ANALYSIS ──",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-rms-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [50.0, 170.0, 130.0, 22.0],
					"text": "average~ 2048 @mode rms"
				}
			},
			{
				"box": {
					"id": "obj-rms-r",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [200.0, 170.0, 130.0, 22.0],
					"text": "average~ 2048 @mode rms"
				}
			},
			{
				"box": {
					"id": "obj-atodb-rms-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [50.0, 200.0, 55.0, 22.0],
					"text": "atodb~"
				}
			},
			{
				"box": {
					"id": "obj-atodb-rms-r",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [200.0, 200.0, 55.0, 22.0],
					"text": "atodb~"
				}
			},
			{
				"box": {
					"id": "obj-snapshot-rms-l",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [50.0, 230.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-snapshot-rms-r",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [200.0, 230.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-peak-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [350.0, 170.0, 80.0, 22.0],
					"text": "peakamp~ 30"
				}
			},
			{
				"box": {
					"id": "obj-peak-r",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [450.0, 170.0, 80.0, 22.0],
					"text": "peakamp~ 30"
				}
			},
			{
				"box": {
					"id": "obj-atodb-peak-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [350.0, 200.0, 45.0, 22.0],
					"text": "atodb"
				}
			},
			{
				"box": {
					"id": "obj-atodb-peak-r",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [450.0, 200.0, 45.0, 22.0],
					"text": "atodb"
				}
			},
			{
				"box": {
					"id": "obj-section-stereo",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [50.0, 280.0, 200.0, 20.0],
					"text": "── STEREO ANALYSIS ──",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-mult-lr",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [50.0, 310.0, 35.0, 22.0],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "obj-avg-corr",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [50.0, 340.0, 90.0, 22.0],
					"text": "average~ 4096"
				}
			},
			{
				"box": {
					"id": "obj-snapshot-corr",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [50.0, 370.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-mid",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [200.0, 310.0, 35.0, 22.0],
					"text": "+~"
				}
			},
			{
				"box": {
					"id": "obj-mid-scale",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [200.0, 340.0, 55.0, 22.0],
					"text": "*~ 0.5"
				}
			},
			{
				"box": {
					"id": "obj-mid-abs",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [200.0, 370.0, 45.0, 22.0],
					"text": "abs~"
				}
			},
			{
				"box": {
					"id": "obj-avg-mid",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [200.0, 400.0, 90.0, 22.0],
					"text": "average~ 4096"
				}
			},
			{
				"box": {
					"id": "obj-snapshot-mid",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [200.0, 430.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-side",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [320.0, 310.0, 35.0, 22.0],
					"text": "-~"
				}
			},
			{
				"box": {
					"id": "obj-side-scale",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [320.0, 340.0, 55.0, 22.0],
					"text": "*~ 0.5"
				}
			},
			{
				"box": {
					"id": "obj-side-abs",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [320.0, 370.0, 45.0, 22.0],
					"text": "abs~"
				}
			},
			{
				"box": {
					"id": "obj-avg-side",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [320.0, 400.0, 90.0, 22.0],
					"text": "average~ 4096"
				}
			},
			{
				"box": {
					"id": "obj-snapshot-side",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [320.0, 430.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-section-osc",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [50.0, 480.0, 200.0, 20.0],
					"text": "── OSC OUTPUT (port 9880) ──",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-pack-levels",
					"maxclass": "newobj",
					"numinlets": 6,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [50.0, 510.0, 200.0, 22.0],
					"text": "pack f f f f f f"
				}
			},
			{
				"box": {
					"id": "obj-prepend-levels",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [50.0, 540.0, 100.0, 22.0],
					"text": "prepend /mix/levels"
				}
			},
			{
				"box": {
					"id": "obj-pack-stereo",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [50.0, 580.0, 100.0, 22.0],
					"text": "pack f f f"
				}
			},
			{
				"box": {
					"id": "obj-prepend-stereo",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [50.0, 610.0, 100.0, 22.0],
					"text": "prepend /mix/stereo"
				}
			},
			{
				"box": {
					"id": "obj-udpsend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [50.0, 700.0, 150.0, 22.0],
					"text": "udpsend 127.0.0.1 9880"
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"source": ["obj-loadbang-tempo", 0],
					"destination": ["obj-live-path", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-live-path", 1],
					"destination": ["obj-tempo-observer", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-tempo-observer", 0],
					"destination": ["obj-tempo-f", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugsync", 0],
					"destination": ["obj-playing-snap", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-playing-snap", 0],
					"destination": ["obj-playing-i", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugsync", 6],
					"destination": ["obj-beats-snap", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-beats-snap", 0],
					"destination": ["obj-beats-f", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-toggle", 0],
					"destination": ["obj-metro", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-metro", 0],
					"destination": ["obj-trig-transport", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-trig-transport", 0],
					"destination": ["obj-playing-i", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-playing-i", 0],
					"destination": ["obj-pack-transport", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-trig-transport", 1],
					"destination": ["obj-tempo-f", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-tempo-f", 0],
					"destination": ["obj-pack-transport", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-trig-transport", 2],
					"destination": ["obj-beats-f", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-beats-f", 0],
					"destination": ["obj-bar-calc", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-beats-f", 0],
					"destination": ["obj-beat-calc", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-bar-calc", 0],
					"destination": ["obj-pack-transport", 2]
				}
			},
			{
				"patchline": {
					"source": ["obj-beat-calc", 0],
					"destination": ["obj-pack-transport", 3]
				}
			},
			{
				"patchline": {
					"source": ["obj-pack-transport", 0],
					"destination": ["obj-prepend-transport", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-prepend-transport", 0],
					"destination": ["obj-udpsend", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-L", 0],
					"destination": ["obj-plugout", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-R", 0],
					"destination": ["obj-plugout", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-L", 0],
					"destination": ["obj-rms-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-R", 0],
					"destination": ["obj-rms-r", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-rms-l", 0],
					"destination": ["obj-atodb-rms-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-rms-r", 0],
					"destination": ["obj-atodb-rms-r", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-atodb-rms-l", 0],
					"destination": ["obj-snapshot-rms-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-atodb-rms-r", 0],
					"destination": ["obj-snapshot-rms-r", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-L", 0],
					"destination": ["obj-peak-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-R", 0],
					"destination": ["obj-peak-r", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-peak-l", 0],
					"destination": ["obj-atodb-peak-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-peak-r", 0],
					"destination": ["obj-atodb-peak-r", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-L", 0],
					"destination": ["obj-mult-lr", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-R", 0],
					"destination": ["obj-mult-lr", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-mult-lr", 0],
					"destination": ["obj-avg-corr", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-avg-corr", 0],
					"destination": ["obj-snapshot-corr", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-L", 0],
					"destination": ["obj-mid", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-R", 0],
					"destination": ["obj-mid", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-mid", 0],
					"destination": ["obj-mid-scale", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-mid-scale", 0],
					"destination": ["obj-mid-abs", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-mid-abs", 0],
					"destination": ["obj-avg-mid", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-avg-mid", 0],
					"destination": ["obj-snapshot-mid", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-L", 0],
					"destination": ["obj-side", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-R", 0],
					"destination": ["obj-side", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-side", 0],
					"destination": ["obj-side-scale", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-side-scale", 0],
					"destination": ["obj-side-abs", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-side-abs", 0],
					"destination": ["obj-avg-side", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-avg-side", 0],
					"destination": ["obj-snapshot-side", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-snapshot-rms-l", 0],
					"destination": ["obj-pack-levels", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-snapshot-rms-r", 0],
					"destination": ["obj-pack-levels", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-atodb-peak-l", 0],
					"destination": ["obj-pack-levels", 2]
				}
			},
			{
				"patchline": {
					"source": ["obj-atodb-peak-r", 0],
					"destination": ["obj-pack-levels", 3]
				}
			},
			{
				"patchline": {
					"source": ["obj-snapshot-mid", 0],
					"destination": ["obj-pack-levels", 4]
				}
			},
			{
				"patchline": {
					"source": ["obj-snapshot-side", 0],
					"destination": ["obj-pack-levels", 5]
				}
			},
			{
				"patchline": {
					"source": ["obj-pack-levels", 0],
					"destination": ["obj-prepend-levels", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-prepend-levels", 0],
					"destination": ["obj-udpsend", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-snapshot-corr", 0],
					"destination": ["obj-pack-stereo", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-snapshot-mid", 0],
					"destination": ["obj-pack-stereo", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-snapshot-side", 0],
					"destination": ["obj-pack-stereo", 2]
				}
			},
			{
				"patchline": {
					"source": ["obj-pack-stereo", 0],
					"destination": ["obj-prepend-stereo", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-prepend-stereo", 0],
					"destination": ["obj-udpsend", 0]
				}
			}
		]
	}
}
