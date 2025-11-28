#!/usr/bin/env python3
"""
Create proper train/val/test split for LoRA fine-tuning
- Train: 80%
- Val: 10%
- Test: 10% (held out for final evaluation)
"""
import json
from pathlib import Path
import random

# Set seed for reproducibility
random.seed(42)

# Load the corrected dataset
input_file = "data/serum_gpt5_mistral_897_CORRECTED_hermes_training.jsonl"
output_dir = Path("serum_lora_adapters/training_data_v2")
output_dir.mkdir(parents=True, exist_ok=True)

print("="*80)
print("📊 CREATING TRAIN/VAL/TEST SPLIT")
print("="*80)

# Load all examples
examples = []
with open(input_file, 'r') as f:
    for line in f:
        examples.append(json.loads(line.strip()))

total = len(examples)
print(f"\n📝 Total examples: {total}")

# Shuffle
random.shuffle(examples)

# Split: 80% train, 10% val, 10% test
train_end = int(total * 0.8)
val_end = int(total * 0.9)

train_examples = examples[:train_end]
val_examples = examples[train_end:val_end]
test_examples = examples[val_end:]

print(f"\n📈 Split breakdown:")
print(f"   Train: {len(train_examples)} ({len(train_examples)/total*100:.1f}%)")
print(f"   Val:   {len(val_examples)} ({len(val_examples)/total*100:.1f}%)")
print(f"   Test:  {len(test_examples)} ({len(test_examples)/total*100:.1f}%)")

# Write train file
train_file = output_dir / "train.jsonl"
with open(train_file, 'w') as f:
    for example in train_examples:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')

# Write validation file
val_file = output_dir / "valid.jsonl"
with open(val_file, 'w') as f:
    for example in val_examples:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')

# Write test file (held out)
test_file = output_dir / "test.jsonl"
with open(test_file, 'w') as f:
    for example in test_examples:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')

print(f"\n✅ Files created:")
print(f"   {train_file}")
print(f"   {val_file}")
print(f"   {test_file}")

# Extract test prompts for later evaluation
test_prompts = []
for example in test_examples[:10]:  # Save first 10 test prompts
    text = example['text']
    # Extract user prompt
    import re
    match = re.search(r'<\|im_start\|>user\n(.*?)\n<\|im_end\|>', text, re.DOTALL)
    if match:
        test_prompts.append(match.group(1).strip())

test_prompts_file = output_dir / "test_prompts.json"
with open(test_prompts_file, 'w') as f:
    json.dump(test_prompts, f, indent=2)

print(f"\n📋 Sample test prompts saved to: {test_prompts_file}")
print("\nFirst 5 test prompts:")
for i, prompt in enumerate(test_prompts[:5], 1):
    print(f"   {i}. {prompt}")

print("\n" + "="*80)
print("🎉 DATASET READY FOR TRAINING")
print("="*80)
