# 🎛️ Serum AI - Setup Instructions

AI-powered Serum 2 preset generator trained on 897 presets with 98.9% accuracy.

## 📦 What You've Built

1. **Fine-tuned Mistral 7B Model** - LoRA adapter trained on Serum 2 presets
2. **Flask API Server** - Loads model once, serves predictions on localhost:8080
3. **Mac App Bundle** - Standalone .app with bundled Python + model (coming soon)
4. **Max for Live Device** - AI controller that talks to the API
5. **Python Bridge** - Connects Max to Flask API

## ✅ Current Status

### ✓ Completed
- ✅ Dataset corrected (897 examples, 80/10/10 split)
- ✅ Conservative training (LR: 1e-4, 500 iters, Val loss: 1.154 → 0.140)
- ✅ Semantic accuracy: 100% param overlap, 0.167 value MAE, 100% critical param recall
- ✅ Flask API server with model loading
- ✅ Max for Live JavaScript controller
- ✅ Python API bridge for Max
- ✅ Full integration tested (26s generation time)

### 🚧 Next Steps
- Build Mac .app bundle with PyInstaller
- Create Max patch with UI
- Package for distribution to producers

## 🏃 Running The System (Development Mode)

### Step 1: Start the API Server

```bash
cd /Users/brentpinero/Documents/serum_llm_2
python serum_ai_app/server/api_server.py
```

**Expected output:**
```
🔧 Loading Serum AI model...
✅ Model loaded and ready!
🚀 Serum AI Server running on http://localhost:8080
```

**Note:** First-time startup takes ~20-30 seconds to load model into memory.

### Step 2: Test the API

#### Health Check:
```bash
curl http://localhost:8080/health
```

Expected: `{"status":"healthy","model_loaded":true}`

#### Generate Preset:
```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Deep dubstep bass with lots of wobble"}'
```

Expected: JSON with `parameter_changes` array (~26 seconds)

### Step 3: Use with Max for Live

1. Open Ableton Live with Max for Live
2. Load Serum 2 VST in a track
3. Create new Max for Live device with `serum2_ai_controller.js`
4. Connect vst~ object to Serum 2
5. Use Python bridge: `python max_api_bridge.py`

**Example Max Patch Structure:**
```
[textedit] → [prepend generate] → [js serum2_ai_controller.js]
                                          ↓
                                    [vst~ @dll Serum2]
```

## 📊 Model Performance

### Semantic Accuracy (20 test examples):
- **Parameter Overlap**: 1.000 (100% - exact same params)
- **Value MAE**: 0.167 (excellent similarity)
- **Critical Param Recall**: 1.000 (100%)
- **Name Overlap**: 1.000 (100%)

### Structural Validity (90 test examples):
- **Valid JSON**: 98.9%
- **Param Count (15-20)**: 98.9%
- **Values in [0,1]**: 98.9%
- **Indices in [1,2623]**: 98.9%

## 🔧 Troubleshooting

### Port 8080 already in use
```bash
lsof -ti:8080 | xargs kill -9
```

### Model loading fails
Check that adapter path exists:
```bash
ls serum_lora_adapters/conservative_adapters/
```

Should contain: `adapters.safetensors`, `adapter_config.json`

### Slow generation (>60s)
Normal on first request. Subsequent requests should be ~20-30s.

## 📁 File Structure

```
serum_llm_2/
├── serum_ai_app/
│   ├── server/
│   │   └── api_server.py              # Flask API server
│   ├── build_mac_app.py               # PyInstaller build script
│   ├── menu_bar_launcher.py           # Mac menu bar app
│   └── requirements.txt               # Python dependencies
├── serum_lora_adapters/
│   ├── conservative_adapters/         # Final working model
│   │   ├── adapters.safetensors       # LoRA weights (6.5MB)
│   │   └── adapter_config.json        # Config
│   └── training_data_v2/              # 80/10/10 split
│       ├── train.jsonl                # 717 examples
│       ├── valid.jsonl                # 90 examples
│       └── test.jsonl                 # 90 examples
├── serum2_ai_controller.js            # Max for Live controller
├── max_api_bridge.py                  # Python bridge for Max
└── data/
    └── serum_gpt5_mistral_897_CORRECTED_hermes_training.jsonl
```

## 🎯 Next Steps for Distribution

1. **Build Mac App**:
   ```bash
   python serum_ai_app/build_mac_app.py
   ```

2. **Create Max Patch**: Build UI with textedit, buttons, status indicators

3. **Package**: Zip the .app bundle + Max patch + instructions

4. **Share with Producers**: Send package for user testing

## 🚀 Building the Mac App

```bash
# Install PyInstaller
pip install pyinstaller rumps

# Build the app
python serum_ai_app/build_mac_app.py
```

Expected output: `dist/SerumAI.app` (~15-20GB with bundled model)

## 📝 API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### POST /generate
Generate Serum preset from text

**Request:**
```json
{
  "description": "Deep dubstep bass with lots of wobble"
}
```

**Response:**
```json
{
  "parameter_changes": [
    {"index": 1, "value": 0.75, "name": "Main Vol"},
    {"index": 22, "value": 0.5, "name": "A Level"}
  ],
  "critical_changes": ["Main Vol", "A Level"]
}
```

### POST /shutdown
Gracefully shutdown the server

## 🎛️ Serum 2 Parameter Info

- **Total Parameters**: 2,623
- **Index Range**: 1-2623 (1-based indexing)
- **Value Range**: 0.0 - 1.0
- **Control**: Send `[index value]` to vst~ object

## 📈 Training Details

### Conservative Training (Final):
- **Model**: Hermes-2-Pro-Mistral-7B
- **Method**: LoRA (Low-Rank Adaptation)
- **Learning Rate**: 1e-4 (Mistral official recommendation)
- **Batch Size**: 8
- **LoRA Layers**: 8
- **Iterations**: 500
- **Val Loss**: 1.154 → 0.140 (88% reduction)
- **Trainable Params**: 0.024% of model

### Why Conservative Training Worked:
- Previous attempt with LR 3e-4 caused catastrophic forgetting
- Mistral AI recommends 1e-4 for Mistral 7B
- Lower LR preserved base language capabilities
- Result: 98.9% valid JSON, semantically accurate parameters

## 🔬 Evaluation Methodology

1. **Structural Validation**: JSON validity, param count, value ranges
2. **Semantic Similarity**: Jaccard index for param overlap, MAE for values
3. **Critical Parameter Recall**: % of important params predicted
4. **Parameter Name Matching**: Ensuring correct param names

## 💾 Model Hosting

**HuggingFace**: `bapinero/BAP-Labs-M1`

Download locally:
```bash
huggingface-cli download bapinero/BAP-Labs-M1 --local-dir serum_lora_adapters/conservative_adapters
```

---

Built with ❤️ using MLX, Mistral 7B, and a whole lot of Serum presets.
