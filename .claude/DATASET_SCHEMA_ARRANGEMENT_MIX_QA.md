# ArrangementMixQA Dataset Schema

**Date**: 2025-12-03
**Purpose**: Comprehensive schema for arrangement-aware multi-track music production Q&A dataset

---

## Overview

ArrangementMixQA extends the original MixRelationalQA concept with:
1. **Section-aware context** (intro, verse, chorus, drop, breakdown)
2. **Genre-specific structural conventions**
3. **Temporal relationship tracking** (how tracks change across sections)
4. **Pre-computed embeddings** from MixGraph-CLAP

This enables Q&A that understands: "The bass sounds fine in the verse but is masking the kick in the drop."

---

## Core Schema

### Mix Entry (Top Level)

```json
{
  "mix_id": "amq_001",
  "version": "1.0",
  "created_at": "2025-12-03T12:00:00Z",

  "metadata": {
    "genre": "dubstep",
    "subgenre": "melodic_dubstep",
    "tempo": 140,
    "key": "F minor",
    "time_signature": "4/4",
    "total_duration": 180.0
  },

  "structure": {
    "sections": [...],
    "tempo_changes": [...],
    "key_changes": [...]
  },

  "tracks": [...],

  "relationships": {
    "global": {...},
    "per_section": {...}
  },

  "embeddings": {
    "mix_embedding": "embeddings/amq_001_mix.npy",
    "track_embeddings": "embeddings/amq_001_tracks.npy",
    "section_embeddings": "embeddings/amq_001_sections.npy"
  },

  "qa_pairs": [...]
}
```

---

### Section Schema

```json
{
  "section_id": "section_001",
  "label": "drop",           // intro|verse|prechorus|chorus|drop|buildup|breakdown|bridge|outro
  "start_time": 64.0,
  "end_time": 96.0,
  "bar_start": 33,
  "bar_end": 48,
  "energy_level": 0.92,      // 0-1 normalized
  "spectral_centroid": 3450, // Hz
  "confidence": 0.85,

  "active_tracks": ["kick", "bass", "lead_synth", "hats"],

  "section_specific_features": {
    "is_buildup": false,
    "is_breakdown": false,
    "has_riser": false,
    "has_impact": true
  }
}
```

---

### Track Schema

```json
{
  "track_id": "bass_001",
  "track_name": "Wobble Bass",
  "instrument_type": "bass/synth/wobble",
  "audio_path": "audio/amq_001/bass_001.wav",

  "source": {
    "type": "serum_preset",
    "preset_path": "Serum_Presets/Bass/Heavy_Wobble.fxp",
    "preset_name": "Heavy Wobble"
  },

  "parameters": {
    "serum": {
      "osc_a_wavetable": "Basic Shapes",
      "osc_a_wavetable_position": 0.35,
      "fil_cutoff": 0.45,
      "fil_resonance": 0.3,
      "fil_drive": 0.2,
      "lfo_1_rate": 0.25,
      "lfo_1_depth": 0.7
    },
    "effects_chain": [
      {
        "plugin": "EQ Eight",
        "params": {"low_cut": 30, "high_shelf_gain": -2, "high_shelf_freq": 8000}
      },
      {
        "plugin": "Compressor",
        "params": {"threshold": -18, "ratio": 4, "attack": 10, "release": 100}
      }
    ]
  },

  "audio_features": {
    "rms_level_db": -12.5,
    "spectral_centroid": 280,
    "stereo_correlation": 0.95,
    "peak_frequency": 65,
    "dynamic_range": 12.3
  },

  "per_section_features": {
    "intro": {"active": false},
    "verse": {"active": true, "rms_level_db": -15.2, "filter_automation": "closed"},
    "buildup": {"active": true, "rms_level_db": -12.8, "filter_automation": "opening"},
    "drop": {"active": true, "rms_level_db": -10.5, "filter_automation": "open"}
  }
}
```

---

### Relationship Schema

```json
{
  "global": {
    "spectral_overlap_matrix": [[1.0, 0.7, 0.3], [0.7, 1.0, 0.4], [0.3, 0.4, 1.0]],
    "stereo_positions": {"kick": 0.0, "bass": 0.0, "lead": 0.3},
    "rms_ratios": {"kick_to_bass": 3.2, "lead_to_bass": -2.1}
  },

  "per_section": {
    "verse": {
      "spectral_overlap_matrix": [[1.0, 0.5, 0.2], [0.5, 1.0, 0.3], [0.2, 0.3, 1.0]],
      "masking_issues": [],
      "stereo_conflicts": []
    },
    "drop": {
      "spectral_overlap_matrix": [[1.0, 0.85, 0.4], [0.85, 1.0, 0.5], [0.4, 0.5, 1.0]],
      "masking_issues": [
        {
          "track_a": "kick",
          "track_b": "bass",
          "frequency_range": [50, 120],
          "severity": 0.7,
          "recommendation": "sidechain_compression"
        }
      ],
      "stereo_conflicts": []
    }
  }
}
```

---

### Q&A Pair Schema

```json
{
  "qa_id": "qa_001",
  "question_type": "SECTION_AWARE_RELATIONSHIP",
  "section_context": ["drop"],
  "tracks_involved": ["kick", "bass"],

  "question": "The kick is getting lost in the drop. What's causing this and how can I fix it?",

  "answer": "In the drop section, the bass (Wobble Bass) has high energy in the 60-100Hz range due to fil_cutoff at 0.45 and no high-pass filtering. This overlaps with the kick's fundamental at 65Hz. The spectral overlap score is 0.85 in the drop vs 0.5 in the verse because the bass filter opens up during the drop.\n\nRecommended fixes:\n1. Add sidechain compression from kick to bass (4:1 ratio, 10ms attack, 100ms release)\n2. Reduce bass fil_cutoff to 0.35 specifically in the drop section\n3. Add a slight notch EQ on the bass at 65Hz to carve space for the kick",

  "reasoning_trace": "<think>User reports kick getting lost in drop. Let me analyze:\n1. Check section context: drop has highest energy (0.92)\n2. Check spectral overlap: kick-bass overlap is 0.85 in drop vs 0.5 in verse\n3. Why difference? Bass filter opens (automation: opening → open)\n4. Kick fundamental: 65Hz, Bass peak: 65Hz (same!)\n5. Solutions: sidechain, EQ carve, or filter automation adjustment</think>",

  "computed_evidence": {
    "spectral_overlap_drop": 0.85,
    "spectral_overlap_verse": 0.5,
    "kick_fundamental": 65,
    "bass_peak_frequency": 65,
    "bass_filter_cutoff_drop": 0.45
  },

  "tool_calls": [
    {
      "tool": "add_sidechain_compressor",
      "params": {
        "source_track": "kick",
        "target_track": "bass",
        "ratio": 4,
        "attack_ms": 10,
        "release_ms": 100
      }
    }
  ],

  "audio_examples": {
    "before": "audio/amq_001/examples/qa_001_before.wav",
    "after": "audio/amq_001/examples/qa_001_after.wav"
  },

  "tier": "medium",  // simple|medium|complex (for LLM generation tiering)
  "genre_specific": true
}
```

---

## Question Types (Extended)

| Type | Description | Section-Aware? | Example |
|------|-------------|----------------|---------|
| **CLASSIFICATION** | Identify what's happening | No | "What genre is this mix?" |
| **RELATIONSHIP** | Explain inter-track dynamics | No | "Why are these tracks conflicting?" |
| **SECTION_AWARE_RELATIONSHIP** | Track relationships that vary by section | Yes | "Why does the bass sound fine in verse but muddy in drop?" |
| **CAUSATION** | Predict effect of changes | No | "What happens if I boost 2kHz?" |
| **SECTION_CAUSATION** | Section-specific parameter effects | Yes | "What if I open the filter in the buildup?" |
| **RECOMMENDATION** | Suggest fixes | No | "How do I add warmth?" |
| **ARRANGEMENT_RECOMMENDATION** | Section-aware arrangement advice | Yes | "Should I bring in the lead during the breakdown?" |
| **COMPARISON** | Compare approaches | No | "EQ vs compression for this issue?" |
| **TRANSITION** | Section transition advice | Yes | "How should I transition from buildup to drop?" |

---

## Embedding Storage Format

### Track Embeddings (per mix)
```
embeddings/amq_001_tracks.npy
Shape: [N_tracks, 512]  # MixGraph-CLAP output
```

### Section Embeddings (per mix)
```
embeddings/amq_001_sections.npy
Shape: [N_sections, 512]  # Average of track embeddings active in each section
```

### Mix Embedding
```
embeddings/amq_001_mix.npy
Shape: [512]  # Global context embedding
```

---

## Dataset Generation Pipeline

### Stage 1: Audio Collection
1. Combine Serum renders into synthetic mixes
2. Apply effects chains with parameter variations
3. Render multiple versions (before/after)

### Stage 2: Structure Detection
```python
from structure_detector import StructureDetector
detector = StructureDetector(n_segments=8)
analysis = detector.analyze("mix.wav")
sections = analysis.sections
```

### Stage 3: MixGraph-CLAP Encoding
```python
from mix_encoder import MixEncoder
encoder = MixEncoder()
result = encoder.encode_mix(tracks, track_names=names)
# Save embeddings
np.save(f"embeddings/{mix_id}_tracks.npy", result['track_embeddings'].numpy())
```

### Stage 4: Relationship Computation
```python
relationships = {
    'spectral_overlap': result['computed_features']['spectral_overlap'],
    'stereo_correlation': result['computed_features']['stereo_correlation'],
    'rms_levels': result['computed_features']['rms_levels'],
}
```

### Stage 5: LLM Q&A Generation
Using tiered Claude API (Decision 7):
- **Haiku**: Simple classification, basic relationships
- **Sonnet**: Medium complexity, section-aware questions
- **Opus**: Complex multi-step reasoning, arrangement advice

---

## Dataset Statistics (Targets)

| Metric | Target |
|--------|--------|
| Total mixes | 5,000 |
| Tracks per mix | 4-8 |
| Sections per mix | 4-12 |
| Q&A pairs per mix | 10-20 |
| Total Q&A pairs | 50,000-100,000 |
| Section-aware Q&A | 40% |
| With tool calls | 30% |
| With audio examples | 20% |

---

## Genre Distribution

| Genre | Target % | Section Types |
|-------|----------|---------------|
| EDM (Dubstep, House, DnB) | 30% | buildup, drop, breakdown |
| Hip Hop / Trap | 25% | verse, hook, bridge |
| Pop | 20% | verse, prechorus, chorus |
| R&B / Soul | 15% | verse, chorus, bridge |
| Other (Funk, Gospel, etc.) | 10% | varies |

---

## Validation Pipeline

### Automated Checks
1. **Spectral consistency**: Do computed features match audio?
2. **Section boundary accuracy**: Are detected sections reasonable?
3. **Embedding quality**: Are similar tracks close in embedding space?
4. **Q&A consistency**: Does answer match computed evidence?

### Human Validation (Sample)
- Professional producer review of 5% of dataset
- Focus on: Answer correctness, Recommendation quality, Genre appropriateness

---

## File Structure

```
data/
├── arrangement_mix_qa/
│   ├── mixes/
│   │   ├── amq_001.json
│   │   ├── amq_002.json
│   │   └── ...
│   ├── audio/
│   │   ├── amq_001/
│   │   │   ├── bass_001.wav
│   │   │   ├── kick_001.wav
│   │   │   └── examples/
│   │   │       ├── qa_001_before.wav
│   │   │       └── qa_001_after.wav
│   │   └── ...
│   ├── embeddings/
│   │   ├── amq_001_tracks.npy
│   │   ├── amq_001_sections.npy
│   │   ├── amq_001_mix.npy
│   │   └── ...
│   └── splits/
│       ├── train.txt
│       ├── val.txt
│       └── test.txt
```

---

## Integration with Training Pipeline

### Phase 1: Supervised Fine-Tuning
- Train projector on (embeddings, Q&A) pairs
- Freeze CLAP, train projection + LoRA on Qwen

### Phase 2: Self-Play RL (Decision 18)
- Use ArrangementMixQA for reward model training
- Computed features as ground truth for automated reward

### Phase 3: Evaluation
- Hold-out test set with human evaluation
- Automated metrics: BLEU, ROUGE, computed feature accuracy

---

## Next Steps

1. **Build dataset generator script** (`generate_arrangement_mix_qa.py`)
2. **Create synthetic mix combiner** (combine Serum renders)
3. **Implement LLM Q&A generation** (extend `generate_qa_with_llm.py`)
4. **Set up validation pipeline**
5. **Generate initial 1,000 mixes** for proof-of-concept
