#!/usr/bin/env python3
"""
Debug the 6 failed preset conversions
Analyze what's different about these files
"""

import struct
import zlib
from pathlib import Path

def analyze_failed_preset(fxp_path):
    """Deep analysis of failed .fxp file"""
    print(f"\n🔍 ANALYZING: {Path(fxp_path).name}")
    print("=" * 50)

    if not Path(fxp_path).exists():
        print(f"❌ File doesn't exist: {fxp_path}")
        return

    with open(fxp_path, 'rb') as f:
        data = f.read()

    print(f"📊 File size: {len(data)} bytes")

    # Check basic FXP structure
    if len(data) < 56:
        print(f"❌ File too small: {len(data)} bytes")
        return

    # Parse header
    chunk_magic = data[0:4]
    byte_size = struct.unpack('>I', data[4:8])[0] if len(data) >= 8 else 0
    fx_magic = data[8:12] if len(data) >= 12 else b''

    print(f"🔍 Header analysis:")
    print(f"   Chunk magic: {chunk_magic} ({'✅ Valid' if chunk_magic == b'CcnK' else '❌ Invalid'})")
    print(f"   Byte size: {byte_size}")
    print(f"   FX magic: {fx_magic} ({'✅ Valid' if fx_magic == b'FPCh' else '❌ Invalid'})")

    if chunk_magic != b'CcnK' or fx_magic != b'FPCh':
        print(f"❌ Not a valid FXP file")
        return

    # Parse preset info
    if len(data) >= 28:
        version = struct.unpack('>I', data[12:16])[0]
        fx_id = struct.unpack('>I', data[16:20])[0]
        fx_version = struct.unpack('>I', data[20:24])[0]
        num_params = struct.unpack('>I', data[24:28])[0]

        print(f"📋 Preset info:")
        print(f"   Version: {version}")
        print(f"   FX ID: {fx_id:08X} ({'✅ Serum' if fx_id == 0x58667358 else '⚠️  Non-Serum'})")
        print(f"   FX Version: {fx_version}")
        print(f"   Num Params: {num_params}")

    # Extract preset name
    if len(data) >= 56:
        name_bytes = data[28:56]
        try:
            null_idx = name_bytes.index(b'\x00')
            preset_name = name_bytes[:null_idx].decode('utf-8', errors='ignore')
        except (ValueError, UnicodeDecodeError):
            preset_name = name_bytes.decode('utf-8', errors='ignore').strip('\x00')
        print(f"   Preset name: '{preset_name.strip()}'")

    # Analyze chunk data
    if len(data) > 56:
        chunk_data = data[56:]
        print(f"\n🔍 Chunk data analysis:")
        print(f"   Chunk size: {len(chunk_data)} bytes")

        if len(chunk_data) >= 20:
            # Show hex dump of first 20 bytes
            hex_dump = ' '.join(f'{b:02X}' for b in chunk_data[:20])
            print(f"   First 20 bytes: {hex_dump}")

            # Check for different compression headers
            first_4 = chunk_data[:4]
            print(f"   First 4 bytes: {first_4.hex().upper()}")

            # Try different decompression methods
            print(f"\n🔓 Decompression attempts:")

            methods = [
                ("Standard (skip 4 + zlib)", lambda: zlib.decompress(chunk_data[4:])),
                ("Skip 2 + zlib", lambda: zlib.decompress(chunk_data[2:])),
                ("Skip 6 + zlib", lambda: zlib.decompress(chunk_data[6:])),
                ("Skip 8 + zlib", lambda: zlib.decompress(chunk_data[8:])),
                ("Raw zlib", lambda: zlib.decompress(chunk_data)),
                ("Deflate -15", lambda: zlib.decompress(chunk_data, -15)),
                ("Skip 4 + Deflate -15", lambda: zlib.decompress(chunk_data[4:], -15)),
            ]

            for method_name, decompress_func in methods:
                try:
                    result = decompress_func()
                    print(f"   ✅ {method_name}: SUCCESS ({len(result)} bytes)")

                    # Show first part of decompressed data
                    if len(result) >= 20:
                        hex_result = ' '.join(f'{b:02X}' for b in result[:20])
                        print(f"      First 20 bytes: {hex_result}")

                    # Check for float patterns
                    if len(result) >= 4 and len(result) % 4 == 0:
                        float_count = len(result) // 4
                        try:
                            floats = struct.unpack(f'<{min(10, float_count)}f', result[:min(40, len(result))])
                            valid_params = [f for f in floats if 0.0 <= f <= 1.0]
                            print(f"      First 10 floats: {floats}")
                            print(f"      Valid params (0-1): {len(valid_params)}")
                        except:
                            print(f"      Could not parse as floats")

                    return  # Stop after first success

                except Exception as e:
                    print(f"   ❌ {method_name}: {e}")

        else:
            print(f"   ⚠️  Chunk too small: {len(chunk_data)} bytes")

    else:
        print(f"❌ No chunk data found")

def analyze_all_failed_presets():
    """Analyze all failed presets"""
    print("🔍 DEBUGGING FAILED PRESET CONVERSIONS")
    print("=" * 60)

    failed_files = [
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Sub.fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Cristal.fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Fi8.fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Pirate.fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Vinne.fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/User/Mallada free pack/Sy Catd.fxp"
    ]

    for fxp_file in failed_files:
        analyze_failed_preset(fxp_file)

    # Compare with a working file for reference
    print(f"\n" + "=" * 60)
    print("🔍 COMPARING WITH WORKING FILE:")
    working_file = "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp"
    analyze_failed_preset(working_file)

if __name__ == "__main__":
    analyze_all_failed_presets()