#!/usr/bin/env python3
"""
Investigate the 84 presets with low oscillator levels
to determine if they're valid or need to be removed
"""

import json
import re

DATASET_PATH = "data/serum_gpt5_mistral_combined_897_hermes_training.jsonl"
REPORT_PATH = "data/semantic_validation_report_897.json"

def extract_params(text: str):
    """Extract parameters from ChatML text"""
    match = re.search(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except:
            return {}
    return {}

def extract_instruction(text: str):
    """Extract instruction from ChatML text"""
    match = re.search(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', text, re.DOTALL)
    return match.group(1).strip() if match else ""

def get_param_value(params, name):
    """Get parameter value by name"""
    for p in params.get('parameter_changes', []):
        if p.get('name') == name:
            return float(p.get('value', 0.0))
    return 0.0

# Load report to get problematic line numbers
with open(REPORT_PATH, 'r') as f:
    report = json.load(f)

problem_lines = set()
for issue in report['detailed_issues'].get('sound_type_violations', []):
    if issue.get('severity') == 'high':
        problem_lines.add(issue['line'])

print(f"🔍 Investigating {len(problem_lines)} presets with low oscillator levels\n")
print("="*80)

# Load dataset and analyze problem presets
examples = []
with open(DATASET_PATH, 'r') as f:
    for line_num, line in enumerate(f, 1):
        if line_num in problem_lines:
            entry = json.loads(line.strip())
            examples.append((line_num, entry))

# Analyze each problem preset
noise_based_valid = []
genuinely_broken = []
questionable = []

for line_num, entry in examples:
    text = entry['text']
    instruction = extract_instruction(text)
    params = extract_params(text)

    # Get key parameters
    osc_a = get_param_value(params, 'A Level')
    osc_b = get_param_value(params, 'B Level')
    noise = get_param_value(params, 'Noise Level')
    main_vol = get_param_value(params, 'Main Vol')

    combined_osc = max(osc_a, osc_b)

    # Categorize
    inst_lower = instruction.lower()

    # Check if noise-based is justified
    noise_keywords = ['noise', 'white', 'hiss', 'static', 'wind', 'air', 'breath', 'whoosh']
    has_noise_keyword = any(kw in inst_lower for kw in noise_keywords)

    if combined_osc < 0.1 and noise > 0.5 and has_noise_keyword:
        # Valid noise-based sound
        noise_based_valid.append({
            'line': line_num,
            'instruction': instruction,
            'osc_a': osc_a,
            'osc_b': osc_b,
            'noise': noise,
            'main_vol': main_vol
        })
    elif combined_osc < 0.01 and noise < 0.1:
        # Both oscillators AND noise are silent - broken
        genuinely_broken.append({
            'line': line_num,
            'instruction': instruction,
            'osc_a': osc_a,
            'osc_b': osc_b,
            'noise': noise,
            'main_vol': main_vol
        })
    else:
        # Questionable - low oscs but might be relying on effects
        questionable.append({
            'line': line_num,
            'instruction': instruction,
            'osc_a': osc_a,
            'osc_b': osc_b,
            'noise': noise,
            'main_vol': main_vol
        })

print(f"\n📊 ANALYSIS RESULTS")
print("="*80)
print(f"Valid Noise-Based Sounds:    {len(noise_based_valid)}")
print(f"Genuinely Broken:            {len(genuinely_broken)}")
print(f"Questionable/Ambiguous:      {len(questionable)}")
print()

# Show examples
if noise_based_valid:
    print("\n✅ VALID NOISE-BASED SOUNDS (Sample)")
    print("-"*80)
    for item in noise_based_valid[:5]:
        print(f"Line {item['line']}: {item['instruction']}")
        print(f"  Oscs: A={item['osc_a']:.3f} B={item['osc_b']:.3f} | Noise: {item['noise']:.3f}")
        print()

if genuinely_broken:
    print("\n❌ GENUINELY BROKEN PRESETS (All)")
    print("-"*80)
    for item in genuinely_broken:
        print(f"Line {item['line']}: {item['instruction']}")
        print(f"  Oscs: A={item['osc_a']:.3f} B={item['osc_b']:.3f} | Noise: {item['noise']:.3f} | Vol: {item['main_vol']:.3f}")
        print()

if questionable:
    print("\n⚠️  QUESTIONABLE PRESETS (Sample of first 10)")
    print("-"*80)
    for item in questionable[:10]:
        print(f"Line {item['line']}: {item['instruction']}")
        print(f"  Oscs: A={item['osc_a']:.3f} B={item['osc_b']:.3f} | Noise: {item['noise']:.3f}")
        print()

# Recommendations
print("\n" + "="*80)
print("💡 RECOMMENDATIONS")
print("="*80)
print(f"\n1. Keep {len(noise_based_valid)} noise-based presets - they're valid")
print(f"2. Remove {len(genuinely_broken)} broken presets - no sound source")
print(f"3. Review {len(questionable)} questionable presets - may need parameter adjustment")
print()

# Save lists for manual review
output = {
    'summary': {
        'total_problematic': len(problem_lines),
        'valid_noise_based': len(noise_based_valid),
        'genuinely_broken': len(genuinely_broken),
        'questionable': len(questionable)
    },
    'valid_noise_based': noise_based_valid,
    'genuinely_broken': genuinely_broken,
    'questionable': questionable
}

with open('data/low_osc_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print("📝 Detailed analysis saved to: data/low_osc_analysis.json\n")
