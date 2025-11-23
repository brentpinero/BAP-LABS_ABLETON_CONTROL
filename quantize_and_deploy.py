#!/usr/bin/env python3
"""
Quantize the LoRA-trained model to 8-bit and set up for local deployment.
Optimized for M4 Max inference.
"""

import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load, lora, generate
import json
import numpy as np
from pathlib import Path
import time
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SerumModelQuantizer:
    """Handles quantization and deployment preparation."""

    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_trained_model(self, lora_weights_path: str):
        """Load base model and apply LoRA weights."""
        logger.info("Loading base model and LoRA weights...")

        # Load base model
        self.model, self.tokenizer = load(
            self.config['base_model'],
            tokenizer_config={"trust_remote_code": True}
        )

        # Apply LoRA weights
        if Path(lora_weights_path).exists():
            logger.info(f"Applying LoRA weights: {lora_weights_path}")
            self.model = lora.fuse_linear_layers(self.model, lora_weights_path)
        else:
            logger.warning(f"LoRA weights not found: {lora_weights_path}")
            logger.info("Using base model without LoRA")

        logger.info("✅ Model loaded successfully")

    def quantize_to_8bit(self):
        """Quantize model to 8-bit for efficient inference."""
        logger.info("Quantizing model to 8-bit...")

        start_time = time.time()

        # MLX quantization to 8-bit
        self.model = mx.quantize(
            self.model,
            bits=8,
            group_size=128  # Good balance for quality vs speed
        )

        quantize_time = time.time() - start_time
        logger.info(f"✅ Quantization complete in {quantize_time:.2f}s")

        # Calculate model size reduction
        original_size = sum(p.size * 4 for p in self.model.parameters())  # FP32 bytes
        quantized_size = sum(p.size for p in self.model.parameters())     # 8-bit bytes
        compression_ratio = original_size / quantized_size

        logger.info(f"Model size: {quantized_size / 1e9:.2f}GB (compressed {compression_ratio:.1f}x)")

    def save_quantized_model(self, output_path: str):
        """Save the 8-bit quantized model for deployment."""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving quantized model to: {output_dir}")

        # Save model weights
        mx.save_safetensors(str(output_dir / "model.safetensors"), dict(self.model.named_parameters()))

        # Save tokenizer
        self.tokenizer.save_pretrained(str(output_dir))

        # Save model config
        model_config = {
            "base_model": self.config['base_model'],
            "quantization": "8-bit",
            "group_size": 128,
            "optimized_for": "M4 Max",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "mlx_version": mx.__version__
        }

        with open(output_dir / "model_config.json", 'w') as f:
            json.dump(model_config, f, indent=2)

        # Create deployment README
        readme_content = f"""# Serum Controller - 8-bit Quantized Model

## Quick Start

```python
from mlx_lm import load
import mlx.core as mx

# Load 8-bit model
model, tokenizer = load("{output_dir.absolute()}")

# Generate Serum preset
prompt = "Create a deep dubstep bass with heavy distortion"
response = generate(model, tokenizer, prompt=prompt, max_tokens=200)
```

## Model Info
- **Base Model**: {self.config['base_model']}
- **Quantization**: 8-bit (optimized for M4 Max)
- **Model Size**: ~7GB
- **Expected Performance**: 50-80 tokens/sec on M4 Max
- **Memory Usage**: 8-10GB RAM

## Inference Tips
- Use batch_size=1 for single-user applications
- Enable Metal acceleration for best performance
- Temperature 0.7-0.9 works well for creative generation
- Max context: 4096 tokens

## Integration
This model outputs JSON in the format required by your Max for Live Serum controller.
"""

        with open(output_dir / "README.md", 'w') as f:
            f.write(readme_content)

        logger.info("✅ Quantized model saved successfully")
        return output_dir

    def benchmark_performance(self):
        """Benchmark inference performance on M4 Max."""
        logger.info("🏃‍♂️ Benchmarking inference performance...")

        test_prompts = [
            "Create a deep techno bass",
            "Make an ambient pad for film scoring",
            "Generate a punchy trap lead",
            "Design a rolling acid sequence",
            "Build a cinematic drum sound"
        ]

        total_tokens = 0
        total_time = 0

        for i, prompt in enumerate(test_prompts):
            # Format prompt for Hermes
            formatted_prompt = f"""<|im_start|>system
You are a Serum 2 synthesizer preset generator.
<|im_end|>
<|im_start|>user
{prompt}
<|im_end|>
<|im_start|>assistant
"""

            start_time = time.time()

            # Generate response
            response = generate(
                self.model,
                self.tokenizer,
                prompt=formatted_prompt,
                max_tokens=200,
                temp=0.7
            )

            generation_time = time.time() - start_time
            token_count = len(self.tokenizer.encode(response))

            total_tokens += token_count
            total_time += generation_time

            tokens_per_sec = token_count / generation_time
            logger.info(f"  Test {i+1}: {tokens_per_sec:.1f} tokens/sec ({token_count} tokens, {generation_time:.2f}s)")

        avg_tokens_per_sec = total_tokens / total_time
        logger.info(f"\n📊 Average Performance: {avg_tokens_per_sec:.1f} tokens/sec")
        logger.info(f"🎯 Target for M4 Max: 50-80 tokens/sec")

        if avg_tokens_per_sec >= 50:
            logger.info("✅ Performance meets target!")
        else:
            logger.info("⚠️  Performance below target - consider optimizations")

        return avg_tokens_per_sec

    def test_serum_generation(self):
        """Test generating actual Serum presets."""
        logger.info("🎛️ Testing Serum preset generation...")

        test_instructions = [
            "Deep dubstep wobble bass for the drop",
            "Cinematic ambient pad that slowly evolves",
            "Aggressive saw lead for EDM breakdown"
        ]

        for instruction in test_instructions:
            logger.info(f"\nTesting: '{instruction}'")

            # Format for Hermes
            prompt = f"""<|im_start|>system
You are a Serum 2 synthesizer preset generator. Create parameter settings as JSON.
<|im_end|>
<|im_start|>user
{instruction}
<|im_end|>
<|im_start|>assistant
"""

            try:
                response = generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=300,
                    temp=0.7
                )

                logger.info(f"Response: {response[:200]}...")

                # Try to parse JSON
                if "{" in response and "}" in response:
                    json_start = response.index("{")
                    json_end = response.rindex("}") + 1
                    json_str = response[json_start:json_end]

                    try:
                        preset_data = json.loads(json_str)
                        param_count = len(preset_data.get('parameter_changes', []))
                        logger.info(f"✅ Valid JSON with {param_count} parameters")
                    except json.JSONDecodeError:
                        logger.info("⚠️  Generated text but invalid JSON")
                else:
                    logger.info("❌ No JSON structure found")

            except Exception as e:
                logger.error(f"Error generating: {e}")

def main():
    parser = argparse.ArgumentParser(description="Quantize and deploy Serum model")
    parser.add_argument("--lora-weights", help="Path to LoRA weights")
    parser.add_argument("--output", default="./serum_8bit_model", help="Output directory")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmark")
    parser.add_argument("--test-generation", action="store_true", help="Test preset generation")

    args = parser.parse_args()

    config = {
        "base_model": "NousResearch/Nous-Hermes-2-Mistral-7B-DPO",
        "target_bits": 8,
        "optimization_target": "M4_Max"
    }

    # Initialize quantizer
    quantizer = SerumModelQuantizer(config)

    # Load model (with or without LoRA)
    if args.lora_weights:
        quantizer.load_trained_model(args.lora_weights)
    else:
        logger.info("No LoRA weights specified, using base model")
        quantizer.model, quantizer.tokenizer = load(
            config['base_model'],
            tokenizer_config={"trust_remote_code": True}
        )

    # Quantize to 8-bit
    quantizer.quantize_to_8bit()

    # Save quantized model
    output_path = quantizer.save_quantized_model(args.output)

    # Optional benchmarking
    if args.benchmark:
        quantizer.benchmark_performance()

    # Optional generation testing
    if args.test_generation:
        quantizer.test_serum_generation()

    logger.info(f"\n🎉 Deployment ready! Model saved to: {output_path}")
    logger.info("Next steps:")
    logger.info(f"  1. Test with: python test_inference.py --model {output_path}")
    logger.info("  2. Start server: python serum_server.py")
    logger.info("  3. Integrate with Max for Live")

if __name__ == "__main__":
    main()