#!/usr/bin/env python3
"""
Claude MCP Bridge: Connects Claude to Ableton via MCP

Uses Claude's native tool use for reliable function calling.

Usage:
    python claude_mcp_bridge.py
    python claude_mcp_bridge.py -c "Set tempo to 120"
"""

import os
import json
import socket
import argparse
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


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


# Tool definitions for Claude
TOOLS = [
    {
        "name": "set_tempo",
        "description": "Set the tempo/BPM of the Ableton session",
        "input_schema": {
            "type": "object",
            "properties": {
                "tempo": {"type": "number", "description": "Tempo in BPM (e.g. 120)"}
            },
            "required": ["tempo"]
        }
    },
    {
        "name": "get_session_info",
        "description": "Get information about the current Ableton session (tempo, track count)",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "create_midi_track",
        "description": "Create a new MIDI track",
        "input_schema": {
            "type": "object",
            "properties": {
                "index": {"type": "integer", "description": "Position to insert track (-1 for end)"}
            }
        }
    },
    {
        "name": "set_track_name",
        "description": "Rename a MIDI track. Use this after creating a track to give it a descriptive name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Track index (0-based)"},
                "name": {"type": "string", "description": "New name for the track"}
            },
            "required": ["track_index", "name"]
        }
    },
    {
        "name": "get_arrangement_clips",
        "description": "Get all arrangement clips on a track. Use this BEFORE adding notes to find existing clips.",
        "input_schema": {
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Track index (0-based)"}
            },
            "required": ["track_index"]
        }
    },
    {
        "name": "create_arrangement_clip",
        "description": "Create a new MIDI clip in arrangement view",
        "input_schema": {
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Track index"},
                "start_time": {"type": "number", "description": "Start position in beats"},
                "length": {"type": "number", "description": "Clip length in beats"}
            },
            "required": ["track_index", "start_time", "length"]
        }
    },
    {
        "name": "add_notes_to_arrangement_clip",
        "description": "Add MIDI notes to a clip. Drum pitches: kick=36, snare=38, closed_hat=42, open_hat=46, crash=49",
        "input_schema": {
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Track index"},
                "clip_index": {"type": "integer", "description": "Clip index"},
                "notes": {
                    "type": "array",
                    "description": "List of notes to add",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pitch": {"type": "integer", "description": "MIDI pitch (0-127)"},
                            "start_time": {"type": "number", "description": "Start in beats"},
                            "duration": {"type": "number", "description": "Length in beats"},
                            "velocity": {"type": "integer", "description": "Velocity (1-127)"}
                        },
                        "required": ["pitch", "start_time", "duration", "velocity"]
                    }
                }
            },
            "required": ["track_index", "clip_index", "notes"]
        }
    },
    {
        "name": "search_presets",
        "description": "Search for instrument/effect presets (e.g. '808', 'pad', 'reverb')",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
                "limit": {"type": "integer", "description": "Max results (default 5)"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "load_instrument_or_effect",
        "description": "Load a preset onto a track using its URI",
        "input_schema": {
            "type": "object",
            "properties": {
                "track_index": {"type": "integer", "description": "Track index"},
                "uri": {"type": "string", "description": "Preset URI from search_presets"}
            },
            "required": ["track_index", "uri"]
        }
    },
    {
        "name": "start_playback",
        "description": "Start playback",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "stop_playback",
        "description": "Stop playback",
        "input_schema": {"type": "object", "properties": {}}
    }
]


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool and return the result"""

    # Handle search_presets locally
    if name == "search_presets":
        query = args.get("query", "")
        limit = args.get("limit", 5)
        query_lower = query.lower()

        # Detect category from keywords
        drum_keywords = ["drum", "kit", "kick", "snare", "hat", "808", "909"]
        effect_keywords = ["reverb", "delay", "echo", "chorus", "flanger", "phaser",
                          "compressor", "eq", "filter", "distortion", "saturator"]

        is_drum = any(kw in query_lower for kw in drum_keywords)
        is_effect = any(kw in query_lower for kw in effect_keywords)

        if is_drum:
            category = "drums"
        elif is_effect:
            category = "audio_effects"
        else:
            category = "instruments"

        result = send_mcp_command("get_all_presets", {"category_type": category, "max_depth": 5})
        if result.get("status") != "success":
            return json.dumps({"error": result.get("message")})

        presets = result.get("result", {}).get("presets", [])
        matches = []
        for preset in presets:
            pname = preset.get("name", "").lower()
            if any(word in pname for word in query_lower.split()):
                if is_drum and not pname.endswith('.adg'):
                    continue
                matches.append({"name": preset.get("name"), "uri": preset.get("uri")})
                if len(matches) >= limit:
                    break
        return json.dumps({"query": query, "category": category, "matches": matches})

    # Map tool names to MCP commands
    cmd_map = {
        "set_tempo": "set_tempo",
        "get_session_info": "get_session_info",
        "create_midi_track": "create_midi_track",
        "set_track_name": "set_track_name",
        "get_arrangement_clips": "get_arrangement_clips",
        "create_arrangement_clip": "create_arrangement_clip",
        "add_notes_to_arrangement_clip": "add_notes_to_arrangement_clip",
        "load_instrument_or_effect": "load_browser_item",
        "start_playback": "start_playback",
        "stop_playback": "stop_playback",
    }

    cmd_type = cmd_map.get(name, name)

    # Handle param name mapping
    if name == "load_instrument_or_effect":
        args = {"track_index": args.get("track_index"), "item_uri": args.get("uri")}

    result = send_mcp_command(cmd_type, args)

    if result.get("status") == "success":
        return json.dumps(result.get("result", {}))
    else:
        return json.dumps({"error": result.get("message", "Unknown error")})


def get_session_context() -> str:
    """Get compact session context"""
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

        return f"Session: {' '.join(parts)}"
    except:
        return ""


SYSTEM_PROMPT = """You are a music production AI with direct Ableton Live control.

DISCOVERY TOOLS (use these first when unsure):
- search_presets: Search Ableton presets. Args: {"query": "reverb", "limit": 5}

EXAMPLE - Creating a drum beat:
1. create_midi_track at index 0 → returns track_index
2. search_presets for drum kit → get URI (use "808" or "909" for classic kits)
3. load_instrument_or_effect with SAME track_index and URI
4. create_arrangement_clip on SAME track_index
5. add_notes_to_arrangement_clip on SAME track_index (kick=36, snare=38, hat=42)

EXAMPLE - Adding to existing clip:
1. get_arrangement_clips for the track → see existing clips
2. add_notes_to_arrangement_clip with SAME track_index and clip_index (DON'T create new clip)

CRITICAL RULES:
- Instrument and notes MUST be on the SAME track_index
- Before creating clips, CHECK if one already exists with get_arrangement_clips
- To add more notes (hihats, etc), use add_notes_to_arrangement_clip on EXISTING clip"""


def run_conversation(user_input: str, model: str = "claude-haiku-4-5", use_thinking: bool = True):
    """Run a conversation with Claude using tool use"""

    context = get_session_context()
    if context:
        user_input = f"[{context}]\n\n{user_input}"

    messages = [{"role": "user", "content": user_input}]

    print(f"\nYou: {user_input.split(']')[-1].strip() if ']' in user_input else user_input}")
    print("-" * 40)

    while True:
        # Build API call params
        api_params = {
            "model": model,
            "max_tokens": 16000,  # Higher for thinking
            "system": SYSTEM_PROMPT,
            "tools": TOOLS,
            "messages": messages,
        }

        # Add extended thinking if enabled
        if use_thinking:
            api_params["thinking"] = {"type": "enabled", "budget_tokens": 4096}

        response = client.messages.create(**api_params)

        # Display thinking blocks if present
        for block in response.content:
            if block.type == "thinking":
                print(f"\n💭 Thinking: {block.thinking[:500]}...")

        # Check for tool use
        tool_uses = [block for block in response.content if block.type == "tool_use"]

        if not tool_uses:
            # No tool use, get text response
            text_blocks = [block.text for block in response.content
                          if hasattr(block, "text") and block.type == "text"]
            final_response = " ".join(text_blocks)
            print(f"Claude: {final_response}")
            return final_response

        # Execute tools
        tool_results = []
        for tool_use in tool_uses:
            print(f"  -> {tool_use.name}({json.dumps(tool_use.input)[:60]}...)")
            result = execute_tool(tool_use.name, tool_use.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            })

        # Add assistant message and tool results
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})


def main():
    parser = argparse.ArgumentParser(description="Claude MCP Bridge for Ableton Live")
    parser.add_argument("-c", "--command", help="Single command to execute")
    parser.add_argument("-m", "--model", default="claude-haiku-4-5",
                        help="Model (default: claude-haiku-4-5)")
    parser.add_argument("--no-thinking", action="store_true",
                        help="Disable extended thinking")
    args = parser.parse_args()

    use_thinking = not args.no_thinking
    thinking_status = "thinking ON" if use_thinking else "thinking OFF"
    print(f"Claude MCP Bridge ({args.model}, {thinking_status})")
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
        run_conversation(args.command, model=args.model, use_thinking=use_thinking)
    else:
        print("\nEnter prompts (Ctrl+C to exit):\n")
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                run_conversation(user_input, model=args.model, use_thinking=use_thinking)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()
