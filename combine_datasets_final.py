#!/usr/bin/env python3
"""
Combines multiple Serum training datasets into one mega dataset.
Handles deduplication, quality filtering, and final validation.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
import hashlib
from datetime import datetime

def load_dataset(filepath: str) -> Dict:
    """Load a dataset JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def get_example_hash(example: Dict) -> str:
    """Create a hash for deduplication based on instruction text."""
    instruction = example.get('instruction', '')
    # Use just the instruction for dedup (similar instructions = duplicate)
    return hashlib.md5(instruction.lower().strip().encode()).hexdigest()

def get_param_hash(example: Dict) -> str:
    """Create a hash based on parameter values for finding near-duplicates."""
    params = example.get('response', {}).get('parameter_changes', [])
    # Sort params by index and create a string of index:value pairs
    param_str = "|".join([f"{p['index']}:{p['value']:.3f}" for p in sorted(params, key=lambda x: x['index'])])
    return hashlib.md5(param_str.encode()).hexdigest()

def combine_datasets(dataset_files: List[str], output_file: str, quality_threshold: float = 0.9):
    """
    Combine multiple datasets with deduplication and quality filtering.
    """
    print("🎛️ COMBINING SERUM DATASETS")
    print("=" * 50)

    all_examples = []
    seen_instructions = set()
    seen_params = set()

    stats = {
        'total_input': 0,
        'duplicates_removed': 0,
        'low_quality_removed': 0,
        'near_duplicates_removed': 0,
        'final_count': 0,
        'sources': {}
    }

    # Process each dataset
    for dataset_file in dataset_files:
        if not Path(dataset_file).exists():
            print(f"⚠️  Skipping {dataset_file} (not found)")
            continue

        print(f"\n📁 Processing {dataset_file}")
        data = load_dataset(dataset_file)

        examples = data.get('examples', [])
        source_name = Path(dataset_file).stem
        stats['sources'][source_name] = {'input': len(examples), 'kept': 0}

        for example in examples:
            stats['total_input'] += 1

            # Check quality score
            quality = example.get('quality_scores', {}).get('overall', 1.0)
            if quality < quality_threshold:
                stats['low_quality_removed'] += 1
                continue

            # Check for duplicate instructions
            instruction_hash = get_example_hash(example)
            if instruction_hash in seen_instructions:
                stats['duplicates_removed'] += 1
                continue

            # Check for near-duplicate parameters (very similar presets)
            param_hash = get_param_hash(example)
            if param_hash in seen_params:
                stats['near_duplicates_removed'] += 1
                continue

            # Add to collection
            seen_instructions.add(instruction_hash)
            seen_params.add(param_hash)
            all_examples.append(example)
            stats['sources'][source_name]['kept'] += 1

    stats['final_count'] = len(all_examples)

    # Sort by quality score (best first)
    all_examples.sort(key=lambda x: x.get('quality_scores', {}).get('overall', 0), reverse=True)

    # Create final dataset
    output_data = {
        "metadata": {
            "total_examples": len(all_examples),
            "creation_date": datetime.now().isoformat(),
            "quality_threshold": quality_threshold,
            "source_files": dataset_files,
            "statistics": stats,
            "average_quality": sum(e.get('quality_scores', {}).get('overall', 0) for e in all_examples) / len(all_examples) if all_examples else 0
        },
        "examples": all_examples
    }

    # Save combined dataset
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Print statistics
    print("\n📊 COMBINATION RESULTS")
    print("=" * 50)
    print(f"Total input examples: {stats['total_input']}")
    print(f"Duplicates removed: {stats['duplicates_removed']}")
    print(f"Near-duplicates removed: {stats['near_duplicates_removed']}")
    print(f"Low quality removed: {stats['low_quality_removed']}")
    print(f"Final examples: {stats['final_count']}")
    print(f"Average quality: {output_data['metadata']['average_quality']:.3f}")

    print("\n📁 Source breakdown:")
    for source, counts in stats['sources'].items():
        kept_pct = (counts['kept'] / counts['input'] * 100) if counts['input'] > 0 else 0
        print(f"  {source}: {counts['kept']}/{counts['input']} kept ({kept_pct:.1f}%)")

    print(f"\n✅ Combined dataset saved to: {output_file}")

    return output_data

def validate_combined_dataset(filepath: str):
    """Quick validation of the combined dataset."""
    print("\n🔍 VALIDATING COMBINED DATASET")
    print("=" * 50)

    data = load_dataset(filepath)
    examples = data['examples']

    # Check for required fields
    missing_fields = 0
    param_issues = 0

    for i, example in enumerate(examples):
        if 'instruction' not in example:
            missing_fields += 1
        if 'response' not in example:
            missing_fields += 1
        else:
            params = example['response'].get('parameter_changes', [])
            if len(params) < 1:
                param_issues += 1

    print(f"Total examples: {len(examples)}")
    print(f"Missing fields: {missing_fields}")
    print(f"Parameter issues: {param_issues}")

    if missing_fields == 0 and param_issues == 0:
        print("✅ Dataset is valid and ready for training!")
    else:
        print("⚠️  Some issues found - review before training")

    return missing_fields == 0 and param_issues == 0

def main():
    # Define input datasets
    datasets_to_combine = [
        "data/serum_gpt5_mistral_combined_898.json",  # Original 898 examples
        "data/serum_gpt5_mistral_500_diverse_batch2_dataset.json",  # New batch2 (when complete)
    ]

    # Output file
    output_file = "data/serum_gpt5_mistral_FINAL_combined.json"

    # Check what's available
    print("🔍 Checking available datasets...")
    available = []
    for dataset in datasets_to_combine:
        if Path(dataset).exists():
            size = Path(dataset).stat().st_size / 1024 / 1024  # MB
            print(f"  ✅ {dataset} ({size:.1f} MB)")
            available.append(dataset)
        else:
            print(f"  ❌ {dataset} (not found yet)")

    if len(available) < 2:
        print("\n⚠️  Waiting for batch2 processing to complete...")
        print("Run this script again when batch2 is done!")
        return

    # Combine datasets
    print("\n🚀 Starting combination process...")
    combined = combine_datasets(
        available,
        output_file,
        quality_threshold=0.9  # Only keep high quality examples
    )

    # Validate result
    validate_combined_dataset(output_file)

    # Also create a smaller high-quality subset for testing
    if len(combined['examples']) > 1000:
        print("\n📦 Creating high-quality subset (top 1000)...")
        subset_data = {
            "metadata": combined['metadata'].copy(),
            "examples": combined['examples'][:1000]  # Already sorted by quality
        }
        subset_data['metadata']['total_examples'] = 1000
        subset_data['metadata']['description'] = "Top 1000 highest quality examples"

        subset_file = "data/serum_gpt5_mistral_TOP1000.json"
        with open(subset_file, 'w') as f:
            json.dump(subset_data, f, indent=2)
        print(f"✅ Subset saved to: {subset_file}")

if __name__ == "__main__":
    main()