import json

file1 = "data/serum_gpt5_mistral_FINAL_filtered_500.json"
file2 = "data/serum_gpt5_mistral_500_diverse_dataset.json"
output_file = "data/serum_gpt5_mistral_combined_898.json"

with open(file1, 'r') as f:
    data1 = json.load(f)

with open(file2, 'r') as f:
    data2 = json.load(f)

combined_examples = []

for example in data1['examples']:
    if 'preset_name' in example['response']:
        del example['response']['preset_name']
    combined_examples.append(example)

for example in data2['examples']:
    if 'preset_name' in example['response']:
        del example['response']['preset_name']
    combined_examples.append(example)

combined_data = {
    "metadata": {
        "total_examples": len(combined_examples),
        "source_datasets": [file1, file2],
        "average_quality": (data1['metadata']['average_quality'] * len(data1['examples']) +
                           data2['metadata']['average_quality'] * len(data2['examples'])) / len(combined_examples),
        "description": "Combined GPT-5 generated Serum parameter datasets with preset_name removed"
    },
    "examples": combined_examples
}

with open(output_file, 'w') as f:
    json.dump(combined_data, f, indent=2)

print(f"✅ Combined {len(combined_examples)} examples")
print(f"📊 Average quality: {combined_data['metadata']['average_quality']:.3f}")
print(f"💾 Saved to {output_file}")