#!/usr/bin/env python3
"""
MIDI Generation Benchmark for LLM + MCP

Tests different LLMs on their ability to:
1. Use Ableton MCP tools correctly
2. Generate musically sensible patterns
3. Recover from errors
4. Complete multi-step tasks

Usage:
    python benchmark_midi_generation.py
    python benchmark_midi_generation.py --models claude,gemini
    python benchmark_midi_generation.py --test simple
"""

import os
import json
import socket
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# TEST CASES WITH OBJECTIVE GROUND TRUTH
# ============================================================================

TEST_CASES = {
    # Simple tool use test
    "simple": {
        "name": "Simple Tempo Change",
        "prompt": "Set the tempo to 95 BPM",
        "expected_tools": ["set_tempo"],
        "max_iterations": 5,
        "verify_type": "tempo",
        "expected_tempo": 95,
    },

    # Drum pattern tests - scored against reference MIDI
    # Prompts are intentionally minimal to test model's genre knowledge
    "boom_bap": {
        "name": "Boom Bap Drums",
        "prompt": "Create a new midi track, set the tempo to 90 BPM, load a drum kit suitable for boom bap, and create a boom bap drum pattern. Pitches: kick=36, snare=38, hat=42, open_hat=46.",
        "expected_tools": ["create_midi_track", "search_presets", "load_instrument_or_effect",
                          "create_arrangement_clip", "add_notes_to_arrangement_clip"],
        "max_iterations": 15,
        "verify_type": "beat_similarity",
        "genre": "boom_bap",
    },
    "trap": {
        "name": "Trap Drums",
        "prompt": "Create a new midi track, set the tempo to 140 BPM, load a drum kit suitable for trap, and create a trap drum pattern. Pitches: kick=36, snare=38, hat=42, open_hat=46.",
        "expected_tools": ["create_midi_track", "search_presets", "load_instrument_or_effect",
                          "create_arrangement_clip", "add_notes_to_arrangement_clip"],
        "max_iterations": 15,
        "verify_type": "beat_similarity",
        "genre": "trap",
    },
    "house": {
        "name": "House Drums",
        "prompt": "Create a new midi track, set the tempo to 125 BPM, load a drum kit suitable for house, and create a house drum pattern. Pitches: kick=36, snare=38, hat=42, open_hat=46.",
        "expected_tools": ["create_midi_track", "search_presets", "load_instrument_or_effect",
                          "create_arrangement_clip", "add_notes_to_arrangement_clip"],
        "max_iterations": 15,
        "verify_type": "beat_similarity",
        "genre": "house",
    },
    "dnb": {
        "name": "Drum and Bass",
        "prompt": "Create a new midi track, set the tempo to 174 BPM, load a drum kit suitable for drum and bass, and create a drum and bass drum pattern. Pitches: kick=36, snare=38, hat=42, open_hat=46.",
        "expected_tools": ["create_midi_track", "search_presets", "load_instrument_or_effect",
                          "create_arrangement_clip", "add_notes_to_arrangement_clip"],
        "max_iterations": 15,
        "verify_type": "beat_similarity",
        "genre": "dnb",
    },

    # Chord progression test - scored against reference MIDI
    "chord_progression": {
        "name": "Chord Progression (C Minor)",
        "prompt": "Create a new midi track, load a synth pad suitable for chords, and create a C minor chord progression with 4 chords, each lasting 1 bar.",
        "expected_tools": ["create_midi_track", "search_presets", "load_instrument_or_effect",
                          "create_arrangement_clip", "add_notes_to_arrangement_clip"],
        "max_iterations": 15,
        "verify_type": "chord_progression",
        "key": "C_minor",
        "progression": ["i", "iv", "VII", "i"],  # Cm - Fm - Bb - Cm (common progression)
        # Reference: C minor = 48/60, F minor = 53/65, Bb major = 46/58
    },

    # Full production tests - drums AND bass together (realistic workflow)
    # Note: {model_name} placeholder is replaced at runtime
    "dnb_full": {
        "name": "DnB Drums + Bass",
        "prompt": "Create a drum and bass track at 174 BPM. Create TWO new MIDI tracks: (1) A drum track with a DnB drum pattern (kick=36, snare=38, hat=42) - once created, rename the MIDI track to 'DnB - {model_name} - Drums' using set_track_name, and (2) A bass track with a melodic DnB bassline in C minor. The bass should complement the drums. Once created, rename the MIDI track to 'DnB - {model_name} - Bass' using set_track_name",
        "expected_tools": ["create_midi_track", "set_track_name", "search_presets", "load_instrument_or_effect",
                          "create_arrangement_clip", "add_notes_to_arrangement_clip"],
        "max_iterations": 20,
        "verify_type": "full_production",
        "genre": "dnb",
        "key": "C_minor",
    },
    "wook_full": {
        "name": "Wook/Trap Drums + Bass",
        "prompt": "Create a wook trap track at 150 BPM. Create TWO new MIDI tracks: (1) A drum track with a trap drum pattern (kick=36, snare=38, hat=42) - once created, rename the MIDI track to 'Wook - {model_name} - Drums' using set_track_name, and (2) A bass track with a bass pattern. The bass should complement the drum. Once created, rename the MIDI track to 'Wook - {model_name} - Bass' using set_track_name",
        "expected_tools": ["create_midi_track", "set_track_name", "search_presets", "load_instrument_or_effect",
                          "create_arrangement_clip", "add_notes_to_arrangement_clip"],
        "max_iterations": 20,
        "verify_type": "full_production",
        "genre": "wook",
        "key": "C_minor",
    },
}


# ============================================================================
# MCP HELPERS
# ============================================================================

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


def clear_session():
    """Clear all tracks from the session for clean tests"""
    # This would ideally delete all tracks, but we'll just note the starting state
    info = send_mcp_command("get_session_info")
    return info.get("result", {})


def get_initial_state() -> dict:
    """Capture initial Ableton state before test"""
    state = {"track_count": 0, "tempo": 120}
    try:
        info = send_mcp_command("get_session_info")
        if info.get("status") == "success":
            state["tempo"] = info["result"]["tempo"]
            state["track_count"] = info["result"]["track_count"]
    except:
        pass
    return state


def collect_generated_notes(initial_track_count: int) -> list:
    """
    Collect all notes from tracks created after the test started.
    Returns list of note dicts.
    """
    all_notes = []
    try:
        info = send_mcp_command("get_session_info")
        current_tracks = info["result"]["track_count"]

        # Check all tracks (new ones first, in case notes were added to existing)
        for track_idx in range(current_tracks):
            clips_result = send_mcp_command("get_arrangement_clips", {"track_index": track_idx})
            if clips_result.get("status") == "success":
                clips = clips_result.get("result", {}).get("clips", [])
                for clip_idx, clip in enumerate(clips):
                    if clip.get("is_midi_clip"):
                        # Fetch actual notes from clip using new MCP command
                        notes_result = send_mcp_command("get_arrangement_clip_notes", {
                            "track_index": track_idx,
                            "clip_index": clip_idx
                        })
                        if notes_result.get("status") == "success":
                            notes = notes_result.get("result", {}).get("notes", [])
                            for note in notes:
                                all_notes.append({
                                    "pitch": note.get("pitch"),
                                    "start_time": note.get("start_time"),
                                    "duration": note.get("duration"),
                                    "velocity": note.get("velocity"),
                                    "track_index": track_idx,
                                })
    except Exception as e:
        print(f"  Error collecting notes: {e}")

    return all_notes


def verify_test_result(test_case: dict, initial_state: dict) -> dict:
    """
    Verify test result by querying Ableton and comparing to ground truth.
    Returns verification result with score.
    """
    verify_type = test_case.get("verify_type")
    result = {"verified": False, "score": 0.0, "details": {}}

    if not verify_type:
        return {"verified": False, "reason": "No verification configured"}

    try:
        if verify_type == "tempo":
            # Check tempo matches expected
            info = send_mcp_command("get_session_info")
            actual = info["result"]["tempo"]
            expected = test_case["expected_tempo"]
            result["details"]["expected"] = expected
            result["details"]["actual"] = actual
            result["verified"] = abs(actual - expected) < 0.5
            result["score"] = 1.0 if result["verified"] else 0.0

        elif verify_type == "beat_similarity":
            # Compare generated pattern to reference MIDI
            from beat_similarity import evaluate_generated_pattern

            notes = collect_generated_notes(initial_state["track_count"])
            if not notes:
                result["details"]["error"] = "No notes found"
                result["score"] = 0.0
            else:
                genre = test_case["genre"]
                eval_result = evaluate_generated_pattern(notes, genre)
                result["verified"] = eval_result.get("total_score", 0) > 0.5
                result["score"] = eval_result.get("total_score", 0)
                result["details"] = eval_result

        elif verify_type == "chord_progression":
            # Compare generated chords to expected progression
            notes = collect_generated_notes(initial_state["track_count"])
            if not notes:
                result["details"]["error"] = "No notes found"
                result["score"] = 0.0
            else:
                # Group notes by start time to find chords
                from collections import defaultdict
                chords = defaultdict(list)
                for n in notes:
                    # Round to nearest beat
                    beat = round(n["start_time"])
                    chords[beat].append(n["pitch"])

                result["details"]["chords_found"] = len(chords)
                result["details"]["progression"] = test_case.get("progression", [])

                # Expected roots for i-iv-VII-i in C minor: C(48/60), F(53/65), Bb(58/70), C(48/60)
                expected_roots = {
                    "i": [48, 60],   # C
                    "iv": [53, 65],  # F
                    "VII": [58, 70], # Bb
                }

                progression = test_case.get("progression", [])
                score = 0.0
                for i, numeral in enumerate(progression):
                    beat = i * 4  # Each chord at 0, 4, 8, 12
                    if beat in chords:
                        chord_pitches = set(chords[beat])
                        expected = set(expected_roots.get(numeral, []))
                        # Check if any expected root is present (any octave)
                        root_classes = {p % 12 for p in expected}
                        found_classes = {p % 12 for p in chord_pitches}
                        if root_classes & found_classes:
                            score += 1.0 / len(progression)

                result["verified"] = score > 0.5
                result["score"] = score
                result["details"]["chord_score"] = score

        elif verify_type == "bassline_similarity":
            # Compare generated bassline to genre characteristics
            from bassline_similarity import evaluate_generated_bassline

            notes = collect_generated_notes(initial_state["track_count"])
            if not notes:
                result["details"]["error"] = "No notes found"
                result["score"] = 0.0
            else:
                genre = test_case["genre"]
                key = test_case.get("key", "C_minor")
                eval_result = evaluate_generated_bassline(notes, genre, key)
                result["verified"] = eval_result.get("total_score", 0) > 0.5
                result["score"] = eval_result.get("total_score", 0)
                result["details"] = eval_result

        elif verify_type == "full_production":
            # Score both drums AND bass together
            from beat_similarity import evaluate_generated_pattern
            from bassline_similarity import evaluate_generated_bassline

            all_notes = collect_generated_notes(initial_state["track_count"])
            if not all_notes:
                result["details"]["error"] = "No notes found"
                result["score"] = 0.0
            else:
                # Separate drum notes from bass notes by pitch range
                # Drums typically use GM mapping: kick=36, snare=38, hats=42-46
                # Bass is usually below 60 but not in drum range, or melodic notes
                drum_pitches = {36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51}

                drum_notes = [n for n in all_notes if n["pitch"] in drum_pitches]
                bass_notes = [n for n in all_notes if n["pitch"] not in drum_pitches]

                genre = test_case["genre"]
                key = test_case.get("key", "C_minor")

                # Map genre to drum genre (wook uses trap drums)
                drum_genre = "trap" if genre == "wook" else genre

                # Score drums
                drum_score = 0.0
                if drum_notes:
                    drum_result = evaluate_generated_pattern(drum_notes, drum_genre)
                    drum_score = drum_result.get("total_score", 0)
                    result["details"]["drum_eval"] = drum_result
                else:
                    result["details"]["drum_eval"] = {"error": "No drum notes found"}

                # Score bass
                bass_score = 0.0
                if bass_notes:
                    bass_result = evaluate_generated_bassline(bass_notes, genre, key)
                    bass_score = bass_result.get("total_score", 0)
                    result["details"]["bass_eval"] = bass_result
                else:
                    result["details"]["bass_eval"] = {"error": "No bass notes found"}

                # Combined score (weighted average)
                if drum_notes and bass_notes:
                    result["score"] = (drum_score * 0.5) + (bass_score * 0.5)
                elif drum_notes:
                    result["score"] = drum_score * 0.5  # Penalize missing bass
                elif bass_notes:
                    result["score"] = bass_score * 0.5  # Penalize missing drums
                else:
                    result["score"] = 0.0

                result["verified"] = result["score"] > 0.5
                result["details"]["drum_score"] = drum_score
                result["details"]["bass_score"] = bass_score
                result["details"]["drum_note_count"] = len(drum_notes)
                result["details"]["bass_note_count"] = len(bass_notes)

    except Exception as e:
        result["error"] = str(e)
        result["score"] = 0.0

    return result


# ============================================================================
# MODEL RUNNERS
# ============================================================================

def run_claude(prompt: str, max_iterations: int = 15, use_thinking: bool = True) -> dict:
    """Run prompt with Claude Haiku"""
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Import tools from claude bridge
    from claude_mcp_bridge import TOOLS, execute_tool, get_session_context, SYSTEM_PROMPT

    context = get_session_context()
    if context:
        prompt = f"[{context}]\n\n{prompt}"

    messages = [{"role": "user", "content": prompt}]

    result = {
        "model": "claude-haiku-4-5",
        "thinking": use_thinking,
        "iterations": 0,
        "tool_calls": [],
        "errors": [],
        "final_response": None,
        "success": False,
        "start_time": time.time(),
    }

    for i in range(max_iterations):
        result["iterations"] = i + 1

        api_params = {
            "model": "claude-haiku-4-5",
            "max_tokens": 16000,
            "system": SYSTEM_PROMPT,
            "tools": TOOLS,
            "messages": messages,
        }

        if use_thinking:
            api_params["thinking"] = {"type": "enabled", "budget_tokens": 4096}

        try:
            response = client.messages.create(**api_params)
        except Exception as e:
            result["errors"].append(str(e))
            break

        # Extract tool uses
        tool_uses = [block for block in response.content if block.type == "tool_use"]

        if not tool_uses:
            # Final response
            text_blocks = [block.text for block in response.content
                          if hasattr(block, "text") and block.type == "text"]
            result["final_response"] = " ".join(text_blocks)
            result["success"] = True
            break

        # Execute tools
        tool_results = []
        for tool_use in tool_uses:
            result["tool_calls"].append({
                "name": tool_use.name,
                "args": tool_use.input,
                "iteration": i + 1
            })

            try:
                tool_result = execute_tool(tool_use.name, tool_use.input)
                if "error" in tool_result.lower():
                    result["errors"].append(f"{tool_use.name}: {tool_result}")
            except Exception as e:
                tool_result = f"Error: {e}"
                result["errors"].append(f"{tool_use.name}: {e}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": tool_result
            })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    result["elapsed_time"] = time.time() - result["start_time"]
    return result


def run_gemini(prompt: str, max_iterations: int = 15) -> dict:
    """Run prompt with Gemini 3 Flash Preview using native function calling"""
    from google import genai
    from google.genai import types

    # Import tools and helpers from native bridge
    from gemini_native_bridge import (
        TOOLS, SYSTEM_PROMPT, get_session_context,
        set_tempo, get_session_info, create_midi_track,
        get_arrangement_clips, create_arrangement_clip,
        add_note, add_drum_pattern, search_presets,
        load_instrument_or_effect, start_playback, stop_playback
    )

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    context = get_session_context()
    full_prompt = context + prompt if context else prompt

    result = {
        "model": "gemini-3-flash-preview",
        "iterations": 1,  # Native function calling handles iterations internally
        "tool_calls": [],
        "errors": [],
        "final_response": None,
        "success": False,
        "start_time": time.time(),
    }

    # Use native function calling with automatic execution
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
        temperature=0,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=max_iterations
        ),
    )

    try:
        chat = client.chats.create(model="gemini-3-flash-preview", config=config)
        response = chat.send_message(full_prompt)

        result["final_response"] = response.text
        result["success"] = True

        # Extract tool calls from chat history
        for msg in chat.get_history():
            if msg.role == "model":
                for part in msg.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        result["tool_calls"].append({
                            "name": fc.name,
                            "args": dict(fc.args) if fc.args else {},
                            "iteration": len(result["tool_calls"]) + 1
                        })

    except Exception as e:
        result["errors"].append(str(e))

    result["elapsed_time"] = time.time() - result["start_time"]
    return result


def run_gemini_pro(prompt: str, max_iterations: int = 15) -> dict:
    """
    Run prompt with Gemini 3 Pro using native function calling.

    All tool execution routes through gemini_native_bridge functions which
    call send_mcp_command() → AbletonMCP socket server (port 9877).
    """
    from google import genai
    from google.genai import types

    # These functions all call send_mcp_command() internally
    from gemini_native_bridge import (
        TOOLS, SYSTEM_PROMPT, get_session_context,
        set_tempo, get_session_info, create_midi_track,
        get_arrangement_clips, create_arrangement_clip,
        add_note, add_drum_pattern, search_presets,
        load_instrument_or_effect, start_playback, stop_playback
    )

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    context = get_session_context()
    full_prompt = context + prompt if context else prompt

    result = {
        "model": "gemini-3-pro-preview",
        "iterations": 1,
        "tool_calls": [],
        "errors": [],
        "final_response": None,
        "success": False,
        "start_time": time.time(),
    }

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
        temperature=0,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=max_iterations
        ),
    )

    try:
        chat = client.chats.create(model="gemini-3-pro-preview", config=config)
        response = chat.send_message(full_prompt)

        result["final_response"] = response.text
        result["success"] = True

        # Extract tool calls from chat history
        for msg in chat.get_history():
            if msg.role == "model":
                for part in msg.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        result["tool_calls"].append({
                            "name": fc.name,
                            "args": dict(fc.args) if fc.args else {},
                            "iteration": len(result["tool_calls"]) + 1
                        })

    except Exception as e:
        result["errors"].append(str(e))

    result["elapsed_time"] = time.time() - result["start_time"]
    return result


def run_claude_sonnet(prompt: str, max_iterations: int = 15, use_thinking: bool = True) -> dict:
    """
    Run prompt with Claude 4.5 Sonnet.

    Uses execute_tool() from claude_mcp_bridge which routes all tool calls
    through send_mcp_command() → AbletonMCP socket server (port 9877).
    """
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # execute_tool calls send_mcp_command() for MCP integration
    from claude_mcp_bridge import TOOLS, execute_tool, get_session_context, SYSTEM_PROMPT

    context = get_session_context()
    if context:
        prompt = f"[{context}]\n\n{prompt}"

    messages = [{"role": "user", "content": prompt}]

    result = {
        "model": "claude-sonnet-4-5",
        "thinking": use_thinking,
        "iterations": 0,
        "tool_calls": [],
        "errors": [],
        "final_response": None,
        "success": False,
        "start_time": time.time(),
    }

    for i in range(max_iterations):
        result["iterations"] = i + 1

        api_params = {
            "model": "claude-sonnet-4-5",
            "max_tokens": 16000,
            "system": SYSTEM_PROMPT,
            "tools": TOOLS,
            "messages": messages,
        }

        if use_thinking:
            api_params["thinking"] = {"type": "enabled", "budget_tokens": 4096}

        try:
            response = client.messages.create(**api_params)
        except Exception as e:
            result["errors"].append(str(e))
            break

        tool_uses = [block for block in response.content if block.type == "tool_use"]

        if not tool_uses:
            text_blocks = [block.text for block in response.content
                          if hasattr(block, "text") and block.type == "text"]
            result["final_response"] = " ".join(text_blocks)
            result["success"] = True
            break

        tool_results = []
        for tool_use in tool_uses:
            result["tool_calls"].append({
                "name": tool_use.name,
                "args": tool_use.input,
                "iteration": i + 1
            })

            try:
                # execute_tool routes to MCP via send_mcp_command()
                tool_result = execute_tool(tool_use.name, tool_use.input)
                if "error" in tool_result.lower():
                    result["errors"].append(f"{tool_use.name}: {tool_result}")
            except Exception as e:
                tool_result = f"Error: {e}"
                result["errors"].append(f"{tool_use.name}: {e}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": tool_result
            })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    result["elapsed_time"] = time.time() - result["start_time"]
    return result


def run_claude_opus(prompt: str, max_iterations: int = 15, use_thinking: bool = True) -> dict:
    """
    Run prompt with Claude 4.5 Opus.

    Uses execute_tool() from claude_mcp_bridge which routes all tool calls
    through send_mcp_command() → AbletonMCP socket server (port 9877).
    """
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # execute_tool calls send_mcp_command() for MCP integration
    from claude_mcp_bridge import TOOLS, execute_tool, get_session_context, SYSTEM_PROMPT

    context = get_session_context()
    if context:
        prompt = f"[{context}]\n\n{prompt}"

    messages = [{"role": "user", "content": prompt}]

    result = {
        "model": "claude-opus-4-5-20251101",
        "thinking": use_thinking,
        "iterations": 0,
        "tool_calls": [],
        "errors": [],
        "final_response": None,
        "success": False,
        "start_time": time.time(),
    }

    for i in range(max_iterations):
        result["iterations"] = i + 1

        api_params = {
            "model": "claude-opus-4-5-20251101",
            "max_tokens": 16000,
            "system": SYSTEM_PROMPT,
            "tools": TOOLS,
            "messages": messages,
        }

        if use_thinking:
            api_params["thinking"] = {"type": "enabled", "budget_tokens": 10000}

        try:
            response = client.messages.create(**api_params)
        except Exception as e:
            result["errors"].append(str(e))
            break

        tool_uses = [block for block in response.content if block.type == "tool_use"]

        if not tool_uses:
            text_blocks = [block.text for block in response.content
                          if hasattr(block, "text") and block.type == "text"]
            result["final_response"] = " ".join(text_blocks)
            result["success"] = True
            break

        tool_results = []
        for tool_use in tool_uses:
            result["tool_calls"].append({
                "name": tool_use.name,
                "args": tool_use.input,
                "iteration": i + 1
            })

            try:
                # execute_tool routes to MCP via send_mcp_command()
                tool_result = execute_tool(tool_use.name, tool_use.input)
                if "error" in tool_result.lower():
                    result["errors"].append(f"{tool_use.name}: {tool_result}")
            except Exception as e:
                tool_result = f"Error: {e}"
                result["errors"].append(f"{tool_use.name}: {e}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": tool_result
            })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    result["elapsed_time"] = time.time() - result["start_time"]
    return result


def run_openai(prompt: str, max_iterations: int = 15) -> dict:
    """
    Run prompt with OpenAI GPT-5.2.

    Uses execute_tool() from claude_mcp_bridge which routes all tool calls
    through send_mcp_command() → AbletonMCP socket server (port 9877).
    """
    from openai import OpenAI as OpenAIClient

    client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))

    # execute_tool routes to MCP - same as Claude/Gemini
    from claude_mcp_bridge import TOOLS as CLAUDE_TOOLS, execute_tool, get_session_context, SYSTEM_PROMPT

    context = get_session_context()
    if context:
        prompt = f"[{context}]\n\n{prompt}"

    # Convert Claude tool format to OpenAI format
    openai_tools = []
    for tool in CLAUDE_TOOLS:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"]
            }
        })

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    result = {
        "model": "gpt-5.2",
        "iterations": 0,
        "tool_calls": [],
        "errors": [],
        "final_response": None,
        "success": False,
        "start_time": time.time(),
    }

    for i in range(max_iterations):
        result["iterations"] = i + 1

        try:
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=messages,
                tools=openai_tools,
                tool_choice="auto"
            )
        except Exception as e:
            result["errors"].append(str(e))
            break

        message = response.choices[0].message

        # Check if done
        if not message.tool_calls:
            result["final_response"] = message.content
            result["success"] = True
            break

        # Process tool calls
        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            result["tool_calls"].append({
                "name": func_name,
                "args": func_args,
                "iteration": i + 1
            })

            try:
                # execute_tool routes to MCP via send_mcp_command()
                tool_result = execute_tool(func_name, func_args)
                if "error" in tool_result.lower():
                    result["errors"].append(f"{func_name}: {tool_result}")
            except Exception as e:
                tool_result = f"Error: {e}"
                result["errors"].append(f"{func_name}: {e}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

    result["elapsed_time"] = time.time() - result["start_time"]
    return result


# ============================================================================
# BENCHMARK RUNNER
# ============================================================================

def run_benchmark(test_ids: list = None, model_ids: list = None):
    """Run benchmark tests"""

    if test_ids is None:
        test_ids = list(TEST_CASES.keys())

    if model_ids is None:
        model_ids = ["claude_haiku", "claude_sonnet", "gemini_flash", "gemini_pro", "gpt52"]

    print("=" * 60)
    print("MIDI GENERATION BENCHMARK")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Check MCP connection
    try:
        info = send_mcp_command("get_session_info")
        print(f"Connected to Ableton: {info['result']['track_count']} tracks, {info['result']['tempo']} BPM")
    except Exception as e:
        print(f"ERROR: Cannot connect to AbletonMCP: {e}")
        return

    results = {}

    for test_id in test_ids:
        test = TEST_CASES[test_id]
        print(f"\n{'='*60}")
        print(f"TEST: {test['name']}")
        print(f"Prompt: {test['prompt']}")
        print("=" * 60)

        results[test_id] = {}

        for model_id in model_ids:
            print(f"\n--- {model_id} ---")

            try:
                # Capture initial state before test
                initial_state = get_initial_state()

                # Map model_id to human-readable name for track naming
                model_display_names = {
                    "claude_haiku": "Claude Haiku",
                    "claude_sonnet": "Claude Sonnet",
                    "claude_opus": "Claude Opus",
                    "gemini_flash": "Gemini Flash",
                    "gemini_pro": "Gemini Pro",
                    "gpt52": "GPT-5.2",
                }
                model_name = model_display_names.get(model_id, model_id)

                # Replace {model_name} placeholder in prompt
                prompt = test["prompt"].replace("{model_name}", model_name)

                if model_id == "claude_haiku":
                    result = run_claude(prompt, test["max_iterations"], use_thinking=True)
                elif model_id == "claude_sonnet":
                    result = run_claude_sonnet(prompt, test["max_iterations"], use_thinking=True)
                elif model_id == "claude_opus":
                    result = run_claude_opus(prompt, test["max_iterations"], use_thinking=True)
                elif model_id == "gemini_flash":
                    result = run_gemini(prompt, test["max_iterations"])
                elif model_id == "gemini_pro":
                    result = run_gemini_pro(prompt, test["max_iterations"])
                elif model_id == "gpt52":
                    result = run_openai(prompt, test["max_iterations"])
                else:
                    print(f"Unknown model: {model_id}")
                    continue

                # Verify result against ground truth
                if result["success"]:
                    verification = verify_test_result(test, initial_state)
                    result["verification"] = verification
                    result["ground_truth_score"] = verification.get("score", 0.0)
                else:
                    result["verification"] = {"verified": False, "reason": "Model did not complete"}
                    result["ground_truth_score"] = 0.0

                results[test_id][model_id] = result

                # Print summary
                print(f"  Iterations: {result['iterations']}")
                print(f"  Tool calls: {len(result['tool_calls'])}")
                print(f"  Errors: {len(result['errors'])}")
                print(f"  Success: {result['success']}")
                print(f"  Ground Truth Score: {result['ground_truth_score']:.3f}")
                print(f"  Time: {result['elapsed_time']:.1f}s")

                if result['tool_calls']:
                    tools_used = [tc['name'] for tc in result['tool_calls']]
                    print(f"  Tools: {', '.join(set(tools_used))}")

            except Exception as e:
                print(f"  ERROR: {e}")
                results[test_id][model_id] = {"error": str(e), "ground_truth_score": 0.0}

    # Print summary table
    print("\n" + "=" * 80)
    print("SUMMARY (with Ground Truth Verification)")
    print("=" * 80)
    print(f"{'Test':<18} {'Model':<16} {'OK':<4} {'Score':<8} {'Calls':<6} {'Errs':<5} {'Time':<8}")
    print("-" * 80)

    for test_id, model_results in results.items():
        for model_id, result in model_results.items():
            if "error" in result and "ground_truth_score" not in result:
                print(f"{test_id:<18} {model_id:<16} {'✗':<4} {'-':<8} {'-':<6} {'-':<5} {'-':<8}")
            else:
                success = "✓" if result.get("success") else "✗"
                score = result.get("ground_truth_score", 0.0)
                score_str = f"{score:.3f}" if isinstance(score, float) else str(score)
                calls = len(result.get('tool_calls', []))
                errors = len(result.get('errors', []))
                elapsed = result.get('elapsed_time', 0)
                print(f"{test_id:<18} {model_id:<16} {success:<4} {score_str:<8} {calls:<6} {errors:<5} {elapsed:.1f}s")

    # Print model leaderboard
    print("\n" + "=" * 80)
    print("MODEL LEADERBOARD (Average Ground Truth Score)")
    print("=" * 80)

    model_scores = {}
    for test_id, model_results in results.items():
        for model_id, result in model_results.items():
            if model_id not in model_scores:
                model_scores[model_id] = []
            model_scores[model_id].append(result.get("ground_truth_score", 0.0))

    leaderboard = []
    for model_id, scores in model_scores.items():
        avg = sum(scores) / len(scores) if scores else 0
        leaderboard.append((model_id, avg, len(scores)))

    for rank, (model_id, avg, count) in enumerate(sorted(leaderboard, key=lambda x: -x[1]), 1):
        print(f"  {rank}. {model_id:<20} {avg:.3f} (across {count} tests)")

    # Save results
    output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


def main():
    parser = argparse.ArgumentParser(description="MIDI Generation Benchmark")
    parser.add_argument("--tests", help="Comma-separated test IDs (default: all)")
    parser.add_argument("--models", help="Comma-separated model IDs (default: all)")
    parser.add_argument("--list", action="store_true", help="List available tests")
    args = parser.parse_args()

    if args.list:
        print("Available tests:")
        for test_id, test in TEST_CASES.items():
            print(f"  {test_id}: {test['name']}")
        print("\nAvailable models:")
        print("  claude_haiku     - Claude Haiku 4.5 (fast, cheap)")
        print("  claude_sonnet    - Claude 4.5 Sonnet (best reasoning)")
        print("  claude_opus      - Claude 4.5 Opus (flagship)")
        print("  gemini_flash     - Gemini 3 Flash (fast)")
        print("  gemini_pro       - Gemini 3 Pro (best quality)")
        print("  gpt52            - GPT-5.2 (OpenAI flagship)")
        return

    test_ids = args.tests.split(",") if args.tests else None
    model_ids = args.models.split(",") if args.models else None

    run_benchmark(test_ids, model_ids)


if __name__ == "__main__":
    main()
