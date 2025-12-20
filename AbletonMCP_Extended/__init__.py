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
                "set_device_parameter"
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
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
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
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
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
