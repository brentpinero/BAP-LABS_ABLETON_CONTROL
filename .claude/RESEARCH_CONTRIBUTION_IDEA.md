# Research Contribution: MixRelationalQA

## Novel Dataset for Multi-Track Relational Music Understanding with LLMs

**Status**: Idea/Proposal (Not Yet Executed)
**Date**: 2025-11-30

---

## The Gap in Current Research

### What Exists (Audio Processing, No Language)

| Research | What It Does | Language/Q&A? |
|----------|-------------|---------------|
| [Sony FxNorm-Automix](https://github.com/sony/FxNorm-automix) | Auto-mix stems → polished mix | No |
| [Automix-Toolkit](https://csteinmetz1.github.io/automix-toolkit/) | DMC/Wave-U-Net for mixing | No |
| [Zhao & Pérez-Cota 2024](https://www.researchgate.net/publication/384583481_Adaptive_Filtering_for_Multi-Track_Audio_Based_on_Time-Frequency_Masking_Detection) | Detects frequency masking between tracks | No |
| [MusicGen-Stem (2025)](https://arxiv.org/html/2501.01757v1) | Generates/edits individual stems | No |

### What Exists (LLM + Music, Single-Track Focus)

| Research | What It Does | Multi-Track? |
|----------|-------------|--------------|
| [LLark (Spotify)](https://research.atspotify.com/2023/10/llark-a-multimodal-foundation-model-for-music) | Q&A about single songs (tempo, key, mood) | No |
| [ChatMusician](https://arxiv.org/html/2402.16153v1) | Music theory Q&A, generation | No |
| [M²UGen](https://arxiv.org/html/2311.11255v4) | Music understanding + generation | No |
| [Can LLMs Reason in Music?](https://arxiv.org/html/2407.21531v1) | Benchmarked music reasoning | No |

### The Missing Piece

**Nobody is doing: LLM + Multi-Track Relational Reasoning**

From "Can LLMs Reason in Music?" (2024):
> "Current LLMs exhibit poor performance in song-level multi-step music reasoning, and typically fail to leverage learned music knowledge when addressing complex musical tasks."

From M²UGen:
> "In the realm of LLM-assisted music understanding and generation, there is a notable scarcity of readily available training data."

---

## Proposed Contribution: MixRelationalQA Dataset

### Core Concept

A dataset that teaches LLMs to reason about **relationships between multiple audio tracks** in a music production context.

Unlike existing datasets that ask "What does this song sound like?", MixRelationalQA asks:
- "Why are these two tracks conflicting?"
- "What parameter changes would fix this masking issue?"
- "How should these instruments be balanced?"

### Dataset Schema (Draft)

```json
{
  "mix_id": "mix_001",
  "tracks": [
    {
      "track_id": "kick_001",
      "audio_path": "audio/kick_001.wav",
      "instrument_type": "drums/kick",
      "plugin_chain": [
        {"plugin": "EQ Eight", "params": {"low_cut": 30, "high_shelf": -2}}
      ]
    },
    {
      "track_id": "bass_dubstep_002",
      "audio_path": "audio/bass_dubstep_002.wav",
      "instrument_type": "bass/synth",
      "plugin_chain": [
        {"plugin": "Serum", "preset": "Heavy Wobble", "params": {"fil_cutoff": 0.45}}
      ]
    }
  ],
  "mix_context": {
    "tempo": 140,
    "genre": "dubstep",
    "key": "F minor"
  },
  "qa_pairs": [
    {
      "question_type": "RELATIONSHIP",
      "question": "The bass and kick are fighting in the low end. What's causing this?",
      "answer": "Both tracks have significant energy in the 60-100Hz range. The bass's fil_cutoff at 0.45 allows sub frequencies that overlap with the kick's fundamental.",
      "reasoning_trace": "<think>Analyzing frequency content... kick has fundamental at 60Hz, bass filter allows content down to ~50Hz with current cutoff. Overlapping energy causes masking.</think>"
    },
    {
      "question_type": "RECOMMENDATION",
      "question": "How can I make the kick punch through better?",
      "answer": "Reduce the bass's fil_cutoff to 0.30 to roll off sub-100Hz content, or add sidechain compression from the kick to the bass with 4:1 ratio and 10ms attack.",
      "tool_calls": [
        {"tool": "set_serum_param", "params": {"track": "bass_dubstep_002", "param": "fil_cutoff", "value": 0.30}}
      ]
    },
    {
      "question_type": "CAUSATION",
      "question": "What would happen if I increased the bass's filter drive?",
      "answer": "Increasing fil_driv would add harmonic saturation, creating upper harmonics that could help the bass cut through on smaller speakers, but may also increase mid-range congestion with other elements.",
      "audio_before": "audio/mix_001_before.wav",
      "audio_after": "audio/mix_001_after_drive.wav"
    }
  ]
}
```

### Question Types

| Type | Description | Example |
|------|-------------|---------|
| CLASSIFICATION | Identify what's happening | "Which tracks are conflicting?" |
| RELATIONSHIP | Explain inter-track dynamics | "Why is the vocal getting lost?" |
| CAUSATION | Predict effect of changes | "What happens if I boost 2kHz on the snare?" |
| RECOMMENDATION | Suggest fixes | "How do I add warmth without mud?" |
| COMPARISON | Compare approaches | "Should I use EQ or multiband compression here?" |

### Data Sources

1. **Serum presets + rendered audio** (already have 108K)
2. **Ableton native plugins** (via Max for Live extraction)
3. **Synthetic multi-track mixes** (combine stems programmatically)
4. **Before/after pairs** (render with parameter variations)

### Ground Truth Generation

For each mix, compute:
- Spectral analysis per track
- Frequency overlap detection (masking regions)
- Stereo field analysis
- Dynamic range measurements

Use these metrics + LLM to generate Q&A pairs with verifiable answers.

---

## Why This Matters

### For Research

1. **First multi-track relational music dataset for LLMs**
2. **Bridges gap between audio processing and language understanding**
3. **Enables new benchmarks for music reasoning**

### For Practitioners

1. **AI mixing assistants that explain their decisions**
2. **Educational tools for music production**
3. **Collaborative AI that reasons about your specific mix**

---

## Closest Prior Art

| Work | Similarity | Difference |
|------|-----------|------------|
| [SpatialSoundQA](https://huggingface.co/datasets/zhisheng01/SpatialAudio) | Q&A about spatial audio | Environmental sounds, not music production |
| [LLark](https://research.atspotify.com/2023/10/llark-a-multimodal-foundation-model-for-music) | Music + LLM Q&A | Single track, no inter-track reasoning |
| [FxNorm-Automix](https://github.com/sony/FxNorm-automix) | Multi-track mixing | No language, no explainability |

---

## Open Questions

1. How to reliably compute "ground truth" for subjective mixing decisions?
2. What's the minimum dataset size for effective fine-tuning?
3. How to handle genre-specific mixing conventions?
4. Should the model learn from professional mixes or learn mixing principles?

---

## References

- [Can LLMs "Reason" in Music?](https://arxiv.org/html/2407.21531v1) - Evaluation of music reasoning
- [M²UGen](https://arxiv.org/html/2311.11255v4) - Multi-modal music understanding
- [ChatMusician](https://arxiv.org/html/2402.16153v1) - Music theory with LLMs
- [Sony FxNorm-Automix](https://arxiv.org/pdf/2208.11428) - Automatic mixing with deep learning
- [Zhao & Pérez-Cota 2024](https://www.researchgate.net/publication/384583481_Adaptive_Filtering_for_Multi-Track_Audio_Based_on_Time-Frequency_Masking_Detection) - Frequency masking detection
- [SpatialSoundQA](https://huggingface.co/datasets/zhisheng01/SpatialAudio) - Spatial audio Q&A dataset
