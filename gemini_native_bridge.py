#!/usr/bin/env python3
"""
Gemini Native Function Calling Bridge for Ableton MCP

Uses Gemini's automatic function calling instead of ReAct pattern.
The SDK handles tool execution automatically.

Usage:
    python gemini_native_bridge.py
    python gemini_native_bridge.py -c "Set tempo to 120"
"""

import os
import json
import socket
import argparse
from dotenv import load_dotenv

from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


def send_mcp_command(cmd_type: str, params: dict = None) -> dict:
    """Send command to AbletonMCP socket server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)

    try:
        sock.connect(("localhost", 9877))
        command = {"type": cmd_type, "params": params or {}}
        sock.sendall(json.dumps(command).encode('utf-8'))

        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                json.loads(b''.join(chunks).decode('utf-8'))
                break
            except:
                continue

        return json.loads(b''.join(chunks).decode('utf-8'))
    finally:
        sock.close()


# Log function calls for visibility
def log_call(func_name: str, args: dict):
    """Print function call for debugging."""
    print(f"  🔧 {func_name}({args})")


# Define tool functions with proper docstrings for Gemini
def set_tempo(tempo: float) -> dict:
    """Set the tempo/BPM of the Ableton session.

    Args:
        tempo: The tempo in BPM (beats per minute), e.g. 120.0

    Returns:
        Result of the operation
    """
    log_call("set_tempo", {"tempo": tempo})
    result = send_mcp_command("set_tempo", {"tempo": tempo})
    return result.get("result", {"error": result.get("message")})


def get_session_info() -> dict:
    """Get information about the current Ableton session including tempo and track count.

    Returns:
        Session info with tempo and track count
    """
    result = send_mcp_command("get_session_info")
    return result.get("result", {"error": result.get("message")})


def create_midi_track(index: int = -1) -> dict:
    """Create a new MIDI track in the Ableton session.

    Args:
        index: Position to insert track (-1 for end)

    Returns:
        Info about the created track including track_index
    """
    log_call("create_midi_track", {"index": index})
    result = send_mcp_command("create_midi_track", {"index": index})
    return result.get("result", {"error": result.get("message")})


def set_track_name(track_index: int, name: str) -> dict:
    """Rename a MIDI track. Use this after creating a track to give it a descriptive name.

    Args:
        track_index: Track index (0-based)
        name: New name for the track

    Returns:
        Result of the rename operation
    """
    log_call("set_track_name", {"track_index": track_index, "name": name})
    result = send_mcp_command("set_track_name", {"track_index": track_index, "name": name})
    return result.get("result", {"error": result.get("message")})


def get_arrangement_clips(track_index: int) -> dict:
    """Get all arrangement clips on a specific track.

    Args:
        track_index: The index of the track (0-based)

    Returns:
        List of clips with their indices and time ranges
    """
    result = send_mcp_command("get_arrangement_clips", {"track_index": track_index})
    return result.get("result", {"error": result.get("message")})


def create_arrangement_clip(track_index: int, start_time: float, length: float) -> dict:
    """Create a new MIDI clip in the arrangement view.

    Args:
        track_index: The track to create the clip on
        start_time: Start position in beats (0.0 = bar 1 beat 1)
        length: Length of the clip in beats

    Returns:
        Info about the created clip including clip_index
    """
    log_call("create_arrangement_clip", {"track_index": track_index, "start_time": start_time, "length": length})
    result = send_mcp_command("create_arrangement_clip", {
        "track_index": track_index,
        "start_time": start_time,
        "length": length
    })
    return result.get("result", {"error": result.get("message")})


def add_note(track_index: int, clip_index: int, pitch: int, start_time: float, duration: float, velocity: int = 100) -> dict:
    """Add a single MIDI note to an arrangement clip.

    Args:
        track_index: The track containing the clip
        clip_index: The index of the clip
        pitch: MIDI note number (0-127). Drums: kick=36, snare=38, hihat=42, open_hat=46
        start_time: Start position in beats (0=beat1, 1=beat2, 0.5=8th note)
        duration: Note length in beats (0.5=8th, 1.0=quarter)
        velocity: Note velocity 1-127

    Returns:
        Result of the operation
    """
    notes = [{"pitch": pitch, "start_time": start_time, "duration": duration, "velocity": velocity}]
    result = send_mcp_command("add_notes_to_arrangement_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "notes": notes
    })
    return result.get("result", {"error": result.get("message")})


def add_drum_pattern(track_index: int, clip_index: int, pattern: str = "basic") -> dict:
    """Add a pre-defined drum pattern to a clip.

    Args:
        track_index: The track containing the clip
        clip_index: The index of the clip
        pattern: Pattern type - "basic", "boom_bap", "four_on_floor", "trap"

    Returns:
        Result of the operation
    """
    log_call("add_drum_pattern", {"track_index": track_index, "clip_index": clip_index, "pattern": pattern})
    patterns = {
        "basic": [
            {"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 100},
            {"pitch": 38, "start_time": 1.0, "duration": 0.5, "velocity": 100},
            {"pitch": 36, "start_time": 2.0, "duration": 0.5, "velocity": 100},
            {"pitch": 38, "start_time": 3.0, "duration": 0.5, "velocity": 100},
        ],
        "boom_bap": [
            {"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 110},
            {"pitch": 36, "start_time": 1.58, "duration": 0.5, "velocity": 95},  # swung and of 2
            {"pitch": 38, "start_time": 1.0, "duration": 0.5, "velocity": 120},
            {"pitch": 38, "start_time": 3.0, "duration": 0.5, "velocity": 120},
            {"pitch": 42, "start_time": 0.0, "duration": 0.2, "velocity": 85},
            {"pitch": 42, "start_time": 0.58, "duration": 0.2, "velocity": 60},  # swung
            {"pitch": 42, "start_time": 1.0, "duration": 0.2, "velocity": 80},
            {"pitch": 42, "start_time": 1.58, "duration": 0.2, "velocity": 55},
            {"pitch": 42, "start_time": 2.0, "duration": 0.2, "velocity": 85},
            {"pitch": 46, "start_time": 2.58, "duration": 0.3, "velocity": 65},  # open hat
            {"pitch": 42, "start_time": 3.0, "duration": 0.2, "velocity": 80},
            {"pitch": 42, "start_time": 3.58, "duration": 0.2, "velocity": 55},
        ],
        "four_on_floor": [
            {"pitch": 36, "start_time": float(i), "duration": 0.5, "velocity": 100}
            for i in range(4)
        ],
        "trap": [
            {"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 110},
            {"pitch": 36, "start_time": 2.25, "duration": 0.5, "velocity": 100},
            {"pitch": 38, "start_time": 1.0, "duration": 0.5, "velocity": 120},
            {"pitch": 38, "start_time": 3.0, "duration": 0.5, "velocity": 120},
        ] + [{"pitch": 42, "start_time": i * 0.25, "duration": 0.1, "velocity": 70 + (i % 4) * 10} for i in range(16)],
    }

    notes = patterns.get(pattern, patterns["basic"])
    result = send_mcp_command("add_notes_to_arrangement_clip", {
        "track_index": track_index,
        "clip_index": clip_index,
        "notes": notes
    })
    return result.get("result", {"error": result.get("message")})


def search_presets(query: str, limit: int = 5) -> dict:
    """Search for instrument/effect presets in Ableton's browser.

    Args:
        query: Search term (e.g. "808", "pad", "reverb")
        limit: Maximum number of results

    Returns:
        List of matching presets with name and uri
    """
    log_call("search_presets", {"query": query, "limit": limit})
    # Detect category
    drum_keywords = ["drum", "kit", "kick", "snare", "hat", "808", "909"]
    is_drum = any(kw in query.lower() for kw in drum_keywords)
    category = "drums" if is_drum else "instruments"

    result = send_mcp_command("get_all_presets", {"category_type": category, "max_depth": 5})
    if result.get("status") != "success":
        return {"error": result.get("message")}

    presets = result.get("result", {}).get("presets", [])
    matches = []
    for preset in presets:
        name = preset.get("name", "").lower()
        if any(word in name for word in query.lower().split()):
            if is_drum and not name.endswith('.adg'):
                continue
            matches.append({"name": preset.get("name"), "uri": preset.get("uri")})
            if len(matches) >= limit:
                break

    return {"query": query, "matches": matches}


def load_instrument_or_effect(track_index: int, uri: str) -> dict:
    """Load an instrument or effect preset onto a track.

    Args:
        track_index: The track to load the preset on
        uri: The preset URI from search_presets

    Returns:
        Result of the operation
    """
    log_call("load_instrument_or_effect", {"track_index": track_index, "uri": uri})
    result = send_mcp_command("load_browser_item", {"track_index": track_index, "item_uri": uri})
    return result.get("result", {"error": result.get("message")})


def start_playback() -> dict:
    """Start playback in Ableton.

    Returns:
        Result of the operation
    """
    result = send_mcp_command("start_playback")
    return result.get("result", {"error": result.get("message")})


def stop_playback() -> dict:
    """Stop playback in Ableton.

    Returns:
        Result of the operation
    """
    result = send_mcp_command("stop_playback")
    return result.get("result", {"error": result.get("message")})


# All available tools
TOOLS = [
    set_tempo,
    get_session_info,
    create_midi_track,
    set_track_name,
    get_arrangement_clips,
    create_arrangement_clip,
    add_note,
    add_drum_pattern,
    search_presets,
    load_instrument_or_effect,
    start_playback,
    stop_playback,
]


SYSTEM_PROMPT = """You are a music production AI assistant with direct control over Ableton Live.

Use tools to complete requests. For drums, use add_drum_pattern with pattern types:
- "boom_bap" - classic 90s hip hop with swing
- "trap" - modern trap with fast hihats
- "four_on_floor" - house/techno kick pattern
- "basic" - simple kick/snare

For individual notes, use add_note with pitch, start_time, duration, velocity.

DRUM PITCHES: kick=36, snare=38, hihat=42, open_hat=46
MUSIC THEORY: C minor = 60,63,67 | Chords need same start_time

Always check get_arrangement_clips before adding notes."""


def get_session_context() -> str:
    """Get compact session context for the model."""
    try:
        r = send_mcp_command("get_session_summary")
        if r.get("status") != "success":
            return ""

        data = r["result"]
        tracks = data.get("tracks", [])
        if not tracks:
            return ""

        parts = []
        for t in tracks:
            clip_marker = "*" if t.get("clips") else ""
            parts.append(f"{t['i']}:{t['cat']}({t['dev']}){clip_marker}")

        return f"Current session: {' '.join(parts)}\n\n"
    except:
        return ""


def run_prompt(user_input: str, model_name: str = "gemini-3-flash-preview"):
    """Run a prompt with Gemini's automatic function calling via chat feature.

    Uses the chat feature so thought signatures are handled automatically.
    """

    context = get_session_context()
    full_prompt = context + user_input

    print(f"\nPrompt: {user_input}")
    print("-" * 40)

    # Use automatic function calling - SDK should handle thought signatures
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
        temperature=0,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=10  # Allow up to 10 function call rounds
        ),
    )

    # Create a chat session - this handles thought signatures automatically
    chat = client.chats.create(model=model_name, config=config)

    response = chat.send_message(full_prompt)
    print(f"Response: {response.text}")
    return response.text


def main():
    parser = argparse.ArgumentParser(description="Gemini Native Bridge for Ableton Live")
    parser.add_argument("-c", "--command", help="Single command to execute")
    parser.add_argument("-m", "--model", default="gemini-3-flash-preview",
                        help="Model to use (default: gemini-3-flash-preview)")
    args = parser.parse_args()

    print(f"Gemini Native Bridge ({args.model})")
    print("=" * 40)

    # Test MCP connection
    try:
        result = send_mcp_command("get_session_info")
        if result.get("status") == "success":
            track_count = result["result"]["track_count"]
            tempo = result["result"]["tempo"]
            print(f"Connected to Ableton! {track_count} tracks, {tempo} BPM")
        else:
            print("Warning: Could not connect to AbletonMCP")
    except Exception as e:
        print(f"Error connecting to MCP: {e}")
        return

    if args.command:
        run_prompt(args.command, model_name=args.model)
    else:
        print("\nEnter prompts (Ctrl+C to exit):\n")
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                run_prompt(user_input, model_name=args.model)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()
