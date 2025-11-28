#!/usr/bin/env python3
"""
Test base model WITHOUT adapters to see if prompt format works
"""
from mlx_lm import load, generate

print("🔧 Loading BASE model (no adapters)...")
model, tokenizer = load("NousResearch/Hermes-2-Pro-Mistral-7B")

test_prompt = "Create a deep dubstep bass with lots of wobble"

prompt = f"""<|im_start|>system
You are a Serum synthesizer preset designer. Generate JSON parameter changes for Serum presets based on natural language descriptions.<|im_end|>
<|im_start|>user
{test_prompt}<|im_end|>
<|im_start|>assistant
"""

print("\n" + "="*80)
print("🎯 TESTING BASE MODEL (NO LORA)")
print("="*80)
print(f"\nPrompt: {test_prompt}")
print("\nGenerating...")

response = generate(
    model,
    tokenizer,
    prompt=prompt,
    max_tokens=500,
    verbose=False
)

print("\n" + "="*80)
print("RESPONSE:")
print("="*80)
print(response)
print("="*80)
