# AbletonMCP_Extended/__init__.py
# Extended version of AbletonMCP with Arrangement View support
# Based on ahujasid/ableton-mcp with additions for:
# - duplicate_clip_to_arrangement
# - create_arrangement_clip
# - get_arrangement_clips

from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
import socket
import json
import threading
import time
import traceback

# Change queue import for Python 2/3 compatibility
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3

# Constants for socket communication
DEFAULT_PORT = 9877
HOST = "localhost"

def create_instance(c_instance):
    """Create and return the AbletonMCP script instance"""
    return AbletonMCPExtended(c_instance)

class AbletonMCPExtended(ControlSurface):
    """Extended AbletonMCP Remote Script with Arrangement View support"""

    def __init__(self, c_instance):
        """Initialize the control surface"""
        ControlSurface.__init__(self, c_instance)
        self.log_message("AbletonMCP Extended initializing...")

        # Socket server for communication
        self.server = None
        self.client_threads = []
        self.server_thread = None
        self.running = False

        # Cache the song reference for easier access
        self._song = self.song()

        # Start the socket server
        self.start_server()

        self.log_message("AbletonMCP Extended initialized")
        self.show_message("AbletonMCP Extended: Listening on port " + str(DEFAULT_PORT))

    def disconnect(self):
        """Called when Ableton closes or the control surface is removed"""
        self.log_message("AbletonMCP Extended disconnecting...")
        self.running = False

        if self.server:
            try:
                self.server.close()
            except:
                pass

        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(1.0)

        for client_thread in self.client_threads[:]:
            if client_thread.is_alive():
                self.log_message("Client thread still alive during disconnect")

        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP Extended disconnected")

    def start_server(self):
        """Start the socket server in a separate thread"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((HOST, DEFAULT_PORT))
            self.server.listen(5)

            self.running = True
            self.server_thread = threading.Thread(target=self._server_thread)
            self.server_thread.daemon = True
            self.server_thread.start()

            self.log_message("Server started on port " + str(DEFAULT_PORT))
        except Exception as e:
            self.log_message("Error starting server: " + str(e))
            self.show_message("AbletonMCP Extended: Error - " + str(e))

    def _server_thread(self):
        """Server thread implementation"""
        try:
            self.log_message("Server thread started")
            self.server.settimeout(1.0)

            while self.running:
                try:
                    client, address = self.server.accept()
                    self.log_message("Connection accepted from " + str(address))

                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    self.client_threads.append(client_thread)
                    self.client_threads = [t for t in self.client_threads if t.is_alive()]

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log_message("Server accept error: " + str(e))
                    time.sleep(0.5)

            self.log_message("Server thread stopped")
        except Exception as e:
            self.log_message("Server thread error: " + str(e))

    def _handle_client(self, client):
        """Handle communication with a connected client"""
        self.log_message("Client handler started")
        client.settimeout(None)
        buffer = ''

        try:
            while self.running:
                try:
                    data = client.recv(8192)

                    if not data:
                        self.log_message("Client disconnected")
                        break

                    try:
                        buffer += data.decode('utf-8')
                    except AttributeError:
                        buffer += data

                    try:
                        command = json.loads(buffer)
                        buffer = ''

                        self.log_message("Received command: " + str(command.get("type", "unknown")))
                        response = self._process_command(command)

                        try:
                            client.sendall(json.dumps(response).encode('utf-8'))
                        except AttributeError:
                            client.sendall(json.dumps(response))
                    except ValueError:
                        continue

                except Exception as e:
                    self.log_message("Error handling client data: " + str(e))
                    self.log_message(traceback.format_exc())

                    error_response = {"status": "error", "message": str(e)}
                    try:
                        client.sendall(json.dumps(error_response).encode('utf-8'))
                    except:
                        break

                    if not isinstance(e, ValueError):
                        break
        except Exception as e:
            self.log_message("Error in client handler: " + str(e))
        finally:
            try:
                client.close()
            except:
                pass
            self.log_message("Client handler stopped")

    def _process_command(self, command):
        """Process a command from the client and return a response"""
        command_type = command.get("type", "")
        params = command.get("params", {})

        response = {
            "status": "success",
            "result": {}
        }

        try:
            # Read-only commands (can run on any thread)
            if command_type == "get_session_info":
                response["result"] = self._get_session_info()
            elif command_type == "get_track_info":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_info(track_index)
            elif command_type == "get_arrangement_clips":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_arrangement_clips(track_index)
            elif command_type == "get_arrangement_clip_notes":
                track_index = params.get("track_index", 0)
                clip_index = params.get("clip_index", 0)
                response["result"] = self._get_arrangement_clip_notes(track_index, clip_index)

            # Browser commands (read-only, don't need main thread)
            elif command_type == "get_browser_tree":
                category_type = params.get("category_type", "all")
                response["result"] = self._get_browser_tree(category_type)
            elif command_type == "get_browser_items_at_path":
                path = params.get("path", "")
                response["result"] = self._get_browser_items_at_path(path)
            elif command_type == "get_all_presets":
                category_type = params.get("category_type", "audio_effects")
                max_depth = params.get("max_depth", 5)
                response["result"] = self._get_all_presets(category_type, max_depth)

            # Device parameter commands (read-only)
            elif command_type == "get_device_parameters":
                track_index = params.get("track_index", 0)
                device_index = params.get("device_index", 0)
                response["result"] = self._get_device_parameters(track_index, device_index)

            # Single-call session summary for LLM context
            elif command_type == "get_session_summary":
                response["result"] = self._get_session_summary()

            # Mixer controls (read-only)
            elif command_type == "get_return_tracks":
                response["result"] = self._get_return_tracks()

            # Audio clip properties (read-only)
            elif command_type == "get_audio_clip_properties":
                track_index = params.get("track_index", 0)
                clip_index = params.get("clip_index", 0)
                response["result"] = self._get_audio_clip_properties(track_index, clip_index)
            elif command_type == "get_clip_warp_markers":
                track_index = params.get("track_index", 0)
                clip_index = params.get("clip_index", 0)
                response["result"] = self._get_clip_warp_markers(track_index, clip_index)

            # Track organization (read-only)
            elif command_type == "get_track_routing":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_routing(track_index)

            # Master track (read-only)
            elif command_type == "get_master_track":
                response["result"] = self._get_master_track()
            elif command_type == "get_master_device_parameters":
                device_index = params.get("device_index", 0)
                response["result"] = self._get_master_device_parameters(device_index)

            # Transport (read-only)
            elif command_type == "get_current_position":
                response["result"] = self._get_current_position()

            # Commands that modify Live's state (scheduled on main thread)
            elif command_type in [
                "create_midi_track", "set_track_name",
                "create_clip", "add_notes_to_clip", "set_clip_name",
                "set_tempo", "fire_clip", "stop_clip",
                "start_playback", "stop_playback",
                # Browser loading
                "load_browser_item",
                # Arrangement view commands
                "duplicate_clip_to_arrangement",
                "create_arrangement_clip",
                "add_notes_to_arrangement_clip",
                # Device parameter control
                "set_device_parameter",
                # Mixer controls (Priority 1)
                "set_track_volume", "set_track_pan", "set_send_level",
                "set_track_mute", "set_track_solo", "set_return_track_volume",
                # Audio clip properties (Priority 2)
                "set_clip_gain", "set_clip_pitch", "set_clip_loop", "set_clip_warp_mode",
                # Track organization (Priority 3)
                "create_audio_track", "delete_track", "create_return_track",
                "set_track_color", "fold_track",
                # Device chain (Priority 4)
                "delete_device", "set_device_enabled", "set_device_parameter_by_name",
                # Arrangement editing (Priority 5)
                "set_clip_mute", "set_clip_start_end", "set_clip_color",
                # Master track (Priority 6)
                "set_master_volume", "set_master_device_parameter",
                # Transport and selection (Priority 7)
                "set_current_position", "select_track", "select_clip"
            ]:
                response_queue = queue.Queue()

                def main_thread_task():
                    try:
                        result = None

                        # Original commands
                        if command_type == "create_midi_track":
                            index = params.get("index", -1)
                            result = self._create_midi_track(index)
                        elif command_type == "set_track_name":
                            track_index = params.get("track_index", 0)
                            name = params.get("name", "")
                            result = self._set_track_name(track_index, name)
                        elif command_type == "create_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            length = params.get("length", 4.0)
                            result = self._create_clip(track_index, clip_index, length)
                        elif command_type == "add_notes_to_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            notes = params.get("notes", [])
                            result = self._add_notes_to_clip(track_index, clip_index, notes)
                        elif command_type == "set_clip_name":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            name = params.get("name", "")
                            result = self._set_clip_name(track_index, clip_index, name)
                        elif command_type == "set_tempo":
                            tempo = params.get("tempo", 120.0)
                            result = self._set_tempo(tempo)
                        elif command_type == "fire_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._fire_clip(track_index, clip_index)
                        elif command_type == "stop_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._stop_clip(track_index, clip_index)
                        elif command_type == "start_playback":
                            result = self._start_playback()
                        elif command_type == "stop_playback":
                            result = self._stop_playback()

                        # Browser loading
                        elif command_type == "load_browser_item":
                            track_index = params.get("track_index", 0)
                            item_uri = params.get("item_uri", "")
                            result = self._load_browser_item(track_index, item_uri)

                        # Arrangement view commands
                        elif command_type == "duplicate_clip_to_arrangement":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            position = params.get("position", 0.0)
                            result = self._duplicate_clip_to_arrangement(track_index, clip_index, position)
                        elif command_type == "create_arrangement_clip":
                            track_index = params.get("track_index", 0)
                            start_time = params.get("start_time", 0.0)
                            length = params.get("length", 4.0)
                            result = self._create_arrangement_clip(track_index, start_time, length)
                        elif command_type == "add_notes_to_arrangement_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            notes = params.get("notes", [])
                            result = self._add_notes_to_arrangement_clip(track_index, clip_index, notes)

                        # Device parameter control
                        elif command_type == "set_device_parameter":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            parameter_index = params.get("parameter_index", 0)
                            value = params.get("value", 0.0)
                            result = self._set_device_parameter(track_index, device_index, parameter_index, value)

                        # Mixer controls (Priority 1)
                        elif command_type == "set_track_volume":
                            track_index = params.get("track_index", 0)
                            volume = params.get("volume", 0.85)
                            result = self._set_track_volume(track_index, volume)
                        elif command_type == "set_track_pan":
                            track_index = params.get("track_index", 0)
                            pan = params.get("pan", 0.0)
                            result = self._set_track_pan(track_index, pan)
                        elif command_type == "set_send_level":
                            track_index = params.get("track_index", 0)
                            send_index = params.get("send_index", 0)
                            level = params.get("level", 0.0)
                            result = self._set_send_level(track_index, send_index, level)
                        elif command_type == "set_track_mute":
                            track_index = params.get("track_index", 0)
                            mute = params.get("mute", False)
                            result = self._set_track_mute(track_index, mute)
                        elif command_type == "set_track_solo":
                            track_index = params.get("track_index", 0)
                            solo = params.get("solo", False)
                            result = self._set_track_solo(track_index, solo)
                        elif command_type == "set_return_track_volume":
                            return_index = params.get("return_index", 0)
                            volume = params.get("volume", 0.85)
                            result = self._set_return_track_volume(return_index, volume)

                        # Audio clip properties (Priority 2)
                        elif command_type == "set_clip_gain":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            gain = params.get("gain", 1.0)
                            result = self._set_clip_gain(track_index, clip_index, gain)
                        elif command_type == "set_clip_pitch":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            semitones = params.get("semitones", 0)
                            cents = params.get("cents", 0)
                            result = self._set_clip_pitch(track_index, clip_index, semitones, cents)
                        elif command_type == "set_clip_loop":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            loop_start = params.get("loop_start", None)
                            loop_end = params.get("loop_end", None)
                            looping = params.get("looping", None)
                            result = self._set_clip_loop(track_index, clip_index, loop_start, loop_end, looping)
                        elif command_type == "set_clip_warp_mode":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            warp_mode = params.get("warp_mode", 0)
                            result = self._set_clip_warp_mode(track_index, clip_index, warp_mode)

                        # Track organization (Priority 3)
                        elif command_type == "create_audio_track":
                            index = params.get("index", -1)
                            result = self._create_audio_track(index)
                        elif command_type == "delete_track":
                            track_index = params.get("track_index", 0)
                            result = self._delete_track(track_index)
                        elif command_type == "create_return_track":
                            result = self._create_return_track()
                        elif command_type == "set_track_color":
                            track_index = params.get("track_index", 0)
                            color_index = params.get("color_index", 0)
                            result = self._set_track_color(track_index, color_index)
                        elif command_type == "fold_track":
                            track_index = params.get("track_index", 0)
                            fold = params.get("fold", True)
                            result = self._fold_track(track_index, fold)

                        # Device chain (Priority 4)
                        elif command_type == "delete_device":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            result = self._delete_device(track_index, device_index)
                        elif command_type == "set_device_enabled":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            enabled = params.get("enabled", True)
                            result = self._set_device_enabled(track_index, device_index, enabled)
                        elif command_type == "set_device_parameter_by_name":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            param_name = params.get("param_name", "")
                            value = params.get("value", 0.0)
                            result = self._set_device_parameter_by_name(track_index, device_index, param_name, value)

                        # Arrangement editing (Priority 5)
                        elif command_type == "set_clip_mute":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            muted = params.get("muted", True)
                            result = self._set_clip_mute(track_index, clip_index, muted)
                        elif command_type == "set_clip_start_end":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            start_marker = params.get("start_marker", None)
                            end_marker = params.get("end_marker", None)
                            result = self._set_clip_start_end(track_index, clip_index, start_marker, end_marker)
                        elif command_type == "set_clip_color":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            color_index = params.get("color_index", 0)
                            result = self._set_clip_color(track_index, clip_index, color_index)

                        # Master track (Priority 6)
                        elif command_type == "set_master_volume":
                            volume = params.get("volume", 0.85)
                            result = self._set_master_volume(volume)
                        elif command_type == "set_master_device_parameter":
                            device_index = params.get("device_index", 0)
                            parameter_index = params.get("parameter_index", 0)
                            value = params.get("value", 0.0)
                            result = self._set_master_device_parameter(device_index, parameter_index, value)

                        # Transport and selection (Priority 7)
                        elif command_type == "set_current_position":
                            position = params.get("position", 0.0)
                            result = self._set_current_position(position)
                        elif command_type == "select_track":
                            track_index = params.get("track_index", 0)
                            result = self._select_track(track_index)
                        elif command_type == "select_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._select_clip(track_index, clip_index)

                        response_queue.put({"status": "success", "result": result})
                    except Exception as e:
                        self.log_message("Error in main thread task: " + str(e))
                        self.log_message(traceback.format_exc())
                        response_queue.put({"status": "error", "message": str(e)})

                try:
                    self.schedule_message(0, main_thread_task)
                except AssertionError:
                    main_thread_task()

                try:
                    task_response = response_queue.get(timeout=10.0)
                    if task_response.get("status") == "error":
                        response["status"] = "error"
                        response["message"] = task_response.get("message", "Unknown error")
                    else:
                        response["result"] = task_response.get("result", {})
                except queue.Empty:
                    response["status"] = "error"
                    response["message"] = "Timeout waiting for operation"
            else:
                response["status"] = "error"
                response["message"] = "Unknown command: " + command_type
        except Exception as e:
            self.log_message("Error processing command: " + str(e))
            self.log_message(traceback.format_exc())
            response["status"] = "error"
            response["message"] = str(e)

        return response

    # =========================================================================
    # Original command implementations
    # =========================================================================

    def _get_session_info(self):
        """Get information about the current session"""
        try:
            result = {
                "tempo": self._song.tempo,
                "signature_numerator": self._song.signature_numerator,
                "signature_denominator": self._song.signature_denominator,
                "track_count": len(self._song.tracks),
                "return_track_count": len(self._song.return_tracks),
                "current_song_time": self._song.current_song_time,
                "is_playing": self._song.is_playing,
                "master_track": {
                    "name": "Master",
                    "volume": self._song.master_track.mixer_device.volume.value,
                    "panning": self._song.master_track.mixer_device.panning.value
                }
            }
            return result
        except Exception as e:
            self.log_message("Error getting session info: " + str(e))
            raise

    def _get_session_summary(self):
        """Get compact session summary in one call for LLM context.
        Returns tracks with device type classification (drums/synth/bass/empty).
        """
        try:
            tracks = []
            for i, track in enumerate(self._song.tracks):
                if not track.devices:
                    continue  # Skip empty tracks

                device = track.devices[0]
                class_name = device.class_name if hasattr(device, 'class_name') else ""
                device_name = device.name

                # Categorize device
                cat = "inst"
                name_lower = device_name.lower()
                class_lower = class_name.lower()

                if "instrumentgroupdevice" in class_lower or "impulse" in class_lower:
                    cat = "drums"
                elif "bass" in name_lower:
                    cat = "bass"
                elif any(k in name_lower for k in ["pad", "lead", "synth", "keys"]):
                    cat = "synth"
                elif any(k in class_lower for k in ["analog", "drift", "wavetable", "operator"]):
                    cat = "synth"

                # Check if track has arrangement clips
                has_clips = len(track.arrangement_clips) > 0 if hasattr(track, 'arrangement_clips') else False

                tracks.append({
                    "i": i,
                    "cat": cat,
                    "dev": device_name,
                    "clips": has_clips
                })

            return {"tempo": int(self._song.tempo), "tracks": tracks}
        except Exception as e:
            self.log_message("Error getting session summary: " + str(e))
            raise

    def _get_track_info(self, track_index):
        """Get information about a track including arrangement clips"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            # Get session clip slots
            clip_slots = []
            for slot_index, slot in enumerate(track.clip_slots[:8]):  # Limit to first 8
                clip_info = None
                if slot.has_clip:
                    clip = slot.clip
                    clip_info = {
                        "name": clip.name,
                        "length": clip.length,
                        "is_playing": clip.is_playing,
                        "is_recording": clip.is_recording
                    }

                clip_slots.append({
                    "index": slot_index,
                    "has_clip": slot.has_clip,
                    "clip": clip_info
                })

            # Get arrangement clips (Live 11+)
            arrangement_clips = []
            if hasattr(track, 'arrangement_clips'):
                for i, clip in enumerate(track.arrangement_clips[:20]):  # Limit to 20
                    arrangement_clips.append({
                        "index": i,
                        "name": clip.name,
                        "start_time": clip.start_time,
                        "end_time": clip.end_time,
                        "length": clip.length,
                        "is_playing": clip.is_playing
                    })

            # Get devices on the track
            devices = []
            for device_index, device in enumerate(track.devices):
                devices.append({
                    "index": device_index,
                    "name": device.name,
                    "class_name": device.class_name
                })

            result = {
                "index": track_index,
                "name": track.name,
                "is_audio_track": track.has_audio_input,
                "is_midi_track": track.has_midi_input,
                "mute": track.mute,
                "solo": track.solo,
                "arm": track.arm,
                "volume": track.mixer_device.volume.value,
                "panning": track.mixer_device.panning.value,
                "clip_slots": clip_slots,
                "arrangement_clips": arrangement_clips,
                "arrangement_clip_count": len(arrangement_clips),
                "devices": devices,
                "device_count": len(devices)
            }
            return result
        except Exception as e:
            self.log_message("Error getting track info: " + str(e))
            raise

    def _create_midi_track(self, index):
        """Create a new MIDI track"""
        try:
            self._song.create_midi_track(index)
            new_track_index = len(self._song.tracks) - 1 if index == -1 else index
            new_track = self._song.tracks[new_track_index]

            result = {
                "index": new_track_index,
                "name": new_track.name
            }
            return result
        except Exception as e:
            self.log_message("Error creating MIDI track: " + str(e))
            raise

    def _set_track_name(self, track_index, name):
        """Set the name of a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.name = name

            result = {"name": track.name}
            return result
        except Exception as e:
            self.log_message("Error setting track name: " + str(e))
            raise

    def _create_clip(self, track_index, clip_index, length):
        """Create a new MIDI clip in session view"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")

            clip_slot.create_clip(length)

            result = {
                "name": clip_slot.clip.name,
                "length": clip_slot.clip.length
            }
            return result
        except Exception as e:
            self.log_message("Error creating clip: " + str(e))
            raise

    def _add_notes_to_clip(self, track_index, clip_index, notes):
        """Add MIDI notes to a session view clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip

            # Convert note data to Live 11+ MidiNoteSpecification format
            from Live import Clip as LiveClip

            live_notes = []
            for note in notes:
                # Support multiple field name formats from LLM
                pitch = note.get("pitch") or note.get("note") or 60
                start_time = note.get("start_time") or note.get("time") or 0.0
                duration = note.get("duration") or note.get("length") or 0.25
                velocity = note.get("velocity") or note.get("vel") or 100
                mute = note.get("mute", False)

                # Create MidiNoteSpecification for Live 11+
                note_spec = LiveClip.MidiNoteSpecification(
                    pitch=pitch,
                    start_time=start_time,
                    duration=duration,
                    velocity=velocity,
                    mute=mute
                )
                live_notes.append(note_spec)

            # Use add_new_notes for Live 11+
            clip.add_new_notes(tuple(live_notes))

            result = {"note_count": len(notes)}
            return result
        except Exception as e:
            self.log_message("Error adding notes to clip: " + str(e))
            raise

    def _set_clip_name(self, track_index, clip_index, name):
        """Set the name of a session view clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip
            clip.name = name

            result = {"name": clip.name}
            return result
        except Exception as e:
            self.log_message("Error setting clip name: " + str(e))
            raise

    def _set_tempo(self, tempo):
        """Set the tempo of the session"""
        try:
            self._song.tempo = tempo
            result = {"tempo": self._song.tempo}
            return result
        except Exception as e:
            self.log_message("Error setting tempo: " + str(e))
            raise

    def _fire_clip(self, track_index, clip_index):
        """Fire a session view clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip_slot.fire()

            result = {"fired": True}
            return result
        except Exception as e:
            self.log_message("Error firing clip: " + str(e))
            raise

    def _stop_clip(self, track_index, clip_index):
        """Stop a session view clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]
            clip_slot.stop()

            result = {"stopped": True}
            return result
        except Exception as e:
            self.log_message("Error stopping clip: " + str(e))
            raise

    def _start_playback(self):
        """Start playing the session"""
        try:
            self._song.start_playing()
            result = {"playing": self._song.is_playing}
            return result
        except Exception as e:
            self.log_message("Error starting playback: " + str(e))
            raise

    def _stop_playback(self):
        """Stop playing the session"""
        try:
            self._song.stop_playing()
            result = {"playing": self._song.is_playing}
            return result
        except Exception as e:
            self.log_message("Error stopping playback: " + str(e))
            raise

    # =========================================================================
    # NEW: Arrangement View commands
    # =========================================================================

    def _get_arrangement_clips(self, track_index):
        """Get all arrangement clips for a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            arrangement_clips = []
            if hasattr(track, 'arrangement_clips'):
                for i, clip in enumerate(track.arrangement_clips):
                    arrangement_clips.append({
                        "index": i,
                        "name": clip.name,
                        "start_time": clip.start_time,
                        "end_time": clip.end_time,
                        "length": clip.length,
                        "is_playing": clip.is_playing,
                        "is_midi_clip": clip.is_midi_clip if hasattr(clip, 'is_midi_clip') else False
                    })

            result = {
                "track_index": track_index,
                "track_name": track.name,
                "clip_count": len(arrangement_clips),
                "clips": arrangement_clips
            }
            return result
        except Exception as e:
            self.log_message("Error getting arrangement clips: " + str(e))
            raise

    def _get_arrangement_clip_notes(self, track_index, clip_index):
        """
        Get all MIDI notes from an arrangement view clip.

        Args:
            track_index: Index of the track
            clip_index: Index of the arrangement clip

        Returns:
            Dictionary with clip info and list of notes
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if not hasattr(track, 'arrangement_clips'):
                raise ValueError("Track has no arrangement clips")

            arrangement_clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(arrangement_clips):
                raise IndexError("Clip index out of range")

            clip = arrangement_clips[clip_index]

            if not clip.is_midi_clip:
                raise ValueError("Clip is not a MIDI clip")

            # Get notes using get_notes_extended (Live 11+)
            # Returns tuple of tuples: ((pitch, start, duration, velocity, mute), ...)
            notes_data = clip.get_notes_extended(
                from_time=0,
                from_pitch=0,
                time_span=clip.length,
                pitch_span=128
            )

            notes = []
            for note in notes_data:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity,
                    "mute": note.mute if hasattr(note, 'mute') else False
                })

            result = {
                "track_index": track_index,
                "track_name": track.name,
                "clip_index": clip_index,
                "clip_name": clip.name,
                "clip_length": clip.length,
                "note_count": len(notes),
                "notes": notes
            }
            return result
        except Exception as e:
            self.log_message("Error getting arrangement clip notes: " + str(e))
            raise

    def _duplicate_clip_to_arrangement(self, track_index, clip_index, position):
        """
        Duplicate a session view clip to arrangement view at specified position.

        Args:
            track_index: Index of the track
            clip_index: Index of the clip slot in session view
            position: Position in beats where to place the clip in arrangement

        Returns:
            Dictionary with info about the duplicated clip
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            source_clip = clip_slot.clip
            source_length = source_clip.length

            # Use duplicate_clip_to_arrangement (available in Live 10+)
            if hasattr(track, 'duplicate_clip_to_arrangement'):
                track.duplicate_clip_to_arrangement(source_clip, position)

                result = {
                    "success": True,
                    "source_clip": source_clip.name,
                    "source_length": source_length,
                    "position": position,
                    "track_index": track_index,
                    "message": "Clip duplicated to arrangement at position {} beats".format(position)
                }
                return result
            else:
                raise Exception("duplicate_clip_to_arrangement not available (requires Live 10+)")

        except Exception as e:
            self.log_message("Error duplicating clip to arrangement: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _create_arrangement_clip(self, track_index, start_time, length):
        """
        Create a new MIDI clip directly in arrangement view.

        Args:
            track_index: Index of the track
            start_time: Start time in beats
            length: Length of the clip in beats

        Returns:
            Dictionary with info about the created clip

        Note: This uses Track.create_midi_clip which is available in Live 12+
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            # Check if track is a MIDI track
            if not track.has_midi_input:
                raise Exception("Track is not a MIDI track")

            # Use create_midi_clip (Live 12+)
            if hasattr(track, 'create_midi_clip'):
                track.create_midi_clip(start_time, length)

                # Find the newly created clip
                new_clip = None
                if hasattr(track, 'arrangement_clips'):
                    for clip in track.arrangement_clips:
                        if abs(clip.start_time - start_time) < 0.01:
                            new_clip = clip
                            break

                result = {
                    "success": True,
                    "start_time": start_time,
                    "length": length,
                    "track_index": track_index,
                    "clip_name": new_clip.name if new_clip else "New Clip",
                    "message": "Created arrangement clip at {} beats with length {} beats".format(start_time, length)
                }
                return result
            else:
                raise Exception("create_midi_clip not available (requires Live 12+)")

        except Exception as e:
            self.log_message("Error creating arrangement clip: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _add_notes_to_arrangement_clip(self, track_index, clip_index, notes):
        """
        Add MIDI notes to an arrangement view clip.

        Args:
            track_index: Index of the track
            clip_index: Index of the clip in arrangement_clips
            notes: List of note dictionaries with pitch, start_time, duration, velocity, mute

        Returns:
            Dictionary with info about the added notes
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if not hasattr(track, 'arrangement_clips'):
                raise Exception("arrangement_clips not available (requires Live 11+)")

            if clip_index < 0 or clip_index >= len(track.arrangement_clips):
                raise IndexError("Arrangement clip index out of range")

            clip = track.arrangement_clips[clip_index]

            # Convert note data to Live 11+ MidiNoteSpecification format
            from Live import Clip as LiveClip

            live_notes = []
            for note in notes:
                # Support multiple field name formats from LLM
                pitch = note.get("pitch") or note.get("note") or 60
                start_time = note.get("start_time") or note.get("time") or 0.0
                duration = note.get("duration") or note.get("length") or 0.25
                velocity = note.get("velocity") or note.get("vel") or 100
                mute = note.get("mute", False)

                # Create MidiNoteSpecification for Live 11+
                note_spec = LiveClip.MidiNoteSpecification(
                    pitch=pitch,
                    start_time=start_time,
                    duration=duration,
                    velocity=velocity,
                    mute=mute
                )
                live_notes.append(note_spec)

            # Use add_new_notes for Live 11+
            clip.add_new_notes(tuple(live_notes))

            result = {
                "note_count": len(notes),
                "clip_name": clip.name,
                "track_index": track_index,
                "clip_index": clip_index
            }
            return result
        except Exception as e:
            self.log_message("Error adding notes to arrangement clip: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    # =========================================================================
    # Browser commands
    # =========================================================================

    def _get_browser_tree(self, category_type="all"):
        """Get a simplified tree of browser categories."""
        try:
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")

            if not hasattr(app, 'browser') or app.browser is None:
                raise RuntimeError("Browser is not available")

            result = {
                "type": category_type,
                "categories": []
            }

            def process_item(item):
                if not item:
                    return None
                return {
                    "name": item.name if hasattr(item, 'name') else "Unknown",
                    "is_folder": hasattr(item, 'children') and bool(item.children),
                    "is_loadable": hasattr(item, 'is_loadable') and item.is_loadable,
                    "uri": item.uri if hasattr(item, 'uri') else None
                }

            # Process standard categories
            categories_map = {
                "instruments": ("Instruments", "instruments"),
                "sounds": ("Sounds", "sounds"),
                "drums": ("Drums", "drums"),
                "audio_effects": ("Audio Effects", "audio_effects"),
                "midi_effects": ("MIDI Effects", "midi_effects"),
            }

            for key, (display_name, attr_name) in categories_map.items():
                if (category_type == "all" or category_type == key) and hasattr(app.browser, attr_name):
                    try:
                        cat_item = getattr(app.browser, attr_name)
                        cat = process_item(cat_item)
                        if cat:
                            cat["name"] = display_name
                            # Get first level children
                            if hasattr(cat_item, 'children'):
                                cat["children"] = []
                                for child in cat_item.children[:20]:  # Limit
                                    child_info = process_item(child)
                                    if child_info:
                                        cat["children"].append(child_info)
                            result["categories"].append(cat)
                    except Exception as e:
                        self.log_message("Error processing {}: {}".format(key, str(e)))

            return result
        except Exception as e:
            self.log_message("Error getting browser tree: " + str(e))
            raise

    def _get_browser_items_at_path(self, path):
        """Get browser items at a specific path."""
        try:
            app = self.application()
            if not app or not hasattr(app, 'browser'):
                raise RuntimeError("Browser not available")

            path_parts = path.split("/")
            if not path_parts:
                raise ValueError("Invalid path")

            root_category = path_parts[0].lower()
            current_item = None

            # Map to browser attributes
            category_map = {
                "instruments": "instruments",
                "sounds": "sounds",
                "drums": "drums",
                "audio_effects": "audio_effects",
                "midi_effects": "midi_effects",
            }

            if root_category in category_map and hasattr(app.browser, category_map[root_category]):
                current_item = getattr(app.browser, category_map[root_category])
            else:
                raise ValueError("Unknown category: " + root_category)

            # Navigate through path
            for i in range(1, len(path_parts)):
                part = path_parts[i]
                if not part:
                    continue

                if not hasattr(current_item, 'children'):
                    raise ValueError("Item has no children")

                found = False
                for child in current_item.children:
                    if hasattr(child, 'name') and child.name.lower() == part.lower():
                        current_item = child
                        found = True
                        break

                if not found:
                    raise ValueError("Path part '{}' not found".format(part))

            # Get items at current path
            items = []
            if hasattr(current_item, 'children'):
                for child in current_item.children:
                    items.append({
                        "name": child.name if hasattr(child, 'name') else "Unknown",
                        "is_folder": hasattr(child, 'children') and bool(child.children),
                        "is_loadable": hasattr(child, 'is_loadable') and child.is_loadable,
                        "uri": child.uri if hasattr(child, 'uri') else None
                    })

            return {
                "path": path,
                "name": current_item.name if hasattr(current_item, 'name') else "Unknown",
                "uri": current_item.uri if hasattr(current_item, 'uri') else None,
                "items": items
            }
        except Exception as e:
            self.log_message("Error getting browser items: " + str(e))
            raise

    def _get_all_presets(self, category_type, max_depth=5):
        """Recursively get all loadable presets from a browser category."""
        try:
            app = self.application()
            if not app or not hasattr(app, 'browser'):
                raise RuntimeError("Browser not available")

            category_map = {
                "instruments": "instruments",
                "sounds": "sounds",
                "drums": "drums",
                "audio_effects": "audio_effects",
                "midi_effects": "midi_effects",
            }

            if category_type not in category_map:
                raise ValueError("Unknown category: " + category_type)

            root = getattr(app.browser, category_map[category_type])
            all_presets = []

            def recurse(item, path, depth):
                if depth > max_depth:
                    return

                if not hasattr(item, 'children'):
                    return

                for child in item.children:
                    child_name = child.name if hasattr(child, 'name') else "Unknown"
                    child_path = path + "/" + child_name if path else child_name
                    child_uri = child.uri if hasattr(child, 'uri') else None
                    is_loadable = hasattr(child, 'is_loadable') and child.is_loadable
                    has_children = hasattr(child, 'children') and bool(child.children)

                    if is_loadable:
                        all_presets.append({
                            "name": child_name,
                            "path": child_path,
                            "uri": child_uri,
                            "is_folder": has_children
                        })

                    # Recurse into folders
                    if has_children:
                        recurse(child, child_path, depth + 1)

            recurse(root, "", 0)

            return {
                "category": category_type,
                "preset_count": len(all_presets),
                "presets": all_presets
            }
        except Exception as e:
            self.log_message("Error getting all presets: " + str(e))
            raise

    def _load_browser_item(self, track_index, item_uri):
        """Load a browser item onto a track by its URI."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            app = self.application()

            # Find the browser item by URI
            item = self._find_browser_item_by_uri(app.browser, item_uri)

            if not item:
                raise ValueError("Browser item with URI '{}' not found".format(item_uri))

            # Select the track and load the item
            self._song.view.selected_track = track
            app.browser.load_item(item)

            # Get devices after loading
            devices_after = [d.name for d in track.devices]

            return {
                "loaded": True,
                "item_name": item.name,
                "track_name": track.name,
                "uri": item_uri,
                "devices_after": devices_after
            }
        except Exception as e:
            self.log_message("Error loading browser item: " + str(e))
            raise

    def _find_browser_item_by_uri(self, browser_or_item, uri, max_depth=10, current_depth=0):
        """Find a browser item by its URI recursively."""
        try:
            if hasattr(browser_or_item, 'uri') and browser_or_item.uri == uri:
                return browser_or_item

            if current_depth >= max_depth:
                return None

            # Check root categories if this is the browser
            if hasattr(browser_or_item, 'instruments'):
                for category in [browser_or_item.instruments, browser_or_item.sounds,
                                browser_or_item.drums, browser_or_item.audio_effects,
                                browser_or_item.midi_effects]:
                    item = self._find_browser_item_by_uri(category, uri, max_depth, current_depth + 1)
                    if item:
                        return item
                return None

            # Check children
            if hasattr(browser_or_item, 'children') and browser_or_item.children:
                for child in browser_or_item.children:
                    item = self._find_browser_item_by_uri(child, uri, max_depth, current_depth + 1)
                    if item:
                        return item

            return None
        except Exception as e:
            self.log_message("Error finding browser item: " + str(e))
            return None

    # =========================================================================
    # Device parameter commands
    # =========================================================================

    def _get_device_parameters(self, track_index, device_index):
        """Get all parameters for a device on a track."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range. Track has {} devices.".format(len(track.devices)))

            device = track.devices[device_index]

            parameters = []
            for i, param in enumerate(device.parameters):
                param_info = {
                    "index": i,
                    "name": param.name,
                    "value": param.value,
                    "min": param.min,
                    "max": param.max,
                    "is_enabled": param.is_enabled,
                    "is_quantized": param.is_quantized
                }
                # Add default value if available (safely)
                try:
                    if hasattr(param, 'default_value'):
                        param_info["default_value"] = param.default_value
                except:
                    pass  # Some parameter types don't support default_value
                parameters.append(param_info)

            return {
                "track_index": track_index,
                "track_name": track.name,
                "device_index": device_index,
                "device_name": device.name,
                "device_class": device.class_name if hasattr(device, 'class_name') else "Unknown",
                "parameter_count": len(parameters),
                "parameters": parameters
            }
        except Exception as e:
            self.log_message("Error getting device parameters: " + str(e))
            raise

    def _set_device_parameter(self, track_index, device_index, parameter_index, value):
        """Set a parameter value on a device."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range. Track has {} devices.".format(len(track.devices)))

            device = track.devices[device_index]

            if parameter_index < 0 or parameter_index >= len(device.parameters):
                raise IndexError("Parameter index out of range. Device has {} parameters.".format(len(device.parameters)))

            param = device.parameters[parameter_index]

            # Clamp value to valid range
            clamped_value = max(param.min, min(param.max, value))

            # Set the value
            param.value = clamped_value

            return {
                "track_index": track_index,
                "device_index": device_index,
                "device_name": device.name,
                "parameter_index": parameter_index,
                "parameter_name": param.name,
                "old_value": value,  # What was requested
                "new_value": param.value,  # What was actually set
                "min": param.min,
                "max": param.max
            }
        except Exception as e:
            self.log_message("Error setting device parameter: " + str(e))
            raise

    # =========================================================================
    # Mixer Controls (Priority 1)
    # =========================================================================

    def _value_to_db(self, value):
        """Convert 0-1 volume value to approximate dB for display"""
        import math
        if value <= 0:
            return "-inf"
        db = 20 * math.log10(value)
        return round(db, 1)

    def _set_track_volume(self, track_index, volume):
        """Set track volume (0.0 to 1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clamped = max(0.0, min(1.0, volume))
            track.mixer_device.volume.value = clamped
            return {
                "track_index": track_index,
                "volume": track.mixer_device.volume.value,
                "volume_db": self._value_to_db(track.mixer_device.volume.value)
            }
        except Exception as e:
            self.log_message("Error setting track volume: " + str(e))
            raise

    def _set_track_pan(self, track_index, pan):
        """Set track pan (-1.0 left to 1.0 right)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clamped = max(-1.0, min(1.0, pan))
            track.mixer_device.panning.value = clamped
            return {
                "track_index": track_index,
                "pan": track.mixer_device.panning.value
            }
        except Exception as e:
            self.log_message("Error setting track pan: " + str(e))
            raise

    def _set_send_level(self, track_index, send_index, level):
        """Set send level to return track (0.0 to 1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            sends = track.mixer_device.sends
            if send_index < 0 or send_index >= len(sends):
                raise IndexError("Send index out of range. Track has {} sends.".format(len(sends)))
            clamped = max(0.0, min(1.0, level))
            sends[send_index].value = clamped
            return {
                "track_index": track_index,
                "send_index": send_index,
                "level": sends[send_index].value
            }
        except Exception as e:
            self.log_message("Error setting send level: " + str(e))
            raise

    def _set_track_mute(self, track_index, mute):
        """Set track mute state"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.mute = mute
            return {"track_index": track_index, "mute": track.mute}
        except Exception as e:
            self.log_message("Error setting track mute: " + str(e))
            raise

    def _set_track_solo(self, track_index, solo):
        """Set track solo state"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.solo = solo
            return {"track_index": track_index, "solo": track.solo}
        except Exception as e:
            self.log_message("Error setting track solo: " + str(e))
            raise

    def _get_return_tracks(self):
        """Get info about all return tracks"""
        try:
            returns = []
            for i, track in enumerate(self._song.return_tracks):
                devices = []
                for d in track.devices:
                    devices.append({"name": d.name, "class_name": d.class_name})
                returns.append({
                    "index": i,
                    "name": track.name,
                    "volume": track.mixer_device.volume.value,
                    "pan": track.mixer_device.panning.value,
                    "mute": track.mute,
                    "solo": track.solo,
                    "devices": devices
                })
            return {"return_tracks": returns, "count": len(returns)}
        except Exception as e:
            self.log_message("Error getting return tracks: " + str(e))
            raise

    def _set_return_track_volume(self, return_index, volume):
        """Set return track volume (0.0 to 1.0)"""
        try:
            if return_index < 0 or return_index >= len(self._song.return_tracks):
                raise IndexError("Return track index out of range")
            track = self._song.return_tracks[return_index]
            clamped = max(0.0, min(1.0, volume))
            track.mixer_device.volume.value = clamped
            return {
                "return_index": return_index,
                "volume": track.mixer_device.volume.value
            }
        except Exception as e:
            self.log_message("Error setting return track volume: " + str(e))
            raise

    # =========================================================================
    # Audio Clip Properties (Priority 2)
    # =========================================================================

    def _get_arrangement_clip_by_index(self, track_index, clip_index):
        """Helper to get arrangement clip with validation"""
        if track_index < 0 or track_index >= len(self._song.tracks):
            raise IndexError("Track index out of range")
        track = self._song.tracks[track_index]

        if not hasattr(track, 'arrangement_clips'):
            raise ValueError("Track has no arrangement clips")

        clips = list(track.arrangement_clips)
        if clip_index < 0 or clip_index >= len(clips):
            raise IndexError("Clip index out of range")

        return clips[clip_index]

    def _get_audio_clip_properties(self, track_index, clip_index):
        """Get comprehensive audio clip properties"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)

            if not clip.is_audio_clip:
                raise ValueError("Not an audio clip")

            result = {
                "name": clip.name,
                "gain": clip.gain,
                "gain_display": clip.gain_display_string,
                "pitch_coarse": clip.pitch_coarse,
                "pitch_fine": clip.pitch_fine,
                "warping": clip.warping,
                "warp_mode": clip.warp_mode,
                "loop_start": clip.loop_start,
                "loop_end": clip.loop_end,
                "looping": clip.looping,
                "start_marker": clip.start_marker,
                "end_marker": clip.end_marker,
                "length": clip.length,
                "muted": clip.muted,
                "color_index": clip.color_index,
            }

            try:
                result["file_path"] = clip.file_path
            except:
                pass

            return result
        except Exception as e:
            self.log_message("Error getting audio clip properties: " + str(e))
            raise

    def _set_clip_gain(self, track_index, clip_index, gain):
        """Set audio clip gain (0.0 to 1.0)"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)
            if not clip.is_audio_clip:
                raise ValueError("Not an audio clip")

            clamped = max(0.0, min(1.0, gain))
            clip.gain = clamped

            return {
                "gain": clip.gain,
                "gain_display": clip.gain_display_string
            }
        except Exception as e:
            self.log_message("Error setting clip gain: " + str(e))
            raise

    def _set_clip_pitch(self, track_index, clip_index, semitones, cents):
        """Set audio clip pitch shift (semitones: -48 to 48, cents: -50 to 49)"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)
            if not clip.is_audio_clip:
                raise ValueError("Not an audio clip")

            semitones = max(-48, min(48, semitones))
            cents = max(-50, min(49, cents))

            clip.pitch_coarse = semitones
            clip.pitch_fine = cents

            return {
                "pitch_coarse": clip.pitch_coarse,
                "pitch_fine": clip.pitch_fine
            }
        except Exception as e:
            self.log_message("Error setting clip pitch: " + str(e))
            raise

    def _set_clip_loop(self, track_index, clip_index, loop_start, loop_end, looping):
        """Set clip loop parameters"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)

            if looping is not None:
                clip.looping = looping
            if loop_start is not None:
                clip.loop_start = loop_start
            if loop_end is not None:
                clip.loop_end = loop_end

            return {
                "looping": clip.looping,
                "loop_start": clip.loop_start,
                "loop_end": clip.loop_end
            }
        except Exception as e:
            self.log_message("Error setting clip loop: " + str(e))
            raise

    def _set_clip_warp_mode(self, track_index, clip_index, warp_mode):
        """Set audio clip warp mode (0=Beats, 1=Tones, 2=Texture, 3=Re-Pitch, 4=Complex, 5=Complex Pro)"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)
            if not clip.is_audio_clip:
                raise ValueError("Not an audio clip")

            clip.warp_mode = warp_mode
            return {"warp_mode": clip.warp_mode}
        except Exception as e:
            self.log_message("Error setting clip warp mode: " + str(e))
            raise

    def _get_clip_warp_markers(self, track_index, clip_index):
        """Get warp markers for audio clip (Live 11+)"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)
            if not clip.is_audio_clip:
                raise ValueError("Not an audio clip")

            try:
                markers = clip.warp_markers
                return {"warp_markers": markers}
            except:
                return {"warp_markers": [], "note": "Requires Live 11+"}
        except Exception as e:
            self.log_message("Error getting clip warp markers: " + str(e))
            raise

    # =========================================================================
    # Track Organization (Priority 3)
    # =========================================================================

    def _create_audio_track(self, index):
        """Create a new audio track"""
        try:
            self._song.create_audio_track(index)
            new_index = len(self._song.tracks) - 1 if index == -1 else index
            return {"index": new_index, "name": self._song.tracks[new_index].name}
        except Exception as e:
            self.log_message("Error creating audio track: " + str(e))
            raise

    def _delete_track(self, track_index):
        """Delete a track (DESTRUCTIVE)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._song.delete_track(track_index)
            return {
                "deleted": True,
                "track_index": track_index,
                "warning": "Track deleted. Use automator_undo to revert if needed."
            }
        except Exception as e:
            self.log_message("Error deleting track: " + str(e))
            raise

    def _create_return_track(self):
        """Create a new return track"""
        try:
            self._song.create_return_track()
            new_index = len(self._song.return_tracks) - 1
            return {"index": new_index, "name": self._song.return_tracks[new_index].name}
        except Exception as e:
            self.log_message("Error creating return track: " + str(e))
            raise

    def _set_track_color(self, track_index, color_index):
        """Set track color by index"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.color_index = color_index
            return {"track_index": track_index, "color_index": track.color_index}
        except Exception as e:
            self.log_message("Error setting track color: " + str(e))
            raise

    def _get_track_routing(self, track_index):
        """Get track input/output routing info"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            result = {}
            if hasattr(track, 'input_routing_type') and hasattr(track.input_routing_type, 'display_name'):
                result["input_routing_type"] = str(track.input_routing_type.display_name)
            if hasattr(track, 'output_routing_type') and hasattr(track.output_routing_type, 'display_name'):
                result["output_routing_type"] = str(track.output_routing_type.display_name)
            return result
        except Exception as e:
            self.log_message("Error getting track routing: " + str(e))
            raise

    def _fold_track(self, track_index, fold):
        """Fold/unfold a group track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if hasattr(track, 'fold_state'):
                track.fold_state = 1 if fold else 0
                return {"track_index": track_index, "fold_state": track.fold_state}
            else:
                raise ValueError("Track is not a group track")
        except Exception as e:
            self.log_message("Error folding track: " + str(e))
            raise

    # =========================================================================
    # Device Chain Management (Priority 4)
    # =========================================================================

    def _delete_device(self, track_index, device_index):
        """Delete a device from track (DESTRUCTIVE)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device_name = track.devices[device_index].name
            track.delete_device(device_index)
            return {"deleted": device_name, "warning": "Device deleted. Use automator_undo to revert if needed."}
        except Exception as e:
            self.log_message("Error deleting device: " + str(e))
            raise

    def _set_device_enabled(self, track_index, device_index, enabled):
        """Enable/disable a device"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            for param in device.parameters:
                if param.name == "Device On":
                    param.value = 1.0 if enabled else 0.0
                    return {"device_name": device.name, "enabled": param.value == 1.0}
            raise ValueError("Device does not have on/off control")
        except Exception as e:
            self.log_message("Error setting device enabled: " + str(e))
            raise

    def _set_device_parameter_by_name(self, track_index, device_index, param_name, value):
        """Set device parameter by name (fuzzy match)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]

            param_name_lower = param_name.lower()

            # Try exact match first
            for param in device.parameters:
                if param.name.lower() == param_name_lower:
                    clamped = max(param.min, min(param.max, value))
                    param.value = clamped
                    return {
                        "parameter_name": param.name,
                        "value": param.value,
                        "min": param.min,
                        "max": param.max
                    }

            # Try partial match
            for param in device.parameters:
                if param_name_lower in param.name.lower():
                    clamped = max(param.min, min(param.max, value))
                    param.value = clamped
                    return {
                        "parameter_name": param.name,
                        "value": param.value,
                        "min": param.min,
                        "max": param.max,
                        "note": "Partial match"
                    }

            raise ValueError("Parameter '{}' not found on device '{}'".format(param_name, device.name))
        except Exception as e:
            self.log_message("Error setting device parameter by name: " + str(e))
            raise

    # =========================================================================
    # Arrangement Editing (Priority 5)
    # =========================================================================

    def _set_clip_mute(self, track_index, clip_index, muted):
        """Mute/unmute a clip"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)
            clip.muted = muted
            return {"muted": clip.muted}
        except Exception as e:
            self.log_message("Error setting clip mute: " + str(e))
            raise

    def _set_clip_start_end(self, track_index, clip_index, start_marker, end_marker):
        """Set clip start/end markers"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)
            if start_marker is not None:
                clip.start_marker = start_marker
            if end_marker is not None:
                clip.end_marker = end_marker
            return {
                "start_marker": clip.start_marker,
                "end_marker": clip.end_marker
            }
        except Exception as e:
            self.log_message("Error setting clip start/end: " + str(e))
            raise

    def _set_clip_color(self, track_index, clip_index, color_index):
        """Set clip color"""
        try:
            clip = self._get_arrangement_clip_by_index(track_index, clip_index)
            clip.color_index = color_index
            return {"color_index": clip.color_index}
        except Exception as e:
            self.log_message("Error setting clip color: " + str(e))
            raise

    # =========================================================================
    # Master Track (Priority 6)
    # =========================================================================

    def _get_master_track(self):
        """Get master track info"""
        try:
            master = self._song.master_track
            devices = []
            for i, device in enumerate(master.devices):
                devices.append({
                    "index": i,
                    "name": device.name,
                    "class_name": device.class_name
                })

            return {
                "volume": master.mixer_device.volume.value,
                "pan": master.mixer_device.panning.value,
                "devices": devices,
                "device_count": len(devices)
            }
        except Exception as e:
            self.log_message("Error getting master track: " + str(e))
            raise

    def _set_master_volume(self, volume):
        """Set master track volume"""
        try:
            master = self._song.master_track
            clamped = max(0.0, min(1.0, volume))
            master.mixer_device.volume.value = clamped
            return {"volume": master.mixer_device.volume.value}
        except Exception as e:
            self.log_message("Error setting master volume: " + str(e))
            raise

    def _get_master_device_parameters(self, device_index):
        """Get parameters for a device on master track"""
        try:
            master = self._song.master_track
            if device_index >= len(master.devices):
                raise IndexError("Device index out of range")
            device = master.devices[device_index]

            parameters = []
            for i, param in enumerate(device.parameters):
                parameters.append({
                    "index": i,
                    "name": param.name,
                    "value": param.value,
                    "min": param.min,
                    "max": param.max
                })

            return {
                "device_name": device.name,
                "parameters": parameters
            }
        except Exception as e:
            self.log_message("Error getting master device parameters: " + str(e))
            raise

    def _set_master_device_parameter(self, device_index, parameter_index, value):
        """Set a parameter on a master track device"""
        try:
            master = self._song.master_track
            if device_index >= len(master.devices):
                raise IndexError("Device index out of range")
            device = master.devices[device_index]
            if parameter_index >= len(device.parameters):
                raise IndexError("Parameter index out of range")
            param = device.parameters[parameter_index]
            clamped = max(param.min, min(param.max, value))
            param.value = clamped
            return {
                "device_name": device.name,
                "parameter_name": param.name,
                "value": param.value
            }
        except Exception as e:
            self.log_message("Error setting master device parameter: " + str(e))
            raise

    # =========================================================================
    # Transport and Selection (Priority 7)
    # =========================================================================

    def _get_current_position(self):
        """Get current playhead position in beats"""
        try:
            return {
                "position": self._song.current_song_time,
                "is_playing": self._song.is_playing,
                "tempo": self._song.tempo
            }
        except Exception as e:
            self.log_message("Error getting current position: " + str(e))
            raise

    def _set_current_position(self, position):
        """Set playhead position in beats"""
        try:
            self._song.current_song_time = max(0.0, position)
            return {
                "position": self._song.current_song_time,
                "is_playing": self._song.is_playing
            }
        except Exception as e:
            self.log_message("Error setting current position: " + str(e))
            raise

    def _select_track(self, track_index):
        """Select a track by index"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            self._song.view.selected_track = track
            return {
                "track_index": track_index,
                "track_name": track.name,
                "selected": True
            }
        except Exception as e:
            self.log_message("Error selecting track: " + str(e))
            raise

    def _select_clip(self, track_index, clip_index):
        """
        Select an arrangement clip for editing operations.
        This sets the clip as the detail clip and positions playhead at its start.

        For split operations, you may need to also call set_current_position
        to move the playhead to where you want the split to occur.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if not hasattr(track, 'arrangement_clips'):
                raise ValueError("Track has no arrangement clips")

            clips = list(track.arrangement_clips)
            if clip_index < 0 or clip_index >= len(clips):
                raise IndexError("Clip index out of range. Track has {} arrangement clips.".format(len(clips)))

            clip = clips[clip_index]

            # Select the track first
            self._song.view.selected_track = track

            # Set this clip as the detail clip (shows in clip view)
            self._song.view.detail_clip = clip

            # For arrangement view selection, we also need to highlight the clip
            # This positions the view on the clip
            if hasattr(self._song.view, 'highlighted_clip_slot'):
                # Session view uses highlighted_clip_slot, but for arrangement
                # we rely on detail_clip and positioning
                pass

            result = {
                "track_index": track_index,
                "track_name": track.name,
                "clip_index": clip_index,
                "clip_name": clip.name,
                "clip_start": clip.start_time,
                "clip_end": clip.end_time,
                "clip_length": clip.length,
                "selected": True,
                "note": "Clip selected. For split, position playhead with set_current_position then use automator_split."
            }

            return result
        except Exception as e:
            self.log_message("Error selecting clip: " + str(e))
            raise
