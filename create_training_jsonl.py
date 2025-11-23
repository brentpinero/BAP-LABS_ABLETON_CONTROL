#!/usr/bin/env python3

import json

def create_training_jsonl():
    """Create JSONL format for Mistral training"""

    # Load clean dataset
    with open("data/serum_gpt5_mistral_COMPLETE_dataset_CLEAN.json", 'r') as f:
        data = json.load(f)

    # Create JSONL
    with open("data/serum_gpt5_mistral_training.jsonl", 'w') as f:
        for example in data["examples"]:
            # Extract just the mistral template for training
            training_example = {
                "text": example["mistral_template"]
            }
            f.write(json.dumps(training_example) + '\n')

    print(f"✅ Created training JSONL with {len(data['examples'])} examples")
    print(f"📄 Saved to: data/serum_gpt5_mistral_training.jsonl")

    # Print sample
    print(f"\n🎯 Sample training example:")
    print(data["examples"][0]["mistral_template"][:200] + "...")

if __name__ == "__main__":
    create_training_jsonl()