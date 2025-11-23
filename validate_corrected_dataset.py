#!/usr/bin/env python3
"""
Semantic Preset Validator - Validates that parameter values match instruction descriptions

This validator uses synthesis knowledge to check if parameter settings make sense
for the described sound (e.g., bass sounds should have appropriate oscillator levels,
bright sounds should have higher harmonics, etc.)
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

DATASET_PATH = "data/serum_gpt5_mistral_897_CORRECTED_hermes_training.jsonl"

class SemanticPresetValidator:
    """
    Validates that preset parameters semantically match their descriptions
    using synthesis knowledge and heuristics
    """

    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)

        # Define semantic rules based on synthesis knowledge
        self.define_validation_rules()

    def define_validation_rules(self):
        """Define semantic validation rules based on synthesis principles"""

        # Sound type expectations
        self.sound_type_rules = {
            'bass': {
                'description': 'Bass sounds typically use low-frequency oscillators',
                'expectations': {
                    'osc_a_level_min': 0.1,  # At least one oscillator should be active
                    'osc_b_level_min': 0.0,  # Can use A or B or both
                    'combined_osc_min': 0.1,  # Total oscillator level should be substantial
                    'noise_level_max': 0.5,  # Bass shouldn't be mostly noise
                    'typical_coarse_pitch_range': (-1.0, 1.0)  # Usually not super high
                }
            },
            'lead': {
                'description': 'Lead sounds are typically bright and prominent',
                'expectations': {
                    'main_vol_min': 0.1,  # Should be audible
                    'combined_osc_min': 0.2,  # Clear oscillator presence
                    'noise_level_max': 0.7  # Leads can have some noise but not dominated
                }
            },
            'pad': {
                'description': 'Pads are typically smooth, sustained sounds',
                'expectations': {
                    'combined_osc_min': 0.1,  # Oscillators active
                    'noise_level_max': 0.8,  # Can be atmospheric
                    'main_vol_typical': (0.0, 0.8)  # Often softer
                }
            },
            'pluck': {
                'description': 'Plucks are short, percussive sounds',
                'expectations': {
                    'combined_osc_min': 0.1,
                    'noise_level_max': 0.7
                }
            },
            'arp': {
                'description': 'Arpeggiated sounds, often rhythmic',
                'expectations': {
                    'combined_osc_min': 0.1,
                    'lfo_usage_expected': True
                }
            },
            'riser': {
                'description': 'Risers build tension, often use noise and modulation',
                'expectations': {
                    'noise_level_min': 0.0,  # Can use noise or oscillators
                    'lfo_usage_expected': True  # Usually modulated
                }
            },
            'fx': {
                'description': 'FX sounds can be varied',
                'expectations': {
                    'noise_level_max': 1.0  # Very flexible
                }
            }
        }

        # Genre expectations
        self.genre_rules = {
            'dubstep': {
                'description': 'Dubstep typically features heavy bass and modulation',
                'common_sound_types': ['bass', 'wobble', 'growl'],
                'expectations': {
                    'lfo_usage_common': True,
                    'bass_focus': True
                }
            },
            'ambient': {
                'description': 'Ambient focuses on atmosphere and space',
                'common_sound_types': ['pad', 'drone', 'texture'],
                'expectations': {
                    'main_vol_typical': (0.0, 0.5),
                    'noise_acceptable': True
                }
            },
            'house': {
                'description': 'House music has clear, punchy sounds',
                'common_sound_types': ['bass', 'lead', 'stab'],
                'expectations': {
                    'main_vol_min': 0.1
                }
            }
        }

        # Descriptor expectations
        self.descriptor_rules = {
            'bright': {
                'description': 'Bright sounds have more high-frequency content',
                'expectations': {
                    'wt_pos_typical': (0.3, 1.0),  # Higher wavetable positions often brighter
                    'noise_level_max': 0.6  # Not too much low-freq noise
                }
            },
            'dark': {
                'description': 'Dark sounds emphasize lower frequencies',
                'expectations': {
                    'wt_pos_typical': (0.0, 0.5),  # Lower wavetable positions
                    'noise_level_acceptable': True
                }
            },
            'warm': {
                'description': 'Warm sounds have rich, smooth character',
                'expectations': {
                    'combined_osc_min': 0.2,
                    'noise_level_max': 0.5
                }
            },
            'aggressive': {
                'description': 'Aggressive sounds are harsh and in-your-face',
                'expectations': {
                    'main_vol_min': 0.1,
                    'combined_osc_min': 0.2
                }
            },
            'soft': {
                'description': 'Soft sounds are gentle and quiet',
                'expectations': {
                    'main_vol_typical': (0.0, 0.5),
                    'combined_osc_typical': (0.0, 0.7)
                }
            },
            'wide': {
                'description': 'Wide sounds use stereo width',
                'expectations': {
                    'unison_expected': True
                }
            }
        }

    def extract_instruction_and_params(self, text: str) -> Tuple[str, Dict]:
        """Extract instruction and parameters from ChatML text"""
        # Extract instruction
        user_match = re.search(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', text, re.DOTALL)
        instruction = user_match.group(1).strip() if user_match else ""

        # Extract response
        assistant_match = re.search(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', text, re.DOTALL)
        response_text = assistant_match.group(1).strip() if assistant_match else ""

        try:
            params = json.loads(response_text)
            return instruction, params
        except json.JSONDecodeError:
            return instruction, {}

    def get_parameter_value(self, params: Dict, param_name: str) -> float:
        """Get parameter value by name from parameter_changes array"""
        param_changes = params.get('parameter_changes', [])
        for p in param_changes:
            if p.get('name') == param_name:
                return float(p.get('value', 0.0))
        return 0.0

    def validate_sound_type(self, line_num: int, instruction: str, params: Dict, sound_type: str):
        """Validate that parameters match the sound type"""
        if sound_type not in self.sound_type_rules:
            return

        rules = self.sound_type_rules[sound_type]
        expectations = rules['expectations']

        # Get relevant parameter values
        main_vol = self.get_parameter_value(params, 'Main Vol')
        osc_a_level = self.get_parameter_value(params, 'A Level')
        osc_b_level = self.get_parameter_value(params, 'B Level')
        noise_level = self.get_parameter_value(params, 'Noise Level')
        lfo1_rate = self.get_parameter_value(params, 'LFO 1 Rate')
        lfo2_rate = self.get_parameter_value(params, 'LFO 2 Rate')

        combined_osc = max(osc_a_level, osc_b_level)

        # Check expectations
        if 'combined_osc_min' in expectations:
            if combined_osc < expectations['combined_osc_min']:
                self.issues['sound_type_violations'].append({
                    'line': line_num,
                    'instruction': instruction[:80],
                    'sound_type': sound_type,
                    'issue': f'Combined oscillator level too low ({combined_osc:.3f} < {expectations["combined_osc_min"]})',
                    'severity': 'high'
                })

        if 'noise_level_max' in expectations:
            if noise_level > expectations['noise_level_max']:
                # Only flag if noise is DOMINANT (close to 1.0) and oscillators are very quiet
                if noise_level > 0.8 and combined_osc < 0.1:
                    self.issues['sound_type_violations'].append({
                        'line': line_num,
                        'instruction': instruction[:80],
                        'sound_type': sound_type,
                        'issue': f'Noise level too high for {sound_type} ({noise_level:.3f}, oscs: {combined_osc:.3f})',
                        'severity': 'medium'
                    })

        if 'main_vol_min' in expectations:
            if main_vol < expectations['main_vol_min'] and main_vol != 0.0:
                self.issues['sound_type_violations'].append({
                    'line': line_num,
                    'instruction': instruction[:80],
                    'sound_type': sound_type,
                    'issue': f'Main volume unusually low ({main_vol:.3f})',
                    'severity': 'low'
                })

        if expectations.get('lfo_usage_expected'):
            if lfo1_rate == 0.0 and lfo2_rate == 0.0:
                self.issues['sound_type_suggestions'].append({
                    'line': line_num,
                    'instruction': instruction[:80],
                    'sound_type': sound_type,
                    'suggestion': f'{sound_type.capitalize()}s often use LFO modulation, but none detected',
                    'severity': 'info'
                })

    def validate_descriptor(self, line_num: int, instruction: str, params: Dict, descriptor: str):
        """Validate that parameters match descriptive terms"""
        if descriptor not in self.descriptor_rules:
            return

        rules = self.descriptor_rules[descriptor]
        expectations = rules['expectations']

        # Get relevant parameters
        osc_a_wt = self.get_parameter_value(params, 'A WT Pos')
        osc_b_wt = self.get_parameter_value(params, 'B WT Pos')
        main_vol = self.get_parameter_value(params, 'Main Vol')
        osc_a_level = self.get_parameter_value(params, 'A Level')
        osc_b_level = self.get_parameter_value(params, 'B Level')
        combined_osc = max(osc_a_level, osc_b_level)

        # Check expectations
        if 'main_vol_typical' in expectations:
            min_vol, max_vol = expectations['main_vol_typical']
            if not (min_vol <= main_vol <= max_vol) and main_vol != 0.0:
                self.issues['descriptor_mismatches'].append({
                    'line': line_num,
                    'instruction': instruction[:80],
                    'descriptor': descriptor,
                    'issue': f'Main volume {main_vol:.3f} unusual for "{descriptor}" sound (expected {min_vol}-{max_vol})',
                    'severity': 'low'
                })

        if 'combined_osc_min' in expectations:
            if combined_osc < expectations['combined_osc_min']:
                self.issues['descriptor_mismatches'].append({
                    'line': line_num,
                    'instruction': instruction[:80],
                    'descriptor': descriptor,
                    'issue': f'Oscillator levels too low ({combined_osc:.3f}) for "{descriptor}" sound',
                    'severity': 'medium'
                })

    def validate_example(self, line_num: int, entry: Dict):
        """Validate semantic consistency of a single example"""
        text = entry.get('text', '')
        instruction, params = self.extract_instruction_and_params(text)

        if not instruction or not params:
            return

        inst_lower = instruction.lower()

        # Detect sound types
        sound_types = ['bass', 'lead', 'pad', 'pluck', 'arp', 'riser', 'stab', 'fx', 'drone']
        for sound_type in sound_types:
            if sound_type in inst_lower:
                self.validate_sound_type(line_num, instruction, params, sound_type)
                self.stats[f'validated_{sound_type}'] += 1

        # Detect descriptors
        descriptors = ['bright', 'dark', 'warm', 'aggressive', 'soft', 'wide', 'thin', 'deep', 'lush']
        for descriptor in descriptors:
            if descriptor in inst_lower:
                self.validate_descriptor(line_num, instruction, params, descriptor)
                self.stats[f'validated_{descriptor}'] += 1

        self.stats['total_validated'] += 1

    def validate_dataset(self, dataset_path: str):
        """Validate entire dataset semantically"""
        print(f"🔍 Running Semantic Validation on: {dataset_path}\n")

        with open(dataset_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    self.validate_example(line_num, entry)
                except json.JSONDecodeError:
                    continue

        return self.generate_report()

    def generate_report(self) -> Dict:
        """Generate semantic validation report"""
        total_issues = sum(len(v) if isinstance(v, list) else 1 for v in self.issues.values())

        report = {
            'summary': {
                'total_examples_validated': self.stats.get('total_validated', 0),
                'total_semantic_issues': total_issues,
                'high_severity_issues': len([i for issues in self.issues.values() for i in issues if isinstance(i, dict) and i.get('severity') == 'high']),
                'medium_severity_issues': len([i for issues in self.issues.values() for i in issues if isinstance(i, dict) and i.get('severity') == 'medium']),
                'low_severity_issues': len([i for issues in self.issues.values() for i in issues if isinstance(i, dict) and i.get('severity') == 'low']),
            },
            'validation_stats': dict(self.stats),
            'issues_by_category': {
                category: len(items) if isinstance(items, list) else 1
                for category, items in self.issues.items()
            },
            'detailed_issues': dict(self.issues)
        }

        return report


def print_semantic_report(report: Dict):
    """Print semantic validation report"""
    print("\n" + "="*80)
    print("🧠 SEMANTIC VALIDATION REPORT")
    print("="*80 + "\n")

    summary = report['summary']
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Examples Validated:          {summary['total_examples_validated']}")
    print(f"Total Semantic Issues:       {summary['total_semantic_issues']}")
    print(f"  High Severity:             {summary['high_severity_issues']}")
    print(f"  Medium Severity:           {summary['medium_severity_issues']}")
    print(f"  Low Severity:              {summary['low_severity_issues']}")
    print()

    print("🔍 VALIDATION COVERAGE")
    print("-" * 80)
    stats = report['validation_stats']
    validated_types = {k: v for k, v in stats.items() if k.startswith('validated_')}
    for stat_name, count in sorted(validated_types.items(), key=lambda x: x[1], reverse=True):
        clean_name = stat_name.replace('validated_', '').title()
        print(f"  {clean_name:20s} {count:>4d} examples")
    print()

    if report['issues_by_category']:
        print("🚨 ISSUES BY CATEGORY")
        print("-" * 80)
        for category, count in sorted(report['issues_by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {category:40s} {count:>6d}")
        print()

        # Show sample issues
        print("📋 SAMPLE ISSUES (first 10)")
        print("-" * 80)
        issues_shown = 0
        for category, items in report['detailed_issues'].items():
            if issues_shown >= 10:
                break
            if isinstance(items, list) and items:
                for item in items[:min(3, len(items))]:
                    if issues_shown >= 10:
                        break
                    if isinstance(item, dict):
                        print(f"\n[{category}] Line {item.get('line', '?')}")
                        print(f"  Instruction: {item.get('instruction', item.get('descriptor', ''))}")
                        print(f"  Issue: {item.get('issue', item.get('suggestion', ''))}")
                        print(f"  Severity: {item.get('severity', 'N/A')}")
                        issues_shown += 1
        print()

    # Overall assessment
    print("✅ SEMANTIC QUALITY ASSESSMENT")
    print("-" * 80)
    total = summary['total_examples_validated']
    high_issues = summary['high_severity_issues']
    medium_issues = summary['medium_severity_issues']

    critical_rate = (high_issues / total * 100) if total > 0 else 0

    if critical_rate < 1.0:
        quality = "EXCELLENT - Descriptions match parameter settings"
        status = "🏆"
    elif critical_rate < 5.0:
        quality = "GOOD - Minor semantic inconsistencies"
        status = "👍"
    elif critical_rate < 10.0:
        quality = "FAIR - Some descriptions don't match settings"
        status = "⚠️"
    else:
        quality = "NEEDS REVIEW - Significant semantic mismatches"
        status = "❌"

    print(f"{status} Semantic Quality: {quality}")
    print(f"   Critical Issue Rate: {critical_rate:.2f}%")
    print()


if __name__ == "__main__":
    validator = SemanticPresetValidator()
    report = validator.validate_dataset(DATASET_PATH)
    print_semantic_report(report)

    # Save report
    output_path = "data/semantic_validation_report_897.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"📝 Detailed semantic report saved to: {output_path}\n")
