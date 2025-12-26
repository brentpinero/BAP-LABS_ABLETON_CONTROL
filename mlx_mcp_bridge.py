"""
MLX-MCP Bridge: Connects local Qwen3-4B (via MLX) to Ableton via MCP

Architecture:
    User Input → Qwen3-4B (MLX) → Parse Tool Calls → MCP Client → ableton-mcp → Ableton

Usage:
    python mlx_mcp_bridge.py

    Then in Ableton: Settings → Link, Tempo & MIDI → Control Surface: AbletonMCP
"""

import asyncio
import json
import re
import sys
from typing import Optional, Any, List
from contextlib import AsyncExitStack
from pydantic import BaseModel, Field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# MLX imports for local inference
from mlx_lm import load, stream_generate

# Outlines for structured generation (optional, used for validation)
try:
    import outlines
    OUTLINES_AVAILABLE = True
except ImportError:
    OUTLINES_AVAILABLE = False


# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# ============================================================================

class ToolCall(BaseModel):
    """Structured tool call that can be validated"""
    name: str = Field(description="Name of the tool to call")
    arguments: dict = Field(default_factory=dict, description="Tool arguments")


class AgentStep(BaseModel):
    """A single step in the ReAct loop"""
    thought: str = Field(description="Agent's reasoning")
    action: Optional[ToolCall] = Field(default=None, description="Tool to call")
    final_answer: Optional[str] = Field(default=None, description="Final response when done")


# ============================================================================
# CONFIGURATION
# ============================================================================

# Default Qwen model - can be overridden
DEFAULT_MODEL = "mlx-community/Qwen3-8B-4bit"

# System prompt for the music production collaborator
# Uses ReAct pattern with progressive disclosure
SYSTEM_PROMPT = """You are a music production AI with direct Ableton Live control.

You operate in a Thought → Action → Observation loop until the task is complete.

FORMAT (follow EXACTLY - no variations):
Thought: [reasoning]
Action: <tool_call>{"name": "tool_name", "arguments": {...}}</tool_call>

When done:
Thought: [summary]
Final Answer: [response]

STRICT RULES:
- Action MUST use <tool_call></tool_call> tags, never emojis or other formats
- Only give Final Answer AFTER you see successful Observations from tool calls
- Never claim success without actually calling tools first

DISCOVERY TOOLS (use these first when unsure):
- list_tools: Get available tools. Args: {"category": "session|track|device|browser|clip"}
- search_presets: Search Ableton presets. Args: {"query": "reverb", "limit": 5}

EXAMPLE - Creating a drum beat:
Thought: Need to create track, load kit ON THAT TRACK, then add notes TO SAME TRACK.
1. create_midi_track at index 0 → returns track_index
2. search_presets for drum kit → get URI
3. load_instrument_or_effect with SAME track_index and URI
4. create_arrangement_clip on SAME track_index
5. add_notes_to_arrangement_clip on SAME track_index (kick=36, snare=38, hat=42)

EXAMPLE - Adding to existing clip:
Thought: User wants to add hihats. Check if clip exists first.
1. get_arrangement_clips for the track → see existing clips
2. add_notes_to_arrangement_clip with SAME track_index and clip_index (DON'T create new clip)

CRITICAL RULES:
- Instrument and notes MUST be on the SAME track_index
- Before creating clips, CHECK if one already exists with get_arrangement_clips
- To add more notes (hihats, etc), use add_notes_to_arrangement_clip on EXISTING clip

MANDATORY WORKFLOW:
1. For EACH new category of work, call list_tools FIRST to see exact tool names
2. NEVER guess tool names - only use tools you've discovered via list_tools
3. Categories: session, track, device, browser, clip

FORMATTING: Use exactly <tool_call>{"name": "...", "arguments": {...}}</tool_call> for actions. No emojis."""


# ============================================================================
# MLX INFERENCE
# ============================================================================

class MLXInference:
    """Handles local Qwen inference via MLX"""

    def __init__(self, model_path: str = DEFAULT_MODEL):
        print(f"Loading model: {model_path}")
        self.model, self.tokenizer = load(model_path)
        print("Model loaded successfully!")

    def generate_response(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate a response from the model with early stopping"""
        response_text = ""
        stop_sequences = ["</tool_call>", "<|im_end|>", "\n\nUser:", "\n\nYou:"]

        for chunk in stream_generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens
        ):
            # Extract text from chunk
            token_text = chunk.text if hasattr(chunk, 'text') else str(chunk)
            response_text += token_text

            # Check for stop sequences
            for stop_seq in stop_sequences:
                if stop_seq in response_text:
                    # Truncate at stop sequence (include it for tool_call)
                    idx = response_text.find(stop_seq)
                    if stop_seq == "</tool_call>":
                        response_text = response_text[:idx + len(stop_seq)]
                    else:
                        response_text = response_text[:idx]
                    return response_text.strip()

        return response_text.strip()


# ============================================================================
# REACT PARSER
# ============================================================================

def parse_react_response(response: str) -> AgentStep:
    """
    Parse a ReAct-formatted response into structured AgentStep.

    Expected format:
    Thought: [reasoning]
    Action: <tool_call>{"name": "...", "arguments": {...}}</tool_call>

    Or for completion:
    Thought: [reasoning]
    Final Answer: [response]

    Also handles Qwen3's <think> blocks.
    """
    # First, try to extract from Qwen3's <think> block if present
    think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
    think_content = think_match.group(1).strip() if think_match else ""

    # Extract thought (everything after "Thought:" until "Action:" or "Final Answer:")
    thought_match = re.search(r'Thought:\s*(.*?)(?=Action:|Final Answer:|$)', response, re.DOTALL)
    thought = thought_match.group(1).strip() if thought_match else ""

    # If no explicit Thought: but we have <think> content, use that
    if not thought and think_content:
        thought = think_content

    # Check for Final Answer
    final_match = re.search(r'Final Answer:\s*(.*?)$', response, re.DOTALL)
    if final_match:
        return AgentStep(
            thought=thought,
            action=None,
            final_answer=final_match.group(1).strip()
        )

    # Extract tool call
    tool_call = None
    tool_pattern = r'<tool_call>\s*(.*?)\s*</tool_call>'
    tool_match = re.search(tool_pattern, response, re.DOTALL)

    if tool_match:
        try:
            tool_data = json.loads(tool_match.group(1).strip())
            tool_call = ToolCall(
                name=tool_data.get("name", ""),
                arguments=tool_data.get("arguments", {})
            )
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not parse tool call: {e}")

    return AgentStep(thought=thought, action=tool_call, final_answer=None)


def parse_tool_calls(response: str) -> list[dict]:
    """
    Extract tool calls from model response (legacy compatibility).
    """
    tool_calls = []
    pattern = r'<tool_call>\s*(.*?)\s*</tool_call>'
    matches = re.findall(pattern, response, re.DOTALL)

    for match in matches:
        try:
            tool_data = json.loads(match.strip())
            if "name" in tool_data:
                tool_calls.append({
                    "name": tool_data["name"],
                    "arguments": tool_data.get("arguments", {})
                })
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse tool call: {match[:100]}...")

    return tool_calls


# ============================================================================
# PROGRESSIVE DISCLOSURE - Local tool catalog (no MCP calls needed)
# ============================================================================

# NOTE: This catalog must match the actual ableton-mcp tools!
# The upstream ableton-mcp (via uvx) has different tools than our AbletonMCP_Extended
TOOL_CATALOG = {
    "session": {
        "description": "Session-level operations (tempo, playback, transport)",
        "tools": {
            "get_session_info": "Get session state (tracks, tempo, playing status)",
            "set_tempo": "Set session tempo - args: {tempo: number}",
            "start_playback": "Start playback",
            "stop_playback": "Stop playback",
        }
    },
    "track": {
        "description": "Track operations (create, modify)",
        "tools": {
            "create_midi_track": "Create new MIDI track - args: {index: number}",
            "get_track_info": "Get track details - args: {track_index: number}",
            "set_track_name": "Rename track - args: {track_index: number, name: string}",
        }
    },
    "device": {
        "description": "Load instruments/effects onto tracks",
        "tools": {
            "load_instrument_or_effect": "Load instrument/effect - args: {track_index: number, uri: string}. Use search_presets to find URIs.",
        }
    },
    "browser": {
        "description": "Browser operations (explore presets, plugins)",
        "tools": {
            "get_browser_tree": "Get browser categories",
            "get_browser_items_at_path": "Get items at path - args: {path: string}",
        }
    },
    "clip": {
        "description": "Arrangement clips. ALWAYS check get_arrangement_clips FIRST before creating new clips. DRUM NOTES: kick=36, snare=38, hat=42.",
        "tools": {
            "get_arrangement_clips": "CHECK THIS FIRST - Get existing clips - args: {track_index}",
            "add_notes_to_arrangement_clip": "Add notes to clip - args: {track_index, clip_index, notes: [{pitch, start_time, duration, velocity}]}",
            "create_arrangement_clip": "Create NEW clip (only if none exists) - args: {track_index, start_time, length}",
        }
    },
}

# Pre-loaded preset index from MCP (audio_effects, instruments, etc.)
_preset_cache = {}

def load_presets_from_mcp(category_type: str = "audio_effects") -> list:
    """Load presets from MCP socket server (cached)"""
    global _preset_cache

    if category_type in _preset_cache:
        return _preset_cache[category_type]

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect(("localhost", 9877))

        command = {"type": "get_all_presets", "params": {"category_type": category_type, "max_depth": 5}}
        sock.sendall(json.dumps(command).encode('utf-8'))

        # Receive in chunks
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                full_data = b''.join(chunks).decode('utf-8')
                json.loads(full_data)
                break
            except:
                continue

        sock.close()
        result = json.loads(b''.join(chunks).decode('utf-8'))

        if result.get("status") == "success":
            presets = result.get("result", {}).get("presets", [])
            _preset_cache[category_type] = presets
            return presets
        else:
            print(f"Warning: Failed to load presets: {result.get('message')}")
            return []
    except Exception as e:
        print(f"Warning: Could not load presets from MCP: {e}")
        return []

def handle_discovery_tool(name: str, arguments: dict) -> dict:
    """Handle discovery tools locally without MCP call"""

    if name == "list_tools":
        category = arguments.get("category")
        if category and category in TOOL_CATALOG:
            return {
                "category": category,
                "description": TOOL_CATALOG[category]["description"],
                "tools": TOOL_CATALOG[category]["tools"]
            }
        else:
            return {
                "categories": list(TOOL_CATALOG.keys()),
                "hint": "Call list_tools with category: session|track|device|browser|clip"
            }

    if name == "search_presets":
        query = arguments.get("query", "").lower()
        limit = arguments.get("limit", 10)
        category = arguments.get("category", None)

        # Drum kit keywords - machine types and genre styles
        drum_keywords = ["drum", "kit", "kick", "snare", "hat", "808", "909", "707", "606", "percussion"]
        genre_keywords = ["hip hop", "trap", "boom bap", "techno", "house", "dubstep", "dnb", "breaks",
                         "rock", "jazz", "funk", "soul", "r&b", "pop", "edm", "lo-fi", "lofi"]

        synth_keywords = ["synth", "pad", "lead", "piano", "keys", "organ", "strings", "pluck"]
        bass_keywords = ["bass", "sub", "808 bass"]  # Separate bass from drums
        effect_keywords = ["reverb", "delay", "chorus", "flanger", "phaser", "compressor", "eq", "filter", "distortion", "saturator"]

        # Check if this is a drum kit query
        is_drum_query = any(kw in query for kw in drum_keywords + genre_keywords)
        is_bass_query = any(kw in query for kw in bass_keywords) and not any(kw in query for kw in ["kit", "drum"])

        # Auto-detect category based on query if not specified
        if category is None:
            if is_drum_query and not is_bass_query:
                category = "drums"  # CRITICAL: Use drums category for actual drum racks!
            elif is_bass_query or any(kw in query for kw in synth_keywords):
                category = "instruments"
            elif any(kw in query for kw in effect_keywords):
                category = "audio_effects"
            else:
                category = "instruments"  # default

        # Load presets from MCP (with proper URIs)
        presets = load_presets_from_mcp(category)

        # Split query into words for flexible matching
        query_words = query.split()

        # For drum kit queries, prioritize .adg files (Drum Racks) and match genre/style
        drum_rack_matches = []  # Full drum rack kits (.adg files with "kit" in name)
        classic_matches = []    # Classic drum machine kits (808, 909, etc)
        other_matches = []

        for preset in presets:
            preset_name = preset.get("name", "").lower()
            preset_path = preset.get("path", "").lower()

            match_data = {
                "name": preset.get("name"),
                "path": preset.get("path"),
                "uri": preset.get("uri"),
            }

            # For drum queries, prioritize Drum Rack kits from the drums category
            if is_drum_query:
                is_drum_rack = preset_name.endswith('.adg')

                # Classic drum machines (808, 909, etc) - highest priority if specifically requested
                if is_drum_rack and any(kw in preset_name for kw in ["808", "909", "707", "606", "505"]):
                    if any(kw in query for kw in ["808", "909", "707", "606", "505"]):
                        classic_matches.insert(0, match_data)  # Put requested machine first
                    else:
                        classic_matches.append(match_data)

                # Genre/style kits - check if query words match kit name
                elif is_drum_rack and "kit" in preset_name:
                    # Check for genre matches
                    if any(word in preset_name for word in query_words) or any(genre in query for genre in genre_keywords if genre in preset_name):
                        drum_rack_matches.insert(0, match_data)
                    else:
                        drum_rack_matches.append(match_data)

                # Skip individual samples for kit queries
                elif not is_drum_rack:
                    continue
            else:
                # Non-drum queries: match by query words
                if any(word in preset_name or word in preset_path for word in query_words):
                    other_matches.append(match_data)

        # Return results in priority order
        if is_drum_query:
            # If classic drum machine requested (808, 909), put those first
            # Otherwise put genre matches first, then classic as fallback
            if any(kw in query for kw in ["808", "909", "707", "606", "505"]):
                matches = (classic_matches + drum_rack_matches)[:limit]
            else:
                matches = (drum_rack_matches + classic_matches)[:limit]
            hint = "Drum Rack kits. Use 'uri' with load_instrument_or_effect. MIDI notes: kick=36 (C1), snare=38 (D1), hat=42 (F#1)."
        else:
            matches = other_matches[:limit]
            hint = "Use the 'uri' field with load_instrument_or_effect."

        return {"query": query, "category": category, "matches": matches, "hint": hint}

    return None  # Not a discovery tool


def format_tools_for_prompt(tools: list) -> str:
    """Format MCP tools as a string for the LLM prompt (DEPRECATED - not used with progressive disclosure)"""
    tool_descriptions = []
    for tool in tools:
        desc = f"- **{tool.name}**: {tool.description or 'No description'}"
        if tool.inputSchema and "properties" in tool.inputSchema:
            params = []
            for param_name, param_info in tool.inputSchema["properties"].items():
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "")
                required = param_name in tool.inputSchema.get("required", [])
                req_str = " (required)" if required else " (optional)"
                params.append(f"    - {param_name}: {param_type}{req_str} - {param_desc}")
            if params:
                desc += "\n" + "\n".join(params)
        tool_descriptions.append(desc)
    return "\n".join(tool_descriptions)


# ============================================================================
# SOCKET MCP CLIENT (connects to AbletonMCP_Extended on port 9877)
# ============================================================================

import socket

class MCPClient:
    """Socket-based MCP Client that connects to AbletonMCP_Extended on port 9877"""

    def __init__(self, host: str = "localhost", port: int = 9877):
        self.host = host
        self.port = port
        self.tools = []

    def _send_command(self, cmd_type: str, params: dict = None) -> dict:
        """Send a command to AbletonMCP and return response."""
        if params is None:
            params = {}

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)

        try:
            sock.connect((self.host, self.port))
            command = {"type": cmd_type, "params": params}
            sock.sendall(json.dumps(command).encode('utf-8'))

            # Receive in chunks for large responses
            chunks = []
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
                try:
                    full_data = b''.join(chunks).decode('utf-8')
                    json.loads(full_data)
                    break
                except:
                    continue

            return json.loads(b''.join(chunks).decode('utf-8'))
        finally:
            sock.close()

    async def connect(self):
        """Connect to the AbletonMCP socket server"""
        print(f"Connecting to AbletonMCP on {self.host}:{self.port}...")

        # Test connection
        try:
            result = self._send_command("get_session_info")
            if result.get("status") == "success":
                print(f"Connected! Session has {result['result']['track_count']} tracks")
                # Define available tools (Arrangement View focused)
                self.tools = [
                    # Session info
                    "get_session_info", "set_tempo", "start_playback", "stop_playback",
                    # Track operations
                    "get_track_info", "create_midi_track", "set_track_name",
                    # Browser/presets
                    "get_browser_tree", "get_all_presets", "load_browser_item",
                    # Arrangement View clips (NOT Session View)
                    "create_arrangement_clip", "add_notes_to_arrangement_clip", "get_arrangement_clips",
                    # Device parameters
                    "get_device_parameters", "set_device_parameter"
                ]
                print(f"Available tools ({len(self.tools)}): {', '.join(self.tools[:5])}...")
            else:
                raise ConnectionError(f"Failed to connect: {result.get('message')}")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to AbletonMCP: {e}")

    async def call_tool(self, name: str, arguments: dict) -> Any:
        """Execute a tool call via socket"""
        print(f"Calling tool: {name} with args: {arguments}")

        # Map tool names to command types
        cmd_type = name

        # Map arguments to params format expected by AbletonMCP
        params = arguments

        # Special handling for load_browser_item (was load_instrument_or_effect)
        if name == "load_instrument_or_effect":
            cmd_type = "load_browser_item"
            # Handle different field names the model might use
            uri = arguments.get("uri") or arguments.get("preset_uri") or arguments.get("item_uri") or ""
            params = {
                "track_index": arguments.get("track_index", 0),
                "item_uri": uri
            }

        result = self._send_command(cmd_type, params)

        # Wrap result in a format similar to MCP response
        class MockContent:
            def __init__(self, text):
                self.text = text

        class MockResult:
            def __init__(self, result_dict):
                if result_dict.get("status") == "success":
                    self.content = [MockContent(json.dumps(result_dict.get("result", {})))]
                else:
                    self.content = [MockContent(f"Error: {result_dict.get('message', 'Unknown error')}")]

        return MockResult(result)

    async def cleanup(self):
        """Clean up resources (nothing to clean for socket client)"""
        pass


# ============================================================================
# MAIN BRIDGE
# ============================================================================

class MLXMCPBridge:
    """Main bridge connecting MLX inference to MCP tools"""

    def __init__(self, model_path: str = DEFAULT_MODEL):
        self.llm = MLXInference(model_path)
        self.mcp = MCPClient()
        self.conversation_history = []

    async def connect(self):
        """Connect to MCP server"""
        await self.mcp.connect()

    def build_prompt(self, user_message: str) -> str:
        """Build the full prompt with system message and conversation (no tools - progressive disclosure)"""
        # Progressive disclosure: Don't include tool definitions in prompt
        # Model discovers tools on-demand via list_tools and search_presets

        prompt = f"""<|im_start|>system
{SYSTEM_PROMPT}<|im_end|>
"""
        # Add conversation history
        for msg in self.conversation_history:
            role = msg["role"]
            content = msg["content"]
            prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"

        # Add current user message
        prompt += f"<|im_start|>user\n{user_message}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"

        return prompt

    async def execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a single tool call and return observation string"""
        name = tool_call.name
        arguments = tool_call.arguments

        try:
            # Check if it's a discovery tool (handle locally, no MCP call)
            discovery_result = handle_discovery_tool(name, arguments)

            if discovery_result is not None:
                result_text = json.dumps(discovery_result, indent=2)
                print(f"  ✓ {name}: (local) Success")
                return result_text
            else:
                # Regular MCP tool call
                result = await self.mcp.call_tool(name, arguments)
                if hasattr(result, 'content') and result.content:
                    if hasattr(result.content[0], 'text'):
                        result_text = result.content[0].text
                    else:
                        result_text = str(result.content)
                else:
                    result_text = str(result)
                print(f"  ✓ {name}: Success")
                return result_text

        except Exception as e:
            print(f"  ✗ {name}: {e}")
            return f"Error: {str(e)}"

    async def process_message(self, user_message: str, max_iterations: int = 20) -> str:
        """
        Process a user message using ReAct loop.

        Loops through Thought → Action → Observation cycles until:
        - Model outputs Final Answer
        - Max iterations reached
        - No action in response
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Build initial prompt
        prompt = self.build_prompt(user_message)

        # Track the full reasoning trace for this request
        reasoning_trace = []

        for iteration in range(max_iterations):
            print(f"\n{'='*40}")
            print(f"ReAct Iteration {iteration + 1}/{max_iterations}")
            print(f"{'='*40}")

            # Generate response
            print("Generating...")
            response = self.llm.generate_response(prompt, max_tokens=512)

            # Parse ReAct response
            step = parse_react_response(response)

            # Display thought (visible for evals)
            if step.thought:
                print(f"\n💭 Thought: {step.thought}")

            # Check for Final Answer
            if step.final_answer:
                print(f"\n✅ Final Answer: {step.final_answer}")
                reasoning_trace.append(f"Thought: {step.thought}\nFinal Answer: {step.final_answer}")

                # Save to conversation history
                full_response = "\n".join(reasoning_trace)
                self.conversation_history.append({"role": "assistant", "content": full_response})

                return step.final_answer

            # Execute action if present
            if step.action:
                print(f"\n🔧 Action: {step.action.name}({step.action.arguments})")

                observation = await self.execute_tool(step.action)
                print(f"\n👁 Observation: {observation[:500]}{'...' if len(observation) > 500 else ''}")

                # Record this step
                reasoning_trace.append(
                    f"Thought: {step.thought}\n"
                    f"Action: {step.action.name}({step.action.arguments})\n"
                    f"Observation: {observation}"
                )

                # Append observation to prompt for next iteration
                prompt += f"{response}\n\nObservation: {observation}\n\n"
                prompt += "Now continue with your next Thought and Action (or Final Answer if done):\n"

            else:
                # No action and no final answer - model might be confused
                print("\n⚠ No action or final answer found in response")
                print(f"Raw response: {response[:500]}")

                # Try to recover by asking for clarification
                if iteration < max_iterations - 1:
                    prompt += f"{response}\n\nPlease provide either an Action or a Final Answer.\n"
                else:
                    # Give up and return what we have
                    return f"I encountered an issue. Here's what I was thinking:\n{step.thought}"

        # Max iterations reached
        print(f"\n⚠ Max iterations ({max_iterations}) reached")
        return "I wasn't able to complete the task within the allowed steps. Please try a simpler request."

    async def chat_loop(self):
        """Interactive chat loop"""
        print("\n" + "="*60)
        print("MLX-MCP Bridge: Qwen3-4B → Ableton Live")
        print("="*60)
        print("\nType your commands or 'quit' to exit.")
        print("Make sure Ableton is running with AbletonMCP control surface enabled!\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                response = await self.process_message(user_input)
                print(f"\nAssistant: {response}")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except EOFError:
                print("\n\nEnd of input. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")

    async def cleanup(self):
        """Clean up resources"""
        await self.mcp.cleanup()


# ============================================================================
# ENTRY POINT
# ============================================================================

async def single_command(command: str, model_path: str = DEFAULT_MODEL):
    """Process a single command (non-interactive mode)"""
    bridge = MLXMCPBridge(model_path)

    try:
        await bridge.connect()
        response = await bridge.process_message(command)
        print(f"\nAssistant: {response}")
    finally:
        await bridge.cleanup()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="MLX-MCP Bridge: Qwen3-4B → Ableton Live")
    parser.add_argument("--command", "-c", type=str, help="Single command to execute (non-interactive)")
    parser.add_argument("--model", "-m", type=str, default=DEFAULT_MODEL, help="Model path")
    args = parser.parse_args()

    if args.command:
        # Non-interactive mode - single command
        await single_command(args.command, args.model)
    else:
        # Interactive mode
        bridge = MLXMCPBridge(args.model)
        try:
            await bridge.connect()
            await bridge.chat_loop()
        finally:
            await bridge.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
