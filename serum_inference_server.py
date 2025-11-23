#!/usr/bin/env python3
"""
FastAPI server for local Serum preset generation.
Optimized for M4 Max with 8-bit quantized model.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mlx_lm import load, generate
import mlx.core as mx
import json
import re
import time
import logging
from pathlib import Path
from typing import Optional, Dict, List
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Request/Response models
class GenerationRequest(BaseModel):
    instruction: str
    temperature: float = 0.7
    max_tokens: int = 300
    top_p: float = 0.9

class ParameterChange(BaseModel):
    index: int
    value: float
    name: str

class SerumPreset(BaseModel):
    parameter_changes: List[ParameterChange]
    critical_changes: List[str]

class GenerationResponse(BaseModel):
    preset: Optional[SerumPreset]
    raw_response: str
    generation_time: float
    token_count: int
    success: bool
    error: Optional[str] = None

class SerumInferenceServer:
    """Local inference server for Serum preset generation."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.load_model()

    def load_model(self):
        """Load the 8-bit quantized model."""
        logger.info(f"Loading model from: {self.model_path}")
        start_time = time.time()

        try:
            self.model, self.tokenizer = load(
                self.model_path,
                tokenizer_config={"trust_remote_code": True}
            )

            load_time = time.time() - start_time
            logger.info(f"✅ Model loaded in {load_time:.2f}s")

            # Warm up the model with a test generation
            self.warmup()

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def warmup(self):
        """Warm up the model for faster first inference."""
        logger.info("Warming up model...")

        warmup_prompt = """<|im_start|>system
You are a Serum 2 synthesizer preset generator.
<|im_end|>
<|im_start|>user
Create a simple bass sound.
<|im_end|>
<|im_start|>assistant
"""

        try:
            _ = generate(
                self.model,
                self.tokenizer,
                prompt=warmup_prompt,
                max_tokens=50,
                temp=0.7
            )
            logger.info("✅ Model warmed up")
        except Exception as e:
            logger.warning(f"Warmup failed: {e}")

    def format_prompt(self, instruction: str) -> str:
        """Format instruction for Hermes model."""
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

        return f"""<|im_start|>system
{system_message}
<|im_end|>
<|im_start|>user
{instruction}
<|im_end|>
<|im_start|>assistant
"""

    def parse_response(self, raw_response: str) -> Optional[SerumPreset]:
        """Extract and validate JSON from model response."""
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not json_match:
                return None

            json_str = json_match.group(0)

            # Clean up common issues
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)

            # Parse JSON
            preset_data = json.loads(json_str)

            # Validate structure
            if 'parameter_changes' not in preset_data:
                return None

            parameter_changes = []
            for param in preset_data['parameter_changes']:
                if all(key in param for key in ['index', 'value', 'name']):
                    # Validate ranges
                    if 1 <= param['index'] <= 2623 and 0.0 <= param['value'] <= 1.0:
                        parameter_changes.append(ParameterChange(**param))

            if not parameter_changes:
                return None

            critical_changes = preset_data.get('critical_changes', [])

            return SerumPreset(
                parameter_changes=parameter_changes,
                critical_changes=critical_changes
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse response: {e}")
            return None

    def generate_preset(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a Serum preset from an instruction."""
        start_time = time.time()

        try:
            # Format prompt
            prompt = self.format_prompt(request.instruction)

            # Generate response
            raw_response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=request.max_tokens,
                temp=request.temperature,
                top_p=request.top_p
            )

            generation_time = time.time() - start_time

            # Parse preset from response
            preset = self.parse_response(raw_response)

            # Count tokens
            token_count = len(self.tokenizer.encode(raw_response))

            # Log performance
            tokens_per_sec = token_count / generation_time
            logger.info(f"Generated preset: {tokens_per_sec:.1f} tok/s, {generation_time:.2f}s")

            return GenerationResponse(
                preset=preset,
                raw_response=raw_response,
                generation_time=generation_time,
                token_count=token_count,
                success=preset is not None
            )

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return GenerationResponse(
                preset=None,
                raw_response="",
                generation_time=time.time() - start_time,
                token_count=0,
                success=False,
                error=str(e)
            )

# Global server instance
server = None

# FastAPI app
app = FastAPI(
    title="Serum Preset Generator",
    description="Local API for generating Serum 2 presets using MLX",
    version="1.0.0"
)

# Enable CORS for Max for Live integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup."""
    global server
    model_path = app.state.model_path
    logger.info("Starting Serum Inference Server...")
    server = SerumInferenceServer(model_path)
    logger.info("🎛️ Server ready for Serum preset generation!")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model_loaded": server is not None}

@app.post("/generate", response_model=GenerationResponse)
async def generate_preset(request: GenerationRequest):
    """Generate a Serum preset from an instruction."""
    if server is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not request.instruction.strip():
        raise HTTPException(status_code=400, detail="Instruction cannot be empty")

    return server.generate_preset(request)

@app.get("/stats")
async def get_stats():
    """Get server statistics."""
    if server is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "model_path": server.model_path,
        "mlx_version": mx.__version__,
        "memory_usage": "Not implemented",  # Could add memory monitoring
        "uptime": "Not implemented"
    }

@app.post("/test")
async def test_generation():
    """Test endpoint with predefined examples."""
    if server is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    test_instruction = "Create a deep dubstep wobble bass for the drop"
    request = GenerationRequest(instruction=test_instruction)

    response = server.generate_preset(request)

    return {
        "test_instruction": test_instruction,
        "success": response.success,
        "generation_time": response.generation_time,
        "parameter_count": len(response.preset.parameter_changes) if response.preset else 0
    }

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Start Serum Inference Server")
    parser.add_argument("--model", required=True, help="Path to quantized model")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")

    args = parser.parse_args()

    # Validate model path
    if not Path(args.model).exists():
        logger.error(f"Model path does not exist: {args.model}")
        return

    # Store model path in app state
    app.state.model_path = args.model

    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"Model: {args.model}")

    # Start server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=args.workers,
        log_level="info"
    )

if __name__ == "__main__":
    main()