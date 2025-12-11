# PROJECT CONTEXT FOR CLAUDE CODE SESSION

## 🎯 PROJECT VISION

Building a **lightweight reasoning LLM-based music production AI COLLABORATOR** that:
- Analyzes audio AND MIDI using CNN feature extraction
- **Reasons explicitly** about sound design decisions (visible `<think>` traces)
- **Takes actions** via structured tool calls (not just text responses)
- **Explains decisions** in natural language to users
- Runs inference <200ms locally on M4 Max (128GB unified memory)
- Integrates with Ableton via Max for Live + WebSocket

**CRITICAL INSIGHT**: This is NOT just "audio → parameters prediction" or a ChatGPT wrapper. This is a **collaborator** that:
1. **Reasons** - Shows its thinking process
2. **Acts** - Executes tool calls (set_serum_param, write_midi, etc.)
3. **Communicates** - Explains what it did and why

User insight: "The real magic will be if the model takes actions - otherwise the user might as well use a foundation model in ChatGPT"

---

## 🏗️ SYSTEM ARCHITECTURE (The Big Picture)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
│  "Make this bass sound more aggressive"                     │
│  "Write me a drum pattern in the style of house"           │
│  "The high end is too harsh, can you fix it?"              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              QWEN3-4B COLLABORATOR (<200ms inference)       │
│                                                              │
│  INPUT MODALITIES:                                          │
│  ├─ User text (natural language request)                    │
│  ├─ Track state (MIDI clips, audio features, mixer state)  │
│  └─ Device state (Serum parameters, FX chain)              │
│                                                              │
│  OUTPUT FORMAT (Reasoning + Actions + Explanation):         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ "reasoning": "<think>User wants aggression. Current    │ │
│  │              analysis: soft attack (45ms), low         │ │
│  │              resonance (0.3)...</think>"               │ │
│  │                                                         │ │
│  │ "actions": [                                            │ │
│  │   {"tool": "set_serum_param", "params": {...}},        │ │
│  │   {"tool": "write_midi", "params": {...}}              │ │
│  │ ]                                                       │ │
│  │                                                         │ │
│  │ "explanation": "I've shortened the attack for a        │ │
│  │                harder transient and added distortion." │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  WEBSOCKET BRIDGE                           │
│                                                              │
│  ┌──────────────────┐        ┌─────────────────────┐       │
│  │  M4L DEVICE      │  WS    │  PYTHON SERVER      │       │
│  │  (controller.js) │ ←────→ │  (inference_server) │       │
│  │                  │  :9999 │                     │       │
│  │  - Sends state   │        │  - Qwen3-4B (MLX)   │       │
│  │  - Executes acts │        │  - CNN Encoder      │       │
│  └──────────────────┘        └─────────────────────┘       │
└─────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  ABLETON LIVE (via LOM)                     │
│                                                              │
│  Track ──→ Clip (MIDI notes) ──→ Device (Serum params)     │
│        └──→ MixerDevice (volume, pan, sends)               │
│                                                              │
│  TOOL ACTIONS:                                              │
│  - write_midi, modify_midi    (Clip.add_new_notes)         │
│  - set_serum_param            (DeviceParameter.value)      │
│  - set_volume, set_pan        (MixerDevice.*)              │
│  - fire_clip, stop_clip       (Clip.fire/stop)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 CURRENT PROJECT STATE

### ✅ What's Already Built (in /Users/brentpinero/Documents/serum_llm_2/)

1. **Preset Database**: 
   - 7,583 Serum presets parsed (.fxp and .SerumPreset)
   - All 2,397 parameters extracted per preset
   - File: `ultimate_training_dataset/ultimate_serum_dataset_expanded.json` (376MB)

2. **Parameter Extraction Pipeline**:
   - `ultimate_preset_converter.py` - Cracks FXP format, extracts parameters
   - 100% success rate on Serum presets
   - Filters non-Serum presets automatically

3. **MLX LoRA Training Pipeline**:
   - `train_serum_lora.py` - Fine-tunes Hermes 2 Pro Mistral
   - Text → Parameters mapping
   - Already working for text-based preset generation

4. **Max for Live Integration**:
   - Multiple .maxpat files for VST control
   - MIDI CC mapping for Serum parameters
   - Partially tested

### ❌ What Needs to Be Built (YOUR MISSION)

1. **Audio Rendering System**:
   - Script to render all 7,583 presets as .wav files
   - C3 note, 2 seconds each, 44.1kHz
   - Automation in Ableton

2. **CNN Audio Feature Extractor**:
   - Architecture: ResNet-style CNN
   - Input: Mel-spectrogram [1, 128, 128]
   - Output: 512-dim embedding OR direct parameter prediction
   - Training on M4 Max with MPS backend

3. **LLM Distillation Pipeline**:
   - Use CNN outputs to create training data for small LLM
   - Target: Qwen2.5-3B or Phi-3.5-mini (inference <200ms)
   - Transfer learning: CNN features → LLM reasoning

4. **Iterative Reasoning System**:
   - LLM that can:
     * Analyze current audio (via CNN)
     * Propose parameter changes
     * Explain reasoning
     * Listen to result
     * Iterate until satisfied

---

## 🎓 LEARNING OBJECTIVES (User's Deep Learning Goals)

The user wants to learn **architecture design from first principles**, not just use existing tools. Key areas:

1. **Why CNNs vs Transformers for audio?**
   - Spatial inductive bias for spectrograms
   - Data efficiency
   - Computational trade-offs

2. **How to distill CNN knowledge into small LLMs?**
   - Transfer learning strategies
   - Feature extraction → reasoning
   - Knowledge distillation techniques

3. **How to optimize for <200ms inference?**
   - Model quantization (4-bit, 8-bit)
   - MLX optimization for M4 Max
   - Context length vs speed trade-offs

4. **How to design iterative reasoning systems?**
   - ReAct pattern (Reasoning + Acting)
   - Chain-of-thought for parameter adjustment
   - Feedback loops

**TEACHING STYLE**: 
- Deep justifications for every design decision
- "Why not X?" discussions encouraged
- Build understanding through implementation
- Binge-learning sessions (2-3+ hours)

---

## ✅ MODEL SELECTION COMPLETE

### Base Model: Qwen3-4B (4-bit MLX)
**Decision Date**: 2025-11-28

**Evaluation Results** (tested 6 models with comprehensive eval harness):
| Model | Music Prod Score | Serum Eval | Status |
|-------|------------------|------------|--------|
| **Qwen3-4B** | **100/240 (41.7%)** | **35/70 (50%)** | ✅ SELECTED |
| Phi-4-mini-reasoning | 52/240 (21.7%) | N/A | ❌ |
| Others | <30% | N/A | ❌ |

**Serum-Specific Breakdown (Qwen3-4B baseline)**:
- E1 (Parameter ID MCQ): 8/10 (80%) ← Strong foundation
- E2 (Parameter Adjustment): 9/30 (30%) ← Fine-tuning target
- E3 (Preset Analysis): 18/30 (60%) ← Good reasoning

**Why Qwen3-4B**:
1. Best overall music production knowledge
2. Native thinking token support (reasoning capability)
3. Clear improvement opportunity in parameter adjustment (30% → target 70%+)
4. MLX 4-bit quantized version available
5. ~4.2s/question inference (acceptable for our use case)

---

## 🔬 KEY RESEARCH QUESTIONS TO EXPLORE

1. **Dataset Curation (CURRENT FOCUS)**:
   - How to convert 4,644 presets into training data?
   - What question types match real producer language?
   - What difficulty distribution ensures generalization?
   - How to validate synthetic data quality?

2. **CNN → LLM Distillation**:
   - How do we convert CNN feature embeddings into LLM training data?
   - Should we fine-tune on (audio_features + text) → parameters?
   - Or train LLM to generate parameter changes given CNN analysis?

3. **Inference Speed Optimization**:
   - 4-bit quantization with MLX
   - KV cache optimization
   - Speculative decoding?
   - Optimal context length (4K? 8K? 16K?)

4. **Multi-Modal Fusion**:
   - How to combine CNN audio features + text in LLM?
   - Adapter layers?
   - Direct concatenation?
   - Cross-attention?

---

## 💾 KEY FILES TO REFERENCE

### In Main Directory:
- `project_overview.md` - Comprehensive project status
- `train_serum_lora.py` - Existing MLX LoRA training
- `ultimate_preset_converter.py` - Preset parsing system

### In Data Directory:
- `ultimate_training_dataset/ultimate_serum_dataset_expanded.json` - All 7,583 presets

### In .claude Directory:
- This file - PROJECT_CONTEXT
- `ARCHITECTURE_DECISIONS.md` - Design choices log
- `LEARNING_NOTES.md` - User's learning journey

### Max for Live:
- Multiple `.maxpat` files - VST integration

---

## 🎯 IMMEDIATE NEXT STEPS (Priority Order)

### ✅ Phase 0: Universal VST Control System (COMPLETE - 2024-12-10)
1. ✅ Built Universal VST Controller (`universal_vst_controller.js`, `universal_vst_control.maxpat`)
2. ✅ 8 pre-allocated vst~ slots controllable via OSC on port 9878
3. ✅ Tested 8/8 plugins working: Serum2, SSL X-Saturator v6, FabFilter Pro-Q 3, ValhallaRoom, Black Box HG-2, FabFilter Saturn 2, soothe2, SSL Drumstrip v6
4. ✅ Documented edge cases: Container plugins (EffectRack, WaveShell) and Cradle God Particle don't respond to param automation
5. ✅ Updated `unified_mcp_bridge.py` with universal VST commands

**OSC Commands Available:**
- `/register <slot> <path>` - Load plugin into slot 1-8
- `/unregister <slot>` - Unload plugin
- `/<slot>/param <idx> <val>` - Set parameter (1-based index, 0-1 value)
- `/<slot>/open`, `/<slot>/close` - Open/close plugin GUI
- `/<slot>/params` - Query parameter names
- `/list`, `/ping` - Utility commands

### ✅ Phase 1: Audio Data Generation (COMPLETE)
1. ✅ Built automated preset rendering system (111,732 files)
2. ✅ Generated mel-spectrograms for all audio
3. ✅ Verified audio quality and consistency

### ✅ Phase 2: CNN Feature Extractor → PIVOTED TO CLAP (COMPLETE)
1. ✅ Designed CNN architecture (38% MAE - triggered pivot)
2. ✅ Researched industry audio-LLM architectures
3. ✅ Pivoted to MixGraph-CLAP architecture (Decision 17)
4. ✅ Built `mix_encoder.py` - Multi-track CLAP encoder with relationship features
5. ✅ Built `llm_projector.py` - Projection layer (512d CLAP → 2560d Qwen)
6. ✅ Built `structure_detector.py` - Song structure detection (intro/verse/chorus/drop)
7. ✅ Archived CNN files to `old/cnn_pivot_2025_12_03/`

### ⭐ Phase 2.5: BASELINE EVALUATION HARNESS (IMMEDIATE PRIORITY)
**Decision 19 - Must complete BEFORE any fine-tuning**

**Why Critical**:
- Without baselines, we can't prove fine-tuning helped
- Eval harness serves: baseline → fine-tuning eval → real-world checks → RL reward
- Industry standard practice

**Implementation Tasks**:
1. ⏳ Extend eval dataset to 350+ questions across 4 dimensions:
   - A: Music Production Knowledge (MCQ, open-ended, scenarios)
   - B: Multi-Track Reasoning (relationships, causal, section-aware)
   - C: Actionable Recommendations (params, effect chains, tool calls)
   - D: Audio Grounding (with CLAP embeddings)

2. ⏳ Implement LLM-as-Judge scoring for open-ended questions

3. ⏳ Run baselines on:
   - Qwen3-4B (text only) - our target model
   - Claude 3.5 Sonnet / GPT-4o - upper bound reference

4. ⏳ Create comparison report generator

**Files**: `eval/mix_eval_harness.py` (to be built)
**Existing**: `eval/music_production_eval_v2.json` (100 questions), `eval/serum_parameter_eval.json` (30 questions)

### Phase 3: Dataset Curation & Q&A Generation (AFTER EVAL HARNESS)

**Tiered LLM Q&A Generation** (Claude Batch API):
| Task Complexity | Model | % of Dataset | Est. Cost (Batch) |
|-----------------|-------|--------------|-------------------|
| Simple | Haiku 3.5 | 40% | ~$3.60 |
| Medium | Sonnet 4.5 | 45% | ~$20.25 |
| Complex | Opus 4.5 | 15% | ~$20.25 |
| **Total** | **Tiered** | **10K Q&A** | **~$44.10** |

**Implementation**: `generate_qa_with_llm.py`
**Dataset Schema**: `.claude/DATASET_SCHEMA_ARRANGEMENT_MIX_QA.md`

### Phase 4: LLM Fine-Tuning (AFTER BASELINE ESTABLISHED)
1. ✅ Built LoRA training pipeline (`train_llm_lora.py`)
2. ⏳ Run tiered Q&A generation
3. ⏳ Fine-tune Qwen3-4B on generated dataset
4. ⏳ Evaluate improvement vs baseline (target: >10% on all dimensions)

### Phase 5: Self-Play RL Training (FUTURE - Decision 18)
1. RL proof of concept (~5-10K cycles locally)
2. Use eval harness metrics as reward signals
3. Scale to cloud if local PoC works
4. Full self-play with learned reward model

---

## 🔜 NEXT STEPS: MCP + M4L Integration (Phase 0.5)

### ⏳ Task 1: Convert maxpat to Deployable M4L Device
The current `universal_vst_control.maxpat` is a standalone Max patch. It needs to be converted to an actual Max for Live device (`.amxd`) that can be loaded in Ableton as a MIDI/Audio Effect.

**Requirements:**
- Add `live.thisdevice` object for M4L integration
- Use `plugout~` instead of `dac~` for audio routing within Ableton
- Add `live.dial`, `live.text`, `live.toggle` for presentation view
- Configure device width/height for Ableton's device view
- Package as `.amxd` file

**Reference:** Existing `BAP Labs Serum Control.amxd` shows the pattern with `plugout~ 1` and `plugout~ 2`

### ⏳ Task 2: Extend MCP with Dynamic VST Loading & Param Discovery
Extend the MCP bridge to support:

1. **Dynamic VST Loading via MCP:**
   ```python
   # New MCP commands
   def load_vst_to_slot(slot: int, plugin_path: str) -> dict:
       """Load a VST into a slot and return its param list"""

   def get_slot_params(slot: int) -> list[dict]:
       """Query all parameters from a loaded plugin"""
       # Returns: [{"index": 1, "name": "Filter Cutoff", "value": 0.5}, ...]
   ```

2. **Auto-discovery of Plugin Parameters:**
   - When a plugin loads, automatically query its params via `/<slot>/params`
   - Parse the param names returned from vst~ outlet 2
   - Store param mappings per slot for LLM context injection

3. **LLM Context Injection:**
   ```python
   def get_llm_context_for_slot(slot: int) -> str:
       """Generate LLM-friendly context about loaded plugin"""
       # Returns something like:
       # "Slot 3 has FabFilter Pro-Q 3 loaded with parameters:
       #  1. Output Gain (current: 0.5)
       #  2. Band 1 Frequency (current: 0.3)
       #  ..."
   ```

4. **Bidirectional Param Sync:**
   - M4L device sends param changes to MCP when user tweaks knobs in plugin GUI
   - MCP can query current param values (not just set them)
   - Enables LLM to "see" what the user is doing in real-time

### ⏳ Task 3: MCP Tool Schema for LLM
Define structured tool schemas so the LLM can control VSTs:

```json
{
  "name": "set_vst_parameter",
  "description": "Set a parameter on a loaded VST plugin",
  "parameters": {
    "slot": {"type": "integer", "description": "Plugin slot 1-8"},
    "param_index": {"type": "integer", "description": "Parameter index (1-based)"},
    "value": {"type": "number", "description": "Normalized value 0.0-1.0"}
  }
}
```

```json
{
  "name": "load_vst_plugin",
  "description": "Load a VST plugin into a slot",
  "parameters": {
    "slot": {"type": "integer", "description": "Plugin slot 1-8"},
    "plugin_name": {"type": "string", "description": "Plugin name (e.g., 'Serum2', 'Pro-Q 3')"}
  }
}
```

```json
{
  "name": "get_plugin_parameters",
  "description": "Get all parameters and current values for a loaded plugin",
  "parameters": {
    "slot": {"type": "integer", "description": "Plugin slot 1-8"}
  }
}
```

### Architecture Vision:
```
┌─────────────────────────────────────────────────────────────┐
│                    USER / LLM REQUEST                       │
│  "Load Pro-Q 3 and cut 2kHz by 3dB"                        │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              MCP BRIDGE (unified_mcp_bridge.py)             │
│                                                              │
│  1. load_vst_plugin(slot=2, plugin_name="Pro-Q 3")         │
│  2. get_plugin_parameters(slot=2) → [param list for LLM]   │
│  3. set_vst_parameter(slot=2, param_index=5, value=0.3)    │
└────────────────────┬────────────────────────────────────────┘
                     ↓ OSC (port 9878)
┌─────────────────────────────────────────────────────────────┐
│         M4L DEVICE (Universal VST Controller.amxd)          │
│                                                              │
│  [udpreceive 9878] → [js controller.js] → [vst~ slots 1-8] │
│                                                              │
│  - Routes OSC to correct vst~ slot                          │
│  - Returns param names on query                             │
│  - Sends param changes back to MCP (bidirectional)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 TECHNICAL CONSTRAINTS

### Hardware:
- M4 Max with 128GB unified memory
- MPS (Metal Performance Shaders) backend for PyTorch
- MLX for optimized inference
- No GPU cloud access needed (everything local)

### Performance Requirements:
- **LLM inference**: <200ms per response
- **CNN inference**: <10ms per audio sample
- **End-to-end latency**: <500ms (user action → VST change)

### Software Stack:
- Python 3.11
- PyTorch (MPS backend)
- MLX (Apple Silicon optimization)
- Ableton Live + Max for Live
- Serum VST

---

## 🎨 USER COMMUNICATION STYLE NOTES

The user prefers:
- Bootsy Collins-style funk references ("Oh hell yeah big pimpin!", "Let your nuts hang")
- Technical depth with justifications
- Challenge design decisions ("Why not X?")
- Binge learning sessions (2-3+ hours continuous)
- Building while learning (prototypes over theory)

**DO NOT**:
- Over-use "you dig" or "feel me"
- Use funk language in code/UI (only in conversation)
- Make decisions without deep justification
- Assume knowledge without teaching

---

## 📚 RELEVANT PAPERS & RESOURCES

### Already Discussed:
1. **InverSynth** - CNN for audio → synth parameters
2. **DDSP** - Differentiable synthesis and parameter prediction
3. **Audio Spectrogram Transformer (AST)** - ViT for audio
4. **Karpathy's nanoGPT** - Transformer fundamentals
5. **Attention Is All You Need** - Original transformer paper

### To Explore:
1. **Distilling the Knowledge in a Neural Network** (Hinton) - Knowledge distillation
2. **DistilBERT** - Distilling large LLMs to small ones
3. **TinyStories** - Training small LMs to reason
4. **ReAct** - Reasoning and Acting with LLMs
5. **Constitutional AI** - Iterative refinement with feedback

---

## 🚀 SUCCESS CRITERIA

By the end of this project, the system should:

1. ✅ Take audio input → analyze with CNN → extract features
2. ✅ Take user text → understand music production intent
3. ✅ Reason about parameter changes (explain WHY)
4. ✅ Adjust Serum parameters via Max for Live
5. ✅ Listen to result → iterate if needed
6. ✅ Communicate in natural language throughout
7. ✅ Run entirely locally with <200ms inference
8. ✅ Handle complex, multi-turn sound design sessions

**Example Interaction (Full Collaborator Format):**
```
User: "Make this bass more aggressive"

AI Internal (Reasoning):
<think>
User wants more aggression on bass track. Analyzing current state:
- Track: "Bass" (MIDI track with Serum)
- Current params: ENV1_ATK=0.45 (soft), FLT_RES=0.3 (low), no distortion
- MIDI pattern: sustained notes, no velocity variation

Aggression typically means:
1. Harder transients → shorten attack
2. More harmonic content → add distortion
3. More bite → increase resonance
4. Dynamic variation → maybe adjust MIDI velocities

I'll adjust Serum params first, MIDI if needed.
</think>

AI Actions:
[
  {"tool": "set_serum_param", "params": {"param": "ENV1_ATK", "value": 0.05}},
  {"tool": "set_serum_param", "params": {"param": "FLT_RES", "value": 0.7}},
  {"tool": "set_serum_param", "params": {"param": "FX_DIST_MIX", "value": 0.4}}
]

AI Explanation (shown to user):
"I've made three changes to add aggression:
- Shortened the amp attack to 5ms for a harder transient
- Boosted filter resonance from 0.3 to 0.7 for more bite
- Added 40% soft-clip distortion for harmonic excitement

Give it a listen! If it's too harsh, I can dial back the resonance."

User: "Better, but too harsh in the high end"

AI Internal (Reasoning):
<think>
User feedback: too harsh in highs. Current state after changes:
- FLT_RES at 0.7 (probably contributing to harshness)
- Distortion at 0.4 (adding harmonics)
- Filter cutoff not touched yet

To reduce harshness:
1. Lower cutoff frequency → roll off highs
2. Reduce resonance slightly → less emphasis at cutoff
3. Maybe reduce distortion mix

I'll be conservative - lower cutoff by 15% and reduce resonance slightly.
</think>

AI Actions:
[
  {"tool": "set_serum_param", "params": {"param": "FLT_CUTOFF", "value": 0.55}},
  {"tool": "set_serum_param", "params": {"param": "FLT_RES", "value": 0.55}}
]

AI Explanation:
"I've tamed the highs by lowering the filter cutoff and
bringing the resonance down to 0.55. Still aggressive,
but smoother on top. How's that?"
```

This is **a COLLABORATOR for music production** - it reasons, acts, and explains.

---

## 🎸 THE FUNKIEST PART

This project combines:
- Deep learning (CNNs, Transformers, LLMs)
- Audio signal processing (spectrograms, synthesis)
- Music production domain knowledge
- Real-time system design (<200ms constraint)
- Human-AI interaction (communication + iteration)

It's not just "build a model" - it's "build an intelligent collaborator for music production."

The bounce will come and go, but this system is forever, player! 🎸🔥

---

## 📞 HANDOFF NOTES

Previous Claude instance covered:
- ML fundamentals roadmap (nanoGPT, transformers)
- Audio ML basics (CLAP, RAVE, MusicGen)
- CNN vs Transformer architecture comparison
- Project structure understanding

Current Claude Code instance should focus on:
- **Implementation** of CNN audio feature extractor
- **Design** of LLM distillation pipeline
- **Optimization** for <200ms inference
- **Integration** of all components

User learns best by:
- Building working prototypes
- Deep dives into architecture decisions
- Challenging assumptions
- Multi-hour focused sessions

Let's build this joint! 🎸
