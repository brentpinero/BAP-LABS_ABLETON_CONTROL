#!/usr/bin/env python3
"""
Extract presets 501-1000 from diverse_presets_1000.json
and format them for GPT-5 processing.
"""

import json

def extract_next_500():
    # Load the 1000 diverse presets
    with open('data/diverse_presets_1000.json', 'r') as f:
        data = json.load(f)

    print(f"Total presets available: {len(data['presets'])}")

    # Extract presets 501-1000 (index 500-999)
    next_500_presets = data['presets'][500:1000]

    print(f"Extracting presets 501-1000: {len(next_500_presets)} presets")

    # Format for GPT-5 input (same structure as before)
    gpt5_input = {
        "metadata": {
            "source": "diverse_presets_1000.json",
            "range": "501-1000",
            "total_presets": len(next_500_presets)
        },
        "presets": next_500_presets
    }

    # Save to new file
    output_file = 'data/gpt5_input_500_diverse_batch2.json'
    with open(output_file, 'w') as f:
        json.dump(gpt5_input, f, indent=2)

    print(f"✅ Saved {len(next_500_presets)} presets to {output_file}")

    # Show sample categories
    categories = {}
    for preset in next_500_presets:
        cat = preset.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nCategory breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    return output_file

if __name__ == "__main__":
    extract_next_500()