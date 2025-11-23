#!/usr/bin/env python3
"""
🎵 ULTIMATE PRESET CONVERTER 🎵
Converts ENTIRE preset library: .fxp + .SerumPreset files
Creates the ultimate training dataset for Hermes-2-Pro fine-tuning!
"""

import struct
import zlib
import json
import time
import numpy as np
from pathlib import Path
from pedalboard import load_plugin
from typing import Dict, Any, List, Optional, Tuple
import concurrent.futures
from threading import Lock

class UltimatePresetConverter:
    """Converts both .fxp and .SerumPreset files to unified training format"""

    def __init__(self):
        self.serum = None
        self.serum_params = {}
        self.conversion_lock = Lock()
        self._load_serum()

        # Statistics
        self.stats = {
            'fxp_converted': 0,
            'serum_preset_processed': 0,
            'total_parameters_extracted': 0,
            'failed_conversions': 0,
            'skipped_non_serum': 0,
            'conversion_times': []
        }

    def _load_serum(self):
        """Load Serum plugin for parameter extraction"""
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

                    self.serum_params = dict(self.serum.parameters)
                    print(f"🎹 Loaded {path.split('/')[-1]}: {len(self.serum_params)} parameters")
                    return

                except Exception as e:
                    print(f"⚠️  Failed to load {path}: {e}")

        raise ValueError("❌ Could not load any Serum VST!")

    def convert_fxp_file(self, fxp_path: str) -> Optional[Dict[str, Any]]:
        """Convert single .fxp file using our cracked method"""
        try:
            with open(fxp_path, 'rb') as f:
                data = f.read()

            # Parse FXP header
            if not data.startswith(b'CcnK') or data[8:12] != b'FPCh':
                return None

            # 🔍 VALIDATE SERUM FX ID TO FILTER NON-SERUM PRESETS 🔍
            if len(data) >= 20:
                fx_id = struct.unpack('>I', data[16:20])[0]
                serum_fx_id = 0x58667358  # "XfsX" - Serum's magic ID

                if fx_id != serum_fx_id:
                    # Decode the FX ID to see what plugin this is actually for
                    try:
                        plugin_name = fx_id.to_bytes(4, 'big').decode('ascii', errors='ignore')
                        print(f"🎛️  Skipping {plugin_name.upper()} preset: {Path(fxp_path).name}")
                    except:
                        print(f"⚠️  Skipping non-Serum preset {Path(fxp_path).name}: FX ID {fx_id:08X}")
                    return None

            # Extract metadata
            preset_name = self._extract_name(data[28:56]).strip()
            chunk_data = data[56:]

            # 🔥 DECOMPRESS USING OUR CRACKED METHOD 🔥
            decompressed = zlib.decompress(chunk_data[4:])

            # Parse floats and extract valid parameters
            float_count = len(decompressed) // 4
            raw_floats = struct.unpack(f'<{float_count}f', decompressed)
            valid_params = [f for f in raw_floats if 0.0 <= f <= 1.0]

            # Map to Serum parameters (with thread safety)
            with self.conversion_lock:
                mapped_params = self._map_to_serum_parameters(valid_params)
                analysis = self._analyze_preset_parameters(mapped_params)

            return {
                'format': 'fxp_converted',
                'source_file': str(fxp_path),
                'preset_name': preset_name,
                'parameters': mapped_params,
                'analysis': analysis,
                'stats': {
                    'raw_floats': len(raw_floats),
                    'valid_params': len(valid_params),
                    'mapped_params': len(mapped_params),
                    'chunk_size': len(chunk_data),
                    'decompressed_size': len(decompressed)
                }
            }

        except Exception as e:
            print(f"❌ FXP conversion failed for {Path(fxp_path).name}: {e}")
            return None

    def process_serum_preset_file(self, preset_path: str) -> Optional[Dict[str, Any]]:
        """Process .SerumPreset file (binary format analysis)"""
        try:
            with open(preset_path, 'rb') as f:
                data = f.read()

            # Analyze .SerumPreset structure
            if not data.startswith(b'XferJson'):
                return None

            preset_name = Path(preset_path).stem

            # Try to extract any readable info from the binary format
            # Look for JSON-like structures
            json_patterns = []
            if b'{' in data:
                # Find potential JSON sections
                start_idx = data.find(b'{')
                if start_idx > 0:
                    try:
                        # Try to find complete JSON structure
                        json_section = data[start_idx:]
                        # This would need Kenneth Wussmann's decompression for full parsing
                        json_patterns.append(f"JSON found at offset {start_idx}")
                    except:
                        pass

            # Create analysis based on what we can extract
            analysis = {
                'instrument_type': self._guess_type_from_name(preset_name),
                'characteristics': self._extract_characteristics_from_name(preset_name),
                'complexity_score': min(len(data) / 10000, 1.0)  # Rough complexity based on file size
            }

            return {
                'format': 'serum_preset_native',
                'source_file': str(preset_path),
                'preset_name': preset_name,
                'parameters': {'note': 'Native .SerumPreset - requires Kenneth Wussmann parser for full extraction'},
                'analysis': analysis,
                'stats': {
                    'file_size': len(data),
                    'has_json': b'{' in data,
                    'json_patterns': json_patterns
                }
            }

        except Exception as e:
            print(f"❌ SerumPreset processing failed for {Path(preset_path).name}: {e}")
            return None

    def _map_to_serum_parameters(self, valid_params: List[float]) -> Dict[str, float]:
        """Map extracted parameters to Serum parameter names"""
        serum_param_names = list(self.serum_params.keys())
        mapped = {}

        # Map as many parameters as we can
        map_count = min(len(valid_params), len(serum_param_names))

        for i in range(map_count):
            param_name = serum_param_names[i]
            param_value = valid_params[i]
            mapped[param_name] = param_value

        return mapped

    def _analyze_preset_parameters(self, parameters: Dict[str, float]) -> Dict[str, Any]:
        """Analyze parameters to determine preset characteristics"""
        analysis = {
            'instrument_type': 'Unknown',
            'characteristics': [],
            'complexity_score': 0,
            'parameter_stats': {}
        }

        if not parameters:
            return analysis

        # Calculate stats
        non_zero = sum(1 for v in parameters.values() if abs(v) > 0.01)
        analysis['parameter_stats'] = {
            'total_params': len(parameters),
            'non_zero_params': non_zero,
            'complexity_score': non_zero / len(parameters)
        }

        # Analyze parameter patterns
        param_names = list(parameters.keys())

        # Look for instrument type indicators
        bass_indicators = [name for name in param_names if any(x in name.lower() for x in ['sub', 'bass', 'low'])]
        if bass_indicators:
            bass_values = [parameters[name] for name in bass_indicators]
            if any(v > 0.3 for v in bass_values):
                analysis['characteristics'].append('bass-heavy')
                analysis['instrument_type'] = 'Bass'

        lead_indicators = [name for name in param_names if any(x in name.lower() for x in ['lead', 'bright', 'high'])]
        if lead_indicators:
            lead_values = [parameters[name] for name in lead_indicators]
            if any(v > 0.3 for v in lead_values):
                analysis['characteristics'].append('bright')
                if analysis['instrument_type'] == 'Unknown':
                    analysis['instrument_type'] = 'Lead'

        # Check for complexity
        if analysis['parameter_stats']['complexity_score'] > 0.6:
            analysis['characteristics'].append('complex')

        return analysis

    def _guess_type_from_name(self, name: str) -> str:
        """Guess instrument type from filename"""
        name_lower = name.lower()

        if any(x in name_lower for x in ['bass', 'bs', 'sub']):
            return 'Bass'
        elif any(x in name_lower for x in ['lead', 'ld', 'pluck', 'pl']):
            return 'Lead'
        elif any(x in name_lower for x in ['pad', 'pd', 'string']):
            return 'Pad'
        elif any(x in name_lower for x in ['arp', 'seq', 'sequence']):
            return 'Arp'
        elif any(x in name_lower for x in ['fx', 'effect', 'noise']):
            return 'FX'
        elif any(x in name_lower for x in ['key', 'piano', 'organ']):
            return 'Keys'

        return 'Unknown'

    def _extract_characteristics_from_name(self, name: str) -> List[str]:
        """Extract characteristics from filename"""
        name_lower = name.lower()
        characteristics = []

        char_map = {
            'dark': ['dark', 'deep', 'heavy'],
            'bright': ['bright', 'sharp', 'crisp'],
            'warm': ['warm', 'smooth', 'soft'],
            'aggressive': ['aggressive', 'hard', 'brutal'],
            'ambient': ['ambient', 'atmospheric', 'space'],
            'distorted': ['distorted', 'dirty', 'gritty'],
            'clean': ['clean', 'pure', 'clear']
        }

        for char, keywords in char_map.items():
            if any(keyword in name_lower for keyword in keywords):
                characteristics.append(char)

        return characteristics

    def _extract_name(self, name_bytes: bytes) -> str:
        """Extract preset name from bytes"""
        try:
            null_idx = name_bytes.index(b'\\x00')
            name = name_bytes[:null_idx].decode('utf-8', errors='ignore')
        except (ValueError, UnicodeDecodeError):
            name = name_bytes.decode('utf-8', errors='ignore').strip('\\x00')
        return name.strip()

    def convert_preset_library(self, serum1_dir: str, serum2_dir: str, output_dir: str, max_files: int = None):
        """Convert entire preset library to unified training format"""
        print("🔥🔥🔥 ULTIMATE PRESET CONVERTER - FULL LIBRARY 🔥🔥🔥")
        print("=" * 70)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all files
        fxp_files = list(Path(serum1_dir).glob("**/*.fxp"))
        serum_files = list(Path(serum2_dir).glob("**/*.SerumPreset"))

        if max_files:
            fxp_files = fxp_files[:max_files//2]
            serum_files = serum_files[:max_files//2]

        total_files = len(fxp_files) + len(serum_files)

        print(f"📊 DATASET OVERVIEW:")
        print(f"   🎵 .fxp files (Serum 1): {len(fxp_files)}")
        print(f"   🎛️  .SerumPreset files (Serum 2): {len(serum_files)}")
        print(f"   📁 Total files: {total_files}")
        print(f"   💾 Output: {output_path}")
        print("=" * 70)

        converted_presets = []
        failed_files = []
        start_time = time.time()

        # Process .fxp files
        print(f"\\n🔓 CONVERTING .FXP FILES...")
        for i, fxp_file in enumerate(fxp_files, 1):
            file_start = time.time()

            try:
                result = self.convert_fxp_file(str(fxp_file))
                if result:
                    converted_presets.append(result)
                    self.stats['fxp_converted'] += 1
                    self.stats['total_parameters_extracted'] += result['stats']['mapped_params']
                else:
                    # Check if this was a skipped non-Serum preset vs actual failure
                    with open(fxp_file, 'rb') as f:
                        data = f.read()
                    if (len(data) >= 20 and
                        data.startswith(b'CcnK') and
                        data[8:12] == b'FPCh' and
                        struct.unpack('>I', data[16:20])[0] != 0x58667358):
                        self.stats['skipped_non_serum'] += 1
                    else:
                        failed_files.append(str(fxp_file))
                        self.stats['failed_conversions'] += 1

                conversion_time = time.time() - file_start
                self.stats['conversion_times'].append(conversion_time)

                # Progress
                if i % 100 == 0 or i == len(fxp_files):
                    avg_time = np.mean(self.stats['conversion_times'][-50:])
                    remaining_fxp = len(fxp_files) - i
                    eta_fxp = remaining_fxp * avg_time

                    print(f"📊 FXP Progress: {i}/{len(fxp_files)} ({i/len(fxp_files)*100:.1f}%) | "
                          f"ETA: {eta_fxp/60:.1f}m | Avg: {avg_time:.2f}s/file")

            except Exception as e:
                failed_files.append(str(fxp_file))
                self.stats['failed_conversions'] += 1

        # Process .SerumPreset files
        print(f"\\n🎛️  PROCESSING .SERUMPRESET FILES...")
        for i, preset_file in enumerate(serum_files, 1):
            try:
                result = self.process_serum_preset_file(str(preset_file))
                if result:
                    converted_presets.append(result)
                    self.stats['serum_preset_processed'] += 1
                else:
                    failed_files.append(str(preset_file))
                    self.stats['failed_conversions'] += 1

                # Progress
                if i % 50 == 0 or i == len(serum_files):
                    print(f"📊 SerumPreset Progress: {i}/{len(serum_files)} ({i/len(serum_files)*100:.1f}%)")

            except Exception as e:
                failed_files.append(str(preset_file))
                self.stats['failed_conversions'] += 1

        total_time = time.time() - start_time

        # Save the massive dataset
        print(f"\\n💾 SAVING ULTIMATE TRAINING DATASET...")

        # Save main dataset
        dataset_file = output_path / "ultimate_serum_dataset.json"
        with open(dataset_file, 'w') as f:
            json.dump(converted_presets, f, indent=2)

        # Save statistics
        serum_files_found = total_files - self.stats['skipped_non_serum']
        final_stats = {
            'conversion_summary': {
                'total_files_processed': total_files,
                'serum_files_found': serum_files_found,
                'fxp_converted': self.stats['fxp_converted'],
                'serum_presets_processed': self.stats['serum_preset_processed'],
                'total_successful': len(converted_presets),
                'total_failed': len(failed_files),
                'skipped_non_serum': self.stats['skipped_non_serum'],
                'success_rate_all_files': len(converted_presets) / total_files * 100,
                'success_rate_serum_only': len(converted_presets) / serum_files_found * 100 if serum_files_found > 0 else 0,
                'total_time_minutes': total_time / 60,
                'avg_time_per_file': total_time / total_files,
                'total_parameters_extracted': self.stats['total_parameters_extracted']
            },
            'dataset_composition': {
                'fxp_presets': self.stats['fxp_converted'],
                'native_serum_presets': self.stats['serum_preset_processed']
            },
            'failed_files': failed_files,
            'conversion_date': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        stats_file = output_path / "conversion_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(final_stats, f, indent=2)

        # Save failed files list
        if failed_files:
            failed_file = output_path / "failed_conversions.txt"
            with open(failed_file, 'w') as f:
                f.write('\\n'.join(failed_files))

        # Final results
        print(f"\\n🎉 ULTIMATE CONVERSION COMPLETE!")
        print("=" * 70)
        print(f"✅ Total successful: {len(converted_presets)}")
        print(f"   🔓 .fxp converted: {self.stats['fxp_converted']}")
        print(f"   🎛️  .SerumPreset processed: {self.stats['serum_preset_processed']}")
        print(f"❌ Total failed: {len(failed_files)}")
        print(f"⚠️  Skipped non-Serum: {self.stats['skipped_non_serum']}")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"📈 Success rate (all files): {len(converted_presets)/total_files*100:.1f}%")
        if serum_files_found > 0:
            print(f"🎯 Success rate (Serum only): {len(converted_presets)/serum_files_found*100:.1f}%")
        print(f"🎛️  Parameters extracted: {self.stats['total_parameters_extracted']:,}")
        print(f"💾 Dataset size: {dataset_file.stat().st_size/1024/1024:.1f} MB")

        return converted_presets, final_stats

def main():
    """Run the ultimate conversion"""
    try:
        converter = UltimatePresetConverter()

        # Convert everything
        presets, stats = converter.convert_preset_library(
            serum1_dir="/Users/brentpinero/Documents/serum_llm_2/Serum_1_Presets",
            serum2_dir="/Users/brentpinero/Documents/serum_llm_2/Serum_2_Presets",
            output_dir="/Users/brentpinero/Documents/serum_llm_2/ultimate_training_dataset",
            max_files=None  # Convert ALL files
        )

        print(f"\\n🚀 READY FOR HERMES-2-PRO TRAINING!")
        print(f"📊 Dataset: {len(presets)} presets")
        print(f"📁 Location: ultimate_training_dataset/")

    except Exception as e:
        print(f"❌ Conversion failed: {e}")

if __name__ == "__main__":
    main()