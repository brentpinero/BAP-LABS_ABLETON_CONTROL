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
					"fontsize": 24.0,
					"id": "obj-1",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [15.0, 15.0, 300.0, 40.0],
					"presentation": 1,
					"presentation_rect": [20.0, 10.0, 300.0, 40.0],
					"text": "M1 by Bap Labs",
					"textcolor": [0.0, 1.0, 0.95, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-2",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [15.0, 60.0, 400.0, 20.0],
					"presentation": 1,
					"presentation_rect": [320.0, 20.0, 150.0, 20.0],
					"text": "AI Preset Generator"
				}
			},
			{
				"box": {
					"bgcolor": [0.0, 1.0, 0.0, 1.0],
					"id": "obj-status-led",
					"maxclass": "led",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["int"],
					"patching_rect": [500.0, 20.0, 20.0, 20.0],
					"presentation": 1,
					"presentation_rect": [750.0, 20.0, 30.0, 30.0]
				}
			},
			{
				"box": {
					"id": "obj-status-text",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [530.0, 20.0, 100.0, 20.0],
					"presentation": 1,
					"presentation_rect": [700.0, 25.0, 50.0, 20.0],
					"text": "READY",
					"textcolor": [0.0, 1.0, 0.0, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-loadbang",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [15.0, 100.0, 70.0, 22.0],
					"text": "loadbang"
				}
			},
			{
				"box": {
					"id": "obj-load-serum",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [15.0, 130.0, 120.0, 22.0],
					"text": "plug_vst3 Serum2"
				}
			},
			{
				"box": {
					"id": "obj-vst",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 8,
					"outlettype": ["signal", "signal", "", "list", "", "", "", ""],
					"patching_rect": [15.0, 200.0, 400.0, 22.0],
					"text": "vst~ 2 2 Serum2",
					"saved_object_attributes": {
						"parameter_enable": 0,
						"prefer": "VST3"
					}
				}
			},
			{
				"box": {
					"id": "obj-js-controller",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", ""],
					"patching_rect": [15.0, 250.0, 200.0, 22.0],
					"text": "js M1_chat_controller.js"
				}
			},
			{
				"box": {
					"id": "obj-shell-bridge",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [230.0, 250.0, 200.0, 22.0],
					"text": "shell python max_api_bridge.py"
				}
			},
			{
				"box": {
					"id": "obj-chat-display",
					"maxclass": "textedit",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": ["", "int", "", ""],
					"patching_rect": [15.0, 300.0, 600.0, 300.0],
					"presentation": 1,
					"presentation_rect": [20.0, 60.0, 760.0, 340.0],
					"readonly": 1,
					"bgcolor": [0.04, 0.05, 0.1, 1.0],
					"textcolor": [0.9, 0.9, 0.9, 1.0],
					"fontsize": 12.0,
					"text": "Welcome to M1 by Bap Labs\nAI-powered Serum preset generator\n\nWaiting for server connection..."
				}
			},
			{
				"box": {
					"id": "obj-quick-bass",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [15.0, 620.0, 80.0, 30.0],
					"presentation": 1,
					"presentation_rect": [20.0, 410.0, 80.0, 30.0],
					"text": "Bass",
					"bgcolor": [0.2, 0.2, 0.3, 1.0],
					"textcolor": [0.0, 1.0, 0.95, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-quick-lead",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [105.0, 620.0, 80.0, 30.0],
					"presentation": 1,
					"presentation_rect": [110.0, 410.0, 80.0, 30.0],
					"text": "Lead",
					"bgcolor": [0.2, 0.2, 0.3, 1.0],
					"textcolor": [0.0, 1.0, 0.95, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-quick-pad",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [195.0, 620.0, 80.0, 30.0],
					"presentation": 1,
					"presentation_rect": [200.0, 410.0, 80.0, 30.0],
					"text": "Pad",
					"bgcolor": [0.2, 0.2, 0.3, 1.0],
					"textcolor": [0.0, 1.0, 0.95, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-quick-pluck",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [285.0, 620.0, 80.0, 30.0],
					"presentation": 1,
					"presentation_rect": [290.0, 410.0, 80.0, 30.0],
					"text": "Pluck",
					"bgcolor": [0.2, 0.2, 0.3, 1.0],
					"textcolor": [0.0, 1.0, 0.95, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-quick-fx",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [375.0, 620.0, 80.0, 30.0],
					"presentation": 1,
					"presentation_rect": [380.0, 410.0, 80.0, 30.0],
					"text": "FX",
					"bgcolor": [0.2, 0.2, 0.3, 1.0],
					"textcolor": [0.0, 1.0, 0.95, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-user-input",
					"maxclass": "textedit",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": ["", "int", "", ""],
					"patching_rect": [15.0, 670.0, 550.0, 40.0],
					"presentation": 1,
					"presentation_rect": [20.0, 450.0, 660.0, 40.0],
					"bgcolor": [0.1, 0.1, 0.15, 1.0],
					"textcolor": [0.9, 0.9, 0.9, 1.0],
					"fontsize": 14.0,
					"text": "Describe your sound..."
				}
			},
			{
				"box": {
					"id": "obj-send-button",
					"maxclass": "textbutton",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"],
					"patching_rect": [575.0, 670.0, 60.0, 40.0],
					"presentation": 1,
					"presentation_rect": [690.0, 450.0, 90.0, 40.0],
					"text": "→ Send",
					"bgcolor": [0.0, 0.8, 0.75, 1.0],
					"textcolor": [1.0, 1.0, 1.0, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-progress-bar",
					"maxclass": "slider",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [15.0, 730.0, 600.0, 20.0],
					"presentation": 1,
					"presentation_rect": [20.0, 500.0, 760.0, 10.0],
					"bgcolor": [0.2, 0.2, 0.3, 1.0],
					"elementcolor": [0.0, 1.0, 0.95, 1.0],
					"min": 0.0,
					"max": 100.0
				}
			},
			{
				"box": {
					"id": "obj-dac",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": ["signal", "signal"],
					"patching_rect": [15.0, 770.0, 60.0, 22.0],
					"text": "ezdac~"
				}
			},
			{
				"box": {
					"id": "obj-route-ui",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 7,
					"outlettype": ["", "", "", "", "", "", ""],
					"patching_rect": [650.0, 300.0, 400.0, 22.0],
					"text": "route chat_message status progress server_status serum_status error"
				}
			},
			{
				"box": {
					"id": "obj-prepend-send",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [575.0, 640.0, 120.0, 22.0],
					"text": "prepend send_message"
				}
			},
			{
				"box": {
					"id": "obj-prepend-bass",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [15.0, 655.0, 80.0, 22.0],
					"text": "quick_bass"
				}
			},
			{
				"box": {
					"id": "obj-prepend-lead",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [105.0, 655.0, 80.0, 22.0],
					"text": "quick_lead"
				}
			},
			{
				"box": {
					"id": "obj-prepend-pad",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [195.0, 655.0, 80.0, 22.0],
					"text": "quick_pad"
				}
			},
			{
				"box": {
					"id": "obj-prepend-pluck",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [285.0, 655.0, 80.0, 22.0],
					"text": "quick_pluck"
				}
			},
			{
				"box": {
					"id": "obj-prepend-fx",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""],
					"patching_rect": [375.0, 655.0, 80.0, 22.0],
					"text": "quick_fx"
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"destination": ["obj-load-serum", 0],
					"source": ["obj-loadbang", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-vst", 0],
					"source": ["obj-load-serum", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-js-controller", 0],
					"source": ["obj-vst", 3]
				}
			},
			{
				"patchline": {
					"destination": ["obj-dac", 0],
					"source": ["obj-vst", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-dac", 1],
					"source": ["obj-vst", 1]
				}
			},
			{
				"patchline": {
					"destination": ["obj-vst", 0],
					"source": ["obj-js-controller", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-shell-bridge", 0],
					"source": ["obj-js-controller", 1]
				}
			},
			{
				"patchline": {
					"destination": ["obj-route-ui", 0],
					"source": ["obj-js-controller", 2]
				}
			},
			{
				"patchline": {
					"destination": ["obj-js-controller", 0],
					"source": ["obj-shell-bridge", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-chat-display", 0],
					"source": ["obj-route-ui", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-status-text", 0],
					"source": ["obj-route-ui", 1]
				}
			},
			{
				"patchline": {
					"destination": ["obj-progress-bar", 0],
					"source": ["obj-route-ui", 2]
				}
			},
			{
				"patchline": {
					"destination": ["obj-status-led", 0],
					"source": ["obj-route-ui", 3]
				}
			},
			{
				"patchline": {
					"destination": ["obj-prepend-send", 0],
					"source": ["obj-user-input", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-prepend-send", 0],
					"source": ["obj-send-button", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-js-controller", 0],
					"source": ["obj-prepend-send", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-js-controller", 0],
					"source": ["obj-prepend-bass", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-prepend-bass", 0],
					"source": ["obj-quick-bass", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-js-controller", 0],
					"source": ["obj-prepend-lead", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-prepend-lead", 0],
					"source": ["obj-quick-lead", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-js-controller", 0],
					"source": ["obj-prepend-pad", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-prepend-pad", 0],
					"source": ["obj-quick-pad", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-js-controller", 0],
					"source": ["obj-prepend-pluck", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-prepend-pluck", 0],
					"source": ["obj-quick-pluck", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-js-controller", 0],
					"source": ["obj-prepend-fx", 0]
				}
			},
			{
				"patchline": {
					"destination": ["obj-prepend-fx", 0],
					"source": ["obj-quick-fx", 0]
				}
			}
		]
	}
}
