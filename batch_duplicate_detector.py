#!/usr/bin/env python3
"""
⚡ BATCH DUPLICATE DETECTOR ⚡
Process duplicates in batches to avoid memory issues
Focus on actionable results only
"""

import json
import hashlib
from pathlib import Path
from ultimate_preset_converter import UltimatePresetConverter
from typing import Dict, List, Set, Tuple, Any
import time

class BatchDuplicateDetector:
    """Batch processing duplicate detector for large datasets"""

    def __init__(self, batch_size: int = 500):
        self.converter = UltimatePresetConverter()
        self.batch_size = batch_size
        self.existing_index = {}
        self.duplicates_found = []

    def load_existing_dataset_index(self, dataset_path: str):
        """Load existing dataset and create efficient index"""
        print("📖 Loading existing dataset index...")

        with open(dataset_path, 'r') as f:
            dataset = json.load(f)

        print(f"   Loaded {len(dataset)} existing presets")

        # Create efficient indexes
        self.existing_index = {
            'by_filename': {},
            'by_source_path': set(),
            'by_param_hash': {}
        }

        for i, preset in enumerate(dataset):
            # Index by filename (most reliable duplicate indicator)
            filename = Path(preset['source_file']).name.lower()
            if filename not in self.existing_index['by_filename']:
                self.existing_index['by_filename'][filename] = []
            self.existing_index['by_filename'][filename].append({
                'index': i,
                'source_file': preset['source_file'],
                'preset_name': preset['preset_name']
            })

            # Index by source path
            self.existing_index['by_source_path'].add(preset['source_file'])

            # Index by parameter hash (for exact parameter matches)
            if 'parameters' in preset and isinstance(preset['parameters'], dict):
                # Skip SerumPreset files with just notes
                if not (len(preset['parameters']) == 1 and 'note' in preset['parameters']):
                    param_hash = self._create_parameter_hash(preset['parameters'])
                    if param_hash not in self.existing_index['by_param_hash']:
                        self.existing_index['by_param_hash'][param_hash] = []
                    self.existing_index['by_param_hash'][param_hash].append({
                        'index': i,
                        'source_file': preset['source_file'],
                        'preset_name': preset['preset_name']
                    })

        print(f"✅ Created efficient index with {len(self.existing_index['by_filename'])} filenames")

    def _create_parameter_hash(self, parameters: Dict[str, Any]) -> str:
        """Create hash of parameters for exact matching"""
        sorted_params = sorted(parameters.items())
        rounded_params = []

        for k, v in sorted_params:
            if isinstance(v, (int, float)):
                rounded_params.append((k, round(float(v), 6)))
            else:
                rounded_params.append((k, str(v)))

        return hashlib.md5(str(rounded_params).encode()).hexdigest()

    def find_duplicates_in_batch(self, new_files_batch: List[Path]) -> List[Dict[str, Any]]:
        """Process a batch of new files and find duplicates"""
        batch_duplicates = []

        for new_file in new_files_batch:
            # Check filename duplicate (most reliable)
            filename_lower = new_file.name.lower()

            if filename_lower in self.existing_index['by_filename']:
                for existing_info in self.existing_index['by_filename'][filename_lower]:
                    batch_duplicates.append({
                        'new_file': str(new_file),
                        'existing_file': existing_info['source_file'],
                        'match_type': 'exact_filename',
                        'confidence': 'very_high'
                    })

            # Check exact path duplicate
            if str(new_file) in self.existing_index['by_source_path']:
                batch_duplicates.append({
                    'new_file': str(new_file),
                    'existing_file': str(new_file),
                    'match_type': 'exact_path',
                    'confidence': 'absolute'
                })

        return batch_duplicates

    def process_directory_in_batches(self, new_preset_dir: str) -> Dict[str, Any]:
        """Process entire directory in batches"""
        print(f"⚡ BATCH PROCESSING: {new_preset_dir}")
        print("=" * 60)

        # Find all files
        fxp_files = list(Path(new_preset_dir).glob("**/*.fxp"))
        serum_files = list(Path(new_preset_dir).glob("**/*.SerumPreset"))
        all_files = fxp_files + serum_files

        total_files = len(all_files)
        total_batches = (total_files + self.batch_size - 1) // self.batch_size

        print(f"📊 PROCESSING PLAN:")
        print(f"   Total files: {total_files}")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Total batches: {total_batches}")

        all_duplicates = []
        start_time = time.time()

        # Process in batches
        for batch_num in range(total_batches):
            batch_start = batch_num * self.batch_size
            batch_end = min(batch_start + self.batch_size, total_files)
            batch_files = all_files[batch_start:batch_end]

            print(f"\\n⚡ Processing batch {batch_num + 1}/{total_batches} "
                  f"(files {batch_start + 1}-{batch_end})")

            # Find duplicates in this batch
            batch_duplicates = self.find_duplicates_in_batch(batch_files)
            all_duplicates.extend(batch_duplicates)

            # Progress update
            processed = batch_end
            progress = processed / total_files * 100
            elapsed = time.time() - start_time

            if batch_num > 0:
                eta = (elapsed / processed) * (total_files - processed)
                print(f"   Progress: {processed}/{total_files} ({progress:.1f}%) | "
                      f"Duplicates found: {len(batch_duplicates)} | ETA: {eta/60:.1f}m")
            else:
                print(f"   Progress: {processed}/{total_files} ({progress:.1f}%) | "
                      f"Duplicates found: {len(batch_duplicates)}")

        total_time = time.time() - start_time

        # Summarize results
        duplicate_types = {}
        for dup in all_duplicates:
            match_type = dup['match_type']
            duplicate_types[match_type] = duplicate_types.get(match_type, 0) + 1

        summary = {
            'total_files_processed': total_files,
            'total_duplicates_found': len(all_duplicates),
            'processing_time_minutes': total_time / 60,
            'duplicate_breakdown': duplicate_types,
            'estimated_unique_files': total_files - len(all_duplicates),
            'duplicates': all_duplicates
        }

        print(f"\\n🎉 BATCH PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"⏱️  Processing time: {total_time/60:.1f} minutes")
        print(f"📊 Total duplicates found: {len(all_duplicates)}")
        for match_type, count in duplicate_types.items():
            print(f"   • {match_type}: {count}")
        print(f"✅ Estimated unique files: {summary['estimated_unique_files']}")

        return summary

    def save_results(self, results: Dict[str, Any], output_dir: str):
        """Save results efficiently"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save summary
        summary_file = output_path / "batch_duplicate_summary.json"
        summary_data = {k: v for k, v in results.items() if k != 'duplicates'}
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)

        # Save just the duplicate file list (actionable)
        duplicates_file = output_path / "duplicate_files_to_skip.txt"
        duplicate_files = [dup['new_file'] for dup in results['duplicates']]
        with open(duplicates_file, 'w') as f:
            f.write('\\n'.join(duplicate_files))

        # Save detailed duplicates (if needed)
        if len(results['duplicates']) < 10000:  # Only if manageable size
            detailed_file = output_path / "detailed_duplicates.json"
            with open(detailed_file, 'w') as f:
                json.dump(results['duplicates'], f, indent=2)

        print(f"\\n💾 RESULTS SAVED:")
        print(f"   📊 Summary: {summary_file}")
        print(f"   🚫 Skip list: {duplicates_file}")
        if len(results['duplicates']) < 10000:
            print(f"   📝 Details: {detailed_file}")

def main():
    """Run batch duplicate detection"""
    print("⚡⚡⚡ BATCH DUPLICATE DETECTION ⚡⚡⚡")
    print("=" * 60)

    detector = BatchDuplicateDetector(batch_size=1000)  # Process 1000 files at a time

    # Load existing dataset
    existing_dataset_path = "/Users/brentpinero/Documents/serum_llm_2/ultimate_training_dataset/ultimate_serum_dataset.json"
    detector.load_existing_dataset_index(existing_dataset_path)

    # Process new directory in batches
    new_preset_dir = "/Users/brentpinero/Documents/serum_llm_2/DT_Serum_Presets"
    results = detector.process_directory_in_batches(new_preset_dir)

    # Save results
    output_dir = "/Users/brentpinero/Documents/serum_llm_2/duplicate_analysis"
    detector.save_results(results, output_dir)

    print(f"\\n🚀 READY FOR DATASET EXPANSION!")
    print(f"🚫 Skip {results['total_duplicates_found']} duplicate files")
    print(f"✅ Add ~{results['estimated_unique_files']} unique presets")

if __name__ == "__main__":
    main()