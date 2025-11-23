#!/usr/bin/env python3
"""
Test the enhanced converter on the previously failed files
Confirm proper FX ID validation and logging
"""

from ultimate_preset_converter import UltimatePresetConverter
from pathlib import Path

def test_enhanced_filtering():
    """Test enhanced converter on known non-Serum presets"""
    print("🧪 TESTING ENHANCED CONVERTER FILTERING")
    print("=" * 50)

    converter = UltimatePresetConverter()

    # Test files that should be skipped (Sylenth1 presets)
    failed_files = [
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Sub.fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Cristal.fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Fi8.fxp"
    ]

    # Test known working Serum preset
    working_file = "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp"

    print("\\n🎛️  Testing Sylenth1 presets (should be skipped):")
    for fxp_file in failed_files:
        result = converter.convert_fxp_file(fxp_file)
        if result is None:
            print(f"✅ Correctly skipped: {Path(fxp_file).name}")
        else:
            print(f"❌ UNEXPECTED: Converted {Path(fxp_file).name}")

    print("\\n🎹 Testing known Serum preset (should convert):")
    result = converter.convert_fxp_file(working_file)
    if result:
        print(f"✅ Successfully converted: {Path(working_file).name}")
        print(f"   Parameters: {result['stats']['mapped_params']}")
        print(f"   Preset name: {result['preset_name']}")
    else:
        print(f"❌ UNEXPECTED: Failed to convert {Path(working_file).name}")

    print(f"\\n📊 Final stats:")
    print(f"   Skipped non-Serum: {converter.stats['skipped_non_serum']}")
    print(f"   FXP converted: {converter.stats['fxp_converted']}")
    print(f"   Failed conversions: {converter.stats['failed_conversions']}")

if __name__ == "__main__":
    test_enhanced_filtering()