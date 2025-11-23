#!/usr/bin/env python3
"""
Test both .fxp and .SerumPreset formats to show the difference
"""

import dawdreamer as daw
import json
from pathlib import Path

def test_serum_preset_extraction():
    """Test extracting parameters from Serum without loading presets"""

    print("🎵 Testing Serum Parameter Extraction")
    print("=" * 50)

    # Test .SerumPreset file (if we can read it as JSON)
    serum_preset_file = "/Users/brentpinero/Documents/serum_llm_2/Serum_2_Presets/BA - PZ Formant Filter.SerumPreset"

    print(f"\n📋 Testing .SerumPreset file:")
    print(f"File: {Path(serum_preset_file).name}")

    # Try to read as JSON first
    try:
        with open(serum_preset_file, 'r') as f:
            preset_data = json.load(f)
        print(f"✅ Read as JSON successfully")
        print(f"📊 Keys: {list(preset_data.keys())}")
        if 'metadata' in preset_data:
            print(f"🏷️  Name: {preset_data['metadata'].get('name', 'Unknown')}")
    except:
        print("⚠️  Not readable as JSON (binary format)")
        with open(serum_preset_file, 'rb') as f:
            data = f.read()
        print(f"📊 File size: {len(data)} bytes")
        print(f"🔍 Header: {data[:20]}")

    # Test Serum 2 VST loading and parameter extraction
    print(f"\n🎹 Testing Serum 2 VST Parameter Access:")

    try:
        engine = daw.RenderEngine(44100, 512)
        synth = engine.make_plugin_processor('serum2', '/Library/Audio/Plug-Ins/VST3/Serum2.vst3')

        params_description = synth.get_parameters_description()
        param_count = len(params_description)

        print(f"✅ Serum 2 loaded successfully")
        print(f"📊 Total parameters: {param_count}")

        # Show some interesting parameters
        print(f"\n🎛️  Sample parameters:")
        interesting_params = []
        for param in params_description[:20]:  # First 20 params
            name = param['name']
            value = synth.get_parameter(param['index'])
            interesting_params.append({'name': name, 'value': value, 'text': param.get('text', '')})

        for param in interesting_params[:5]:
            print(f"   {param['name']}: {param['value']:.3f} ({param['text']})")

        # Test .fxp loading (this is where the issue is)
        print(f"\n📁 Testing .fxp loading:")
        fxp_file = "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp"

        print(f"File: {Path(fxp_file).name}")

        # Try different loading methods
        load_success = synth.load_preset(fxp_file)
        print(f"load_preset() result: {load_success}")

        if not load_success:
            print("⚠️  .fxp loading failed - this is the main issue to solve")
            print("💡 Possible solutions:")
            print("   1. Try Serum 1 VST instead of Serum 2")
            print("   2. Check if .fxp file is compatible")
            print("   3. Use different DawDreamer method")

        # Test with Serum 1 if available
        try:
            serum1 = engine.make_plugin_processor('serum1', '/Library/Audio/Plug-Ins/VST3/Serum.vst3')
            load_success1 = serum1.load_preset(fxp_file)
            print(f"Serum 1 load_preset() result: {load_success1}")

            if load_success1:
                print("✅ Success with Serum 1!")
                # Get a few parameters to show it worked
                params1 = serum1.get_parameters_description()
                main_vol = serum1.get_parameter(0)
                print(f"   Main Vol after loading: {main_vol}")

        except Exception as e:
            print(f"⚠️  Serum 1 test failed: {e}")

    except Exception as e:
        print(f"❌ Serum VST test failed: {e}")

if __name__ == "__main__":
    test_serum_preset_extraction()