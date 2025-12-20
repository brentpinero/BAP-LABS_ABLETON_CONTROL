#!/usr/bin/env python3
"""
Fast Ableton preset parser - reads directly from XML files.

Parses all Ableton stock plugin presets from disk without loading in Ableton.
Processes thousands of presets in minutes instead of hours.

Usage:
    python parse_ableton_presets_xml.py
"""

import os
import gzip
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict

# Ableton Core Library path
CORE_LIBRARY = "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/Core Library"
OUTPUT_DIR = "plugin_parameter_maps/ableton/presets_from_xml"
BASE_MAPS_DIR = "plugin_parameter_maps/ableton"


def load_base_plugin_maps():
    """Load the base plugin parameter maps to get name->index mappings."""
    maps = {}

    # XML class name -> MCP class name mapping (for versioned classes)
    xml_to_mcp_class = {
        "AutoFilter": "AutoFilter2",
        "AutoPan": "AutoPan2",
        "Chorus": "Chorus2",
        "Compressor": "Compressor2",
        "Delay": "Delay",
        "Echo": "Echo",
        "Eq8": "Eq8",
        "Flanger": "PhaserFlanger",  # Combined in Live 12
        "FrequencyShifter": "Shifter",  # Renamed in Live 12
        "Gate": "Gate",
        "GlueCompressor": "GlueCompressor",
        "Limiter": "Limiter",
        "MultibandDynamics": "MultibandDynamics",
        "Overdrive": "Overdrive",
        "Phaser": "PhaserFlanger",  # Combined in Live 12
        "PhaserNew": "PhaserFlanger",
        "Redux": "Redux",
        "Redux2": "Redux2",
        "Resonator": "Resonator",
        "Reverb": "Reverb",
        "Saturator": "Saturator",
        "Vinyl": "Vinyl",
        "Vocoder": "Vocoder",
        # Racks - GroupDevicePreset maps to these based on type
        "GroupDevicePreset": "AudioEffectGroupDevice",  # Most common
        # Instruments
        "Operator": "Operator",
        "InstrumentVector": "InstrumentVector",  # Wavetable
        "StringStudio": "StringStudio",  # Tension
        "InstrumentMeld": "InstrumentMeld",  # Meld
        "MultiSampler": "MultiSampler",  # Sampler
        "OriginalSimpler": "OriginalSimpler",  # Simpler
    }

    for filename in os.listdir(BASE_MAPS_DIR):
        if filename.startswith("ableton_") and filename.endswith(".json") and "preset" not in filename:
            filepath = os.path.join(BASE_MAPS_DIR, filename)
            with open(filepath, "r") as f:
                data = json.load(f)
                # Key by class_name (e.g., "Compressor2")
                class_name = data.get("class_name", "")
                if class_name:
                    # Build name -> index mapping
                    name_to_index = {}
                    for param in data.get("parameters", []):
                        # Normalize name for matching
                        name = param["name"]
                        name_to_index[name.lower().replace(" ", "").replace("/", "")] = {
                            "index": param["index"],
                            "name": param["name"],
                            "min": param.get("min", 0),
                            "max": param.get("max", 1),
                            "is_quantized": param.get("is_quantized", False)
                        }
                    map_data = {
                        "plugin_name": data.get("plugin", ""),
                        "type": data.get("type", ""),
                        "parameters": name_to_index,
                        "parameter_count": len(name_to_index)
                    }
                    maps[class_name] = map_data

                    # Also add without version suffix for XML matching
                    base_name = re.sub(r'\d+$', '', class_name)
                    if base_name != class_name:
                        maps[base_name] = map_data

    # Add reverse mappings from xml_to_mcp_class
    for xml_class, mcp_class in xml_to_mcp_class.items():
        if mcp_class in maps and xml_class not in maps:
            maps[xml_class] = maps[mcp_class]

    return maps


def decompress_and_parse(filepath):
    """Decompress gzip XML and parse it."""
    try:
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            content = f.read()
        return ET.fromstring(content)
    except Exception as e:
        # Try reading as plain XML
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return ET.fromstring(content)
        except:
            return None


def extract_parameters_from_xml(root):
    """Extract parameter values from XML element."""
    parameters = {}

    # The root element after Ableton tag is the device class (e.g., Compressor2)
    device_element = None
    device_class = None

    for child in root:
        if child.tag not in ['Ableton']:
            device_element = child
            device_class = child.tag
            break

    if device_element is None:
        return None, None

    def extract_manual_values(element, prefix=""):
        """Recursively extract Manual values from elements."""
        for child in element:
            # Look for Manual elements with Value attribute
            manual = child.find("Manual")
            if manual is not None and "Value" in manual.attrib:
                param_name = child.tag
                try:
                    value = float(manual.attrib["Value"])
                except:
                    value = manual.attrib["Value"]

                # Normalize param name for matching
                normalized = param_name.lower().replace(" ", "").replace("/", "")
                parameters[normalized] = {
                    "xml_name": param_name,
                    "value": value
                }

            # Also check for nested structures (but don't go too deep)
            if len(list(child)) > 0 and child.tag not in ['LomId', 'AutomationTarget', 'ModulationTarget',
                                                           'MidiControllerRange', 'MidiCCOnOffThresholds',
                                                           'LastPresetRef', 'SourceContext', 'LockedScripts']:
                # Check for Value attribute directly on some elements
                if "Value" in child.attrib:
                    param_name = child.tag
                    try:
                        value = float(child.attrib["Value"])
                    except:
                        value = child.attrib["Value"]
                    normalized = param_name.lower().replace(" ", "").replace("/", "")
                    parameters[normalized] = {
                        "xml_name": param_name,
                        "value": value
                    }

    extract_manual_values(device_element)

    # Also get UserName (preset name)
    user_name_elem = device_element.find("UserName")
    preset_name = user_name_elem.attrib.get("Value", "") if user_name_elem is not None else ""

    return device_class, parameters, preset_name


def find_preset_files(directory):
    """Find all .adv and .adg files recursively."""
    presets = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.adv') or filename.endswith('.adg'):
                filepath = os.path.join(root, filename)
                # Get relative path from Core Library
                rel_path = os.path.relpath(filepath, CORE_LIBRARY)
                presets.append({
                    "filepath": filepath,
                    "rel_path": rel_path,
                    "filename": filename
                })
    return presets


def sanitize_filename(name):
    """Convert name to safe filename."""
    safe = re.sub(r'[^\w\s-]', '', name.lower())
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe[:100]


def main():
    print("=" * 60)
    print("  ABLETON PRESET XML PARSER")
    print("  Fast direct-from-disk parsing")
    print("=" * 60)
    print()

    # Load base plugin maps
    print("Loading base plugin parameter maps...")
    base_maps = load_base_plugin_maps()
    print(f"Loaded {len(base_maps)} plugin class mappings")
    print()

    # Find all preset files
    print(f"Scanning {CORE_LIBRARY} for presets...")

    # Focus on Devices folder (Audio Effects, MIDI Effects, Instruments)
    devices_path = os.path.join(CORE_LIBRARY, "Devices")
    all_presets = find_preset_files(devices_path)
    print(f"Found {len(all_presets)} preset files in Devices")

    # Also check Racks folder
    racks_path = os.path.join(CORE_LIBRARY, "Racks")
    if os.path.exists(racks_path):
        rack_presets = find_preset_files(racks_path)
        print(f"Found {len(rack_presets)} preset files in Racks")
        all_presets.extend(rack_presets)

    print(f"Total: {len(all_presets)} preset files")
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Process each preset
    successful = 0
    failed = 0
    class_stats = defaultdict(int)
    unmapped_classes = set()

    all_parsed_presets = []

    for i, preset_info in enumerate(all_presets):
        filepath = preset_info["filepath"]
        rel_path = preset_info["rel_path"]

        if (i + 1) % 100 == 0:
            print(f"Processing {i+1}/{len(all_presets)}...")

        # Parse XML
        root = decompress_and_parse(filepath)
        if root is None:
            failed += 1
            continue

        result = extract_parameters_from_xml(root)
        if result[0] is None:
            failed += 1
            continue

        device_class, xml_params, preset_name = result
        class_stats[device_class] += 1

        # Try to map to base plugin
        base_map = base_maps.get(device_class)

        if base_map is None:
            unmapped_classes.add(device_class)
            # Still save the raw XML data
            preset_data = {
                "preset_name": preset_name or preset_info["filename"],
                "rel_path": rel_path,
                "device_class": device_class,
                "has_base_map": False,
                "xml_parameters": {k: v["value"] for k, v in xml_params.items()}
            }
        else:
            # Map XML params to indices
            mapped_params = []
            for normalized_name, xml_info in xml_params.items():
                if normalized_name in base_map["parameters"]:
                    base_info = base_map["parameters"][normalized_name]
                    mapped_params.append({
                        "index": base_info["index"],
                        "name": base_info["name"],
                        "value": xml_info["value"],
                        "min": base_info["min"],
                        "max": base_info["max"]
                    })

            # Sort by index
            mapped_params.sort(key=lambda x: x["index"])

            preset_data = {
                "preset_name": preset_name or preset_info["filename"],
                "rel_path": rel_path,
                "device_class": device_class,
                "plugin_name": base_map["plugin_name"],
                "plugin_type": base_map["type"],
                "has_base_map": True,
                "parameter_count": len(mapped_params),
                "parameters": mapped_params
            }

        all_parsed_presets.append(preset_data)
        successful += 1

    print()
    print("=" * 60)
    print(f"PARSING COMPLETE")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print()

    # Save all presets to single file
    output_file = os.path.join(OUTPUT_DIR, "all_presets.json")
    with open(output_file, "w") as f:
        json.dump({
            "total_presets": len(all_parsed_presets),
            "presets": all_parsed_presets
        }, f, indent=2)
    print(f"Saved to: {output_file}")

    # Also save by device class
    by_class = defaultdict(list)
    for preset in all_parsed_presets:
        by_class[preset["device_class"]].append(preset)

    for device_class, presets in by_class.items():
        class_file = os.path.join(OUTPUT_DIR, f"{sanitize_filename(device_class)}_presets.json")
        with open(class_file, "w") as f:
            json.dump({
                "device_class": device_class,
                "preset_count": len(presets),
                "presets": presets
            }, f, indent=2)

    print(f"Saved {len(by_class)} device class files")
    print()

    # Stats
    print("Device class distribution:")
    for cls, count in sorted(class_stats.items(), key=lambda x: -x[1])[:20]:
        mapped = "✓" if cls in base_maps else "✗"
        print(f"  {mapped} {cls}: {count}")

    if unmapped_classes:
        print()
        print(f"Unmapped device classes ({len(unmapped_classes)}):")
        for cls in sorted(unmapped_classes):
            print(f"  - {cls}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
