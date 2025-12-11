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
		"rect": [100.0, 100.0, 800.0, 600.0],
		"gridsize": [15.0, 15.0],
		"boxes": [
			{
				"box": {
					"id": "obj-title",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 10.0, 300.0, 24.0],
					"text": "SERUM UDP CONTROL",
					"fontsize": 16.0,
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-loadbang",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["bang"],
					"patching_rect": [20.0, 50.0, 60.0, 22.0],
					"text": "loadbang"
				}
			},
			{
				"box": {
					"id": "obj-plug",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [20.0, 80.0, 280.0, 22.0],
					"text": "plug /Library/Audio/Plug-Ins/VST3/Serum2.vst3, open"
				}
			},
			{
				"box": {
					"id": "obj-vst",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "", "", "", ""],
					"patching_rect": [20.0, 120.0, 300.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [20.0, 160.0, 60.0, 22.0],
					"text": "dac~ 1 2"
				}
			},
			{
				"box": {
					"id": "obj-udp",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": ["", ""],
					"patching_rect": [400.0, 50.0, 170.0, 22.0],
					"text": "mxj net.udp.recv @port 9878"
				}
			},
			{
				"box": {
					"id": "obj-print-in",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [580.0, 50.0, 70.0, 22.0],
					"text": "print UDP_IN"
				}
			},
			{
				"box": {
					"id": "obj-fromsymbol",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [400.0, 90.0, 75.0, 22.0],
					"text": "fromsymbol"
				}
			},
			{
				"box": {
					"id": "obj-route",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", ""],
					"patching_rect": [400.0, 130.0, 180.0, 22.0],
					"text": "route set_param ping"
				}
			},
			{
				"box": {
					"id": "obj-print-cmd",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [400.0, 170.0, 55.0, 22.0],
					"text": "print CMD"
				}
			},
			{
				"box": {
					"id": "obj-print-ping",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [500.0, 170.0, 60.0, 22.0],
					"text": "print PING"
				}
			},
			{
				"box": {
					"id": "obj-filter-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 220.0, 100.0, 20.0],
					"text": "Filter Cutoff"
				}
			},
			{
				"box": {
					"id": "obj-dial",
					"maxclass": "dial",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [20.0, 240.0, 80.0, 80.0],
					"size": 1.0,
					"floatoutput": 1
				}
			},
			{
				"box": {
					"id": "obj-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [20.0, 330.0, 60.0, 22.0],
					"text": "206 $1"
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"source": ["obj-loadbang", 0],
					"destination": ["obj-plug", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plug", 0],
					"destination": ["obj-vst", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst", 0],
					"destination": ["obj-dac", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst", 1],
					"destination": ["obj-dac", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-udp", 0],
					"destination": ["obj-print-in", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-udp", 0],
					"destination": ["obj-fromsymbol", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-fromsymbol", 0],
					"destination": ["obj-route", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route", 0],
					"destination": ["obj-print-cmd", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route", 0],
					"destination": ["obj-vst", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route", 1],
					"destination": ["obj-print-ping", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-dial", 0],
					"destination": ["obj-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-msg", 0],
					"destination": ["obj-vst", 0]
				}
			}
		]
	}
}
