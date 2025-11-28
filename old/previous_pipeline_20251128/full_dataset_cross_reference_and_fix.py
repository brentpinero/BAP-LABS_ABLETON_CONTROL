#!/usr/bin/env python3
"""
Full cross-reference of all 897 examples and fix misrepresented presets
"""

import json
import re
from pathlib import Path
from difflib import SequenceMatcher

# Paths
ORIGINAL_DATASET = "data/ultimate_training_dataset/ultimate_serum_dataset.json"
HERMES_DATASET = "data/serum_gpt5_mistral_combined_897_hermes_training.jsonl"
OUTPUT_DATASET = "data/serum_gpt5_mistral_897_CORRECTED_hermes_training.jsonl"

# Parameter name mapping: GPT-5 format -> original format
PARAM_NAME_MAP = {
    'Main Vol': 'mastervol',
    'A Level': 'a_vol',
    'A Pan': 'a_pan',
    'A Coarse Pitch': 'a_coarsepit',
    'A WT Pos': 'a_wtpos',
    'B Level': 'b_vol',
    'B Pan': 'b_pan',
    'B Coarse Pitch': 'b_coarsepit',
    'B WT Pos': 'b_wtpos',
    'Noise Level': 'noise_level',
    'LFO 1 Rate': 'lfo1_rate',
    'LFO 2 Rate': 'lfo2_rate',
    'Macro 1': None,  # Not in original
    'Macro 2': None,
    'Macro 3': None,
    'Macro 4': None,
    'Amp': None,
    'LFO 1 Smooth': None,
    'LFO 2 Smooth': None
}

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_instruction(text: str) -> str:
    """Extract instruction from ChatML text"""
    match = re.search(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_params(text: str) -> dict:
    """Extract parameters from ChatML text"""
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

def set_param_value(params, name, value):
    """Set parameter value by name"""
    if isinstance(params, dict) and 'parameter_changes' in params:
        for p in params.get('parameter_changes', []):
            if p.get('name') == name:
                p['value'] = value
                return True
    return False

def find_matching_original_preset(instruction: str, original_presets: list):
    """Find best matching original preset by instruction/preset name similarity"""
    best_match = None
    best_score = 0.0

    for preset in original_presets:
        preset_name = preset.get('preset_name', '').strip('\x00').strip()
        score = similarity(instruction, preset_name)

        if score > best_score:
            best_score = score
            best_match = preset

    return best_match, best_score

def rebuild_chatml_text(text: str, updated_params: dict) -> str:
    """Rebuild ChatML text with updated parameters"""
    # Extract system and user parts
    system_match = re.search(r'(<\|im_start\|>system.*?<\|im_end\|>)', text, re.DOTALL)
    user_match = re.search(r'(<\|im_start\|>user.*?<\|im_end\|>)', text, re.DOTALL)

    system_part = system_match.group(1) if system_match else ""
    user_part = user_match.group(1) if user_match else ""

    # Build new assistant part with updated params
    assistant_part = f"<|im_start|>assistant\n{json.dumps(updated_params, ensure_ascii=False)}<|im_end|>"

    return f"{system_part}\n{user_part}\n{assistant_part}"

print("🔍 Full Cross-Reference and Fix Analysis")
print("="*80)

# Load original presets
print("\nLoading original Serum dataset...")
with open(ORIGINAL_DATASET, 'r') as f:
    original_presets = json.load(f)
print(f"  ✓ Loaded {len(original_presets)} original presets")

# Process all examples
print(f"\nProcessing all examples from {HERMES_DATASET}...")
print("="*80 + "\n")

stats = {
    'total_processed': 0,
    'matches_found': 0,
    'misrepresentations_fixed': 0,
    'no_match_found': 0,
    'already_correct': 0,
    'unfixable': 0
}

corrections_log = []
corrected_examples = []

with open(HERMES_DATASET, 'r') as f:
    for line_num, line in enumerate(f, 1):
        stats['total_processed'] += 1

        try:
            entry = json.loads(line.strip())
            text = entry['text']
            instruction = extract_instruction(text)
            params = extract_params(text)

            if not instruction or not params:
                corrected_examples.append(entry)
                continue

            # Get current oscillator levels
            current_osc_a = get_param_value(params, 'A Level')
            current_osc_b = get_param_value(params, 'B Level')
            current_noise = get_param_value(params, 'Noise Level')
            current_combined_osc = max(current_osc_a, current_osc_b)

            # Find matching original preset
            match, score = find_matching_original_preset(instruction, original_presets)

            if match and score > 0.3:  # Reasonable match
                stats['matches_found'] += 1
                preset_name = match.get('preset_name', '').strip('\x00').strip()
                orig_params = match.get('parameters', {})

                # Get original oscillator levels
                orig_a_vol = orig_params.get('a_vol', 0.0)
                orig_b_vol = orig_params.get('b_vol', 0.0)
                orig_noise = orig_params.get('noise_level', 0.0)
                orig_combined_osc = max(orig_a_vol, orig_b_vol)

                # Check if misrepresented
                needs_fixing = False

                # Major misrepresentation: GPT-5 zeroed out substantial oscillators
                if orig_combined_osc > 0.1 and current_combined_osc < 0.05:
                    needs_fixing = True
                    reason = f"Oscillators zeroed (orig: {orig_combined_osc:.3f}, gpt5: {current_combined_osc:.3f})"

                # Also fix if noise was severely wrong
                elif abs(orig_noise - current_noise) > 0.5 and orig_noise > 0.3:
                    needs_fixing = True
                    reason = f"Noise mismatch (orig: {orig_noise:.3f}, gpt5: {current_noise:.3f})"

                if needs_fixing:
                    # Fix by replacing with original values
                    set_param_value(params, 'A Level', orig_a_vol)
                    set_param_value(params, 'B Level', orig_b_vol)
                    set_param_value(params, 'Noise Level', orig_noise)

                    # Also copy other core parameters if available
                    for gpt5_name, orig_name in PARAM_NAME_MAP.items():
                        if orig_name and orig_name in orig_params:
                            orig_value = orig_params[orig_name]
                            set_param_value(params, gpt5_name, orig_value)

                    # Rebuild entry with corrected params
                    new_text = rebuild_chatml_text(text, params)
                    entry['text'] = new_text

                    stats['misrepresentations_fixed'] += 1

                    corrections_log.append({
                        'line': line_num,
                        'instruction': instruction,
                        'original_preset': preset_name,
                        'similarity': score,
                        'reason': reason,
                        'before': {
                            'osc_a': current_osc_a,
                            'osc_b': current_osc_b,
                            'noise': current_noise
                        },
                        'after': {
                            'osc_a': orig_a_vol,
                            'osc_b': orig_b_vol,
                            'noise': orig_noise
                        }
                    })

                    if line_num <= 10 or stats['misrepresentations_fixed'] <= 20:
                        print(f"✏️  Fixed Line {line_num}: {instruction[:60]}")
                        print(f"   Original: '{preset_name}' (match: {score:.2f})")
                        print(f"   Osc A: {current_osc_a:.3f} → {orig_a_vol:.3f}")
                        print(f"   Osc B: {current_osc_b:.3f} → {orig_b_vol:.3f}")
                        print(f"   Noise: {current_noise:.3f} → {orig_noise:.3f}")
                        print()
                else:
                    stats['already_correct'] += 1
            else:
                stats['no_match_found'] += 1

            corrected_examples.append(entry)

        except Exception as e:
            print(f"❌ Error on line {line_num}: {e}")
            corrected_examples.append(entry)
            continue

        # Progress update
        if line_num % 100 == 0:
            print(f"Progress: {line_num}/897 lines processed...")

print("\n" + "="*80)
print("📊 FULL ANALYSIS SUMMARY")
print("="*80)
print(f"Total Examples Processed:     {stats['total_processed']}")
print(f"Matches Found:                {stats['matches_found']}")
print(f"Misrepresentations Fixed:     {stats['misrepresentations_fixed']}")
print(f"Already Correct:              {stats['already_correct']}")
print(f"No Match Found:               {stats['no_match_found']}")
print()

# Save corrected dataset
print(f"💾 Saving corrected dataset to {OUTPUT_DATASET}...")
with open(OUTPUT_DATASET, 'w') as f:
    for entry in corrected_examples:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f"   ✓ Saved {len(corrected_examples)} examples")
print()

# Save corrections log
log_path = "data/corrections_log.json"
with open(log_path, 'w') as f:
    json.dump({
        'summary': stats,
        'corrections': corrections_log
    }, f, indent=2)

print(f"📝 Corrections log saved to: {log_path}")
print()

# Show sample corrections
if corrections_log:
    print("="*80)
    print("📋 SAMPLE CORRECTIONS (first 10)")
    print("="*80)
    for correction in corrections_log[:10]:
        print(f"\nLine {correction['line']}: {correction['instruction'][:70]}")
        print(f"  Matched: '{correction['original_preset']}' (similarity: {correction['similarity']:.2f})")
        print(f"  Reason: {correction['reason']}")
        print(f"  Before: A={correction['before']['osc_a']:.3f}, B={correction['before']['osc_b']:.3f}, Noise={correction['before']['noise']:.3f}")
        print(f"  After:  A={correction['after']['osc_a']:.3f}, B={correction['after']['osc_b']:.3f}, Noise={correction['after']['noise']:.3f}")

print("\n" + "="*80)
print("✅ CORRECTION COMPLETE!")
print("="*80)
print(f"\n🎯 Corrected dataset: {OUTPUT_DATASET}")
print(f"📊 {stats['misrepresentations_fixed']} presets were fixed")
print(f"🏆 Dataset quality significantly improved!\n")
