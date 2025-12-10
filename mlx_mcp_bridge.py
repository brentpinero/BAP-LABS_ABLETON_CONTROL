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
from typing import Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# MLX imports for local inference
from mlx_lm import load, generate


# ============================================================================
# CONFIGURATION
# ============================================================================

# Default Qwen model - can be overridden
DEFAULT_MODEL = "mlx-community/Qwen3-4B-4bit"

# System prompt for the music production collaborator
SYSTEM_PROMPT = """You are a music production AI collaborator with direct control over Ableton Live.

You can execute actions by calling tools. When the user asks you to do something in Ableton,
use the available tools to accomplish it.

IMPORTANT: When you want to call a tool, output your response in this exact format:
<tool_call>
{"name": "tool_name", "arguments": {"param1": "value1", "param2": "value2"}}
</tool_call>

You can call multiple tools by including multiple <tool_call> blocks.

After tool calls, explain what you did to the user.

Available tools will be provided in each conversation.
"""


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
        """Generate a response from the model"""
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=False
        )
        return response


# ============================================================================
# TOOL CALL PARSER
# ============================================================================

def parse_tool_calls(response: str) -> list[dict]:
    """
    Extract tool calls from model response.

    Looks for patterns like:
    <tool_call>
    {"name": "create_midi_track", "arguments": {"index": -1}}
    </tool_call>
    """
    tool_calls = []

    # Find all tool_call blocks
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


def format_tools_for_prompt(tools: list) -> str:
    """Format MCP tools as a string for the LLM prompt"""
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
# MCP CLIENT
# ============================================================================

class MCPClient:
    """MCP Client that connects to ableton-mcp server"""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = []

    async def connect(self):
        """Connect to the ableton-mcp server"""
        print("Connecting to ableton-mcp server...")

        # Use uvx to run ableton-mcp
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

        # Get available tools
        response = await self.session.list_tools()
        self.tools = response.tools

        print(f"Connected! Available tools ({len(self.tools)}):")
        for tool in self.tools:
            print(f"  - {tool.name}")

    async def call_tool(self, name: str, arguments: dict) -> Any:
        """Execute a tool call"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        print(f"Calling tool: {name} with args: {arguments}")
        result = await self.session.call_tool(name, arguments)
        return result

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


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
        """Build the full prompt with system message, tools, and conversation"""
        tools_str = format_tools_for_prompt(self.mcp.tools)

        prompt = f"""<|im_start|>system
{SYSTEM_PROMPT}

## Available Tools:
{tools_str}
<|im_end|>
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

    async def process_message(self, user_message: str) -> str:
        """Process a user message and execute any tool calls"""
        # Build prompt
        prompt = self.build_prompt(user_message)

        # Generate response
        print("\nThinking...")
        response = self.llm.generate_response(prompt, max_tokens=1024)
        print(f"\nModel response:\n{response}\n")

        # Parse and execute tool calls
        tool_calls = parse_tool_calls(response)

        tool_results = []
        if tool_calls:
            print(f"\nExecuting {len(tool_calls)} tool call(s)...")
            for tc in tool_calls:
                try:
                    result = await self.mcp.call_tool(tc["name"], tc["arguments"])
                    # Extract actual text content from result
                    if hasattr(result, 'content') and result.content:
                        if hasattr(result.content[0], 'text'):
                            result_text = result.content[0].text
                        else:
                            result_text = str(result.content)
                    else:
                        result_text = str(result)
                    tool_results.append({
                        "tool": tc["name"],
                        "success": True,
                        "result": result_text
                    })
                    print(f"  ✓ {tc['name']}: Success")
                    print(f"    Result: {result_text[:500]}...")
                except Exception as e:
                    tool_results.append({
                        "tool": tc["name"],
                        "success": False,
                        "error": str(e)
                    })
                    print(f"  ✗ {tc['name']}: {e}")

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Create assistant response with tool results if any
        if tool_results:
            results_summary = "\n".join([
                f"- {r['tool']}: {'Success' if r['success'] else 'Failed - ' + r.get('error', 'Unknown error')}"
                for r in tool_results
            ])
            full_response = f"{response}\n\n[Tool Results]\n{results_summary}"
        else:
            full_response = response

        self.conversation_history.append({"role": "assistant", "content": full_response})

        return full_response

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
