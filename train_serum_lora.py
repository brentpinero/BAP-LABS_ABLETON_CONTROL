#!/usr/bin/env python3
"""
MLX-LM optimized LoRA training for Serum Control
Uses mlx-lm's built-in utilities for Hermes 2 Pro Mistral fine-tuning
"""

import json
import argparse
from pathlib import Path
import subprocess
import sys

def prepare_training_data(input_jsonl: str, output_dir: str):
    """Convert JSONL to MLX-LM format"""
    print(f"📝 Preparing training data from {input_jsonl}...")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # MLX-LM expects train.jsonl and optionally valid.jsonl
    train_file = output_path / "train.jsonl"
    valid_file = output_path / "valid.jsonl"

    # Load all examples
    examples = []
    with open(input_jsonl, 'r') as f:
        for line in f:
            examples.append(json.loads(line.strip()))

    total = len(examples)
    print(f"   Total examples: {total}")

    # Split 90/10 train/valid
    split_idx = int(total * 0.9)
    train_examples = examples[:split_idx]
    valid_examples = examples[split_idx:]

    print(f"   Train: {len(train_examples)}")
    print(f"   Valid: {len(valid_examples)}")

    # Write train file
    with open(train_file, 'w') as f:
        for example in train_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    # Write valid file
    with open(valid_file, 'w') as f:
        for example in valid_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"✅ Training data prepared in {output_dir}")
    return train_file, valid_file


def create_lora_config(output_dir: str, test_mode: bool = False):
    """Create LoRA configuration for MLX-LM"""

    if test_mode:
        config = {
            "num_iters": 50,  # Very short for testing
            "batch_size": 2,
            "learning_rate": 3e-4,
            "lora_layers": 8,  # Fewer layers for test
            "lora_rank": 32,
            "lora_alpha": 64,
            "lora_dropout": 0.1,
            "val_batches": 5,
            "save_every": 25,
            "eval_every": 25,
            "test_batches": 10
        }
    else:
        # Production config optimized for M4 Max with 897 examples
        config = {
            # Training iterations (897 * 0.9 = 807 train examples)
            # At batch_size=8: 807/8 = ~101 steps per epoch
            # For 3 epochs: 303 steps total
            "num_iters": 300,

            # Batch size - balance speed and memory (M4 Max can handle more)
            "batch_size": 8,

            # Learning rate - standard for LoRA fine-tuning
            "learning_rate": 3e-4,

            # LoRA configuration for quality
            "lora_layers": 16,      # All attention + MLP layers
            "lora_rank": 64,        # Higher rank for better quality
            "lora_alpha": 128,      # 2x rank (scaling factor)
            "lora_dropout": 0.1,    # Prevent overfitting

            # Validation and checkpointing
            "val_batches": 10,      # Validate on 10 batches
            "save_every": 50,       # Save checkpoint every 50 steps
            "eval_every": 25,       # Evaluate every 25 steps
            "test_batches": 25,     # Final test on 25 batches

            # Additional optimizations
            "grad_checkpoint": False,  # M4 has enough memory
            "seed": 42
        }

    config_path = Path(output_dir) / "lora_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ LoRA config created: {config_path}")
    print(f"   Config: {json.dumps(config, indent=2)}")

    return config_path


def run_mlx_lora_training(
    model_name: str,
    data_dir: str,
    output_dir: str,
    config_path: str
):
    """Run MLX-LM LoRA training using command-line interface"""

    print(f"\n🚀 Starting MLX-LM LoRA Fine-tuning")
    print(f"   Model: {model_name}")
    print(f"   Data: {data_dir}")
    print(f"   Output: {output_dir}")
    print("="*80)

    # Build MLX-LM command
    cmd = [
        "python", "-m", "mlx_lm.lora",
        "--model", model_name,
        "--train",
        "--data", data_dir,
        "--adapter-path", output_dir,
        "--config", str(config_path),
        "--iters", "300",  # Will be overridden by config
    ]

    print(f"\n🔧 Command: {' '.join(cmd)}\n")

    # Run training
    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        print(result.stdout)
        print("\n✅ Training completed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Training failed with error:")
        print(e.output)
        sys.exit(1)


def test_trained_model(model_name: str, adapter_path: str):
    """Quick test of the trained model"""
    print(f"\n🧪 Testing trained model...")

    test_prompts = [
        "Create a deep dubstep bass for the drop",
        "Make a bright future bass lead",
        "Ambient pad for cinematic backgrounds"
    ]

    print(f"Test prompts:")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"  {i}. {prompt}")

    # Test using MLX-LM generate
    cmd = [
        "python", "-m", "mlx_lm.generate",
        "--model", model_name,
        "--adapter-path", adapter_path,
        "--prompt", test_prompts[0],
        "--max-tokens", 500,
        "--temp", "0.7"
    ]

    print(f"\n🔧 Running: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("="*80)
        print("GENERATION TEST:")
        print("="*80)
        print(result.stdout)
        print("="*80)

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Test generation failed: {e}")
        print(e.stderr)


def main():
    parser = argparse.ArgumentParser(description="Train Serum LoRA with MLX-LM")
    parser.add_argument(
        "--data",
        default="data/serum_gpt5_mistral_897_CORRECTED_hermes_training.jsonl",
        help="Input JSONL training file"
    )
    parser.add_argument(
        "--model",
        default="NousResearch/Hermes-2-Pro-Mistral-7B",
        help="Base model to fine-tune"
    )
    parser.add_argument(
        "--output",
        default="./serum_lora_adapters",
        help="Output directory for LoRA adapters"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run quick test with minimal iterations"
    )

    args = parser.parse_args()

    print("="*80)
    print("🎯 SERUM LORA FINE-TUNING")
    print("="*80)
    print(f"Input data: {args.data}")
    print(f"Base model: {args.model}")
    print(f"Output dir: {args.output}")
    print(f"Test mode:  {args.test}")
    print("="*80 + "\n")

    # Step 1: Prepare data
    data_dir = Path(args.output) / "training_data"
    train_file, valid_file = prepare_training_data(args.data, str(data_dir))

    # Step 2: Create config
    config_path = create_lora_config(args.output, test_mode=args.test)

    # Step 3: Run training
    adapter_output = Path(args.output) / "adapters"
    run_mlx_lora_training(
        model_name=args.model,
        data_dir=str(data_dir),
        output_dir=str(adapter_output),
        config_path=config_path
    )

    # Step 4: Test the model
    if not args.test:
        test_trained_model(args.model, str(adapter_output))

    print("\n" + "="*80)
    print("🎉 TRAINING COMPLETE!")
    print("="*80)
    print(f"\n✅ LoRA adapters saved to: {adapter_output}")
    print(f"\n📝 Usage:")
    print(f"   python -m mlx_lm.generate \\")
    print(f"     --model {args.model} \\")
    print(f"     --adapter-path {adapter_output} \\")
    print(f"     --prompt 'Create a dubstep bass'")
    print()


if __name__ == "__main__":
    main()
