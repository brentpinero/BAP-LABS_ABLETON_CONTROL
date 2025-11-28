#!/usr/bin/env python3
"""
Cross-reference the 78 problematic GPT-5 presets with original Serum presets
to see if GPT-5 misrepresented them or if they're genuinely edge cases
"""

import json
import re
from pathlib import Path
from difflib import SequenceMatcher

# Paths
LOW_OSC_ANALYSIS = "data/low_osc_analysis.json"
ORIGINAL_DATASET = "data/ultimate_training_dataset/ultimate_serum_dataset.json"
GPT5_COMBINED = "data/serum_gpt5_mistral_combined_898.json"
HERMES_DATASET = "data/serum_gpt5_mistral_combined_897_hermes_training.jsonl"

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_instruction_from_line(line_num: int, dataset_path: str):
    """Extract instruction from a specific line in JSONL"""
    with open(dataset_path, 'r') as f:
        for idx, line in enumerate(f, 1):
            if idx == line_num:
                entry = json.loads(line.strip())
                text = entry['text']
                match = re.search(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', text, re.DOTALL)
                return match.group(1).strip() if match else ""
    return ""

def get_params_from_line(line_num: int, dataset_path: str):
    """Extract parameters from a specific line in JSONL"""
    with open(dataset_path, 'r') as f:
        for idx, line in enumerate(f, 1):
            if idx == line_num:
                entry = json.loads(line.strip())
                text = entry['text']
                match = re.search(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(1).strip())
                    except:
                        return {}
    return {}

def get_param_value(params, name):
    """Get parameter value by name"""
    if isinstance(params, dict) and 'parameter_changes' in params:
        for p in params.get('parameter_changes', []):
            if p.get('name') == name:
                return float(p.get('value', 0.0))
    return 0.0

def find_matching_original_preset(instruction: str, original_presets: list):
    """Find best matching original preset by instruction/preset name similarity"""
    best_match = None
    best_score = 0.0

    for preset in original_presets:
        preset_name = preset.get('preset_name', '').strip('\x00').strip()

        # Calculate similarity
        score = similarity(instruction, preset_name)

        if score > best_score:
            best_score = score
            best_match = preset

    return best_match, best_score

print("🔍 Cross-referencing 78 problematic presets with original Serum dataset...\n")

# Load problem analysis
with open(LOW_OSC_ANALYSIS, 'r') as f:
    analysis = json.load(f)

# Load original Serum dataset
print("Loading original Serum dataset...")
with open(ORIGINAL_DATASET, 'r') as f:
    original_presets = json.load(f)
print(f"  Loaded {len(original_presets)} original presets\n")

# Combine all problematic presets
all_problematic = (
    analysis['genuinely_broken'] +
    analysis['questionable'] +
    analysis['valid_noise_based']
)

print(f"Analyzing {len(all_problematic)} problematic presets...\n")
print("="*80)

results = {
    'gpt5_misrepresented': [],
    'gpt5_generated_correctly': [],
    'no_match_found': []
}

for idx, problem in enumerate(all_problematic[:20], 1):  # Start with first 20 for testing
    line_num = problem['line']
    instruction = problem['instruction']

    print(f"\n[{idx}] Line {line_num}")
    print(f"Instruction: {instruction}")
    print(f"GPT-5 Output: Osc A={problem['osc_a']:.3f}, B={problem['osc_b']:.3f}, Noise={problem['noise']:.3f}")

    # Try to find matching original preset
    match, score = find_matching_original_preset(instruction, original_presets)

    if match and score > 0.3:  # Reasonable similarity threshold
        preset_name = match.get('preset_name', '').strip('\x00').strip()
        params = match.get('parameters', {})

        # Get original oscillator levels
        orig_a_vol = params.get('a_vol', 0.0)
        orig_b_vol = params.get('b_vol', 0.0)
        orig_noise = params.get('noise_level', 0.0)

        print(f"  ✓ Match Found: '{preset_name}' (similarity: {score:.2f})")
        print(f"  Original Preset: Osc A={orig_a_vol:.3f}, B={orig_b_vol:.3f}, Noise={orig_noise:.3f}")

        # Compare
        orig_combined_osc = max(orig_a_vol, orig_b_vol)
        gpt5_combined_osc = max(problem['osc_a'], problem['osc_b'])

        # Check if GPT-5 misrepresented
        if orig_combined_osc > 0.1 and gpt5_combined_osc < 0.1:
            print(f"  ❌ GPT-5 MISREPRESENTED: Original had {orig_combined_osc:.3f} osc level, GPT-5 made it {gpt5_combined_osc:.3f}")
            results['gpt5_misrepresented'].append({
                'line': line_num,
                'instruction': instruction,
                'original_preset': preset_name,
                'original_osc_a': orig_a_vol,
                'original_osc_b': orig_b_vol,
                'original_noise': orig_noise,
                'gpt5_osc_a': problem['osc_a'],
                'gpt5_osc_b': problem['osc_b'],
                'gpt5_noise': problem['noise'],
                'similarity_score': score
            })
        elif orig_combined_osc < 0.1 and gpt5_combined_osc < 0.1:
            print(f"  ✓ GPT-5 CORRECT: Original was also low osc ({orig_combined_osc:.3f}), GPT-5 matched it")
            results['gpt5_generated_correctly'].append({
                'line': line_num,
                'instruction': instruction,
                'original_preset': preset_name,
                'reason': 'Correctly represented low-osc or noise-based preset',
                'similarity_score': score
            })
        else:
            print(f"  ⚠️  Unclear: Different representation style")
    else:
        print(f"  ⚠️  No clear match found in original dataset (best score: {score:.2f})")
        results['no_match_found'].append({
            'line': line_num,
            'instruction': instruction,
            'best_match_score': score,
            'best_match_name': match.get('preset_name', '').strip('\x00').strip() if match else None
        })

print("\n" + "="*80)
print("📊 CROSS-REFERENCE SUMMARY")
print("="*80)
print(f"GPT-5 Misrepresented Presets:  {len(results['gpt5_misrepresented'])}")
print(f"GPT-5 Generated Correctly:     {len(results['gpt5_generated_correctly'])}")
print(f"No Match Found:                {len(results['no_match_found'])}")
print()

# Save results
output_path = "data/cross_reference_report.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"📝 Detailed cross-reference report saved to: {output_path}\n")

# Show misrepresented examples
if results['gpt5_misrepresented']:
    print("\n❌ GPT-5 MISREPRESENTED EXAMPLES:")
    print("-"*80)
    for item in results['gpt5_misrepresented']:
        print(f"\nLine {item['line']}: {item['instruction']}")
        print(f"  Original '{item['original_preset']}':")
        print(f"    Osc A: {item['original_osc_a']:.3f} → GPT-5: {item['gpt5_osc_a']:.3f}")
        print(f"    Osc B: {item['original_osc_b']:.3f} → GPT-5: {item['gpt5_osc_b']:.3f}")
        print(f"    Noise: {item['original_noise']:.3f} → GPT-5: {item['gpt5_noise']:.3f}")
