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
		"rect": [100.0, 100.0, 900.0, 700.0],
		"openinpresentation": 1,
		"default_fontsize": 11.0,
		"gridsize": [15.0, 15.0],
		"boxes": [
			{
				"box": {
					"id": "obj-panel",
					"maxclass": "panel",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [400.0, 10.0, 340.0, 95.0],
					"presentation": 1,
					"presentation_rect": [0.0, 0.0, 340.0, 95.0],
					"bgcolor": [0.15, 0.15, 0.15, 1.0],
					"bordercolor": [0.4, 0.4, 0.4, 1.0],
					"border": 1
				}
			},
			{
				"box": {
					"id": "obj-title",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [405.0, 12.0, 200.0, 19.0],
					"presentation": 1,
					"presentation_rect": [5.0, 3.0, 200.0, 19.0],
					"text": "BAP Labs VST FX Chain",
					"fontsize": 12.0,
					"fontface": 1,
					"textcolor": [0.9, 0.9, 0.9, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-subtitle",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [405.0, 28.0, 150.0, 19.0],
					"presentation": 1,
					"presentation_rect": [5.0, 18.0, 150.0, 19.0],
					"text": "OSC Port: 9879",
					"fontsize": 10.0,
					"textcolor": [0.6, 0.6, 0.6, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-btn1",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [405.0, 50.0, 35.0, 18.0],
					"presentation": 1,
					"presentation_rect": [5.0, 38.0, 35.0, 18.0],
					"text": "1",
					"bgcolor": [0.3, 0.3, 0.3, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0],
					"fontsize": 10.0
				}
			},
			{
				"box": {
					"id": "obj-btn2",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [445.0, 50.0, 35.0, 18.0],
					"presentation": 1,
					"presentation_rect": [45.0, 38.0, 35.0, 18.0],
					"text": "2",
					"bgcolor": [0.3, 0.3, 0.3, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0],
					"fontsize": 10.0
				}
			},
			{
				"box": {
					"id": "obj-btn3",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [485.0, 50.0, 35.0, 18.0],
					"presentation": 1,
					"presentation_rect": [85.0, 38.0, 35.0, 18.0],
					"text": "3",
					"bgcolor": [0.3, 0.3, 0.3, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0],
					"fontsize": 10.0
				}
			},
			{
				"box": {
					"id": "obj-btn4",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [525.0, 50.0, 35.0, 18.0],
					"presentation": 1,
					"presentation_rect": [125.0, 38.0, 35.0, 18.0],
					"text": "4",
					"bgcolor": [0.3, 0.3, 0.3, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0],
					"fontsize": 10.0
				}
			},
			{
				"box": {
					"id": "obj-btn5",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [565.0, 50.0, 35.0, 18.0],
					"presentation": 1,
					"presentation_rect": [165.0, 38.0, 35.0, 18.0],
					"text": "5",
					"bgcolor": [0.3, 0.3, 0.3, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0],
					"fontsize": 10.0
				}
			},
			{
				"box": {
					"id": "obj-btn6",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [605.0, 50.0, 35.0, 18.0],
					"presentation": 1,
					"presentation_rect": [205.0, 38.0, 35.0, 18.0],
					"text": "6",
					"bgcolor": [0.3, 0.3, 0.3, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0],
					"fontsize": 10.0
				}
			},
			{
				"box": {
					"id": "obj-btn7",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [645.0, 50.0, 35.0, 18.0],
					"presentation": 1,
					"presentation_rect": [245.0, 38.0, 35.0, 18.0],
					"text": "7",
					"bgcolor": [0.3, 0.3, 0.3, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0],
					"fontsize": 10.0
				}
			},
			{
				"box": {
					"id": "obj-btn8",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [685.0, 50.0, 35.0, 18.0],
					"presentation": 1,
					"presentation_rect": [285.0, 38.0, 35.0, 18.0],
					"text": "8",
					"bgcolor": [0.3, 0.3, 0.3, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0],
					"fontsize": 10.0
				}
			},
			{
				"box": {
					"id": "obj-open-label",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [405.0, 70.0, 120.0, 19.0],
					"presentation": 1,
					"presentation_rect": [5.0, 58.0, 120.0, 19.0],
					"text": "Open VST Slot:",
					"fontsize": 10.0,
					"textcolor": [0.7, 0.7, 0.7, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-status",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [405.0, 85.0, 320.0, 19.0],
					"presentation": 1,
					"presentation_rect": [5.0, 75.0, 320.0, 19.0],
					"text": "Ready - Control via OSC or click buttons above",
					"fontsize": 9.0,
					"textcolor": [0.5, 0.8, 0.5, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-open1",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [405.0, 120.0, 35.0, 21.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-open2",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [445.0, 120.0, 35.0, 21.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-open3",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [485.0, 120.0, 35.0, 21.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-open4",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [525.0, 120.0, 35.0, 21.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-open5",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [565.0, 120.0, 35.0, 21.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-open6",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [605.0, 120.0, 35.0, 21.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-open7",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [645.0, 120.0, 35.0, 21.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-open8",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [685.0, 120.0, 35.0, 21.0],
					"text": "open"
				}
			},
			{
				"box": {
					"id": "obj-udp",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [20.0, 20.0, 110.0, 21.0],
					"text": "udpreceive 9879"
				}
			},
			{
				"box": {
					"id": "obj-print-osc",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 20.0, 61.0, 21.0],
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
					"patching_rect": [20.0, 60.0, 360.0, 21.0],
					"text": "js universal_vst_controller.js"
				}
			},
			{
				"box": {
					"id": "obj-print-status",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [340.0, 90.0, 80.0, 21.0],
					"text": "print STATUS"
				}
			},
			{
				"box": {
					"id": "obj-plugin-in-L",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["signal"],
					"patching_rect": [20.0, 150.0, 55.0, 21.0],
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
					"patching_rect": [90.0, 150.0, 55.0, 21.0],
					"text": "plugin~ 2"
				}
			},
			{
				"box": {
					"id": "obj-vst1",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 190.0, 100.0, 21.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-vst2",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 230.0, 100.0, 21.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-vst3",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 270.0, 100.0, 21.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-vst4",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 310.0, 100.0, 21.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-vst5",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 350.0, 100.0, 21.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-vst6",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 390.0, 100.0, 21.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-vst7",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 430.0, 100.0, 21.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-vst8",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "int", "", "", ""],
					"patching_rect": [20.0, 470.0, 100.0, 21.0],
					"text": "vst~ 2 2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-plugout",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [20.0, 510.0, 65.0, 21.0],
					"text": "plugout~"
				}
			},
			{
				"box": {
					"id": "obj-print-params1",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 190.0, 85.0, 21.0],
					"text": "print PARAMS1"
				}
			},
			{
				"box": {
					"id": "obj-print-params2",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 230.0, 85.0, 21.0],
					"text": "print PARAMS2"
				}
			},
			{
				"box": {
					"id": "obj-print-params3",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 270.0, 85.0, 21.0],
					"text": "print PARAMS3"
				}
			},
			{
				"box": {
					"id": "obj-print-params4",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 310.0, 85.0, 21.0],
					"text": "print PARAMS4"
				}
			},
			{
				"box": {
					"id": "obj-print-params5",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 350.0, 85.0, 21.0],
					"text": "print PARAMS5"
				}
			},
			{
				"box": {
					"id": "obj-print-params6",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 390.0, 85.0, 21.0],
					"text": "print PARAMS6"
				}
			},
			{
				"box": {
					"id": "obj-print-params7",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 430.0, 85.0, 21.0],
					"text": "print PARAMS7"
				}
			},
			{
				"box": {
					"id": "obj-print-params8",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [150.0, 470.0, 85.0, 21.0],
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
					"source": ["obj-btn1", 0],
					"destination": ["obj-open1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-btn2", 0],
					"destination": ["obj-open2", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-btn3", 0],
					"destination": ["obj-open3", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-btn4", 0],
					"destination": ["obj-open4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-btn5", 0],
					"destination": ["obj-open5", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-btn6", 0],
					"destination": ["obj-open6", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-btn7", 0],
					"destination": ["obj-open7", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-btn8", 0],
					"destination": ["obj-open8", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open1", 0],
					"destination": ["obj-vst1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open2", 0],
					"destination": ["obj-vst2", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open3", 0],
					"destination": ["obj-vst3", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open4", 0],
					"destination": ["obj-vst4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open5", 0],
					"destination": ["obj-vst5", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open6", 0],
					"destination": ["obj-vst6", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open7", 0],
					"destination": ["obj-vst7", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-open8", 0],
					"destination": ["obj-vst8", 0]
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
					"source": ["obj-vst2", 2],
					"destination": ["obj-print-params2", 0]
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
					"source": ["obj-vst4", 2],
					"destination": ["obj-print-params4", 0]
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
					"source": ["obj-vst6", 2],
					"destination": ["obj-print-params6", 0]
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
					"source": ["obj-vst8", 2],
					"destination": ["obj-print-params8", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-L", 0],
					"destination": ["obj-vst1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in-R", 0],
					"destination": ["obj-vst1", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst1", 0],
					"destination": ["obj-vst2", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst1", 1],
					"destination": ["obj-vst2", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst2", 0],
					"destination": ["obj-vst3", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst2", 1],
					"destination": ["obj-vst3", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst3", 0],
					"destination": ["obj-vst4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst3", 1],
					"destination": ["obj-vst4", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst4", 0],
					"destination": ["obj-vst5", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst4", 1],
					"destination": ["obj-vst5", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst5", 0],
					"destination": ["obj-vst6", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst5", 1],
					"destination": ["obj-vst6", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst6", 0],
					"destination": ["obj-vst7", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst6", 1],
					"destination": ["obj-vst7", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst7", 0],
					"destination": ["obj-vst8", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst7", 1],
					"destination": ["obj-vst8", 1]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst8", 0],
					"destination": ["obj-plugout", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-vst8", 1],
					"destination": ["obj-plugout", 1]
				}
			}
		]
	}
}
