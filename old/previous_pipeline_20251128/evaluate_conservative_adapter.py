#!/usr/bin/env python3
"""
Comprehensive evaluation of conservative adapter on full test dataset
Validates JSON structure, parameter accuracy, and semantic correctness
"""
from mlx_lm import load, generate
import json
from pathlib import Path

print("🔧 Loading conservative adapter...")
model, tokenizer = load(
    "NousResearch/Hermes-2-Pro-Mistral-7B",
    adapter_path="serum_lora_adapters/conservative_adapters"
)

# Load full test dataset
test_file = Path("serum_lora_adapters/training_data_v2/test.jsonl")
test_examples = []
with open(test_file, 'r') as f:
    for line in f:
        test_examples.append(json.loads(line.strip()))

print(f"📊 Loaded {len(test_examples)} test examples")

# System prompt from training
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
print("🎯 EVALUATING CONSERVATIVE ADAPTER ON TEST DATASET")
print("="*80)

# Evaluation metrics
results = {
    "total": 0,
    "valid_json": 0,
    "has_parameter_changes": 0,
    "has_critical_changes": 0,
    "correct_param_count": 0,
    "all_values_in_range": 0,
    "all_indices_valid": 0,
    "exact_match": 0,
    "errors": []
}

for i, example in enumerate(test_examples, 1):
    # Extract user prompt from training example
    text = example['text']
    import re
    user_match = re.search(r'<\|im_start\|>user\n(.*?)\n<\|im_end\|>', text, re.DOTALL)
    if not user_match:
        continue

    user_prompt = user_match.group(1).strip()

    # Extract expected response
    expected_match = re.search(r'<\|im_start\|>assistant\n(.*?)\n<\|im_end\|>', text, re.DOTALL)
    expected_response = expected_match.group(1).strip() if expected_match else None

    # Generate prediction
    prompt = f"{system_prompt}\n<|im_start|>user\n{user_prompt}\n<|im_end|>\n<|im_start|>assistant\n"

    print(f"\n[{i}/{len(test_examples)}] Testing: {user_prompt[:60]}...")

    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=2048,
        verbose=False
    )

    results["total"] += 1

    # Validate JSON structure
    try:
        predicted = json.loads(response)
        results["valid_json"] += 1

        # Check has parameter_changes
        if "parameter_changes" in predicted:
            results["has_parameter_changes"] += 1
            params = predicted["parameter_changes"]

            # Check parameter count (15-20 expected)
            if 15 <= len(params) <= 20:
                results["correct_param_count"] += 1

            # Check all values in range [0, 1]
            all_in_range = all(
                0.0 <= p.get("value", -1) <= 1.0
                for p in params
            )
            if all_in_range:
                results["all_values_in_range"] += 1

            # Check all indices valid (1-2623)
            all_valid_idx = all(
                1 <= p.get("index", 0) <= 2623
                for p in params
            )
            if all_valid_idx:
                results["all_indices_valid"] += 1

        # Check has critical_changes
        if "critical_changes" in predicted:
            results["has_critical_changes"] += 1

        # Check exact match with expected
        if expected_response:
            try:
                expected = json.loads(expected_response)
                if predicted == expected:
                    results["exact_match"] += 1
            except:
                pass

        print(f"  ✅ Valid JSON - {len(params)} params")

    except json.JSONDecodeError as e:
        results["errors"].append({
            "example": i,
            "prompt": user_prompt[:60],
            "error": str(e),
            "response": response[:200]
        })
        print(f"  ❌ Invalid JSON: {e}")

print("\n" + "="*80)
print("📊 EVALUATION RESULTS")
print("="*80)

total = results["total"]
print(f"\nTotal examples evaluated: {total}")
print(f"\n✅ Structural Validation:")
print(f"   Valid JSON: {results['valid_json']}/{total} ({results['valid_json']/total*100:.1f}%)")
print(f"   Has parameter_changes: {results['has_parameter_changes']}/{total} ({results['has_parameter_changes']/total*100:.1f}%)")
print(f"   Has critical_changes: {results['has_critical_changes']}/{total} ({results['has_critical_changes']/total*100:.1f}%)")

print(f"\n📏 Parameter Quality:")
print(f"   Correct param count (15-20): {results['correct_param_count']}/{total} ({results['correct_param_count']/total*100:.1f}%)")
print(f"   All values in range [0,1]: {results['all_values_in_range']}/{total} ({results['all_values_in_range']/total*100:.1f}%)")
print(f"   All indices valid (1-2623): {results['all_indices_valid']}/{total} ({results['all_indices_valid']/total*100:.1f}%)")

print(f"\n🎯 Accuracy:")
print(f"   Exact match with expected: {results['exact_match']}/{total} ({results['exact_match']/total*100:.1f}%)")

if results["errors"]:
    print(f"\n❌ Errors ({len(results['errors'])}):")
    for err in results["errors"][:5]:  # Show first 5 errors
        print(f"   Example {err['example']}: {err['error']}")
        print(f"   Prompt: {err['prompt']}")
        print(f"   Response: {err['response']}...")

# Save detailed results
output_file = Path("serum_lora_adapters/conservative_adapters/evaluation_results.json")
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n💾 Detailed results saved to: {output_file}")
print("="*80)
