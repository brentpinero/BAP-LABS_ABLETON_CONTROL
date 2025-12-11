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
		"rect": [100.0, 100.0, 1000.0, 700.0],
		"bgcolor": [0.1, 0.1, 0.15, 1.0],
		"editing_bgcolor": [0.1, 0.1, 0.15, 1.0],
		"gridsize": [15.0, 15.0],
		"boxes": [
			{
				"box": {
					"id": "obj-title",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 15.0, 400.0, 30.0],
					"text": "SERUM SOCKET CONTROL - M4L Device",
					"fontsize": 20.0,
					"fontface": 1,
					"textcolor": [0.0, 1.0, 0.9, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-subtitle",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 45.0, 400.0, 20.0],
					"text": "Receives commands on port 9878, controls Serum via vst~",
					"fontsize": 12.0,
					"textcolor": [0.6, 0.6, 0.7, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-loadbang",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["bang"],
					"patching_rect": [20.0, 80.0, 60.0, 22.0],
					"text": "loadbang"
				}
			},
			{
				"box": {
					"id": "obj-plug-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [20.0, 110.0, 160.0, 22.0],
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
					"patching_rect": [20.0, 150.0, 200.0, 22.0],
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
					"patching_rect": [20.0, 190.0, 60.0, 22.0],
					"text": "dac~ 1 2"
				}
			},
			{
				"box": {
					"id": "obj-server-comment",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [450.0, 80.0, 200.0, 20.0],
					"text": "Socket Server (port 9878)",
					"fontsize": 14.0,
					"fontface": 1,
					"textcolor": [0.8, 0.8, 0.9, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-udp",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": ["", ""],
					"patching_rect": [450.0, 110.0, 150.0, 22.0],
					"text": "mxj net.udp.recv @port 9878"
				}
			},
			{
				"box": {
					"id": "obj-fromsymbol",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [450.0, 140.0, 80.0, 22.0],
					"text": "fromsymbol"
				}
			},
			{
				"box": {
					"id": "obj-route-cmd",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 8,
					"outlettype": ["", "", "", "", "", "", "", ""],
					"patching_rect": [450.0, 170.0, 500.0, 22.0],
					"text": "route set_param get_param set_param_name ping open close list_params json"
				}
			},
			{
				"box": {
					"id": "obj-js",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": ["", ""],
					"patching_rect": [450.0, 280.0, 200.0, 22.0],
					"text": "js serum_socket_controller.js"
				}
			},
			{
				"box": {
					"id": "obj-print-status",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [700.0, 350.0, 100.0, 22.0],
					"text": "print serum_ctrl"
				}
			},
			{
				"box": {
					"id": "obj-udpsend",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [700.0, 380.0, 130.0, 22.0],
					"text": "udpsend localhost 9879"
				}
			},
			{
				"box": {
					"id": "obj-prepend-set",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [450.0, 210.0, 100.0, 22.0],
					"text": "prepend set_param"
				}
			},
			{
				"box": {
					"id": "obj-prepend-get",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [560.0, 210.0, 100.0, 22.0],
					"text": "prepend get_param"
				}
			},
			{
				"box": {
					"id": "obj-prepend-name",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [670.0, 210.0, 120.0, 22.0],
					"text": "prepend set_param_name"
				}
			},
			{
				"box": {
					"id": "obj-prepend-json",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [900.0, 210.0, 70.0, 22.0],
					"text": "prepend json"
				}
			},
			{
				"box": {
					"id": "obj-ping-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [780.0, 210.0, 40.0, 22.0],
					"text": "ping"
				}
			},
			{
				"box": {
					"id": "obj-open-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [825.0, 210.0, 35.0, 22.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-close-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [865.0, 210.0, 35.0, 22.0],
					"text": "close"
				}
			},
			{
				"box": {
					"id": "obj-test-section",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 250.0, 200.0, 20.0],
					"text": "Manual Test Controls:",
					"fontsize": 14.0,
					"fontface": 1,
					"textcolor": [0.8, 0.8, 0.9, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-filter-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 280.0, 100.0, 20.0],
					"text": "Filter Cutoff (206)",
					"textcolor": [0.7, 0.7, 0.8, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-filter-dial",
					"maxclass": "dial",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [20.0, 300.0, 80.0, 80.0],
					"size": 1.0,
					"mult": 1.0,
					"floatoutput": 1
				}
			},
			{
				"box": {
					"id": "obj-filter-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [20.0, 390.0, 80.0, 22.0],
					"text": "206 $1"
				}
			},
			{
				"box": {
					"id": "obj-res-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [120.0, 280.0, 100.0, 20.0],
					"text": "Filter Res (207)",
					"textcolor": [0.7, 0.7, 0.8, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-res-dial",
					"maxclass": "dial",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [120.0, 300.0, 80.0, 80.0],
					"size": 1.0,
					"mult": 1.0,
					"floatoutput": 1
				}
			},
			{
				"box": {
					"id": "obj-res-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [120.0, 390.0, 80.0, 22.0],
					"text": "207 $1"
				}
			},
			{
				"box": {
					"id": "obj-osc-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [220.0, 280.0, 100.0, 20.0],
					"text": "Osc A Level (22)",
					"textcolor": [0.7, 0.7, 0.8, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-osc-dial",
					"maxclass": "dial",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [220.0, 300.0, 80.0, 80.0],
					"size": 1.0,
					"mult": 1.0,
					"floatoutput": 1
				}
			},
			{
				"box": {
					"id": "obj-osc-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [220.0, 390.0, 80.0, 22.0],
					"text": "22 $1"
				}
			},
			{
				"box": {
					"id": "obj-wt-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [320.0, 280.0, 100.0, 20.0],
					"text": "WT Pos A (60)",
					"textcolor": [0.7, 0.7, 0.8, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-wt-dial",
					"maxclass": "dial",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["float"],
					"patching_rect": [320.0, 300.0, 80.0, 80.0],
					"size": 1.0,
					"mult": 1.0,
					"floatoutput": 1
				}
			},
			{
				"box": {
					"id": "obj-wt-msg",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [320.0, 390.0, 80.0, 22.0],
					"text": "60 $1"
				}
			},
			{
				"box": {
					"id": "obj-status-led",
					"maxclass": "led",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["int"],
					"patching_rect": [560.0, 80.0, 24.0, 24.0],
					"oncolor": [0.0, 1.0, 0.5, 1.0],
					"offcolor": [0.3, 0.3, 0.3, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-status-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [590.0, 82.0, 60.0, 20.0],
					"text": "Active",
					"textcolor": [0.6, 0.6, 0.7, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-instructions",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 450.0, 400.0, 200.0],
					"text": "USAGE:\n\n1. This device listens on UDP port 9878\n2. Send commands as: set_param <index> <value>\n   Example: set_param 206 0.75\n\n3. Or use named params:\n   set_param_name filter_1_freq 0.5\n\n4. Get param values: get_param <index>\n\n5. Responses sent to UDP port 9879",
					"textcolor": [0.6, 0.6, 0.7, 1.0],
					"fontsize": 12.0,
					"linecount": 12
				}
			},
			{
				"box": {
					"id": "obj-1",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["int"],
					"patching_rect": [560.0, 50.0, 22.0, 22.0],
					"text": "1"
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"source": ["obj-loadbang", 0],
					"destination": ["obj-plug-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-loadbang", 0],
					"destination": ["obj-1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-1", 0],
					"destination": ["obj-status-led", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plug-msg", 0],
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
					"source": ["obj-vst", 3],
					"destination": ["obj-js", 1]
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
					"destination": ["obj-route-cmd", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route-cmd", 0],
					"destination": ["obj-prepend-set", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route-cmd", 1],
					"destination": ["obj-prepend-get", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route-cmd", 2],
					"destination": ["obj-prepend-name", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route-cmd", 3],
					"destination": ["obj-ping-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route-cmd", 4],
					"destination": ["obj-open-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route-cmd", 5],
					"destination": ["obj-close-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-route-cmd", 7],
					"destination": ["obj-prepend-json", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-prepend-set", 0],
					"destination": ["obj-js", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-prepend-get", 0],
					"destination": ["obj-js", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-prepend-name", 0],
					"destination": ["obj-js", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-prepend-json", 0],
					"destination": ["obj-js", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-ping-msg", 0],
					"destination": ["obj-js", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open-msg", 0],
					"destination": ["obj-js", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-close-msg", 0],
					"destination": ["obj-js", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 0],
					"destination": ["obj-vst", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 1],
					"destination": ["obj-print-status", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 1],
					"destination": ["obj-udpsend", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-filter-dial", 0],
					"destination": ["obj-filter-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-filter-msg", 0],
					"destination": ["obj-vst", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-res-dial", 0],
					"destination": ["obj-res-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-res-msg", 0],
					"destination": ["obj-vst", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-osc-dial", 0],
					"destination": ["obj-osc-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-osc-msg", 0],
					"destination": ["obj-vst", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-wt-dial", 0],
					"destination": ["obj-wt-msg", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-wt-msg", 0],
					"destination": ["obj-vst", 0]
				}
			}
		]
	}
}
