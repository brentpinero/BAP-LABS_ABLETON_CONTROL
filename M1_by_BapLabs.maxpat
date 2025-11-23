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
		"rect": [100.0, 100.0, 900.0, 600.0],
		"bgcolor": [0.062745, 0.086275, 0.160784, 1.0],
		"editing_bgcolor": [0.062745, 0.086275, 0.160784, 1.0],
		"openinpresentation": 1,
		"boxes": [
			{
				"box": {
					"id": "obj-1",
					"maxclass": "newobj",
					"text": "vst~ 2 2 Serum2",
					"patching_rect": [20.0, 50.0, 120.0, 22.0],
					"numinlets": 2,
					"numoutlets": 4,
					"outlettype": ["signal", "signal", "", ""]
				}
			},
			{
				"box": {
					"id": "obj-2",
					"maxclass": "newobj",
					"text": "loadbang",
					"patching_rect": [20.0, 20.0, 60.0, 22.0],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["bang"]
				}
			},
			{
				"box": {
					"id": "obj-3",
					"maxclass": "message",
					"text": "plug Serum2, wopen",
					"patching_rect": [20.0, 35.0, 140.0, 22.0],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-4",
					"maxclass": "newobj",
					"text": "js M1_chat_controller.js",
					"patching_rect": [200.0, 100.0, 150.0, 22.0],
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", ""]
				}
			},
			{
				"box": {
					"id": "obj-5",
					"maxclass": "newobj",
					"text": "node.script max_api_bridge.js @autostart 1",
					"patching_rect": [200.0, 200.0, 250.0, 22.0],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": ["", ""]
				}
			},
			{
				"box": {
					"id": "obj-6",
					"maxclass": "textedit",
					"text": "Welcome to M1 by Bap Labs\\nAI-powered Serum preset generator\\n\\nWaiting for server...",
					"patching_rect": [500.0, 50.0, 780.0, 360.0],
					"presentation_rect": [20.0, 80.0, 860.0, 390.0],
					"presentation": 1,
					"bgcolor": [0.101961, 0.121569, 0.180392, 1.0],
					"textcolor": [0.862745, 0.878431, 0.921569, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 13.0,
					"readonly": 1,
					"wordwrap": 1,
					"rounded": 12.0,
					"border": 0,
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": ["", "int", "", ""]
				}
			},
			{
				"box": {
					"id": "obj-7",
					"maxclass": "textedit",
					"text": "",
					"hint": "Describe your sound...",
					"patching_rect": [500.0, 450.0, 720.0, 50.0],
					"presentation_rect": [20.0, 520.0, 740.0, 50.0],
					"presentation": 1,
					"bgcolor": [0.133333, 0.156863, 0.215686, 1.0],
					"textcolor": [0.862745, 0.878431, 0.921569, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 14.0,
					"wordwrap": 0,
					"lines": 1,
					"rounded": 25.0,
					"border": 0,
					"outputmode": 0,
					"keymode": 1,
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": ["", "int", "", ""]
				}
			},
			{
				"box": {
					"id": "obj-8",
					"maxclass": "textbutton",
					"text": "→ Send",
					"patching_rect": [1230.0, 450.0, 100.0, 50.0],
					"presentation_rect": [770.0, 520.0, 110.0, 50.0],
					"presentation": 1,
					"bgcolor": [0.0, 1.0, 0.949020, 1.0],
					"bgoncolor": [0.0, 0.8, 0.8, 1.0],
					"textcolor": [0.062745, 0.086275, 0.160784, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 16.0,
					"fontface": 1,
					"rounded": 25.0,
					"border": 0,
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"]
				}
			},
			{
				"box": {
					"id": "obj-9",
					"maxclass": "comment",
					"text": "M1",
					"patching_rect": [500.0, 10.0, 100.0, 28.0],
					"presentation_rect": [20.0, 15.0, 100.0, 40.0],
					"presentation": 1,
					"textcolor": [0.0, 1.0, 0.949020, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 32.0,
					"fontface": 1,
					"numinlets": 1,
					"numoutlets": 0
				}
			},
			{
				"box": {
					"id": "obj-10",
					"maxclass": "comment",
					"text": "by Bap Labs",
					"patching_rect": [610.0, 20.0, 120.0, 20.0],
					"presentation_rect": [100.0, 33.0, 120.0, 22.0],
					"presentation": 1,
					"textcolor": [0.501961, 0.549020, 0.639216, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 14.0,
					"numinlets": 1,
					"numoutlets": 0
				}
			},
			{
				"box": {
					"id": "obj-11",
					"maxclass": "led",
					"patching_rect": [750.0, 15.0, 20.0, 20.0],
					"presentation_rect": [850.0, 28.0, 20.0, 20.0],
					"presentation": 1,
					"oncolor": [0.0, 1.0, 0.0, 1.0],
					"offcolor": [0.301961, 0.301961, 0.301961, 1.0],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": ["int"]
				}
			},
			{
				"box": {
					"id": "obj-12",
					"maxclass": "comment",
					"text": "Ready",
					"patching_rect": [780.0, 15.0, 50.0, 20.0],
					"presentation_rect": [810.0, 28.0, 50.0, 20.0],
					"presentation": 1,
					"textcolor": [0.501961, 0.549020, 0.639216, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 12.0,
					"numinlets": 1,
					"numoutlets": 0
				}
			},
			{
				"box": {
					"id": "obj-13",
					"maxclass": "textbutton",
					"text": "Bass",
					"patching_rect": [500.0, 520.0, 100.0, 32.0],
					"presentation_rect": [20.0, 480.0, 100.0, 32.0],
					"presentation": 1,
					"bgcolor": [0.156863, 0.180392, 0.247059, 1.0],
					"bgoncolor": [0.0, 1.0, 0.949020, 0.3],
					"textcolor": [0.0, 1.0, 0.949020, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 13.0,
					"fontface": 1,
					"rounded": 16.0,
					"border": 0,
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"]
				}
			},
			{
				"box": {
					"id": "obj-14",
					"maxclass": "textbutton",
					"text": "Lead",
					"patching_rect": [610.0, 520.0, 100.0, 32.0],
					"presentation_rect": [130.0, 480.0, 100.0, 32.0],
					"presentation": 1,
					"bgcolor": [0.156863, 0.180392, 0.247059, 1.0],
					"bgoncolor": [0.0, 1.0, 0.949020, 0.3],
					"textcolor": [0.0, 1.0, 0.949020, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 13.0,
					"fontface": 1,
					"rounded": 16.0,
					"border": 0,
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"]
				}
			},
			{
				"box": {
					"id": "obj-15",
					"maxclass": "textbutton",
					"text": "Pad",
					"patching_rect": [720.0, 520.0, 100.0, 32.0],
					"presentation_rect": [240.0, 480.0, 100.0, 32.0],
					"presentation": 1,
					"bgcolor": [0.156863, 0.180392, 0.247059, 1.0],
					"bgoncolor": [0.0, 1.0, 0.949020, 0.3],
					"textcolor": [0.0, 1.0, 0.949020, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 13.0,
					"fontface": 1,
					"rounded": 16.0,
					"border": 0,
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"]
				}
			},
			{
				"box": {
					"id": "obj-16",
					"maxclass": "textbutton",
					"text": "Pluck",
					"patching_rect": [830.0, 520.0, 100.0, 32.0],
					"presentation_rect": [350.0, 480.0, 100.0, 32.0],
					"presentation": 1,
					"bgcolor": [0.156863, 0.180392, 0.247059, 1.0],
					"bgoncolor": [0.0, 1.0, 0.949020, 0.3],
					"textcolor": [0.0, 1.0, 0.949020, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 13.0,
					"fontface": 1,
					"rounded": 16.0,
					"border": 0,
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"]
				}
			},
			{
				"box": {
					"id": "obj-17",
					"maxclass": "textbutton",
					"text": "FX",
					"patching_rect": [940.0, 520.0, 100.0, 32.0],
					"presentation_rect": [460.0, 480.0, 100.0, 32.0],
					"presentation": 1,
					"bgcolor": [0.156863, 0.180392, 0.247059, 1.0],
					"bgoncolor": [0.0, 1.0, 0.949020, 0.3],
					"textcolor": [0.0, 1.0, 0.949020, 1.0],
					"fontname": "SF Pro Display",
					"fontsize": 13.0,
					"fontface": 1,
					"rounded": 16.0,
					"border": 0,
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": ["", "", "int"]
				}
			},
			{
				"box": {
					"id": "obj-18",
					"maxclass": "slider",
					"patching_rect": [500.0, 560.0, 780.0, 12.0],
					"presentation_rect": [20.0, 578.0, 860.0, 12.0],
					"presentation": 1,
					"bgcolor": [0.156863, 0.180392, 0.247059, 1.0],
					"floatoutput": 1,
					"size": 100.0,
					"mult": 1.0,
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""],
					"orientation": 1
				}
			},
			{
				"box": {
					"id": "obj-19",
					"maxclass": "newobj",
					"text": "prepend",
					"patching_rect": [500.0, 510.0, 60.0, 22.0],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-20",
					"maxclass": "newobj",
					"text": "route chat_message status progress serum_status server_status error complete",
					"patching_rect": [400.0, 300.0, 500.0, 22.0],
					"numinlets": 1,
					"numoutlets": 8,
					"outlettype": ["", "", "", "", "", "", "", ""]
				}
			},
			{
				"box": {
					"id": "obj-21",
					"maxclass": "newobj",
					"text": "prepend append",
					"patching_rect": [400.0, 350.0, 100.0, 22.0],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-22",
					"maxclass": "message",
					"text": "quick_bass",
					"patching_rect": [500.0, 480.0, 80.0, 22.0],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-23",
					"maxclass": "message",
					"text": "quick_lead",
					"patching_rect": [590.0, 480.0, 80.0, 22.0],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-24",
					"maxclass": "message",
					"text": "quick_pad",
					"patching_rect": [680.0, 480.0, 80.0, 22.0],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-25",
					"maxclass": "message",
					"text": "quick_pluck",
					"patching_rect": [770.0, 480.0, 80.0, 22.0],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-26",
					"maxclass": "message",
					"text": "quick_fx",
					"patching_rect": [860.0, 480.0, 80.0, 22.0],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-27",
					"maxclass": "newobj",
					"text": "prepend send_message",
					"patching_rect": [500.0, 420.0, 140.0, 22.0],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-31",
					"maxclass": "newobj",
					"text": "route text",
					"patching_rect": [500.0, 390.0, 70.0, 22.0],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": ["", ""]
				}
			},
			{
				"box": {
					"id": "obj-28",
					"maxclass": "newobj",
					"text": "prepend api_response",
					"patching_rect": [200.0, 240.0, 140.0, 22.0],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [""]
				}
			},
			{
				"box": {
					"id": "obj-30",
					"maxclass": "message",
					"text": "bang",
					"patching_rect": [1230.0, 410.0, 40.0, 22.0],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [""]
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"source": ["obj-2", 0],
					"destination": ["obj-3", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-3", 0],
					"destination": ["obj-1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-4", 0],
					"destination": ["obj-1", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-4", 1],
					"destination": ["obj-5", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-4", 2],
					"destination": ["obj-20", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-5", 0],
					"destination": ["obj-28", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-28", 0],
					"destination": ["obj-4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-1", 3],
					"destination": ["obj-4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-7", 0],
					"destination": ["obj-31", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-31", 0],
					"destination": ["obj-27", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-8", 0],
					"destination": ["obj-30", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-30", 0],
					"destination": ["obj-7", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-27", 0],
					"destination": ["obj-4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-13", 0],
					"destination": ["obj-22", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-14", 0],
					"destination": ["obj-23", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-15", 0],
					"destination": ["obj-24", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-16", 0],
					"destination": ["obj-25", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-17", 0],
					"destination": ["obj-26", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-22", 0],
					"destination": ["obj-4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-23", 0],
					"destination": ["obj-4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-24", 0],
					"destination": ["obj-4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-25", 0],
					"destination": ["obj-4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-26", 0],
					"destination": ["obj-4", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-20", 0],
					"destination": ["obj-21", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-21", 0],
					"destination": ["obj-6", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-20", 2],
					"destination": ["obj-18", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-20", 3],
					"destination": ["obj-11", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-20", 4],
					"destination": ["obj-11", 0]
				}
			}
		]
	}
}
