#!/usr/bin/env python3
"""
🚀 ULTIMATE DATASET EXPANDER 🚀
Adds non-duplicate presets to the ultimate training dataset
Filters out duplicates and creates the massive final dataset!
"""

import json
import time
from pathlib import Path
from ultimate_preset_converter import UltimatePresetConverter
from typing import Dict, List, Set, Any

class UltimateDatasetExpander:
    """Expands ultimate dataset with filtered new presets"""

    def __init__(self):
        self.converter = UltimatePresetConverter()
        self.duplicate_files = set()
        self.stats = {
            'files_processed': 0,
            'files_skipped_duplicate': 0,
            'files_skipped_non_serum': 0,
            'files_converted_successfully': 0,
            'files_failed': 0,
            'total_parameters_added': 0
        }

    def load_duplicate_list(self, duplicate_list_path: str):
        """Load list of duplicate files to skip"""
        print("📋 Loading duplicate files list...")

        with open(duplicate_list_path, 'r') as f:
            duplicate_files = f.read().strip().split('\\n')

        self.duplicate_files = set(duplicate_files)
        print(f"   Loaded {len(self.duplicate_files)} duplicate files to skip")

    def load_existing_dataset(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Load existing ultimate dataset"""
        print("📖 Loading existing ultimate dataset...")

        with open(dataset_path, 'r') as f:
            existing_dataset = json.load(f)

        print(f"   Loaded {len(existing_dataset)} existing presets")
        return existing_dataset

    def process_new_directory_filtered(self, new_preset_dir: str) -> List[Dict[str, Any]]:
        """Process new directory with duplicate filtering"""
        print(f"\\n🚀 PROCESSING NEW PRESETS WITH FILTERING...")
        print("=" * 60)

        # Find all new preset files
        fxp_files = list(Path(new_preset_dir).glob("**/*.fxp"))
        serum_files = list(Path(new_preset_dir).glob("**/*.SerumPreset"))
        all_files = fxp_files + serum_files

        total_files = len(all_files)
        print(f"📊 PROCESSING OVERVIEW:")
        print(f"   🎵 .fxp files found: {len(fxp_files)}")
        print(f"   🎛️  .SerumPreset files found: {len(serum_files)}")
        print(f"   📁 Total files to process: {total_files}")
        print(f"   🚫 Duplicates to skip: {len(self.duplicate_files)}")

        new_presets = []
        start_time = time.time()

        # Process .fxp files
        print(f"\\n🔓 CONVERTING .FXP FILES...")
        for i, fxp_file in enumerate(fxp_files, 1):
            file_start = time.time()
            self.stats['files_processed'] += 1

            # Skip if duplicate
            if str(fxp_file) in self.duplicate_files:
                self.stats['files_skipped_duplicate'] += 1
                continue

            try:
                result = self.converter.convert_fxp_file(str(fxp_file))
                if result:
                    new_presets.append(result)
                    self.stats['files_converted_successfully'] += 1
                    self.stats['total_parameters_added'] += result['stats']['mapped_params']
                else:
                    # Check if skipped as non-Serum
                    with open(fxp_file, 'rb') as f:
                        data = f.read()
                    if (len(data) >= 20 and
                        data.startswith(b'CcnK') and
                        data[8:12] == b'FPCh'):
                        import struct
                        fx_id = struct.unpack('>I', data[16:20])[0]
                        if fx_id != 0x58667358:
                            self.stats['files_skipped_non_serum'] += 1
                        else:
                            self.stats['files_failed'] += 1
                    else:
                        self.stats['files_failed'] += 1

                conversion_time = time.time() - file_start

                # Progress update
                if i % 500 == 0 or i == len(fxp_files):
                    processed = i
                    skipped = self.stats['files_skipped_duplicate'] + self.stats['files_skipped_non_serum']
                    converted = self.stats['files_converted_successfully']

                    print(f"   📊 Progress: {processed}/{len(fxp_files)} ({processed/len(fxp_files)*100:.1f}%) | "
                          f"Converted: {converted} | Skipped: {skipped}")

            except Exception as e:
                self.stats['files_failed'] += 1
                if i % 500 == 0:
                    print(f"   ❌ Error processing {fxp_file.name}: {e}")

        # Process .SerumPreset files
        print(f"\\n🎛️  PROCESSING .SERUMPRESET FILES...")
        for i, preset_file in enumerate(serum_files, 1):
            self.stats['files_processed'] += 1

            # Skip if duplicate
            if str(preset_file) in self.duplicate_files:
                self.stats['files_skipped_duplicate'] += 1
                continue

            try:
                result = self.converter.process_serum_preset_file(str(preset_file))
                if result:
                    new_presets.append(result)
                    self.stats['files_converted_successfully'] += 1
                else:
                    self.stats['files_failed'] += 1

                # Progress update
                if i % 100 == 0 or i == len(serum_files):
                    processed = i
                    converted = len([p for p in new_presets if p['format'] == 'serum_preset_native'])
                    print(f"   📊 Progress: {processed}/{len(serum_files)} ({processed/len(serum_files)*100:.1f}%) | "
                          f"Processed: {converted}")

            except Exception as e:
                self.stats['files_failed'] += 1

        total_time = time.time() - start_time

        print(f"\\n✅ NEW PRESET PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"⏱️  Processing time: {total_time/60:.1f} minutes")
        print(f"📊 Files processed: {self.stats['files_processed']}")
        print(f"🚫 Duplicates skipped: {self.stats['files_skipped_duplicate']}")
        print(f"⚠️  Non-Serum skipped: {self.stats['files_skipped_non_serum']}")
        print(f"✅ Successfully converted: {self.stats['files_converted_successfully']}")
        print(f"❌ Failed conversions: {self.stats['files_failed']}")
        print(f"🎛️  New parameters extracted: {self.stats['total_parameters_added']:,}")

        return new_presets

    def merge_datasets(self, existing_dataset: List[Dict[str, Any]],
                      new_presets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge existing and new datasets"""
        print(f"\\n🔗 MERGING DATASETS...")

        merged_dataset = existing_dataset + new_presets

        print(f"   📊 Original dataset: {len(existing_dataset)} presets")
        print(f"   ➕ New presets added: {len(new_presets)}")
        print(f"   📁 Final dataset size: {len(merged_dataset)} presets")

        return merged_dataset

    def save_expanded_dataset(self, merged_dataset: List[Dict[str, Any]],
                             output_dir: str) -> Dict[str, Any]:
        """Save the expanded ultimate dataset"""
        print(f"\\n💾 SAVING EXPANDED ULTIMATE DATASET...")

        output_path = Path(output_dir)

        # Save main dataset
        dataset_file = output_path / "ultimate_serum_dataset_expanded.json"
        with open(dataset_file, 'w') as f:
            json.dump(merged_dataset, f, indent=2)

        # Calculate final statistics
        existing_count = len(merged_dataset) - self.stats['files_converted_successfully']

        # Count by format
        fxp_count = len([p for p in merged_dataset if p['format'] == 'fxp_converted'])
        serum_count = len([p for p in merged_dataset if p['format'] == 'serum_preset_native'])

        # Calculate total parameters
        total_parameters = 0
        for preset in merged_dataset:
            if 'stats' in preset and 'mapped_params' in preset['stats']:
                total_parameters += preset['stats']['mapped_params']

        final_stats = {
            'expansion_summary': {
                'original_dataset_size': existing_count,
                'new_presets_added': self.stats['files_converted_successfully'],
                'final_dataset_size': len(merged_dataset),
                'growth_percentage': (self.stats['files_converted_successfully'] / existing_count) * 100,
                'total_parameters_in_dataset': total_parameters,
                'processing_time_minutes': 0  # Will be updated
            },
            'dataset_composition': {
                'fxp_presets': fxp_count,
                'native_serum_presets': serum_count
            },
            'processing_stats': self.stats,
            'expansion_date': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save statistics
        stats_file = output_path / "expansion_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(final_stats, f, indent=2)

        print(f"✅ Dataset saved to: {dataset_file}")
        print(f"📊 Statistics saved to: {stats_file}")
        print(f"💾 Dataset file size: {dataset_file.stat().st_size/1024/1024:.1f} MB")

        return final_stats

def main():
    """Run the ultimate dataset expansion"""
    print("🚀🚀🚀 ULTIMATE DATASET EXPANDER 🚀🚀🚀")
    print("=" * 70)

    expander = UltimateDatasetExpander()

    # Resolve paths relative to this script's directory
    _dir = os.path.dirname(os.path.abspath(__file__))
    _root = os.path.dirname(_dir)

    # Load duplicate files list
    duplicate_list_path = os.path.join(_root, "duplicate_analysis", "duplicate_files_to_skip.txt")
    expander.load_duplicate_list(duplicate_list_path)

    # Load existing dataset
    existing_dataset_path = os.path.join(_root, "ultimate_training_dataset", "ultimate_serum_dataset.json")
    existing_dataset = expander.load_existing_dataset(existing_dataset_path)

    # Process new directory with filtering
    new_preset_dir = os.path.join(_root, "DT_Serum_Presets")
    new_presets = expander.process_new_directory_filtered(new_preset_dir)

    # Merge datasets
    merged_dataset = expander.merge_datasets(existing_dataset, new_presets)

    # Save expanded dataset
    output_dir = os.path.join(_root, "ultimate_training_dataset")
    final_stats = expander.save_expanded_dataset(merged_dataset, output_dir)

    print(f"\\n🎉 ULTIMATE DATASET EXPANSION COMPLETE!")
    print("=" * 70)
    print(f"📈 Dataset growth: {final_stats['expansion_summary']['growth_percentage']:.1f}%")
    print(f"📁 Final size: {final_stats['expansion_summary']['final_dataset_size']:,} presets")
    print(f"🎛️  Total parameters: {final_stats['expansion_summary']['total_parameters_in_dataset']:,}")
    print(f"🔓 FXP presets: {final_stats['dataset_composition']['fxp_presets']:,}")
    print(f"🎹 SerumPreset files: {final_stats['dataset_composition']['native_serum_presets']:,}")
    print(f"\\n🚀 READY FOR HERMES-2-PRO TRAINING!")

if __name__ == "__main__":
    main()