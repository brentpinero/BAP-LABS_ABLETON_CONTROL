{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 9,
			"minor" : 0,
			"revision" : 7,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ -469.0, -1353.0, 2492.0, 1319.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "obj-1",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 15.0, 15.0, 450.0, 25.0 ],
					"text" : "🎛️ Serum 2 Auto-Loading Test - VST3 Format"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 15.0, 40.0, 400.0, 20.0 ],
					"text" : "Auto-loads Serum 2 using official VST~ arguments and preferences"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-4",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 480.0, 156.0, 120.0, 22.0 ],
					"text" : "plug_vst3 Serum2"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 473.0, 126.0, 150.0, 20.0 ],
					"text" : "Auto-load on patch open"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.2, 0.8, 0.2, 1.0 ],
					"id" : "obj-6",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 676.0, 126.0, 35.0, 35.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-7",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 676.0, 171.0, 120.0, 22.0 ],
					"text" : "discover_params"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-8",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 721.0, 131.0, 130.0, 20.0 ],
					"text" : "Discover Parameters"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 1.0, 0.5, 0.0, 1.0 ],
					"id" : "obj-9",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 888.0, 126.0, 35.0, 35.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-10",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 888.0, 171.0, 100.0, 22.0 ],
					"text" : "test_sequence"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-11",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 933.0, 131.0, 132.0, 20.0 ],
					"text" : "Test Parameter Control"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-12",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 731.0, 337.0, 300.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "serum2_autoload_controller.js",
						"parameter_enable" : 0
					}
,
					"text" : "js serum2_autoload_controller.js"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"id" : "obj-13",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 8,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "signal", "signal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 446.0, 584.0, 400.0, 22.0 ],
					"save" : [ "#N", "vst~", "loaduniqueid", 0, 2, 2, "Serum2", ";" ],
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
							"pluginname" : "Serum2.vst3info",
							"plugindisplayname" : "Serum 2",
							"pluginsavedname" : "",
							"pluginsaveduniqueid" : 0,
							"version" : 1,
							"isbank" : 0,
							"isbase64" : 1,
							"blob" : "3031.VMjLg37B...O+fWarAhckI2bo8la8HRLt.iHfTlai8FYo41Y8HRUTYTK3HxO9.BOVMEUy.Ea0cVZtMEcgQWY9vSRC8Vav8lak4Fc9DiLzbiKXkkUYg2a5IVczXjKxHjKt3hKt3hKtXGYnwTLgMWPxDFcUwVX5kDZNglKsIVcMYUV40jLggWRBsDZlYEV4cFaHUCRR4DLTkWSznVZYcVVrwDZMMDS14xTNYGR40zLXECV5I1TLAiXS0TLPkGSyfjPKglKsIVcQY0XoEUaHUCR3Q0ZIc0XykTZHIGRBIFd3XTVvzjQiYUUrIVdqESXzkDZNgFRosjcyfFS1gjPKgFUsIlbIglSnYlQioWPxHVM2f2RyjkUYgWRWkUZ3vlXp0TaKkFNVEVcHIzRng0UYQWTwDFdIglSnY1ZYsVRGgjTUECV0kzQYkWRBsDZXcUV30zUZUGMrgTMhk1R1o2UMkkKt3hPt3hKtXlTyUmdOgELlE0Rl4hYuY2cI8jcyomdAoWcJkyQDAkazYldAwTT2U1XqLzQC8VRg8lZZkkTzIUbqolMio0RusTdTEWRmoFTJcVa2DCaMM2JzEUL1LGUJYyMW0DYmM0SXsjVG8jPPglK2fjKjM0T4EmXJkyPvkzasEGNUgzT2ojPpcDUqrxJpoWdQ8VSgwVQU8zZ1nWYKUEaxY1SBo1QTMkTOc0RjkkV5MTYzrjY4TDZvwTVAUkTVk1Un4xUgITVLEUZOEUXlcyZLwlX3H1bxr1ZqsFLFYESPgjXPAUR1IDT5okSvvTRgo1Ulk2MtTELNIjb5gGaHAEYP0TR3HVTxDFYtQGQVgSRnUiTIomVEcWbLk1b0.2RKYzUYszTssldMYERnYUbtUyTFIUd2UmbxEGUtQDRmM2cyTCQxI2aC4Rbx01TNoTPKEFc2MUaVoUUyEkQLImZhgiPgojQuwlURcGVLkSUrEEMmEiRUYEaMQiRBoVXDU0JKszZNomUYMESFUlSvYTUDUESBo1QTMkT0kjLTElRZojQAg2PvkTRu0lZSAWREkTQo4BMAAidSUCNjQ2U1TDNnEkY2XFdMQiZh8Ta4AiXQQGVDgzStwlZj4jLgIyUn8VMuQTZtPSPvnldKI1Z4nlQ0T2PtwlZjQWLvnWcYsRQYUFMKwlVkMFMvDVYzDWcFwlTxfESCIlaHYFZtnjPtojdRYjV1rDQUEVRyHSRsAiYHcSMVQlayglQYgEc4fDL1gGZSgzaBcjUt8DMwo0ZwQzXt3hZtPkcFomYDMiYyMTQHQDLqHDMIgCS1DSU30DYVsRVlsBMzHlSskGLZMmUwMVPFola0cSQwYjSLQja1ECUNgVVnsjXXE1aFIFaIIFVFAUaLg0MYg1UwHkKPAEY14hYXkSNvrVRvMWUFgWMW0TXNYkS1QFREECb0LjMZM2b0LicAEjb5YSSFYlS3okQLIDdxf2bzXGVyPkcjcmLJ8TcxQCUz7VcqHWMoMGdWEkSJgla1kUSkIiUgcDSigUVvXTZvTDaUgSU0TEUtTSbIU1aZEiU5QkbGcyYvQSPZoDaF41RxnUNRokRr8Td34FMCc0T0EiXvIWP4HkV3LWLFkSUvUVa3byaX8jd1jTXYM0RtflSvEzTGIEQQQTTpolPREURi4hcLIkZYM0TGIkKLgEVy3lcPAkYP4FVHgkQTQEQDQDQPgDVnMzaD4lalAGbUMjYDEDTtHVQUwDbRAmQ5g0TKAiZ4XVLZ8zXykUNxDldwojKU0zbWM0aI0DQEQDbNIWSxQDL2PSdw0lcogmaAYkYTAWTmkTXIACbKM1LEgSTLIVYUoGb0DCb2zTYMMWULUjSFIUa04Tdo4RVScjMQcFUnIjKGgiKyDTYt4RZC0jK2vVQJgkcXgVTmE0aEMkakwDU4YiTDUES3rzJkEDT0A0SXYmbOAUdvbkV2j2XIEjPOImdM8zRvHjP3HVLXYyJt0zTZw1TtrjKJEUbqU2PM8ldX8zTD0VL2zVYGgyMvUkSOYSRlEkM4Pyb4UGcxfVTZk0LzHzLzLWdqPCNHY0JugGMY8jQrMDSsYFSJMjcZYUQuYGVXkFZ3TEbtQ0SNk1PlgkMVUjZqrTdO0jPLUkawL2LoYDcE4TQDEzTkokcLsDMyDGRt4BLTcVaCE0L3IyRAMkMoEFau01TSkyT3TkKj8lK4XlMHMicj81ZHo2L2cyUvbUYsM1XsQCSxXiboE0QHkEUxUyRsomVrQDL0EiUMYiVhgmZzP2XR8jPgElZN4VYxc1TvkmRQMlUO8TbZszZ0M1ax.ib5oUbikUPNsVV2XFQAsVLYo2XtEEMpgVPjE2byYVaBMDLtvyKIMzasA2atUlaz4COIUDYoQ2Pu4Fcx8FarUlb9jSLx3BVYYUV38ldhUGMF4hMC4hKt3hKt3hK1QFZLESXyEjLgQWUrEldIglSnwTLgQWTsIVc2YTXqkTaHIGRBo0YMcjVn4VZHIiZowDZMESSrUTLXk1XCwzZYYUSzn1PMomXS4jLDYUVrEUZLECSCwDMtjFRxgjPhgWUwH1ZQcETvD0QZUWRsgTMHgFRxgjPhgWUwH1ZQcTTq0jLXg2ZFIldqESXzkDZNgFRBsDZtzlXq0zUYoGMTg0bUwFR0fjPHMmKRIEcqYzXlomPHglcngjcIISXpUkLXoWRn4DZLUUV3U0UggGRBsDZtzlX0EkUikVTsU0ZIIiXugCagglaogDdyHDSzgzPLglcngDLIcTXn4VZH4VTGMlcM0lS0ciPjwVUrIFdUECV0kzQYkGM3gUcvDyRnYGZHESUrElZ3vlXn4VZHgUVVkEdAgFUq0TLggWTwHFZ1gFRwTEahk2ZwDFcIglSxLiPLgyY5EjKtXlKt3hKt3FU1rDNCYjTFQEMD4BVy01ayMDUsACMtXlYiwlQ2wTdxkUaIgFQjwTdvkUbjEDLDgFURo0aHc0biIWLrYURx7lXMwlc3DlVtkDVMgFaQkWVvHiL0ckS27VVMUzQtw1a0XibE4RXAYVUtXGVjwDTWMDQskSNJgyRgckUmUiSjkVRVY0bzYjLuoDcHISP5UTTZgSSwfmS1HUTQEUUmsFZvEDQtglTysBLO0VNRICRqomS5kjMhUyLsQiZ2EjSA4hS2ICaXkzQRcFUrgTRBo1QNQmbvcCTwYGbvsTSPgSbLo0YGQjcqYyMYsVczPlUSkTMtI2aGMVVVIlVJkFY3.GUZIzQDMGVQEkbsESMQAyM3HiKtDVVykVd2DmdSkGSpgGQIEkY2X2cqUUQuAUb1ozU4AyLTAUVnoFRPQ1LyfGZnojbKkDT1TSUskEUtfzRk0FZHo0cjYUMMQyQCIidCQVUzM2bq.2Mg8lZ4HSRMIUMNYSRyESToQ2RoY0RhMEamUSdkIDY4nlKyjzSkoUVOkkSio2aOYGN5MWNosBQt.URngjV2o1Mkk1XMk1PSYSVJMDSvfzLJEkQGYmdzfyXwfzbYMjLsUWVT8zXTUiPxMEbG4RQEQjRPUTYnUibyXSSPgWav0jM0MmQioGRCEWLSkFNqfiQXklQKgUbxXCRt3hRkUGVvTTZJYzUgMEbgsRNmQCLwzTMuE0Jv4VQJI2L0jGSKQEVA8FcoICTJIjV3.CLZgULMMjU43RLPU0JoESLBQzYjUiag4RVmokcTUkRRYGU4QDSRYlURI0YNYmRnoDbDgiKR4hYTc1aPAWMQwlKZIDalkDVBMUNqfkVKYjK2kCZ3ozUnYDRoA0PEc2QCIDUXQmZLQjMOojYZgSUpMCZwsBazL1RXQDdRgkZ0YVYnAmLBcCYt8DaqbjTw3xbzD2Q0YyLQUWb4EUVy4BRPglZ4XiMtXFNyMiKuMmaUEVTw8jKrIUbMQFMzMUanMCcyUCVvECcpA2QBgTN0ImZkQWbqE0ZtzTPrcEMTUURhYiTn41Z4MTUokGLFMERrMlcKoELEcjZnQFT4XCNYUSatb2SpkFU04FMQQjcUIldiUzTUIidHEVS1YWVgElXmcFbXg0XwPyP77RREQVZzMzatQmbuwFakImO77hUSQ0LPwVcmklaSQWXzUlO.."
						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "Serum 2",
									"origin" : "Serum2.vst3info",
									"type" : "VST3",
									"subtype" : "Instrument",
									"embed" : 0,
									"snapshot" : 									{
										"pluginname" : "Serum2.vst3info",
										"plugindisplayname" : "Serum 2",
										"pluginsavedname" : "",
										"pluginsaveduniqueid" : 0,
										"version" : 1,
										"isbank" : 0,
										"isbase64" : 1,
										"blob" : "3031.VMjLg37B...O+fWarAhckI2bo8la8HRLt.iHfTlai8FYo41Y8HRUTYTK3HxO9.BOVMEUy.Ea0cVZtMEcgQWY9vSRC8Vav8lak4Fc9DiLzbiKXkkUYg2a5IVczXjKxHjKt3hKt3hKtXGYnwTLgMWPxDFcUwVX5kDZNglKsIVcMYUV40jLggWRBsDZlYEV4cFaHUCRR4DLTkWSznVZYcVVrwDZMMDS14xTNYGR40zLXECV5I1TLAiXS0TLPkGSyfjPKglKsIVcQY0XoEUaHUCR3Q0ZIc0XykTZHIGRBIFd3XTVvzjQiYUUrIVdqESXzkDZNgFRosjcyfFS1gjPKgFUsIlbIglSnYlQioWPxHVM2f2RyjkUYgWRWkUZ3vlXp0TaKkFNVEVcHIzRng0UYQWTwDFdIglSnY1ZYsVRGgjTUECV0kzQYkWRBsDZXcUV30zUZUGMrgTMhk1R1o2UMkkKt3hPt3hKtXlTyUmdOgELlE0Rl4hYuY2cI8jcyomdAoWcJkyQDAkazYldAwTT2U1XqLzQC8VRg8lZZkkTzIUbqolMio0RusTdTEWRmoFTJcVa2DCaMM2JzEUL1LGUJYyMW0DYmM0SXsjVG8jPPglK2fjKjM0T4EmXJkyPvkzasEGNUgzT2ojPpcDUqrxJpoWdQ8VSgwVQU8zZ1nWYKUEaxY1SBo1QTMkTOc0RjkkV5MTYzrjY4TDZvwTVAUkTVk1Un4xUgITVLEUZOEUXlcyZLwlX3H1bxr1ZqsFLFYESPgjXPAUR1IDT5okSvvTRgo1Ulk2MtTELNIjb5gGaHAEYP0TR3HVTxDFYtQGQVgSRnUiTIomVEcWbLk1b0.2RKYzUYszTssldMYERnYUbtUyTFIUd2UmbxEGUtQDRmM2cyTCQxI2aC4Rbx01TNoTPKEFc2MUaVoUUyEkQLImZhgiPgojQuwlURcGVLkSUrEEMmEiRUYEaMQiRBoVXDU0JKszZNomUYMESFUlSvYTUDUESBo1QTMkT0kjLTElRZojQAg2PvkTRu0lZSAWREkTQo4BMAAidSUCNjQ2U1TDNnEkY2XFdMQiZh8Ta4AiXQQGVDgzStwlZj4jLgIyUn8VMuQTZtPSPvnldKI1Z4nlQ0T2PtwlZjQWLvnWcYsRQYUFMKwlVkMFMvDVYzDWcFwlTxfESCIlaHYFZtnjPtojdRYjV1rDQUEVRyHSRsAiYHcSMVQlayglQYgEc4fDL1gGZSgzaBcjUt8DMwo0ZwQzXt3hZtPkcFomYDMiYyMTQHQDLqHDMIgCS1DSU30DYVsRVlsBMzHlSskGLZMmUwMVPFola0cSQwYjSLQja1ECUNgVVnsjXXE1aFIFaIIFVFAUaLg0MYg1UwHkKPAEY14hYXkSNvrVRvMWUFgWMW0TXNYkS1QFREECb0LjMZM2b0LicAEjb5YSSFYlS3okQLIDdxf2bzXGVyPkcjcmLJ8TcxQCUz7VcqHWMoMGdWEkSJgla1kUSkIiUgcDSigUVvXTZvTDaUgSU0TEUtTSbIU1aZEiU5QkbGcyYvQSPZoDaF41RxnUNRokRr8Td34FMCc0T0EiXvIWP4HkV3LWLFkSUvUVa3byaX8jd1jTXYM0RtflSvEzTGIEQQQTTpolPREURi4hcLIkZYM0TGIkKLgEVy3lcPAkYP4FVHgkQTQEQDQDQPgDVnMzaD4lalAGbUMjYDEDTtHVQUwDbRAmQ5g0TKAiZ4XVLZ8zXykUNxDldwojKU0zbWM0aI0DQEQDbNIWSxQDL2PSdw0lcogmaAYkYTAWTmkTXIACbKM1LEgSTLIVYUoGb0DCb2zTYMMWULUjSFIUa04Tdo4RVScjMQcFUnIjKGgiKyDTYt4RZC0jK2vVQJgkcXgVTmE0aEMkakwDU4YiTDUES3rzJkEDT0A0SXYmbOAUdvbkV2j2XIEjPOImdM8zRvHjP3HVLXYyJt0zTZw1TtrjKJEUbqU2PM8ldX8zTD0VL2zVYGgyMvUkSOYSRlEkM4Pyb4UGcxfVTZk0LzHzLzLWdqPCNHY0JugGMY8jQrMDSsYFSJMjcZYUQuYGVXkFZ3TEbtQ0SNk1PlgkMVUjZqrTdO0jPLUkawL2LoYDcE4TQDEzTkokcLsDMyDGRt4BLTcVaCE0L3IyRAMkMoEFau01TSkyT3TkKj8lK4XlMHMicj81ZHo2L2cyUvbUYsM1XsQCSxXiboE0QHkEUxUyRsomVrQDL0EiUMYiVhgmZzP2XR8jPgElZN4VYxc1TvkmRQMlUO8TbZszZ0M1ax.ib5oUbikUPNsVV2XFQAsVLYo2XtEEMpgVPjE2byYVaBMDLtvyKIMzasA2atUlaz4COIUDYoQ2Pu4Fcx8FarUlb9jSLx3BVYYUV38ldhUGMF4hMC4hKt3hKt3hK1QFZLESXyEjLgQWUrEldIglSnwTLgQWTsIVc2YTXqkTaHIGRBo0YMcjVn4VZHIiZowDZMESSrUTLXk1XCwzZYYUSzn1PMomXS4jLDYUVrEUZLECSCwDMtjFRxgjPhgWUwH1ZQcETvD0QZUWRsgTMHgFRxgjPhgWUwH1ZQcTTq0jLXg2ZFIldqESXzkDZNgFRBsDZtzlXq0zUYoGMTg0bUwFR0fjPHMmKRIEcqYzXlomPHglcngjcIISXpUkLXoWRn4DZLUUV3U0UggGRBsDZtzlX0EkUikVTsU0ZIIiXugCagglaogDdyHDSzgzPLglcngDLIcTXn4VZH4VTGMlcM0lS0ciPjwVUrIFdUECV0kzQYkGM3gUcvDyRnYGZHESUrElZ3vlXn4VZHgUVVkEdAgFUq0TLggWTwHFZ1gFRwTEahk2ZwDFcIglSxLiPLgyY5EjKtXlKt3hKt3FU1rDNCYjTFQEMD4BVy01ayMDUsACMtXlYiwlQ2wTdxkUaIgFQjwTdvkUbjEDLDgFURo0aHc0biIWLrYURx7lXMwlc3DlVtkDVMgFaQkWVvHiL0ckS27VVMUzQtw1a0XibE4RXAYVUtXGVjwDTWMDQskSNJgyRgckUmUiSjkVRVY0bzYjLuoDcHISP5UTTZgSSwfmS1HUTQEUUmsFZvEDQtglTysBLO0VNRICRqomS5kjMhUyLsQiZ2EjSA4hS2ICaXkzQRcFUrgTRBo1QNQmbvcCTwYGbvsTSPgSbLo0YGQjcqYyMYsVczPlUSkTMtI2aGMVVVIlVJkFY3.GUZIzQDMGVQEkbsESMQAyM3HiKtDVVykVd2DmdSkGSpgGQIEkY2X2cqUUQuAUb1ozU4AyLTAUVnoFRPQ1LyfGZnojbKkDT1TSUskEUtfzRk0FZHo0cjYUMMQyQCIidCQVUzM2bq.2Mg8lZ4HSRMIUMNYSRyESToQ2RoY0RhMEamUSdkIDY4nlKyjzSkoUVOkkSio2aOYGN5MWNosBQt.URngjV2o1Mkk1XMk1PSYSVJMDSvfzLJEkQGYmdzfyXwfzbYMjLsUWVT8zXTUiPxMEbG4RQEQjRPUTYnUibyXSSPgWav0jM0MmQioGRCEWLSkFNqfiQXklQKgUbxXCRt3hRkUGVvTTZJYzUgMEbgsRNmQCLwzTMuE0Jv4VQJI2L0jGSKQEVA8FcoICTJIjV3.CLZgULMMjU43RLPU0JoESLBQzYjUiag4RVmokcTUkRRYGU4QDSRYlURI0YNYmRnoDbDgiKR4hYTc1aPAWMQwlKZIDalkDVBMUNqfkVKYjK2kCZ3ozUnYDRoA0PEc2QCIDUXQmZLQjMOojYZgSUpMCZwsBazL1RXQDdRgkZ0YVYnAmLBcCYt8DaqbjTw3xbzD2Q0YyLQUWb4EUVy4BRPglZ4XiMtXFNyMiKuMmaUEVTw8jKrIUbMQFMzMUanMCcyUCVvECcpA2QBgTN0ImZkQWbqE0ZtzTPrcEMTUURhYiTn41Z4MTUokGLFMERrMlcKoELEcjZnQFT4XCNYUSatb2SpkFU04FMQQjcUIldiUzTUIidHEVS1YWVgElXmcFbXg0XwPyP77RREQVZzMzatQmbuwFakImO77hUSQ0LPwVcmklaSQWXzUlO.."
									}
,
									"fileref" : 									{
										"name" : "Serum 2",
										"filename" : "Serum 2_20250922.maxsnap",
										"filepath" : "~/Documents/Max 9/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "51924c0a70e98d33c00c720a09aa0bd4"
									}

								}
 ]
						}

					}
,
					"text" : "vst~ 2 2 Serum2",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-14",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 581.0, 629.0, 130.0, 22.0 ],
					"text" : "print serum2_params"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-15",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 731.0, 629.0, 130.0, 22.0 ],
					"text" : "print serum2_values"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-16",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 881.0, 629.0, 120.0, 22.0 ],
					"text" : "print serum2_info"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-17",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 71.0, 126.0, 311.0, 20.0 ],
					"text" : "Manual Parameter Control (Serum 2 - 1-based indexing):"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-18",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 71.0, 151.0, 50.0, 22.0 ],
					"text" : "1 0.5"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-19",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 131.0, 151.0, 50.0, 22.0 ],
					"text" : "2 0.3"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-20",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 191.0, 151.0, 60.0, 22.0 ],
					"text" : "10 0.8"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-21",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 261.0, 151.0, 60.0, 22.0 ],
					"text" : "20 0.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-22",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1159.0, 483.0, 200.0, 20.0 ],
					"text" : "MIDI Test for Serum 2:"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-23",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1159.0, 508.0, 150.0, 22.0 ],
					"text" : "midievent 144 60 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-24",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1319.0, 508.0, 140.0, 22.0 ],
					"text" : "midievent 128 60 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-25",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1488.0, 483.0, 300.0, 20.0 ],
					"text" : "Alternative Loading Methods:"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-26",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1488.0, 508.0, 90.0, 22.0 ],
					"text" : "plug Serum2"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-27",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1588.0, 508.0, 120.0, 22.0 ],
					"text" : "plug_au Serum2"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-28",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1723.0, 513.0, 200.0, 20.0 ],
					"text" : "Generic / Audio Unit versions"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-29",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 463.0, 680.0, 45.0, 45.0 ]
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-12", 0 ],
					"source" : [ "obj-10", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-12", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-12", 0 ],
					"order" : 0,
					"source" : [ "obj-13", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-14", 0 ],
					"order" : 1,
					"source" : [ "obj-13", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-15", 0 ],
					"source" : [ "obj-13", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-16", 0 ],
					"source" : [ "obj-13", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-29", 1 ],
					"source" : [ "obj-13", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-29", 0 ],
					"source" : [ "obj-13", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-18", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-19", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-20", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-21", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-23", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-24", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-26", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-27", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 0 ],
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-12", 0 ],
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-10", 0 ],
					"source" : [ "obj-9", 0 ]
				}

			}
 ],
		"dependency_cache" : [ 			{
				"name" : "Serum 2_20250922.maxsnap",
				"bootpath" : "~/Documents/Max 9/Snapshots",
				"patcherrelativepath" : "../Max 9/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "serum2_autoload_controller.js",
				"bootpath" : "~/Documents/serum_llm_2",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
