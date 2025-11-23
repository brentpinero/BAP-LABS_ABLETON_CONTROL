#!/usr/bin/env python3
"""
Validates Serum training data against Max for Live plugin format.
Ensures LLM will output parameter changes that actually work with the plugin.
"""

import json
import sys
from typing import Dict, List, Set

# Serum 2 specs from Max for Live controller
SERUM2_PARAM_COUNT = 2623
VALID_PARAM_RANGE = (0.0, 1.0)

def validate_training_data(filepath: str) -> Dict:
    """Validate training data format and values."""

    print("🔍 VALIDATING SERUM TRAINING DATA")
    print("=" * 50)

    with open(filepath, 'r') as f:
        data = json.load(f)

    results = {
        'total_examples': len(data.get('examples', [])),
        'valid_examples': 0,
        'errors': [],
        'warnings': [],
        'stats': {
            'param_indices_used': set(),
            'min_params_per_example': float('inf'),
            'max_params_per_example': 0,
            'avg_params_per_example': 0,
            'out_of_range_values': 0,
            'invalid_indices': 0,
            'missing_fields': 0
        }
    }

    total_params = 0

    for i, example in enumerate(data.get('examples', [])):
        example_valid = True

        # Check required fields
        if 'instruction' not in example:
            results['errors'].append(f"Example {i}: Missing 'instruction' field")
            results['stats']['missing_fields'] += 1
            example_valid = False

        if 'response' not in example:
            results['errors'].append(f"Example {i}: Missing 'response' field")
            results['stats']['missing_fields'] += 1
            example_valid = False
            continue

        response = example['response']

        if 'parameter_changes' not in response:
            results['errors'].append(f"Example {i}: Missing 'parameter_changes' in response")
            results['stats']['missing_fields'] += 1
            example_valid = False
            continue

        param_changes = response['parameter_changes']
        param_count = len(param_changes)
        total_params += param_count

        # Track stats
        results['stats']['min_params_per_example'] = min(
            results['stats']['min_params_per_example'],
            param_count
        )
        results['stats']['max_params_per_example'] = max(
            results['stats']['max_params_per_example'],
            param_count
        )

        # Validate each parameter change
        for j, param in enumerate(param_changes):
            # Check required fields
            if 'index' not in param:
                results['errors'].append(
                    f"Example {i}, Param {j}: Missing 'index' field"
                )
                example_valid = False
                continue

            if 'value' not in param:
                results['errors'].append(
                    f"Example {i}, Param {j}: Missing 'value' field"
                )
                example_valid = False
                continue

            # Validate index (1-indexed in Max, but checking bounds)
            index = param['index']
            if not isinstance(index, (int, float)):
                results['errors'].append(
                    f"Example {i}, Param {j}: Index must be a number, got {type(index)}"
                )
                example_valid = False
            elif index < 1 or index > SERUM2_PARAM_COUNT:
                results['errors'].append(
                    f"Example {i}, Param {j}: Index {index} out of range (1-{SERUM2_PARAM_COUNT})"
                )
                results['stats']['invalid_indices'] += 1
                example_valid = False
            else:
                results['stats']['param_indices_used'].add(index)

            # Validate value (must be 0.0-1.0 for VST~ plugin)
            value = param['value']
            if not isinstance(value, (int, float)):
                results['errors'].append(
                    f"Example {i}, Param {j}: Value must be a number, got {type(value)}"
                )
                example_valid = False
            elif value < VALID_PARAM_RANGE[0] or value > VALID_PARAM_RANGE[1]:
                results['warnings'].append(
                    f"Example {i}, Param {j}: Value {value} outside typical range {VALID_PARAM_RANGE} "
                    f"(index={index}, name={param.get('name', 'unknown')})"
                )
                results['stats']['out_of_range_values'] += 1
                # Don't mark as invalid - some params might use extended ranges

            # Check if 'name' field exists (helpful but not required)
            if 'name' not in param:
                results['warnings'].append(
                    f"Example {i}, Param {j}: Missing 'name' field (helpful for debugging)"
                )

        if example_valid:
            results['valid_examples'] += 1

    # Calculate averages
    if results['total_examples'] > 0:
        results['stats']['avg_params_per_example'] = (
            total_params / results['total_examples']
        )

    return results

def print_validation_results(results: Dict):
    """Print formatted validation results."""

    print("\n📊 VALIDATION RESULTS")
    print("=" * 50)
    print(f"Total Examples: {results['total_examples']}")
    print(f"Valid Examples: {results['valid_examples']}")
    print(f"Invalid Examples: {results['total_examples'] - results['valid_examples']}")

    print("\n📈 STATISTICS")
    print("=" * 50)
    stats = results['stats']
    print(f"Unique Parameter Indices Used: {len(stats['param_indices_used'])}")
    print(f"Min Params per Example: {stats['min_params_per_example']}")
    print(f"Max Params per Example: {stats['max_params_per_example']}")
    print(f"Avg Params per Example: {stats['avg_params_per_example']:.2f}")
    print(f"Out-of-Range Values: {stats['out_of_range_values']}")
    print(f"Invalid Indices: {stats['invalid_indices']}")
    print(f"Missing Required Fields: {stats['missing_fields']}")

    if results['errors']:
        print("\n❌ ERRORS (first 10)")
        print("=" * 50)
        for error in results['errors'][:10]:
            print(f"  • {error}")
        if len(results['errors']) > 10:
            print(f"  ... and {len(results['errors']) - 10} more errors")

    if results['warnings']:
        print("\n⚠️  WARNINGS (first 10)")
        print("=" * 50)
        for warning in results['warnings'][:10]:
            print(f"  • {warning}")
        if len(results['warnings']) > 10:
            print(f"  ... and {len(results['warnings']) - 10} more warnings")

    # Final verdict
    print("\n🎯 VERDICT")
    print("=" * 50)
    if results['total_examples'] == results['valid_examples'] and not results['errors']:
        print("✅ ALL EXAMPLES VALID! Ready for training.")
    elif results['valid_examples'] > 0 and len(results['errors']) < results['total_examples'] * 0.05:
        print("⚠️  MOSTLY VALID (< 5% errors). Review errors before training.")
    else:
        print("❌ SIGNIFICANT ISSUES FOUND. Fix errors before training!")

    return results['total_examples'] == results['valid_examples']

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_training_data.py <path_to_json>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        results = validate_training_data(filepath)
        is_valid = print_validation_results(results)
        sys.exit(0 if is_valid else 1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()