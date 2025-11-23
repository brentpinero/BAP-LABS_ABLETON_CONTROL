#!/usr/bin/env python3
"""
Crack Serum FXP compression format
Try different decompression methods and analyze the structure
"""

import struct
import zlib
import json
from pathlib import Path
from pedalboard import load_plugin

def try_all_decompressions(chunk_data):
    """Try every possible decompression method"""
    print(f"🔓 Trying all decompression methods on {len(chunk_data)} bytes...")

    # Show hex dump of first part
    print(f"🔍 Hex dump (first 64 bytes):")
    hex_dump = ' '.join(f'{b:02X}' for b in chunk_data[:64])
    print(f"   {hex_dump}")

    # Try various methods
    methods = []

    # Standard zlib methods
    methods.extend([
        ("zlib_raw", lambda d: zlib.decompress(d)),
        ("zlib_skip_2", lambda d: zlib.decompress(d[2:])),
        ("zlib_skip_4", lambda d: zlib.decompress(d[4:])),
        ("zlib_skip_8", lambda d: zlib.decompress(d[8:])),
    ])

    # Deflate methods (different wbits values)
    for wbits in [-15, -14, -13, -12, -11, -10, -9, 15, 14, 13, 12, 11, 10, 9]:
        methods.append((f"deflate_wbits_{wbits}", lambda d, w=wbits: zlib.decompress(d, w)))

    # Skip various header sizes and try deflate
    for skip in [0, 2, 4, 6, 8, 10, 12, 16, 20]:
        for wbits in [-15, 15]:
            methods.append((f"deflate_skip_{skip}_wbits_{wbits}",
                          lambda d, s=skip, w=wbits: zlib.decompress(d[s:], w)))

    successful_decompressions = []

    for method_name, decompress_func in methods:
        try:
            decompressed = decompress_func(chunk_data)
            size = len(decompressed)

            if size > 100:  # Only interested in substantial decompression
                print(f"✅ {method_name}: {size} bytes")

                # Analyze the decompressed data
                analysis = analyze_decompressed_data(decompressed)

                successful_decompressions.append({
                    'method': method_name,
                    'data': decompressed,
                    'size': size,
                    'analysis': analysis
                })

                # Show first part
                print(f"   🔍 First 100 chars: {decompressed[:100]}")

        except Exception as e:
            # Most will fail, only show interesting failures
            if "invalid" not in str(e).lower():
                pass  # Silent fail for expected failures

    return successful_decompressions

def analyze_decompressed_data(data):
    """Analyze decompressed data to understand structure"""
    analysis = {
        'size': len(data),
        'has_json': False,
        'has_strings': False,
        'float_count': 0,
        'valid_floats': 0,
        'patterns': []
    }

    # Check for JSON
    if b'{' in data or b'[' in data:
        analysis['has_json'] = True

    # Check for readable strings
    try:
        text = data.decode('utf-8', errors='ignore')
        if len([c for c in text if c.isprintable()]) > len(text) * 0.5:
            analysis['has_strings'] = True
            analysis['text_sample'] = text[:200]
    except:
        pass

    # Try to parse as floats
    if len(data) >= 4 and len(data) % 4 == 0:
        try:
            float_count = len(data) // 4
            floats = struct.unpack(f'<{float_count}f', data)
            analysis['float_count'] = float_count

            # Count valid parameter-like floats (0-1 range)
            valid_floats = [f for f in floats if 0.0 <= f <= 1.0]
            analysis['valid_floats'] = len(valid_floats)
            analysis['float_sample'] = floats[:20]

        except:
            pass

    # Look for specific patterns
    if b'serum' in data.lower():
        analysis['patterns'].append('contains_serum')
    if b'xfer' in data.lower():
        analysis['patterns'].append('contains_xfer')

    return analysis

def test_compression_cracking():
    """Test cracking compression on multiple files"""
    print("🎵 Cracking Serum FXP Compression")
    print("=" * 50)

    test_files = [
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/SAW Find me [AF].fxp",
    ]

    all_results = []

    for fxp_file in test_files:
        if not Path(fxp_file).exists():
            continue

        print(f"\\n{'='*50}")
        print(f"🔍 Analyzing: {Path(fxp_file).name}")

        # Parse FXP file
        with open(fxp_file, 'rb') as f:
            data = f.read()

        # Skip to chunk data (56 bytes header)
        chunk_data = data[56:]

        # Try all decompression methods
        decompressions = try_all_decompressions(chunk_data)

        if decompressions:
            print(f"\\n📊 Analysis of successful decompressions:")
            for result in decompressions:
                analysis = result['analysis']
                print(f"\\n🔍 {result['method']}:")
                print(f"   Size: {analysis['size']} bytes")
                print(f"   JSON: {analysis['has_json']}")
                print(f"   Strings: {analysis['has_strings']}")
                print(f"   Float count: {analysis['float_count']}")
                print(f"   Valid parameters (0-1): {analysis['valid_floats']}")
                print(f"   Patterns: {analysis['patterns']}")

                if analysis.get('text_sample'):
                    print(f"   Text sample: {analysis['text_sample'][:100]}...")

                if analysis.get('float_sample'):
                    valid_params = [f for f in analysis['float_sample'] if 0.0 <= f <= 1.0]
                    if valid_params:
                        print(f"   Valid params: {valid_params}")

        all_results.append({
            'file': fxp_file,
            'decompressions': decompressions
        })

    # Summary
    print(f"\\n{'='*50}")
    print(f"🎯 Summary:")

    best_methods = {}
    for result in all_results:
        for decomp in result['decompressions']:
            method = decomp['method']
            valid_params = decomp['analysis']['valid_floats']

            if method not in best_methods or valid_params > best_methods[method]:
                best_methods[method] = valid_params

    if best_methods:
        print(f"🏆 Best decompression methods:")
        for method, params in sorted(best_methods.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {method}: {params} valid parameters")
    else:
        print("❌ No successful decompressions found")

    return all_results

if __name__ == "__main__":
    results = test_compression_cracking()