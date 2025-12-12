{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 9,
			"minor" : 0,
			"revision" : 9,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 78.0, 100.0, 1400.0, 795.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontface" : 1,
					"fontsize" : 16.0,
					"id" : "obj-title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 10.0, 400.0, 24.0 ],
					"text" : "BAP LABS VST HUB (Instrument - 8 synth slots)"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "obj-instructions",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 35.0, 600.0, 19.0 ],
					"text" : "OSC port 9878 | /register <slot> <path> | /<slot>/param <idx> <val> | /select <slot>"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-midiin",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 700.0, 70.0, 50.0, 22.0 ],
					"text" : "midiin"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-midiparse",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 8,
					"outlettype" : [ "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 700.0, 100.0, 92.0, 22.0 ],
					"text" : "midiparse"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "obj-midiout-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 700.0, 50.0, 120.0, 18.0 ],
					"text" : "MIDI from Ableton"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 20.0, 70.0, 110.0, 22.0 ],
					"text" : "udpreceive 9878"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-osc",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 150.0, 70.0, 70.0, 22.0 ],
					"text" : "print OSC"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-js",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 9,
					"outlettype" : [ "", "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 20.0, 110.0, 650.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "universal_vst_controller.js",
						"parameter_enable" : 0
					}
,
					"text" : "js universal_vst_controller.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-route-status",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 600.0, 140.0, 120.0, 22.0 ],
					"text" : "route select pong"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-status",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 680.0, 170.0, 81.0, 22.0 ],
					"text" : "print STATUS"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-select-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 850.0, 50.0, 113.0, 20.0 ],
					"text" : "Output Slot Select"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-slot-select",
					"maxclass" : "number",
					"maximum" : 8,
					"minimum" : 1,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 850.0, 70.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-slot1-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 160.0, 80.0, 20.0 ],
					"text" : "Slot 1"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-vst1",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 20.0, 180.0, 120.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, ";" ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0,
						"parameter_mappable" : 0,
						"prefer" : "VST3"
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{

						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "",
									"origin" : "",
									"type" : "AudioUnit",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{

									}
,
									"fileref" : 									{
										"name" : "",
										"filename" : ".maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "41bba6f71004ab9828fcb7e98568db69"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-params1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 100.0, 210.0, 92.0, 22.0 ],
					"text" : "print PARAMS1"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-slot2-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 160.0, 160.0, 80.0, 20.0 ],
					"text" : "Slot 2"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-vst2",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 160.0, 180.0, 120.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, ";" ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0,
						"parameter_mappable" : 0,
						"prefer" : "VST3"
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{

						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "",
									"origin" : "",
									"type" : "AudioUnit",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{

									}
,
									"fileref" : 									{
										"name" : "",
										"filename" : "_20251211.maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "f72cf1f20c22eb07eccdbb2ea7de9f21"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-params2",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 240.0, 210.0, 92.0, 22.0 ],
					"text" : "print PARAMS2"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-slot3-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 300.0, 160.0, 80.0, 20.0 ],
					"text" : "Slot 3"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-vst3",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 300.0, 180.0, 120.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, ";" ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0,
						"parameter_mappable" : 0,
						"prefer" : "VST3"
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{

						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "",
									"origin" : "",
									"type" : "AudioUnit",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{

									}
,
									"fileref" : 									{
										"name" : "",
										"filename" : "_20251211_1.maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "c009cb0a7ff2b7773747fc43876c1e2f"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-params3",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 380.0, 210.0, 92.0, 22.0 ],
					"text" : "print PARAMS3"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-slot4-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 440.0, 160.0, 80.0, 20.0 ],
					"text" : "Slot 4"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-vst4",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 440.0, 180.0, 120.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, ";" ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0,
						"parameter_mappable" : 0,
						"prefer" : "VST3"
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{

						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "",
									"origin" : "",
									"type" : "AudioUnit",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{

									}
,
									"fileref" : 									{
										"name" : "",
										"filename" : "_20251211_2.maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "10a2351cc5909af228b477224814627a"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-params4",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 520.0, 210.0, 92.0, 22.0 ],
					"text" : "print PARAMS4"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-slot5-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 250.0, 80.0, 20.0 ],
					"text" : "Slot 5"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-vst5",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 20.0, 270.0, 120.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, ";" ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0,
						"parameter_mappable" : 0,
						"prefer" : "VST3"
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{

						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "",
									"origin" : "",
									"type" : "AudioUnit",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{

									}
,
									"fileref" : 									{
										"name" : "",
										"filename" : "_20251211_3.maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "c05f47816c1b734a637beebda5c1a9cc"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-params5",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 100.0, 300.0, 92.0, 22.0 ],
					"text" : "print PARAMS5"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-slot6-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 160.0, 250.0, 80.0, 20.0 ],
					"text" : "Slot 6"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-vst6",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 160.0, 270.0, 120.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, ";" ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0,
						"parameter_mappable" : 0,
						"prefer" : "VST3"
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{

						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "",
									"origin" : "",
									"type" : "AudioUnit",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{

									}
,
									"fileref" : 									{
										"name" : "",
										"filename" : "_20251211_4.maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "e5af985ff0831c69d1d71a42dfbfab10"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-params6",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 240.0, 300.0, 92.0, 22.0 ],
					"text" : "print PARAMS6"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-slot7-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 300.0, 250.0, 80.0, 20.0 ],
					"text" : "Slot 7"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-vst7",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 300.0, 270.0, 120.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, ";" ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0,
						"parameter_mappable" : 0,
						"prefer" : "VST3"
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{

						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "",
									"origin" : "",
									"type" : "AudioUnit",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{

									}
,
									"fileref" : 									{
										"name" : "",
										"filename" : "_20251211_5.maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "2196e5684bc12e07befc91480bece8c1"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-params7",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 380.0, 300.0, 92.0, 22.0 ],
					"text" : "print PARAMS7"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-slot8-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 440.0, 250.0, 80.0, 20.0 ],
					"text" : "Slot 8"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-vst8",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 440.0, 270.0, 120.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, ";" ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0,
						"parameter_mappable" : 0,
						"prefer" : "VST3"
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{

						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "",
									"origin" : "",
									"type" : "AudioUnit",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{

									}
,
									"fileref" : 									{
										"name" : "",
										"filename" : "_20251211_6.maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "1e841d846b935a029ddacf1c5be435b6"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-print-params8",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 520.0, 300.0, 92.0, 22.0 ],
					"text" : "print PARAMS8"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-selector-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 300.0, 407.0, 150.0, 20.0 ],
					"text" : "Output Selector (L)"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-selector-L",
					"maxclass" : "newobj",
					"numinlets" : 9,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 420.0, 406.0, 200.0, 22.0 ],
					"text" : "selector~ 8"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-selector-R",
					"maxclass" : "newobj",
					"numinlets" : 9,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 700.0, 400.0, 200.0, 22.0 ],
					"text" : "selector~ 8"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-selector-R-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 400.0, 100.0, 20.0 ],
					"text" : "(R)"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-output-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 584.5, 456.0, 151.0, 20.0 ],
					"text" : "Stereo Output to Ableton"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-plugout",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 485.0, 491.0, 65.0, 22.0 ],
					"text" : "plugout~"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-route-status", 0 ],
					"source" : [ "obj-js", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst1", 0 ],
					"source" : [ "obj-js", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst2", 0 ],
					"source" : [ "obj-js", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst3", 0 ],
					"source" : [ "obj-js", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst4", 0 ],
					"source" : [ "obj-js", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst5", 0 ],
					"source" : [ "obj-js", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst6", 0 ],
					"source" : [ "obj-js", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst7", 0 ],
					"source" : [ "obj-js", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst8", 0 ],
					"source" : [ "obj-js", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-midiparse", 0 ],
					"source" : [ "obj-midiin", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst1", 0 ],
					"order" : 7,
					"source" : [ "obj-midiparse", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst2", 0 ],
					"order" : 6,
					"source" : [ "obj-midiparse", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst3", 0 ],
					"order" : 5,
					"source" : [ "obj-midiparse", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst4", 0 ],
					"order" : 4,
					"source" : [ "obj-midiparse", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst5", 0 ],
					"order" : 3,
					"source" : [ "obj-midiparse", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst6", 0 ],
					"order" : 2,
					"source" : [ "obj-midiparse", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst7", 0 ],
					"order" : 1,
					"source" : [ "obj-midiparse", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-vst8", 0 ],
					"order" : 0,
					"source" : [ "obj-midiparse", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-status", 0 ],
					"source" : [ "obj-route-status", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-slot-select", 0 ],
					"source" : [ "obj-route-status", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-plugout", 0 ],
					"source" : [ "obj-selector-L", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-plugout", 1 ],
					"source" : [ "obj-selector-R", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 0 ],
					"order" : 1,
					"source" : [ "obj-slot-select", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 0 ],
					"order" : 0,
					"source" : [ "obj-slot-select", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-js", 0 ],
					"order" : 1,
					"source" : [ "obj-udp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-osc", 0 ],
					"order" : 0,
					"source" : [ "obj-udp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-params1", 0 ],
					"source" : [ "obj-vst1", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 1 ],
					"source" : [ "obj-vst1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 1 ],
					"source" : [ "obj-vst1", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-params2", 0 ],
					"source" : [ "obj-vst2", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 2 ],
					"source" : [ "obj-vst2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 2 ],
					"source" : [ "obj-vst2", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-params3", 0 ],
					"source" : [ "obj-vst3", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 3 ],
					"source" : [ "obj-vst3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 3 ],
					"source" : [ "obj-vst3", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-params4", 0 ],
					"source" : [ "obj-vst4", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 4 ],
					"source" : [ "obj-vst4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 4 ],
					"source" : [ "obj-vst4", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-params5", 0 ],
					"source" : [ "obj-vst5", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 5 ],
					"source" : [ "obj-vst5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 5 ],
					"source" : [ "obj-vst5", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-params6", 0 ],
					"source" : [ "obj-vst6", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 6 ],
					"source" : [ "obj-vst6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 6 ],
					"source" : [ "obj-vst6", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-params7", 0 ],
					"source" : [ "obj-vst7", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 7 ],
					"source" : [ "obj-vst7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 7 ],
					"source" : [ "obj-vst7", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-print-params8", 0 ],
					"source" : [ "obj-vst8", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-L", 8 ],
					"source" : [ "obj-vst8", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-selector-R", 8 ],
					"source" : [ "obj-vst8", 1 ]
				}

			}
 ],
		"dependency_cache" : [ 			{
				"name" : ".maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "_20251211.maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "_20251211_1.maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "_20251211_2.maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "_20251211_3.maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "_20251211_4.maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "_20251211_5.maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "_20251211_6.maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "universal_vst_controller.js",
				"bootpath" : "~/Documents/serum_llm_2",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
