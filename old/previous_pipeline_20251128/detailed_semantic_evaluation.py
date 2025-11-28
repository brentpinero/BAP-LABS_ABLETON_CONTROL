#!/usr/bin/env python3
"""
Detailed semantic evaluation - compares predicted parameters to ground truth
Calculates parameter overlap, value similarity, and critical parameter recall
"""
from mlx_lm import load, generate
import json
from pathlib import Path
import numpy as np
import re

print("🔧 Loading conservative adapter...")
model, tokenizer = load(
    "NousResearch/Hermes-2-Pro-Mistral-7B",
    adapter_path="serum_lora_adapters/conservative_adapters"
)

# Load test dataset
test_file = Path("serum_lora_adapters/training_data_v2/test.jsonl")
test_examples = []
with open(test_file, 'r') as f:
    for line in f:
        test_examples.append(json.loads(line.strip()))

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

print(f"📊 Evaluating first 20 test examples for detailed semantic analysis...")
print("\n" + "="*80)

# Semantic similarity metrics
semantic_metrics = {
    "parameter_overlap_scores": [],     # Jaccard similarity of parameter indices
    "value_mae_scores": [],             # Mean Absolute Error for matching params
    "critical_param_recall_scores": [], # Recall of critical parameters
    "parameter_name_overlap": [],       # % of parameter names that match
}

detailed_results = []

for i, example in enumerate(test_examples[:20], 1):  # First 20 for detailed analysis
    # Extract user prompt and expected response
    text = example['text']
    user_match = re.search(r'<\|im_start\|>user\n(.*?)\n<\|im_end\|>', text, re.DOTALL)
    if not user_match:
        continue

    user_prompt = user_match.group(1).strip()

    expected_match = re.search(r'<\|im_start\|>assistant\n(.*?)\n<\|im_end\|>', text, re.DOTALL)
    if not expected_match:
        continue

    expected_json = expected_match.group(1).strip()

    # Generate prediction
    prompt = f"{system_prompt}\n<|im_start|>user\n{user_prompt}\n<|im_end|>\n<|im_start|>assistant\n"

    print(f"\n[{i}/20] {user_prompt[:60]}...")

    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=2048,
        verbose=False
    )

    try:
        expected = json.loads(expected_json)
        predicted = json.loads(response)

        # Extract parameter sets
        expected_params = {p['index']: p['value'] for p in expected['parameter_changes']}
        predicted_params = {p['index']: p['value'] for p in predicted['parameter_changes']}

        expected_names = {p['name'] for p in expected['parameter_changes']}
        predicted_names = {p['name'] for p in predicted['parameter_changes']}

        # 1. Parameter Overlap (Jaccard similarity of indices)
        expected_indices = set(expected_params.keys())
        predicted_indices = set(predicted_params.keys())
        intersection = expected_indices & predicted_indices
        union = expected_indices | predicted_indices
        jaccard = len(intersection) / len(union) if union else 0
        semantic_metrics["parameter_overlap_scores"].append(jaccard)

        # 2. Value MAE for matching parameters
        if intersection:
            mae_values = []
            for idx in intersection:
                mae_values.append(abs(expected_params[idx] - predicted_params[idx]))
            mae = np.mean(mae_values)
            semantic_metrics["value_mae_scores"].append(mae)

        # 3. Critical parameter recall
        expected_critical = set(expected.get('critical_changes', []))
        predicted_critical = set(predicted.get('critical_changes', []))
        if expected_critical:
            recall = len(expected_critical & predicted_critical) / len(expected_critical)
            semantic_metrics["critical_param_recall_scores"].append(recall)

        # 4. Parameter name overlap
        name_intersection = expected_names & predicted_names
        name_union = expected_names | predicted_names
        name_overlap = len(name_intersection) / len(name_union) if name_union else 0
        semantic_metrics["parameter_name_overlap"].append(name_overlap)

        print(f"  ✅ Param Overlap: {jaccard:.2f} | Value MAE: {mae:.3f} | Name Overlap: {name_overlap:.2f}")

        detailed_results.append({
            "prompt": user_prompt,
            "param_overlap": jaccard,
            "value_mae": mae if intersection else None,
            "name_overlap": name_overlap,
            "expected_param_count": len(expected_params),
            "predicted_param_count": len(predicted_params),
        })

    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON: {e}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*80)
print("📊 SEMANTIC ACCURACY RESULTS (First 20 Examples)")
print("="*80)

if semantic_metrics["parameter_overlap_scores"]:
    print(f"\n🎯 Parameter Index Overlap (Jaccard):")
    print(f"   Mean: {np.mean(semantic_metrics['parameter_overlap_scores']):.3f}")
    print(f"   Median: {np.median(semantic_metrics['parameter_overlap_scores']):.3f}")
    print(f"   Min: {np.min(semantic_metrics['parameter_overlap_scores']):.3f}")
    print(f"   Max: {np.max(semantic_metrics['parameter_overlap_scores']):.3f}")

if semantic_metrics["value_mae_scores"]:
    print(f"\n📏 Value Similarity (MAE for matching params):")
    print(f"   Mean: {np.mean(semantic_metrics['value_mae_scores']):.3f}")
    print(f"   Median: {np.median(semantic_metrics['value_mae_scores']):.3f}")
    print(f"   (Lower is better - 0.0 = perfect match)")

if semantic_metrics["critical_param_recall_scores"]:
    print(f"\n⭐ Critical Parameter Recall:")
    print(f"   Mean: {np.mean(semantic_metrics['critical_param_recall_scores']):.3f}")
    print(f"   Median: {np.median(semantic_metrics['critical_param_recall_scores']):.3f}")
    print(f"   (1.0 = all critical params predicted)")

if semantic_metrics["parameter_name_overlap"]:
    print(f"\n📝 Parameter Name Overlap:")
    print(f"   Mean: {np.mean(semantic_metrics['parameter_name_overlap']):.3f}")
    print(f"   Median: {np.median(semantic_metrics['parameter_name_overlap']):.3f}")

# Save detailed results
output_file = Path("serum_lora_adapters/conservative_adapters/semantic_accuracy_results.json")
with open(output_file, 'w') as f:
    json.dump({
        "summary_metrics": {
            "param_overlap_mean": float(np.mean(semantic_metrics['parameter_overlap_scores'])) if semantic_metrics['parameter_overlap_scores'] else None,
            "value_mae_mean": float(np.mean(semantic_metrics['value_mae_scores'])) if semantic_metrics['value_mae_scores'] else None,
            "critical_recall_mean": float(np.mean(semantic_metrics['critical_param_recall_scores'])) if semantic_metrics['critical_param_recall_scores'] else None,
            "name_overlap_mean": float(np.mean(semantic_metrics['parameter_name_overlap'])) if semantic_metrics['parameter_name_overlap'] else None,
        },
        "detailed_results": detailed_results
    }, f, indent=2)

print(f"\n💾 Detailed results saved to: {output_file}")
print("="*80)
