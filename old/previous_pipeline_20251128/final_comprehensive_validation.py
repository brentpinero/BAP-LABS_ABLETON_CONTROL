#!/usr/bin/env python3
"""
Final comprehensive validation of the corrected dataset
Runs all validation checks and generates final quality report
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

CORRECTED_DATASET = "data/serum_gpt5_mistral_897_CORRECTED_hermes_training.jsonl"
PARAM_MAPPING = "data/serum2_parameter_mapping_final.json"

class FinalValidator:
    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)

        # Load parameter mapping
        with open(PARAM_MAPPING, 'r') as f:
            mapping = json.load(f)
            self.param_map = mapping['parameter_map']
            self.valid_indices = set(self.param_map.values())

    def extract_instruction(self, text: str) -> str:
        match = re.search(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def extract_params(self, text: str) -> dict:
        match = re.search(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except:
                return {}
        return {}

    def validate_example(self, line_num: int, entry: dict):
        """Validate a single example"""
        self.stats['total_examples'] += 1

        text = entry.get('text', '')

        # 1. Check ChatML structure
        required_markers = ['<|im_start|>system', '<|im_start|>user', '<|im_start|>assistant', '<|im_end|>']
        for marker in required_markers:
            if marker not in text:
                self.issues['chatml_format'].append(line_num)
                return

        # 2. Extract and validate instruction
        instruction = self.extract_instruction(text)
        if not instruction:
            self.issues['missing_instruction'].append(line_num)
            return

        if len(instruction) < 5:
            self.issues['instruction_too_short'].append(line_num)

        self.stats['total_instructions'] += 1

        # 3. Extract and validate parameters
        params = self.extract_params(text)
        if not params or 'parameter_changes' not in params:
            self.issues['missing_parameters'].append(line_num)
            return

        param_changes = params['parameter_changes']

        # 4. Validate each parameter
        for idx, param in enumerate(param_changes):
            if not all(k in param for k in ['index', 'value', 'name']):
                self.issues['malformed_parameter'].append({
                    'line': line_num,
                    'param_index': idx
                })
                continue

            # Check index validity
            param_idx = param['index']
            if param_idx not in self.valid_indices:
                self.issues['invalid_param_index'].append({
                    'line': line_num,
                    'index': param_idx,
                    'name': param['name']
                })

            # Check value range
            value = param['value']
            if not isinstance(value, (int, float)):
                self.issues['invalid_value_type'].append({
                    'line': line_num,
                    'name': param['name'],
                    'value': value
                })
            elif not (0.0 <= value <= 1.0) and value not in [0, 1]:
                # Allow very small scientific notation
                if not (0 <= value < 1e-30):
                    self.issues['value_out_of_range'].append({
                        'line': line_num,
                        'name': param['name'],
                        'value': value
                    })

            # Check name validity
            if param['name'] not in self.param_map:
                self.issues['unknown_param_name'].append({
                    'line': line_num,
                    'name': param['name']
                })

        # 5. Check parameter count
        param_count = len(param_changes)
        if param_count != 19:
            self.issues['wrong_param_count'].append({
                'line': line_num,
                'count': param_count
            })

        self.stats['total_parameter_changes'] += param_count
        self.stats['valid_examples'] += 1

    def validate_dataset(self, dataset_path: str):
        """Validate entire dataset"""
        print(f"🔍 Final Comprehensive Validation")
        print(f"Dataset: {dataset_path}")
        print("="*80 + "\n")

        with open(dataset_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    self.validate_example(line_num, entry)
                except json.JSONDecodeError as e:
                    self.issues['json_parse_error'].append({
                        'line': line_num,
                        'error': str(e)
                    })

        return self.generate_report()

    def generate_report(self) -> dict:
        """Generate final validation report"""
        total_issues = sum(
            len(v) if isinstance(v, list) else 1
            for v in self.issues.values()
        )

        return {
            'summary': {
                'total_examples': self.stats['total_examples'],
                'valid_examples': self.stats['valid_examples'],
                'total_issues': total_issues,
                'total_parameter_changes': self.stats['total_parameter_changes'],
                'pass_rate': (self.stats['valid_examples'] / self.stats['total_examples'] * 100) if self.stats['total_examples'] > 0 else 0
            },
            'issues': dict(self.issues),
            'stats': dict(self.stats)
        }

def print_final_report(report: dict):
    """Print final validation report"""
    print("\n" + "="*80)
    print("📋 FINAL VALIDATION REPORT")
    print("="*80 + "\n")

    summary = report['summary']

    print("📊 DATASET STATISTICS")
    print("-"*80)
    print(f"Total Examples:           {summary['total_examples']}")
    print(f"Valid Examples:           {summary['valid_examples']}")
    print(f"Total Parameter Changes:  {summary['total_parameter_changes']}")
    print(f"Avg Params per Example:   {summary['total_parameter_changes']/summary['total_examples']:.1f}")
    print(f"Pass Rate:                {summary['pass_rate']:.2f}%")
    print()

    issues = report['issues']
    if issues:
        print("🚨 ISSUES FOUND")
        print("-"*80)
        for category, items in sorted(issues.items(), key=lambda x: len(x[1]) if isinstance(x[1], list) else 1, reverse=True):
            count = len(items) if isinstance(items, list) else 1
            print(f"  {category:40s} {count:>6d}")
        print()
    else:
        print("✅ NO ISSUES FOUND - DATASET IS PERFECT!")
        print()

    # Overall quality
    print("🏆 FINAL QUALITY ASSESSMENT")
    print("-"*80)

    total = summary['total_examples']
    issues_count = summary['total_issues']
    pass_rate = summary['pass_rate']

    if issues_count == 0:
        quality = "PERFECT"
        status = "🏆"
        recommendation = "Ready for production fine-tuning!"
    elif pass_rate >= 99.0:
        quality = "EXCELLENT"
        status = "🌟"
        recommendation = "Ready for production fine-tuning with minor review."
    elif pass_rate >= 95.0:
        quality = "VERY GOOD"
        status = "✅"
        recommendation = "Suitable for fine-tuning."
    elif pass_rate >= 90.0:
        quality = "GOOD"
        status = "👍"
        recommendation = "Suitable for fine-tuning with noted limitations."
    else:
        quality = "NEEDS WORK"
        status = "⚠️"
        recommendation = "Review and fix issues before fine-tuning."

    print(f"{status} Overall Quality: {quality}")
    print(f"   Pass Rate: {pass_rate:.2f}%")
    print(f"   Issue Count: {issues_count}")
    print(f"   Recommendation: {recommendation}")
    print()

    # Show key metrics
    print("📈 KEY METRICS")
    print("-"*80)
    format_ok = 'chatml_format' not in issues
    param_ok = 'invalid_param_index' not in issues
    value_ok = 'value_out_of_range' not in issues
    count_ok = 'wrong_param_count' not in issues

    print(f"✓ Format Compliance:      {'100%' if format_ok else 'Issues detected'}")
    print(f"✓ Parameter Validity:     {'100%' if param_ok else str(len(issues.get('invalid_param_index', []))) + ' issues'}")
    print(f"✓ Value Range Compliance: {'100%' if value_ok else str(len(issues.get('value_out_of_range', []))) + ' issues'}")
    print(f"✓ Consistency:            {'100%' if count_ok else str(len(issues.get('wrong_param_count', []))) + ' issues'}")
    print()

if __name__ == "__main__":
    validator = FinalValidator()
    report = validator.validate_dataset(CORRECTED_DATASET)
    print_final_report(report)

    # Save report
    output_path = "data/FINAL_validation_report.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"📝 Final validation report saved to: {output_path}\n")

    # Summary for user
    if report['summary']['total_issues'] == 0:
        print("="*80)
        print("🎉 VALIDATION COMPLETE - DATASET IS PRODUCTION READY!")
        print("="*80)
        print(f"\n✓ {report['summary']['total_examples']} examples validated")
        print(f"✓ {report['summary']['total_parameter_changes']} parameter changes verified")
        print(f"✓ 100% pass rate")
        print(f"\n🚀 Dataset ready for Hermes 2 Pro Mistral fine-tuning!\n")
    else:
        print("="*80)
        print("⚠️  VALIDATION COMPLETE - MINOR ISSUES DETECTED")
        print("="*80)
        print(f"\n✓ {report['summary']['valid_examples']}/{report['summary']['total_examples']} examples validated")
        print(f"⚠️  {report['summary']['total_issues']} issues found")
        print(f"\n📊 See detailed report for specifics.\n")
