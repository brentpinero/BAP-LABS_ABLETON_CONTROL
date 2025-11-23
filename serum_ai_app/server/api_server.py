#!/usr/bin/env python3
"""
Serum AI API Server
Lightweight Flask server that loads the model once and serves predictions
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from mlx_lm import load, generate
import json
import os
import sys
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Global model variables (loaded once at startup)
model = None
tokenizer = None

# System prompt from training (WITHOUT parameter count restriction)
SYSTEM_PROMPT = """<|im_start|>system
You are a Serum 2 synthesizer preset generator. You create parameter settings for the Serum 2 synthesizer based on musical descriptions.

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
- Focus on parameters that create the described sound
- Always include critical_changes array with key parameter names
<|im_end|>"""

def load_model():
    """Load model and adapters once at startup"""
    global model, tokenizer

    print("🔧 Loading Serum AI model...")

    # Determine paths based on whether we're bundled or running in dev
    if getattr(sys, 'frozen', False):
        # Running as bundled app
        bundle_dir = Path(sys._MEIPASS)
        adapter_path = bundle_dir / "adapters"
    else:
        # Running in development
        adapter_path = Path(__file__).parent.parent.parent / "serum_lora_adapters" / "conservative_adapters"

    model, tokenizer = load(
        "NousResearch/Hermes-2-Pro-Mistral-7B",
        adapter_path=str(adapter_path)
    )

    print("✅ Model loaded and ready!")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    })

@app.route('/generate', methods=['POST'])
def generate_preset():
    """
    Generate Serum preset from natural language description

    Request body:
    {
        "description": "Deep dubstep bass with lots of wobble"
    }

    Response:
    {
        "parameter_changes": [...],
        "critical_changes": [...]
    }
    """
    try:
        data = request.get_json()
        print(f"[Server] Received data: {data}", flush=True)
        description = data.get('description', '')
        print(f"[Server] Description: '{description}'", flush=True)

        if not description:
            print("[Server] ERROR: No description provided", flush=True)
            return jsonify({"error": "No description provided"}), 400

        # Build prompt
        prompt = f"{SYSTEM_PROMPT}\n<|im_start|>user\n{description}\n<|im_end|>\n<|im_start|>assistant\n"
        print(f"[Server] Starting generation...", flush=True)

        # Generate response
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=2048,
            verbose=False
        )
        print(f"[Server] Generation complete. Response length: {len(response)}", flush=True)

        # Parse JSON response
        try:
            preset_data = json.loads(response)
            print(f"[Server] Successfully parsed JSON", flush=True)
            return jsonify(preset_data)
        except json.JSONDecodeError as e:
            print(f"[Server] JSON parsing failed: {e}", flush=True)
            print(f"[Server] Raw response: {response[:500]}", flush=True)
            return jsonify({
                "error": "Failed to parse model output as JSON",
                "raw_response": response[:500]
            }), 500

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR in /generate: {error_details}", flush=True)
        sys.stdout.flush()
        sys.stderr.flush()
        return jsonify({"error": str(e), "details": error_details}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown the server gracefully"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return jsonify({"message": "Server shutting down..."})

if __name__ == '__main__':
    # Load model before starting server
    load_model()

    # Start server
    port = int(os.environ.get('PORT', 8080))
    print(f"\n🚀 Serum AI Server running on http://localhost:{port}")
    print("   Ready to generate presets!")

    app.run(
        host='127.0.0.1',
        port=port,
        debug=False,
        threaded=True
    )
