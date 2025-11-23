#!/usr/bin/env python3
"""
Demo: Working Serum Parameter Extraction
Shows what we CAN extract from Serum 2 and .SerumPreset files
"""

import dawdreamer as daw
import json
from pathlib import Path
import struct

def analyze_serumpreset_file(preset_path):
    """Analyze a .SerumPreset file structure"""
    print(f"🔍 Analyzing .SerumPreset: {Path(preset_path).name}")

    with open(preset_path, 'rb') as f:
        data = f.read()

    print(f"📊 File size: {len(data)} bytes")
    print(f"🔍 Header: {data[:20]}")

    # Check if it starts with XferJson
    if data.startswith(b'XferJson'):
        print("✅ Valid Serum 2 preset format detected")

        # Try to find JSON data after header
        try:
            # Look for JSON start after the header
            json_start = data.find(b'{"')
            if json_start > 0:
                json_data = data[json_start:]

                # Try to decompress if it's compressed
                try:
                    import zstandard as zstd
                    # The data might be Zstandard compressed
                    dctx = zstd.ZstdDecompressor()
                    decompressed = dctx.decompress(json_data)
                    preset_json = json.loads(decompressed.decode('utf-8'))
                    print("✅ Successfully decompressed and parsed JSON")
                    return preset_json
                except:
                    # Try direct JSON parsing
                    try:
                        preset_json = json.loads(json_data.decode('utf-8'))
                        print("✅ Successfully parsed JSON directly")
                        return preset_json
                    except:
                        print("⚠️  Could not parse JSON data")
        except Exception as e:
            print(f"⚠️  Error analyzing preset: {e}")

    return None

def extract_serum2_default_state():
    """Extract default Serum 2 state to show parameter structure"""
    print(f"\n🎹 Extracting Serum 2 Default State")
    print("=" * 50)

    try:
        engine = daw.RenderEngine(44100, 512)
        synth = engine.make_plugin_processor('serum2', '/Library/Audio/Plug-Ins/VST3/Serum2.vst3')

        params_description = synth.get_parameters_description()

        # Organize parameters by category
        categories = {}
        for param in params_description:
            name = param['name']
            value = synth.get_parameter(param['index'])

            # Categorize by name patterns
            category = 'Other'
            if any(x in name.lower() for x in ['osc', 'wave']):
                category = 'Oscillators'
            elif any(x in name.lower() for x in ['filter', 'cutoff', 'resonance']):
                category = 'Filters'
            elif any(x in name.lower() for x in ['env', 'attack', 'decay', 'sustain', 'release']):
                category = 'Envelopes'
            elif any(x in name.lower() for x in ['lfo']):
                category = 'LFOs'
            elif any(x in name.lower() for x in ['fx', 'reverb', 'delay', 'chorus', 'distort']):
                category = 'Effects'
            elif any(x in name.lower() for x in ['main', 'master', 'vol', 'tune']):
                category = 'Global'

            if category not in categories:
                categories[category] = []

            categories[category].append({
                'name': name,
                'value': value,
                'text': param.get('text', ''),
                'default': param.get('defaultValue', 0)
            })

        # Show summary
        print(f"📊 Parameter Categories:")
        for category, params in categories.items():
            non_default = sum(1 for p in params if abs(p['value'] - p['default']) > 0.01)
            print(f"   {category}: {len(params)} parameters ({non_default} non-default)")

        # Show sample from each category
        print(f"\n🎛️  Sample Parameters by Category:")
        for category, params in categories.items():
            if params:
                print(f"\n{category}:")
                for param in params[:3]:  # First 3 from each category
                    print(f"   {param['name']}: {param['value']:.3f} ({param['text']})")

        return categories

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def demonstrate_what_works():
    """Demonstrate what we can actually accomplish"""
    print("🎵 Demo: What We CAN Extract from Serum")
    print("=" * 60)

    # 1. Analyze .SerumPreset file
    preset_files = [
        "/Users/brentpinero/Documents/serum_llm_2/Serum_2_Presets/BA - PZ Formant Filter.SerumPreset",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_2_Presets/HV - Smack My Reese Up.SerumPreset"
    ]

    for preset_file in preset_files:
        if Path(preset_file).exists():
            preset_data = analyze_serumpreset_file(preset_file)
            if preset_data:
                print(f"📋 Found preset data keys: {list(preset_data.keys())}")
            break

    # 2. Extract default Serum 2 state
    categories = extract_serum2_default_state()

    # 3. Show what we could do with working .fxp loading
    print(f"\n💡 What We COULD Do with Working .fxp Loading:")
    print("   1. Load .fxp preset into Serum 2")
    print("   2. Extract all 2,623 parameters")
    print("   3. Organize by categories (oscillators, filters, etc.)")
    print("   4. Analyze characteristics (bass-heavy, bright, etc.)")
    print("   5. Save as enhanced .SerumPreset format")

    print(f"\n🔧 Current Limitation:")
    print("   - DawDreamer's load_preset() method fails with our .fxp files")
    print("   - Possible solutions:")
    print("     • Try older DawDreamer version")
    print("     • Use different VST host")
    print("     • Parse .fxp manually and set parameters individually")
    print("     • Focus on .SerumPreset analysis instead")

if __name__ == "__main__":
    demonstrate_what_works()