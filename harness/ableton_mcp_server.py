#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.3.0", "numpy", "scipy", "soundfile", "mido", "pyloudnorm"]
# ///
"""
ableton_mcp_server.py — Extended Ableton Live stdio MCP server.

Exposes the FULL extended toolset to any MCP client (Claude Desktop, etc.):
  - 57 Live Object Model commands over the TCP socket (localhost:9877) served
    by the AbletonMCP_Extended Remote Script — transport, tracks, session &
    arrangement clips, MIDI notes, mixer, master, track org, device params,
    browser/device loading, and audio-clip properties.
  - The GUI-automation ("automator") toolset from AbletonMCP_Extended/
    automator_bridge.py — split/consolidate/freeze/group/smart-select, etc.
    These are AppleScript-driven and NOT reachable over the socket, so this
    server imports the bridge and calls it in-process.

Socket protocol (matches the base fork server, proven working):
  request : {"type": <command>, "params": {...}}  raw UTF-8 JSON, no framing
  response: {"status":"success","result":{...}} | {"status":"error","message":...}
  A message is "complete" when the accumulated bytes parse as valid JSON.

Run:  uv run --script harness/ableton_mcp_server.py
Requires Ableton Live open with the AbletonMCP_Extended Remote Script loaded
(listening on port 9877). Automator tools additionally need macOS Accessibility
permission for the process running this server.
"""

from mcp.server.fastmcp import FastMCP, Context
import socket
import json
import time
import logging
import os
import sys
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List, Union, Optional

# ---------------------------------------------------------------------------
# Logging (to stderr; stdout is reserved for the MCP stdio transport)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("AbletonMCPExtended")

ABLETON_HOST = "localhost"
ABLETON_PORT = 9877

# Commands that mutate Live state. The Remote Script marshals these onto Live's
# main thread, so we give them a longer timeout and a small settle delay.
MODIFYING_COMMANDS = {
    # transport / selection
    "set_tempo", "start_playback", "stop_playback", "set_current_position",
    "select_track", "select_clip",
    # tracks / org
    "create_midi_track", "create_audio_track", "create_return_track",
    "delete_track", "set_track_name", "set_track_color", "fold_track",
    # mixer / master
    "set_track_volume", "set_track_pan", "set_send_level", "set_track_mute",
    "set_track_solo", "set_return_track_volume", "set_master_volume",
    "set_master_device_parameter",
    # session clips / notes
    "create_clip", "add_notes_to_clip", "set_clip_name", "fire_clip", "stop_clip",
    # arrangement
    "create_arrangement_clip", "add_notes_to_arrangement_clip",
    "duplicate_clip_to_arrangement", "set_clip_mute", "set_clip_color",
    "set_clip_start_end",
    # audio-clip props
    "set_clip_gain", "set_clip_pitch", "set_clip_loop", "set_clip_warp_mode",
    # devices / browser
    "set_device_parameter", "set_device_parameter_by_name", "set_device_enabled",
    "delete_device", "load_browser_item",
}

# ---------------------------------------------------------------------------
# Automator bridge (GUI automation) — imported in-process, NOT over the socket.
# We add the AbletonMCP_Extended dir directly to sys.path so we import the
# standalone automator_bridge module WITHOUT triggering the package __init__
# (that __init__ is the Live-only Remote Script and fails outside Ableton).
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)  # so sibling modules (ableton_knowledge) import cleanly
sys.path.insert(0, os.path.join(_HERE, "AbletonMCP_Extended"))
try:
    import automator_bridge  # type: ignore
    _handle_automator = automator_bridge.handle_automator_command
    _AUTOMATOR_ERR = None
    logger.info("Automator bridge loaded (GUI automation available)")
except Exception as e:  # pragma: no cover - defensive
    _handle_automator = None
    _AUTOMATOR_ERR = str(e)
    logger.warning(f"Automator bridge unavailable: {e}")

# The "producer brain": instrument catalog, genre profiles, pattern generators.
try:
    import ableton_knowledge as K  # type: ignore
    _KB_ERR = None
    logger.info("Knowledge base loaded (genre-aware instruments + patterns)")
except Exception as e:  # pragma: no cover - defensive
    K = None
    _KB_ERR = str(e)
    logger.warning(f"Knowledge base unavailable: {e}")


# ---------------------------------------------------------------------------
# Socket connection to the Remote Script (protocol copied from the base fork
# server, which is verified working against this Remote Script).
# ---------------------------------------------------------------------------
@dataclass
class AbletonConnection:
    host: str
    port: int
    sock: socket.socket = None

    def connect(self) -> bool:
        if self.sock:
            return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Ableton at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ableton: {e}")
            self.sock = None
            return False

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Ableton: {e}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192) -> bytes:
        """Read until the accumulated bytes parse as one complete JSON object."""
        chunks = []
        sock.settimeout(15.0)
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise Exception("Connection closed before receiving any data")
                        break
                    chunks.append(chunk)
                    try:
                        data = b"".join(chunks)
                        json.loads(data.decode("utf-8"))
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        continue  # incomplete, keep reading
                except socket.timeout:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {e}")
                    raise
        except Exception as e:
            logger.error(f"Error during receive: {e}")
            raise
        if chunks:
            data = b"".join(chunks)
            try:
                json.loads(data.decode("utf-8"))
                return data
            except json.JSONDecodeError:
                raise Exception("Incomplete JSON response received")
        raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Ableton")

        command = {"type": command_type, "params": params or {}}
        is_modifying = command_type in MODIFYING_COMMANDS
        try:
            logger.info(f"Sending command: {command_type} with params: {params}")
            self.sock.sendall(json.dumps(command).encode("utf-8"))
            if is_modifying:
                time.sleep(0.1)  # give Live a moment before we read
            self.sock.settimeout(15.0 if is_modifying else 10.0)
            response_data = self.receive_full_response(self.sock)
            response = json.loads(response_data.decode("utf-8"))
            if response.get("status") == "error":
                logger.error(f"Ableton error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Ableton"))
            if is_modifying:
                time.sleep(0.1)
            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Ableton")
            self.sock = None
            raise Exception("Timeout waiting for Ableton response")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {e}")
            self.sock = None
            raise Exception(f"Connection to Ableton lost: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ableton: {e}")
            self.sock = None
            raise Exception(f"Invalid response from Ableton: {e}")
        except Exception as e:
            logger.error(f"Error communicating with Ableton: {e}")
            self.sock = None
            raise


_ableton_connection: Optional[AbletonConnection] = None


def get_ableton_connection() -> AbletonConnection:
    """Return a live singleton connection, (re)connecting with retries if needed."""
    global _ableton_connection
    if _ableton_connection is not None:
        try:
            _ableton_connection.sock.settimeout(1.0)
            _ableton_connection.sock.sendall(b"")  # liveness probe
            return _ableton_connection
        except Exception:
            logger.warning("Existing connection invalid, reconnecting...")
            try:
                _ableton_connection.disconnect()
            except Exception:
                pass
            _ableton_connection = None

    for attempt in range(1, 4):
        conn = AbletonConnection(host=ABLETON_HOST, port=ABLETON_PORT)
        if conn.connect():
            try:
                conn.send_command("get_session_info")  # validate
                _ableton_connection = conn
                return conn
            except Exception as e:
                logger.warning(f"Validation failed (attempt {attempt}/3): {e}")
                conn.disconnect()
        if attempt < 3:
            time.sleep(1.0)
    raise Exception(
        "Could not connect to Ableton. Make sure Live is open with the "
        "AbletonMCP_Extended Remote Script loaded (listening on port 9877)."
    )


# ---------------------------------------------------------------------------
# Server + helpers
# ---------------------------------------------------------------------------
@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    logger.info("AbletonMCP Extended server starting up")
    try:
        try:
            get_ableton_connection()
            logger.info("Connected to Ableton on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Ableton on startup: {e}")
            logger.warning("Server will still start; connect Live and retry a tool call.")
        yield {}
    finally:
        global _ableton_connection
        if _ableton_connection:
            _ableton_connection.disconnect()
            _ableton_connection = None
        logger.info("AbletonMCP Extended server shut down")


SERVER_INSTRUCTIONS = """\
Control Ableton Live and MAKE MUSIC THAT ACTUALLY PLAYS. Prefer the high-level
WORKFLOW tools — they encode genre best-practices and pick the right instruments,
so you don't have to. Only drop to low-level tools for precise edits.

YOU are the composer. These tools do NOT generate MIDI for you — they set up the
session with the right instruments and hand you STYLE knowledge; you write the notes.

FOR ANY CREATIVE REQUEST ("make a boom bap beat", "write a lofi loop", "add a bassline"):
  1. style_guide(genre) — how the genre is actually played: feel/groove, the drum-map +
     where each hit sits, harmony (scale + progression), bass/melody approach, reference
     artists, and what to avoid. (production_guide(genre) gives the short recipe + steps.)
  2. scaffold_song(genre, bars, parts) — ONE call creates a track per part, loads the RIGHT
     instrument for the style (boom bap keys = Electric/Rhodes, drums = a dusty KIT with
     samples — NEVER an empty Drum Rack or a generic default), and makes an EMPTY arrangement
     clip for each. It returns {role, track, clip_index} per part + the style guide.
     (Or add_part(role, genre) for one part at a time.)
  3. COMPOSE the MIDI yourself from the style guide and write it per clip with
     add_notes_to_arrangement_clip(track, clip_index, notes). notes are
     [{pitch,start_time,duration,velocity}] with times in BEATS (1 bar of 4/4 = 4 beats).
     Humanize velocity/timing where the feel calls for it.
  4. Finish: balance_mix(), then get_playability_report(). If any track is SILENT (no
     instrument) fix it before telling the user it's done.

INSTRUMENT CHOICE MATTERS: do NOT default every track to the same synth — the scaffold
tools pick a genre-appropriate palette. Use suggest_instruments(role, genre) to compare.
A MIDI track with no instrument is SILENT.

LOW-LEVEL CONTROL: call browse_tools() to discover the ~80 primitives by category
(mixer, device, arrangement, browser, automator, ...). Build songs in the ARRANGEMENT
(create_arrangement_clip -> add_notes_to_arrangement_clip; times in BEATS, 1 bar = 4
beats). Session-view tools only if the user explicitly asks. clip_index means a SESSION
SLOT for session tools but an ARRANGEMENT CLIP for arrangement/audio tools.

Tracks resolve by name OR index everywhere. Search browsers sparingly (they're slow) —
prefer load_instrument / a specific get_browser_items_at_path path over broad get_all_presets.
"""

mcp = FastMCP(
    "AbletonExtended",
    instructions=SERVER_INSTRUCTIONS,
    lifespan=server_lifespan,
)


def _cmd(command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Send a socket command via the singleton connection."""
    return get_ableton_connection().send_command(command_type, params or {})


def _ok(result: Any) -> str:
    """Serialize a successful result for the client."""
    if isinstance(result, str):
        return result
    return json.dumps(result, indent=2, default=str)


def _err(context: str, e: Exception) -> str:
    return f"Error {context}: {e}"


def _automator(command_type: str, params: Dict[str, Any] = None) -> str:
    if _handle_automator is None:
        return (
            f"Automator (GUI automation) unavailable: {_AUTOMATOR_ERR}. "
            "It needs macOS + Accessibility permission for this process."
        )
    try:
        return _ok(_handle_automator(command_type, params or {}))
    except Exception as e:
        return _err(f"running {command_type}", e)


# --- name-based track resolution (the "extended" convenience) --------------
_track_cache: Dict[str, Any] = {"t": 0.0, "names": []}


def _track_names() -> List:
    """Cached (index, name) list; only rebuilt when a name lookup is needed."""
    now = time.time()
    if now - _track_cache["t"] < 3.0 and _track_cache["names"]:
        return _track_cache["names"]
    info = _cmd("get_session_info")
    count = int(info.get("track_count", 0))
    names = []
    for i in range(count):
        try:
            ti = _cmd("get_track_info", {"track_index": i})
            names.append((i, ti.get("name", f"Track {i}")))
        except Exception:
            names.append((i, f"Track {i}"))
    _track_cache.update(t=now, names=names)
    return names


def _resolve_track(track: Union[int, str]) -> int:
    """Accept a track index (int/numeric string) or a track NAME and return the index."""
    if isinstance(track, bool):  # guard: bool is a subclass of int
        raise Exception(f"Invalid track reference: {track}")
    if isinstance(track, int):
        return track
    s = str(track).strip()
    if s.lstrip("-").isdigit():
        return int(s)
    names = _track_names()
    low = s.lower()
    for i, n in names:  # exact (case-insensitive)
        if n.lower() == low:
            return i
    for i, n in names:  # partial
        if low in n.lower():
            return i
    available = ", ".join(f"{i}:{n}" for i, n in names) or "(none)"
    raise Exception(f"No track matching '{s}'. Available -> {available}")


def _resolve_tracks(tracks: List[Union[int, str]]) -> List[int]:
    return [_resolve_track(t) for t in tracks]


# --- playability / completion feedback loop --------------------------------
# class_name substrings that indicate a sound-producing instrument device.
_INSTRUMENT_MARKERS = (
    "drumgroupdevice", "instrumentgroupdevice", "impulse", "operator",
    "instrumentvector", "wavetable", "ultraanalog", "analog", "originalsimpler",
    "simpler", "multisampler", "sampler", "drift", "meld", "loungelizard",
    "lounglizard", "stringstudio", "tension", "collision", "electric",
    "plugindevice", "auplugindevice", "mxdeviceinstrument", "bass",
)
# Preferred stock synths for load_instrument when no name hint is given.
_MELODIC_DEFAULTS = ("Wavetable", "Operator", "Analog", "Drift")


def _find_instrument(devices) -> Optional[Dict[str, Any]]:
    """Return the first instrument device on a track, or None (=> track is silent)."""
    for d in devices or []:
        cls = str(d.get("class_name", "")).lower()
        if any(m in cls for m in _INSTRUMENT_MARKERS):
            return d
    return None


def _analyze_track(ti: Dict[str, Any]) -> Dict[str, Any]:
    """Build a playability record from a get_track_info result."""
    devices = ti.get("devices", [])
    is_midi = bool(ti.get("is_midi_track"))
    is_audio = bool(ti.get("is_audio_track"))
    instr = _find_instrument(devices)
    session_clips = sum(1 for s in ti.get("clip_slots", []) if s.get("has_clip"))
    arr_clips = int(ti.get("arrangement_clip_count", 0))
    has_content = session_clips > 0 or arr_clips > 0

    warnings: List[str] = []
    if is_midi and instr is None:
        warnings.append("SILENT: MIDI track has no instrument - notes make no sound. Use load_instrument.")
    elif is_midi and instr is not None:
        cls = str(instr.get("class_name", "")).lower()
        nm = str(instr.get("name", "")).strip().lower()
        if "drumgroup" in cls and nm in ("drum rack", ""):
            warnings.append("Drum Rack may be empty/silent - load a kit (load_instrument, 'drum kit').")
    if not has_content:
        warnings.append("No clips on this track yet.")

    capable = (instr is not None) if is_midi else is_audio
    return {
        "index": ti.get("index"),
        "name": ti.get("name"),
        "type": "midi" if is_midi else ("audio" if is_audio else "other"),
        "instrument": instr.get("name") if instr else None,
        "has_instrument": instr is not None,
        "session_clips": session_clips,
        "arrangement_clips": arr_clips,
        "ready_to_play": bool(capable and has_content),
        "warnings": warnings,
    }


def _silence_suffix(resolved_track_index: int) -> str:
    """Return a short inline warning if adding notes here won't produce sound."""
    try:
        rec = _analyze_track(_cmd("get_track_info", {"track_index": resolved_track_index}))
        crit = [w for w in rec["warnings"] if "SILENT" in w or "Drum Rack" in w]
        if crit:
            return "\n\n[playability] " + " ".join(crit)
    except Exception:
        pass
    return ""


# ===========================================================================
# SESSION / INFO  (read-only)
# ===========================================================================
@mcp.tool()
def get_session_info() -> str:
    """Get global session state: tempo, time signature, track counts, playhead, playing status, master info."""
    try:
        return _ok(_cmd("get_session_info"))
    except Exception as e:
        return _err("getting session info", e)


@mcp.tool()
def get_session_summary() -> str:
    """Get a compact, LLM-friendly summary of the session (tempo + per-track category/devices/clip counts). Skips empty tracks."""
    try:
        return _ok(_cmd("get_session_summary"))
    except Exception as e:
        return _err("getting session summary", e)


@mcp.tool()
def get_all_tracks() -> str:
    """List every track with its index and name. Use this to resolve track names before other calls (or just pass names directly to track_index)."""
    try:
        return _ok([{"index": i, "name": n} for i, n in _track_names()])
    except Exception as e:
        return _err("listing tracks", e)


@mcp.tool()
def get_track_info(track_index: Union[int, str]) -> str:
    """Get full state of one track (name, mute/solo/arm, volume, pan, first 8 clip slots, arrangement clips, devices). track_index accepts an index or a track name."""
    try:
        return _ok(_cmd("get_track_info", {"track_index": _resolve_track(track_index)}))
    except Exception as e:
        return _err("getting track info", e)


# ===========================================================================
# TRANSPORT / PLAYBACK / SELECTION
# ===========================================================================
@mcp.tool()
def set_tempo(tempo: float) -> str:
    """Set the song tempo in BPM."""
    try:
        return _ok(_cmd("set_tempo", {"tempo": tempo}))
    except Exception as e:
        return _err("setting tempo", e)


@mcp.tool()
def start_playback() -> str:
    """Start playing the session/arrangement."""
    try:
        return _ok(_cmd("start_playback"))
    except Exception as e:
        return _err("starting playback", e)


@mcp.tool()
def stop_playback() -> str:
    """Stop playback."""
    try:
        return _ok(_cmd("stop_playback"))
    except Exception as e:
        return _err("stopping playback", e)


@mcp.tool()
def get_current_position() -> str:
    """Get the current playhead position (in beats), plus is_playing and tempo."""
    try:
        return _ok(_cmd("get_current_position"))
    except Exception as e:
        return _err("getting position", e)


@mcp.tool()
def set_current_position(position: float) -> str:
    """Move the playhead to a beat position (clamped to >= 0)."""
    try:
        return _ok(_cmd("set_current_position", {"position": position}))
    except Exception as e:
        return _err("setting position", e)


@mcp.tool()
def select_track(track_index: Union[int, str]) -> str:
    """Select a track (sets the LOM selected track). Accepts index or name."""
    try:
        return _ok(_cmd("select_track", {"track_index": _resolve_track(track_index)}))
    except Exception as e:
        return _err("selecting track", e)


@mcp.tool()
def select_clip(track_index: Union[int, str], clip_index: int) -> str:
    """Select an ARRANGEMENT clip as the detail clip (prep for a GUI split). Accepts track index or name."""
    try:
        return _ok(_cmd("select_clip", {"track_index": _resolve_track(track_index), "clip_index": clip_index}))
    except Exception as e:
        return _err("selecting clip", e)


# ===========================================================================
# TRACKS / ORGANIZATION
# ===========================================================================
@mcp.tool()
def create_midi_track(index: int = -1) -> str:
    """Create a new MIDI track at the given index (-1 appends at the end)."""
    try:
        return _ok(_cmd("create_midi_track", {"index": index}))
    except Exception as e:
        return _err("creating MIDI track", e)


@mcp.tool()
def create_audio_track(index: int = -1) -> str:
    """Create a new audio track at the given index (-1 appends at the end)."""
    try:
        return _ok(_cmd("create_audio_track", {"index": index}))
    except Exception as e:
        return _err("creating audio track", e)


@mcp.tool()
def create_return_track() -> str:
    """Create a new return track."""
    try:
        return _ok(_cmd("create_return_track"))
    except Exception as e:
        return _err("creating return track", e)


@mcp.tool()
def set_track_name(track_index: Union[int, str], name: str) -> str:
    """Rename a track. track_index accepts an index or the current name."""
    try:
        return _ok(_cmd("set_track_name", {"track_index": _resolve_track(track_index), "name": name}))
    except Exception as e:
        return _err("setting track name", e)


@mcp.tool()
def set_track_color(track_index: Union[int, str], color_index: int) -> str:
    """Set a track's color by Live color index. Accepts track index or name."""
    try:
        return _ok(_cmd("set_track_color", {"track_index": _resolve_track(track_index), "color_index": color_index}))
    except Exception as e:
        return _err("setting track color", e)


@mcp.tool()
def fold_track(track_index: Union[int, str], fold: bool = True) -> str:
    """Fold or unfold a GROUP track (errors if the track is not a group). Accepts index or name."""
    try:
        return _ok(_cmd("fold_track", {"track_index": _resolve_track(track_index), "fold": fold}))
    except Exception as e:
        return _err("folding track", e)


@mcp.tool()
def get_track_routing(track_index: Union[int, str]) -> str:
    """Get a track's input/output routing display names. Accepts index or name."""
    try:
        return _ok(_cmd("get_track_routing", {"track_index": _resolve_track(track_index)}))
    except Exception as e:
        return _err("getting track routing", e)


@mcp.tool()
def delete_track(track_index: Union[int, str]) -> str:
    """DESTRUCTIVE: delete a track. Accepts index or name. Cannot be undone via this tool (use automator_undo in Ableton)."""
    try:
        return _ok(_cmd("delete_track", {"track_index": _resolve_track(track_index)}))
    except Exception as e:
        return _err("deleting track", e)


# ===========================================================================
# MIXER
# ===========================================================================
@mcp.tool()
def set_track_volume(track_index: Union[int, str], volume: float) -> str:
    """Set a track's fader (0.0-1.0, where ~0.85 is 0 dB). Accepts index or name."""
    try:
        return _ok(_cmd("set_track_volume", {"track_index": _resolve_track(track_index), "volume": volume}))
    except Exception as e:
        return _err("setting track volume", e)


@mcp.tool()
def set_track_pan(track_index: Union[int, str], pan: float) -> str:
    """Set a track's pan (-1.0 left .. 1.0 right). Accepts index or name."""
    try:
        return _ok(_cmd("set_track_pan", {"track_index": _resolve_track(track_index), "pan": pan}))
    except Exception as e:
        return _err("setting track pan", e)


@mcp.tool()
def set_track_mute(track_index: Union[int, str], mute: bool = True) -> str:
    """Mute or unmute a track. Accepts index or name."""
    try:
        return _ok(_cmd("set_track_mute", {"track_index": _resolve_track(track_index), "mute": mute}))
    except Exception as e:
        return _err("setting track mute", e)


@mcp.tool()
def set_track_solo(track_index: Union[int, str], solo: bool = True) -> str:
    """Solo or unsolo a track. Accepts index or name."""
    try:
        return _ok(_cmd("set_track_solo", {"track_index": _resolve_track(track_index), "solo": solo}))
    except Exception as e:
        return _err("setting track solo", e)


@mcp.tool()
def set_send_level(track_index: Union[int, str], send_index: int, level: float) -> str:
    """Set a track's send level to a return (0.0-1.0). send_index is the return slot. Accepts track index or name."""
    try:
        return _ok(_cmd("set_send_level", {"track_index": _resolve_track(track_index), "send_index": send_index, "level": level}))
    except Exception as e:
        return _err("setting send level", e)


@mcp.tool()
def get_return_tracks() -> str:
    """List all return tracks with volume/pan/mute/solo and their devices."""
    try:
        return _ok(_cmd("get_return_tracks"))
    except Exception as e:
        return _err("getting return tracks", e)


@mcp.tool()
def set_return_track_volume(return_index: int, volume: float) -> str:
    """Set a return track's volume (0.0-1.0)."""
    try:
        return _ok(_cmd("set_return_track_volume", {"return_index": return_index, "volume": volume}))
    except Exception as e:
        return _err("setting return track volume", e)


# ===========================================================================
# MASTER TRACK
# ===========================================================================
@mcp.tool()
def get_master_track() -> str:
    """Get master track info: volume, pan, and device list."""
    try:
        return _ok(_cmd("get_master_track"))
    except Exception as e:
        return _err("getting master track", e)


@mcp.tool()
def set_master_volume(volume: float) -> str:
    """Set the master track volume (0.0-1.0)."""
    try:
        return _ok(_cmd("set_master_volume", {"volume": volume}))
    except Exception as e:
        return _err("setting master volume", e)


@mcp.tool()
def get_master_device_parameters(device_index: int = 0) -> str:
    """Get all parameters of a device on the master track."""
    try:
        return _ok(_cmd("get_master_device_parameters", {"device_index": device_index}))
    except Exception as e:
        return _err("getting master device parameters", e)


@mcp.tool()
def set_master_device_parameter(device_index: int, parameter_index: int, value: float) -> str:
    """Set a parameter (by index) of a device on the master track (value clamped to the param's min/max)."""
    try:
        return _ok(_cmd("set_master_device_parameter", {"device_index": device_index, "parameter_index": parameter_index, "value": value}))
    except Exception as e:
        return _err("setting master device parameter", e)


# ===========================================================================
# SESSION CLIPS & MIDI NOTES  (clip_index = SESSION slot)
# ===========================================================================
@mcp.tool()
def create_clip(track_index: Union[int, str], clip_index: int, length: float = 4.0) -> str:
    """SESSION VIEW ONLY: create an empty MIDI clip in a session clip SLOT (errors if occupied). length in beats.
    For building loops/songs in the timeline use create_arrangement_clip instead. Accepts track index or name."""
    try:
        return _ok(_cmd("create_clip", {"track_index": _resolve_track(track_index), "clip_index": clip_index, "length": length}))
    except Exception as e:
        return _err("creating clip", e)


@mcp.tool()
def add_notes_to_clip(track_index: Union[int, str], clip_index: int, notes: List[Dict[str, Any]]) -> str:
    """SESSION VIEW ONLY: add MIDI notes to a session-slot clip. For timeline/song building use add_notes_to_arrangement_clip instead.
    Each note: {pitch:int(0-127), start_time:float(beats), duration:float(beats), velocity:int(0-127), mute:bool}. Accepts track index or name."""
    try:
        ti = _resolve_track(track_index)
        out = _ok(_cmd("add_notes_to_clip", {"track_index": ti, "clip_index": clip_index, "notes": notes}))
        return out + _silence_suffix(ti)
    except Exception as e:
        return _err("adding notes to clip", e)


@mcp.tool()
def set_clip_name(track_index: Union[int, str], clip_index: int, name: str) -> str:
    """Rename a SESSION clip. Accepts track index or name."""
    try:
        return _ok(_cmd("set_clip_name", {"track_index": _resolve_track(track_index), "clip_index": clip_index, "name": name}))
    except Exception as e:
        return _err("setting clip name", e)


@mcp.tool()
def fire_clip(track_index: Union[int, str], clip_index: int) -> str:
    """Launch (fire) a SESSION clip slot. Accepts track index or name."""
    try:
        return _ok(_cmd("fire_clip", {"track_index": _resolve_track(track_index), "clip_index": clip_index}))
    except Exception as e:
        return _err("firing clip", e)


@mcp.tool()
def stop_clip(track_index: Union[int, str], clip_index: int) -> str:
    """Stop a SESSION clip slot. Accepts track index or name."""
    try:
        return _ok(_cmd("stop_clip", {"track_index": _resolve_track(track_index), "clip_index": clip_index}))
    except Exception as e:
        return _err("stopping clip", e)


# ===========================================================================
# ARRANGEMENT VIEW  (clip_index = ARRANGEMENT clip)
# ===========================================================================
@mcp.tool()
def get_arrangement_clips(track_index: Union[int, str]) -> str:
    """List all ARRANGEMENT clips on a track (index, name, start/end/length, playing, is_midi). Accepts track index or name."""
    try:
        return _ok(_cmd("get_arrangement_clips", {"track_index": _resolve_track(track_index)}))
    except Exception as e:
        return _err("getting arrangement clips", e)


@mcp.tool()
def get_arrangement_clip_notes(track_index: Union[int, str], clip_index: int) -> str:
    """Read MIDI notes from an ARRANGEMENT clip (must be a MIDI clip). Accepts track index or name."""
    try:
        return _ok(_cmd("get_arrangement_clip_notes", {"track_index": _resolve_track(track_index), "clip_index": clip_index}))
    except Exception as e:
        return _err("getting arrangement clip notes", e)


@mcp.tool()
def create_arrangement_clip(track_index: Union[int, str], start_time: float, length: float = 4.0) -> str:
    """DEFAULT for building loops/songs: create a MIDI clip in the ARRANGEMENT timeline at start_time (in BEATS; bar N of 4/4 = (N-1)*4).
    Live 12+, MIDI tracks only. Then call add_notes_to_arrangement_clip. Accepts track index or name."""
    try:
        return _ok(_cmd("create_arrangement_clip", {"track_index": _resolve_track(track_index), "start_time": start_time, "length": length}))
    except Exception as e:
        return _err("creating arrangement clip", e)


@mcp.tool()
def add_notes_to_arrangement_clip(track_index: Union[int, str], clip_index: int, notes: List[Dict[str, Any]]) -> str:
    """DEFAULT for song/loop building: add MIDI notes to an ARRANGEMENT clip (from create_arrangement_clip / get_arrangement_clips).
    Each note: {pitch:int(0-127), start_time:float(beats), duration:float(beats), velocity:int(0-127), mute:bool}. Accepts track index or name."""
    try:
        ti = _resolve_track(track_index)
        out = _ok(_cmd("add_notes_to_arrangement_clip", {"track_index": ti, "clip_index": clip_index, "notes": notes}))
        return out + _silence_suffix(ti)
    except Exception as e:
        return _err("adding notes to arrangement clip", e)


@mcp.tool()
def duplicate_clip_to_arrangement(track_index: Union[int, str], clip_index: int, position: float) -> str:
    """Copy a SESSION clip slot into the ARRANGEMENT at a beat position. Accepts track index or name."""
    try:
        return _ok(_cmd("duplicate_clip_to_arrangement", {"track_index": _resolve_track(track_index), "clip_index": clip_index, "position": position}))
    except Exception as e:
        return _err("duplicating clip to arrangement", e)


@mcp.tool()
def set_clip_mute(track_index: Union[int, str], clip_index: int, muted: bool = True) -> str:
    """Mute/unmute an ARRANGEMENT clip. Accepts track index or name."""
    try:
        return _ok(_cmd("set_clip_mute", {"track_index": _resolve_track(track_index), "clip_index": clip_index, "muted": muted}))
    except Exception as e:
        return _err("setting clip mute", e)


@mcp.tool()
def set_clip_color(track_index: Union[int, str], clip_index: int, color_index: int) -> str:
    """Set an ARRANGEMENT clip's color by Live color index. Accepts track index or name."""
    try:
        return _ok(_cmd("set_clip_color", {"track_index": _resolve_track(track_index), "clip_index": clip_index, "color_index": color_index}))
    except Exception as e:
        return _err("setting clip color", e)


@mcp.tool()
def set_clip_start_end(track_index: Union[int, str], clip_index: int,
                       start_marker: Optional[float] = None, end_marker: Optional[float] = None) -> str:
    """Set an ARRANGEMENT clip's start/end markers (pass None to leave one unchanged). Accepts track index or name."""
    try:
        params = {"track_index": _resolve_track(track_index), "clip_index": clip_index}
        if start_marker is not None:
            params["start_marker"] = start_marker
        if end_marker is not None:
            params["end_marker"] = end_marker
        return _ok(_cmd("set_clip_start_end", params))
    except Exception as e:
        return _err("setting clip start/end", e)


# ===========================================================================
# AUDIO CLIP PROPERTIES  (ARRANGEMENT audio clips)
# ===========================================================================
@mcp.tool()
def get_audio_clip_properties(track_index: Union[int, str], clip_index: int) -> str:
    """Get full state of an ARRANGEMENT AUDIO clip (gain, pitch, warp, loop, markers, file path). Accepts track index or name."""
    try:
        return _ok(_cmd("get_audio_clip_properties", {"track_index": _resolve_track(track_index), "clip_index": clip_index}))
    except Exception as e:
        return _err("getting audio clip properties", e)


@mcp.tool()
def get_clip_warp_markers(track_index: Union[int, str], clip_index: int) -> str:
    """Read the warp markers of an ARRANGEMENT audio clip. Accepts track index or name."""
    try:
        return _ok(_cmd("get_clip_warp_markers", {"track_index": _resolve_track(track_index), "clip_index": clip_index}))
    except Exception as e:
        return _err("getting warp markers", e)


@mcp.tool()
def set_clip_gain(track_index: Union[int, str], clip_index: int, gain: float = 1.0) -> str:
    """Set an ARRANGEMENT audio clip's gain (0.0-1.0). Accepts track index or name."""
    try:
        return _ok(_cmd("set_clip_gain", {"track_index": _resolve_track(track_index), "clip_index": clip_index, "gain": gain}))
    except Exception as e:
        return _err("setting clip gain", e)


@mcp.tool()
def set_clip_pitch(track_index: Union[int, str], clip_index: int, semitones: int = 0, cents: int = 0) -> str:
    """Transpose an ARRANGEMENT audio clip (semitones -48..48, cents -50..49). Accepts track index or name."""
    try:
        return _ok(_cmd("set_clip_pitch", {"track_index": _resolve_track(track_index), "clip_index": clip_index, "semitones": semitones, "cents": cents}))
    except Exception as e:
        return _err("setting clip pitch", e)


@mcp.tool()
def set_clip_loop(track_index: Union[int, str], clip_index: int,
                  loop_start: Optional[float] = None, loop_end: Optional[float] = None,
                  looping: Optional[bool] = None) -> str:
    """Set an ARRANGEMENT audio clip's loop region and/or toggle looping (pass None to leave unchanged). Accepts track index or name."""
    try:
        params = {"track_index": _resolve_track(track_index), "clip_index": clip_index}
        if loop_start is not None:
            params["loop_start"] = loop_start
        if loop_end is not None:
            params["loop_end"] = loop_end
        if looping is not None:
            params["looping"] = looping
        return _ok(_cmd("set_clip_loop", params))
    except Exception as e:
        return _err("setting clip loop", e)


@mcp.tool()
def set_clip_warp_mode(track_index: Union[int, str], clip_index: int, warp_mode: int = 0) -> str:
    """Set an ARRANGEMENT audio clip's warp mode: 0=Beats,1=Tones,2=Texture,3=Re-Pitch,4=Complex,5=Complex Pro. Accepts track index or name."""
    try:
        return _ok(_cmd("set_clip_warp_mode", {"track_index": _resolve_track(track_index), "clip_index": clip_index, "warp_mode": warp_mode}))
    except Exception as e:
        return _err("setting warp mode", e)


# ===========================================================================
# DEVICES & PLUGIN PARAMETERS
# ===========================================================================
@mcp.tool()
def get_device_parameters(track_index: Union[int, str], device_index: int = 0) -> str:
    """Enumerate all parameters of a device on a track (name, value, min, max, quantized). Accepts track index or name."""
    try:
        return _ok(_cmd("get_device_parameters", {"track_index": _resolve_track(track_index), "device_index": device_index}))
    except Exception as e:
        return _err("getting device parameters", e)


@mcp.tool()
def set_device_parameter(track_index: Union[int, str], device_index: int, parameter_index: int, value: float) -> str:
    """Set a device parameter by index (value clamped to the param's min/max). Accepts track index or name."""
    try:
        return _ok(_cmd("set_device_parameter", {"track_index": _resolve_track(track_index), "device_index": device_index, "parameter_index": parameter_index, "value": value}))
    except Exception as e:
        return _err("setting device parameter", e)


@mcp.tool()
def set_device_parameter_by_name(track_index: Union[int, str], device_index: int, param_name: str, value: float) -> str:
    """Set a device parameter by name (exact match, then case-insensitive partial). Accepts track index or name."""
    try:
        return _ok(_cmd("set_device_parameter_by_name", {"track_index": _resolve_track(track_index), "device_index": device_index, "param_name": param_name, "value": value}))
    except Exception as e:
        return _err("setting device parameter by name", e)


@mcp.tool()
def set_device_enabled(track_index: Union[int, str], device_index: int, enabled: bool = True) -> str:
    """Toggle a device's on/off state. Accepts track index or name."""
    try:
        return _ok(_cmd("set_device_enabled", {"track_index": _resolve_track(track_index), "device_index": device_index, "enabled": enabled}))
    except Exception as e:
        return _err("setting device enabled", e)


@mcp.tool()
def delete_device(track_index: Union[int, str], device_index: int) -> str:
    """DESTRUCTIVE: delete a device from a track. Accepts track index or name."""
    try:
        return _ok(_cmd("delete_device", {"track_index": _resolve_track(track_index), "device_index": device_index}))
    except Exception as e:
        return _err("deleting device", e)


# ===========================================================================
# BROWSER / DEVICE LOADING
# ===========================================================================
@mcp.tool()
def get_browser_tree(category_type: str = "all") -> str:
    """List top-level browser categories only (shallow, fast). category_type: all|instruments|sounds|drums|audio_effects|midi_effects.
    Then drill in with get_browser_items_at_path - do NOT follow this with a deep get_all_presets scan."""
    try:
        return _ok(_cmd("get_browser_tree", {"category_type": category_type}))
    except Exception as e:
        return _err("getting browser tree", e)


@mcp.tool()
def get_browser_items_at_path(path: str) -> str:
    """PREFERRED browser tool: list ONE folder's items (name, is_folder, is_loadable, uri) by path, e.g. "Instruments/Wavetable".
    Fast and focused - use this to find a device/preset rather than scanning everything, then load_browser_item with the uri."""
    try:
        return _ok(_cmd("get_browser_items_at_path", {"path": path}))
    except Exception as e:
        return _err("getting browser items", e)


# Cap on how many presets we return, to keep responses fast and small even if a
# broad category is requested. The model is steered to narrow queries anyway.
_PRESET_CAP = 60


@mcp.tool()
def get_all_presets(category_type: str = "audio_effects", max_depth: int = 2) -> str:
    """SLOW - use only as a last resort on a NARROW category with small max_depth (1-2). Recursively lists loadable presets.
    Prefer get_browser_items_at_path for a specific folder. Results are capped at 60; narrow the category if truncated.
    category_type: instruments|sounds|drums|audio_effects|midi_effects."""
    try:
        result = _cmd("get_all_presets", {"category_type": category_type, "max_depth": max_depth})
        presets = result.get("presets") if isinstance(result, dict) else None
        if isinstance(presets, list) and len(presets) > _PRESET_CAP:
            total = len(presets)
            result["presets"] = presets[:_PRESET_CAP]
            result["truncated"] = True
            result["truncated_note"] = (
                f"Showing {_PRESET_CAP} of {total} presets. Narrow the search with "
                f"get_browser_items_at_path on a specific sub-folder instead of scanning the whole category."
            )
        return _ok(result)
    except Exception as e:
        return _err("getting presets", e)


@mcp.tool()
def load_browser_item(track_index: Union[int, str], item_uri: str) -> str:
    """Load a browser item (device or preset) onto a track by its URI (get the URI from get_browser_items_at_path / get_all_presets). Accepts track index or name."""
    try:
        return _ok(_cmd("load_browser_item", {"track_index": _resolve_track(track_index), "item_uri": item_uri}))
    except Exception as e:
        return _err("loading browser item", e)


# --- instrument loading (knowledge-base driven) ----------------------------
_DRUM_WORDS = ("drum", "kit", "808", "909", "707", "606", "505", "boom", "bap",
               "beat", "perc", "hat", "kick", "snare", "trap", "hip")


def _kit_pick(prefer: List[str], avoid: List[str]) -> Optional[Dict[str, Any]]:
    """Choose a loadable drum KIT from the Drums folder (never the empty Drum Rack)."""
    items = _cmd("get_browser_items_at_path", {"path": "Drums"}).get("items", [])
    kits = [it for it in items if it.get("is_loadable") and it.get("name", "").strip().lower() != "drum rack"]
    pool = [it for it in kits if not any(a in it.get("name", "").lower() for a in (avoid or []))] or kits
    for kw in (prefer or []):
        m = [it for it in pool if kw in it.get("name", "").lower()]
        if m:
            return m[0]
    return next((it for it in pool if it.get("name", "").endswith(".adg")), None) or (pool[0] if pool else None)


def _device_pick(device: str) -> Optional[Dict[str, Any]]:
    """Load a preset from Instruments/<device> if possible (in-character), else the device default."""
    try:
        sub = _cmd("get_browser_items_at_path", {"path": f"Instruments/{device}"}).get("items", [])
        preset = next((it for it in sub if it.get("is_loadable")
                       and it.get("name", "").lower().endswith((".adv", ".adg", ".fxp"))), None)
        if preset:
            return preset
    except Exception:
        pass
    top = _cmd("get_browser_items_at_path", {"path": "Instruments"}).get("items", [])
    exact = next((it for it in top if it.get("is_loadable") and it.get("name", "").lower() == device.lower()), None)
    if exact:
        return exact
    return next((it for it in top if it.get("is_loadable") and device.lower() in it.get("name", "").lower()), None)


def _resolve_instrument_target(role: str, genre: str, hint: str):
    """Decide what to load. Returns ('kit', prefer, avoid) or ('instrument', device_name)."""
    hint = (hint or "").strip().lower()
    role = (role or "").lower()
    # explicit device named in the hint wins (e.g. "load Operator" / "rhodes")
    if K is not None:
        for name in K.INSTRUMENTS:
            if name.lower() in hint:
                return ("instrument", name)
    if "rhodes" in hint or "wurli" in hint or "e-piano" in hint or "epiano" in hint:
        return ("instrument", "Electric")
    is_drums = role == "drums" or any(w in hint for w in _DRUM_WORDS)
    if K is not None:
        h = K.instrument_load_hint("drums" if is_drums else (role or "keys"), genre or "boom bap")
        if h["kind"] == "kit":
            # honor a specific token in the hint (e.g. "808") by prepending it
            prefer = ([t for t in hint.split() if t] + h["prefer"]) if hint else h["prefer"]
            return ("kit", prefer, h["avoid"])
        return ("instrument", h["device"])
    # KB missing -> minimal fallback
    if is_drums:
        return ("kit", [t for t in hint.split()], ["drum rack"])
    return ("instrument", hint.title() if hint else "Operator")


def _ensure_instrument(ti: int, role: str = "", genre: str = "", hint: str = "") -> Dict[str, Any]:
    """Load a genre/role-appropriate instrument onto track ti. Returns {loaded, role, uri}."""
    target = _resolve_instrument_target(role, genre, hint)
    if target[0] == "kit":
        pick = _kit_pick(target[1], target[2])
        label = "drum kit"
    else:
        pick = _device_pick(target[1])
        label = target[1]
    if not pick:
        return {"loaded": None, "error": f"no loadable {label} found in browser"}
    _cmd("load_browser_item", {"track_index": ti, "item_uri": pick["uri"]})
    return {"loaded": pick.get("name"), "as": label, "uri": pick.get("uri")}


@mcp.tool()
def load_instrument(track_index: Union[int, str], instrument: str = "",
                    role: str = "", genre: str = "") -> str:
    """Load a genre-appropriate, sound-producing instrument onto a MIDI track so it isn't silent.
    Picks the RIGHT Ableton instrument for the style (e.g. boom bap keys -> Electric/Rhodes, drums -> a dusty
    KIT with samples, not an empty Drum Rack). Pass any of: instrument (a hint like 'rhodes', 'operator',
    'drum kit', '808'), role ('drums'|'bass'|'keys'|'chords'|'melody'|'lead'|'pad'), and genre
    ('boom bap','lofi','trap','house','techno','dnb','rnb','ambient','pop'). Accepts track index or name."""
    try:
        ti = _resolve_track(track_index)
        if not instrument and not role:
            # infer from the track name when nothing specified
            tname = str(_cmd("get_track_info", {"track_index": ti}).get("name", "")).lower()
            if any(w in tname for w in ("drum", "beat", "perc", "kit")):
                role = "drums"
        res = _ensure_instrument(ti, role=role, genre=genre, hint=instrument)
        if res.get("loaded") is None:
            return f"Error loading instrument: {res.get('error')}"
        res["track_index"] = ti
        res["note"] = "Instrument loaded. Add notes, then confirm with get_playability_report."
        return _ok(res)
    except Exception as e:
        return _err("loading instrument", e)


@mcp.tool()
def get_playability_report(track_index: Optional[Union[int, str]] = None) -> str:
    """COMPLETION CHECK - call this after building a beat/loop to confirm it will actually PLAY.
    Reports, per track: instrument loaded?, clip counts, ready_to_play, and warnings (e.g. SILENT = no
    instrument). Pass a track to check one, or omit to check all. If tracks_with_issues > 0, fix them
    (usually load_instrument) before telling the user it's done."""
    try:
        if track_index is not None and track_index != "":
            recs = [_analyze_track(_cmd("get_track_info", {"track_index": _resolve_track(track_index)}))]
        else:
            count = int(_cmd("get_session_info").get("track_count", 0))
            recs = [_analyze_track(_cmd("get_track_info", {"track_index": i})) for i in range(count)]
        problems = [r for r in recs if r["warnings"]]
        report = {
            "all_ready": bool(recs) and all(r["ready_to_play"] for r in recs),
            "tracks_checked": len(recs),
            "tracks_with_issues": len(problems),
            "action_needed": [f"Track {r['index']} '{r['name']}': {'; '.join(r['warnings'])}" for r in problems],
            "tracks": recs,
        }
        return _ok(report)
    except Exception as e:
        return _err("building playability report", e)


# ===========================================================================
# WORKFLOW / CLUSTER TOOLS — the producer-story layer (start here). Each maps
# a real production workflow to one call: pick the right instrument for the
# genre, build in the arrangement, and self-verify. Built on the primitives.
# ===========================================================================
def _genre_title(genre: str) -> str:
    return K.resolve_genre(genre).replace("_", " ").title() if K else str(genre).title()


def _new_track_index() -> int:
    """Create a MIDI track and return its index (appended at the end)."""
    _cmd("create_midi_track", {"index": -1})
    _track_cache["t"] = 0.0  # invalidate name cache
    return int(_cmd("get_session_info").get("track_count", 1)) - 1


def _arr_clip_index_near(track_index: int, start_beat: float) -> int:
    clips = _cmd("get_arrangement_clips", {"track_index": track_index}).get("clips", [])
    if not clips:
        return 0
    return min(clips, key=lambda c: abs(c.get("start_time", 0) - start_beat)).get("index", clips[-1]["index"])


def _do_add_part(role: str, genre: str, bars: int, start_bar: int, track,
                 notes: Optional[List[Dict[str, Any]]], set_bpm: bool) -> Dict[str, Any]:
    """Cluster: (track) -> genre-appropriate instrument -> EMPTY arrangement clip.
    Writes notes only if the caller (the model) supplies them — this module does NOT
    generate MIDI; the model composes it from the style guide."""
    if K is None:
        raise Exception(f"knowledge base unavailable: {_KB_ERR}")
    prof = K.genre_profile(genre)
    if set_bpm:
        _cmd("set_tempo", {"tempo": prof.get("bpm", 120)})
    if track is None or track == "":
        ti = _new_track_index()
        _cmd("set_track_name", {"track_index": ti, "name": f"{_genre_title(genre)} {role.title()}"})
    else:
        ti = _resolve_track(track)
    ins = _ensure_instrument(ti, role=role, genre=genre)
    start_beat = start_bar * 4.0
    _cmd("create_arrangement_clip", {"track_index": ti, "start_time": start_beat, "length": bars * 4.0})
    cidx = _arr_clip_index_near(ti, start_beat)
    written = 0
    if notes:
        _cmd("add_notes_to_arrangement_clip", {"track_index": ti, "clip_index": cidx, "notes": notes})
        written = len(notes)
    rec = _analyze_track(_cmd("get_track_info", {"track_index": ti}))
    return {"role": role, "track": ti, "track_name": rec.get("name"),
            "instrument": ins.get("loaded"), "clip_index": cidx,
            "notes_written": written, "has_instrument": rec.get("has_instrument")}


@mcp.tool()
def production_guide(genre: str = "") -> str:
    """START HERE for any creative request ("make a beat", "write a loop"). Returns the recipe for a genre
    (tempo, key, feel, instrument palette, song structure) AND the exact next tool calls to make. Call with no
    genre to list supported genres. Supported: boom bap, lofi, trap, house, techno, dnb, rnb, ambient, pop."""
    if K is None:
        return f"Error: knowledge base unavailable: {_KB_ERR}"
    try:
        if not genre:
            return _ok({
                "genres": [{"name": k.replace("_", " "), "bpm": v["bpm"], "vibe": v.get("tips", "")}
                           for k, v in K.GENRES.items()],
                "roles": K.ROLES,
                "fastest_path": "1) style_guide(genre) for how the genre is actually played. "
                                "2) scaffold_song(genre, bars, parts) creates tracks + the RIGHT instruments + "
                                "empty arrangement clips in one call. 3) YOU compose genre-correct MIDI for each "
                                "clip and write it with add_notes_to_arrangement_clip. 4) balance_mix() + "
                                "get_playability_report(). suggest_instruments(role, genre) shows sound options.",
            })
        prof = K.genre_profile(genre)
        gkey = prof["_key"]
        sg = K.style_guide(genre)
        return _ok({
            "genre": gkey.replace("_", " "), "bpm": prof["bpm"], "bpm_range": prof.get("bpm_range"),
            "key": prof["key"], "feel": sg.get("feel"), "swing": prof.get("swing"),
            "instrument_palette": prof.get("palette"), "song_structure": prof.get("structure"),
            "reference_artists": sg.get("reference_artists"),
            "next_steps": [
                f"style_guide('{gkey}')  # full how-to-play reference before you compose",
                f"scaffold_song(genre='{gkey}', bars=16, parts=['drums','bass','chords','melody'])  # tracks+instruments+empty clips",
                "compose MIDI for each clip yourself and write it with add_notes_to_arrangement_clip(track, clip_index, notes)",
                "then balance_mix(), then get_playability_report() to confirm it plays",
            ],
        })
    except Exception as e:
        return _err("building production guide", e)


@mcp.tool()
def style_guide(genre: str, role: str = "") -> str:
    """The genre STYLE reference for COMPOSING (you write the MIDI, this returns knowledge not notes). Returns
    feel/groove, the drum-map + where each hit goes, harmony (scale + suggested progression), bass & melody
    approach, arrangement, REFERENCE ARTISTS, and what to avoid. Pass role to focus (drums|bass|chords|keys|
    melody|lead|pad). genre: boom bap|lofi|trap|house|techno|dnb|rnb|ambient|pop. Read this before composing."""
    if K is None:
        return f"Error: knowledge base unavailable: {_KB_ERR}"
    try:
        return _ok(K.style_guide(genre, role))
    except Exception as e:
        return _err("building style guide", e)


@mcp.tool()
def suggest_instruments(role: str, genre: str = "") -> str:
    """Show the best Ableton 12 instruments for a role in a genre (why boom bap keys = Electric/Rhodes, not Wavetable).
    role: drums|bass|keys|chords|melody|lead|pad. The top pick is what add_part/setup_track will load."""
    if K is None:
        return f"Error: knowledge base unavailable: {_KB_ERR}"
    try:
        return _ok({
            "role": role, "genre": K.resolve_genre(genre),
            "recommended": K.suggest_instruments(role, genre),
            "override": "To force one: load_instrument(track, instrument='<name>').",
        })
    except Exception as e:
        return _err("suggesting instruments", e)


@mcp.tool()
def setup_track(role: str, genre: str = "boom bap", name: str = "") -> str:
    """Cluster: create a MIDI track, name it, and load the genre-appropriate instrument (no notes yet).
    role: drums|bass|keys|chords|melody|lead|pad. Use when you want an instrument-ready track to build on."""
    if K is None:
        return f"Error: knowledge base unavailable: {_KB_ERR}"
    try:
        ti = _new_track_index()
        _cmd("set_track_name", {"track_index": ti, "name": name or f"{_genre_title(genre)} {role.title()}"})
        ins = _ensure_instrument(ti, role=role, genre=genre)
        rec = _analyze_track(_cmd("get_track_info", {"track_index": ti}))
        return _ok({"track": ti, "name": rec.get("name"), "role": role,
                    "instrument": ins.get("loaded"), "has_instrument": rec.get("has_instrument"),
                    "note": "Ready for notes. Use add_part(role, genre, track=%d) or add_notes_to_arrangement_clip." % ti})
    except Exception as e:
        return _err("setting up track", e)


@mcp.tool()
def add_part(role: str, genre: str = "boom bap", bars: int = 8, start_bar: int = 0,
             track: Union[int, str, None] = None, notes: List[Dict[str, Any]] = None) -> str:
    """Scaffold ONE part: make/target a track, load the genre-appropriate instrument, and create an EMPTY
    ARRANGEMENT clip ready for MIDI. role: drums|bass|chords|keys|melody|lead|pad.
    - If you pass `notes` (YOUR composed MIDI, [{pitch,start_time,duration,velocity}] in beats), they're written
      and the track is verified.
    - If you OMIT notes, it returns the clip reference + the STYLE guide for this role so you compose the MIDI,
      then call add_notes_to_arrangement_clip(track, clip_index, notes).
    Adding 'drums' also sets the genre tempo. start_bar places the clip later in the timeline."""
    if K is None:
        return f"Error: knowledge base unavailable: {_KB_ERR}"
    try:
        res = _do_add_part(role, genre, bars, start_bar, track, notes, set_bpm=(role.lower() == "drums"))
        if not res["notes_written"]:
            res["style"] = K.style_guide(genre, role)
            res["next"] = (f"Compose {role} MIDI following 'style', then "
                           f"add_notes_to_arrangement_clip(track={res['track']}, clip_index={res['clip_index']}, notes=[...]).")
        return _ok(res)
    except Exception as e:
        return _err("adding part", e)


@mcp.tool()
def scaffold_song(genre: str = "boom bap", bars: int = 16, parts: List[str] = None) -> str:
    """Fast path from a prompt to a ready-to-compose session: sets the genre tempo, then for EACH part creates a
    track, loads the RIGHT instrument for the style, and makes an EMPTY arrangement clip. Returns the STYLE guide
    plus a map of {role, track, clip_index} for every part. YOU then compose genre-correct MIDI for each clip and
    write it with add_notes_to_arrangement_clip(track, clip_index, notes). parts defaults to
    ['drums','bass','chords','melody']. genre: boom bap|lofi|trap|house|techno|dnb|rnb|ambient|pop.
    This module does NOT generate notes — you compose them from the style guide (you're the better composer)."""
    if K is None:
        return f"Error: knowledge base unavailable: {_KB_ERR}"
    try:
        prof = K.genre_profile(genre)
        parts = parts or ["drums", "bass", "chords", "melody"]
        _cmd("set_tempo", {"tempo": prof.get("bpm", 120)})
        slots = [_do_add_part(r, genre, bars, 0, None, None, set_bpm=False) for r in parts]
        return _ok({
            "genre": prof["_key"].replace("_", " "), "key": prof.get("key"), "tempo": prof.get("bpm"),
            "bars": bars,
            "tracks": [{"role": s["role"], "track": s["track"], "clip_index": s["clip_index"],
                        "instrument": s["instrument"]} for s in slots],
            "style": K.style_guide(genre),
            "next": ("For EACH track above, compose genre-correct MIDI following 'style' and write it with "
                     "add_notes_to_arrangement_clip(track, clip_index, notes). Times in beats (1 bar = 4). "
                     "Then balance_mix() and get_playability_report()."),
        })
    except Exception as e:
        return _err("scaffolding song", e)


# rough per-role mix targets: (volume 0-1, pan -1..1)
_ROLE_MIX = [
    ("kick", (0.86, 0.0)), ("drum", (0.85, 0.0)), ("beat", (0.85, 0.0)), ("perc", (0.7, 0.15)),
    ("bass", (0.82, 0.0)), ("808", (0.84, 0.0)),
    ("chord", (0.66, -0.18)), ("key", (0.68, -0.18)), ("rhodes", (0.68, -0.18)),
    ("pad", (0.58, 0.22)), ("lead", (0.72, 0.2)), ("melody", (0.72, 0.2)), ("pluck", (0.7, 0.18)),
]


@mcp.tool()
def balance_mix() -> str:
    """Cluster: rough out a mix — set sensible per-role volume and pan across all tracks (drums/bass centered and
    loud, keys/chords tucked and slightly left, melody/lead forward and slightly right, pads back). A starting balance,
    not a master mix."""
    try:
        count = int(_cmd("get_session_info").get("track_count", 0))
        applied = []
        for i in range(count):
            nm = str(_cmd("get_track_info", {"track_index": i}).get("name", "")).lower()
            vol, pan = 0.75, 0.0
            for kw, (v, p) in _ROLE_MIX:
                if kw in nm:
                    vol, pan = v, p
                    break
            _cmd("set_track_volume", {"track_index": i, "volume": vol})
            if abs(pan) > 0.001:
                _cmd("set_track_pan", {"track_index": i, "pan": pan})
            applied.append({"track": i, "name": nm, "volume": vol, "pan": pan})
        return _ok({"balanced": applied, "note": "Rough balance applied. Tweak individual tracks as needed."})
    except Exception as e:
        return _err("balancing mix", e)


# ===========================================================================
# PROGRESSIVE DISCLOSURE — browse_tools() reveals the low-level primitives by
# category so the model (and Haiku) can find fine-control tools without holding
# all 80 in mind. Pattern ported from unified_mcp_bridge TOOL_CATALOG/list_tools.
# ===========================================================================
TOOL_CATALOG: Dict[str, Dict[str, Any]] = {
    "workflow": {"description": "High-level producer actions (START HERE)",
                 "tools": {"production_guide": "genre recipe + next steps",
                           "style_guide": "how to PLAY a genre (you compose the MIDI)",
                           "scaffold_song": "tracks+instruments+empty clips for a section",
                           "add_part": "scaffold one part (+optional your notes)",
                           "setup_track": "track + instrument, no notes",
                           "suggest_instruments": "best instrument per role+genre",
                           "load_instrument": "load a specific/role instrument",
                           "balance_mix": "rough per-role levels & pan"}},
    "session": {"description": "Read session/track state",
                "tools": {"get_session_info": "tempo/tracks/playhead",
                          "get_session_summary": "compact per-track summary",
                          "get_all_tracks": "index+name of every track",
                          "get_track_info": "one track's full state",
                          "get_playability_report": "will it actually play? (completion check)"}},
    "transport": {"description": "Playback & playhead",
                  "tools": {"set_tempo": "BPM", "start_playback": "play", "stop_playback": "stop",
                            "get_current_position": "playhead", "set_current_position": "move playhead",
                            "select_track": "select", "select_clip": "select arrangement clip"}},
    "track": {"description": "Create/organize tracks (accepts name or index)",
              "tools": {"create_midi_track": "new MIDI track", "create_audio_track": "new audio track",
                        "create_return_track": "new return", "set_track_name": "rename",
                        "set_track_color": "color", "fold_track": "fold group",
                        "get_track_routing": "in/out routing", "delete_track": "DELETE"}},
    "mixer": {"description": "Mixer (volume/pan/mute/solo/sends)",
              "tools": {"set_track_volume": "0-1", "set_track_pan": "-1..1", "set_track_mute": "bool",
                        "set_track_solo": "bool", "set_send_level": "to a return",
                        "get_return_tracks": "list returns", "set_return_track_volume": "return vol"}},
    "master": {"description": "Master track",
               "tools": {"set_master_volume": "0-1", "get_master_track": "info",
                         "get_master_device_parameters": "params", "set_master_device_parameter": "set param"}},
    "arrangement": {"description": "Timeline clips (DEFAULT for songs). clip_index = arrangement clip",
                    "tools": {"create_arrangement_clip": "MIDI clip at beat",
                              "add_notes_to_arrangement_clip": "add notes",
                              "get_arrangement_clips": "list", "get_arrangement_clip_notes": "read notes",
                              "duplicate_clip_to_arrangement": "copy session clip in",
                              "set_clip_mute": "mute", "set_clip_color": "color",
                              "set_clip_start_end": "trim"}},
    "session_clips": {"description": "Session-view slots (only if user asks). clip_index = slot",
                      "tools": {"add_notes_to_clip": "add notes", "set_clip_name": "rename",
                                "fire_clip": "launch", "stop_clip": "stop"}},
    "audio_clip": {"description": "Audio clip properties (arrangement audio clips)",
                   "tools": {"set_clip_gain": "0-1", "set_clip_pitch": "semitones/cents",
                             "set_clip_loop": "loop region", "set_clip_warp_mode": "0-5",
                             "get_clip_warp_markers": "read"}},
    "device": {"description": "Devices & plugin parameters (accepts name or index)",
               "tools": {"get_device_parameters": "list params",
                         "set_device_parameter": "by index", "set_device_parameter_by_name": "by name (fuzzy)",
                         "set_device_enabled": "on/off", "delete_device": "DELETE"}},
    "browser": {"description": "Browse/load devices & presets (search sparingly)",
                "tools": {"get_browser_items_at_path": "list one folder", "get_all_presets": "narrow scan",
                          "load_browser_item": "load by URI"}},
    "automator": {"description": "GUI automation (macOS Accessibility): split/group/freeze/undo etc.",
                  "tools": {"automator_split": "Cmd+E", "automator_consolidate": "Cmd+J",
                            "automator_group": "group sel", "automator_ungroup": "ungroup",
                            "smart_select_tracks": "select many", "smart_group_tracks": "select+group",
                            "automator_undo": "undo", "automator_freeze": "freeze",
                            "automator_flatten": "flatten", "automator_reverse": "reverse",
                            "(more)": "automator_redo/save/export/quantize/duplicate/move_track_up|down/keystroke, calibrate_layout, get_layout_config"}},
}


@mcp.tool()
def browse_tools(category: str = "", detail: str = "name") -> str:
    """Discover the low-level tools by category (progressive disclosure). Call with no args for the category list;
    pass a category to see its tools; detail='description' or 'full' for more. Categories: workflow, session,
    transport, track, mixer, master, arrangement, session_clips, audio_clip, device, browser, automator."""
    try:
        if not category:
            return _ok({"categories": {c: TOOL_CATALOG[c]["description"] for c in TOOL_CATALOG},
                        "hint": "browse_tools('<category>') for its tools. For creative work, start with 'workflow'."})
        cat = TOOL_CATALOG.get(category)
        if not cat:
            return _ok({"error": f"unknown category '{category}'", "categories": list(TOOL_CATALOG.keys())})
        if detail == "name":
            return _ok({category: list(cat["tools"].keys())})
        return _ok({category: cat})
    except Exception as e:
        return _err("browsing tools", e)


# ===========================================================================
# GUI AUTOMATION (automator) — AppleScript, in-process. macOS + Accessibility.
# ===========================================================================
@mcp.tool()
def automator_split() -> str:
    """GUI: split the selected clip at the playhead (Cmd+E). Select the clip first (see select_clip)."""
    return _automator("automator_split")


@mcp.tool()
def automator_consolidate() -> str:
    """GUI: consolidate the current selection into one clip (Cmd+J)."""
    return _automator("automator_consolidate")


@mcp.tool()
def automator_duplicate() -> str:
    """GUI: duplicate the current selection (Cmd+D)."""
    return _automator("automator_duplicate")


@mcp.tool()
def automator_undo() -> str:
    """GUI: undo the last action (Cmd+Z)."""
    return _automator("automator_undo")


@mcp.tool()
def automator_redo() -> str:
    """GUI: redo (Cmd+Shift+Z)."""
    return _automator("automator_redo")


@mcp.tool()
def automator_quantize() -> str:
    """GUI: quantize the current selection (Cmd+U)."""
    return _automator("automator_quantize")


@mcp.tool()
def automator_save() -> str:
    """GUI: save the Live set (Cmd+S)."""
    return _automator("automator_save")


@mcp.tool()
def automator_export() -> str:
    """GUI: open the Export Audio/Video dialog (Cmd+Shift+R). Opens a dialog for the user to complete."""
    return _automator("automator_export")


@mcp.tool()
def automator_freeze() -> str:
    """GUI: freeze the selected track (Edit > Freeze Track)."""
    return _automator("automator_freeze")


@mcp.tool()
def automator_flatten() -> str:
    """GUI: flatten the selected track (Edit > Flatten)."""
    return _automator("automator_flatten")


@mcp.tool()
def automator_reverse() -> str:
    """GUI: reverse the selected audio clip (Edit > Reverse)."""
    return _automator("automator_reverse")


@mcp.tool()
def automator_group() -> str:
    """GUI: group the currently selected tracks (Cmd+G)."""
    return _automator("automator_group")


@mcp.tool()
def automator_ungroup() -> str:
    """GUI: ungroup the selected group track (Cmd+Shift+G)."""
    return _automator("automator_ungroup")


@mcp.tool()
def automator_move_track_up() -> str:
    """GUI: move the selected track up (Cmd+Up)."""
    return _automator("automator_move_track_up")


@mcp.tool()
def automator_move_track_down() -> str:
    """GUI: move the selected track down (Cmd+Down)."""
    return _automator("automator_move_track_down")


@mcp.tool()
def automator_keystroke(key: str, modifiers: List[str] = None) -> str:
    """GUI: send an arbitrary keystroke to Ableton. key e.g. 'e'; modifiers e.g. ['command','shift']."""
    return _automator("automator_keystroke", {"key": key, "modifiers": modifiers or []})


@mcp.tool()
def smart_select_tracks(tracks: List[Union[int, str]]) -> str:
    """GUI: select multiple tracks by click automation (first normal, rest Shift+click). Accepts a list of indices or names. If clicks miss, use calibrate_layout."""
    try:
        return _automator("smart_select_tracks", {"tracks": _resolve_tracks(tracks)})
    except Exception as e:
        return _err("smart-selecting tracks", e)


@mcp.tool()
def smart_group_tracks(tracks: List[Union[int, str]]) -> str:
    """GUI: smart-select the given tracks then group them (Cmd+G). Accepts a list of indices or names."""
    try:
        return _automator("smart_group_tracks", {"tracks": _resolve_tracks(tracks)})
    except Exception as e:
        return _err("smart-grouping tracks", e)


@mcp.tool()
def calibrate_layout(track_height: Optional[int] = None, top_offset: Optional[int] = None,
                     header_x_offset: Optional[int] = None, session_track_width: Optional[int] = None,
                     session_header_y: Optional[int] = None) -> str:
    """GUI: tune the click coordinates used by smart_select/group if clicks land in the wrong place. Only pass the values you want to change."""
    params = {k: v for k, v in {
        "track_height": track_height, "top_offset": top_offset,
        "header_x_offset": header_x_offset, "session_track_width": session_track_width,
        "session_header_y": session_header_y,
    }.items() if v is not None}
    return _automator("calibrate_layout", params)


@mcp.tool()
def get_layout_config() -> str:
    """GUI: read the current click-layout config used for smart selection/grouping."""
    return _automator("get_layout_config")


# ===========================================================================
# SANDBOX — headless compose→render→listen→critique loop (sandbox/ package).
# Guarded like the knowledge module: sandbox unavailable ≠ server down.
# ===========================================================================
try:
    from sandbox_tools import register_sandbox_tools
    register_sandbox_tools(mcp, {"ok": _ok, "err": _err, "do_add_part": _do_add_part})
    logger.info("Sandbox tools registered (headless compose/listen loop available)")
except Exception as e:  # pragma: no cover - defensive
    logger.warning(f"Sandbox tools unavailable: {e}")

try:
    from live_ears import register_live_ear_tools
    register_live_ear_tools(mcp, {"ok": _ok, "err": _err})
    logger.info("Live-ears tools registered (real-session listening)")
except Exception as e:  # pragma: no cover - defensive
    logger.warning(f"Live-ears tools unavailable: {e}")


def main():
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
