# M4 Max 8-Bit Quantized Local Deployment Strategy

## Optimized for Local Inference
- **Model Size**: ~7GB (8-bit) vs 14GB (FP16)
- **Inference Speed**: 2-3x faster than FP16
- **Quality Loss**: <1% with proper quantization
- **RAM Usage**: ~10GB total (model + context)

## Best Quantization Approaches for M4 Max

### 1. MLX with 8-bit Quantization (RECOMMENDED)
```python
# MLX native quantization - optimized for Apple Silicon
import mlx.core as mx
from mlx_lm import load, convert

# Load and quantize to 8-bit
model, tokenizer = load(
    "NousResearch/Nous-Hermes-2-Mistral-7B-DPO",
    tokenizer_config={"trust_remote_code": True}
)

# Quantize to 8-bit (W8A16 - weights 8-bit, activations 16-bit)
quantized_model = mx.quantize(model, bits=8)
```

### 2. llama.cpp with Q8_0 (FASTEST)
```bash
# Convert to GGUF and quantize
python convert.py model --outtype q8_0

# Run with full Metal acceleration
./main -m model-q8_0.gguf \
  -ngl 999 \
  --ctx-size 4096 \
  --batch-size 512 \
  --threads 8
```

### 3. bitsandbytes 8-bit (PyTorch)
```python
# Load in 8-bit with bitsandbytes
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained(
    "NousResearch/Nous-Hermes-2-Mistral-7B-DPO",
    load_in_8bit=True,
    device_map="auto",
    torch_dtype=torch.float16
)
```

## Training Strategy for 8-bit Deployment

### QLoRA Training (Train in 4-bit, Deploy in 8-bit)
```python
training_config = {
    # Train with 4-bit base model + LoRA
    "load_in_4bit": True,
    "bnb_4bit_compute_dtype": "bfloat16",
    "bnb_4bit_quant_type": "nf4",

    # LoRA config optimized for quality
    "lora_r": 64,              # Higher rank for better quality
    "lora_alpha": 128,
    "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    "lora_dropout": 0.1,

    # Training params for M4 Max
    "per_device_train_batch_size": 16,  # Big batch with 128GB
    "gradient_accumulation_steps": 1,
    "learning_rate": 3e-4,
    "num_train_epochs": 3,
    "max_seq_length": 2048,
    "fp16": False,
    "bf16": True,  # Better for M4 Max
}
```

### Post-Training Quantization Flow
```python
# 1. Merge LoRA weights with base model
merged_model = merge_lora_weights(base_model, lora_weights)

# 2. Quantize to 8-bit for deployment
quantized_model = quantize_to_8bit(merged_model)

# 3. Save in optimized format
save_for_mlx(quantized_model, "serum_controller_8bit")
```

## Memory & Performance Targets

### 8-bit Model Stats
- **Model Size**: 6.7GB (vs 13.5GB FP16)
- **RAM Usage**: 8-10GB during inference
- **Token Generation**: 50-80 tokens/sec on M4 Max
- **First Token Latency**: <500ms
- **Context Window**: 4096 tokens (uses ~2GB)

### Optimization Settings for M4 Max
```python
inference_config = {
    "max_memory": "20GB",      # Conservative for background running
    "num_threads": 8,           # Half of performance cores
    "metal_acceleration": True,
    "batch_size": 1,           # Single user local inference
    "use_cache": True,
    "temperature": 0.7,
    "top_p": 0.9,
    "repetition_penalty": 1.1,
}
```

## Local Deployment Architecture

### 1. Model Server (FastAPI + MLX)
```python
from fastapi import FastAPI
import mlx.core as mx
from mlx_lm import generate

app = FastAPI()

# Load 8-bit quantized model once
model, tokenizer = load_8bit_model("serum_controller_8bit")

@app.post("/generate")
async def generate_preset(instruction: str):
    # Fast 8-bit inference
    response = generate(
        model, tokenizer,
        prompt=format_instruction(instruction),
        max_tokens=500,
        temp=0.7
    )
    return parse_serum_params(response)
```

### 2. Integration with Max for Live
```javascript
// Max for Live calls local model server
function query_local_llm(instruction) {
    const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        body: JSON.stringify({instruction: instruction})
    });
    return response.json();
}
```

## Quantization Quality Preservation

### Critical for Serum Control
1. **Preserve parameter precision**: Use symmetric quantization
2. **Calibration dataset**: Use actual Serum presets for calibration
3. **Mixed precision**: Keep critical layers in FP16
4. **Test thoroughly**: Validate parameter ranges stay 0.0-1.0

### Quantization Comparison
| Method | Size | Speed | Quality | M4 Compatibility |
|--------|------|-------|---------|------------------|
| FP16 | 14GB | 1x | 100% | Excellent |
| 8-bit | 7GB | 2x | 99.5% | Excellent |
| 4-bit | 3.5GB | 3x | 98% | Good |
| 3-bit | 2.6GB | 4x | 95% | Experimental |

## Recommended Setup for Production

```bash
# 1. Install MLX
pip install mlx mlx-lm

# 2. Download and quantize model
python quantize_for_m4.py \
  --model "NousResearch/Nous-Hermes-2-Mistral-7B-DPO" \
  --lora_weights "./serum_lora_weights" \
  --quantization "8bit" \
  --output "./models/serum_8bit"

# 3. Run local server
python serum_server.py --model "./models/serum_8bit" --port 8000

# 4. Test inference speed
python benchmark.py --model "./models/serum_8bit" --samples 100
```

## Performance Benchmarks (Expected on M4 Max)

### 8-bit Quantized Model
- **Load Time**: 2-3 seconds
- **First Token**: 400ms
- **Tokens/sec**: 60-80
- **RAM Usage**: 8-10GB
- **Power Draw**: 40-60W
- **Temperature**: 75-85°C under load

### Optimization Tips
1. **Use MLX** for best Apple Silicon performance
2. **Keep model in memory** between requests
3. **Batch similar requests** when possible
4. **Use KV cache** for multi-turn conversations
5. **Profile with Instruments** to find bottlenecks