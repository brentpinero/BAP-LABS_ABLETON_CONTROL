#!/usr/bin/env python3
"""
Test the FIRST adapter we trained (50 iters, 8 layers, batch 2)
This one had better validation loss behavior
"""
from mlx_lm import load, generate

print("🔧 Loading FIRST test adapter (50 iters)...")
model, tokenizer = load(
    "NousResearch/Hermes-2-Pro-Mistral-7B",
    adapter_path="serum_lora_adapters/adapters"
)

test_prompt = "Create a deep dubstep bass with lots of wobble"

# USE THE EXACT SYSTEM PROMPT FROM TRAINING
prompt = f"""<|im_start|>system
You are a Serum 2 synthesizer preset generator. You create parameter settings for the Serum 2 synthesizer based on musical descriptions.

Your responses must be valid JSON with this exact structure:
{{
  "parameter_changes": [
    {{"index": 1, "value": 0.75, "name": "Main Vol"}},
    {{"index": 22, "value": 0.5, "name": "A Level"}}
  ],
  "critical_changes": ["Main Vol", "A Level"]
}}

Guidelines:
- Use parameter indices 1-2623 (Serum 2 has 2623 parameters)
- All values must be between 0.0 and 1.0
- Include 15-20 parameter changes per preset
- Focus on parameters that create the described sound
- Always include critical_changes array with key parameter names
<|im_end|>
<|im_start|>user
{test_prompt}
<|im_end|>
<|im_start|>assistant
"""

print("\n" + "="*80)
print("🎯 TESTING FIRST ADAPTER (50 iters, 8 layers, batch 2)")
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
