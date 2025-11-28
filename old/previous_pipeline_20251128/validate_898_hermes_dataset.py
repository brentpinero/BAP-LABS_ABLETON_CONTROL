#!/usr/bin/env python3
"""
Comprehensive validation of the 898 Hermes training dataset
Validates parameter indices, ranges, names, musical realism, and ChatML formatting
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import Counter, defaultdict
import difflib

# Load parameter mapping
PARAM_MAPPING_PATH = "data/serum2_parameter_mapping_final.json"
DATASET_PATH = "data/serum_gpt5_mistral_combined_898_hermes_training.jsonl"

class DatasetValidator:
    def __init__(self, param_mapping_path: str):
        # Load parameter reference data
        with open(param_mapping_path, 'r') as f:
            mapping_data = json.load(f)
            self.param_map = mapping_data['parameter_map']
            self.param_count = mapping_data['parameter_count']

        # Build reverse mapping (index -> name)
        self.index_to_name = {v: k for k, v in self.param_map.items()}

        # Valid parameter indices
        self.valid_indices = set(self.param_map.values())

        # Validation results
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        self.all_instructions = []
        self.all_parameter_names = Counter()

    def validate_dataset(self, dataset_path: str):
        """Main validation function"""
        print(f"🔍 Validating dataset: {dataset_path}\n")

        examples = []
        with open(dataset_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    examples.append((line_num, entry))
                except json.JSONDecodeError as e:
                    self.issues['json_parse_errors'].append({
                        'line': line_num,
                        'error': str(e)
                    })

        print(f"📊 Total examples loaded: {len(examples)}\n")

        # Validate each example
        for line_num, entry in examples:
            self.validate_example(line_num, entry)

        return self.generate_report()

    def validate_example(self, line_num: int, entry: Dict):
        """Validate a single training example"""

        # 1. Validate ChatML structure
        if 'text' not in entry:
            self.issues['missing_text_field'].append(line_num)
            return

        text = entry['text']
        self.validate_chatml_format(line_num, text)

        # 2. Extract components
        instruction, response = self.extract_instruction_and_response(text)

        if not instruction or not response:
            self.issues['extraction_failed'].append(line_num)
            return

        # 3. Validate instruction
        self.validate_instruction(line_num, instruction)

        # 4. Validate response JSON
        self.validate_response_json(line_num, response)

    def validate_chatml_format(self, line_num: int, text: str):
        """Validate ChatML formatting"""
        required_markers = [
            '<|im_start|>system',
            '<|im_end|>',
            '<|im_start|>user',
            '<|im_start|>assistant'
        ]

        for marker in required_markers:
            if marker not in text:
                self.issues['chatml_format_errors'].append({
                    'line': line_num,
                    'missing_marker': marker
                })

        # Check proper nesting
        if text.count('<|im_start|>') != text.count('<|im_end|>'):
            self.issues['chatml_unbalanced'].append(line_num)

    def extract_instruction_and_response(self, text: str) -> Tuple[str, str]:
        """Extract instruction and response from ChatML text"""
        # Extract user instruction
        user_match = re.search(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', text, re.DOTALL)
        instruction = user_match.group(1).strip() if user_match else ""

        # Extract assistant response
        assistant_match = re.search(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', text, re.DOTALL)
        response = assistant_match.group(1).strip() if assistant_match else ""

        return instruction, response

    def validate_instruction(self, line_num: int, instruction: str):
        """Validate musical instruction quality"""
        self.all_instructions.append(instruction)
        self.stats['total_instructions'] += 1

        # Check if empty
        if not instruction or len(instruction.strip()) == 0:
            self.issues['empty_instructions'].append(line_num)
            return

        # Check length (should be reasonable)
        if len(instruction) < 5:
            self.issues['too_short_instructions'].append({
                'line': line_num,
                'instruction': instruction
            })

        if len(instruction) > 500:
            self.issues['too_long_instructions'].append({
                'line': line_num,
                'length': len(instruction)
            })

        # Check for musical realism keywords
        musical_keywords = [
            'bass', 'lead', 'pad', 'pluck', 'arp', 'chord', 'sequence',
            'synth', 'sound', 'tone', 'wave', 'oscillator', 'filter',
            'edm', 'techno', 'house', 'trance', 'dubstep', 'dnb',
            'warm', 'bright', 'dark', 'harsh', 'soft', 'aggressive',
            'lush', 'rich', 'deep', 'fat', 'thin', 'wide', 'narrow'
        ]

        has_musical_context = any(keyword in instruction.lower() for keyword in musical_keywords)
        if has_musical_context:
            self.stats['musically_relevant'] += 1

    def validate_response_json(self, line_num: int, response: str):
        """Validate response JSON structure and parameters"""
        try:
            response_obj = json.loads(response)
        except json.JSONDecodeError as e:
            self.issues['invalid_response_json'].append({
                'line': line_num,
                'error': str(e),
                'response': response[:200]
            })
            return

        # Check required fields
        if 'parameter_changes' not in response_obj:
            self.issues['missing_parameter_changes'].append(line_num)
            return

        param_changes = response_obj['parameter_changes']

        if not isinstance(param_changes, list):
            self.issues['parameter_changes_not_array'].append(line_num)
            return

        # Validate each parameter
        for idx, param in enumerate(param_changes):
            self.validate_parameter(line_num, idx, param)

        # Check parameter count
        num_params = len(param_changes)
        if num_params < 10:
            self.issues['too_few_parameters'].append({
                'line': line_num,
                'count': num_params
            })
        elif num_params > 30:
            self.issues['too_many_parameters'].append({
                'line': line_num,
                'count': num_params
            })

        self.stats['total_parameter_changes'] += num_params

    def validate_parameter(self, line_num: int, param_idx: int, param: Dict):
        """Validate individual parameter"""
        # Check required fields
        required_fields = ['index', 'value', 'name']
        missing = [f for f in required_fields if f not in param]

        if missing:
            self.issues['parameter_missing_fields'].append({
                'line': line_num,
                'param_index': param_idx,
                'missing_fields': missing
            })
            return

        # Validate index
        param_index = param['index']
        if not isinstance(param_index, int):
            self.issues['invalid_index_type'].append({
                'line': line_num,
                'param_index': param_idx,
                'index': param_index
            })
        elif param_index not in self.valid_indices:
            self.issues['invalid_parameter_index'].append({
                'line': line_num,
                'param_index': param_idx,
                'index': param_index,
                'max_valid': max(self.valid_indices)
            })

        # Validate value range
        value = param['value']
        if not isinstance(value, (int, float)):
            self.issues['invalid_value_type'].append({
                'line': line_num,
                'param_index': param_idx,
                'value': value
            })
        elif not (0.0 <= value <= 1.0) and value not in [0, 1]:
            # Allow scientific notation near zero
            if not (value < 1e-30 and value >= 0):
                self.issues['value_out_of_range'].append({
                    'line': line_num,
                    'param_index': param_idx,
                    'name': param['name'],
                    'value': value
                })

        # Validate name
        param_name = param['name']
        self.all_parameter_names[param_name] += 1

        if param_name not in self.param_map:
            # Try to find close match
            close_matches = difflib.get_close_matches(param_name, self.param_map.keys(), n=1, cutoff=0.8)
            self.issues['invalid_parameter_name'].append({
                'line': line_num,
                'param_index': param_idx,
                'name': param_name,
                'suggestion': close_matches[0] if close_matches else None
            })
        else:
            # Check if name matches index
            expected_index = self.param_map[param_name]
            if expected_index != param_index:
                self.issues['name_index_mismatch'].append({
                    'line': line_num,
                    'param_index': param_idx,
                    'name': param_name,
                    'given_index': param_index,
                    'expected_index': expected_index
                })

    def check_for_duplicates(self):
        """Check for duplicate instructions"""
        instruction_counts = Counter(self.all_instructions)
        duplicates = {inst: count for inst, count in instruction_counts.items() if count > 1}

        if duplicates:
            self.issues['duplicate_instructions'] = [
                {'instruction': inst[:100], 'count': count}
                for inst, count in duplicates.items()
            ]
            self.stats['duplicate_count'] = len(duplicates)

    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        self.check_for_duplicates()

        # Calculate overall stats
        total_issues = sum(len(v) if isinstance(v, list) else 1 for v in self.issues.values())

        report = {
            'summary': {
                'total_examples': self.stats.get('total_instructions', 0),
                'total_issues': total_issues,
                'total_parameter_changes': self.stats.get('total_parameter_changes', 0),
                'musically_relevant': self.stats.get('musically_relevant', 0),
                'duplicate_instructions': self.stats.get('duplicate_count', 0)
            },
            'issues_by_category': {
                category: len(items) if isinstance(items, list) else 1
                for category, items in self.issues.items()
            },
            'detailed_issues': dict(self.issues),
            'parameter_usage': {
                'total_unique_parameters_used': len(self.all_parameter_names),
                'most_common_parameters': self.all_parameter_names.most_common(20),
                'valid_parameter_names_in_mapping': len(self.param_map)
            }
        }

        return report


def print_report(report: Dict):
    """Print validation report in readable format"""
    print("\n" + "="*80)
    print("📋 VALIDATION REPORT")
    print("="*80 + "\n")

    # Summary
    summary = report['summary']
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Total Examples:              {summary['total_examples']}")
    print(f"Total Issues Found:          {summary['total_issues']}")
    print(f"Total Parameter Changes:     {summary['total_parameter_changes']}")
    print(f"Musically Relevant:          {summary['musically_relevant']}")
    print(f"Duplicate Instructions:      {summary['duplicate_instructions']}")
    print()

    # Issues by category
    print("🚨 ISSUES BY CATEGORY")
    print("-" * 80)
    issues_by_cat = report['issues_by_category']
    if issues_by_cat:
        for category, count in sorted(issues_by_cat.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category:40s} {count:>6d}")
    else:
        print("  ✅ No issues found!")
    print()

    # Parameter usage
    param_usage = report['parameter_usage']
    print("🎛️  PARAMETER USAGE")
    print("-" * 80)
    print(f"Unique Parameters Used:      {param_usage['total_unique_parameters_used']}")
    print(f"Valid Parameters in Mapping: {param_usage['valid_parameter_names_in_mapping']}")
    print("\nMost Common Parameters:")
    for param_name, count in param_usage['most_common_parameters'][:10]:
        print(f"  {param_name:40s} {count:>6d}")
    print()

    # Quality assessment
    print("✅ QUALITY ASSESSMENT")
    print("-" * 80)
    total = summary['total_examples']
    issues = summary['total_issues']

    if issues == 0:
        quality = "EXCELLENT"
        status = "🏆"
    elif issues < total * 0.01:
        quality = "VERY GOOD"
        status = "🌟"
    elif issues < total * 0.05:
        quality = "GOOD"
        status = "👍"
    elif issues < total * 0.10:
        quality = "FAIR"
        status = "⚠️"
    else:
        quality = "NEEDS IMPROVEMENT"
        status = "❌"

    print(f"{status} Overall Quality: {quality}")
    print(f"   Issue Rate: {(issues/total*100):.2f}%")
    print()


if __name__ == "__main__":
    # Initialize validator
    validator = DatasetValidator(PARAM_MAPPING_PATH)

    # Run validation
    report = validator.validate_dataset(DATASET_PATH)

    # Print report
    print_report(report)

    # Save detailed report
    output_path = "data/validation_report_898_hermes.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"📝 Detailed report saved to: {output_path}\n")
