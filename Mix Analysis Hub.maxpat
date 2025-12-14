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
					"text": "MIX ANALYSIS HUB - Real-Time Audio Analysis + Transport Sync",
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
					"text": "Streams audio analysis + transport state to Python (port 9880) for LLM context"
				}
			},
			{
				"box": {
					"id": "obj-plugin-in",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": ["signal", "signal"],
					"patching_rect": [50.0, 100.0, 80.0, 22.0],
					"text": "plugin~ 2"
				}
			},
			{
				"box": {
					"id": "obj-plugin-out",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [50.0, 800.0, 90.0, 22.0],
					"text": "plugout~ 1 2"
				}
			},
			{
				"box": {
					"id": "obj-loadbang",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["bang"],
					"patching_rect": [850.0, 50.0, 60.0, 22.0],
					"text": "loadbang"
				}
			},
			{
				"box": {
					"id": "obj-toggle",
					"maxclass": "toggle",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["int"],
					"patching_rect": [900.0, 50.0, 24.0, 24.0],
					"parameter_enable": 1,
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "Enable Analysis",
							"parameter_shortname": "Enable",
							"parameter_type": 2,
							"parameter_mmax": 1.0
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
					"patching_rect": [930.0, 52.0, 120.0, 20.0],
					"text": "Enable Analysis"
				}
			},
			{
				"box": {
					"id": "obj-metro",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["bang"],
					"patching_rect": [900.0, 90.0, 71.0, 22.0],
					"text": "metro 33"
				}
			},
			{
				"box": {
					"id": "obj-section-transport",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [850.0, 130.0, 250.0, 20.0],
					"text": "── TRANSPORT SYNC (Live API) ──",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-js-transport",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "bang", ""],
					"patching_rect": [850.0, 160.0, 140.0, 22.0],
					"text": "js transport_sync.js"
				}
			},
			{
				"box": {
					"id": "obj-transport-display",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [850.0, 195.0, 250.0, 22.0],
					"text": "0 120 0 0 100 4 4"
				}
			},
			{
				"box": {
					"id": "obj-transport-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [850.0, 220.0, 280.0, 20.0],
					"text": "[playing, bpm, bar, beat, length, sig_num, sig_den]"
				}
			},
			{
				"box": {
					"id": "obj-prepend-transport",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [850.0, 250.0, 150.0, 22.0],
					"text": "prepend /mix/transport"
				}
			},
			{
				"box": {
					"id": "obj-bar-change",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [1000.0, 160.0, 100.0, 22.0],
					"text": "print BAR_CHANGE"
				}
			},
			{
				"box": {
					"id": "obj-status-print",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [1100.0, 160.0, 100.0, 22.0],
					"text": "print TRANSPORT"
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
					"id": "obj-abs-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [50.0, 170.0, 45.0, 22.0],
					"text": "abs~"
				}
			},
			{
				"box": {
					"id": "obj-abs-r",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [150.0, 170.0, 45.0, 22.0],
					"text": "abs~"
				}
			},
			{
				"box": {
					"id": "obj-avg-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [50.0, 200.0, 90.0, 22.0],
					"text": "average~ 2048"
				}
			},
			{
				"box": {
					"id": "obj-avg-r",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [150.0, 200.0, 90.0, 22.0],
					"text": "average~ 2048"
				}
			},
			{
				"box": {
					"id": "obj-atodb-rms-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [50.0, 230.0, 55.0, 22.0],
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
					"patching_rect": [150.0, 230.0, 55.0, 22.0],
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
					"patching_rect": [50.0, 260.0, 85.0, 22.0],
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
					"patching_rect": [150.0, 260.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-rms-l-num",
					"maxclass": "number~",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": ["signal", "float"],
					"patching_rect": [50.0, 290.0, 80.0, 22.0],
					"mode": 2,
					"sig": 0.0
				}
			},
			{
				"box": {
					"id": "obj-rms-r-num",
					"maxclass": "number~",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": ["signal", "float"],
					"patching_rect": [150.0, 290.0, 80.0, 22.0],
					"mode": 2,
					"sig": 0.0
				}
			},
			{
				"box": {
					"id": "obj-rms-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [50.0, 315.0, 180.0, 20.0],
					"text": "RMS L / R (dB)"
				}
			},
			{
				"box": {
					"id": "obj-peak-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [280.0, 170.0, 100.0, 22.0],
					"text": "peakamp~ 2048"
				}
			},
			{
				"box": {
					"id": "obj-peak-r",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [390.0, 170.0, 100.0, 22.0],
					"text": "peakamp~ 2048"
				}
			},
			{
				"box": {
					"id": "obj-atodb-peak-l",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [280.0, 200.0, 55.0, 22.0],
					"text": "atodb~"
				}
			},
			{
				"box": {
					"id": "obj-atodb-peak-r",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [390.0, 200.0, 55.0, 22.0],
					"text": "atodb~"
				}
			},
			{
				"box": {
					"id": "obj-snapshot-peak-l",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [280.0, 230.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-snapshot-peak-r",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [390.0, 230.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-peak-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [280.0, 260.0, 180.0, 20.0],
					"text": "Peak L / R (dB)"
				}
			},
			{
				"box": {
					"id": "obj-section-stereo",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [50.0, 350.0, 200.0, 20.0],
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
					"patching_rect": [50.0, 380.0, 35.0, 22.0],
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
					"patching_rect": [50.0, 410.0, 90.0, 22.0],
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
					"patching_rect": [50.0, 440.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-corr-num",
					"maxclass": "number~",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": ["signal", "float"],
					"patching_rect": [50.0, 470.0, 80.0, 22.0],
					"mode": 2,
					"sig": 0.0
				}
			},
			{
				"box": {
					"id": "obj-corr-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [50.0, 495.0, 120.0, 20.0],
					"text": "Correlation (-1 to 1)"
				}
			},
			{
				"box": {
					"id": "obj-mid",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [200.0, 380.0, 35.0, 22.0],
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
					"patching_rect": [200.0, 410.0, 55.0, 22.0],
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
					"patching_rect": [200.0, 440.0, 45.0, 22.0],
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
					"patching_rect": [200.0, 470.0, 90.0, 22.0],
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
					"patching_rect": [200.0, 500.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-mid-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [200.0, 525.0, 80.0, 20.0],
					"text": "Mid Energy"
				}
			},
			{
				"box": {
					"id": "obj-side",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [320.0, 380.0, 35.0, 22.0],
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
					"patching_rect": [320.0, 410.0, 55.0, 22.0],
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
					"patching_rect": [320.0, 440.0, 45.0, 22.0],
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
					"patching_rect": [320.0, 470.0, 90.0, 22.0],
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
					"patching_rect": [320.0, 500.0, 85.0, 22.0],
					"text": "snapshot~ 33"
				}
			},
			{
				"box": {
					"id": "obj-side-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [320.0, 525.0, 80.0, 20.0],
					"text": "Side Energy"
				}
			},
			{
				"box": {
					"id": "obj-section-osc",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [500.0, 350.0, 200.0, 20.0],
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
					"patching_rect": [500.0, 400.0, 200.0, 22.0],
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
					"patching_rect": [500.0, 430.0, 130.0, 22.0],
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
					"patching_rect": [500.0, 480.0, 100.0, 22.0],
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
					"patching_rect": [500.0, 510.0, 130.0, 22.0],
					"text": "prepend /mix/stereo"
				}
			},
			{
				"box": {
					"id": "obj-udpsend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [500.0, 600.0, 150.0, 22.0],
					"text": "udpsend 127.0.0.1 9880"
				}
			},
			{
				"box": {
					"id": "obj-print-osc",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [660.0, 600.0, 80.0, 22.0],
					"text": "print OSC_OUT"
				}
			},
			{
				"box": {
					"id": "obj-msg-count",
					"maxclass": "number",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": ["", "bang"],
					"patching_rect": [500.0, 560.0, 60.0, 22.0]
				}
			},
			{
				"box": {
					"id": "obj-counter",
					"maxclass": "newobj",
					"numinlets": 5,
					"numoutlets": 4,
					"outlettype": ["int", "", "", "int"],
					"patching_rect": [570.0, 560.0, 80.0, 22.0],
					"text": "counter"
				}
			},
			{
				"box": {
					"id": "obj-count-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [655.0, 560.0, 100.0, 20.0],
					"text": "msgs sent"
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"source": ["obj-loadbang", 0],
					"destination": ["obj-toggle", 0]
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
					"destination": ["obj-js-transport", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js-transport", 0],
					"destination": ["obj-transport-display", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-js-transport", 0],
					"destination": ["obj-prepend-transport", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js-transport", 1],
					"destination": ["obj-bar-change", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js-transport", 2],
					"destination": ["obj-status-print", 0]
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
					"source": ["obj-plugin-in", 0],
					"destination": ["obj-plugin-out", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 1],
					"destination": ["obj-plugin-out", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 0],
					"destination": ["obj-abs-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 1],
					"destination": ["obj-abs-r", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-abs-l", 0],
					"destination": ["obj-avg-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-abs-r", 0],
					"destination": ["obj-avg-r", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-avg-l", 0],
					"destination": ["obj-atodb-rms-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-avg-r", 0],
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
					"source": ["obj-atodb-rms-l", 0],
					"destination": ["obj-rms-l-num", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-atodb-rms-r", 0],
					"destination": ["obj-rms-r-num", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 0],
					"destination": ["obj-peak-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 1],
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
					"source": ["obj-atodb-peak-l", 0],
					"destination": ["obj-snapshot-peak-l", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-atodb-peak-r", 0],
					"destination": ["obj-snapshot-peak-r", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 0],
					"destination": ["obj-mult-lr", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 1],
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
					"source": ["obj-avg-corr", 0],
					"destination": ["obj-corr-num", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 0],
					"destination": ["obj-mid", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 1],
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
					"source": ["obj-plugin-in", 0],
					"destination": ["obj-side", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 1],
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
					"source": ["obj-snapshot-peak-l", 0],
					"destination": ["obj-pack-levels", 2]
				}
			},
			{
				"patchline": {
					"source": ["obj-snapshot-peak-r", 0],
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
					"source": ["obj-prepend-levels", 0],
					"destination": ["obj-counter", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-counter", 0],
					"destination": ["obj-msg-count", 0]
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
