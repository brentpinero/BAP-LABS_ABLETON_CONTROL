#!/usr/bin/env python3
"""
Mix Assistant Bridge - Integrated MLX + Mix Analysis + MCP

Combines:
- Real-time audio analysis from Mix Analysis Hub (M4L)
- Qwen3-4B inference via MLX
- Ableton control via MCP

Architecture:
    M4L (Audio Analysis) → OSC → Mix Analysis Bridge
                                       ↓
    User Query + Audio Context → Qwen3-4B (MLX) → Tool Calls → MCP → Ableton

Usage:
    python mix_assistant_bridge.py

Author: BAP Labs
"""

import asyncio
import json
import re
import sys
import time
from typing import Optional, Any
from contextlib import AsyncExitStack
from threading import Thread

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mlx_lm import load, generate


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_MODEL = "mlx-community/Qwen3-4B-4bit"
OSC_PORT = 9880
CONTEXT_WINDOW_BARS = 32  # 16 bars before + 16 bars after

SYSTEM_PROMPT = """You are an expert audio engineer and music production AI assistant with:
1. Real-time audio analysis of the user's mix (spectrum, levels, stereo width)
2. Direct control over Ableton Live via tools

## Your Capabilities:
- **Analyze**: You receive real-time audio analysis data showing levels, stereo correlation, and frequency balance
- **Reason**: Use audio engineering knowledge to identify issues and suggest improvements
- **Act**: Execute changes in Ableton using the available tools

## Audio Analysis Context:
You will receive a "Mix Context" section showing:
- RMS levels (L/R in dB)
- Peak levels (L/R in dB)
- Stereo correlation (-1 to +1, where 1 = mono, 0 = uncorrelated, -1 = out of phase)
- Stereo width (0 = mono, 1 = full stereo)
- Transport state (playing, BPM, current bar)

## How to Respond:
1. First, analyze the audio context to understand the current mix state
2. If the user asks about their mix, reference the actual data
3. When suggesting changes, use the tools to implement them
4. Explain your reasoning based on audio engineering principles

## Tool Call Format:
<tool_call>
{"name": "tool_name", "arguments": {"param1": "value1"}}
</tool_call>

Be concise but informative. Reference actual values from the mix context.
"""


# ============================================================================
# BAR ANALYSIS CACHE
# ============================================================================

@dataclass
class BarAnalysis:
    """Analysis snapshot for a single bar."""
    bar_number: int
    timestamp: float
    rms_l: float = -100.0
    rms_r: float = -100.0
    peak_l: float = -100.0
    peak_r: float = -100.0
    mid_energy: float = 0.0
    side_energy: float = 0.0
    correlation: float = 0.0

    def to_dict(self) -> dict:
        width = self.side_energy / (self.mid_energy + self.side_energy + 0.0001)
        return {
            "bar": self.bar_number,
            "rms": round((self.rms_l + self.rms_r) / 2, 1),
            "peak": round(max(self.peak_l, self.peak_r), 1),
            "corr": round(self.correlation, 2),
            "width": round(width, 2)
        }


class BarCache:
    """LRU cache for bar analysis."""
    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self.cache: Dict[int, BarAnalysis] = {}
        self.access_order: deque = deque()

    def get(self, bar: int) -> Optional[BarAnalysis]:
        if bar in self.cache:
            return self.cache[bar]
        return None

    def put(self, bar: int, analysis: BarAnalysis):
        if bar in self.cache:
            return  # Don't overwrite
        if len(self.cache) >= self.max_size:
            oldest = self.access_order.popleft()
            if oldest in self.cache:
                del self.cache[oldest]
        self.cache[bar] = analysis
        self.access_order.append(bar)

    def get_range(self, start: int, end: int) -> List[dict]:
        """Get analysis for a range of bars."""
        result = []
        for b in range(start, end):
            analysis = self.get(b)
            if analysis:
                result.append(analysis.to_dict())
            else:
                result.append({"bar": b, "status": "not_analyzed"})
        return result


# ============================================================================
# MIX ANALYSIS STATE (receives OSC from M4L)
# ============================================================================

class MixAnalysisState:
    """Holds real-time audio analysis data from M4L device."""

    def __init__(self):
        # Current frame values
        self.rms_l = -100.0
        self.rms_r = -100.0
        self.peak_l = -100.0
        self.peak_r = -100.0
        self.mid_energy = 0.0
        self.side_energy = 0.0
        self.correlation = 0.0

        # Transport state
        self.bpm = 120.0
        self.current_bar = 0
        self.current_beat = 0.0
        self.song_length_bars = 0
        self.time_sig_num = 4
        self.time_sig_den = 4
        self.is_playing = False

        # Tracking
        self.last_update = 0.0
        self.messages_received = 0
        self.last_cached_bar = -1

        # Bar cache for 32-bar context window
        self.bar_cache = BarCache()

    def handle_levels(self, address: str, *args):
        """Handle /mix/levels OSC message."""
        if len(args) >= 6:
            self.rms_l = args[0]
            self.rms_r = args[1]
            self.peak_l = args[2]
            self.peak_r = args[3]
            self.mid_energy = args[4]
            self.side_energy = args[5]
            self.last_update = time.time()
            self.messages_received += 1

    def handle_stereo(self, address: str, *args):
        """Handle /mix/stereo OSC message."""
        if len(args) >= 3:
            self.correlation = args[0]
            self.mid_energy = args[1]
            self.side_energy = args[2]
            self.last_update = time.time()
            self.messages_received += 1

    def handle_transport(self, address: str, *args):
        """Handle /mix/transport OSC message.

        Args: playing, bpm, bar, beat, song_length_bars, sig_num, sig_den
        """
        if len(args) >= 5:
            self.is_playing = bool(args[0])
            self.bpm = float(args[1])
            new_bar = int(args[2])
            self.current_beat = float(args[3])
            self.song_length_bars = int(args[4])

            if len(args) >= 7:
                self.time_sig_num = int(args[5])
                self.time_sig_den = int(args[6])

            # Cache analysis when bar changes
            if new_bar != self.last_cached_bar and self.is_playing:
                self._cache_current_bar(self.last_cached_bar)
                self.last_cached_bar = new_bar

            self.current_bar = new_bar
            self.last_update = time.time()
            self.messages_received += 1

    def _cache_current_bar(self, bar_num: int):
        """Cache the current analysis for a bar."""
        if bar_num < 0:
            return

        analysis = BarAnalysis(
            bar_number=bar_num,
            timestamp=time.time(),
            rms_l=self.rms_l,
            rms_r=self.rms_r,
            peak_l=self.peak_l,
            peak_r=self.peak_r,
            mid_energy=self.mid_energy,
            side_energy=self.side_energy,
            correlation=self.correlation
        )
        self.bar_cache.put(bar_num, analysis)

    def calculate_width(self) -> float:
        """Calculate stereo width from mid/side."""
        total = self.mid_energy + self.side_energy
        if total < 0.0001:
            return 0.0
        return self.side_energy / total

    def get_32bar_context(self) -> str:
        """Get 32-bar context window as string."""
        start_bar = max(0, self.current_bar - 16)
        end_bar = min(self.song_length_bars, self.current_bar + 16)

        bars = self.bar_cache.get_range(start_bar, end_bar)
        analyzed = [b for b in bars if "status" not in b]

        if not analyzed:
            return f"[No bar analysis cached yet - bars {start_bar}-{end_bar}]"

        # Summarize the context
        summary = f"**32-Bar Context** (bars {start_bar}-{end_bar}, {len(analyzed)} analyzed):\n"

        # Group into 8-bar sections
        for section_start in range(start_bar, end_bar, 8):
            section_end = min(section_start + 8, end_bar)
            section_bars = [b for b in analyzed if section_start <= b["bar"] < section_end]

            if section_bars:
                avg_rms = sum(b["rms"] for b in section_bars) / len(section_bars)
                avg_corr = sum(b["corr"] for b in section_bars) / len(section_bars)
                summary += f"- Bars {section_start}-{section_end}: avg RMS={avg_rms:.1f}dB, corr={avg_corr:.2f}\n"

        return summary

    def get_context_string(self) -> str:
        """Get formatted context string for LLM prompt."""
        age = time.time() - self.last_update if self.last_update > 0 else float('inf')

        if self.messages_received == 0:
            return "[Mix Analysis Hub not connected - no audio data available]"

        if age > 5.0:
            freshness = f"(stale - {age:.1f}s old)"
        else:
            freshness = "(live)"

        width = self.calculate_width()
        width_desc = "mono" if width < 0.1 else "narrow" if width < 0.3 else "balanced" if width < 0.6 else "wide"
        corr_desc = "out of phase" if self.correlation < -0.3 else "uncorrelated" if self.correlation < 0.3 else "correlated" if self.correlation < 0.7 else "mono-ish"

        context = f"""## Mix Context {freshness}
**Current Position:** Bar {self.current_bar} of {self.song_length_bars} | {'▶ Playing' if self.is_playing else '⏸ Stopped'} at {self.bpm:.1f} BPM

**Current Levels:**
- RMS: L={self.rms_l:.1f}dB, R={self.rms_r:.1f}dB
- Peak: L={self.peak_l:.1f}dB, R={self.peak_r:.1f}dB

**Stereo Field:**
- Correlation: {self.correlation:.2f} ({corr_desc})
- Width: {width:.2f} ({width_desc})

**Cached Bars:** {len(self.bar_cache.cache)} bars analyzed
"""
        # Add 32-bar context if we have cached data
        if len(self.bar_cache.cache) > 0:
            context += "\n" + self.get_32bar_context()

        return context


# ============================================================================
# MLX INFERENCE
# ============================================================================

class MLXInference:
    """Handles local Qwen inference via MLX."""

    def __init__(self, model_path: str = DEFAULT_MODEL):
        print(f"Loading model: {model_path}")
        self.model, self.tokenizer = load(model_path)
        print("Model loaded!")

    def generate_response(self, prompt: str, max_tokens: int = 512) -> str:
        return generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=False
        )


# ============================================================================
# MCP CLIENT
# ============================================================================

class MCPClient:
    """MCP Client for Ableton control."""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = []

    async def connect(self):
        """Connect to ableton-mcp."""
        print("Connecting to ableton-mcp...")

        server_params = StdioServerParameters(
            command="uvx",
            args=["ableton-mcp"],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()
        response = await self.session.list_tools()
        self.tools = response.tools

        print(f"Connected! {len(self.tools)} tools available")

    async def call_tool(self, name: str, arguments: dict) -> Any:
        if not self.session:
            raise RuntimeError("Not connected")
        result = await self.session.call_tool(name, arguments)
        return result

    async def cleanup(self):
        await self.exit_stack.aclose()


# ============================================================================
# TOOL PARSING
# ============================================================================

def parse_tool_calls(response: str) -> list[dict]:
    """Extract tool calls from model response."""
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
        except json.JSONDecodeError:
            pass

    return tool_calls


def format_tools_for_prompt(tools: list) -> str:
    """Format MCP tools for LLM prompt."""
    lines = []
    for tool in tools:
        desc = f"- **{tool.name}**: {tool.description or 'No description'}"
        lines.append(desc)
    return "\n".join(lines)


# ============================================================================
# INTEGRATED BRIDGE
# ============================================================================

class MixAssistantBridge:
    """
    Integrated bridge: Mix Analysis + MLX + MCP.

    Receives audio analysis from M4L, includes it in LLM context,
    and executes tool calls via MCP.
    """

    def __init__(self, model_path: str = DEFAULT_MODEL):
        self.mix_state = MixAnalysisState()
        self.llm = MLXInference(model_path)
        self.mcp = MCPClient()
        self.conversation_history = []
        self.osc_transport = None

    async def start_osc_server(self):
        """Start OSC server to receive M4L data."""
        dispatcher = Dispatcher()
        dispatcher.map("/mix/levels", self.mix_state.handle_levels)
        dispatcher.map("/mix/stereo", self.mix_state.handle_stereo)
        dispatcher.map("/mix/transport", self.mix_state.handle_transport)

        server = AsyncIOOSCUDPServer(
            ("127.0.0.1", OSC_PORT),
            dispatcher,
            asyncio.get_event_loop()
        )
        self.osc_transport, _ = await server.create_serve_endpoint()
        print(f"OSC server listening on port {OSC_PORT}")

    async def connect(self):
        """Connect all services."""
        await self.start_osc_server()
        await self.mcp.connect()

    def build_prompt(self, user_message: str) -> str:
        """Build prompt with system message, mix context, tools, and history."""
        tools_str = format_tools_for_prompt(self.mcp.tools)
        mix_context = self.mix_state.get_context_string()

        prompt = f"""<|im_start|>system
{SYSTEM_PROMPT}

{mix_context}

## Available Tools:
{tools_str}
<|im_end|>
"""
        for msg in self.conversation_history:
            prompt += f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>\n"

        prompt += f"<|im_start|>user\n{user_message}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"

        return prompt

    async def process_message(self, user_message: str) -> str:
        """Process user message with mix context and execute tools."""
        prompt = self.build_prompt(user_message)

        print("\nThinking...")
        response = self.llm.generate_response(prompt, max_tokens=1024)
        print(f"\nResponse:\n{response}\n")

        # Execute tool calls
        tool_calls = parse_tool_calls(response)
        tool_results = []

        if tool_calls:
            print(f"\nExecuting {len(tool_calls)} tool(s)...")
            for tc in tool_calls:
                try:
                    result = await self.mcp.call_tool(tc["name"], tc["arguments"])
                    result_text = str(result.content[0].text if hasattr(result, 'content') else result)
                    tool_results.append({"tool": tc["name"], "success": True, "result": result_text})
                    print(f"  ✓ {tc['name']}")
                except Exception as e:
                    tool_results.append({"tool": tc["name"], "success": False, "error": str(e)})
                    print(f"  ✗ {tc['name']}: {e}")

        # Update history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    async def chat_loop(self):
        """Interactive chat loop."""
        print("\n" + "=" * 60)
        print("MIX ASSISTANT - Real-Time Audio Analysis + Ableton Control")
        print("=" * 60)
        print("\nLoad 'Mix Analysis Hub.maxpat' in Max/Live for audio analysis")
        print("Commands: 'status', 'bars', 'quit'\n")

        # Status printer task
        async def print_status():
            last_bar = -1
            while True:
                await asyncio.sleep(5)
                if self.mix_state.messages_received > 0:
                    bar = self.mix_state.current_bar
                    cached = len(self.mix_state.bar_cache.cache)
                    if bar != last_bar:
                        print(f"\n[TRANSPORT] Bar {bar} | {self.mix_state.bpm:.0f} BPM | "
                              f"{'▶' if self.mix_state.is_playing else '⏸'} | "
                              f"{cached} bars cached")
                        last_bar = bar

        status_task = asyncio.create_task(print_status())

        try:
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input("\nYou: ").strip()
                )

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                if user_input.lower() == 'status':
                    print(self.mix_state.get_context_string())
                    continue

                if user_input.lower() == 'bars':
                    print(self.mix_state.get_32bar_context())
                    continue

                if not user_input:
                    continue

                response = await self.process_message(user_input)
                print(f"\nAssistant: {response}")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
        finally:
            status_task.cancel()

    async def cleanup(self):
        """Clean up resources."""
        if self.osc_transport:
            self.osc_transport.close()
        await self.mcp.cleanup()


# ============================================================================
# ENTRY POINT
# ============================================================================

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Mix Assistant: Audio Analysis + MLX + MCP")
    parser.add_argument("--model", "-m", type=str, default=DEFAULT_MODEL, help="Model path")
    parser.add_argument("--command", "-c", type=str, help="Single command (non-interactive)")
    args = parser.parse_args()

    bridge = MixAssistantBridge(args.model)

    try:
        await bridge.connect()

        if args.command:
            response = await bridge.process_message(args.command)
            print(f"\nAssistant: {response}")
        else:
            await bridge.chat_loop()
    finally:
        await bridge.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
