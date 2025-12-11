{
	"patcher": {
		"fileversion": 1,
		"appversion": {
			"major": 9,
			"minor": 0,
			"revision": 0,
			"architecture": "x64",
			"modernui": 1
		},
		"classnamespace": "box",
		"rect": [100.0, 100.0, 1200.0, 800.0],
		"gridsize": [15.0, 15.0],
		"boxes": [
			{
				"box": {
					"id": "obj-title",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 10.0, 400.0, 24.0],
					"text": "UNIVERSAL VST CONTROLLER (8 slots, port 9878)",
					"fontsize": 16.0,
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-instructions",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 35.0, 500.0, 20.0],
					"text": "OSC: /register <slot> <path> | /<slot>/param <idx> <val> | /<slot>/open | /list",
					"fontsize": 11.0
				}
			},
			{
				"box": {
					"id": "obj-udp",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [20.0, 70.0, 110.0, 22.0],
					"text": "udpreceive 9878"
				}
			},
			{
				"box": {
					"id": "obj-print-osc",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 70.0, 70.0, 22.0],
					"text": "print OSC"
				}
			},
			{
				"box": {
					"id": "obj-js",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 9,
					"outlettype": ["", "", "", "", "", "", "", "", ""],
					"patching_rect": [20.0, 110.0, 600.0, 22.0],
					"text": "js universal_vst_controller.js"
				}
			},
			{
				"box": {
					"id": "obj-print-status",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [560.0, 150.0, 80.0, 22.0],
					"text": "print STATUS"
				}
			},
			{
				"box": {
					"id": "obj-slot1-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 160.0, 80.0, 20.0],
					"text": "Slot 1",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-vst1",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 180.0, 120.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac1",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [20.0, 220.0, 60.0, 22.0],
					"text": "dac~ 1 2"
				}
			},
			{
				"box": {
					"id": "obj-print-params1",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [90.0, 220.0, 85.0, 22.0],
					"text": "print PARAMS1"
				}
			},
			{
				"box": {
					"id": "obj-slot2-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [160.0, 160.0, 80.0, 20.0],
					"text": "Slot 2",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-vst2",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [160.0, 180.0, 120.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac2",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [160.0, 220.0, 60.0, 22.0],
					"text": "dac~ 3 4"
				}
			},
			{
				"box": {
					"id": "obj-print-params2",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [230.0, 220.0, 85.0, 22.0],
					"text": "print PARAMS2"
				}
			},
			{
				"box": {
					"id": "obj-slot3-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [300.0, 160.0, 80.0, 20.0],
					"text": "Slot 3",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-vst3",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [300.0, 180.0, 120.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac3",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [300.0, 220.0, 60.0, 22.0],
					"text": "dac~ 5 6"
				}
			},
			{
				"box": {
					"id": "obj-print-params3",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [370.0, 220.0, 85.0, 22.0],
					"text": "print PARAMS3"
				}
			},
			{
				"box": {
					"id": "obj-slot4-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [440.0, 160.0, 80.0, 20.0],
					"text": "Slot 4",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-vst4",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [440.0, 180.0, 120.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac4",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [440.0, 220.0, 60.0, 22.0],
					"text": "dac~ 7 8"
				}
			},
			{
				"box": {
					"id": "obj-print-params4",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [510.0, 220.0, 85.0, 22.0],
					"text": "print PARAMS4"
				}
			},
			{
				"box": {
					"id": "obj-slot5-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [20.0, 270.0, 80.0, 20.0],
					"text": "Slot 5",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-vst5",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 290.0, 120.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac5",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [20.0, 330.0, 68.0, 22.0],
					"text": "dac~ 9 10"
				}
			},
			{
				"box": {
					"id": "obj-print-params5",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [90.0, 330.0, 85.0, 22.0],
					"text": "print PARAMS5"
				}
			},
			{
				"box": {
					"id": "obj-slot6-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [160.0, 270.0, 80.0, 20.0],
					"text": "Slot 6",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-vst6",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [160.0, 290.0, 120.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac6",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [160.0, 330.0, 74.0, 22.0],
					"text": "dac~ 11 12"
				}
			},
			{
				"box": {
					"id": "obj-print-params6",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [240.0, 330.0, 85.0, 22.0],
					"text": "print PARAMS6"
				}
			},
			{
				"box": {
					"id": "obj-slot7-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [300.0, 270.0, 80.0, 20.0],
					"text": "Slot 7",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-vst7",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [300.0, 290.0, 120.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac7",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [300.0, 330.0, 74.0, 22.0],
					"text": "dac~ 13 14"
				}
			},
			{
				"box": {
					"id": "obj-print-params7",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [380.0, 330.0, 85.0, 22.0],
					"text": "print PARAMS7"
				}
			},
			{
				"box": {
					"id": "obj-slot8-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [440.0, 270.0, 80.0, 20.0],
					"text": "Slot 8",
					"fontface": 1
				}
			},
			{
				"box": {
					"id": "obj-vst8",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [440.0, 290.0, 120.0, 22.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-dac8",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [440.0, 330.0, 74.0, 22.0],
					"text": "dac~ 15 16"
				}
			},
			{
				"box": {
					"id": "obj-print-params8",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [520.0, 330.0, 85.0, 22.0],
					"text": "print PARAMS8"
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"source": ["obj-udp", 0],
					"destination": ["obj-print-osc", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-udp", 0],
					"destination": ["obj-js", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 8],
					"destination": ["obj-print-status", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 0],
					"destination": ["obj-vst1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 1],
					"destination": ["obj-vst2", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 2],
					"destination": ["obj-vst3", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 3],
					"destination": ["obj-vst4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 4],
					"destination": ["obj-vst5", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 5],
					"destination": ["obj-vst6", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 6],
					"destination": ["obj-vst7", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-js", 7],
					"destination": ["obj-vst8", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst1", 0],
					"destination": ["obj-dac1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst1", 1],
					"destination": ["obj-dac1", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst1", 2],
					"destination": ["obj-print-params1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst2", 0],
					"destination": ["obj-dac2", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst2", 1],
					"destination": ["obj-dac2", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst2", 2],
					"destination": ["obj-print-params2", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst3", 0],
					"destination": ["obj-dac3", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst3", 1],
					"destination": ["obj-dac3", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst3", 2],
					"destination": ["obj-print-params3", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst4", 0],
					"destination": ["obj-dac4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst4", 1],
					"destination": ["obj-dac4", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst4", 2],
					"destination": ["obj-print-params4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst5", 0],
					"destination": ["obj-dac5", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst5", 1],
					"destination": ["obj-dac5", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst5", 2],
					"destination": ["obj-print-params5", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst6", 0],
					"destination": ["obj-dac6", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst6", 1],
					"destination": ["obj-dac6", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst6", 2],
					"destination": ["obj-print-params6", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst7", 0],
					"destination": ["obj-dac7", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst7", 1],
					"destination": ["obj-dac7", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst7", 2],
					"destination": ["obj-print-params7", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst8", 0],
					"destination": ["obj-dac8", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst8", 1],
					"destination": ["obj-dac8", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst8", 2],
					"destination": ["obj-print-params8", 0]
				}
			}
		]
	}
}
