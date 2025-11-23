#!/usr/bin/env python3
"""
MLX LoRA training script optimized for M4 Max with 128GB RAM.
Trains Hermes Mistral 7B on Serum control data for 8-bit local deployment.
"""

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx_lm import load, lora
from mlx_lm.tuner import train
import json
import numpy as np
from pathlib import Path
import time
from typing import Dict, List, Tuple
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SerumMLXTrainer:
    """MLX-optimized trainer for Serum control model."""

    def __init__(self, config: Dict):
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Load Hermes Mistral model for LoRA training."""
        logger.info(f"Loading model: {self.config['model_name']}")
        start_time = time.time()

        # Load model and tokenizer with MLX
        self.model, self.tokenizer = load(
            self.config['model_name'],
            tokenizer_config={"trust_remote_code": True}
        )

        load_time = time.time() - start_time
        logger.info(f"✅ Model loaded in {load_time:.2f}s")

        # Get model size info
        num_params = sum(p.size for p in self.model.parameters() if p.dtype == mx.float16)
        logger.info(f"Model parameters: {num_params:,} ({num_params * 2 / 1e9:.2f}GB in FP16)")

    def setup_lora(self):
        """Configure LoRA for efficient fine-tuning."""
        logger.info("Setting up LoRA configuration...")

        # LoRA config optimized for M4 Max
        lora_config = {
            "rank": self.config['lora_rank'],
            "alpha": self.config['lora_alpha'],
            "dropout": self.config['lora_dropout'],
            "target_modules": [
                "self_attn.q_proj",
                "self_attn.k_proj",
                "self_attn.v_proj",
                "self_attn.o_proj",
                "mlp.gate_proj",
                "mlp.up_proj",
                "mlp.down_proj"
            ]
        }

        # Apply LoRA to model
        self.model = lora.LoRA(
            self.model,
            rank=lora_config["rank"],
            scale=lora_config["alpha"] / lora_config["rank"],
            dropout=lora_config["dropout"]
        )

        # Count trainable parameters
        trainable_params = sum(p.size for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.size for p in self.model.parameters())

        logger.info(f"LoRA applied:")
        logger.info(f"  Trainable params: {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")
        logger.info(f"  Memory for LoRA: ~{trainable_params * 4 / 1e6:.1f}MB")

    def load_dataset(self, jsonl_file: str) -> List[str]:
        """Load training data from JSONL file."""
        logger.info(f"Loading dataset: {jsonl_file}")

        examples = []
        with open(jsonl_file, 'r') as f:
            for line in f:
                data = json.loads(line.strip())
                examples.append(data['text'])

        logger.info(f"Loaded {len(examples)} training examples")

        # With 128GB RAM, we can keep everything in memory
        logger.info("Keeping entire dataset in memory (128GB advantage)")

        return examples

    def tokenize_dataset(self, examples: List[str]) -> Tuple[mx.array, mx.array]:
        """Tokenize the dataset for training."""
        logger.info("Tokenizing dataset...")

        # Tokenize all examples
        tokenized = []
        max_length = self.config['max_seq_length']

        for i, text in enumerate(examples):
            # Tokenize with proper attention mask
            tokens = self.tokenizer.encode(text, add_special_tokens=True)

            # Truncate if too long
            if len(tokens) > max_length:
                tokens = tokens[:max_length]

            tokenized.append(tokens)

            if (i + 1) % 100 == 0:
                logger.info(f"  Tokenized {i + 1}/{len(examples)} examples")

        # Pad to same length for efficient batching
        max_len = min(max_length, max(len(t) for t in tokenized))

        input_ids = []
        attention_masks = []

        for tokens in tokenized:
            # Pad sequence
            padded = tokens + [self.tokenizer.pad_token_id] * (max_len - len(tokens))
            mask = [1] * len(tokens) + [0] * (max_len - len(tokens))

            input_ids.append(padded)
            attention_masks.append(mask)

        # Convert to MLX arrays
        input_ids = mx.array(input_ids, dtype=mx.int32)
        attention_masks = mx.array(attention_masks, dtype=mx.int32)

        logger.info(f"Tokenization complete: {input_ids.shape}")
        return input_ids, attention_masks

    def train(self, jsonl_file: str):
        """Run the training loop."""
        logger.info("🚀 Starting LoRA training...")

        # Load and tokenize data
        examples = self.load_dataset(jsonl_file)
        input_ids, attention_masks = self.tokenize_dataset(examples)

        # Set up optimizer (AdamW with warm-up)
        optimizer = optim.AdamW(
            learning_rate=self.config['learning_rate'],
            betas=(0.9, 0.999),
            eps=1e-8,
            weight_decay=self.config['weight_decay']
        )

        # Training parameters
        batch_size = self.config['batch_size']
        num_epochs = self.config['num_epochs']
        save_interval = self.config['save_interval']

        total_steps = (len(examples) // batch_size) * num_epochs
        warmup_steps = min(100, total_steps // 10)

        logger.info(f"Training config:")
        logger.info(f"  Batch size: {batch_size}")
        logger.info(f"  Epochs: {num_epochs}")
        logger.info(f"  Total steps: {total_steps}")
        logger.info(f"  Warmup steps: {warmup_steps}")

        # Training loop
        start_time = time.time()
        global_step = 0

        for epoch in range(num_epochs):
            logger.info(f"\nEpoch {epoch + 1}/{num_epochs}")
            epoch_loss = 0

            # Shuffle data each epoch
            perm = mx.random.permutation(len(examples))
            input_ids = input_ids[perm]
            attention_masks = attention_masks[perm]

            for step in range(0, len(examples), batch_size):
                global_step += 1

                # Get batch
                end_step = min(step + batch_size, len(examples))
                batch_input_ids = input_ids[step:end_step]
                batch_attention_masks = attention_masks[step:end_step]

                # Forward pass with gradient computation
                def loss_fn():
                    logits = self.model(batch_input_ids)
                    # Causal LM loss (predict next token)
                    targets = batch_input_ids[:, 1:]  # Shift labels
                    logits = logits[:, :-1]  # Shift logits

                    return nn.losses.cross_entropy(
                        logits.reshape(-1, logits.shape[-1]),
                        targets.reshape(-1),
                        reduction='mean'
                    )

                # Compute gradients and update
                loss, grads = mx.value_and_grad(loss_fn)()
                optimizer.update(self.model, grads)
                mx.eval(self.model.parameters(), optimizer.state)

                epoch_loss += loss.item()

                # Learning rate warmup
                if global_step <= warmup_steps:
                    lr = self.config['learning_rate'] * (global_step / warmup_steps)
                    optimizer.learning_rate = lr

                # Logging
                if global_step % 10 == 0:
                    lr = optimizer.learning_rate.item() if hasattr(optimizer.learning_rate, 'item') else optimizer.learning_rate
                    logger.info(f"  Step {global_step}: loss={loss.item():.4f}, lr={lr:.2e}")

                # Save checkpoint
                if global_step % save_interval == 0:
                    self.save_checkpoint(global_step)

            avg_loss = epoch_loss / (len(examples) // batch_size)
            logger.info(f"Epoch {epoch + 1} complete: avg_loss={avg_loss:.4f}")

        total_time = time.time() - start_time
        logger.info(f"\n✅ Training complete in {total_time/60:.1f} minutes")

        # Save final model
        self.save_final_model()

    def save_checkpoint(self, step: int):
        """Save training checkpoint."""
        checkpoint_dir = Path(self.config['output_dir']) / f"checkpoint-{step}"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Save LoRA weights
        lora.save_weights(str(checkpoint_dir / "lora_weights.npz"), self.model)

        # Save config
        with open(checkpoint_dir / "config.json", 'w') as f:
            json.dump(self.config, f, indent=2)

        logger.info(f"Checkpoint saved: {checkpoint_dir}")

    def save_final_model(self):
        """Save the final trained model."""
        output_dir = Path(self.config['output_dir']) / "final_model"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save LoRA weights
        lora.save_weights(str(output_dir / "lora_weights.npz"), self.model)

        # Save training config
        with open(output_dir / "training_config.json", 'w') as f:
            json.dump(self.config, f, indent=2)

        # Save README with usage instructions
        readme_content = f"""# Serum Controller Model - LoRA Weights

Trained on {self.config.get('dataset_size', 'N/A')} examples.

## Usage

```python
from mlx_lm import load, lora

# Load base model
model, tokenizer = load("{self.config['model_name']}")

# Apply LoRA weights
model = lora.apply_lora_weights(model, "lora_weights.npz")

# Generate Serum preset
response = generate(model, tokenizer, prompt="Create a deep dubstep bass")
```

## Model Info
- Base: {self.config['model_name']}
- LoRA Rank: {self.config['lora_rank']}
- Training Examples: {self.config.get('dataset_size', 'N/A')}
- Quantization: Ready for 8-bit deployment
"""

        with open(output_dir / "README.md", 'w') as f:
            f.write(readme_content)

        logger.info(f"✅ Final model saved: {output_dir}")
        return output_dir

def main():
    parser = argparse.ArgumentParser(description="Train Serum controller with MLX LoRA")
    parser.add_argument("--data", required=True, help="Training JSONL file")
    parser.add_argument("--output", default="./serum_lora_output", help="Output directory")
    parser.add_argument("--test-run", action="store_true", help="Quick test with 10 examples")

    args = parser.parse_args()

    # M4 Max optimized config
    config = {
        "model_name": "NousResearch/Nous-Hermes-2-Mistral-7B-DPO",

        # LoRA settings for quality + efficiency
        "lora_rank": 64,
        "lora_alpha": 128,
        "lora_dropout": 0.1,

        # Training settings optimized for M4 Max 128GB
        "batch_size": 16,           # Large batch with 128GB RAM
        "learning_rate": 3e-4,      # Aggressive for LoRA
        "num_epochs": 3,
        "weight_decay": 0.01,
        "max_seq_length": 2048,     # Enough for our use case

        # Checkpointing
        "save_interval": 50,
        "output_dir": args.output,

        # Dataset info
        "dataset_file": args.data
    }

    if args.test_run:
        logger.info("🧪 Running test mode (10 examples, 1 epoch)")
        config.update({
            "num_epochs": 1,
            "save_interval": 5,
            "batch_size": 2
        })

    # Initialize trainer
    trainer = SerumMLXTrainer(config)

    # Load model and setup LoRA
    trainer.load_model()
    trainer.setup_lora()

    # Start training
    trainer.train(args.data)

if __name__ == "__main__":
    main()