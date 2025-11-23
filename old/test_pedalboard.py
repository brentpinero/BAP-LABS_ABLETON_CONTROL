#!/usr/bin/env python3
"""
Test Spotify Pedalboard for Serum VST loading and .fxp preset handling
"""

import pedalboard
from pedalboard import load_plugin
import numpy as np
from pathlib import Path

def test_pedalboard_serum():
    """Test Pedalboard with Serum VST"""
    print("🎵 Testing Spotify Pedalboard with Serum")
    print("=" * 50)

    # Test paths for Serum
    serum_paths = [
        "/Library/Audio/Plug-Ins/VST3/Serum2.vst3",
        "/Library/Audio/Plug-Ins/VST3/Serum.vst3",
        "/Library/Audio/Plug-Ins/Components/Serum2.component",
        "/Library/Audio/Plug-Ins/Components/Serum.component"
    ]

    for path in serum_paths:
        if not Path(path).exists():
            print(f"⚠️  Path doesn't exist: {path}")
            continue

        print(f"\n🔍 Testing: {path}")

        try:
            # Load Serum plugin
            serum = load_plugin(path)
            print(f"✅ Successfully loaded Serum plugin")

            # Check if it's an instrument
            print(f"📊 Plugin info:")
            print(f"   Name: {serum.name if hasattr(serum, 'name') else 'Unknown'}")
            print(f"   Type: {type(serum)}")

            # Get parameters
            if hasattr(serum, 'parameters'):
                params = serum.parameters
                print(f"   Parameters: {len(params)} available")

                # Show first few parameters
                print(f"\n🎛️  Sample parameters:")
                for i, (param_name, param_value) in enumerate(list(params.items())[:5]):
                    print(f"   {param_name}: {param_value}")

                # Test .fxp loading
                print(f"\n📁 Testing .fxp preset loading:")
                test_fxp = "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp"

                if Path(test_fxp).exists():
                    try:
                        # Try to load preset
                        if hasattr(serum, 'load_preset'):
                            success = serum.load_preset(test_fxp)
                            print(f"   load_preset() result: {success}")
                        else:
                            print("   ⚠️  No load_preset method found")

                        # Check if parameters changed after loading
                        if hasattr(serum, 'parameters'):
                            new_params = serum.parameters
                            changed_params = 0
                            for param_name, param_value in new_params.items():
                                if param_name in params and params[param_name] != param_value:
                                    changed_params += 1

                            print(f"   Changed parameters: {changed_params}")

                            if changed_params > 0:
                                print("   ✅ FXP loading appears to work!")

                                # Show some changed parameters
                                print(f"   🎛️  Some changed parameters:")
                                count = 0
                                for param_name, param_value in new_params.items():
                                    if param_name in params and params[param_name] != param_value and count < 5:
                                        print(f"      {param_name}: {params[param_name]} → {param_value}")
                                        count += 1
                            else:
                                print("   ⚠️  No parameters changed - preset may not have loaded")

                    except Exception as e:
                        print(f"   ❌ FXP loading failed: {e}")

                # Test audio processing to make sure plugin works
                print(f"\n🔊 Testing audio processing:")
                try:
                    # Create test audio (silent)
                    sample_rate = 44100
                    duration = 0.1  # 100ms
                    test_audio = np.zeros((int(sample_rate * duration), 2), dtype=np.float32)

                    # Process audio
                    processed = serum(test_audio, sample_rate)
                    print(f"   ✅ Audio processing works: {processed.shape}")

                except Exception as e:
                    print(f"   ⚠️  Audio processing failed: {e}")

                return serum  # Return working plugin for further testing

            else:
                print("   ⚠️  No parameters attribute found")

        except Exception as e:
            print(f"❌ Failed to load plugin: {e}")

    return None

def test_fxp_batch_loading(serum_plugin):
    """Test loading multiple .fxp files"""
    if not serum_plugin:
        print("❌ No working Serum plugin available")
        return

    print(f"\n🔄 Testing batch .fxp loading:")

    test_files = [
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/SAW Find me [AF].fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/KY WurlyKeys [ASL].fxp"
    ]

    for fxp_file in test_files:
        if Path(fxp_file).exists():
            print(f"\n📁 Testing: {Path(fxp_file).name}")

            try:
                # Get baseline parameters
                baseline_params = dict(serum_plugin.parameters)

                # Try to load preset
                if hasattr(serum_plugin, 'load_preset'):
                    success = serum_plugin.load_preset(fxp_file)
                    print(f"   Load result: {success}")

                # Check changes
                new_params = dict(serum_plugin.parameters)
                changed = sum(1 for k, v in new_params.items()
                             if k in baseline_params and baseline_params[k] != v)

                print(f"   Parameters changed: {changed}")

            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    serum = test_pedalboard_serum()
    if serum:
        test_fxp_batch_loading(serum)