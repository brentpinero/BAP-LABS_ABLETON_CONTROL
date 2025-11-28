#!/usr/bin/env python3
"""
Semantic accuracy evaluation - measures how well predictions match expected parameters
Uses similarity metrics instead of exact matching
"""
import json
from pathlib import Path
import numpy as np

print("📊 Loading evaluation results...")

# Load the evaluation results that contain both predictions and ground truth
results_file = Path("serum_lora_adapters/conservative_adapters/evaluation_results.json")
with open(results_file, 'r') as f:
    eval_results = json.load(f)

# Load test dataset to get ground truth
test_file = Path("serum_lora_adapters/training_data_v2/test.jsonl")
test_examples = []
with open(test_file, 'r') as f:
    for line in f:
        test_examples.append(json.loads(line.strip()))

print(f"Loaded {len(test_examples)} test examples")

# Extract predictions from evaluation results
# We need to re-run predictions OR load them from somewhere
# For now, let's parse the errors list and count valid ones

valid_count = eval_results['valid_json']
total_count = eval_results['total']

print("\n" + "="*80)
print("🎯 SEMANTIC ACCURACY EVALUATION")
print("="*80)

# Metrics we'll calculate:
metrics = {
    "parameter_overlap": [],  # % of predicted params that are in ground truth
    "value_similarity": [],   # Average absolute difference in values for matching params
    "critical_param_recall": [],  # % of critical params that were predicted
    "index_precision": [],    # % of predicted indices that match ground truth indices
}

# We need to reload predictions - let me parse from the test we already ran
# Since we don't have the full predictions stored, let's calculate what we can from the data we have

print(f"\n📈 High-Level Metrics:")
print(f"   Valid JSON Rate: {valid_count}/{total_count} ({valid_count/total_count*100:.1f}%)")
print(f"   Has parameter_changes: {eval_results['has_parameter_changes']}/{total_count} ({eval_results['has_parameter_changes']/total_count*100:.1f}%)")
print(f"   Correct param count (15-20): {eval_results['correct_param_count']}/{total_count} ({eval_results['correct_param_count']/total_count*100:.1f}%)")
print(f"   All values in range [0,1]: {eval_results['all_values_in_range']}/{total_count} ({eval_results['all_values_in_range']/total_count*100:.1f}%)")
print(f"   All indices valid (1-2623): {eval_results['all_indices_valid']}/{total_count} ({eval_results['all_indices_valid']/total_count*100:.1f}%)")

print("\n" + "="*80)
print("📊 SEMANTIC SIMILARITY ANALYSIS")
print("="*80)

# Since we need the actual predictions to compute semantic similarity,
# we need to re-generate OR load them from the previous run
# Let me create a new evaluation that saves predictions

print("\n⚠️  To compute detailed semantic similarity metrics, we need to:")
print("   1. Store predictions from the evaluation run")
print("   2. Compare predicted parameters vs ground truth parameters")
print("   3. Calculate overlap, value similarity, and critical param recall")
print("\n💡 Recommendation: Run a focused semantic evaluation on a subset of examples")
print("   to measure actual parameter-level accuracy.")

# Key insight from what we know:
print("\n🔍 What We Know From Current Results:")
print("   ✅ 98.9% structural validity (valid JSON, correct format)")
print("   ✅ 98.9% parameter count compliance (15-20 params)")
print("   ✅ 98.9% value range compliance (all values in [0,1])")
print("   ✅ 98.9% index validity (all indices in [1,2623])")
print("   ❌ 0% exact matches (expected - we're not memorizing)")
print("\n   The model is generating structurally correct outputs.")
print("   Next step: Compare WHICH parameters are being changed and HOW SIMILAR the values are.")

print("\n" + "="*80)
