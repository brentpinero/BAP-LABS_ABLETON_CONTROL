#!/usr/bin/env python3

import json
import re

def clean_scientific_notation_value(value):
    """Convert scientific notation values < 1e-6 to 0.0"""
    if isinstance(value, (int, float)):
        if abs(value) < 1e-6:
            return 0.0
        return float(value)
    elif isinstance(value, str):
        try:
            float_val = float(value)
            if abs(float_val) < 1e-6:
                return 0.0
            return float_val
        except:
            return value
    return value

def clean_dataset(file_path):
    """Clean scientific notation in dataset"""
    print(f"🔧 Cleaning scientific notation in {file_path}...")

    with open(file_path, 'r') as f:
        data = json.load(f)

    cleaned_count = 0

    for example in data.get("examples", []):
        # Clean parameter_changes (supports both dict and array formats)
        if "response" in example and "parameter_changes" in example["response"]:
            params = example["response"]["parameter_changes"]

            # Handle dict format (old)
            if isinstance(params, dict):
                for key, value in params.items():
                    cleaned_val = clean_scientific_notation_value(value)
                    if cleaned_val != value:
                        params[key] = cleaned_val
                        cleaned_count += 1

            # Handle array format (new Max for Live compatible)
            elif isinstance(params, list):
                for param in params:
                    if "value" in param:
                        original_val = param["value"]
                        cleaned_val = clean_scientific_notation_value(original_val)
                        if cleaned_val != original_val:
                            param["value"] = cleaned_val
                            cleaned_count += 1

        # Clean critical_changes
        if "response" in example and "critical_changes" in example["response"]:
            critical = example["response"]["critical_changes"]
            for key, value in critical.items():
                cleaned_val = clean_scientific_notation_value(value)
                if cleaned_val != value:
                    critical[key] = cleaned_val
                    cleaned_count += 1

        # Clean mistral_template (replace scientific notation in JSON)
        if "mistral_template" in example:
            template = example["mistral_template"]
            # Find scientific notation pattern and replace with 0.0
            pattern = r':\s*[0-9]+\.[0-9]+e-[0-9]+'
            cleaned_template = re.sub(pattern, ':0.0', template)
            if cleaned_template != template:
                example["mistral_template"] = cleaned_template
                cleaned_count += 1

    # Clean API key in metadata
    if "metadata" in data and "generation_config" in data["metadata"]:
        if "openai_api_key" in data["metadata"]["generation_config"]:
            data["metadata"]["generation_config"]["openai_api_key"] = "[REDACTED]"

    # Save cleaned version
    output_path = file_path.replace('.json', '_CLEAN.json')
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Cleaned {cleaned_count} scientific notation values")
    print(f"💾 Saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        clean_dataset(sys.argv[1])
    else:
        clean_dataset("data/serum_gpt5_mistral_COMPLETE_dataset.json")