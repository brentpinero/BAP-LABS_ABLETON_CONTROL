"""
Test script to verify MCP connection to Ableton

Run this AFTER:
1. Ableton is open
2. AbletonMCP is selected as Control Surface in Settings → Link, Tempo & MIDI

Usage:
    python test_mcp_connection.py
"""

import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_connection():
    """Test connection to ableton-mcp and list available tools"""
    print("Testing MCP connection to Ableton...")
    print("-" * 50)

    exit_stack = AsyncExitStack()

    try:
        # Connect to ableton-mcp server
        server_params = StdioServerParameters(
            command="uvx",
            args=["ableton-mcp"],
            env=None
        )

        print("Starting ableton-mcp server...")
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport

        print("Creating client session...")
        session = await exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )

        print("Initializing session...")
        await session.initialize()

        # List available tools
        print("\nGetting available tools...")
        response = await session.list_tools()

        print(f"\n{'='*50}")
        print(f"SUCCESS! Connected to ableton-mcp")
        print(f"{'='*50}")
        print(f"\nAvailable tools ({len(response.tools)}):\n")

        for tool in response.tools:
            print(f"  {tool.name}")
            if tool.description:
                # Truncate long descriptions
                desc = tool.description[:80] + "..." if len(tool.description) > 80 else tool.description
                print(f"    └─ {desc}")

        # Try to get session info (tests actual Ableton connection)
        print(f"\n{'='*50}")
        print("Testing Ableton connection...")
        print(f"{'='*50}\n")

        try:
            result = await session.call_tool("get_session_info", {})
            print("Session info retrieved successfully!")
            print(f"Result: {result.content[:500] if hasattr(result, 'content') else result}...")
        except Exception as e:
            print(f"Could not get session info: {e}")
            print("\nMake sure:")
            print("  1. Ableton Live is running")
            print("  2. Go to Settings → Link, Tempo & MIDI")
            print("  3. Set Control Surface to 'AbletonMCP'")
            print("  4. Set Input and Output to 'None'")

    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure 'uv' is installed: brew install uv")
        print("  2. Try running: uvx ableton-mcp")
        print("  3. Check if Ableton is running with AbletonMCP enabled")

    finally:
        await exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(test_connection())
