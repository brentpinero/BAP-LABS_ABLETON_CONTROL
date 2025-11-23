#!/usr/bin/env python3
"""
Format Serum training dataset for Hermes Mistral 7B training.
Converts our Q&A pairs to proper Hermes chat format.
"""

import json
from pathlib import Path
from typing import Dict, List
import re

def format_for_hermes(instruction: str, response: Dict) -> str:
    """
    Convert instruction + response to Hermes chat format.

    Hermes format:
    <|im_start|>system
    {system_message}
    <|im_end|>
    <|im_start|>user
    {user_message}
    <|im_end|>
    <|im_start|>assistant
    {assistant_response}
    <|im_end|>
    """

    # System message for Serum control
    system_message = """You are a Serum 2 synthesizer preset generator. You create parameter settings for the Serum 2 synthesizer based on musical descriptions.

Your responses must be valid JSON with this exact structure:
{
  "parameter_changes": [
    {"index": 1, "value": 0.75, "name": "Main Vol"},
    {"index": 22, "value": 0.5, "name": "A Level"}
  ],
  "critical_changes": ["Main Vol", "A Level"]
}

Guidelines:
- Use parameter indices 1-2623 (Serum 2 has 2623 parameters)
- All values must be between 0.0 and 1.0
- Include 15-20 parameter changes per preset
- Focus on parameters that create the described sound
- Always include critical_changes array with key parameter names"""

    # Format the response as JSON string
    response_json = json.dumps(response, indent=2)

    # Create Hermes format
    formatted = f"""<|im_start|>system
{system_message}
<|im_end|>
<|im_start|>user
{instruction}
<|im_end|>
<|im_start|>assistant
{response_json}
<|im_end|>"""

    return formatted

def clean_instruction(instruction: str) -> str:
    """Clean and normalize instruction text."""
    # Remove extra whitespace
    instruction = re.sub(r'\s+', ' ', instruction.strip())

    # Ensure it ends with proper punctuation
    if not instruction.endswith(('.', '!', '?', '...')):
        instruction += '.'

    return instruction

def validate_response(response: Dict) -> bool:
    """Validate that response has proper structure."""
    if not isinstance(response, dict):
        return False

    if 'parameter_changes' not in response:
        return False

    param_changes = response['parameter_changes']
    if not isinstance(param_changes, list) or len(param_changes) == 0:
        return False

    # Check each parameter change
    for param in param_changes:
        if not isinstance(param, dict):
            return False
        if 'index' not in param or 'value' not in param:
            return False
        if not isinstance(param['index'], (int, float)):
            return False
        if not isinstance(param['value'], (int, float)):
            return False
        if param['value'] < 0.0 or param['value'] > 1.0:
            return False

    return True

def format_dataset(input_file: str, output_file: str):
    """
    Convert Serum dataset to Hermes training format.
    """
    print("🎛️ FORMATTING DATASET FOR HERMES MISTRAL")
    print("=" * 50)

    # Load dataset
    with open(input_file, 'r') as f:
        data = json.load(f)

    examples = data.get('examples', [])
    print(f"Input examples: {len(examples)}")

    formatted_examples = []
    skipped = 0

    for i, example in enumerate(examples):
        # Validate structure
        if 'instruction' not in example or 'response' not in example:
            skipped += 1
            continue

        instruction = clean_instruction(example['instruction'])
        response = example['response']

        # Validate response
        if not validate_response(response):
            skipped += 1
            continue

        # Format for Hermes
        formatted_text = format_for_hermes(instruction, response)

        formatted_examples.append({
            "text": formatted_text,
            "metadata": {
                "original_index": i,
                "instruction_length": len(instruction),
                "param_count": len(response.get('parameter_changes', [])),
                "quality_score": example.get('quality_scores', {}).get('overall', 1.0)
            }
        })

        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1} examples...")

    print(f"\nFormatted examples: {len(formatted_examples)}")
    print(f"Skipped (invalid): {skipped}")

    # Create output dataset
    output_data = {
        "metadata": {
            "format": "hermes_chat",
            "model_target": "NousResearch/Nous-Hermes-2-Mistral-7B-DPO",
            "total_examples": len(formatted_examples),
            "source_file": input_file,
            "average_quality": sum(ex['metadata']['quality_score'] for ex in formatted_examples) / len(formatted_examples)
        },
        "examples": formatted_examples
    }

    # Save formatted dataset
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Formatted dataset saved to: {output_file}")

    # Show sample
    if formatted_examples:
        print("\n📄 SAMPLE FORMATTED EXAMPLE")
        print("-" * 40)
        sample = formatted_examples[0]['text']
        print(sample[:500] + "..." if len(sample) > 500 else sample)

    return output_data

def create_jsonl_for_training(input_file: str, output_file: str):
    """
    Create JSONL format for training (one example per line).
    """
    print("\n📝 Creating JSONL for training...")

    with open(input_file, 'r') as f:
        data = json.load(f)

    with open(output_file, 'w') as f:
        for example in data['examples']:
            # Create simple training format
            training_example = {
                "text": example['text']
            }
            f.write(json.dumps(training_example) + '\n')

    print(f"✅ JSONL saved to: {output_file}")

def main():
    # Check what datasets are available
    datasets_to_format = [
        "data/serum_gpt5_mistral_combined_898.json",
        "data/serum_gpt5_mistral_FINAL_combined.json"  # When batch2 is done
    ]

    for dataset_file in datasets_to_format:
        if Path(dataset_file).exists():
            print(f"\n🔍 Found dataset: {dataset_file}")

            # Format for Hermes
            base_name = Path(dataset_file).stem
            formatted_file = f"data/{base_name}_hermes_formatted.json"
            jsonl_file = f"data/{base_name}_hermes_training.jsonl"

            # Format dataset
            formatted_data = format_dataset(dataset_file, formatted_file)

            # Create JSONL for training
            create_jsonl_for_training(formatted_file, jsonl_file)

            print(f"\n📊 Dataset Stats:")
            print(f"  Examples: {len(formatted_data['examples'])}")
            print(f"  Avg quality: {formatted_data['metadata']['average_quality']:.3f}")
            print(f"  Ready for MLX training: {jsonl_file}")

        else:
            print(f"⚠️  Dataset not found: {dataset_file}")

    print(f"\n✅ Dataset formatting complete!")
    print("Next step: Run MLX LoRA training with the JSONL files")

if __name__ == "__main__":
    main()