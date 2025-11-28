#!/usr/bin/env python3
"""
Filter dataset to keep only the highest quality example per preset
"""

import json
from collections import defaultdict

def filter_best_per_preset(input_file: str, output_file: str):
    """Keep only the highest quality example for each preset"""

    print(f"📂 Loading dataset from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    examples = data['examples']
    print(f"   Total examples: {len(examples)}")

    # Group examples by preset name
    preset_groups = defaultdict(list)
    for example in examples:
        preset_name = example['response']['preset_name'].strip()
        preset_groups[preset_name].append(example)

    print(f"   Unique presets: {len(preset_groups)}")

    # Keep only the highest quality example per preset
    best_examples = []
    for preset_name, preset_examples in preset_groups.items():
        # Sort by overall quality score (descending)
        preset_examples.sort(key=lambda x: x['quality_scores']['overall'], reverse=True)
        best_example = preset_examples[0]
        best_examples.append(best_example)

        if len(preset_examples) > 1:
            print(f"   {preset_name}: kept quality {best_example['quality_scores']['overall']:.3f}, "
                  f"filtered {len(preset_examples)-1} examples")

    # Sort by preset name for consistency
    best_examples.sort(key=lambda x: x['response']['preset_name'])

    # Create output data structure
    output_data = {
        "metadata": {
            "total_examples": len(best_examples),
            "unique_presets": len(preset_groups),
            "average_quality": sum(ex['quality_scores']['overall'] for ex in best_examples) / len(best_examples),
            "filtering_strategy": "highest_quality_per_preset",
            "original_total": len(examples)
        },
        "examples": best_examples
    }

    # Save filtered dataset
    print(f"\n💾 Saving filtered dataset to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Also create JSONL for training
    jsonl_file = output_file.replace('.json', '.jsonl')
    print(f"💾 Creating training JSONL at {jsonl_file}...")
    with open(jsonl_file, 'w') as f:
        for example in best_examples:
            f.write(json.dumps({"text": example['mistral_template']}) + '\n')

    print(f"\n✅ Filtering complete!")
    print(f"   Original examples: {len(examples)}")
    print(f"   Filtered examples: {len(best_examples)}")
    print(f"   Average quality: {output_data['metadata']['average_quality']:.3f}")
    print(f"   Examples per preset: 1.0 (perfect balance)")

    return output_file

if __name__ == "__main__":
    filter_best_per_preset(
        "data/serum_gpt5_mistral_FINAL_dataset_progress_batch25.json",
        "data/serum_gpt5_mistral_FINAL_filtered_500.json"
    )