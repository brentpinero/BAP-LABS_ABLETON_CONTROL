#!/usr/bin/env python3

import json
import sys

def validate_dataset(file_path):
    """Validate generated dataset quality"""

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False

    print(f"\n🔍 DATASET VALIDATION REPORT")
    print("=" * 60)

    # Basic stats
    examples = data.get("examples", [])
    metadata = data.get("metadata", {})

    print(f"\n📊 BASIC STATS:")
    print(f"  Total examples: {len(examples)}")
    print(f"  Presets processed: {metadata.get('presets_processed', 'N/A')}")
    print(f"  Average quality: {metadata.get('average_quality', 'N/A'):.3f}")
    print(f"  Quality threshold: {metadata.get('quality_threshold', 'N/A')}")

    if not examples:
        print("\n⚠️  No examples found in dataset")
        return False

    # Instruction diversity
    instructions = [ex['instruction'] for ex in examples]
    unique_instructions = len(set(instructions))
    diversity_pct = (unique_instructions / len(instructions)) * 100

    print(f"\n🎯 DIVERSITY METRICS:")
    print(f"  Unique instructions: {unique_instructions}/{len(instructions)} ({diversity_pct:.1f}%)")

    # Instruction length stats
    lengths = [len(inst) for inst in instructions]
    avg_length = sum(lengths) / len(lengths)
    min_length = min(lengths)
    max_length = max(lengths)

    print(f"\n📏 INSTRUCTION LENGTH:")
    print(f"  Average: {avg_length:.0f} chars")
    print(f"  Min: {min_length} chars")
    print(f"  Max: {max_length} chars")

    # Parameter coverage
    all_params = set()
    for ex in examples:
        params = ex.get('response', {}).get('parameter_changes', {})
        all_params.update(params.keys())

    print(f"\n🎛️  PARAMETER COVERAGE:")
    print(f"  Unique parameters used: {len(all_params)}/2623")
    print(f"  Coverage: {(len(all_params)/2623)*100:.1f}%")

    # Sample instructions
    print(f"\n📝 SAMPLE INSTRUCTIONS (first 5):")
    for i, inst in enumerate(instructions[:5], 1):
        preview = inst[:80] + "..." if len(inst) > 80 else inst
        print(f"  {i}. {preview}")

    # Quality scores
    qualities = [ex.get('quality_scores', {}).get('overall', 0) for ex in examples]
    if qualities:
        avg_quality = sum(qualities) / len(qualities)
        print(f"\n⭐ QUALITY SCORES:")
        print(f"  Average overall: {avg_quality:.3f}")
        print(f"  Min: {min(qualities):.3f}")
        print(f"  Max: {max(qualities):.3f}")

    # Check for scientific notation
    sci_notation_count = 0
    for ex in examples:
        params = ex.get('response', {}).get('parameter_changes', {})
        for val in params.values():
            if isinstance(val, (int, float)) and abs(val) < 1e-6 and val != 0:
                sci_notation_count += 1
                break

    if sci_notation_count > 0:
        print(f"\n⚠️  Found {sci_notation_count} examples with scientific notation values")
    else:
        print(f"\n✅ No scientific notation issues detected")

    # Mistral template validation
    template_count = sum(1 for ex in examples if 'mistral_template' in ex)
    print(f"\n📋 MISTRAL TEMPLATES:")
    print(f"  Examples with templates: {template_count}/{len(examples)}")

    print(f"\n" + "=" * 60)
    print(f"✅ Validation complete!")

    return True

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "data/serum_gpt5_mistral_LARGE_dataset.json"
    validate_dataset(file_path)