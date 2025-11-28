#!/usr/bin/env python3
"""
Select 1000 diverse presets from the dataset, excluding GPT-5 processed ones
Split into 500 for Gemini and 500 for Claude
"""

import json
import random
from collections import defaultdict

# Load full dataset
with open('data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json', 'r') as f:
    all_presets = json.load(f)

# Load GPT-5 processed preset names
with open('data/serum_gpt5_mistral_FINAL_filtered_500.json', 'r') as f:
    gpt5_data = json.load(f)

gpt5_processed = set()
for example in gpt5_data['examples']:
    preset_name = example['response']['preset_name'].strip()
    gpt5_processed.add(preset_name)

print(f'📊 Starting Selection Process')
print(f'=' * 60)
print(f'Total presets: {len(all_presets)}')
print(f'GPT-5 processed: {len(gpt5_processed)}')
print(f'Available: {len(all_presets) - len(gpt5_processed)}')
print()

# Filter out GPT-5 processed presets
unprocessed_presets = [
    p for p in all_presets
    if p['preset_name'].strip() not in gpt5_processed
]

print(f'✅ Filtered to {len(unprocessed_presets)} unprocessed presets')
print()

# Categorize presets by type for diversity
categories = defaultdict(list)
for preset in unprocessed_presets:
    name = preset['preset_name'].strip().upper()

    # Categorize by prefix/type
    if any(x in name for x in ['BASS', 'BA ', 'BS ', 'REESE', 'SUB']):
        categories['bass'].append(preset)
    elif any(x in name for x in ['LEAD', 'LD ']):
        categories['lead'].append(preset)
    elif any(x in name for x in ['PAD', 'PD ', 'CHORD', 'CH ']):
        categories['pad'].append(preset)
    elif any(x in name for x in ['ARP', 'SQ ', 'SEQ']):
        categories['sequence'].append(preset)
    elif any(x in name for x in ['FX ', 'SFX']):
        categories['fx'].append(preset)
    elif any(x in name for x in ['PLUCK', 'PK ', 'PL ']):
        categories['pluck'].append(preset)
    elif any(x in name for x in ['KEY', 'KY ', 'PIANO', 'ORGAN']):
        categories['keys'].append(preset)
    else:
        categories['other'].append(preset)

print(f'📂 Category Distribution:')
for cat, presets in sorted(categories.items(), key=lambda x: -len(x[1])):
    print(f'  {cat:12} {len(presets):5} presets')
print()

# Select 1000 presets with proportional representation
total_needed = 1000
selected_presets = []

# Calculate proportions
total_available = len(unprocessed_presets)
for category, presets in categories.items():
    # Proportional selection with minimum representation
    proportion = len(presets) / total_available
    count = max(50, int(total_needed * proportion))  # At least 50 per category

    # Don't exceed available
    count = min(count, len(presets))

    # Random sample from this category
    sampled = random.sample(presets, count)
    selected_presets.extend(sampled)
    print(f'  Selected {count} from {category}')

# If we're over 1000, trim randomly
if len(selected_presets) > 1000:
    selected_presets = random.sample(selected_presets, 1000)
    print(f'\n⚠️  Trimmed to exactly 1000 presets')

# If we're under 1000, add more from remaining
elif len(selected_presets) < 1000:
    remaining_presets = [p for p in unprocessed_presets if p not in selected_presets]
    needed = 1000 - len(selected_presets)
    selected_presets.extend(random.sample(remaining_presets, needed))
    print(f'\n✅ Added {needed} more to reach 1000')

print(f'\n✅ Selected {len(selected_presets)} diverse presets')

# Shuffle for random distribution
random.shuffle(selected_presets)

# Split into 500 for Gemini, 500 for Claude
gemini_presets = selected_presets[:500]
claude_presets = selected_presets[500:]

print(f'\n📤 Split Results:')
print(f'  Gemini: {len(gemini_presets)} presets')
print(f'  Claude: {len(claude_presets)} presets')

# Save splits
with open('data/gemini_presets_500.json', 'w') as f:
    json.dump(gemini_presets, f, indent=2)

with open('data/claude_presets_500.json', 'w') as f:
    json.dump(claude_presets, f, indent=2)

# Save combined for reference
with open('data/diverse_presets_1000.json', 'w') as f:
    json.dump({
        'total': len(selected_presets),
        'gemini_count': len(gemini_presets),
        'claude_count': len(claude_presets),
        'categories': {k: len(v) for k, v in categories.items()},
        'presets': selected_presets
    }, f, indent=2)

print(f'\n💾 Saved Files:')
print(f'  data/gemini_presets_500.json')
print(f'  data/claude_presets_500.json')
print(f'  data/diverse_presets_1000.json')
print(f'\n{"="*60}')
print(f'✅ Selection Complete!')
print(f'{"="*60}')