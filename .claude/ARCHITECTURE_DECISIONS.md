# ARCHITECTURE DECISIONS LOG

## Decision 1: CNN for Audio Feature Extraction
**Date**: Session 1  
**Decision**: Use CNN (not Transformer) for initial audio → parameter feature extraction  
**Rationale**:
- Spectrograms have spatial structure (frequency × time)
- CNNs have translational equivariance (good for spectrograms)
- More data-efficient (works with 7,583 samples)
- Faster training/inference on M4 Max
- Proven track record (InverSynth, DDSP)

**Trade-offs**:
- Limited global context (vs Transformers)
- No pre-trained models available (vs AST)
- Less flexible than attention-based models

**Status**: Approved for Phase 1 implementation

---

## Decision 2: Small LLM for Reasoning (Not Just CNN Regression)
**Date**: Session 1  
**Decision**: Use CNN outputs to train a small reasoning LLM, NOT use CNN alone  
**Rationale**:
- Music production requires COMMUNICATION (explain decisions)
- Need ITERATIVE reasoning (adjust → listen → re-adjust)
- CNNs lack language capability
- Small LLM can integrate multiple modalities (audio features + text + parameter state)

**Architecture**:
```
CNN (audio features) ──┐
                       ├──> Small LLM ──> Actions + Explanations
User text ────────────┤
Current params ───────┘
```

**Status**: Core design principle

---

## Decision 3: <200ms Inference Constraint
**Date**: Session 1  
**Decision**: Target <200ms for LLM inference on M4 Max  
**Rationale**:
- Real-time feel for music production workflow
- Enables iterative back-and-forth conversations
- Competitive with commercial AI tools

**Implementation Strategies**:
- 4-bit quantization (MLX)
- Small model (3B parameters max)
- Optimized context length
- KV cache optimization

**Status**: Hard requirement

---

## Decision 4: Transfer Learning Pipeline
**Date**: Session 1  
**Decision**: CNN → LLM distillation via transfer learning  
**Approach**: TBD (needs research)
**Options**:
1. Fine-tune LLM on (CNN_features + text) → parameter_changes
2. Use CNN as "perception module" + LLM as "reasoning module"
3. Multi-modal adapter layers

**Status**: To be designed in Phase 3

---

## Decision 5: Dataset Strategy
**Date**: Session 1  
**Decision**: Render all 7,583 presets as audio for CNN training  
**Format**:
- Note: C3 (bass-focused)
- Duration: 2 seconds
- Sample rate: 44.1kHz
- File format: WAV (uncompressed)

**Status**: Phase 1 priority

---

---

## Decision 6: Base Model Selection - Qwen3-4B
**Date**: 2025-11-28
**Decision**: Use Qwen3-4B as the base model for fine-tuning
**Evaluation Methodology**:
- Built comprehensive MLX-based eval harness with LLM-as-Judge (Claude Sonnet 4.5)
- Tested 6 models: Qwen3-4B, Phi-4-mini-reasoning, Qwen2.5-3B, Qwen2.5-1.5B, DeepSeek-R1-1.5B, Gemma-2-2B
- 100-question music production eval (MCQ, open-ended, scenario-based)
- 30-question Serum-specific parameter manipulation eval

**Results**:
| Model | Music Prod Eval | Serum Eval | Inference Speed |
|-------|-----------------|------------|-----------------|
| **Qwen3-4B** | **100/240 (41.7%)** | **35/70 (50%)** | ~4.2s/question |
| Phi-4-mini-reasoning | 52/240 (21.7%) | N/A | ~4.5s/question |
| Others | <30% | N/A | Various |

**Serum Eval Breakdown (Qwen3-4B)**:
- E1 (MCQ - Parameter ID): 8/10 (80%) ← Strong conceptual knowledge
- E2 (Open - Parameter Adj): 9/30 (30%) ← Room for fine-tuning improvement
- E3 (Scenario - Preset Analysis): 18/30 (60%) ← Good reasoning

**Rationale**:
1. **Best overall performance** - 2x better than second-place Phi-4
2. **Strong MCQ performance** - Indicates good foundational knowledge
3. **Clear fine-tuning opportunity** - E2 scores (30%) can improve with preset data
4. **Thinking/reasoning built-in** - Has native thinking tokens support
5. **MLX optimized** - 4-bit quantized version available

**Status**: ✅ APPROVED - Proceeding to fine-tuning dataset curation

---

## Decision 7: Tiered LLM Q&A Generation Strategy
**Date**: 2025-11-29
**Decision**: Use tiered Claude models via Batch API for Q&A generation based on task complexity

**Architecture**:
```
Task Complexity → Model Selection → Batch API (50% discount)

┌─────────────────────────────────────────────────────────────────┐
│  TIER 1: SIMPLE TASKS (Haiku 3.5)                               │
│  Cost: $0.80/$4.00 per 1M tokens (Batch: $0.40/$2.00)          │
│  Tasks:                                                         │
│  - Direct parameter queries ("What is the filter cutoff?")     │
│  - Simple sound descriptions                                    │
│  - Basic "how-to" questions                                     │
│  Est. 40% of dataset (~4,000 Q&A pairs @ ~$3.60 batch)         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 2: MEDIUM TASKS (Sonnet 4.5)                              │
│  Cost: $3.00/$15.00 per 1M tokens (Batch: $1.50/$7.50)         │
│  Tasks:                                                         │
│  - Sound modification advice (multi-parameter coordination)    │
│  - Preset analysis with reasoning                               │
│  - Comparative questions                                        │
│  - Musical context recommendations                              │
│  Est. 45% of dataset (~4,500 Q&A pairs @ ~$20.25 batch)        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 3: COMPLEX TASKS (Opus 4.5)                               │
│  Cost: $15.00/$75.00 per 1M tokens (Batch: $7.50/$37.50)       │
│  Tasks:                                                         │
│  - Genre-specific synthesis techniques                          │
│  - Complex troubleshooting scenarios                            │
│  - Multi-step sound design workflows                            │
│  - Advanced MIDI-aware parameter reasoning                      │
│  Est. 15% of dataset (~1,500 Q&A pairs @ ~$20.25 batch)        │
└─────────────────────────────────────────────────────────────────┘
```

**Total Estimated Cost (10,000 Q&A pairs via Batch API)**: ~$44.10
- Without Batch API: ~$88.20 (2x more expensive)
- All Haiku (baseline): ~$9.00 but lower quality on complex tasks
- All Opus (overkill): ~$135.00 (wastes budget on simple tasks)

**Rationale**:
1. **Quality-Cost Optimization**: Use expensive models only where they add value
2. **Batch API Savings**: 50% discount on ALL models makes even Opus feasible
3. **Task-Appropriate Reasoning**: Opus's deeper reasoning for complex sound design
4. **Diversity**: Different models may produce more varied training data

**Implementation**: `generate_qa_with_llm.py` supports model routing based on task type

**Status**: ✅ APPROVED - Ready for implementation after external drive scan

---

## Decision 8: External Hard Drive Data Scan (NEXT PRIORITY)
**Date**: 2025-11-29
**Decision**: Scan external hard drives before running batch Q&A generation

**Rationale**:
1. **More MIDI-Preset Pairs**: External drives likely contain more sample packs with paired content
2. **Project Files (.als)**: The "Holy Grail" - complete Ableton sessions with context
3. **Better Dataset Before Generation**: More data = better Q&A quality
4. **One-Time Scan Cost**: Free (just takes time) vs recurring API costs

**Current Scan Results (Documents only)**:
- 9,922 presets
- 267 MIDI files
- 66 MIDI-preset pairs
- 7 project files

**Expected External Drive Additions**:
- Additional sample pack libraries
- Archived projects with full context
- More MIDI-preset-loop "Holy Trinity" packs

**Scan Command**: `python scan_sample_packs.py --scan-external`

**Status**: ⏳ PENDING - Next priority before batch generation

---

## Decision 9: Collaborator Architecture (Reasoning + Tool Use)
**Date**: 2025-11-29
**Decision**: Model outputs reasoning traces + tool calls + user-facing explanation (not just text responses)

**Rationale**:
User insight: "The real magic will be if the model takes actions - otherwise the user might as well use a foundation model in ChatGPT"

**Response Format**:
```json
{
  "reasoning": "<think>User wants more aggression. Current analysis shows soft attack (45ms) and low resonance (0.3). Aggression typically requires: harder transients (shorter attack), more harmonic content (distortion), brighter tone (higher resonance)...</think>",
  "actions": [
    {"tool": "set_serum_param", "params": {"param": "ENV1_ATK", "value": 0.05}},
    {"tool": "set_serum_param", "params": {"param": "FLT_RES", "value": 0.7}},
    {"tool": "set_serum_param", "params": {"param": "FX_DIST_MIX", "value": 0.4}}
  ],
  "explanation": "I've shortened the attack for a harder transient, boosted the filter resonance for more bite, and added some soft-clip distortion for harmonic excitement. Give it a listen!"
}
```

**Why This Format**:
1. **Reasoning Traces** - Enables chain-of-thought supervision during fine-tuning
2. **Tool Calls** - Structured actions that M4L can execute directly
3. **Explanation** - Natural language for user communication

**Comparison to Alternatives**:
| Approach | Tool Use | Reasoning | User Comms | Fit |
|----------|----------|-----------|------------|-----|
| Text-only | ❌ | ❌ | ✅ | ChatGPT replacement |
| Actions-only | ✅ | ❌ | ❌ | Black box |
| **Reasoning+Actions+Explain** | ✅ | ✅ | ✅ | **COLLABORATOR** |

**Status**: ✅ APPROVED - Core architecture pattern

---

## Decision 10: WebSocket Integration (M4L ↔ Python)
**Date**: 2025-11-29
**Decision**: Use WebSocket for bidirectional communication between Max for Live and Python inference server

**Architecture**:
```
┌─────────────────┐     WebSocket      ┌────────────────────┐
│  Ableton Live   │ ←────────────────→ │  Python Inference  │
│  + M4L Device   │     localhost:9999 │  Server            │
│                 │                    │                    │
│  - Track state  │  ──── JSON ────→   │  - Qwen3-4B        │
│  - Audio stream │                    │  - CNN Encoder     │
│  - Clip data    │  ←─── JSON ────    │  - Tool dispatch   │
│  - Param state  │     (actions)      │                    │
└─────────────────┘                    └────────────────────┘
```

**Why WebSocket**:
1. **Bidirectional** - M4L sends state, receives actions
2. **Real-time** - Low latency for iterative workflow
3. **Proven** - ricardomatias/ableton-live uses this pattern
4. **M4L Compatible** - `node.script` object supports WebSocket

**Message Protocol**:
- **M4L → Python**: `track_state` (clips, params, audio features)
- **Python → M4L**: `tool_response` (reasoning, actions, explanation)

**Status**: ✅ APPROVED - See DATASET_GENERATION_PLAN.md Part 3 for full spec

---

## Decision 11: Tool Schema Based on Live Object Model (LOM)
**Date**: 2025-11-29
**Decision**: Define tool actions based on actual Ableton Live Object Model capabilities

**Tool Categories**:
| Category | Tools | LOM Objects |
|----------|-------|-------------|
| Clip/MIDI | `write_midi`, `modify_midi`, `delete_notes` | `Clip.add_new_notes`, `remove_notes_extended` |
| Device | `set_serum_param`, `set_device_on` | `DeviceParameter.value` |
| Mixer | `set_volume`, `set_pan`, `set_send` | `MixerDevice.volume`, `panning`, `sends` |
| Transport | `fire_clip`, `stop_clip` | `Clip.fire`, `stop` |

**Why LOM-Based**:
1. **Actually Executable** - Not hypothetical tools
2. **Complete Coverage** - Everything Ableton exposes
3. **M4L Native** - Direct `LiveAPI` calls

**Status**: ✅ APPROVED - Full schema in DATASET_GENERATION_PLAN.md Part 3

---

## Decision 12: Expanded Task Taxonomy (21 Categories)
**Date**: 2025-11-29
**Decision**: Expand from 13 to 21 task categories to include composition and multi-track reasoning

**New Categories (T14-T21)**:
| ID | Category | Description | Model Tier |
|----|----------|-------------|------------|
| T14 | Drum Patterns | Write/analyze drum MIDI | Sonnet |
| T15 | Bass Lines | Write/analyze bass MIDI | Sonnet |
| T16 | Chord Voicings | Write/analyze chord progressions | Sonnet/Opus |
| T17 | Melody Writing | Write/analyze melodic content | Opus |
| T18 | Arrangement Advice | Section transitions, structure | Opus |
| T19 | Mix Context Reasoning | Multi-track frequency decisions | Opus |
| T20 | Sound Selection | Choose preset based on mix context | Sonnet |
| T21 | MIDI-Preset Pairing | Match MIDI to appropriate sound | Sonnet |

**Why This Expansion**:
User insight: "To truly be a production assistant - to be more specific it should be a collaborator/assistant. It will need context on how to write good drums or keys etc."

**Status**: ✅ APPROVED - See DATASET_GENERATION_PLAN.md Part 2 for full taxonomy

---

## Future Decisions to Make:

### ~~Dataset Curation Strategy~~ ✅ RESOLVED
See Decision 7 (Tiered LLM Q&A) + Decision 12 (Expanded Taxonomy)

### Multi-Modal Fusion Strategy
**Question**: How to combine CNN audio features with text input in LLM?
**Options**:
- Simple concatenation
- Adapter layers
- Cross-attention
- Prefix tuning

### ~~Iterative Reasoning Pattern~~ ✅ RESOLVED
See Decision 9 (Collaborator Architecture) - Reasoning + Actions + Explanation format enables iteration

---

## Technical Debt / Open Questions:

1. ~~How many parameters should CNN predict? All 2,397 or subset?~~ → See Decision 13 (CLAP pivot)
2. ~~Should CNN output embeddings or direct parameters?~~ → See Decision 13 (CLAP pivot)
3. ~~Optimal mel-spectrogram configuration for Serum sounds?~~ → See Decision 13 (CLAP pivot)
4. How to handle temporal dynamics (e.g., evolving pads)?
5. Evaluation metrics beyond MSE for parameter prediction?

---

## Notes:
- User prefers deep justifications for all decisions
- "Why not X?" discussions encouraged
- Build prototypes to test hypotheses, don't over-engineer

---

# ═══════════════════════════════════════════════════════════════════════════════
# PIVOT 2: CLAP + Multi-Track Relational Dataset (2025-11-30)
# ═══════════════════════════════════════════════════════════════════════════════

## Decision 13: Replace Custom CNN with Pretrained CLAP Encoder
**Date**: 2025-11-30
**Decision**: Abandon custom CNN approach in favor of frozen CLAP audio encoder + projection layer
**Trigger**: Evaluation of CNN results showed 38% MAE, prompting architecture re-evaluation

### Why the CNN Approach Was Problematic

**CNN Training Results (50 epochs)**:
- Val Loss: 0.1832
- Val MAE: 0.384 (38% average error)
- Per-parameter breakdown:
  - 1/30 params GOOD (MAE < 0.15)
  - 3/30 params OK (0.15-0.30)
  - 16/30 params ROUGH (0.30-0.45)
  - 10/30 params POOR (≥ 0.45)
- Critical params like `env1_sus_db` (envelope sustain) and `fil_driv` (filter drive) performed poorly

**The Fundamental Issue**:
We were training a custom CNN from scratch with:
- 4M parameters
- 108K training samples
- No pretrained knowledge

Meanwhile, industry-standard approaches use:
- **Pretrained, frozen** audio encoders
- **Only train** a simple projection layer
- Leverage encoders trained on millions of hours of audio

### Industry Research (2025)

| Model | Audio Encoder | LLM | What They Train |
|-------|--------------|-----|-----------------|
| [Ultravox](https://github.com/fixie-ai/ultravox) | Frozen Whisper | Frozen LLM | **Only projector** (2-3 hrs on 8xH100) |
| [Qwen2-Audio](https://arxiv.org/html/2407.10759v1) | Frozen Whisper-large-v2 | Qwen-7B | Projector + LoRA |
| [LLark (Spotify)](https://research.atspotify.com/2023/10/llark-a-multimodal-foundation-model-for-music) | Frozen Jukebox-5B | LLama2-7B | Projector from scratch |
| [SALMONN](https://aclanthology.org/2024.emnlp-main.361.pdf) | Dual: Whisper + BEATs | Vicuna | Q-former adapter |
| **Us (old)** | Custom CNN from scratch | Qwen | CNN + projector + LoRA |

### Why CLAP Over Whisper

**Key insight**: Whisper is optimized for **speech**, not **music/timbre**.

| Encoder | Purpose | Params | Music/Timbre Proof |
|---------|---------|--------|-------------------|
| **[CLAP](https://github.com/LAION-AI/CLAP)** | Audio-text alignment | ~100M | **90.4% accuracy classifying 953 instruments** |
| **[MERT](https://arxiv.org/pdf/2306.00107)** | Music understanding | 95M-330M | "Well on local timbre like singer info" |
| [Jukebox](https://openai.com/index/jukebox/) | Music generation | 5B | Captures "timbre, pitch, volume" |
| Whisper | Speech transcription | 640M | ❌ Not designed for music |

From the [TokenSynth paper (2025)](https://arxiv.org/html/2502.08939.pdf):
> "To evaluate the pretrained CLAP model's ability to capture rich timbre information, they trained an MLP classifier on the extracted embeddings to classify **953 instruments, achieving 90.4% top-1 accuracy**."

### New Architecture

```
OLD (Frankenstein):
[Audio] → [Custom CNN] → [Mel-specs] → [Projection] → [Qwen + LoRA]
           (train)        (extract)      (train)        (fine-tune)

NEW (Industry-standard):
[Raw Audio] → [Frozen CLAP Encoder] → [Projection Layer] → [Qwen + LoRA]
               (pretrained)            (train, simple)      (fine-tune)
```

**What We Delete**:
- Custom CNN architecture (`cnn_audio_encoder.py`)
- Mel-spectrogram extraction pipeline
- 4-channel feature engineering (RMS, centroid, flatness)
- CNN training scripts

**What We Keep**:
- 108K rendered audio files (CLAP needs raw audio)
- Preset parameter database
- Q&A generation pipeline
- Qwen3-4B fine-tuning approach

### Implementation Resources

- [CLAP on HuggingFace](https://huggingface.co/docs/transformers/en/model_doc/clap)
- [SLAM-LLM Framework](https://github.com/X-LANCE/SLAM-LLM) - Purpose-built for CLAP → LLM integration
- [LAION-AI/CLAP](https://github.com/LAION-AI/CLAP) - Original implementation

**Status**: ✅ APPROVED - Pivot to CLAP-based architecture

---

## Decision 14: MixSpatialQA Dataset Format (Multi-Track Relational Understanding)
**Date**: 2025-11-30
**Decision**: Adapt SpatialAudio dataset format for music production context
**Inspiration**: [SLAM-LLM SpatialSoundQA](https://huggingface.co/datasets/zhisheng01/SpatialAudio)

### The Gap in Our Original Approach

Original approach taught: **"What does this single sound do?"**

What producers actually need: **"How do these sounds relate in a mix?"**

### SpatialAudio Format (Original)

```json
{
  "audio_id": "audioset_clip.wav",
  "reverb_id": "room_impulse.npy",
  "question": "Where is the dog barking?",
  "answer": "left, front, below; 1m",
  "question_type": "DOA"  // Direction of Arrival
}
```

### MixSpatialQA Format (Ours)

```json
{
  "audio_ids": ["kick_001.wav", "bass_dubstep_002.wav", "lead_saw_003.wav"],
  "plugin_chains": {
    "bass_dubstep_002": {
      "plugin": "Serum",
      "preset": "Heavy Wobble",
      "params": {"osc_a_vol": 0.8, "fil_cutoff": 0.45, "fil_driv": 0.7}
    },
    "lead_saw_003": {
      "plugin": "Compressor",
      "params": {"threshold": -18, "ratio": 4, "attack": 10}
    }
  },
  "mix_context": {
    "tempo": 140,
    "genre": "dubstep",
    "key": "F minor"
  },
  "question": "The bass is masking the kick in the low end. What parameter changes would help separation?",
  "answer": "Reduce fil_cutoff on the bass to 0.30 to carve out sub-100Hz headroom for the kick, or add sidechain compression triggered by the kick with 4:1 ratio and fast attack.",
  "question_type": "RELATIONSHIP"
}
```

### Question Types

| Type | SpatialAudio | MixSpatialQA |
|------|-------------|--------------|
| CLASSIFICATION | "What sound is this?" | "What type of sound is this?" |
| DOA | "Where is it in space?" | N/A |
| **RELATIONSHIP** | N/A | "How do these tracks interact?" |
| **CAUSATION** | N/A | "What happens if I change X?" |
| **RECOMMENDATION** | N/A | "What would help achieve Y?" |

### Dataset Components

| Priority | Component | Source | Volume |
|----------|-----------|--------|--------|
| 1 | Serum presets + audio | Already have | 108K samples |
| 2 | Ableton native plugins | Max for Live extraction | TBD |
| 3 | Multi-track relationships | Synthetic mixes | TBD |
| 4 | Before/after comparisons | Param variation renders | TBD |

**Status**: ✅ APPROVED - New dataset format for relational understanding

---

## Decision 15: Real-Time Streaming via Chunked CLAP Embeddings
**Date**: 2025-11-30
**Decision**: Pre-compute CLAP embeddings during playback, respond instantly on query
**Problem**: [TokenSynth limitation](https://arxiv.org/html/2502.08939.pdf) - "cannot perform real-time synthesis as it requires the complete MIDI sequence"

### The Real-Time Problem

For a production assistant to be useful, it must:
1. **Not block** - Can't wait for full 8-bar loop to finish
2. **Respond fast** - <200ms after user asks question
3. **Maintain context** - Remember what was playing

### Industry Solutions

From [Speech ReaLLM](https://arxiv.org/html/2406.09569v1):
> "Generate after every input token received in real time (it is often empty)"

From [Ultravox](https://github.com/fixie-ai/ultravox):
> "Extends any open-weight LLM with a multimodal projector that converts audio directly into the high-dimensional space used by the LLM... responds much more quickly than systems that combine separate ASR and LLM components"

### Our Solution: Chunked Context Windows

```
Instead of waiting:
[Full 8-bar loop plays] → [Encode entire loop] → [User asks] → [LLM responds]
                          ~~~~ 5-10 seconds ~~~~

Stream and cache:
[Bar 1 plays] → CLAP → Cache embedding₁
[Bar 2 plays] → CLAP → Append embedding₂
[Bar 3 plays] → CLAP → Append embedding₃
[User asks]   → [Cached embeddings₁₋₃ + question] → LLM → Response
              ~~~~ <200ms ~~~~
```

### Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ABLETON LIVE                                  │
│  ┌──────────────┐                                                   │
│  │  Audio Out   │──── 100ms chunks ────┐                           │
│  └──────────────┘                      │                           │
│                                        ▼                           │
│  ┌──────────────┐               ┌─────────────────┐                │
│  │  M4L Device  │◄──── WS ─────│  Python Server  │                │
│  │              │               │                 │                │
│  │  - UI        │               │  - CLAP Encoder │                │
│  │  - Controls  │               │  - Embedding    │                │
│  │              │               │    Cache        │                │
│  └──────────────┘               │  - Qwen + LoRA  │                │
│                                 └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────┘

Flow:
1. Audio chunks stream to Python server via WebSocket
2. CLAP encodes each chunk → stored in rolling cache
3. User asks question via M4L UI
4. Server combines cached embeddings + question → Qwen
5. Response (reasoning + actions) sent back to M4L
```

### Latency Budget

| Component | Target | Notes |
|-----------|--------|-------|
| Chunk encode (CLAP) | ~20ms | Pre-computed during playback |
| Cache lookup | ~1ms | In-memory |
| Projection | ~5ms | Simple linear layer |
| LLM inference | ~150ms | Qwen3-4B quantized |
| **Total on query** | **<200ms** | Meets real-time requirement |

**Status**: ✅ APPROVED - Chunked streaming architecture

---

## Decision 16: Expanded Data Collection (Ableton Native + VSTs)
**Date**: 2025-11-30
**Decision**: Extend dataset beyond Serum to include Ableton native plugins and other VSTs

### Rationale

User insight: "We should create a dataset using Ableton plugin presets via Max for Live parameter extraction for each plugin to teach the model to use those and VSTs like Serum"

A true collaborator needs to understand:
1. **Serum** (already have) - Wavetable synthesis
2. **Ableton Native Plugins** - EQ Eight, Compressor, Reverb, etc.
3. **Other VSTs** - Vital, Massive, etc. (future)

### Max for Live Parameter Extraction

```javascript
// M4L script to extract all device parameters
function extract_device_params(device) {
    var params = {};
    var param_count = device.get("parameters").length;

    for (var i = 0; i < param_count; i++) {
        var param = new LiveAPI("live_set tracks 0 devices 0 parameters " + i);
        params[param.get("name")] = {
            "value": param.get("value"),
            "min": param.get("min"),
            "max": param.get("max"),
            "default": param.get("default_value")
        };
    }
    return params;
}
```

### Dataset Expansion Plan

| Plugin Type | Method | Est. Presets | Priority |
|-------------|--------|--------------|----------|
| Serum | Already parsed | 7,583 | ✅ Done |
| EQ Eight | M4L extraction | ~50 factory | High |
| Compressor | M4L extraction | ~30 factory | High |
| Reverb | M4L extraction | ~100 factory | High |
| Auto Filter | M4L extraction | ~50 factory | Medium |
| Saturator | M4L extraction | ~40 factory | Medium |
| Vital | VST3 parsing | ~500 factory | Future |

### Before/After Comparison Data

For each plugin, render:
1. **Dry audio** (bypass)
2. **Wet audio** with preset X
3. **Wet audio** with varied parameters

This teaches the model: "When you turn up the ratio on a compressor, THIS is what happens to the audio"

**Status**: ✅ APPROVED - Multi-plugin dataset expansion

---

## Summary: The CLAP Pivot

### What Changed

| Aspect | Before (Decisions 1-12) | After (Decisions 13-16) |
|--------|------------------------|------------------------|
| Audio Encoder | Custom CNN (train from scratch) | Frozen CLAP (pretrained) |
| Features | Mel-spectrograms + RMS/centroid/flatness | Raw audio → CLAP embeddings |
| Dataset Focus | Single sounds | Multi-track relationships |
| Real-time | Not addressed | Chunked streaming cache |
| Plugin Coverage | Serum only | Serum + Ableton native + VSTs |

### What Stays the Same

- Qwen3-4B as base LLM
- LoRA fine-tuning approach
- Tiered Q&A generation (Haiku/Sonnet/Opus)
- Collaborator response format (reasoning + actions + explanation)
- WebSocket M4L ↔ Python architecture
- <200ms inference target

### Files to Archive (move to `/old`)

- `cnn_audio_encoder.py` → `old/cnn_audio_encoder_v1.py`
- `mel_spectrogram_pipeline.py` → `old/mel_spectrogram_pipeline_v2.py`
- `train_cnn.py` → `old/train_cnn_v1.py`
- `serum_dataset.py` → `old/serum_dataset_v1.py`

### New Files to Create

- `clap_encoder.py` - CLAP embedding extraction
- `projection_layer.py` - Simple CLAP → LLM projection
- `mix_spatial_dataset.py` - New dataset format
- `streaming_cache.py` - Real-time embedding cache
- `m4l_param_extractor/` - Max for Live device scripts

---

---

## Decision 17: MixGraph-CLAP Architecture for Multi-Track Mix Representation
**Date**: 2025-12-02
**Decision**: Use a hybrid 4-stage architecture to represent full mixes as continuous embeddings for LLM reasoning
**Trigger**: Need to represent instruments, arrangement, stereo field, and frequency relationships in a way an LLM can reason about

### The Core Challenge

We need to encode into continuous embeddings:
- **Multiple sources** (kick, bass, synths, vocals, etc.)
- **Frequency content** per source
- **Stereo position** (panning)
- **Temporal/arrangement context** (section type)
- **Inter-track relationships** (masking, harmonic interaction)

### Research Survey Results

| Approach | Paper | Key Innovation | Fit for Us |
|----------|-------|----------------|------------|
| **Spatial-CLAP** | [arxiv:2509.14785](https://arxiv.org/html/2509.14785) | Content-aware spatial encoder + Spatial Contrastive Learning for multi-source | HIGH |
| **MEGAMI** | [arxiv:2511.08040](https://arxiv.org/html/2511.08040) | Effect embeddings via FxEncoder++, permutation-equivariant transformer | HIGH |
| **DMC** | [arxiv:2010.10291](https://ar5iv.labs.arxiv.org/html/2010.10291) | Context embedding = average(all track embeddings) | MEDIUM |
| **PyramidCodec** | [EMNLP 2024](https://aclanthology.org/2024.findings-emnlp.246.pdf) | Hierarchical multi-scale features | MEDIUM |
| **GNN for Audio** | [Warwick](https://wrap.warwick.ac.uk/176718/) | Graph structure for audio classification, GAT 91% accuracy | MEDIUM |
| **Multi-Track LDM** | [arxiv:2409.12346](https://arxiv.org/abs/2409.12346) | Joint probability distribution of tracks sharing musical context | LOW (generation focus) |

### Key Findings from Research

**1. Spatial-CLAP (September 2025)** - Most relevant
- Extends CLAP for multi-source spatial audio
- Uses **Content-Aware Spatial Encoder (CA-SE)** that couples content with spatial position
- **Spatial Contrastive Learning (SCL)** with hard negatives (permuted source-location pairs)
- Handles 3+ sources in mixtures
- Code available: `github.com/sarulab-speech/SpatialCLAP`

**2. MEGAMI (November 2024)** - Effect embedding approach
- Disentangles **effect characteristics from musical content** using FxEncoder++
- Effect embeddings include: log-RMS, crest factor, dynamic spread, stereo width, stereo imbalance
- **Permutation-equivariant transformer** handles variable track counts
- Captures multimodal distribution of valid mixes (not just one "right" answer)

**3. DMC Context Embedding** - Simple but effective
- Each track gets: `[track_embedding || context_embedding]`
- Context = average of all track embeddings
- Gives each processor awareness of whole mix
- Sum/difference transform for stereo invariance

### Proposed Architecture: MixGraph-CLAP

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIXGRAPH-CLAP ENCODER                        │
│            (4-Stage Hybrid Architecture)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: Stereo mix + (optional) stems                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STAGE 1: Per-Track Embedding (Spatial-CLAP inspired)    │   │
│  │                                                         │   │
│  │  Each track → [Content Enc || Spatial Enc] → MLP        │   │
│  │  Output: Per-track embedding with spatial info          │   │
│  │  Dimension: 768 (content) + 256 (spatial) → 512 (MLP)   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STAGE 2: Relationship Graph (GNN)                       │   │
│  │                                                         │   │
│  │  • Nodes = track embeddings from Stage 1                │   │
│  │  • Edges = computed relationships:                      │   │
│  │    - Spectral overlap (masking score, 0-1)              │   │
│  │    - Stereo correlation (L/R similarity)                │   │
│  │    - RMS difference (volume relationship)               │   │
│  │    - Harmonic consonance (frequency ratios)             │   │
│  │  • GAT layers → contextualized track embeddings         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STAGE 3: Hierarchical Pooling                           │   │
│  │                                                         │   │
│  │  • Frame-level: fine-grained temporal info              │   │
│  │  • Section-level: pool frames within sections           │   │
│  │  • Song-level: pool sections                            │   │
│  │  • Preserve all levels for different query types        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STAGE 4: Context Embedding (DMC inspired)               │   │
│  │                                                         │   │
│  │  Mix-wide context = Attention-pooled(all tracks)        │   │
│  │  Each track gets: [track_emb || context_emb]            │   │
│  │  Enables: "This bass relative to THIS mix"              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         ↓                                       │
│  OUTPUT TO LLM:                                                 │
│  • Per-track contextualized embeddings (N × 512)                │
│  • Mix-wide embedding (512)                                     │
│  • Section-level embeddings (S × 512)                           │
│  • Computed metrics (RMS, stereo width, masking scores)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Edge Features for Track Relationship Graph

| Feature | Computation | Range | Purpose |
|---------|-------------|-------|---------|
| **Spectral Overlap** | Cosine sim of mel bands | [0, 1] | Masking detection |
| **Stereo Correlation** | Pearson(L, R) per track | [-1, 1] | Mono vs stereo width |
| **RMS Ratio** | dB difference | [-inf, +inf] | Volume balance |
| **Harmonic Consonance** | Pitch class histogram correlation | [0, 1] | Key/harmony clash |
| **Temporal Sync** | Cross-correlation peak | [0, 1] | Rhythmic alignment |

### Phased Implementation Plan

#### Phase 1: Start Simple (Current Priority)
```python
# CLAP per-track + computed features + context embedding
class Phase1MixEncoder:
    def __init__(self):
        self.clap = ClapModel.from_pretrained("laion/clap-htsat-unfused")
        self.projector = nn.Linear(512 + NUM_COMPUTED_FEATURES, 512)

    def encode_mix(self, tracks: List[Tensor]) -> Dict:
        # Per-track CLAP embeddings
        track_embs = [self.clap.get_audio_features(t) for t in tracks]

        # Computed relationship features
        masking = compute_spectral_overlap(tracks)
        stereo = compute_stereo_correlation(tracks)
        rms = compute_rms_ratios(tracks)

        # Context embedding (simple average)
        context = torch.mean(torch.stack(track_embs), dim=0)

        # Concatenate each track with context + features
        outputs = []
        for i, emb in enumerate(track_embs):
            features = torch.cat([masking[i], stereo[i], rms[i]])
            combined = torch.cat([emb, context, features])
            outputs.append(self.projector(combined))

        return {
            'track_embeddings': torch.stack(outputs),
            'mix_embedding': context,
            'computed_features': {'masking': masking, 'stereo': stereo, 'rms': rms}
        }
```

#### Phase 2: Add Spatial Awareness
- Integrate **Spatial-CLAP** when stable/released
- Replace vanilla CLAP with content-aware spatial encoder
- Train on synthetic multi-track data with known spatial positions

#### Phase 3: Add Graph Structure
- Build **GNN layer** on top of track embeddings
- Use **GAT (Graph Attention)** for relationship-aware embeddings
- Edge features from computed metrics

#### Phase 4: Hierarchical Structure
- Add **section-level pooling** using msaf segmentation
- Train on SALAMI-annotated data
- Enable arrangement-aware reasoning ("in the drop, do X")

### Comparison to Alternatives

| Approach | Spatial | Relationships | Arrangement | Complexity | Our Choice |
|----------|---------|---------------|-------------|------------|------------|
| Raw CLAP only | ❌ | ❌ | ❌ | Low | Phase 0 |
| CLAP + computed features | Partial | ✅ | ❌ | Low | **Phase 1** |
| Spatial-CLAP | ✅ | Partial | ❌ | Medium | Phase 2 |
| Full MixGraph-CLAP | ✅ | ✅ | ✅ | High | Phase 3-4 |

### Why Not Just Use Spatial-CLAP Directly?

1. **Designed for localization** - "Where is the dog barking?" not "Why are bass and kick masking?"
2. **No arrangement awareness** - Doesn't know verse from drop
3. **No explicit relationship features** - We need masking scores, not just positions
4. **But**: We borrow the content-aware spatial encoding idea

### Why GNN for Track Relationships?

From [Graph-Based Audio Classification](https://pmc.ncbi.nlm.nih.gov/articles/PMC11014159/):
> "The GAT model emerged as the top performer, achieving 91% in classifying environmental sounds and 91% in identifying land cover based on audio recordings."

GNN advantages:
- **Explicit edge features** for relationships
- **Variable track count** handled naturally
- **Attention over relationships** (not just track features)
- **Proven on audio** classification tasks

### Status: ✅ APPROVED

- Phase 1: Implement immediately (CLAP + computed features + context)
- Phase 2-4: Iterate based on Phase 1 results

---

## Research Sources (Decision 17)

### Multi-Track Mixing Embeddings
- [Spatial-CLAP](https://arxiv.org/html/2509.14785) - Multi-source spatial audio embeddings
- [MEGAMI](https://arxiv.org/html/2511.08040) - Effect embeddings for automatic mixing
- [Differentiable Mixing Console](https://ar5iv.labs.arxiv.org/html/2010.10291) - Track + context embeddings

### Hierarchical Audio Representations
- [PyramidCodec](https://aclanthology.org/2024.findings-emnlp.246.pdf) - Multi-scale hierarchical features
- [Self-Supervised Multi-Level Audio](https://dl.acm.org/doi/10.1109/TASLP.2024.3379894) - Coarse/fine segmentation

### Graph Neural Networks for Audio
- [Graph-Based Audio Classification](https://pmc.ncbi.nlm.nih.gov/articles/PMC11014159/) - GAT for audio
- [GNN for Audio Representation Learning](https://wrap.warwick.ac.uk/176718/) - Graph structure for audio

### Source Separation & Multi-Track
- [Multi-Track Latent Diffusion](https://arxiv.org/abs/2409.12346) - Joint track distributions
- [CLAPSep](https://arxiv.org/html/2402.17455v3) - Query-conditioned target sound extraction
- [Text2FX](https://arxiv.org/abs/2409.18847) - CLAP embeddings for audio effects

---

## Decision 18: Self-Play RL Training Strategy (Future Phase)
**Date**: 2025-12-02
**Decision**: Plan for multi-step reasoning + self-play RL in later phases, after supervised learning validation
**Inspiration**: Noam Brown's work on poker (Libratus/Pluribus), Diplomacy (CICERO), and OpenAI o1

### The Core Insight

User observation: "One of the best ways to learn to play music or mix music is to just mess around until you have a sense of what sounds good."

This maps directly to self-play reinforcement learning:
- **Poker/Diplomacy**: Learn by playing thousands of games against yourself
- **Music Production**: Learn by making thousands of mixing decisions and hearing the results

From [Noam Brown](https://noambrown.github.io/) (OpenAI, previously Meta AI):
> "In all of the domains I'd worked on—poker, Hanabi, and diplomacy—having the models think before acting made a huge difference in performance, like orders of magnitude difference. Like a thousand to a hundred thousand times."

### Why This Applies to Mixing

| Poker | Music Production |
|-------|------------------|
| Imperfect information (hidden cards) | Imperfect information (what does "punchy" mean?) |
| Multi-step reasoning (if I bet, they might fold...) | Multi-step reasoning (if I cut 200Hz, the kick might get lost...) |
| No single "right" answer | No single "right" mix |
| Learn by playing thousands of hands | Learn by "messing around" with thousands of mixes |

### The Self-Play Loop for Mixing

```
┌─────────────────────────────────────────────────────────────────┐
│                    SELF-PLAY MIXING LOOP                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. START: Raw stems (kick, bass, synth, vocal)                │
│                                                                 │
│  2. MODEL PROPOSES ACTION                                       │
│     "Cut 200Hz on bass by 3dB"                                 │
│                                                                 │
│  3. APPLY ACTION (via Ableton/plugin automation)               │
│     Bass track EQ → 200Hz, -3dB                                │
│                                                                 │
│  4. RENDER NEW MIX                                             │
│     Export audio with applied change                           │
│                                                                 │
│  5. EVALUATE (Reward Model)                                    │
│     ┌─────────────────────────────────────────┐                │
│     │ • Computed: Spectral overlap decreased? │                │
│     │ • Computed: RMS balance improved?       │                │
│     │ • Learned: Does this sound "better"?    │                │
│     └─────────────────────────────────────────┘                │
│                                                                 │
│  6. UPDATE POLICY                                              │
│     Good outcome → reinforce this action                       │
│     Bad outcome → reduce probability                           │
│                                                                 │
│  7. REPEAT (thousands of iterations)                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Compute Requirements Analysis

**Per-cycle timing (estimated)**:
| Step | Time | Notes |
|------|------|-------|
| Render audio | ~0.5-2s | Ableton offline, or pedalboard ~50ms |
| CLAP encode | ~20-50ms | M4 Max |
| Compute reward | ~10ms | Spectral analysis |
| Forward pass | ~100-200ms | Qwen 4-bit |
| Backward pass | ~500ms-2s | RL gradient update |
| **Total** | **~2-5 seconds** | |

**Scale requirements**:
| Scale | Cycles | Time (Local M4) | Time (A100) | Cloud Cost |
|-------|--------|-----------------|-------------|------------|
| Toy experiment | 1,000 | ~1-2 hrs | ~15 min | ~$2 |
| Proof of concept | 10,000 | ~10-20 hrs | ~2 hrs | ~$10 |
| Reasonable RL | 100,000 | ~4-7 days | ~20 hrs | ~$50-100 |
| Serious training | 1,000,000 | ~40-70 days | ~8 days | ~$300-500 |
| MusicRL (Google) | Millions | Cluster | TPU pods | $$$$ |

### Local (M4 Max) Limitations

1. **No CUDA** - Most RL libraries optimized for NVIDIA
2. **MPS incomplete** - PyTorch MPS doesn't support all RL ops
3. **Ableton bottleneck** - Can't parallelize rendering easily
4. **But**: Good enough for ~5-10K cycles as proof of concept

### Reward Model Options

| Reward Type | Pros | Cons | Priority |
|-------------|------|------|----------|
| **Spectral overlap reduction** | Computed, objective | Doesn't capture "vibe" | HIGH |
| **RMS balance improvement** | Computed, fast | Genre-dependent | HIGH |
| **LUFS/dynamic range** | Industry standard | Not always the goal | MEDIUM |
| **A/B human preference** | Gold standard | Expensive, slow | LOW |
| **Trained reward model** | Scales | Needs preference data | FUTURE |

### Alternative: Pedalboard for Fast Rendering

Instead of Ableton, use Spotify's `pedalboard` for 100x faster rendering:

```python
import pedalboard
from pedalboard import Compressor, Reverb, HighpassFilter

def apply_action_and_render(audio, action):
    board = pedalboard.Pedalboard([
        HighpassFilter(cutoff_frequency_hz=action['hp_freq']),
        Compressor(threshold_db=action['comp_thresh']),
    ])
    return board(audio, sample_rate=48000)
```

**Advantages**: Fast, parallelizable, cloud-compatible
**Disadvantages**: Limited plugins (no Serum), less realistic

### Phased Implementation Plan

#### Phase 1-2: Supervised Learning (Current Priority)
- Train on Q&A pairs with reasoning traces
- No RL yet - just learning the mapping
- **Compute**: Local M4 Max, $0

#### Phase 2.5: RL Proof of Concept (After Phase 2)
- ~5,000-10,000 cycles locally
- Use `pedalboard` for fast rendering
- Computed reward metrics only
- **Compute**: Local M4 Max, $0 + time

#### Phase 3: RL Fine-Tuning (If Phase 2.5 works)
- Rent A100 for 1-2 days
- Run 100K+ cycles
- Train proper reward model
- **Compute**: Cloud, ~$50-100

#### Phase 4: Full Self-Play (Ambitious, Optional)
- Full self-play with learned reward model
- Multiple "critics" debating mix decisions
- Similar to CICERO's dialogue + planning
- **Compute**: Cloud, ~$200-500

### Key Research References

**Noam Brown's Work**:
- [Libratus/Pluribus](https://www.semanticscholar.org/paper/Superhuman-AI-for-multiplayer-poker-Brown-Sandholm/2ee463bba9d4db6aec0eab17e54431a6dc80bf17) - Poker AI
- [CICERO (Diplomacy)](https://arxiv.org/abs/2210.05492) - Self-play RL + LLM dialogue
- [Latent Space Interview](https://www.latent.space/p/noam-brown) - Test-time compute insights

**Test-Time Compute / o1**:
- [OpenAI o1](https://openai.com/index/learning-to-reason-with-llms/) - Multi-step reasoning
- [Test-Time Compute Scaling](https://huggingface.co/blog/Kseniase/testtimecompute) - How it works

**Music RL**:
- [MusicRL (Google)](https://arxiv.org/abs/2402.04229) - RLHF for music generation
- [RaveForce](https://smc2019.uma.es/articles/P2/P2_01_SMC2019_paper.pdf) - RL environment for music

### Decision Summary

| Phase | Approach | Compute | Cost |
|-------|----------|---------|------|
| 1-2 | Supervised + reasoning traces | Local | $0 |
| 2.5 | RL proof of concept | Local | $0 |
| 3 | RL fine-tuning | Cloud A100 | ~$50-100 |
| 4 | Full self-play | Cloud | ~$200-500 |

**Status**: ✅ APPROVED as future roadmap - Focus on Phase 1-2 first, validate before scaling

---

## Decision 19: Baseline Evaluation Harness (IMMEDIATE PRIORITY)
**Date**: 2025-12-03
**Decision**: Build comprehensive eval harness BEFORE fine-tuning to establish baselines and enable continuous evaluation
**Priority**: CRITICAL - Must complete before any fine-tuning begins

### Why This Is Critical

1. **Without baselines, we can't prove improvement**
   - How do we know fine-tuning helped?
   - Need before/after comparison on same eval set

2. **Eval harness serves multiple purposes**
   - Pre-fine-tuning: Establish baseline capabilities
   - Post-fine-tuning: Measure improvement
   - Real-world: Production quality checks
   - Self-play RL: Reward signal source

3. **Industry standard practice**
   - Every serious ML project has eval before training
   - Prevents "training on test set" accidents
   - Enables ablation studies

### Evaluation Dimensions

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EVALUATION HARNESS ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DIMENSION A: MUSIC PRODUCTION KNOWLEDGE                                │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │  A1. Parameter Understanding (MCQ)                         │         │
│  │      "What does filter cutoff control?"                    │         │
│  │                                                            │         │
│  │  A2. Sound Description (Open-ended)                        │         │
│  │      "Describe the character of this wavetable position"   │         │
│  │                                                            │         │
│  │  A3. Genre Conventions (Scenario)                          │         │
│  │      "What makes a dubstep bass sound heavy?"              │         │
│  └───────────────────────────────────────────────────────────┘         │
│                                                                         │
│  DIMENSION B: MULTI-TRACK REASONING                                     │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │  B1. Relationship Identification                           │         │
│  │      "Which tracks are conflicting in this mix?"           │         │
│  │                                                            │         │
│  │  B2. Causal Reasoning                                      │         │
│  │      "Why is the kick getting lost in the drop?"           │         │
│  │                                                            │         │
│  │  B3. Section-Aware Analysis                                │         │
│  │      "Why does bass sound good in verse but muddy in drop?"│         │
│  └───────────────────────────────────────────────────────────┘         │
│                                                                         │
│  DIMENSION C: ACTIONABLE RECOMMENDATIONS                                │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │  C1. Parameter Adjustment                                  │         │
│  │      "What value should filter cutoff be?"                 │         │
│  │                                                            │         │
│  │  C2. Effect Chain Suggestions                              │         │
│  │      "What processing chain would help this vocal?"        │         │
│  │                                                            │         │
│  │  C3. Tool Calling Accuracy                                 │         │
│  │      Can model correctly format parameter changes?         │         │
│  └───────────────────────────────────────────────────────────┘         │
│                                                                         │
│  DIMENSION D: AUDIO GROUNDING (Requires CLAP integration)               │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │  D1. Audio → Text Description                              │         │
│  │      Given audio embedding, describe the sound             │         │
│  │                                                            │         │
│  │  D2. Audio Comparison                                      │         │
│  │      "Which of these sounds brighter?"                     │         │
│  │                                                            │         │
│  │  D3. Mix Analysis                                          │         │
│  │      "What issues exist in this multi-track mix?"          │         │
│  └───────────────────────────────────────────────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Eval Dataset Composition

| Category | Subcategory | Questions | Source | Scoring |
|----------|-------------|-----------|--------|---------|
| **A1** | Parameter MCQ | 50 | Serum manual + presets | Accuracy |
| **A2** | Sound Description | 30 | Expert written | LLM-as-Judge |
| **A3** | Genre Conventions | 30 | Research + expert | LLM-as-Judge |
| **B1** | Relationship ID | 40 | ArrangementMixQA | Accuracy + F1 |
| **B2** | Causal Reasoning | 30 | ArrangementMixQA | LLM-as-Judge |
| **B3** | Section-Aware | 30 | ArrangementMixQA | LLM-as-Judge |
| **C1** | Parameter Adj | 40 | Serum presets | MAE on values |
| **C2** | Effect Chains | 20 | Expert written | LLM-as-Judge |
| **C3** | Tool Calling | 30 | Synthetic | Exact match |
| **D1-D3** | Audio Grounded | 50 | With embeddings | Multiple |
| **TOTAL** | | **350** | | |

### Scoring Methods

```python
class EvalScorer:
    """Multi-method scoring for different question types."""

    def score_mcq(self, prediction: str, answer: str) -> float:
        """Exact match for multiple choice."""
        return 1.0 if prediction.strip().upper() == answer.strip().upper() else 0.0

    def score_parameter(self, pred_value: float, true_value: float) -> float:
        """MAE for continuous parameters (normalized 0-1)."""
        return 1.0 - abs(pred_value - true_value)

    def score_tool_call(self, pred_json: dict, true_json: dict) -> float:
        """Structured match for tool calls."""
        # Check tool name, parameter names, value ranges
        ...

    async def score_llm_judge(self, question: str, prediction: str,
                              reference: str, rubric: str) -> float:
        """Use Claude as judge for open-ended questions."""
        prompt = f"""
        Question: {question}
        Reference Answer: {reference}
        Model Answer: {prediction}
        Rubric: {rubric}

        Score the model answer from 0-10 based on:
        - Correctness of music production concepts
        - Actionability of recommendations
        - Appropriate reasoning shown

        Return ONLY a number 0-10.
        """
        response = await claude_client.messages.create(...)
        return float(response.content[0].text) / 10.0
```

### Baseline Models to Evaluate

| Model | Size | Notes |
|-------|------|-------|
| **Qwen3-4B** (base) | 4B | Our target model, pre-fine-tuning |
| Qwen3-4B + audio | 4B | With CLAP embeddings, pre-fine-tuning |
| Claude 3.5 Sonnet | ~200B | Upper bound reference |
| GPT-4o | ~200B | Upper bound reference |
| Phi-4-mini | 3.8B | Alternative small model |

### Eval Harness Implementation

```python
# eval/mix_eval_harness.py

class MixProductionEvalHarness:
    """Comprehensive eval harness for music production AI."""

    def __init__(self, model_backend: str, eval_dataset_path: str):
        self.backend = self._init_backend(model_backend)
        self.dataset = self._load_eval_dataset(eval_dataset_path)
        self.scorer = EvalScorer()

    async def run_full_eval(self, output_path: str) -> EvalReport:
        """Run complete evaluation across all dimensions."""
        results = {}

        # Dimension A: Music Production Knowledge
        results['A'] = await self._eval_dimension_a()

        # Dimension B: Multi-Track Reasoning
        results['B'] = await self._eval_dimension_b()

        # Dimension C: Actionable Recommendations
        results['C'] = await self._eval_dimension_c()

        # Dimension D: Audio Grounding (if embeddings provided)
        if self.has_audio_embeddings:
            results['D'] = await self._eval_dimension_d()

        report = self._generate_report(results)
        report.save(output_path)
        return report

    def compare_models(self, *eval_reports: EvalReport) -> ComparisonReport:
        """Generate comparison across multiple model evaluations."""
        ...
```

### Integration with Self-Play RL

The eval harness directly feeds into the self-play RL reward model:

```
┌─────────────────────────────────────────────────────────────────┐
│                  EVAL → RL INTEGRATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Eval Harness                    Self-Play RL                   │
│  ┌─────────────┐                ┌─────────────────┐            │
│  │ Dimension C │───────────────▶│  Action Quality │            │
│  │ (Tool Calls)│                │  Reward Signal  │            │
│  └─────────────┘                └─────────────────┘            │
│                                                                 │
│  ┌─────────────┐                ┌─────────────────┐            │
│  │ Dimension B │───────────────▶│  Reasoning      │            │
│  │ (Reasoning) │                │  Quality Score  │            │
│  └─────────────┘                └─────────────────┘            │
│                                                                 │
│  ┌─────────────┐                ┌─────────────────┐            │
│  │ Dimension D │───────────────▶│  Audio-Grounded │            │
│  │ (Audio)     │                │  Reward Signal  │            │
│  └─────────────┘                └─────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Existing Eval Resources to Leverage

We already have:
1. `eval/music_production_eval_v2.json` - 100 questions from Decision 6
2. `eval/serum_parameter_eval.json` - 30 Serum-specific questions
3. `eval/run_eval.py` - Basic MLX eval runner

**Need to extend**:
- Add multi-track reasoning questions (Dimension B)
- Add audio-grounded questions with embeddings (Dimension D)
- Add LLM-as-Judge scoring
- Add baseline comparison reporting

### Implementation Priority

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Extend eval dataset with B, C, D questions | HIGH | Medium | ArrangementMixQA schema |
| Implement LLM-as-Judge scoring | HIGH | Low | Claude API |
| Run baseline on Qwen3-4B (text only) | HIGH | Low | Existing eval |
| Add CLAP embedding integration | MEDIUM | Medium | mix_encoder.py |
| Create comparison report generator | MEDIUM | Low | Baseline results |
| Integrate with RL reward pipeline | LOW | Medium | After RL phase |

### Success Criteria

Before fine-tuning begins:
- [ ] 350+ eval questions across all dimensions
- [ ] Baseline scores for Qwen3-4B on Dimensions A, B, C
- [ ] Upper bound scores from Claude/GPT-4 on same questions
- [ ] Reproducible eval harness script

After fine-tuning:
- [ ] Demonstrate >10% improvement on Dimensions A, B, C
- [ ] No regression on any dimension
- [ ] Improvement correlates with training data coverage

**Status**: ✅ APPROVED - Immediate next step before any fine-tuning

---

## Research Sources

- [Audio Language Models and Multimodal Architecture](https://medium.com/@prdeepak.babu/audio-language-models-and-multimodal-architecture-1cdd90f46fac)
- [Qwen2-Audio Technical Report](https://arxiv.org/html/2407.10759v1)
- [SLAM-LLM Framework](https://github.com/X-LANCE/SLAM-LLM)
- [Ultravox Real-time Voice](https://github.com/fixie-ai/ultravox)
- [LAION CLAP](https://github.com/LAION-AI/CLAP)
- [TokenSynth (2025)](https://arxiv.org/html/2502.08939.pdf)
- [MERT Music Understanding](https://arxiv.org/pdf/2306.00107)
- [Speech ReaLLM](https://arxiv.org/html/2406.09569v1)
- [SpatialSoundQA Dataset](https://huggingface.co/datasets/zhisheng01/SpatialAudio)
- [Sebastian Raschka - Understanding Multimodal LLMs](https://magazine.sebastianraschka.com/p/understanding-multimodal-llms)
