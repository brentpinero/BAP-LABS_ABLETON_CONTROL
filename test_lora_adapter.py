#!/usr/bin/env python3
"""
Test the trained LoRA adapter
"""
from mlx_lm import load, generate

print("🔧 Loading model with LoRA adapter...")
model, tokenizer = load(
    "NousResearch/Hermes-2-Pro-Mistral-7B",
    adapter_path="serum_lora_adapters/production_adapters"
)

test_prompts = [
    "Create a deep dubstep bass with lots of wobble",
    "Make a bright future bass lead",
    "Ambient pad for cinematic backgrounds",
    "Gnarly neuro reese bass for drum and bass"
]

print("\n" + "="*80)
print("🎯 TESTING BAP-LABS-M1 LORA ADAPTER")
print("="*80 + "\n")

for i, user_prompt in enumerate(test_prompts, 1):
    prompt = f"""<|im_start|>system
You are a Serum synthesizer preset designer. Generate JSON parameter changes for Serum presets based on natural language descriptions.<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
"""

    print(f"\n{'='*80}")
    print(f"Test {i}: {user_prompt}")
    print('-'*80)

    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=500,
        verbose=False
    )

    print(response)
    print('='*80)
