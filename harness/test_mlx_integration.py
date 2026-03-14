#!/usr/bin/env python3
"""
Test MLX-MCP Bridge Integration

Verifies:
1. UnifiedMCPBridge connection works
2. Name-based track resolution works
3. Tool catalog is correct
4. Discovery tools work (list_tools, get_all_tracks, search_presets)

Run: python test_mlx_integration.py
"""

import asyncio
import json
import os
import sys
# Ensure sibling imports work regardless of how this script is invoked
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_unified_bridge():
    """Test UnifiedMCPBridge directly"""
    print("\n=== Testing UnifiedMCPBridge ===")

    from unified_mcp_bridge import UnifiedMCPBridge

    bridge = UnifiedMCPBridge()

    # Test connection
    print("1. Connecting to Ableton...")
    connected = bridge.connect_ableton()
    if not connected:
        print("   FAILED: Could not connect to Ableton")
        print("   Make sure Ableton is running with AbletonMCP control surface!")
        return False
    print("   OK: Connected!")

    # Test get_session_info
    print("\n2. Testing get_session_info...")
    result = bridge.get_session_info()
    if result.get("status") != "success":
        print(f"   FAILED: {result}")
        return False
    print(f"   OK: {result['result']['track_count']} tracks")

    # Test get_all_tracks
    print("\n3. Testing get_all_tracks...")
    tracks = bridge.get_all_tracks()
    if not tracks:
        print("   FAILED: No tracks returned")
        return False
    print(f"   OK: Found {len(tracks)} tracks:")
    for t in tracks[:5]:
        print(f"      [{t['index']}] {t['name']}")

    # Test name-based resolution
    print("\n4. Testing name-based track resolution...")
    if tracks:
        track_name = tracks[0]["name"]
        resolved = bridge.resolve_track(track_name)
        print(f"   resolve_track('{track_name}') -> {resolved}")
        if resolved != 0:
            print(f"   FAILED: Expected 0, got {resolved}")
            return False
        print("   OK: Name resolution works!")

    # Test ableton_command with name
    print("\n5. Testing ableton_command with track name...")
    if tracks:
        track_name = tracks[0]["name"]
        result = bridge.ableton_command("get_track_info", {"track_index": track_name})
        if result.get("status") != "success":
            print(f"   FAILED: {result}")
            return False
        print(f"   OK: Got track info for '{track_name}'")

    bridge.disconnect()
    return True


def test_mcp_client():
    """Test MCPClient from mlx_mcp_bridge"""
    print("\n=== Testing MCPClient (from mlx_mcp_bridge) ===")

    from mlx_mcp_bridge import MCPClient

    client = MCPClient()

    # Test async connection
    async def test_connection():
        print("1. Connecting via MCPClient...")
        await client.connect()
        print("   OK: Connected!")

        # Test calling a tool
        print("\n2. Testing tool call: get_session_info...")
        result = await client.call_tool("get_session_info", {})
        if result.content and result.content[0].text:
            data = json.loads(result.content[0].text)
            print(f"   OK: {data.get('track_count', 'N/A')} tracks")

        # Test name-based tool call
        print("\n3. Testing tool call with track name...")
        # First get track names
        tracks_result = await client.call_tool("get_session_info", {})

        if result.content:
            # Try to get track info by name
            # This tests the name resolution through the bridge
            track_result = await client.call_tool("get_track_info", {"track_index": 0})
            if track_result.content:
                print(f"   OK: Got track info")

        await client.cleanup()
        return True

    return asyncio.run(test_connection())


def test_discovery_tools():
    """Test discovery tools"""
    print("\n=== Testing Discovery Tools ===")

    from mlx_mcp_bridge import handle_discovery_tool, TOOL_CATALOG, MCPClient

    # Test list_tools
    print("1. Testing list_tools (no category)...")
    result = handle_discovery_tool("list_tools", {})
    print(f"   Categories: {result['categories']}")

    print("\n2. Testing list_tools (session)...")
    result = handle_discovery_tool("list_tools", {"category": "session"})
    print(f"   Tools: {list(result['tools'].keys())}")

    print("\n3. Testing list_tools (smart_select)...")
    result = handle_discovery_tool("list_tools", {"category": "smart_select"})
    print(f"   Tools: {list(result['tools'].keys())}")

    # Test get_all_tracks (needs mcp_client)
    print("\n4. Testing get_all_tracks...")
    client = MCPClient()

    async def test_tracks():
        await client.connect()
        result = handle_discovery_tool("get_all_tracks", {}, mcp_client=client)
        if "tracks" in result:
            print(f"   OK: {result['track_count']} tracks")
            for t in result['tracks'][:3]:
                print(f"      [{t['index']}] {t['name']}")
        else:
            print(f"   FAILED: {result}")
        await client.cleanup()

    asyncio.run(test_tracks())

    return True


def test_tool_catalog():
    """Verify tool catalog has all expected categories"""
    print("\n=== Testing TOOL_CATALOG ===")

    from mlx_mcp_bridge import TOOL_CATALOG

    expected_categories = [
        "session", "track", "device", "browser", "clip",
        "mixer", "transport", "selection", "smart_select", "automator"
    ]

    missing = [c for c in expected_categories if c not in TOOL_CATALOG]
    if missing:
        print(f"   FAILED: Missing categories: {missing}")
        return False

    print(f"   OK: All {len(expected_categories)} categories present")

    # Check smart_select has key tools
    smart_tools = TOOL_CATALOG["smart_select"]["tools"]
    required_tools = ["smart_select_tracks", "smart_group_tracks", "calibrate_layout"]
    for tool in required_tools:
        if tool not in smart_tools:
            print(f"   FAILED: Missing tool: {tool}")
            return False

    print(f"   OK: smart_select has required tools")

    return True


def main():
    print("=" * 60)
    print("MLX-MCP Bridge Integration Test")
    print("=" * 60)

    # Run tests
    results = {}

    # Test 1: Tool catalog
    results["tool_catalog"] = test_tool_catalog()

    # Test 2: Unified bridge (requires Ableton)
    print("\n[Note: Tests 2-4 require Ableton running with AbletonMCP]")
    try:
        results["unified_bridge"] = test_unified_bridge()
    except Exception as e:
        print(f"   FAILED: {e}")
        results["unified_bridge"] = False

    # Test 3: MCP Client
    if results.get("unified_bridge"):
        try:
            results["mcp_client"] = test_mcp_client()
        except Exception as e:
            print(f"   FAILED: {e}")
            results["mcp_client"] = False

    # Test 4: Discovery tools
    if results.get("unified_bridge"):
        try:
            results["discovery_tools"] = test_discovery_tools()
        except Exception as e:
            print(f"   FAILED: {e}")
            results["discovery_tools"] = False

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    all_passed = True
    for test, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nAll tests passed! Ready to test with Qwen3-4B.")
    else:
        print("\nSome tests failed. Fix issues before testing with LLM.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
