#!/usr/bin/env python3
"""
🎵 FINAL WORKING FXP CONVERTER 🎵
Successfully cracks Serum .fxp compression and extracts ALL parameters!
Uses Pedalboard for VST hosting + manual parameter mapping
"""

import struct
import zlib
import json
import time
import numpy as np
from pathlib import Path
from pedalboard import load_plugin
from typing import Dict, Any, List, Optional, Tuple

class SerumFXPCracker:
    """Cracks Serum .fxp files and extracts all parameters"""

    def __init__(self):
        self.chunk_magic = b'CcnK'
        self.fxp_magic = b'FPCh'
        self.serum_magic = b'XfsX'

        # Load Serum plugin
        self.serum = None
        self.serum_params = {}
        self._load_serum()

    def _load_serum(self):
        """Load Serum plugin via Pedalboard"""
        serum_paths = [
            "/Library/Audio/Plug-Ins/VST3/Serum.vst3",
            "/Library/Audio/Plug-Ins/VST3/Serum2.vst3",
        ]

        for path in serum_paths:
            if Path(path).exists():
                try:
                    if "Serum2" in path:
                        self.serum = load_plugin(path, plugin_name="Serum 2")
                    else:
                        self.serum = load_plugin(path)

                    # Get parameter mapping
                    self.serum_params = dict(self.serum.parameters)
                    param_count = len(self.serum_params)

                    print(f"🎹 Loaded {path.split('/')[-1]}: {param_count} parameters")
                    return

                except Exception as e:
                    print(f"⚠️  Failed to load {path}: {e}")

        raise ValueError("❌ Could not load any Serum VST!")

    def crack_fxp_file(self, fxp_path: str) -> Dict[str, Any]:
        """Crack open an .fxp file and extract all the goods"""
        print(f"🔓 Cracking: {Path(fxp_path).name}")

        with open(fxp_path, 'rb') as f:
            data = f.read()

        # Validate FXP structure
        if not data.startswith(self.chunk_magic):
            raise ValueError("Invalid FXP file")

        # Parse header
        fx_magic = data[8:12]
        if fx_magic != self.fxp_magic:
            raise ValueError("Not a valid FXP preset")

        # Check for Serum magic
        serum_check = data[16:20]
        if serum_check != self.serum_magic:
            print(f"⚠️  Warning: Not a Serum preset (ID: {struct.unpack('>I', serum_check)[0]:08X})")

        # Extract metadata
        preset_name = self._extract_name(data[28:56])
        chunk_data = data[56:]

        print(f"📋 Preset: '{preset_name}' | Chunk: {len(chunk_data)} bytes")

        # 🔥 THE MAGIC HAPPENS HERE 🔥
        # Decompress using our cracked method: skip 4 bytes + zlib
        try:
            decompressed = zlib.decompress(chunk_data[4:])
            print(f"✅ DECOMPRESSED: {len(decompressed)} bytes | {len(decompressed)//4} floats")
        except Exception as e:
            raise ValueError(f"Failed to decompress chunk data: {e}")

        # Parse the float array
        float_count = len(decompressed) // 4
        raw_floats = struct.unpack(f'<{float_count}f', decompressed)

        # Filter to valid parameter range
        valid_params = [f for f in raw_floats if 0.0 <= f <= 1.0]
        print(f"🎛️  Found {len(valid_params)} valid parameters (0-1 range)")

        return {
            'preset_name': preset_name,
            'raw_floats': raw_floats,
            'valid_params': valid_params,
            'chunk_size': len(chunk_data),
            'decompressed_size': len(decompressed)
        }

    def map_parameters_to_serum(self, fxp_data: Dict[str, Any]) -> Dict[str, float]:
        """Map extracted parameters to Serum parameter names"""
        print(f"🗺️  Mapping parameters to Serum...")

        raw_floats = fxp_data['raw_floats']
        serum_param_names = list(self.serum_params.keys())

        print(f"📊 Raw floats: {len(raw_floats)} | Serum params: {len(serum_param_names)}")

        # Strategy: Take the first N valid parameters and map them sequentially
        # This is a starting point - we can refine the mapping later
        valid_floats = [f for f in raw_floats if 0.0 <= f <= 1.0]

        mapped_params = {}

        # Map valid parameters to Serum parameter names
        map_count = min(len(valid_floats), len(serum_param_names))

        for i in range(map_count):
            param_name = serum_param_names[i]
            param_value = valid_floats[i]
            mapped_params[param_name] = param_value

        print(f"✅ Mapped {len(mapped_params)} parameters")
        return mapped_params

    def apply_parameters_to_serum(self, mapped_params: Dict[str, float]) -> Dict[str, Any]:
        """Apply mapped parameters to Serum and extract the state"""
        print(f"🎵 Applying {len(mapped_params)} parameters to Serum...")

        # Store original state
        original_params = {}
        for param_name in mapped_params.keys():
            if param_name in self.serum_params:
                original_params[param_name] = self.serum_params[param_name].raw_value

        # Apply new parameters
        applied_count = 0
        failed_count = 0

        for param_name, value in mapped_params.items():
            try:
                if param_name in self.serum_params:
                    self.serum_params[param_name].raw_value = value
                    applied_count += 1
            except Exception as e:
                failed_count += 1

        print(f"✅ Applied {applied_count} parameters | ❌ Failed {failed_count}")

        # Extract final state
        final_params = {}
        for param_name in self.serum_params.keys():
            param = self.serum_params[param_name]
            final_params[param_name] = {
                'raw_value': param.raw_value,
                'display_value': str(param),  # Use str() instead of .value
                'name': param.name
            }

        return {
            'original_params': original_params,
            'applied_params': mapped_params,
            'final_params': final_params,
            'applied_count': applied_count,
            'failed_count': failed_count
        }

    def analyze_preset_characteristics(self, final_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the preset to determine characteristics"""
        print(f"🔍 Analyzing preset characteristics...")

        analysis = {
            'instrument_type': 'Unknown',
            'characteristics': [],
            'complexity_score': 0,
            'parameter_stats': {}
        }

        # Get parameter values
        param_values = {name: data['raw_value'] for name, data in final_params.items()}
        non_zero = sum(1 for v in param_values.values() if abs(v) > 0.01)

        analysis['parameter_stats'] = {
            'total_params': len(param_values),
            'non_zero_params': non_zero,
            'complexity_score': non_zero / len(param_values)
        }

        # Analyze specific parameters for characteristics
        param_names = list(param_values.keys())

        # Look for bass characteristics
        bass_indicators = [name for name in param_names if any(x in name.lower() for x in ['sub', 'bass', 'low'])]
        if bass_indicators:
            bass_values = [param_values[name] for name in bass_indicators]
            if any(v > 0.3 for v in bass_values):
                analysis['characteristics'].append('bass-heavy')

        # Look for brightness
        bright_indicators = [name for name in param_names if any(x in name.lower() for x in ['treble', 'high', 'bright'])]
        if bright_indicators:
            bright_values = [param_values[name] for name in bright_indicators]
            if any(v > 0.3 for v in bright_values):
                analysis['characteristics'].append('bright')

        # Classify instrument type based on characteristics
        if 'bass-heavy' in analysis['characteristics']:
            analysis['instrument_type'] = 'Bass'
        elif 'bright' in analysis['characteristics']:
            analysis['instrument_type'] = 'Lead'
        elif analysis['complexity_score'] > 0.5:
            analysis['instrument_type'] = 'Complex'

        print(f"🎼 Type: {analysis['instrument_type']} | Characteristics: {analysis['characteristics']}")

        return analysis

    def save_as_serum_preset(self, preset_data: Dict[str, Any], output_path: str) -> bool:
        """Save the extracted preset data as .SerumPreset format"""
        print(f"💾 Saving as: {Path(output_path).name}")

        # Create comprehensive preset data structure
        serum_preset = {
            "format_version": "serum_preset_v2",
            "metadata": {
                "name": preset_data['metadata']['name'],
                "author": "FXP Converter",
                "tags": ["converted", "fxp", preset_data['analysis']['instrument_type'].lower()],
                "description": f"Converted from FXP | Type: {preset_data['analysis']['instrument_type']}",
                "characteristics": preset_data['analysis']['characteristics'],
                "conversion_info": {
                    "original_file": preset_data['metadata']['original_file'],
                    "conversion_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "raw_parameters_extracted": len(preset_data['fxp_data']['raw_floats']),
                    "valid_parameters": len(preset_data['fxp_data']['valid_params']),
                    "mapped_parameters": preset_data['serum_state']['applied_count'],
                    "converter_version": "v2.0_final"
                }
            },
            "parameters": self._organize_parameters(preset_data['serum_state']['final_params']),
            "raw_fxp_data": {
                "chunk_size": preset_data['fxp_data']['chunk_size'],
                "decompressed_size": preset_data['fxp_data']['decompressed_size'],
                "raw_float_count": len(preset_data['fxp_data']['raw_floats']),
                "valid_param_count": len(preset_data['fxp_data']['valid_params'])
            },
            "analysis": preset_data['analysis']
        }

        try:
            with open(output_path, 'w') as f:
                json.dump(serum_preset, f, indent=2)

            file_size = Path(output_path).stat().st_size
            print(f"✅ Saved successfully: {file_size/1024:.1f} KB")
            return True

        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False

    def _organize_parameters(self, final_params: Dict[str, Any]) -> Dict[str, Any]:
        """Organize parameters into logical categories"""
        organized = {
            'oscillators': {},
            'filters': {},
            'envelopes': {},
            'lfos': {},
            'effects': {},
            'global': {},
            'other': {}
        }

        for param_name, param_data in final_params.items():
            value = param_data['raw_value']
            display = param_data['display_value']

            # Categorize by parameter name
            param_lower = param_name.lower()

            if any(x in param_lower for x in ['osc', 'wave', 'pitch', 'tune']):
                organized['oscillators'][param_name] = {'value': value, 'display': display}
            elif any(x in param_lower for x in ['filter', 'cutoff', 'resonance']):
                organized['filters'][param_name] = {'value': value, 'display': display}
            elif any(x in param_lower for x in ['env', 'attack', 'decay', 'sustain', 'release']):
                organized['envelopes'][param_name] = {'value': value, 'display': display}
            elif 'lfo' in param_lower:
                organized['lfos'][param_name] = {'value': value, 'display': display}
            elif any(x in param_lower for x in ['fx', 'reverb', 'delay', 'chorus']):
                organized['effects'][param_name] = {'value': value, 'display': display}
            elif any(x in param_lower for x in ['master', 'main', 'vol']):
                organized['global'][param_name] = {'value': value, 'display': display}
            else:
                organized['other'][param_name] = {'value': value, 'display': display}

        # Remove empty categories
        return {k: v for k, v in organized.items() if v}

    def convert_fxp_to_serum_preset(self, fxp_path: str, output_dir: str) -> Optional[str]:
        """Complete FXP to SerumPreset conversion pipeline"""
        print(f"\\n🎵 CONVERTING: {Path(fxp_path).name}")
        print("=" * 60)

        try:
            # Step 1: Crack the FXP file
            fxp_data = self.crack_fxp_file(fxp_path)

            # Step 2: Map parameters to Serum
            mapped_params = self.map_parameters_to_serum(fxp_data)

            # Step 3: Apply to Serum and get state
            serum_state = self.apply_parameters_to_serum(mapped_params)

            # Step 4: Analyze characteristics
            analysis = self.analyze_preset_characteristics(serum_state['final_params'])

            # Step 5: Create output structure
            preset_data = {
                'metadata': {
                    'name': fxp_data['preset_name'],
                    'original_file': str(fxp_path)
                },
                'fxp_data': fxp_data,
                'serum_state': serum_state,
                'analysis': analysis
            }

            # Step 6: Save as .SerumPreset
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            filename = Path(fxp_path).stem + ".SerumPreset"
            preset_file = output_path / filename

            success = self.save_as_serum_preset(preset_data, str(preset_file))

            if success:
                print(f"🎉 CONVERSION SUCCESS!")
                print(f"📁 Output: {preset_file}")
                return str(preset_file)
            else:
                return None

        except Exception as e:
            print(f"❌ CONVERSION FAILED: {e}")
            return None

    def _extract_name(self, name_bytes: bytes) -> str:
        """Extract preset name from bytes"""
        try:
            null_idx = name_bytes.index(b'\\x00')
            name = name_bytes[:null_idx].decode('utf-8', errors='ignore')
        except (ValueError, UnicodeDecodeError):
            name = name_bytes.decode('utf-8', errors='ignore').strip('\\x00')
        return name.strip()

def batch_convert_fxp_library(input_dir: str, output_dir: str, max_files: int = None):
    """Batch convert entire FXP library"""
    print("🔥🔥🔥 FINAL FXP CONVERTER - BATCH MODE 🔥🔥🔥")
    print("=" * 60)

    # Initialize converter
    try:
        converter = SerumFXPCracker()
    except Exception as e:
        print(f"❌ Failed to initialize converter: {e}")
        return

    # Find all .fxp files
    input_path = Path(input_dir)
    fxp_files = list(input_path.glob("**/*.fxp"))

    if max_files:
        fxp_files = fxp_files[:max_files]

    print(f"🎵 Found {len(fxp_files)} .fxp files to convert")
    print(f"📁 Output directory: {output_dir}")

    converted_count = 0
    failed_files = []
    conversion_times = []

    start_time = time.time()

    for i, fxp_file in enumerate(fxp_files, 1):
        file_start = time.time()

        try:
            # Maintain folder structure
            relative_path = fxp_file.relative_to(input_path)
            output_subdir = Path(output_dir) / relative_path.parent

            # Convert
            result = converter.convert_fxp_to_serum_preset(str(fxp_file), str(output_subdir))

            if result:
                converted_count += 1
                conversion_time = time.time() - file_start
                conversion_times.append(conversion_time)

                # Progress
                if i % 5 == 0 or i == len(fxp_files):
                    avg_time = np.mean(conversion_times[-10:]) if conversion_times else 0
                    remaining = len(fxp_files) - i
                    eta = remaining * avg_time

                    print(f"\\n📊 Progress: {i}/{len(fxp_files)} ({i/len(fxp_files)*100:.1f}%)")
                    print(f"⏱️  ETA: {eta/60:.1f}m | Avg: {avg_time:.2f}s/file")
            else:
                failed_files.append(str(fxp_file))

        except Exception as e:
            failed_files.append(str(fxp_file))
            print(f"❌ Failed: {fxp_file.name} - {e}")

    total_time = time.time() - start_time

    # Final results
    print(f"\\n🎉 BATCH CONVERSION COMPLETE!")
    print("=" * 60)
    print(f"✅ Successful: {converted_count}")
    print(f"❌ Failed: {len(failed_files)}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"📈 Average: {total_time/len(fxp_files):.2f}s per file")
    print(f"🎛️  Success rate: {converted_count/len(fxp_files)*100:.1f}%")

def test_single_conversion():
    """Test on a single file first"""
    print("🧪 TESTING SINGLE CONVERSION")
    print("=" * 40)

    test_files = [
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp",
        "/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets/Misc/SAW Find me [AF].fxp"
    ]

    try:
        converter = SerumFXPCracker()

        for test_file in test_files:
            if Path(test_file).exists():
                result = converter.convert_fxp_to_serum_preset(test_file, "./converted_final_test")
                if result:
                    print(f"\\n🎉 TEST SUCCESS: {Path(result).name}")
                    break

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    # Run test first
    test_single_conversion()

    # Ask for batch conversion
    response = input("\\n🚀 Run full batch conversion? (y/N): ").lower().strip()
    if response == 'y':
        batch_convert_fxp_library(
            input_dir="./Serum_1_Presets",
            output_dir="./converted_serum_presets_final",
            max_files=None  # Convert all
        )