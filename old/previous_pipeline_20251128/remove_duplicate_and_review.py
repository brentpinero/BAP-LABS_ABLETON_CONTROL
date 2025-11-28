#!/usr/bin/env python3
"""
Remove duplicate instruction and perform qualitative review
"""

import json
import random
from pathlib import Path
from collections import defaultdict

DATASET_PATH = "data/serum_gpt5_mistral_combined_898_hermes_training.jsonl"
OUTPUT_PATH = "data/serum_gpt5_mistral_combined_897_hermes_training.jsonl"
DUPLICATE_INSTRUCTION = "Gnarly dubstep growl for the drop."

def remove_duplicate(input_path: str, output_path: str, duplicate_text: str):
    """Remove one instance of duplicate instruction"""

    examples = []
    duplicate_found = False

    with open(input_path, 'r') as f:
        for line in f:
            entry = json.loads(line.strip())

            # Extract instruction
            text = entry['text']
            if duplicate_text in text and not duplicate_found:
                print(f"🗑️  Removing duplicate: {duplicate_text}")
                duplicate_found = True
                continue  # Skip this one

            examples.append(entry)

    # Write cleaned dataset
    with open(output_path, 'w') as f:
        for entry in examples:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"\n✅ Cleaned dataset saved: {output_path}")
    print(f"   Original: 898 examples")
    print(f"   Cleaned:  {len(examples)} examples\n")

    return examples

def extract_instruction(text: str) -> str:
    """Extract instruction from ChatML text"""
    import re
    match = re.search(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', text, re.DOTALL)
    return match.group(1).strip() if match else ""

def qualitative_review(examples: list, num_samples: int = 20):
    """Perform qualitative review of random samples"""

    print("="*80)
    print("🔍 QUALITATIVE REVIEW - Random Sample Analysis")
    print("="*80 + "\n")

    # Random sample
    random.seed(42)  # Reproducible
    sample = random.sample(examples, min(num_samples, len(examples)))

    # Categorize by instruction type
    categories = defaultdict(list)

    genre_keywords = ['edm', 'house', 'techno', 'trance', 'dubstep', 'dnb', 'drum and bass', 'ambient', 'synthwave', 'trap', 'breaks']
    sound_types = ['bass', 'lead', 'pad', 'pluck', 'arp', 'chord', 'stab', 'hit', 'fx', 'riser', 'drone']
    descriptors = ['warm', 'bright', 'dark', 'harsh', 'soft', 'lush', 'rich', 'deep', 'fat', 'thin', 'wide', 'aggressive', 'smooth']

    for idx, entry in enumerate(sample, 1):
        instruction = extract_instruction(entry['text'])

        print(f"Sample #{idx}")
        print(f"Instruction: {instruction}")

        # Categorize
        inst_lower = instruction.lower()

        detected_genre = [g for g in genre_keywords if g in inst_lower]
        detected_sound = [s for s in sound_types if s in inst_lower]
        detected_desc = [d for d in descriptors if d in inst_lower]

        print(f"  Genres:      {', '.join(detected_genre) if detected_genre else 'None'}")
        print(f"  Sound Types: {', '.join(detected_sound) if detected_sound else 'None'}")
        print(f"  Descriptors: {', '.join(detected_desc) if detected_desc else 'None'}")

        # Parse response
        import re
        response_match = re.search(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', entry['text'], re.DOTALL)
        if response_match:
            try:
                response = json.loads(response_match.group(1).strip())
                param_count = len(response.get('parameter_changes', []))
                print(f"  Parameters:  {param_count} changes")

                # Show a few key parameters
                params = response.get('parameter_changes', [])
                key_params = [p for p in params if p['name'] in ['Main Vol', 'A Level', 'B Level']]
                for p in key_params:
                    print(f"    - {p['name']}: {p['value']:.4f}")

            except json.JSONDecodeError:
                print(f"  Parameters:  [JSON parse error]")

        print()

    # Overall statistics
    print("\n" + "="*80)
    print("📊 OVERALL QUALITATIVE ASSESSMENT")
    print("="*80 + "\n")

    all_instructions = [extract_instruction(e['text']) for e in examples]

    # Count by length
    lengths = [len(inst) for inst in all_instructions]
    avg_length = sum(lengths) / len(lengths)

    print(f"Instruction Length Statistics:")
    print(f"  Average:  {avg_length:.1f} characters")
    print(f"  Min:      {min(lengths)} characters")
    print(f"  Max:      {max(lengths)} characters")
    print()

    # Count genres represented
    genre_counts = defaultdict(int)
    sound_counts = defaultdict(int)
    desc_counts = defaultdict(int)

    for inst in all_instructions:
        inst_lower = inst.lower()
        for genre in genre_keywords:
            if genre in inst_lower:
                genre_counts[genre] += 1
        for sound in sound_types:
            if sound in inst_lower:
                sound_counts[sound] += 1
        for desc in descriptors:
            if desc in inst_lower:
                desc_counts[desc] += 1

    print("Top Genres Represented:")
    for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {genre:15s} {count:>4d} examples ({count/len(all_instructions)*100:.1f}%)")

    print("\nTop Sound Types:")
    for sound, count in sorted(sound_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {sound:15s} {count:>4d} examples ({count/len(all_instructions)*100:.1f}%)")

    print("\nTop Descriptors:")
    for desc, count in sorted(desc_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {desc:15s} {count:>4d} examples ({count/len(all_instructions)*100:.1f}%)")

    print("\n" + "="*80)
    print("✅ QUALITATIVE REVIEW COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    # Remove duplicate
    examples = remove_duplicate(DATASET_PATH, OUTPUT_PATH, DUPLICATE_INSTRUCTION)

    # Perform qualitative review
    qualitative_review(examples, num_samples=20)
