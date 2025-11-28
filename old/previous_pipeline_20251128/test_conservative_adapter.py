#!/usr/bin/env python3
"""
Test the conservative adapter (1e-4 LR, 500 iters) with holdout test prompts
"""
from mlx_lm import load, generate
import json

print("🔧 Loading conservative adapter...")
model, tokenizer = load(
    "NousResearch/Hermes-2-Pro-Mistral-7B",
    adapter_path="serum_lora_adapters/conservative_adapters"
)

# Load test prompts
with open("serum_lora_adapters/training_data_v2/test_prompts.json", 'r') as f:
    test_prompts = json.load(f)

# Use the exact system prompt from training
system_prompt = """<|im_start|>system
You are a Serum 2 synthesizer preset generator. You create parameter settings for the Serum 2 synthesizer based on musical descriptions.

Your responses must be valid JSON with this exact structure:
{
  "parameter_changes": [
    {"index": 1, "value": 0.75, "name": "Main Vol"},
    {"index": 22, "value": 0.5, "name": "A Level"}
  ],
  "critical_changes": ["Main Vol", "A Level"]
}

Guidelines:
- Use parameter indices 1-2623 (Serum 2 has 2623 parameters)
- All values must be between 0.0 and 1.0
- Include 15-20 parameter changes per preset
- Focus on parameters that create the described sound
- Always include critical_changes array with key parameter names
<|im_end|>"""

print("\n" + "="*80)
print("🎯 TESTING CONSERVATIVE ADAPTER (1e-4 LR, 500 iters)")
print("="*80)

results = []

for i, test_prompt in enumerate(test_prompts, 1):
    prompt = f"{system_prompt}\n<|im_start|>user\n{test_prompt}\n<|im_end|>\n<|im_start|>assistant\n"

    print(f"\n{'─'*80}")
    print(f"Test {i}/{len(test_prompts)}: {test_prompt}")
    print(f"{'─'*80}")

    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=16000,
        verbose=False
    )

    # Try to validate JSON
    try:
        json_response = json.loads(response)
        is_valid = "parameter_changes" in json_response
        param_count = len(json_response.get("parameter_changes", []))
        print(f"✅ Valid JSON - {param_count} parameters")
    except json.JSONDecodeError as e:
        is_valid = False
        print(f"❌ Invalid JSON: {e}")

    print(f"\nResponse:\n{response[:300]}...")

    results.append({
        "prompt": test_prompt,
        "valid": is_valid,
        "response": response
    })

print("\n" + "="*80)
print("📊 RESULTS SUMMARY")
print("="*80)
valid_count = sum(1 for r in results if r["valid"])
print(f"Valid JSON responses: {valid_count}/{len(results)} ({valid_count/len(results)*100:.1f}%)")

if valid_count == len(results):
    print("\n🎉 SUCCESS! All responses are valid JSON!")
else:
    print(f"\n⚠️  {len(results) - valid_count} responses failed JSON validation")

print("="*80)
