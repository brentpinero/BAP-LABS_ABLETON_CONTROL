# QUICK REFERENCE: KEY RESOURCES & RESEARCH TOPICS

This document provides a quick reference to the most important resources, papers, and repositories mentioned in the ML_Training.md roadmap. Use this as a research starting point.

---

## 📊 CLAUDE API PRICING REFERENCE (2025)

### Model Pricing (per 1M tokens)
| Model | Input | Output | Batch Input (50% off) | Batch Output (50% off) |
|-------|-------|--------|----------------------|------------------------|
| **Haiku 3.5** | $0.80 | $4.00 | $0.40 | $2.00 |
| **Haiku 4.5** | $1.00 | $5.00 | $0.50 | $2.50 |
| **Sonnet 4.5** | $3.00 | $15.00 | $1.50 | $7.50 |
| **Opus 4.5** | $15.00 | $75.00 | $7.50 | $37.50 |

### Batch API Details
- **Discount**: 50% on ALL models (including Opus)
- **Processing Time**: Usually <1 hour, up to 24 hours max
- **Limits**: 100K requests or 256MB per batch
- **Results**: Valid for 29 days
- **Tradeoff**: No real-time responses, no streaming

**Documentation**: [Batch Processing - Claude Docs](https://platform.claude.com/docs/en/build-with-claude/batch-processing)

### Our Tiered Q&A Generation Strategy
| Tier | Model | Task Complexity | Est. 10K Q&A Cost |
|------|-------|-----------------|-------------------|
| 1 | Haiku 3.5 | Simple (40%) | ~$3.60 |
| 2 | Sonnet 4.5 | Medium (45%) | ~$20.25 |
| 3 | Opus 4.5 | Complex (15%) | ~$20.25 |
| **Total** | **Tiered** | **Optimized** | **~$44.10** |

See: [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md#decision-7-tiered-llm-qa-generation-strategy)

---

## 🎯 CRITICAL GITHUB REPOSITORIES

### Audio ML Models (Study These First)
| Repository | What to Learn | Priority |
|------------|---------------|----------|
| [github.com/LAION-AI/CLAP](https://github.com/LAION-AI/CLAP) | Audio-text embeddings (512-dim), contrastive learning | ⭐⭐⭐ HIGH |
| [github.com/acids-ircam/RAVE](https://github.com/acids-ircam/RAVE) | Real-time VAE audio synthesis (20x faster than real-time) | ⭐⭐⭐ HIGH |
| [github.com/facebookresearch/audiocraft](https://github.com/facebookresearch/audiocraft) | MusicGen, EnCodec - production audio generation | ⭐⭐⭐ HIGH |
| [github.com/magenta/ddsp](https://github.com/magenta/ddsp) | Differentiable synthesis, parameter prediction patterns | ⭐⭐⭐ HIGH |
| [github.com/lucidrains/audiolm-pytorch](https://github.com/lucidrains/audiolm-pytorch) | Hierarchical audio tokenization (semantic + acoustic) | ⭐⭐ MEDIUM |

### Transformer Fundamentals
| Repository | What to Learn | Priority |
|------------|---------------|----------|
| [github.com/karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) | GPT in ~600 lines - transformer fundamentals | ⭐⭐⭐ HIGH |
| [github.com/karpathy/micrograd](https://github.com/karpathy/micrograd) | Backpropagation engine in ~150 lines | ⭐⭐ MEDIUM |

### Plugin/Integration
| Repository | What to Learn | Priority |
|------------|---------------|----------|
| [github.com/neutone/neutone-sdk](https://github.com/neutone/neutone-sdk) | Deploy PyTorch models as VST plugins | ⭐⭐⭐ HIGH |
| [github.com/anira-project/anira](https://github.com/anira-project/anira) | Thread-safe real-time inference | ⭐⭐ MEDIUM |

---

## 📄 ESSENTIAL PAPERS TO READ

### Foundational (Must Read)
1. **"Attention Is All You Need"** (Vaswani et al., 2017)
   - Original transformer architecture
   - Self-attention mechanism
   - Read with: [jalammar.github.io/illustrated-transformer](https://jalammar.github.io/illustrated-transformer/)

2. **"FlashAttention"** (Dao et al., 2022)
   - IO-aware attention optimization
   - Enables longer context windows efficiently

### Audio ML (Domain-Specific)
3. **"AudioLM"** (Borsos et al., 2022)
   - Hierarchical audio generation (semantic + acoustic tokens)
   - Why this decomposition works

4. **"MusicGen"** (Copet et al., 2023)
   - Single-stage transformer for music
   - Codebook interleaving patterns

5. **"CLAP: Learning Audio Concepts from Natural Language Supervision"** (LAION)
   - Contrastive audio-text learning
   - How to align modalities

6. **"Music Transformer"** (Huang et al., 2018)
   - Relative attention for music structure
   - MIDI generation with long-term coherence

### Parameter Prediction (Directly Relevant)
7. **"InverSynth"** 
   - CNN-based audio → synth parameter prediction
   - The reference architecture for our use case

8. **"DDSP: Differentiable Digital Signal Processing"** (Engel et al., 2020)
   - Making synthesis differentiable
   - Parameter prediction via gradient descent

### Knowledge Distillation (For LLM Phase)
9. **"Distilling the Knowledge in a Neural Network"** (Hinton et al., 2015)
   - Foundation of knowledge distillation
   - Teacher-student training

10. **"DistilBERT"** (Sanh et al., 2019)
    - Practical distillation of large LLMs
    - 40% smaller, 60% faster, 97% performance

---

## 🎓 LEARNING COURSES & TUTORIALS

### Video Courses
1. **Andrej Karpathy: Neural Networks Zero to Hero**
   - URL: [karpathy.ai/zero-to-hero.html](https://karpathy.ai/zero-to-hero.html)
   - 8 videos, ~13 hours total
   - Build transformers from scratch

2. **Hugging Face Audio Course**
   - URL: [huggingface.co/learn/audio-course](https://huggingface.co/learn/audio-course)
   - Units 1-3: Audio representations, transformers for audio
   - Free, hands-on

### Written Guides
3. **The Illustrated Transformer**
   - URL: [jalammar.github.io/illustrated-transformer](https://jalammar.github.io/illustrated-transformer/)
   - Visual explanations of attention, transformers

4. **The Annotated Transformer**
   - URL: [nlp.seas.harvard.edu/2018/04/03/attention.html](https://nlp.seas.harvard.edu/2018/04/03/attention.html)
   - Line-by-line transformer implementation

---

## 🔬 KEY RESEARCH QUESTIONS FOR EACH PHASE

### Phase 2: CNN Design
**Questions to research:**
- What mel-spectrogram config works best for synth sounds? (n_mels, n_fft, hop_length)
- InverSynth architecture details - what conv layers did they use?
- DDSP parameter prediction - how many parameters can CNNs predict accurately?
- ResNet vs plain CNN for spectrograms?

**Where to look:**
- InverSynth paper (audio → synth parameters)
- DDSP GitHub (spectral loss functions)
- Audio spectrogram literature (mel-spec best practices)

### ✅ RESOLVED: Small LLM Selection
**Decision**: Qwen3-4B (4-bit MLX)
**Date**: 2025-11-28

**Evaluation Results**:
- Tested 6 models with custom MLX eval harness + Claude Sonnet 4.5 as judge
- Qwen3-4B: 100/240 (41.7%) music production, 35/70 (50%) Serum-specific
- 2x better than second place (Phi-4-mini-reasoning at 21.7%)

**Key Findings**:
- Strong conceptual knowledge (80% on parameter ID MCQ)
- Weak on practical application (30% on parameter adjustment) ← Fine-tuning target
- Native thinking token support enables reasoning traces
- 4-bit quantized version available in MLX community

**Next Phase**: Dataset curation for fine-tuning

### Phase 3: CNN → LLM Distillation
**Questions to research:**
- How to convert CNN embeddings into LLM training data?
- Multi-modal fusion strategies (concatenation, adapters, cross-attention)
- Knowledge distillation for audio domains
- LoRA/QLoRA for small model fine-tuning

**Where to look:**
- Knowledge distillation literature
- Multi-modal LLM papers (CLIP, Flamingo)
- Audio-language models (CLAP architecture)

### Phase 4: Iterative Reasoning
**Questions to research:**
- ReAct pattern implementation
- Chain-of-thought for parameter adjustment
- Feedback loop design (when to stop iterating?)
- How commercial tools handle iteration (iZotope, LANDR)

**Where to look:**
- ReAct paper (Reasoning + Acting)
- Constitutional AI (iterative refinement)
- Music production AI tools (existing approaches)

---

## 🎹 DOMAIN-SPECIFIC KNOWLEDGE

### Serum Synthesizer
- 2,397 total parameters per preset
- Parameter ranges: mostly [0, 1] normalized
- File formats: .fxp (VST preset) and .SerumPreset (native)
- Already have parser working at 100% success rate

### Audio Analysis
- **Mel-spectrograms**: Standard for audio ML
  - Typical config: n_mels=128, n_fft=2048, hop_length=512
  - Captures perceptually-relevant frequency content
- **CLAP embeddings**: 512-dim vectors aligned with text
- **Sample rates**: 44.1kHz (standard) vs 48kHz (professional)

### Music Production Constraints
- **Latency tolerance**: 1-5 seconds for analysis (NOT live performance)
- **Commercial benchmarks**: iZotope Ozone takes 30+ seconds
- **Real-time**: RAVE achieves 20x faster than real-time on CPU
- **Integration**: Max for Live is easiest path to Ableton

---

## 💡 OPTIMIZATION STRATEGIES FOR M4 MAX

### MLX-Specific
- 40% higher throughput than PyTorch MPS for many tasks
- Native unified memory - no CPU↔GPU transfer
- lightning-whisper-mlx: 10x faster than Whisper.cpp
- 4-bit quantization with minimal quality loss

### Memory Configuration
```python
import os
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'  # Disable memory limit
```

### What to Run Locally vs Cloud
| Task | Location | Reason |
|------|----------|--------|
| Inference (any model that fits) | Local | 128GB enables large models |
| LoRA fine-tuning | Local | Batch size 8-16 on 7B models |
| Training from scratch >1B params | Cloud | 3-10x faster on A100/H100 |
| Rapid prototyping | Local | Zero latency, privacy |

---

## 🎯 ARCHITECTURE COMPARISON TEMPLATES

When comparing architectures, research and fill out:

### Model Comparison
| Criterion | Option A | Option B | Winner | Source |
|-----------|----------|----------|--------|--------|
| Inference speed | | | | [link] |
| Model size | | | | [link] |
| Quality metric | | | | [link] |
| Training cost | | | | [link] |

### Example: Small LLM Selection
| Criterion | Qwen2.5-3B | Phi-3.5-mini | Winner | Source |
|-----------|------------|--------------|--------|--------|
| MLX tokens/sec (M4 Max) | [research] | [research] | ? | MLX benchmarks |
| GSM8K score | [research] | [research] | ? | Model cards |
| MMLU score | [research] | [research] | ? | Leaderboards |
| Context length | [research] | [research] | ? | Documentation |
| 4-bit quality | [research] | [research] | ? | Quantization papers |

**Always fill these tables with RESEARCHED data before making recommendations.**

---

## 📊 EVALUATION METRICS TO IMPLEMENT

### For CNN (Audio → Parameters)
- **MSE (Mean Squared Error)**: Standard regression metric
- **MAE (Mean Absolute Error)**: More interpretable
- **Per-parameter correlation**: Which params predict well?
- **Perceptual metrics**: Does it SOUND right?

### For LLM (Reasoning)
- **Parameter adjustment accuracy**: Did it change the right params?
- **Explanation quality**: Can a producer understand the reasoning?
- **Iteration efficiency**: How many adjust cycles to target sound?
- **Latency**: <200ms per response

### For Full System
- **FAD (Fréchet Audio Distance)**: Distribution similarity
- **CLAP Score**: Text-audio alignment
- **LUFS**: Loudness compliance (-14 LUFS target)
- **User satisfaction**: MOS (Mean Opinion Score) 1-5 scale

---

## 🚀 QUICK START COMMANDS

### Environment Setup
```bash
# Create environment
conda create -n ml-music python=3.11
conda activate ml-music

# Install dependencies
pip install torch torchvision torchaudio
pip install mlx mlx-lm
pip install librosa soundfile matplotlib numpy scipy tqdm tensorboard
pip install laion-clap transformers audiocraft

# Verify MPS
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

### Test MLX
```python
import mlx.core as mx
import mlx.nn as nn

# Verify unified memory
print(f"MLX device: {mx.default_device()}")
```

---

## 📝 NOTES FOR CLAUDE CODE

**When starting a session:**
1. Read PROJECT_CONTEXT_FOR_CLAUDE_CODE.md first
2. Review ARCHITECTURE_DECISIONS.md for design rationale
3. Use this doc for quick research references
4. ALWAYS research before recommending specific tools/models
5. Show the evidence, not just conclusions

**Red flags that require research:**
- "Model X is better than Y" (need benchmarks)
- "This is the standard approach" (verify it's current)
- "You should use library Z" (compare alternatives)
- Any specific numbers (latency, accuracy, size) without source

**Remember:**
- User learns by doing (build prototypes)
- User wants deep justifications (not surface-level)
- User will challenge assumptions (good! engage with it)
- Research is required, not optional

The bounce will come and go, but rigorous research is forever! 🎸
