#!/usr/bin/env python3
"""Quick test of batch 2 processing"""

import json

# Check input file
with open('data/gpt5_input_500_diverse_batch2.json', 'r') as f:
    data = json.load(f)

print(f"✅ Input file loaded successfully")
print(f"  - Total presets: {len(data['presets'])}")
print(f"  - Range: {data['metadata']['range']}")

# Check first preset structure
first_preset = data['presets'][0]
print(f"\n📊 First preset structure:")
print(f"  - Name: {first_preset.get('preset_name', 'Unknown')}")
print(f"  - Category: {first_preset.get('category', 'Unknown')}")
print(f"  - Parameters: {len(first_preset.get('parameters', {}))}")

# Sample first few parameter names
params = first_preset.get('parameters', {})
param_names = list(params.keys())[:5]
print(f"\n🎛️ Sample parameters:")
for name in param_names:
    print(f"  - {name}: {params[name]}")

print("\n✅ Data structure looks good for processing!")
print("\nTo start full GPT-5 processing, run:")
print("python3 gpt5_serum_mistral_pipeline_batch2.py")