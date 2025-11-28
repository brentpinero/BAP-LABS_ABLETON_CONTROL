#!/usr/bin/env python3
"""
Complete pipeline for training and deploying Serum controller model.
Orchestrates the entire process from dataset to deployment.
"""

import subprocess
import sys
import time
import json
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SerumPipeline:
    """Orchestrates the complete Serum model pipeline."""

    def __init__(self, config: dict):
        self.config = config
        self.results = {}

    def check_prerequisites(self):
        """Check that all required files and dependencies exist."""
        logger.info("🔍 Checking prerequisites...")

        # Check dataset
        dataset_file = self.config['dataset_file']
        if not Path(dataset_file).exists():
            logger.error(f"Dataset not found: {dataset_file}")
            return False

        # Check Python packages
        required_packages = ['mlx', 'mlx-lm', 'fastapi', 'uvicorn']
        for package in required_packages:
            result = subprocess.run([sys.executable, '-c', f'import {package.replace("-", "_")}'],
                                  capture_output=True)
            if result.returncode != 0:
                logger.error(f"Missing package: {package}")
                return False

        logger.info("✅ All prerequisites met")
        return True

    def format_dataset(self):
        """Format dataset for Hermes training."""
        logger.info("📝 Formatting dataset for Hermes...")

        try:
            result = subprocess.run([
                sys.executable, 'format_dataset_for_hermes.py'
            ], capture_output=True, text=True, check=True)

            logger.info("✅ Dataset formatted successfully")
            self.results['dataset_formatted'] = True

            # Find the generated JSONL file
            jsonl_files = list(Path('data').glob('*hermes_training.jsonl'))
            if jsonl_files:
                self.results['training_file'] = str(jsonl_files[0])
                logger.info(f"Training file: {self.results['training_file']}")
            else:
                logger.error("No training JSONL file found")
                return False

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Dataset formatting failed: {e}")
            return False

    def run_training(self, test_mode=False):
        """Run LoRA training."""
        if not self.results.get('training_file'):
            logger.error("No training file available")
            return False

        logger.info("🚀 Starting LoRA training...")

        training_args = [
            sys.executable, 'mlx_lora_training.py',
            '--data', self.results['training_file'],
            '--output', self.config['training_output']
        ]

        if test_mode:
            training_args.append('--test-run')
            logger.info("Running in test mode (quick validation)")

        try:
            start_time = time.time()

            result = subprocess.run(training_args, capture_output=True, text=True, check=True)

            training_time = time.time() - start_time
            logger.info(f"✅ Training completed in {training_time/60:.1f} minutes")

            # Find the final model
            final_model_dir = Path(self.config['training_output']) / 'final_model'
            if final_model_dir.exists():
                self.results['lora_weights'] = str(final_model_dir / 'lora_weights.npz')
                logger.info(f"LoRA weights: {self.results['lora_weights']}")
            else:
                logger.error("Final model directory not found")
                return False

            self.results['training_time'] = training_time
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Training failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False

    def quantize_model(self):
        """Quantize the trained model to 8-bit."""
        if not self.results.get('lora_weights'):
            logger.error("No LoRA weights available for quantization")
            return False

        logger.info("🔧 Quantizing model to 8-bit...")

        quantize_args = [
            sys.executable, 'quantize_and_deploy.py',
            '--lora-weights', self.results['lora_weights'],
            '--output', self.config['quantized_output'],
            '--benchmark'
        ]

        try:
            result = subprocess.run(quantize_args, capture_output=True, text=True, check=True)

            logger.info("✅ Model quantized successfully")
            self.results['quantized_model'] = self.config['quantized_output']

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Quantization failed: {e}")
            return False

    def test_inference(self):
        """Test the quantized model."""
        if not self.results.get('quantized_model'):
            logger.error("No quantized model available")
            return False

        logger.info("🧪 Testing inference...")

        # Test basic model loading
        test_args = [
            sys.executable, 'quantize_and_deploy.py',
            '--lora-weights', self.results['lora_weights'],
            '--output', self.results['quantized_model'],
            '--test-generation'
        ]

        try:
            result = subprocess.run(test_args, capture_output=True, text=True, check=True)

            logger.info("✅ Inference test passed")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Inference test failed: {e}")
            return False

    def create_deployment_package(self):
        """Create a complete deployment package."""
        logger.info("📦 Creating deployment package...")

        deployment_dir = Path(self.config['deployment_dir'])
        deployment_dir.mkdir(parents=True, exist_ok=True)

        # Copy quantized model
        quantized_model_dir = Path(self.results['quantized_model'])
        if quantized_model_dir.exists():
            import shutil
            shutil.copytree(quantized_model_dir, deployment_dir / 'model', dirs_exist_ok=True)

        # Copy server script
        shutil.copy('serum_inference_server.py', deployment_dir / 'serum_server.py')

        # Create startup script
        startup_script = f"""#!/bin/bash
# Serum Controller Server Startup Script

echo "🎛️  Starting Serum Controller Server..."
echo "Model: {deployment_dir / 'model'}"
echo "Server will be available at: http://localhost:8000"
echo ""

# Start the server
python serum_server.py --model ./model --host 127.0.0.1 --port 8000

echo "Server stopped."
"""

        with open(deployment_dir / 'start_server.sh', 'w') as f:
            f.write(startup_script)

        # Make startup script executable
        (deployment_dir / 'start_server.sh').chmod(0o755)

        # Create deployment README
        readme_content = f"""# Serum Controller - Deployment Package

## Quick Start

1. **Start the server:**
   ```bash
   ./start_server.sh
   ```

2. **Test the API:**
   ```bash
   curl -X POST "http://localhost:8000/generate" \\
        -H "Content-Type: application/json" \\
        -d '{{"instruction": "Create a deep dubstep bass"}}'
   ```

## Integration with Max for Live

Use the HTTP endpoint in your Max for Live patch:

```javascript
// Max for Live code
function generate_preset(instruction) {{
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:8000/generate', false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({{instruction: instruction}}));

    if (xhr.status === 200) {{
        var response = JSON.parse(xhr.responseText);
        return response.preset;
    }}
    return null;
}}
```

## Model Info

- **Base Model**: NousResearch/Nous-Hermes-2-Mistral-7B-DPO
- **Training Examples**: {self.config.get('dataset_size', 'N/A')}
- **Quantization**: 8-bit (optimized for M4 Max)
- **Model Size**: ~7GB
- **Performance**: {self.results.get('inference_speed', 'N/A')} tokens/sec

## Training Stats

- **Training Time**: {self.results.get('training_time', 0) / 60:.1f} minutes
- **LoRA Rank**: 64
- **Target Platform**: M4 Max with 128GB RAM

## API Endpoints

- `GET /health` - Health check
- `POST /generate` - Generate Serum preset
- `GET /stats` - Server statistics
- `POST /test` - Test generation

## Troubleshooting

1. **Server won't start**: Check that port 8000 is available
2. **Slow generation**: Ensure no other heavy processes are running
3. **Invalid JSON**: Check the instruction format and try simpler prompts
4. **Memory issues**: Restart the server if memory usage grows too high

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(deployment_dir / 'README.md', 'w') as f:
            f.write(readme_content)

        logger.info(f"✅ Deployment package created: {deployment_dir}")
        return deployment_dir

    def run_complete_pipeline(self, test_mode=False):
        """Run the complete pipeline."""
        logger.info("🎛️ STARTING COMPLETE SERUM PIPELINE")
        logger.info("=" * 50)

        start_time = time.time()

        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False

        # Step 2: Format dataset
        if not self.format_dataset():
            return False

        # Step 3: Run training
        if not self.run_training(test_mode=test_mode):
            return False

        # Step 4: Quantize model
        if not self.quantize_model():
            return False

        # Step 5: Test inference
        if not self.test_inference():
            return False

        # Step 6: Create deployment package
        deployment_dir = self.create_deployment_package()

        total_time = time.time() - start_time

        logger.info("\n🎉 PIPELINE COMPLETE!")
        logger.info("=" * 50)
        logger.info(f"Total time: {total_time/60:.1f} minutes")
        logger.info(f"Deployment ready: {deployment_dir}")
        logger.info("\nNext steps:")
        logger.info(f"  cd {deployment_dir}")
        logger.info("  ./start_server.sh")
        logger.info("  # Integrate with Max for Live")

        return True

def main():
    parser = argparse.ArgumentParser(description="Run complete Serum pipeline")
    parser.add_argument("--dataset",
                       default="data/serum_gpt5_mistral_combined_898.json",
                       help="Input dataset file")
    parser.add_argument("--test-mode", action="store_true",
                       help="Run in test mode (faster, less training)")
    parser.add_argument("--output-dir", default="./serum_deployment",
                       help="Output directory for deployment")

    args = parser.parse_args()

    config = {
        "dataset_file": args.dataset,
        "training_output": "./lora_training_output",
        "quantized_output": "./quantized_model",
        "deployment_dir": args.output_dir,
        "test_mode": args.test_mode
    }

    # Create pipeline
    pipeline = SerumPipeline(config)

    # Run complete pipeline
    success = pipeline.run_complete_pipeline(test_mode=args.test_mode)

    if success:
        logger.info("🎛️ Ready to control Serum with AI!")
        sys.exit(0)
    else:
        logger.error("❌ Pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main()