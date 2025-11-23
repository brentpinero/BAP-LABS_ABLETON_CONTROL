#!/usr/bin/env python3
"""
Test DawDreamer VST loading with different Serum paths
"""

import dawdreamer as daw
from pathlib import Path

def test_vst_loading():
    """Test different VST paths with DawDreamer"""

    # Test paths
    test_paths = [
        "/Library/Audio/Plug-Ins/VST3/Serum2.vst3/Contents/MacOS/Serum2",
        "/Library/Audio/Plug-Ins/VST3/Serum2.vst3",
        "/Library/Audio/Plug-Ins/VST3/Serum.vst3/Contents/MacOS/Serum",
        "/Library/Audio/Plug-Ins/VST3/Serum.vst3",
        "/Library/Audio/Plug-Ins/Components/Serum2.component",
        "/Library/Audio/Plug-Ins/Components/Serum.component"
    ]

    print("🧪 Testing DawDreamer VST Loading")
    print("=" * 50)

    # Initialize DawDreamer engine
    try:
        engine = daw.RenderEngine(44100, 512)
        print("✅ DawDreamer engine initialized")
    except Exception as e:
        print(f"❌ Failed to initialize DawDreamer: {e}")
        return

    for path in test_paths:
        if not Path(path).exists():
            print(f"⚠️  Path doesn't exist: {path}")
            continue

        print(f"\n🔍 Testing: {path}")

        try:
            # Try to load as VST
            synth = engine.make_plugin_processor("serum_test", path)
            print(f"✅ Successfully loaded VST")

            # Try to get basic info
            try:
                param_count = synth.get_parameter_count()
                print(f"📊 Parameter count: {param_count}")

                if param_count > 0:
                    first_param = synth.get_parameter_name(0)
                    print(f"🎛️  First parameter: {first_param}")

            except Exception as e:
                print(f"⚠️  Could not get parameter info: {e}")

        except Exception as e:
            print(f"❌ Failed to load VST: {e}")

    print(f"\n📋 Test completed!")

if __name__ == "__main__":
    test_vst_loading()