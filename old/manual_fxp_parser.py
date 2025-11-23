#!/usr/bin/env python3
"""
Manual FXP parser + Pedalboard parameter setting approach
Parse .fxp files manually and set parameters individually in Serum
"""

import struct
import zlib
import json
from pathlib import Path
from pedalboard import load_plugin

class SerumFXPParser:
    """Parse Serum .fxp files manually"""

    def __init__(self):
        self.chunk_magic = b'CcnK'
        self.fxp_magic = b'FPCh'
        self.serum_magic = b'XfsX'

    def parse_fxp_file(self, fxp_path):
        """Parse .fxp file structure"""
        print(f"🔍 Parsing FXP: {Path(fxp_path).name}")

        with open(fxp_path, 'rb') as f:
            data = f.read()

        if not data.startswith(self.chunk_magic):
            raise ValueError("Invalid FXP file - missing CcnK header")

        # Parse FXP header
        chunk_magic = data[0:4]
        byte_size = struct.unpack('>I', data[4:8])[0]
        fx_magic = data[8:12]

        if fx_magic != self.fxp_magic:
            raise ValueError("Not a valid FXP preset file")

        # Parse preset header
        version = struct.unpack('>I', data[12:16])[0]
        fx_id = struct.unpack('>I', data[16:20])[0]
        fx_version = struct.unpack('>I', data[20:24])[0]
        num_params = struct.unpack('>I', data[24:28])[0]

        # Check for Serum magic
        serum_check = data[16:20]
        if serum_check == self.serum_magic:
            print("✅ Confirmed Serum preset")
        else:
            print(f"⚠️  FX ID: {fx_id:08X} (not standard Serum)")

        # Extract preset name
        preset_name = self._extract_name(data[28:56])

        # Get chunk data (the interesting part)
        chunk_data = data[56:] if len(data) > 56 else b''

        print(f"📊 FXP Info:")
        print(f"   Version: {version}")
        print(f"   FX ID: {fx_id:08X}")
        print(f"   FX Version: {fx_version}")
        print(f"   Num Params: {num_params}")
        print(f"   Preset Name: '{preset_name}'")
        print(f"   Chunk Data: {len(chunk_data)} bytes")

        return {
            'version': version,
            'fx_id': fx_id,
            'fx_version': fx_version,
            'num_params': num_params,
            'preset_name': preset_name,
            'chunk_data': chunk_data,
            'raw_data': data
        }

    def _extract_name(self, name_bytes):
        """Extract preset name from bytes"""
        try:
            null_idx = name_bytes.index(b'\\x00')
            name = name_bytes[:null_idx].decode('utf-8', errors='ignore')
        except (ValueError, UnicodeDecodeError):
            name = name_bytes.decode('utf-8', errors='ignore').strip('\\x00')
        return name.strip()

    def try_decompress_chunk(self, chunk_data):
        """Try to decompress Serum chunk data"""
        if not chunk_data:
            return None

        print(f"🔓 Attempting to decompress chunk data...")

        # Try different decompression methods
        methods = [
            ("zlib", lambda data: zlib.decompress(data)),
            ("zlib_skip_header", lambda data: zlib.decompress(data[2:])),
            ("raw", lambda data: data)  # No compression
        ]

        for method_name, decompress_func in methods:
            try:
                decompressed = decompress_func(chunk_data)
                print(f"✅ {method_name} decompression successful: {len(decompressed)} bytes")

                # Try to find patterns or JSON-like structures
                if b'{' in decompressed or b'[' in decompressed:
                    print("   📋 Found JSON-like structures")

                # Show hex dump of first part
                print(f"   🔍 First 50 bytes: {decompressed[:50]}")

                return {
                    'method': method_name,
                    'data': decompressed,
                    'size': len(decompressed)
                }

            except Exception as e:
                print(f"   ❌ {method_name} failed: {e}")

        return None

def test_manual_approach():
    """Test manual FXP parsing approach"""
    print("🎵 Manual FXP Parsing + Pedalboard Parameter Setting")
    print("=" * 60)

    parser = SerumFXPParser()

    # Test with multiple .fxp files
    test_files = [
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/SAW Find me [AF].fxp",
    ]

    for fxp_file in test_files:
        if not Path(fxp_file).exists():
            continue

        print(f"\\n{'='*50}")

        try:
            # Parse FXP file
            fxp_data = parser.parse_fxp_file(fxp_file)

            # Try to decompress chunk data
            if fxp_data['chunk_data']:
                decompressed = parser.try_decompress_chunk(fxp_data['chunk_data'])

                if decompressed:
                    print(f"\\n🎛️  Attempting parameter extraction...")

                    # This is where we'd need to reverse engineer the parameter format
                    # For now, let's see what we can find
                    data = decompressed['data']

                    # Look for parameter-like patterns
                    if len(data) >= 4:
                        # Try to interpret as float arrays
                        float_count = len(data) // 4
                        if float_count > 0:
                            try:
                                # Try little-endian floats
                                floats = struct.unpack(f'<{min(100, float_count)}f', data[:min(400, len(data))])
                                print(f"   📊 Found {len(floats)} float values (first 10): {floats[:10]}")

                                # Check if values are in reasonable parameter range (0-1)
                                valid_params = [f for f in floats if 0.0 <= f <= 1.0]
                                print(f"   ✅ {len(valid_params)} values in 0-1 range (likely parameters)")

                            except Exception as e:
                                print(f"   ⚠️  Float parsing failed: {e}")

                    # Try to load into Serum and see if we can map these values
                    print(f"\\n🎹 Testing with Pedalboard Serum...")

                    try:
                        serum = load_plugin('/Library/Audio/Plug-Ins/VST3/Serum.vst3')
                        print(f"   ✅ Loaded Serum: {len(serum.parameters)} parameters")

                        # Get current parameter names for reference
                        param_names = list(serum.parameters.keys())
                        print(f"   📋 First 10 parameter names: {param_names[:10]}")

                        # This is where we'd try to map extracted values to parameter names
                        # This would require reverse engineering the parameter order/mapping

                    except Exception as e:
                        print(f"   ❌ Serum loading failed: {e}")

            else:
                print("⚠️  No chunk data found in FXP file")

        except Exception as e:
            print(f"❌ Failed to parse {Path(fxp_file).name}: {e}")

    print(f"\\n💡 Next Steps:")
    print("   1. Reverse engineer Serum parameter format from chunk data")
    print("   2. Map decompressed values to Serum parameter names")
    print("   3. Set parameters individually in Pedalboard")
    print("   4. Validate by comparing with preset loaded in Serum GUI")

if __name__ == "__main__":
    test_manual_approach()