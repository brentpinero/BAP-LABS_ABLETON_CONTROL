#!/usr/bin/env python3
"""
Auto-generate parameter maps for all Ableton stock plugins.

This script:
1. Connects to Ableton via MCP
2. Gets all stock audio effects, instruments, and MIDI effects from browser
3. Loads each plugin on a test track
4. Captures all parameters via get_device_parameters
5. Saves JSON maps to plugin_parameter_maps/ableton/

Usage:
    python generate_ableton_plugin_maps.py
"""

import socket
import json
import os
import time
import re

# MCP connection settings
HOST = "localhost"
PORT = 9877
OUTPUT_DIR = "plugin_parameter_maps/ableton"


def send_command(cmd_type: str, params: dict = None) -> dict:
    """Send a command to Ableton MCP and return response."""
    if params is None:
        params = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)

    try:
        sock.connect((HOST, PORT))
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
                break  # Valid JSON, done
            except:
                continue  # Keep receiving

        return json.loads(b''.join(chunks).decode('utf-8'))
    finally:
        sock.close()


def get_browser_items(category_type: str) -> list:
    """Get all BASE plugins from a browser category (no presets)."""
    result = send_command("get_all_presets", {"category_type": category_type, "max_depth": 1})

    if result.get("status") != "success":
        print(f"  Error getting {category_type}: {result.get('message')}")
        return []

    presets = result.get("result", {}).get("presets", [])

    # Filter to only base plugins (no "/" in path = top-level items)
    base_plugins = [p for p in presets if "/" not in p.get("path", "")]

    # Convert to expected format
    items = []
    for p in base_plugins:
        items.append({
            "name": p["name"],
            "uri": p["uri"],
            "is_loadable": True
        })

    return items


def sanitize_filename(name: str) -> str:
    """Convert plugin name to safe filename."""
    # Remove special characters, convert spaces to underscores
    safe = re.sub(r'[^\w\s-]', '', name.lower())
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe


def map_plugin(track_index: int, uri: str, plugin_name: str) -> dict:
    """Load a plugin and capture its parameters."""

    # Load the plugin
    load_result = send_command("load_browser_item", {
        "track_index": track_index,
        "item_uri": uri
    })

    if load_result.get("status") != "success":
        return {"error": f"Failed to load: {load_result.get('message')}"}

    # Debug: show what load returned
    print(f"\n    Load result: {load_result.get('result', {})}", end="")

    # Longer delay to let plugin fully initialize in Ableton
    time.sleep(1.5)

    # Get device parameters (device is at index 0 after loading)
    # But we need to find the device index - it might not be 0 if there are other devices
    track_result = send_command("get_track_info", {"track_index": track_index})
    if track_result.get("status") != "success":
        return {"error": "Failed to get track info"}

    devices = track_result.get("result", {}).get("devices", [])
    print(f"\n    Track {track_index} has {len(devices)} devices", end="")
    if not devices:
        return {"error": "No devices found after loading"}

    # Find the device we just loaded (should be the last one)
    device_index = len(devices) - 1

    # Get parameters
    params_result = send_command("get_device_parameters", {
        "track_index": track_index,
        "device_index": device_index
    })

    if params_result.get("status") != "success":
        return {"error": f"Failed to get params: {params_result.get('message')}"}

    return params_result.get("result", {})


def delete_all_devices(track_index: int):
    """Delete all devices from a track to prepare for next plugin."""
    # We don't have a delete device command yet, so we'll just work with what we have
    # The track will accumulate devices, but we'll always get the last one
    pass


def main():
    print("=" * 60)
    print("  ABLETON STOCK PLUGIN PARAMETER MAPPER")
    print("=" * 60)
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Test connection
    print("Testing MCP connection...")
    session = send_command("get_session_info")
    if session.get("status") != "success":
        print("ERROR: Cannot connect to Ableton MCP. Is Ableton running?")
        return
    print(f"Connected! Session has {session['result']['track_count']} tracks")
    print()

    # Collect all plugins to map
    all_plugins = []

    # Get Audio Effects
    print("Fetching Audio Effects...")
    audio_effects = get_browser_items("audio_effects")
    for item in audio_effects:
        if item.get("is_loadable"):
            all_plugins.append({
                "name": item["name"],
                "uri": item["uri"],
                "type": "audio_effect"
            })
    print(f"  Found {len([p for p in all_plugins if p['type'] == 'audio_effect'])} audio effects")

    # Get Instruments
    print("Fetching Instruments...")
    instruments = get_browser_items("instruments")
    for item in instruments:
        if item.get("is_loadable"):
            all_plugins.append({
                "name": item["name"],
                "uri": item["uri"],
                "type": "instrument"
            })
    print(f"  Found {len([p for p in all_plugins if p['type'] == 'instrument'])} instruments")

    # Get MIDI Effects
    print("Fetching MIDI Effects...")
    midi_effects = get_browser_items("midi_effects")
    for item in midi_effects:
        if item.get("is_loadable"):
            all_plugins.append({
                "name": item["name"],
                "uri": item["uri"],
                "type": "midi_effect"
            })
    print(f"  Found {len([p for p in all_plugins if p['type'] == 'midi_effect'])} MIDI effects")

    print()
    print(f"Total plugins to map: {len(all_plugins)}")
    print("=" * 60)
    print()

    # Map each plugin - create a NEW TRACK for each one
    successful = 0
    failed = 0
    created_tracks = []

    for i, plugin in enumerate(all_plugins):
        name = plugin["name"]
        uri = plugin["uri"]
        ptype = plugin["type"]

        print(f"[{i+1}/{len(all_plugins)}] Mapping {name}...", end=" ", flush=True)

        try:
            # Create a fresh track for this plugin
            track_result = send_command("create_midi_track", {"index": -1})
            if track_result.get("status") != "success":
                print(f"FAILED: Could not create track")
                failed += 1
                continue

            track_index = track_result["result"]["index"]
            created_tracks.append(track_index)

            # Map the plugin on this fresh track
            result = map_plugin(track_index, uri, name)

            if "error" in result:
                print(f"FAILED: {result['error']}")
                failed += 1
                continue

            # Save to JSON
            filename = f"ableton_{sanitize_filename(name)}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)

            # Add metadata
            output = {
                "plugin": name,
                "type": ptype,
                "uri": uri,
                "class_name": result.get("device_class", result.get("class_name", "")),
                "parameter_count": result.get("parameter_count", 0),
                "parameters": result.get("parameters", [])
            }

            with open(filepath, "w") as f:
                json.dump(output, f, indent=2)

            print(f"OK ({result.get('parameter_count', 0)} params) [track {track_index}]")
            successful += 1

        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

        # 2 second delay between plugins to let Ableton settle
        time.sleep(2.0)

    print()
    print("=" * 60)
    print(f"COMPLETE: {successful} successful, {failed} failed")
    print(f"Maps saved to: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
