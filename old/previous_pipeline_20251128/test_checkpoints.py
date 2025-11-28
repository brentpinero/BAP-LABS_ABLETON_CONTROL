#!/usr/bin/env python3
"""
Test different checkpoint versions to find which one works best
"""
from mlx_lm import load, generate
import json

test_prompt = "Create a deep dubstep bass with lots of wobble"

checkpoints = [
    ("Iteration 100", "serum_lora_adapters/production_adapters/0000100_adapters.safetensors"),
    ("Iteration 200", "serum_lora_adapters/production_adapters/0000200_adapters.safetensors"),
    ("Final (300)", "serum_lora_adapters/production_adapters/adapters.safetensors"),
]

print("="*80)
print("🔍 TESTING DIFFERENT CHECKPOINTS")
print("="*80 + "\n")

for name, adapter_path in checkpoints:
    print(f"\n{'='*80}")
    print(f"📍 Testing: {name}")
    print(f"   Path: {adapter_path}")
    print('-'*80)

    # Load model with specific checkpoint
    print("   Loading model...")
    model, tokenizer = load(
        "NousResearch/Hermes-2-Pro-Mistral-7B",
        adapter_path=adapter_path
    )

    prompt = f"""<|im_start|>system
You are a Serum synthesizer preset designer. Generate JSON parameter changes for Serum presets based on natural language descriptions.<|im_end|>
<|im_start|>user
{test_prompt}<|im_end|>
<|im_start|>assistant
"""

    print(f"   Generating...")
    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=500,
        verbose=False
    )

    print(f"\n   RESPONSE:")
    print(f"   {response[:500]}...")  # First 500 chars

    # Try to parse as JSON
    try:
        # Extract JSON from response
        if '{' in response and '}' in response:
            json_start = response.index('{')
            json_end = response.rindex('}') + 1
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            print(f"\n   ✅ Valid JSON! Keys: {list(parsed.keys())}")
        else:
            print(f"\n   ❌ No JSON structure found")
    except Exception as e:
        print(f"\n   ❌ JSON parse failed: {e}")

    print('='*80)
