# PROJECT CONTEXT FOR CLAUDE CODE SESSION

## 🎯 PROJECT VISION

Building a **lightweight reasoning LLM-based music production AI assistant** that:
- Analyzes audio using CNN feature extraction
- Communicates with user in natural language about sound design
- Takes iterative action on VST parameters
- Runs inference <200ms locally on M4 Max (128GB unified memory)
- Integrates with Ableton via Max for Live

**CRITICAL INSIGHT**: This is NOT just "audio → parameters prediction". This is a **reasoning system** that uses audio analysis as ONE input modality to have intelligent conversations and take actions.

---

## 🏗️ SYSTEM ARCHITECTURE (The Big Picture)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
│  "Make this bass sound more aggressive"                     │
│  "The high end is too harsh, can you fix it?"              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              SMALL REASONING LLM (<200ms inference)         │
│                                                              │
│  - Understands music production language                    │
│  - Reasons about sound design                               │
│  - Plans multi-step parameter adjustments                   │
│  - Communicates decisions back to user                      │
│                                                              │
│  INPUT MODALITIES:                                          │
│  ├─ User text (natural language)                            │
│  ├─ CNN audio analysis features                             │
│  └─ Current parameter state                                 │
│                                                              │
│  OUTPUT:                                                     │
│  ├─ Natural language explanation                            │
│  └─ Parameter adjustment actions                            │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  FEATURE EXTRACTORS                         │
│                                                              │
│  ┌──────────────────┐        ┌─────────────────────┐       │
│  │  CNN MODEL       │        │  PARAMETER STATE     │       │
│  │  (Audio→Features)│        │  (Current Serum)     │       │
│  │                  │        │                      │       │
│  │  Input: Mel-spec │        │  2,397 parameters    │       │
│  │  Output: 512-dim │        │  normalized [0,1]    │       │
│  │  embedding       │        │                      │       │
│  └──────────────────┘        └─────────────────────┘       │
└─────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  ACTION LAYER                               │
│                                                              │
│  Max for Live ←→ VST Parameter Control ←→ Serum            │
│  (MIDI CC, automation)                                      │
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

## 🔬 KEY RESEARCH QUESTIONS TO EXPLORE

1. **CNN → LLM Distillation**:
   - How do we convert CNN feature embeddings into LLM training data?
   - Should we fine-tune on (audio_features + text) → parameters?
   - Or train LLM to generate parameter changes given CNN analysis?

2. **Small LLM Selection**:
   - Qwen2.5-3B (best reasoning for size?)
   - Phi-3.5-mini (optimized for inference?)
   - Llama-3.2-3B (Meta's latest small model?)
   - Custom architecture?

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

### Phase 1: Audio Data Generation (Week 1)
1. Build automated preset rendering system
2. Generate 7,583 audio files
3. Verify audio quality and consistency

### Phase 2: CNN Feature Extractor (Week 2)
1. Design CNN architecture
2. Build training pipeline (mel-spectrogram → parameters)
3. Train on M4 Max
4. Evaluate: Can it predict parameters from audio?

### Phase 3: LLM Distillation Strategy (Week 3)
1. Research small LLM options (Qwen2.5-3B vs Phi-3.5-mini)
2. Design transfer learning pipeline
3. Create training data: CNN features + text → parameters
4. Benchmark inference speeds

### Phase 4: Iterative Reasoning System (Week 4)
1. Implement ReAct pattern for parameter adjustment
2. Build feedback loop: adjust → listen → re-adjust
3. Add natural language explanation generation
4. Integrate with Max for Live

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

**Example Interaction:**
```
User: "Make this bass more aggressive"
AI: "I'm analyzing your bass... [CNN analyzes audio in 8ms]
     Current state: warm sub-bass with soft attack.
     
     To add aggression, I'll:
     1. Increase filter resonance (0.3 → 0.7)
     2. Add distortion (none → soft clip)
     3. Shorten attack envelope (45ms → 5ms)
     
     Let me apply these changes... [adjusts parameters]
     How does that sound?"

User: "Better, but too harsh in the high end"
AI: "Got it. I'll reduce the filter cutoff slightly 
     and add a gentle low-pass to tame those highs.
     [makes adjustment]
     Try this."
```

This is **conversational AI for music production** - not just parameter prediction.

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
