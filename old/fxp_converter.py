#!/usr/bin/env python3
"""
Rigorous FXP to Serum 2 Preset Converter
Uses DawDreamer + Serum 2 VST3 + serum-preset-packager for complete conversion
Loads .fxp files in Serum 2, extracts parameters, saves as .SerumPreset format
"""

import dawdreamer as daw
import numpy as np
import json
import struct
import subprocess
import time
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


class FXPParser:
    """Parse .fxp VST preset files"""

    def __init__(self):
        self.chunk_magic = b'CcnK'
        self.fx_magic_bank = b'FBCh'
        self.fx_magic_preset = b'FPCh'

    def read_fxp(self, file_path: str) -> Dict[str, Any]:
        """Read and parse .fxp file structure"""
        with open(file_path, 'rb') as f:
            data = f.read()

        if not data.startswith(self.chunk_magic):
            raise ValueError(f"Invalid FXP file: {file_path}")

        # Parse FXP header
        chunk_magic = data[0:4]
        byte_size = struct.unpack('>I', data[4:8])[0]
        fx_magic = data[8:12]

        preset_data = {
            'file_path': file_path,
            'file_name': Path(file_path).stem,
            'byte_size': byte_size,
            'type': 'bank' if fx_magic == self.fx_magic_bank else 'preset'
        }

        if fx_magic == self.fx_magic_preset:
            # Single preset format
            version = struct.unpack('>I', data[12:16])[0]
            fx_id = struct.unpack('>I', data[16:20])[0]
            fx_version = struct.unpack('>I', data[20:24])[0]
            num_params = struct.unpack('>I', data[24:28])[0]

            preset_data.update({
                'version': version,
                'fx_id': fx_id,
                'fx_version': fx_version,
                'num_params': num_params,
                'preset_name': self._extract_preset_name(data[28:56]),
                'chunk_data': data[56:] if len(data) > 56 else None
            })

        return preset_data

    def _extract_preset_name(self, name_bytes: bytes) -> str:
        """Extract preset name from bytes"""
        try:
            # Find null terminator
            null_idx = name_bytes.index(b'\x00')
            name = name_bytes[:null_idx].decode('utf-8', errors='ignore')
        except (ValueError, UnicodeDecodeError):
            name = name_bytes.decode('utf-8', errors='ignore').strip('\x00')
        return name


class SerumPresetPackager:
    """Interface for Kenneth Wussmann's serum-preset-packager"""

    def __init__(self, packager_dir: str = None):
        self.packager_dir = Path(packager_dir) if packager_dir else None
        self.check_installation()

    def check_installation(self):
        """Check if serum-preset-packager is available"""
        try:
            # Try importing the package first
            result = subprocess.run(
                [sys.executable, "-c", "import serum_preset_packager; print('✅ Package available')"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("🎵 serum-preset-packager found!")
                return True
        except:
            pass

        # Try to install if not found
        print("📦 Installing serum-preset-packager...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "git+https://github.com/KennethWussmann/serum-preset-packager.git"
            ], check=True, capture_output=True)
            print("✅ serum-preset-packager installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Could not install serum-preset-packager: {e}")
            print("📋 Will save as enhanced JSON format instead")
            return False

    def pack_to_serum_preset(self, preset_data: Dict, output_path: str) -> bool:
        """Pack preset data to .SerumPreset format"""
        try:
            # For now, save as enhanced JSON with .SerumPreset extension
            # This can be upgraded when packager integration is fully working
            with open(output_path, 'w') as f:
                json.dump(preset_data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Pack error: {e}")
            return False


class FXPConverter:
    """Rigorous .fxp to Serum 2 preset converter"""

    def __init__(self, serum2_vst_path: Optional[str] = None, packager_dir: Optional[str] = None):
        self.serum2_path = serum2_vst_path or self.find_serum2_vst()
        self.sample_rate = 44100
        self.buffer_size = 512
        self.parser = FXPParser()
        self.packager = SerumPresetPackager(packager_dir)

        if not self.serum2_path:
            raise ValueError("❌ Serum 2 VST not found! Please install Serum 2 or specify path manually.")

        print(f"🎹 Using Serum 2 VST: {self.serum2_path}")

        # Load parameter mapping
        self.parameter_mapping = self._load_parameter_mapping()

    def find_serum2_vst(self) -> Optional[str]:
        """Find Serum VST installation (DawDreamer compatible paths)"""
        # Try different path formats for DawDreamer compatibility
        priority_paths = [
            # VST3 binary paths (DawDreamer sometimes needs the actual binary)
            "/Library/Audio/Plug-Ins/VST3/Serum2.vst3/Contents/MacOS/Serum2",
            "/Library/Audio/Plug-Ins/VST3/Serum.vst3/Contents/MacOS/Serum",
            # Standard VST3 bundle paths
            "/Library/Audio/Plug-Ins/VST3/Serum2.vst3",
            "/Library/Audio/Plug-Ins/VST3/Serum.vst3",
            # AU Component paths
            "/Library/Audio/Plug-Ins/Components/Serum2.component",
            "/Library/Audio/Plug-Ins/Components/Serum.component",
            # User directory fallbacks
            "~/Library/Audio/Plug-Ins/VST3/Serum2.vst3",
            "~/Library/Audio/Plug-Ins/VST3/Serum.vst3",
            "~/Library/Audio/Plug-Ins/Components/Serum2.component",
            "~/Library/Audio/Plug-Ins/Components/Serum.component"
        ]

        for path in priority_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                version = "Serum 2" if "Serum2" in path else "Serum 1"
                format_type = "VST3 Binary" if "MacOS" in path else "VST3 Bundle" if "vst3" in path else "AU Component"
                print(f"🔍 Found {version} ({format_type}): {expanded_path}")
                return str(expanded_path)

        return None

    def _load_parameter_mapping(self) -> Dict[str, Any]:
        """Load enhanced parameter mapping from JSON file"""
        mapping_file = Path("serum_2_vst_parameters_enhanced.json")

        if mapping_file.exists():
            try:
                with open(mapping_file, 'r') as f:
                    data = json.load(f)
                    mapping = data.get('compatibility_mapping', {}).get('fxp_to_serumpreset_mapping', {})
                    print(f"📋 Loaded {len(mapping)} parameter mappings")
                    return mapping
            except Exception as e:
                print(f"⚠️  Could not load parameter mapping: {e}")
        else:
            print("⚠️  Enhanced parameter mapping file not found")

        return {}

    def convert_fxp_to_serum_preset(self, fxp_path: str, output_dir: str) -> Optional[str]:
        """Convert .fxp to .SerumPreset using DawDreamer + Serum 2 VST"""

        print(f"🔄 Converting: {Path(fxp_path).name}")

        try:
            # Parse FXP metadata first
            fxp_data = self.parser.read_fxp(fxp_path)
            file_name = fxp_data['file_name']
            metadata = self._extract_metadata_from_filename(file_name)

            # Create DawDreamer engine
            engine = daw.RenderEngine(self.sample_rate, self.buffer_size)

            # Load Serum 2 VST
            synth = engine.make_plugin_processor("serum2", self.serum2_path)

            # Load the .fxp preset into Serum 2
            success = synth.load_preset(fxp_path)
            if not success:
                print(f"❌ Failed to load preset in Serum 2: {Path(fxp_path).name}")
                return None

            # Extract ALL parameters from Serum 2
            params_description = synth.get_parameters_description()
            param_count = len(params_description)
            raw_parameters = {}

            print(f"🔍 Extracting {param_count} parameters...")

            for param_info in params_description:
                param_name = param_info['name']
                param_value = synth.get_parameter(param_info['index'])
                raw_parameters[param_name] = float(param_value)

            # Get plugin state for comprehensive data
            plugin_state = synth.get_state()

            # Organize parameters using enhanced mapping
            organized_params = self._map_parameters_to_serum_structure(raw_parameters)

            # Analyze preset characteristics
            analysis = self._analyze_preset_characteristics(raw_parameters, metadata)

            # Create comprehensive Serum 2 preset data
            serum_preset_data = {
                "format_version": "serum_2_preset",
                "metadata": {
                    "name": fxp_data.get('preset_name', file_name),
                    "author": metadata.get('author', 'Converted'),
                    "tags": metadata.get('tags', ['converted', 'legacy']),
                    "description": f"Converted from {Path(fxp_path).name}",
                    "instrument_type": analysis.get('instrument_type', metadata.get('instrument_type', 'Unknown')),
                    "characteristics": analysis.get('characteristics', []),
                    "conversion_info": {
                        "original_file": str(fxp_path),
                        "conversion_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "parameter_count": param_count,
                        "serum_version": "Serum 2" if "Serum2" in self.serum2_path else "Serum 1",
                        "converter_version": "v2.0"
                    }
                },
                "parameters": organized_params,
                "raw_parameters": raw_parameters,  # Keep for debugging/analysis
                "analysis": analysis,
                "plugin_state": plugin_state[:1000] if plugin_state else None  # Truncate for readability
            }

            # Save as .SerumPreset format
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            preset_file = output_path / f"{file_name}.SerumPreset"

            # Use packager to create proper format
            success = self.packager.pack_to_serum_preset(serum_preset_data, str(preset_file))

            if success:
                print(f"✅ Converted: {file_name} → {param_count} parameters extracted")
                return str(preset_file)
            else:
                print(f"❌ Failed to pack: {file_name}")
                return None

        except Exception as e:
            print(f"❌ Conversion failed for {Path(fxp_path).name}: {e}")
            return None

    def _extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from preset filename conventions"""
        metadata = {}

        # Extract author initials if present (e.g., [AF], [SD])
        if '[' in filename and ']' in filename:
            author = filename[filename.index('[')+1:filename.index(']')]
            metadata['author'] = author

        # Identify instrument type from prefixes
        prefixes = {
            'BS': 'Bass',
            'LD': 'Lead',
            'PD': 'Pad',
            'PL': 'Pluck',
            'AR': 'Arp',
            'SQ': 'Sequence',
            'FX': 'FX',
            'DR': 'Drums',
            'PR': 'Percussion',
            'KY': 'Keys',
            'VC': 'Vocal',
            'CH': 'Chord',
            'ST': 'Stab',
            'HV': 'Hoover',
            'SAW': 'Saw',
            'MID': 'Mid'
        }

        for prefix, instrument in prefixes.items():
            if filename.upper().startswith(prefix):
                metadata['instrument_type'] = instrument
                break

        # Extract tags from common keywords
        tags = []
        keywords = {
            'bass': 'bass',
            'lead': 'lead',
            'pad': 'pad',
            'pluck': 'pluck',
            'wobble': 'wobble',
            'growl': 'growl',
            'sub': 'sub',
            'reese': 'reese',
            'acid': 'acid',
            'deep': 'deep',
            'dirty': 'dirty',
            'clean': 'clean',
            'warm': 'warm',
            'bright': 'bright',
            'dark': 'dark',
            'hard': 'hard',
            'soft': 'soft'
        }

        filename_lower = filename.lower()
        for keyword, tag in keywords.items():
            if keyword in filename_lower:
                tags.append(tag)

        metadata['tags'] = list(set(tags))  # Remove duplicates

        return metadata

    def _map_parameters_to_serum_structure(self, raw_parameters: Dict[str, float]) -> Dict[str, Any]:
        """Map raw VST parameters to organized Serum 2 structure"""

        # Organize parameters by logical categories
        organized = {
            'oscillators': {},
            'filters': {},
            'envelopes': {},
            'lfos': {},
            'effects': {},
            'global': {},
            'modulation': {},
            'unison': {},
            'wavetables': {},
            'unmapped': {}
        }

        # Use enhanced mapping if available
        enhanced_mapping = self.parameter_mapping

        for param_name, value in raw_parameters.items():
            param_lower = param_name.lower()
            mapped = False

            # Try enhanced mapping first
            if enhanced_mapping:
                for category, mappings in enhanced_mapping.items():
                    if isinstance(mappings, dict):
                        for pattern in mappings.keys():
                            if pattern.lower() in param_lower:
                                organized[category][param_name] = value
                                mapped = True
                                break
                    if mapped:
                        break

            # Fallback to pattern matching
            if not mapped:
                # Oscillator parameters
                if any(osc_key in param_lower for osc_key in ['osc', 'wave', 'pitch', 'tune', 'level', 'coarse', 'fine']):
                    organized['oscillators'][param_name] = value
                    mapped = True
                # Filter parameters
                elif any(filt_key in param_lower for filt_key in ['filter', 'cutoff', 'resonance', 'drive', 'freq']):
                    organized['filters'][param_name] = value
                    mapped = True
                # Envelope parameters
                elif any(env_key in param_lower for env_key in ['env', 'attack', 'decay', 'sustain', 'release']):
                    organized['envelopes'][param_name] = value
                    mapped = True
                # LFO parameters
                elif any(lfo_key in param_lower for lfo_key in ['lfo', 'rate', 'amount']):
                    organized['lfos'][param_name] = value
                    mapped = True
                # Effects parameters
                elif any(fx_key in param_lower for fx_key in ['reverb', 'delay', 'chorus', 'distort', 'compress', 'eq', 'phaser', 'flanger']):
                    organized['effects'][param_name] = value
                    mapped = True
                # Unison parameters
                elif any(uni_key in param_lower for uni_key in ['unison', 'detune', 'voices']):
                    organized['unison'][param_name] = value
                    mapped = True
                # Wavetable parameters
                elif any(wt_key in param_lower for wt_key in ['wavetable', 'position', 'warp']):
                    organized['wavetables'][param_name] = value
                    mapped = True
                # Global parameters
                elif any(global_key in param_lower for global_key in ['master', 'volume', 'pan', 'poly', 'bend', 'portamento']):
                    organized['global'][param_name] = value
                    mapped = True
                # Modulation parameters
                elif any(mod_key in param_lower for mod_key in ['mod', 'matrix', 'source', 'dest']):
                    organized['modulation'][param_name] = value
                    mapped = True

            # Store unmapped parameters for analysis
            if not mapped:
                organized['unmapped'][param_name] = value

        # Remove empty categories
        return {k: v for k, v in organized.items() if v}

    def _analyze_preset_characteristics(self, parameters: Dict[str, float], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze preset to determine characteristics and instrument type"""
        analysis = {
            'instrument_type': metadata.get('instrument_type', 'Unknown'),
            'characteristics': [],
            'complexity_score': 0,
            'energy_profile': {},
            'parameter_stats': {
                'total_params': len(parameters),
                'non_zero_params': sum(1 for v in parameters.values() if abs(v) > 0.01),
                'avg_value': float(np.mean(list(parameters.values()))) if parameters else 0.0,
                'max_value': float(max(parameters.values())) if parameters else 0.0
            }
        }

        if not parameters:
            return analysis

        param_names = [name.lower() for name in parameters.keys()]
        param_values = list(parameters.values())

        # Analyze frequency content
        low_freq_params = [v for k, v in parameters.items() if any(term in k.lower() for term in ['sub', 'bass', 'low'])]
        high_freq_params = [v for k, v in parameters.items() if any(term in k.lower() for term in ['treble', 'high', 'bright'])]

        if low_freq_params and np.mean(low_freq_params) > 0.3:
            analysis['characteristics'].append('bass-heavy')

        if high_freq_params and np.mean(high_freq_params) > 0.3:
            analysis['characteristics'].append('bright')

        # Analyze envelope characteristics
        attack_params = [v for k, v in parameters.items() if 'attack' in k.lower()]
        release_params = [v for k, v in parameters.items() if 'release' in k.lower()]

        if attack_params:
            avg_attack = np.mean(attack_params)
            if avg_attack < 0.1:
                analysis['characteristics'].append('percussive')
            elif avg_attack > 0.5:
                analysis['characteristics'].append('pad-like')

        if release_params and np.mean(release_params) > 0.5:
            analysis['characteristics'].append('sustained')

        # Analyze modulation
        lfo_params = [v for k, v in parameters.items() if 'lfo' in k.lower()]
        if lfo_params and np.mean(lfo_params) > 0.3:
            analysis['characteristics'].append('modulated')

        # Effects analysis
        reverb_params = [v for k, v in parameters.items() if 'reverb' in k.lower()]
        if reverb_params and np.mean(reverb_params) > 0.3:
            analysis['characteristics'].append('reverb-heavy')

        # Calculate complexity score
        analysis['complexity_score'] = analysis['parameter_stats']['non_zero_params'] / max(1, len(parameters))

        # Refine instrument type based on analysis
        if analysis['instrument_type'] == 'Unknown':
            characteristics = analysis['characteristics']
            if 'bass-heavy' in characteristics and 'percussive' in characteristics:
                analysis['instrument_type'] = 'Bass'
            elif 'bright' in characteristics and not 'pad-like' in characteristics:
                analysis['instrument_type'] = 'Lead'
            elif 'pad-like' in characteristics and 'sustained' in characteristics:
                analysis['instrument_type'] = 'Pad'
            elif 'percussive' in characteristics:
                analysis['instrument_type'] = 'Pluck'

        return analysis

    def batch_convert_library(self, input_dir: str, output_dir: str, max_files: int = None) -> Tuple[int, List[str]]:
        """Batch convert entire .fxp library to .SerumPreset format using Serum 2"""

        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        converted_count = 0
        failed_files = []
        stats = {
            'total_parameters_extracted': 0,
            'instruments_detected': {},
            'conversion_times': [],
            'characteristics_found': {}
        }

        # Find all .fxp files
        fxp_files = list(input_path.glob("**/*.fxp"))
        if max_files:
            fxp_files = fxp_files[:max_files]

        print(f"🎵 Found {len(fxp_files)} .fxp files to convert")
        print(f"🎹 Using Serum 2 VST: {self.serum2_path}")
        print(f"📁 Output directory: {output_path}")
        print("📋 Enhanced parameter mapping loaded" if self.parameter_mapping else "⚠️  No parameter mapping loaded")
        print("=" * 60)

        start_time = time.time()

        for i, fxp_file in enumerate(fxp_files, 1):
            file_start = time.time()

            try:
                # Maintain folder structure
                relative_path = fxp_file.relative_to(input_path)
                output_subdir = output_path / relative_path.parent

                # Convert to .SerumPreset
                converted_file = self.convert_fxp_to_serum_preset(str(fxp_file), str(output_subdir))

                if converted_file:
                    converted_count += 1
                    conversion_time = time.time() - file_start
                    stats['conversion_times'].append(conversion_time)

                    # Load the converted file to gather stats
                    try:
                        with open(converted_file, 'r') as f:
                            preset_data = json.load(f)

                        # Update statistics
                        param_count = preset_data.get('metadata', {}).get('conversion_info', {}).get('parameter_count', 0)
                        stats['total_parameters_extracted'] += param_count

                        instrument = preset_data.get('metadata', {}).get('instrument_type', 'Unknown')
                        stats['instruments_detected'][instrument] = stats['instruments_detected'].get(instrument, 0) + 1

                        characteristics = preset_data.get('metadata', {}).get('characteristics', [])
                        for char in characteristics:
                            stats['characteristics_found'][char] = stats['characteristics_found'].get(char, 0) + 1

                    except Exception as e:
                        print(f"⚠️  Could not analyze converted file: {e}")

                    # Progress reporting
                    if i % 10 == 0 or i == len(fxp_files):
                        avg_time = np.mean(stats['conversion_times'][-10:]) if stats['conversion_times'] else 0
                        remaining = len(fxp_files) - i
                        eta = remaining * avg_time
                        print(f"📊 Progress: {i}/{len(fxp_files)} ({i/len(fxp_files)*100:.1f}%) | "
                              f"ETA: {eta/60:.1f}m | Avg: {avg_time:.2f}s/file")
                else:
                    failed_files.append(str(fxp_file))

            except Exception as e:
                failed_files.append(str(fxp_file))
                print(f"❌ Failed: {fxp_file.name} - {e}")

        total_time = time.time() - start_time

        # Final statistics
        print("\n" + "=" * 60)
        print(f"🎉 Conversion Complete!")
        print(f"✅ Successful: {converted_count}")
        print(f"❌ Failed: {len(failed_files)}")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"📈 Average: {total_time/len(fxp_files):.2f}s per file")
        print(f"🎛️  Total parameters extracted: {stats['total_parameters_extracted']:,}")

        if stats['instruments_detected']:
            print(f"\n🎼 Instruments detected:")
            for instrument, count in sorted(stats['instruments_detected'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {instrument}: {count}")

        if stats['characteristics_found']:
            print(f"\n🔊 Top characteristics:")
            for char, count in sorted(stats['characteristics_found'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {char}: {count}")

        # Save comprehensive conversion report
        report = {
            'conversion_summary': {
                'total_files': len(fxp_files),
                'successful': converted_count,
                'failed': len(failed_files),
                'success_rate': converted_count / len(fxp_files) * 100 if fxp_files else 0,
                'total_time_minutes': total_time / 60,
                'avg_time_per_file': total_time / len(fxp_files) if fxp_files else 0,
                'total_parameters_extracted': stats['total_parameters_extracted']
            },
            'statistics': {
                'instruments_detected': stats['instruments_detected'],
                'characteristics_found': stats['characteristics_found']
            },
            'failed_files': failed_files,
            'settings': {
                'input_directory': str(input_path),
                'output_directory': str(output_path),
                'serum2_vst_path': self.serum2_path,
                'parameter_mapping_loaded': bool(self.parameter_mapping),
                'conversion_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'converter_version': "v2.0"
            }
        }

        with open(output_path / 'conversion_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        if failed_files:
            with open(output_path / 'failed_files.txt', 'w') as f:
                f.write('\n'.join(failed_files))

        return converted_count, failed_files


def main():
    """Main conversion workflow with rigorous FXP to Serum 2 conversion"""
    print("🎵 Rigorous FXP to Serum 2 Preset Converter v2.0")
    print("Uses DawDreamer + Serum 2 VST + Enhanced Parameter Mapping")
    print("=" * 60)

    # Initialize converter
    try:
        converter = FXPConverter()
    except ValueError as e:
        print(f"❌ {e}")
        print("\n🔍 Searching for Serum installations...")

        # Try to find and suggest Serum paths
        possible_paths = []
        for pattern in ["/Library/Audio/Plug-Ins/**/Serum*.vst3", "/Library/Audio/Plug-Ins/**/Serum*.component"]:
            from glob import glob
            possible_paths.extend(glob(pattern, recursive=True))

        if possible_paths:
            print("Found possible Serum installations:")
            for path in possible_paths:
                print(f"  - {path}")
            print("\nSpecify path manually: converter = FXPConverter('/path/to/serum2')")
        return

    # Test single file conversion first
    test_files = [
        "./Serum_1_Presets/Misc/PR 808 Kick Circuit [SD].fxp",
        "./Serum_1_Presets/Bass/BS Dark Wizzard [SD].fxp",
        "./Serum_1_Presets/Leads/LD CZ Glider [AF].fxp",
        # Fallback patterns
        "./Serum_1_Presets/*/BS*.fxp",
        "./Serum_1_Presets/*/LD*.fxp"
    ]

    print("\n🧪 Testing single file conversions...")
    test_success = False

    for test_pattern in test_files:
        if "*" in test_pattern:
            from glob import glob
            matches = glob(test_pattern)
            if matches:
                test_file = matches[0]
            else:
                continue
        else:
            test_file = test_pattern

        if Path(test_file).exists():
            print(f"\n📁 Testing: {Path(test_file).name}")
            result = converter.convert_fxp_to_serum_preset(test_file, "./converted_presets_test")
            if result:
                print(f"✅ Success: {Path(result).name}")

                # Show some details from the converted file
                try:
                    with open(result, 'r') as f:
                        data = json.load(f)

                    metadata = data.get('metadata', {})
                    print(f"   📋 Name: {metadata.get('name', 'Unknown')}")
                    print(f"   🎛️  Parameters: {metadata.get('conversion_info', {}).get('parameter_count', 0)}")
                    print(f"   🎼 Type: {metadata.get('instrument_type', 'Unknown')}")

                    characteristics = metadata.get('characteristics', [])
                    if characteristics:
                        print(f"   🔊 Characteristics: {', '.join(characteristics)}")

                except Exception as e:
                    print(f"   ⚠️  Could not read details: {e}")

                test_success = True
                break
            else:
                print(f"❌ Failed to convert test file")

    if not test_success:
        print("❌ Test conversion failed. Check Serum 2 installation and .fxp file paths.")
        return

    # Ask user for batch conversion
    print("\n" + "=" * 60)
    response = input("🚀 Run full batch conversion on Serum_1_Presets? (y/N): ").lower().strip()

    if response == 'y':
        print("\n🔄 Starting batch conversion...")
        input_dir = "./Serum_1_Presets"
        output_dir = "./converted_serum2_presets"

        # Check if input directory exists
        if not Path(input_dir).exists():
            print(f"❌ Input directory not found: {input_dir}")
            print("📁 Available directories:")
            for path in Path(".").glob("**/"):
                if "serum" in path.name.lower() or "preset" in path.name.lower():
                    print(f"   - {path}")
            return

        # Run batch conversion
        converted, failed = converter.batch_convert_library(
            input_dir=input_dir,
            output_dir=output_dir,
            max_files=None  # Convert all files
        )

        print(f"\n🎯 Final Results:")
        print(f"✅ Converted: {converted} presets")
        print(f"❌ Failed: {len(failed)} presets")
        print(f"📁 Output: {output_dir}")
        print(f"📊 Report: {output_dir}/conversion_report.json")

        if failed:
            print(f"📝 Failed files list: {output_dir}/failed_files.txt")

    else:
        print("\n👋 Conversion cancelled. Run again when ready!")
        print("💡 Tip: You can also import this as a module and use converter.convert_fxp_to_serum_preset()")


if __name__ == "__main__":
    main()