# COMPREHENSIVE DATASET GENERATION PLAN

**Created**: 2025-11-29
**Purpose**: Master plan for generating high-quality training data for music production AI assistant
**Target**: 50,000+ Q&A pairs with interleaved multi-task curriculum structure

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current Data Inventory](#current-data-inventory)
3. [Research Foundation](#research-foundation)
4. [Task Taxonomy](#task-taxonomy)
5. [Curriculum Structure](#curriculum-structure)
6. [Data Sources & Generation Methods](#data-sources--generation-methods)
7. [Quality Assurance Pipeline](#quality-assurance-pipeline)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Cost Estimates](#cost-estimates)

---

## Executive Summary

### The Goal
Build a conversational music production AI assistant that can:
- Understand audio through CNN+Projector architecture
- Reason about synthesis parameters in natural language
- Take iterative action via Max for Live integration
- Run locally on M4 Max with <200ms inference

### The Challenge
Research shows (per [EMNLP 2025 findings](https://arxiv.org/html/2510.22455v1)) that current multimodal LLMs excel at symbolic/MIDI reasoning but struggle with direct audio understanding. Our CNN+Projector approach specifically addresses this "perceptual gap."

### The Solution: Multi-Task Interleaved Curriculum
Based on 2025 research including [MFTCoder (KDD 2024)](https://dl.acm.org/doi/10.1145/3637528.3671609) and [CAMPUS Framework](https://arxiv.org/html/2509.13790):

```
┌─────────────────────────────────────────────────────────────┐
│   MULTI-TASK LEARNING (prevents catastrophic forgetting)   │
│   + INTERLEAVED CURRICULUM (easy→hard across ALL tasks)    │
│   + TIERED MODEL GENERATION (Haiku/Sonnet/Opus by quality) │
│   = OPTIMAL FINE-TUNING STRATEGY                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Current Data Inventory

### Scanned Assets (2025-11-29)

| Source | Presets | MIDI | Audio | MIDI-Preset Pairs | Holy Trinity |
|--------|---------|------|-------|-------------------|--------------|
| Documents | 9,922 | 267 | 83K+ | 66 | 1 pack |
| External Drives | 6,389 | 5,452 | 83,827 | 175 | 6 packs |
| **TOTAL** | **16,311** | **5,719** | **166,827+** | **241** | **7 packs** |

### Pre-Processed Data

| Asset | Count | Location | Status |
|-------|-------|----------|--------|
| Parsed Serum presets | 7,583 | `ultimate_training_dataset/` | ✅ Complete |
| Rendered audio | ~111K | `data/rendered_audio/` | ✅ Complete |
| Mel-spectrograms | ~111K | `data/mel_specs/` | ✅ Complete |
| External preset params | 6,389 | To be parsed | ⏳ Pending |

### Documentation Sources

| Document | Pages | Content | Q&A Potential |
|----------|-------|---------|---------------|
| Serum User Guide Pro | 50+ | Parameters, synthesis | ~500 Q&A |
| Ableton Live 12 Manual | 700+ | DAW, workflow, mixing | ~2,000 Q&A |
| Max for Live Docs | 200+ | Integration, M4L devices | ~300 Q&A |

---

## Research Foundation

### Key 2025 Papers & Models Informing Our Approach

#### Audio Understanding Models

| Model | Architecture | Key Insight for Our System |
|-------|--------------|---------------------------|
| [DeepResonance (EMNLP 2025)](https://arxiv.org/abs/2502.12623) | Multi-way instruction tuning | Multi-modal fusion Transformer before LLM |
| [Qwen2.5-Omni](https://arxiv.org/abs/2503.20215) | Thinker-Talker architecture | TMRoPE for temporal alignment |
| [MERT-v1-330M](https://huggingface.co/m-a-p/MERT-v1-330M) | Music-specific SSL | CQT + RVQ-VAE teachers for music |
| [Stable Audio 2.5](https://stability.ai/stable-audio) | DiT + compressed autoencoder | Long-form coherent structure |

#### Music Production AI

| System | Approach | Applicable Learning |
|--------|----------|---------------------|
| [AI TrackMate](https://arxiv.org/html/2412.06617v1) | Graph-of-Thought prompting | Production-oriented feedback structure |
| [FilmComposer (2025)](https://arxiv.org/abs/2503.08147) | Multi-agent LLM workflow | Simulating professional workflows |
| [Voxtral (Mistral)](https://techchilli.com/artificial-intelligence/mistral-voxtral-open-source-ai-audio-model/) | Audio encoder + LLM decoder | Alternative encoder architecture |

#### Synthetic Data Best Practices

From [Scale AI's 2025 Guide](https://scale.com/blog/synthetic-data-fine-tuning-llms) and [Confident AI](https://www.confident-ai.com/blog/the-definitive-guide-to-synthetic-data-generation-using-llms):

1. **Teacher-Student Distillation**: Use Opus to generate data for fine-tuning smaller model
2. **Agentic Workflows**: Multi-step review and iteration improves quality
3. **Blend Synthetic + Real**: Include documentation-derived Q&A alongside synthetic
4. **Temperature Diversity**: Vary temperature for output diversity
5. **Quality Filtering**: Two-stage filtering (context + generation)

---

## Task Taxonomy

### Complete Task Hierarchy for Full Production Assistant

```
TASK CATEGORIES (12 Total)
├── SYNTHESIS & SOUND DESIGN (40% of dataset)
│   ├── T1: Parameter Identification (What does X do?)
│   ├── T2: Parameter Adjustment (How to achieve Y?)
│   ├── T3: Preset Analysis (Describe this sound)
│   ├── T4: Sound Matching (Recreate this sound)
│   └── T5: Troubleshooting (Fix this issue)
│
├── ARRANGEMENT & COMPOSITION (20% of dataset)
│   ├── T6: MIDI-Preset Matching (Why does this work?)
│   ├── T7: Arrangement Advice (Structure, progression)
│   └── T8: Genre-Specific Workflows (Dubstep bass, etc.)
│
├── MIXING & MASTERING (25% of dataset)
│   ├── T9: EQ & Frequency (Carve space, clarity)
│   ├── T10: Dynamics (Compression, limiting)
│   └── T11: Spatial (Reverb, delay, stereo)
│
└── WORKFLOW & INTEGRATION (15% of dataset)
    ├── T12: Ableton Workflow (DAW operations)
    └── T13: Plugin Integration (3rd party, M4L)
```

### Task-to-Model Mapping (Tiered Generation)

| Tier | Model | Tasks | Difficulty | % of Dataset | Est. Cost |
|------|-------|-------|------------|--------------|-----------|
| 1 | **Haiku 3.5** | T1, T3 (simple), T12 | Easy | 35% | ~$6.30 |
| 2 | **Sonnet 4.5** | T2, T3-T7, T9-T11 | Medium | 50% | ~$33.75 |
| 3 | **Opus 4.5** | T5, T8, Complex T2 | Hard | 15% | ~$33.75 |

**Total for 50K Q&A via Batch API**: ~$73.80

---

## Curriculum Structure

### Interleaved Curriculum Learning

Based on [psychological research on interleaving](https://www.lesswrong.com/posts/n45Awh7bkGRe4YayT/send-llms-to-school-instruction-tuning-with-human-curriculum), mixing topic types while progressing easy→hard produces better retention than sequential single-topic training.

```
EPOCH STRUCTURE (Interleaved)
─────────────────────────────────────────────────────
Phase 1 (Epochs 1-2): FOUNDATION
├── Easy examples from ALL task categories
├── Single-parameter questions
├── Basic descriptions
└── Target: Build vocabulary and parameter knowledge

Phase 2 (Epochs 3-5): INTERMEDIATE
├── Easy + Medium from ALL task categories
├── Multi-parameter coordination
├── Comparative reasoning
└── Target: Build relationships between concepts

Phase 3 (Epochs 6-8): ADVANCED
├── All difficulties, ALL task categories
├── Complex multi-step workflows
├── Genre-specific deep dives
└── Target: Master practical application

Phase 4 (Epochs 9+): REFINEMENT
├── Emphasis on weak categories (E2 from eval)
├── Edge cases and troubleshooting
└── Target: Close remaining gaps
─────────────────────────────────────────────────────
```

### Difficulty Criteria

| Level | Criteria | Example |
|-------|----------|---------|
| **Easy** | Single parameter, direct question | "What does filter cutoff do?" |
| **Medium** | 2-4 parameters, causal reasoning | "How do I make this bass wider?" |
| **Hard** | 5+ parameters, multi-step, genre-specific | "Create a dubstep growl bass from scratch" |
| **Expert** | Full preset creation, troubleshooting chains | "This preset clicks at note boundaries, diagnose and fix" |

---

## Data Sources & Generation Methods

### Source 1: Preset-Based Generation (~25,000 Q&A)

**Input**: 7,583 parsed Serum presets with full parameters

**Generation Strategy**:
```python
PRESET_TASKS = {
    # T1: Parameter Identification (Easy - Haiku)
    "param_id": {
        "prompt": "Given preset '{name}' with {params}, explain what the key parameters do",
        "model": "haiku",
        "count_per_preset": 1,
    },

    # T3: Preset Analysis (Medium - Sonnet)
    "preset_analysis": {
        "prompt": "Analyze preset '{name}' and describe its sonic character, suitable genres, and key parameter choices",
        "model": "sonnet",
        "count_per_preset": 2,
    },

    # T2: Parameter Adjustment (Medium/Hard - Sonnet/Opus)
    "param_adjust": {
        "prompt": "Given preset '{name}', explain how to modify it to achieve {goal}",
        "goals": ["brighter", "darker", "wider", "punchier", "warmer", "more aggressive"],
        "model": "sonnet",
        "count_per_preset": 2,
    },

    # T4: Sound Matching (Hard - Opus)
    "sound_match": {
        "prompt": "This preset achieves {characteristic}. Explain the synthesis approach and how to recreate it",
        "model": "opus",
        "count_per_preset": 0.5,  # Every other preset
    },
}
```

**Estimated Output**: 7,583 × 3.5 avg = ~26,540 Q&A pairs

---

### Source 2: MIDI-Preset Pair Generation (~1,200 Q&A)

**Input**: 241 MIDI-preset pairs from scans

**Generation Strategy**:
```python
MIDI_TASKS = {
    # T6: MIDI-Preset Matching
    "midi_match": {
        "prompt": """Given MIDI file '{midi_name}' paired with preset '{preset_name}':
        - MIDI characteristics: {midi_info}
        - Preset parameters: {preset_params}
        Explain why this pairing works musically and what makes them complement each other.""",
        "model": "sonnet",
        "count_per_pair": 3,
    },

    # T7: Arrangement Context
    "arrangement": {
        "prompt": "How should this {category} preset be arranged in a track structure?",
        "model": "sonnet",
        "count_per_pair": 2,
    },
}
```

**Estimated Output**: 241 × 5 = ~1,205 Q&A pairs

---

### Source 3: Genre-Specific Tutorials (~8,000 Q&A)

**Target Genres** (based on [Sonic Academy](https://www.sonicacademy.com/courses/genres) curriculum):

| Genre | Sub-styles | Key Sound Design Tasks |
|-------|------------|------------------------|
| **Dubstep** | Brostep, Melodic, Deep | Wobble bass, growls, FM basses |
| **House** | Tech, Deep, Future | Supersaws, plucks, chord stabs |
| **Techno** | Melodic, Minimal, Industrial | Acid lines, pads, percussion synths |
| **Trap** | Modern, Melodic | 808s, bells, pads |
| **DnB** | Liquid, Neurofunk, Jump-up | Reese bass, pads, leads |
| **Trance** | Progressive, Uplifting, Psy | Supersaws, arps, leads |

**Generation Strategy**:
```python
GENRE_TASKS = {
    # T8: Genre-Specific Workflows (Hard - Opus)
    "genre_workflow": {
        "prompt": """Create a comprehensive {genre} {sound_type} tutorial:
        1. Core synthesis approach
        2. Key parameter settings
        3. Common modulation techniques
        4. Processing chain (effects)
        5. Mix placement advice""",
        "model": "opus",
        "sounds_per_genre": 10,
        "variations": 5,
    },
}
```

**Estimated Output**: 6 genres × 10 sounds × 5 variations × 2-3 Q&A = ~8,000 pairs

---

### Source 4: Documentation Extraction (~3,000 Q&A)

**Sources**:
1. Serum User Guide Pro (PDF)
2. Ableton Live 12 Manual (PDF)
3. Max for Live documentation

**Extraction Methods**:

```python
DOC_EXTRACTION = {
    # Method 1: Section-based Q&A
    "section_qa": {
        "approach": "Extract each section, generate Q&A about concepts",
        "model": "sonnet",
    },

    # Method 2: FAQ Generation
    "faq_gen": {
        "approach": "Generate common questions a producer would ask about each topic",
        "model": "haiku",
    },

    # Method 3: Tutorial Conversion
    "tutorial_conv": {
        "approach": "Convert step-by-step instructions into Q&A format",
        "model": "sonnet",
    },
}
```

---

### Source 5: YouTube Tutorial Transcripts (~5,000 Q&A)

**Approach**: Use [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) to extract transcripts from music production tutorials.

**Target Channels** (from [EDMProd's top list](https://www.edmprod.com/ableton-tutorials/)):
- Mr. Bill (Ableton, experimental)
- ELPHNT (Max for Live, sound design)
- Venus Theory (creative synthesis)
- Andrew Huang (general production)
- Point Blank (comprehensive tutorials)

**Pipeline**:
```python
def extract_tutorial_qa(video_id):
    """
    1. Fetch transcript via youtube-transcript-api
    2. Chunk into ~2min segments
    3. Use Claude to extract Q&A pairs from each segment
    4. Filter for quality and relevance
    """
    transcript = YouTubeTranscriptApi.fetch(video_id)
    chunks = chunk_transcript(transcript, max_duration=120)

    qa_pairs = []
    for chunk in chunks:
        # Generate Q&A from transcript chunk
        response = generate_qa_from_transcript(chunk, model="sonnet")
        qa_pairs.extend(response)

    return filter_quality(qa_pairs)
```

**Quality Filter**: Only keep Q&A where:
- Question is clear and standalone
- Answer contains specific, actionable information
- Not generic advice ("experiment with settings")

---

### Source 6: Paywalled Tutorial Access Strategy

**Your Resources** (subscriptions you have access to):
- Sonic Academy
- ADSR Sounds
- Loopmasters tutorials
- Splice tutorials

**Extraction Approach** (Offline, No API Required):

```python
PAYWALL_EXTRACTION = {
    "method": "manual_assisted",
    "steps": [
        # 1. Download videos for offline viewing (within ToS for personal use)
        # 2. Use Whisper/Voxtral locally to transcribe
        # 3. Process transcripts with Claude for Q&A extraction
        # 4. Training is personal use, not redistribution
    ],

    "local_transcription": {
        "model": "whisper-large-v3",  # or Voxtral if available
        "device": "mps",  # M4 Max
        "format": "json",  # with timestamps
    },
}
```

**Legal Considerations**:
- Transcription for personal AI training = likely fair use
- No redistribution of original content
- Training data stays local
- Model weights (derivative work) = gray area but common practice

---

### Source 7: Mixing & Mastering Tasks (~7,000 Q&A)

**Task Coverage**:

| Task | Subtasks | Example Q&A |
|------|----------|-------------|
| **T9: EQ** | Low-cut, surgical cuts, broad shapes | "How do I carve space for my bass in the mix?" |
| **T10: Dynamics** | Compression, limiting, sidechain | "My mix sounds flat, how do I add punch?" |
| **T11: Spatial** | Reverb, delay, stereo width | "How do I create depth in my mix?" |

**Generation Strategy**:
```python
MIXING_TASKS = {
    "eq_carving": {
        "scenarios": [
            "Bass and kick conflict",
            "Muddy low-mids",
            "Harsh high frequencies",
            "Vocal sits wrong in mix",
        ],
        "model": "sonnet",
    },

    "dynamics": {
        "scenarios": [
            "Add punch to drums",
            "Control dynamic range",
            "Sidechain pumping effect",
            "Parallel compression",
        ],
        "model": "sonnet",
    },

    "spatial": {
        "scenarios": [
            "Create depth front-to-back",
            "Widen stereo image",
            "Add space without mud",
            "Delay throw effects",
        ],
        "model": "sonnet",
    },
}
```

---

## Quality Assurance Pipeline

### Two-Stage Filtering (per [Scale AI best practices](https://scale.com/blog/synthetic-data-fine-tuning-llms))

```
STAGE 1: CONTEXT QUALITY
────────────────────────
Before generating Q&A, validate input:
├── Preset has valid parameter ranges
├── MIDI file parses correctly
├── Document section is coherent
└── Reject malformed inputs

STAGE 2: GENERATION QUALITY
───────────────────────────
After generating Q&A, validate output:
├── Question is clear and standalone
├── Answer is specific (not generic)
├── Parameter values are in valid ranges
├── Producer language (not engineering jargon)
├── Causal claims are accurate
└── Appropriate difficulty rating
```

### Automated Quality Checks

```python
QUALITY_CHECKS = {
    # Structural
    "min_question_length": 10,
    "max_question_length": 200,
    "min_answer_length": 50,
    "max_answer_length": 1000,

    # Content
    "has_specific_params": True,  # Must mention actual parameter names
    "has_numeric_values": True,   # Should include suggested values
    "no_generic_advice": True,    # Filter "experiment with settings"

    # Diversity
    "max_template_similarity": 0.8,  # Reject near-duplicates
    "category_balance": True,        # Ensure all categories represented

    # Accuracy (spot-check)
    "sample_rate_for_human_review": 0.05,  # 5% manual review
}
```

### Human Review Protocol

```
REVIEW CHECKLIST
├── [ ] Technically accurate (parameter effects match reality)
├── [ ] Uses natural producer language
├── [ ] Answer is actionable (not vague)
├── [ ] Difficulty rating is appropriate
├── [ ] Would a producer actually ask this?
└── [ ] Would this answer help them?
```

---

## Implementation Roadmap

### Phase 1: Data Preparation (Week 1)

| Task | Command | Output |
|------|---------|--------|
| Parse external drive presets | `python ultimate_preset_converter.py --path /Volumes/...` | +6,389 presets |
| Merge scan inventories | `python merge_inventories.py` | Unified inventory |
| Extract doc sections | `python extract_docs.py` | Chunked docs |
| Setup YouTube scraper | `python setup_yt_scraper.py` | Channel list |

### Phase 2: Batch API Implementation (Week 1-2)

```python
# Update generate_qa_with_llm.py with:
BATCH_API_CONFIG = {
    "endpoint": "https://api.anthropic.com/v1/messages/batches",
    "max_requests_per_batch": 10000,
    "max_batch_size_mb": 256,
    "processing_time": "up to 24 hours",
    "result_validity": "29 days",
}

# Tiered model routing
def route_to_model(task_type, difficulty):
    if difficulty == "easy" or task_type in ["param_id", "basic_description"]:
        return "claude-3-5-haiku-latest"
    elif difficulty == "hard" or task_type in ["genre_workflow", "troubleshooting"]:
        return "claude-sonnet-4-5-20250929"
    else:
        return "claude-3-5-sonnet-latest"
```

### Phase 3: Generation Batches (Weeks 2-3)

| Batch | Source | Count | Model Mix | Est. Cost |
|-------|--------|-------|-----------|-----------|
| 1 | Presets (Easy) | 10,000 | 100% Haiku | $3.60 |
| 2 | Presets (Medium) | 15,000 | 100% Sonnet | $33.75 |
| 3 | Presets (Hard) | 5,000 | 100% Opus | $33.75 |
| 4 | MIDI Pairs | 1,200 | 70% Sonnet, 30% Opus | $4.50 |
| 5 | Genre Tutorials | 8,000 | 50% Sonnet, 50% Opus | $36.00 |
| 6 | Documentation | 3,000 | 80% Sonnet, 20% Haiku | $8.10 |
| 7 | YT Transcripts | 5,000 | 100% Sonnet | $11.25 |
| 8 | Mixing/Mastering | 7,000 | 100% Sonnet | $15.75 |
| **TOTAL** | - | **54,200** | - | **~$146.70** |

### Phase 4: Quality Filtering (Week 3)

```
EXPECTED YIELD AFTER FILTERING
─────────────────────────────
Generated: 54,200 Q&A pairs
├── Stage 1 (structural): -5% → 51,490
├── Stage 2 (content): -10% → 46,341
├── Deduplication: -5% → 44,024
└── Final dataset: ~44,000 high-quality pairs
```

### Phase 5: Curriculum Ordering (Week 3)

```python
def order_for_curriculum(qa_pairs):
    """Order Q&A pairs for interleaved curriculum training."""

    # Tag each pair with difficulty
    tagged = [tag_difficulty(qa) for qa in qa_pairs]

    # Group by difficulty
    easy = [qa for qa in tagged if qa['difficulty'] == 'easy']
    medium = [qa for qa in tagged if qa['difficulty'] == 'medium']
    hard = [qa for qa in tagged if qa['difficulty'] == 'hard']

    # Interleave within difficulty groups (mix task types)
    easy_interleaved = interleave_by_task_type(easy)
    medium_interleaved = interleave_by_task_type(medium)
    hard_interleaved = interleave_by_task_type(hard)

    # Create curriculum phases
    curriculum = []

    # Phase 1: Easy only (first 20%)
    curriculum.extend(easy_interleaved[:int(len(easy_interleaved) * 0.2)])

    # Phase 2: Easy + Medium mixed
    phase2 = interleave(
        easy_interleaved[int(len(easy_interleaved) * 0.2):],
        medium_interleaved[:int(len(medium_interleaved) * 0.5)]
    )
    curriculum.extend(phase2)

    # Phase 3: All difficulties
    phase3 = interleave(
        medium_interleaved[int(len(medium_interleaved) * 0.5):],
        hard_interleaved
    )
    curriculum.extend(phase3)

    return curriculum
```

---

## Cost Estimates

### Batch API Pricing (50% Discount)

| Model | Standard Input | Standard Output | Batch Input | Batch Output |
|-------|---------------|-----------------|-------------|--------------|
| Haiku 3.5 | $0.80/1M | $4.00/1M | $0.40/1M | $2.00/1M |
| Sonnet 4.5 | $3.00/1M | $15.00/1M | $1.50/1M | $7.50/1M |
| Opus 4.5 | $15.00/1M | $75.00/1M | $7.50/1M | $37.50/1M |

### Projected Costs

| Scenario | Q&A Pairs | Model Mix | Batch Cost |
|----------|-----------|-----------|------------|
| Minimum Viable | 15,000 | 50% Haiku, 50% Sonnet | ~$22.50 |
| **Recommended** | **50,000** | **35% Haiku, 50% Sonnet, 15% Opus** | **~$147** |
| Maximum Scale | 100,000 | 30% Haiku, 50% Sonnet, 20% Opus | ~$320 |

### Alternative: Real-Time API (No Batch)

Without Batch API discount, costs would be 2x:
- Recommended (50K): ~$294
- Maximum (100K): ~$640

**Recommendation**: Use Batch API for all generation (50% savings, 24hr processing acceptable)

---

## Appendix A: Example Q&A Pairs by Category

### T1: Parameter Identification (Easy)
```json
{
  "task": "param_id",
  "difficulty": "easy",
  "question": "What does the Wavetable Position parameter (WT POS) do in Serum?",
  "answer": "Wavetable Position controls which frame of the loaded wavetable is playing. At 0%, you hear the first frame. At 100%, you hear the last frame. Values in between morph through the wavetable. This is one of the most important parameters for sound design - modulating WT POS with an LFO or envelope creates movement and evolving timbres. In this preset, WT POS is set to 0.65, which means we're hearing a frame about 2/3 through the wavetable."
}
```

### T2: Parameter Adjustment (Medium)
```json
{
  "task": "param_adjust",
  "difficulty": "medium",
  "question": "This bass sounds too thin. How do I make it fatter?",
  "answer": "To fatten this bass, focus on these areas:\n\n1. **Add Unison Voices**: Increase OSC A Unison from 1 to 4-6 voices. This instantly thickens the sound.\n\n2. **Increase Detune**: Set Unison Detune to 0.15-0.25. More detune = wider, fatter sound.\n\n3. **Layer with Sub**: Turn up the Sub Oscillator to 0.5-0.7. This adds fundamental low-end weight.\n\n4. **Widen Stereo**: Add slight stereo spread to the unison voices, but keep sub in mono.\n\n5. **Saturation**: Add subtle distortion (0.2-0.3) to add harmonics.\n\nStart with unison + detune - that's the quickest path to a fatter sound."
}
```

### T8: Genre-Specific Workflow (Hard)
```json
{
  "task": "genre_workflow",
  "difficulty": "hard",
  "question": "How do I create a classic dubstep wobble bass in Serum?",
  "answer": "Classic dubstep wobble bass recipe:\n\n**1. Oscillator Setup**\n- OSC A: Load a complex wavetable (try 'Growl' or 'Analog Brass')\n- WT POS: Start around 0.5 for harmonic content\n- Unison: 4 voices, Detune: 0.2\n\n**2. LFO Wobble**\n- LFO 1: Set to 1/4 note (synced to tempo)\n- Route LFO 1 to WT Position with ~50% depth\n- Route LFO 1 to Filter Cutoff with ~40% depth\n- Shape: Sine or Triangle for smooth wobble\n\n**3. Filter**\n- Type: Low-pass 24dB\n- Cutoff: Start at 400Hz\n- Resonance: 0.5-0.7 for that nasal character\n\n**4. Processing**\n- Add Distortion: Soft Clip at 0.3\n- OTT or multiband compression\n- Subtle stereo widening on highs only\n\n**5. Automation**\n- Automate LFO rate (1/4 → 1/8 → 1/16) for builds\n- Automate resonance for filter sweeps\n\nThe key is the LFO→WT Position modulation - that's what creates the 'wub' sound."
}
```

---

## Appendix B: Training Data Format

### JSONL Output Format
```json
{"source": "preset_analysis", "task": "T3", "difficulty": "medium", "question": "...", "answer": "...", "preset": "BASS_Heavy_01", "category": "bass"}
{"source": "genre_workflow", "task": "T8", "difficulty": "hard", "question": "...", "answer": "...", "genre": "dubstep", "category": "bass"}
{"source": "midi_pair", "task": "T6", "difficulty": "medium", "question": "...", "answer": "...", "midi": "chord_prog_01.mid", "preset": "PAD_Lush_02"}
```

### Curriculum Metadata
```json
{
  "dataset_info": {
    "total_pairs": 44000,
    "creation_date": "2025-11-29",
    "curriculum_structure": "interleaved",
    "difficulty_distribution": {"easy": 0.25, "medium": 0.50, "hard": 0.20, "expert": 0.05}
  },
  "task_distribution": {
    "T1_param_id": 5000,
    "T2_param_adjust": 10000,
    "T3_preset_analysis": 8000,
    ...
  }
}
```

---

## Sources & References

### 2025 Research
- [DeepResonance (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.653/)
- [Qwen2.5-Omni Technical Report](https://arxiv.org/abs/2503.20215)
- [AI TrackMate](https://arxiv.org/html/2412.06617v1)
- [FilmComposer](https://arxiv.org/abs/2503.08147)
- [MERT-v1](https://huggingface.co/m-a-p/MERT-v1-330M)
- [Evaluating MLLMs on Core Music Tasks](https://arxiv.org/html/2510.22455v1)
- [LLM4MA Workshop @ ISMIR 2025](https://m-a-p.ai/LLM4Music/)

### Synthetic Data Best Practices
- [Scale AI: Synthetic Data Strategies](https://scale.com/blog/synthetic-data-fine-tuning-llms)
- [Confident AI: Definitive Guide](https://www.confident-ai.com/blog/the-definitive-guide-to-synthetic-data-generation-using-llms)
- [LLM Synthetic Data Reading List (GitHub)](https://github.com/pengr/LLM-Synthetic-Data)

### Audio Encoders
- [Voxtral (Mistral)](https://techchilli.com/artificial-intelligence/mistral-voxtral-open-source-ai-audio-model/)
- [NVIDIA Canary](https://modal.com/blog/open-source-stt)
- [Stable Audio 2.5](https://stability.ai/stable-audio)

### Tutorial Resources
- [Sonic Academy Genres](https://www.sonicacademy.com/courses/genres)
- [ADSR Sound Design](https://www.adsrsounds.com/courses/)
- [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/)

---

**Document Status**: Living document - update as implementation progresses
**Next Review**: After Phase 2 completion

---

# PART 2: COLLABORATOR EXPANSION (Added 2025-11-29)

## Vision Upgrade: Assistant → Collaborator

### The Critical Insight

> "It will need context on how to write good drums or keys etc. It will need to be able to think about all of the streams of data coming in from other channels to support its preset choice and be able to write drums MIDI among other instances to truly be a production assistant - to be more specific it should be a **collaborator/assistant**."

This fundamentally changes our approach:

| Aspect | Assistant (Original) | Collaborator (Expanded) |
|--------|---------------------|------------------------|
| **Scope** | Sound design focus | Full production workflow |
| **Input** | User request + single preset | User request + **multi-track context** (audio + MIDI) |
| **Output** | Text response | Text + **tool calls** (actions in Ableton) |
| **Value Add** | Knowledge sharing | **Takes action** in the DAW |

### Why Tool Use Matters

Without tool use, users might as well use ChatGPT - it's larger and more robust for pure Q&A. The real value is the model **taking action** through Max for Live integration.

---

## Revised Response Format: Reasoning + Actions + Explanation

Every training example should include three parts:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. REASONING (the "thinking" - WHY)                            │
│     - Analyze current state (audio + MIDI + arrangement)        │
│     - Identify the problem/goal                                 │
│     - Consider options and trade-offs                           │
│     - Decide on approach                                        │
├─────────────────────────────────────────────────────────────────┤
│  2. ACTIONS (tool calls - WHAT)                                 │
│     - Serum parameter changes                                   │
│     - MIDI writes to tracks                                     │
│     - Mixer/EQ adjustments                                      │
│     - Clip/arrangement operations                               │
├─────────────────────────────────────────────────────────────────┤
│  3. EXPLANATION (user-facing - HOW/WHAT HAPPENED)               │
│     - What was done and why                                     │
│     - What to listen for                                        │
│     - Follow-up suggestions                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Why Reasoning is Critical

1. **Teaches the model HOW to think** about multi-track problems
2. **Creates interpretable decisions** - user can understand and correct
3. **Enables iteration** - "I don't like that approach, try X instead"
4. **Differentiates from foundation models** - domain-specific production reasoning

---

## Training Data Format (Revised)

### Full Example with Context, Reasoning, Actions, Explanation

```json
{
  "context": {
    "user_request": "The bass feels weak compared to the drums",
    "tracks": {
      "Drums": {
        "type": "audio",
        "analysis": {
          "rms": 0.7,
          "spectral_centroid": 180,
          "low_end_energy": 0.8,
          "transient_sharpness": 0.9
        }
      },
      "Bass": {
        "type": "midi",
        "instrument": "Serum",
        "preset_name": "BA Deep Sub",
        "params": {
          "sub_level": 0.3,
          "filter_cutoff": 0.5,
          "osc_a_level": 0.8
        },
        "midi_pattern": {
          "notes": ["A1", "A1", "A1", "A1"],
          "timing": ["1.1", "2.1", "3.1", "4.1"],
          "description": "root notes on beats 1, 2, 3, 4"
        }
      },
      "Keys": {
        "type": "midi",
        "instrument": "Serum",
        "chord_progression": "Am - F - C - G"
      }
    },
    "tempo": 128,
    "section": "drop"
  },

  "response": {
    "reasoning": "<think>\nAnalyzing the context:\n- Drums have high low-end energy (0.8) with spectral centroid at 180Hz\n- Bass sub_level is only 0.3 - that's quite low for a 'Deep Sub' preset\n- Bass is hitting on every beat (1,2,3,4) - competing with kick on all downbeats\n- This is a drop section at 128 BPM - needs energy and clarity\n\nThe problem is both SPECTRAL (frequencies competing) and TEMPORAL (same timing).\n\nOptions:\n1. Boost bass sub_level alone → might cause mud, doesn't fix timing\n2. EQ carve the drums → loses drum punch in a drop\n3. Sidechain the bass → common solution but can sound pumpy\n4. Shift bass timing + boost sub → addresses both issues\n5. Change bass to hit on 2 and 4 only → creates space, might feel sparse\n\nBest approach for a drop: Option 4 - boost sub for weight AND shift timing to off-beats for rhythmic interplay. The drop needs both power AND groove.\n</think>",

    "actions": [
      {
        "tool": "set_serum_param",
        "track": "Bass",
        "param": "sub_level",
        "value": 0.7,
        "reason": "Increase fundamental weight"
      },
      {
        "tool": "set_serum_param",
        "track": "Bass",
        "param": "filter_cutoff",
        "value": 0.6,
        "reason": "Open filter slightly for more presence"
      },
      {
        "tool": "modify_midi",
        "track": "Bass",
        "operation": "shift_timing",
        "offset": "+0.5",
        "unit": "beats",
        "reason": "Move bass to off-beats to complement kick"
      }
    ],

    "explanation": "I analyzed your tracks and found two issues: your bass sub level was quite low (0.3), and it was hitting on the same beats as your kick, causing them to compete.\n\nI've made three changes:\n1. **Boosted sub oscillator** (0.3 → 0.7) for more fundamental weight\n2. **Opened the filter slightly** (0.5 → 0.6) for more presence in the mix\n3. **Shifted bass timing** to land on off-beats - now it grooves BETWEEN the kicks\n\nListen for how the low end feels more defined - kick punches on the downbeat, bass fills the space after. This call-and-response pattern is classic for high-energy drops.\n\nWant me to also add some sidechain compression for extra pump, or does this feel good?"
  }
}
```

---

## Expanded Task Taxonomy (21 Categories)

### Original Categories (T1-T13) - Preserved

*(See Part 1 above)*

### NEW: Composition & MIDI Tasks (T14-T18)

```
COMPOSITION & MIDI GENERATION (NEW)
├── T14: Drum Pattern Generation
│   ├── Genre-specific patterns (house, techno, trap, dnb, dubstep)
│   ├── Variations and fills
│   ├── Velocity and groove programming
│   └── Output: MIDI pattern + reasoning
│
├── T15: Bass Line Construction
│   ├── Chord-aware bass writing
│   ├── Rhythmic interplay with drums
│   ├── Genre-specific approaches
│   └── Output: MIDI pattern + parameter suggestions
│
├── T16: Chord Voicing & Progressions
│   ├── Inversions and voice leading
│   ├── Open vs closed voicings
│   ├── Genre-appropriate progressions
│   └── Output: MIDI chords + voicing reasoning
│
├── T17: Melody Writing
│   ├── Contour and phrasing
│   ├── Chord tone targeting
│   ├── Rhythmic variation
│   └── Output: MIDI melody + compositional reasoning
│
└── T18: Arpeggio & Sequence Patterns
    ├── Pattern types (up, down, random, chord)
    ├── Rate and sync settings
    ├── Serum arpeggiator integration
    └── Output: Pattern settings + MIDI
```

### NEW: Multi-Track Context Reasoning (T19-T21)

```
MULTI-TRACK CONTEXT (NEW)
├── T19: Cross-Channel Analysis
│   ├── "What's happening across all tracks?"
│   ├── Frequency spectrum distribution
│   ├── Rhythmic relationships
│   └── Output: Analysis + recommendations
│
├── T20: Contextual Preset/Sound Selection
│   ├── "What sound would fit this arrangement?"
│   ├── Consider existing elements
│   ├── Frequency space availability
│   └── Output: Preset recommendation + reasoning
│
└── T21: Conflict Resolution
    ├── Frequency masking issues
    ├── Timing/phase conflicts
    ├── Arrangement density problems
    └── Output: Diagnosis + multi-track actions
```

---

## Tool Schema (Actions Available)

### Serum Control Tools

```python
SERUM_TOOLS = {
    "set_serum_param": {
        "description": "Set any Serum parameter",
        "params": {
            "track": "Track name in Ableton",
            "param": "Parameter name (e.g., 'filter_cutoff', 'osc_a_level')",
            "value": "Normalized value 0.0-1.0"
        }
    },
    "load_serum_preset": {
        "description": "Load a Serum preset",
        "params": {
            "track": "Track name",
            "preset_path": "Path to preset file"
        }
    },
    "set_serum_wavetable": {
        "description": "Change wavetable on oscillator",
        "params": {
            "track": "Track name",
            "oscillator": "A or B",
            "wavetable": "Wavetable name"
        }
    }
}
```

### MIDI Tools

```python
MIDI_TOOLS = {
    "write_midi": {
        "description": "Write MIDI notes to a clip",
        "params": {
            "track": "Track name",
            "clip_slot": "Clip slot index or 'new'",
            "notes": [
                {"pitch": "C3", "start": 0.0, "duration": 0.5, "velocity": 100}
            ]
        }
    },
    "modify_midi": {
        "description": "Modify existing MIDI",
        "params": {
            "track": "Track name",
            "operation": "shift_timing | transpose | change_velocity | quantize",
            "parameters": {}
        }
    },
    "generate_drum_pattern": {
        "description": "Generate a drum pattern",
        "params": {
            "track": "Track name",
            "genre": "house | techno | trap | dnb | dubstep",
            "variation": "basic | complex | fill",
            "bars": 4
        }
    }
}
```

### Mixer Tools

```python
MIXER_TOOLS = {
    "set_track_volume": {
        "params": {"track": "str", "db": "float"}
    },
    "set_track_pan": {
        "params": {"track": "str", "pan": "float -1 to 1"}
    },
    "set_send_level": {
        "params": {"track": "str", "send": "A|B|C...", "level": "float"}
    },
    "set_eq_band": {
        "params": {"track": "str", "band": "int", "freq": "Hz", "gain": "dB", "q": "float"}
    },
    "set_compressor": {
        "params": {"track": "str", "threshold": "dB", "ratio": "float", "attack": "ms", "release": "ms"}
    }
}
```

### Arrangement Tools

```python
ARRANGEMENT_TOOLS = {
    "create_clip": {
        "params": {"track": "str", "slot": "int", "length_bars": "int"}
    },
    "duplicate_clip": {
        "params": {"track": "str", "source_slot": "int", "dest_slot": "int"}
    },
    "set_clip_loop": {
        "params": {"track": "str", "slot": "int", "loop_start": "beats", "loop_end": "beats"}
    }
}
```

---

## Data Sources for Collaborator Training

### Source 8: Project File Extraction (~5,000 Q&A)

**Input**: 35 .als project files

**Extraction Pipeline**:
```python
PROJECT_EXTRACTION = {
    "steps": [
        # 1. Open project in Ableton
        # 2. Solo and export each track as stem (audio)
        # 3. Export MIDI from each MIDI track
        # 4. Capture all plugin states (Serum params, etc.)
        # 5. Record arrangement structure (sections, markers)
    ],

    "output_per_project": {
        "stems": ["drums.wav", "bass.wav", "keys.wav", ...],
        "midi": ["drums.mid", "bass.mid", "keys.mid", ...],
        "plugin_states": {"Bass_Serum": {...params...}},
        "arrangement": {"sections": [...], "tempo": 128}
    },

    "qa_generation": {
        "multi_track_analysis": "Given this arrangement, analyze...",
        "modification_tasks": "How would you make the bass more aggressive?",
        "conflict_resolution": "The kick and bass are fighting, fix it",
        "composition_suggestions": "Add a lead melody that fits"
    }
}
```

**Estimated Output**: 35 projects × ~150 Q&A variations = ~5,000 pairs

### Source 9: Composition Theory + Tool Use (~10,000 Q&A)

**Combining theory with actionable outputs**:

```python
COMPOSITION_WITH_TOOLS = {
    "drum_patterns": {
        "per_genre": 6,
        "patterns_per_genre": 20,
        "each_includes": ["reasoning", "midi_output", "tool_calls"],
        "model": "opus",
        "total": ~2,400 Q&A
    },

    "bass_lines": {
        "progressions": 50,
        "contexts": 10,  # Different drum/chord contexts
        "each_includes": ["context_analysis", "midi_output", "serum_params"],
        "model": "opus",
        "total": ~2,500 Q&A
    },

    "chord_voicings": {
        "progressions": 50,
        "voicing_types": 5,
        "each_includes": ["voice_leading_reasoning", "midi_output"],
        "model": "sonnet",
        "total": ~1,250 Q&A
    },

    "multi_track_scenarios": {
        "base_contexts": 100,
        "question_types": 5,
        "each_includes": ["full_analysis", "multiple_tool_calls", "explanation"],
        "model": "opus",
        "total": ~2,500 Q&A
    }
}
```

### Source 10: MIDI File Analysis (~3,000 Q&A)

**From our 5,719 MIDI files**:

```python
MIDI_ANALYSIS = {
    "categorization": {
        # Categorize by instrument based on pitch range
        "drums": "GM drum map or percussion patterns",
        "bass": "avg_pitch < 48 (below C3)",
        "keys": "48 <= avg_pitch < 72 (C3-C5)",
        "lead": "avg_pitch >= 72 (C5+)"
    },

    "analysis_tasks": {
        "pattern_description": "Describe this drum pattern's characteristics",
        "genre_identification": "What genre does this pattern fit?",
        "modification_suggestions": "How would you vary this for a fill?",
        "complementary_parts": "Given this bass, what drum pattern works?"
    },

    "output_format": {
        "includes_reasoning": True,
        "includes_tool_calls": True,  # "To recreate this, use these tools..."
        "includes_midi_notation": True
    }
}
```

---

## Instrument-Specific Knowledge Requirements

### Drums: What the Model Must Know

| Genre | Kick Pattern | Snare/Clap | Hi-Hats | Key Characteristics |
|-------|--------------|------------|---------|---------------------|
| **House** | Four-on-floor (1,2,3,4) | 2 and 4 | Off-beats | Driving, consistent |
| **Techno** | Four-on-floor | 2 and 4 or none | 16ths | Mechanical, hypnotic |
| **Trap** | Sparse, 808 | Beat 3 | Triplet rolls | Bouncy, syncopated |
| **DnB** | 2-step (1, 2.5) | 2 and 4 | Fast 16ths | Broken, energetic |
| **Dubstep** | Half-time | Beat 3 | Sparse | Heavy, spaced |

**Training Focus**: Generate patterns with correct placement, velocity curves, and genre-appropriate variations.

### Bass: What the Model Must Know

| Concept | Description | Tool Integration |
|---------|-------------|------------------|
| **Root movement** | Following chord roots | `write_midi` with chord-aware notes |
| **Rhythmic interplay** | Complementing kick | Analyze drums → offset bass timing |
| **Frequency space** | Sub vs mid-bass | `set_serum_param` for sub_level, filter |
| **Genre styles** | House groove vs DnB reese | Preset selection + MIDI pattern |

### Keys/Chords: What the Model Must Know

| Concept | Description | Tool Integration |
|---------|-------------|------------------|
| **Voice leading** | Smooth note movement | `write_midi` with minimal jumps |
| **Inversions** | Root, 1st, 2nd position | Calculate inversions in reasoning |
| **Voicing spread** | Open vs closed | Note spacing in MIDI output |
| **Genre voicings** | Future bass 7ths vs house stabs | Style-appropriate note choices |

---

## Curriculum Update for Collaborator Tasks

### Phase 1: Foundation (Include New Tasks at EASY Level)

```
PHASE 1 ADDITIONS:
├── T14 (Drums): Basic 4/4 kick patterns, single genre
├── T15 (Bass): Root notes following chords
├── T16 (Chords): Root position triads only
├── T19 (Context): Simple 2-track analysis ("what's the kick doing?")
└── Tool use: Single tool calls only
```

### Phase 2: Intermediate (Multi-Parameter, Multi-Tool)

```
PHASE 2 ADDITIONS:
├── T14: Genre-specific patterns with hats and snare
├── T15: Chord tones, rhythmic variation
├── T16: First inversions, basic voice leading
├── T19: 3-4 track analysis with conflict identification
├── T20: Preset recommendations based on context
└── Tool use: 2-3 tool calls per response
```

### Phase 3: Advanced (Full Complexity)

```
PHASE 3 ADDITIONS:
├── T14: Fills, variations, velocity programming
├── T15: Walking bass, syncopation, genre-specific
├── T16-T17: Full voice leading, melody + chord interaction
├── T19-T21: Full arrangement analysis, complex conflict resolution
└── Tool use: Multi-step tool sequences with reasoning
```

---

## Updated Cost Estimates

### Additional Data Sources

| Batch | Source | Count | Model Mix | Est. Cost |
|-------|--------|-------|-----------|-----------|
| 9 | Project file extraction | 5,000 | 70% Opus, 30% Sonnet | ~$35 |
| 10 | Composition + tools | 10,000 | 60% Opus, 40% Sonnet | ~$55 |
| 11 | MIDI file analysis | 3,000 | 100% Sonnet | ~$7 |
| **NEW TOTAL** | | **18,000** | | **~$97** |

### Combined Totals

| Scenario | Q&A Pairs | Batch Cost |
|----------|-----------|------------|
| Original Plan (Sources 1-8) | 54,200 | ~$147 |
| Collaborator Expansion (Sources 9-11) | 18,000 | ~$97 |
| **COMBINED TOTAL** | **72,200** | **~$244** |

---

## Integration Architecture (For Reference)

```
┌─────────────────────────────────────────────────────────────────┐
│                         ABLETON LIVE                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │ Drums   │ │ Bass    │ │ Keys    │ │ Lead    │               │
│  │ (Audio) │ │ (MIDI)  │ │ (MIDI)  │ │ (MIDI)  │               │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘               │
│       └───────────┴───────────┴───────────┘                     │
│                         │                                        │
│              ┌──────────▼──────────┐                            │
│              │   MAX FOR LIVE      │                            │
│              │   WebSocket Bridge  │                            │
│              │   - Send track state│                            │
│              │   - Receive actions │                            │
│              │   - Execute tools   │                            │
│              └──────────┬──────────┘                            │
└─────────────────────────┼───────────────────────────────────────┘
                          │ WebSocket (JSON)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL QWEN3-4B + CNN                          │
│                                                                  │
│  INPUT:                           OUTPUT:                        │
│  - Track states (audio+MIDI)      - Reasoning trace             │
│  - CNN audio analysis             - Tool calls (actions)        │
│  - User request                   - Explanation                  │
│  - Serum param states             │                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Define complete tool schema** - Research M4L/Ableton Live API capabilities
2. **Build project file extractor** - Stem + MIDI + state extraction from .als
3. **Create MIDI analyzer** - Categorize and analyze 5,719 MIDI files
4. **Generate composition training data** - With reasoning + tool calls
5. **Update curriculum** - Interleave new tasks with existing

---

## Appendix C: Additional Example Training Pairs

### T14: Drum Pattern Generation (with Tool Use)

```json
{
  "context": {
    "user_request": "Create a techno drum pattern for this track",
    "tempo": 130,
    "existing_tracks": {
      "Bass": {"type": "midi", "pattern": "16th note pulse on F1"}
    }
  },
  "response": {
    "reasoning": "<think>\nTechno at 130 BPM needs:\n- Four-on-floor kick (driving foundation)\n- Minimal snare/clap (maybe just 2 and 4, or none)\n- 16th note hi-hats (mechanical, hypnotic)\n- The bass is already pulsing 16ths on F1, so I'll keep drums tight and locked\n\nFor a classic Berlin techno feel, I'll use:\n- Punchy kick on every beat\n- Closed hats on all 16ths, accented off-beats\n- Open hat on the 'and' of 2 and 4 for swing\n- No snare initially - keep it minimal\n</think>",

    "actions": [
      {
        "tool": "write_midi",
        "track": "Drums",
        "clip_name": "Techno_Beat_01",
        "notes": [
          {"pitch": "C1", "start": 0.0, "duration": 0.25, "velocity": 110},
          {"pitch": "C1", "start": 1.0, "duration": 0.25, "velocity": 110},
          {"pitch": "C1", "start": 2.0, "duration": 0.25, "velocity": 110},
          {"pitch": "C1", "start": 3.0, "duration": 0.25, "velocity": 110},
          {"pitch": "F#1", "start": 0.0, "duration": 0.1, "velocity": 80},
          {"pitch": "F#1", "start": 0.25, "duration": 0.1, "velocity": 100},
          {"pitch": "F#1", "start": 0.5, "duration": 0.1, "velocity": 80},
          {"pitch": "F#1", "start": 0.75, "duration": 0.1, "velocity": 100}
        ],
        "comment": "Kick on beats, hats on 16ths with off-beat accents"
      }
    ],

    "explanation": "I've created a classic Berlin techno pattern:\n\n- **Kick**: Solid four-on-floor at full velocity for that driving pulse\n- **Hi-hats**: 16th notes with velocity variation - louder on off-beats (80→100→80→100) creates that hypnotic swing\n- **No snare yet**: Keeping it minimal to match the pulsing bass\n\nThis locks perfectly with your 16th note bass pulse. The accented off-beat hats create forward momentum.\n\nWant me to add an open hat for more swing, or a rim shot on 2 and 4?"
  }
}
```

### T21: Multi-Track Conflict Resolution (with Tool Use)

```json
{
  "context": {
    "user_request": "The low end is muddy, kick and bass are fighting",
    "tracks": {
      "Drums": {
        "type": "audio",
        "analysis": {"low_end_peak": 65, "attack_time": 5, "sustain": 0.2}
      },
      "Bass": {
        "type": "midi",
        "instrument": "Serum",
        "params": {"sub_level": 0.9, "filter_cutoff": 0.3},
        "fundamental_freq": 55
      }
    }
  },
  "response": {
    "reasoning": "<think>\nAnalyzing the conflict:\n- Kick peaks at 65Hz, bass fundamental at 55Hz - they're 10Hz apart, definitely overlapping\n- Kick has fast attack (5ms) and short sustain (0.2) - punchy\n- Bass has very high sub_level (0.9) and low filter_cutoff (0.3) - lots of sub energy\n\nBoth are fighting for the 50-80Hz range. Options:\n\n1. Sidechain bass to kick - classic solution, creates pumping\n2. High-pass the kick around 60Hz - let bass own the sub\n3. High-pass the bass around 60Hz - let kick own the sub  \n4. EQ notch in bass at kick frequency - surgical approach\n5. Reduce bass sub_level - simplest fix\n\nBest approach: The kick is punchy with short sustain, so it should own the transient. The bass has the sustained sub energy. I'll:\n1. Reduce bass sub_level slightly (0.9 → 0.65) so it doesn't overwhelm\n2. Add sidechain compression for the transient moment\n3. High-pass bass at 30Hz to remove inaudible rumble\n\nThis keeps both powerful but separated in time.\n</think>",

    "actions": [
      {
        "tool": "set_serum_param",
        "track": "Bass",
        "param": "sub_level",
        "value": 0.65,
        "reason": "Reduce sub energy to make room for kick"
      },
      {
        "tool": "set_eq_band",
        "track": "Bass",
        "band": 1,
        "type": "highpass",
        "freq": 30,
        "reason": "Remove inaudible sub rumble"
      },
      {
        "tool": "set_compressor",
        "track": "Bass",
        "sidechain_source": "Drums",
        "threshold": -20,
        "ratio": 4,
        "attack": 1,
        "release": 100,
        "reason": "Duck bass when kick hits"
      }
    ],

    "explanation": "I found the issue: your kick peaks at 65Hz and bass fundamental is at 55Hz - they're fighting for the same frequency space.\n\nI've made three changes to separate them:\n\n1. **Reduced sub oscillator** (0.9 → 0.65) - your sub was very hot, now it sits better\n2. **Added high-pass at 30Hz** - removes rumble you can't hear anyway\n3. **Added sidechain compression** - bass ducks 4:1 when kick hits, then releases over 100ms\n\nThe kick now punches through on the transient, and the bass fills in the sustain. Listen for clarity in the low end - you should hear each element distinctly now.\n\nIf the sidechain pumping is too noticeable, I can reduce the ratio or increase the threshold."
  }
}
```

---

## Sources & References (Collaborator Expansion)

### MIDI Generation Research
- [MIDI-LLM (NeurIPS AI4Music 2025)](https://arxiv.org/abs/2511.03942) - Llama 3.2 + MIDI vocabulary expansion
- [MIDI-GPT (Jan 2025)](https://arxiv.org/abs/2501.17011) - Multi-track infilling with attribute control
- [Composer's Assistant 2](https://www.researchgate.net/publication/382459592_Composer's_Assistant_2_Interactive_Multi-Track_MIDI_Infilling_with_Fine-Grained_User_Control) - Fine-grained MIDI control
- [Staccato AI](https://staccato.ai/) - Context-aware MIDI continuation

### Composition Theory
- [LANDR: Drum Programming Guide](https://blog.landr.com/drum-programming/) - 17 essential patterns + free MIDI
- [Native Instruments: 7 Drum Patterns](https://blog.native-instruments.com/drum-patterns/) - Genre coverage
- [EDMProd: Complete Drums Guide](https://www.edmprod.com/drums-guide/) - 6000+ word analysis
- [Hyperbits: Bass Line Writing](https://hyperbits.com/writing-bass-lines/) - Chord-aware construction
- [MusicRadar: Contrapuntal Motion](https://www.musicradar.com/news/practical-music-theory-use-motion-to-make-a-melody-and-bassline-complement-each-other) - Multi-part interaction
- [MusicRadar: Chord Inversions](https://www.musicradar.com/how-to/how-using-chord-inversions-and-different-voicings-can-make-your-music-sound-better) - Voice leading theory

### Tool Use & Integration
- [Max for Live JavaScript API](https://docs.cycling74.com/max8/vignettes/jsliveapi) - LiveAPI object for JS
- [Live Object Model (LOM)](https://docs.cycling74.com/legacy/max8/vignettes/live_object_model) - Complete object hierarchy
- [WebSocket M4L Library](https://github.com/ricardomatias/ableton-live) - Bidirectional communication pattern
- [PyLive (OSC alternative)](https://github.com/ideoforms/pylive) - Python → Ableton via OSC
- [Adam Murray's MIDI Tutorials](https://adammurray.link/max-for-live/js-in-live/generating-midi-clips/) - MIDI clip manipulation examples

---

# PART 3: INTEGRATION ARCHITECTURE (Added 2025-11-29)

## Communication Architecture: WebSocket Approach

### Why WebSocket?

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **WebSocket** | Real-time bidirectional, Python-native, low latency | Needs M4L WebSocket server device | ✅ **CHOSEN** |
| OSC (PyLive) | Simpler setup, established pattern | Slightly higher latency, less flexible | Alternative |
| Direct M4L embed | Everything in one place | Model too large for M4L runtime | ❌ Not feasible |

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ABLETON LIVE 12                                 │
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Drums   │ │   Bass   │ │   Keys   │ │   Lead   │ │    FX    │          │
│  │ (Audio)  │ │ (Serum)  │ │ (Serum)  │ │ (Serum)  │ │ (Return) │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       │            │            │            │            │                 │
│       └────────────┴────────────┴────────────┴────────────┘                 │
│                                 │                                            │
│                    ┌────────────▼────────────┐                              │
│                    │   M4L WebSocket Bridge   │                              │
│                    │   (LiveAPI.amxd)         │                              │
│                    │                          │                              │
│                    │  • Polls track state     │                              │
│                    │  • Sends JSON via WS     │                              │
│                    │  • Receives tool calls   │                              │
│                    │  • Executes LOM commands │                              │
│                    └────────────┬────────────┘                              │
│                                 │                                            │
└─────────────────────────────────┼────────────────────────────────────────────┘
                                  │
                                  │ WebSocket (ws://localhost:9000)
                                  │ JSON messages
                                  │
┌─────────────────────────────────▼────────────────────────────────────────────┐
│                         PYTHON INFERENCE SERVER                              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        QWEN3-4B (MLX)                                │    │
│  │                                                                      │    │
│  │   INPUT:                          OUTPUT:                            │    │
│  │   • Track state JSON              • Reasoning trace                  │    │
│  │   • Audio embeddings (CNN)        • Tool call JSON                   │    │
│  │   • User request text             • Explanation text                 │    │
│  │   • Conversation history                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        CNN AUDIO ENCODER                             │    │
│  │                                                                      │    │
│  │   • Receives audio stems from M4L                                   │    │
│  │   • Generates 512-dim embeddings                                    │    │
│  │   • Passed to LLM via projector                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        WEBSOCKET SERVER                              │    │
│  │                                                                      │    │
│  │   • asyncio + websockets library                                    │    │
│  │   • Handles M4L connection                                          │    │
│  │   • Routes messages to inference                                    │    │
│  │   • Returns tool calls to M4L                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Message Protocol

### M4L → Python: Track State Message

```json
{
  "type": "track_state",
  "timestamp": 1732900000,
  "transport": {
    "tempo": 128,
    "time_signature": [4, 4],
    "playing": true,
    "current_beat": 45.5
  },
  "tracks": [
    {
      "index": 0,
      "name": "Drums",
      "type": "audio",
      "mute": false,
      "solo": false,
      "volume_db": 0.0,
      "pan": 0.0,
      "meter_level": 0.72,
      "clips": [
        {
          "slot": 0,
          "name": "Drums_Main",
          "length": 8.0,
          "playing": true,
          "audio_analysis": {
            "rms": 0.65,
            "spectral_centroid": 2400,
            "low_end_energy": 0.8
          }
        }
      ]
    },
    {
      "index": 1,
      "name": "Bass",
      "type": "midi",
      "mute": false,
      "solo": false,
      "volume_db": -2.0,
      "pan": 0.0,
      "device": {
        "name": "Serum",
        "params": {
          "Osc A Level": 0.8,
          "Osc B Level": 0.0,
          "Sub Level": 0.65,
          "Filter Cutoff": 0.4,
          "Filter Resonance": 0.3,
          "Env 1 Attack": 0.01,
          "Env 1 Decay": 0.3,
          "Env 1 Sustain": 0.7,
          "Env 1 Release": 0.2
        }
      },
      "clips": [
        {
          "slot": 0,
          "name": "Bass_Main",
          "length": 8.0,
          "playing": true,
          "midi_notes": [
            {"pitch": 36, "start": 0.0, "duration": 0.5, "velocity": 100},
            {"pitch": 36, "start": 1.0, "duration": 0.5, "velocity": 95}
          ]
        }
      ]
    }
  ],
  "user_request": "The bass feels weak compared to the drums"
}
```

### Python → M4L: Tool Call Response

```json
{
  "type": "tool_response",
  "request_id": "req_12345",
  "reasoning": "<think>\nAnalyzing the state:\n- Drums have high low-end energy (0.8)\n- Bass sub level is 0.65, which is decent\n- But filter cutoff is only 0.4 - quite closed\n- Bass notes are hitting on beats, same as kick\n\nThe bass is being masked by the drums. Options:\n1. Boost sub level further\n2. Open the filter for more presence\n3. Shift bass timing to off-beats\n\nBest approach: Open filter + slight sub boost + timing shift\n</think>",
  "actions": [
    {
      "tool": "set_serum_param",
      "params": {
        "track": "Bass",
        "param": "Filter Cutoff",
        "value": 0.55
      }
    },
    {
      "tool": "set_serum_param",
      "params": {
        "track": "Bass",
        "param": "Sub Level",
        "value": 0.75
      }
    },
    {
      "tool": "modify_midi",
      "params": {
        "track": "Bass",
        "slot": 0,
        "operation": "shift_timing",
        "offset_beats": 0.5
      }
    }
  ],
  "explanation": "I found the issue: your bass filter was quite closed (0.4), muffling the sound, and the bass was hitting exactly on the kicks.\n\nI've made three changes:\n1. Opened the filter (0.4 → 0.55) for more presence\n2. Boosted sub oscillator (0.65 → 0.75) for more weight\n3. Shifted bass notes to off-beats for rhythmic separation\n\nListen for how the bass now punches between the kicks instead of competing."
}
```

---

## Complete Tool Schema (Based on LOM Research)

### Clip/MIDI Tools

```python
CLIP_TOOLS = {
    "create_clip": {
        "description": "Create a new empty MIDI clip",
        "params": {
            "track": {"type": "str", "description": "Track name"},
            "slot": {"type": "int", "description": "Clip slot index"},
            "length_beats": {"type": "float", "description": "Clip length in beats"}
        },
        "lom_path": "live_set tracks {track_idx} clip_slots {slot}",
        "lom_method": "create_clip",
        "example": {"track": "Bass", "slot": 0, "length_beats": 8.0}
    },

    "write_midi": {
        "description": "Write MIDI notes to a clip (replaces existing notes)",
        "params": {
            "track": {"type": "str"},
            "slot": {"type": "int"},
            "notes": {
                "type": "array",
                "items": {
                    "pitch": "int 0-127 (MIDI note number)",
                    "start": "float (beats from clip start)",
                    "duration": "float (beats)",
                    "velocity": "int 0-127"
                }
            }
        },
        "lom_method": "add_new_notes",
        "example": {
            "track": "Bass",
            "slot": 0,
            "notes": [
                {"pitch": 36, "start": 0.0, "duration": 0.5, "velocity": 100},
                {"pitch": 36, "start": 0.5, "duration": 0.25, "velocity": 80}
            ]
        }
    },

    "append_midi": {
        "description": "Add notes to existing clip without clearing",
        "params": {
            "track": {"type": "str"},
            "slot": {"type": "int"},
            "notes": {"type": "array"}
        },
        "lom_method": "add_new_notes"
    },

    "clear_midi": {
        "description": "Remove all notes from a clip",
        "params": {
            "track": {"type": "str"},
            "slot": {"type": "int"}
        },
        "lom_method": "remove_notes_extended(0, 128, 0, clip_length)"
    },

    "modify_midi": {
        "description": "Transform existing MIDI notes",
        "params": {
            "track": {"type": "str"},
            "slot": {"type": "int"},
            "operation": {
                "type": "enum",
                "values": ["shift_timing", "transpose", "scale_velocity", "quantize"]
            },
            "amount": {"type": "float", "description": "Operation-specific value"}
        },
        "operations": {
            "shift_timing": "Offset all notes by N beats",
            "transpose": "Shift all pitches by N semitones",
            "scale_velocity": "Multiply all velocities by factor",
            "quantize": "Snap to grid (amount = grid size in beats)"
        }
    },

    "get_midi": {
        "description": "Read MIDI notes from a clip",
        "params": {
            "track": {"type": "str"},
            "slot": {"type": "int"}
        },
        "returns": "array of note objects",
        "lom_method": "get_notes_extended(0, 128, 0, clip_length)"
    }
}
```

### Device/Parameter Tools

```python
DEVICE_TOOLS = {
    "set_device_param": {
        "description": "Set any device parameter by name",
        "params": {
            "track": {"type": "str"},
            "device": {"type": "str", "description": "Device name (e.g., 'Serum', 'EQ Eight')"},
            "param": {"type": "str", "description": "Parameter name"},
            "value": {"type": "float", "range": [0.0, 1.0], "description": "Normalized value"}
        },
        "lom_path": "live_set tracks {idx} devices {dev_idx} parameters {param_idx}",
        "example": {"track": "Bass", "device": "Serum", "param": "Filter Cutoff", "value": 0.6}
    },

    "get_device_param": {
        "description": "Read current value of a device parameter",
        "params": {
            "track": {"type": "str"},
            "device": {"type": "str"},
            "param": {"type": "str"}
        },
        "returns": {"value": "float 0-1", "display": "str (formatted value)"}
    },

    "set_serum_param": {
        "description": "Convenience wrapper for Serum parameters",
        "params": {
            "track": {"type": "str"},
            "param": {"type": "str", "description": "Serum parameter name"},
            "value": {"type": "float", "range": [0.0, 1.0]}
        },
        "notes": "Serum must have parameters exposed via Configure Mode",
        "common_params": [
            "Osc A Level", "Osc A Pan", "Osc A Octave", "Osc A Semi", "Osc A Fine",
            "Osc A Unison", "Osc A UniDet", "Osc A UniBlend", "Osc A WTPos",
            "Osc B Level", "Osc B Pan", "Osc B Octave", "Osc B Semi", "Osc B Fine",
            "Sub Level", "Noise Level",
            "Filter Cutoff", "Filter Resonance", "Filter Drive", "Filter Mix",
            "Env 1 Attack", "Env 1 Decay", "Env 1 Sustain", "Env 1 Release",
            "LFO 1 Rate", "LFO 1 Rise", "LFO 1 Delay",
            "Master Volume", "Master Pan"
        ]
    },

    "load_preset": {
        "description": "Load a preset file into a device",
        "params": {
            "track": {"type": "str"},
            "device": {"type": "str"},
            "preset_path": {"type": "str", "description": "Path to .fxp or .SerumPreset file"}
        }
    }
}
```

### Mixer Tools

```python
MIXER_TOOLS = {
    "set_track_volume": {
        "description": "Set track volume in dB",
        "params": {
            "track": {"type": "str"},
            "db": {"type": "float", "range": [-70, 6], "description": "Volume in decibels"}
        },
        "lom_path": "mixer_device volume"
    },

    "set_track_pan": {
        "description": "Set track panning",
        "params": {
            "track": {"type": "str"},
            "pan": {"type": "float", "range": [-1.0, 1.0], "description": "-1=left, 0=center, 1=right"}
        }
    },

    "set_track_mute": {
        "params": {"track": "str", "mute": "bool"}
    },

    "set_track_solo": {
        "params": {"track": "str", "solo": "bool"}
    },

    "set_send_level": {
        "description": "Set send level to return track",
        "params": {
            "track": {"type": "str"},
            "send": {"type": "str", "description": "Send letter (A, B, C, etc.)"},
            "level": {"type": "float", "range": [0.0, 1.0]}
        }
    }
}
```

### Transport Tools

```python
TRANSPORT_TOOLS = {
    "fire_clip": {
        "description": "Trigger a clip to start playing",
        "params": {
            "track": {"type": "str"},
            "slot": {"type": "int"}
        },
        "lom_method": "fire()"
    },

    "stop_clip": {
        "description": "Stop a playing clip",
        "params": {
            "track": {"type": "str"},
            "slot": {"type": "int"}
        },
        "lom_method": "stop()"
    },

    "stop_track": {
        "description": "Stop all clips on a track",
        "params": {"track": "str"},
        "lom_method": "stop_all_clips()"
    }
}
```

---

## M4L WebSocket Bridge Implementation Outline

### JavaScript (controller.js in M4L device)

```javascript
// M4L WebSocket Bridge - controller.js

var ws = null;
var pollInterval = 100;  // ms between state updates

function connect() {
    ws = new WebSocket("ws://localhost:9000");

    ws.onopen = function() {
        post("Connected to inference server\n");
        startPolling();
    };

    ws.onmessage = function(event) {
        var response = JSON.parse(event.data);
        if (response.type === "tool_response") {
            executeActions(response.actions);
        }
    };

    ws.onclose = function() {
        post("Connection closed, reconnecting...\n");
        setTimeout(connect, 1000);
    };
}

function startPolling() {
    new Task(function() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            var state = gatherTrackState();
            ws.send(JSON.stringify(state));
        }
    }).repeat(pollInterval);
}

function gatherTrackState() {
    var api = new LiveAPI("live_set");
    var state = {
        type: "track_state",
        timestamp: Date.now(),
        transport: {
            tempo: api.get("tempo"),
            playing: api.get("is_playing")
        },
        tracks: []
    };

    // Iterate tracks and gather state...
    var trackCount = api.getcount("tracks");
    for (var i = 0; i < trackCount; i++) {
        var track = gatherTrackInfo(i);
        state.tracks.push(track);
    }

    return state;
}

function executeActions(actions) {
    for (var i = 0; i < actions.length; i++) {
        var action = actions[i];
        switch (action.tool) {
            case "set_serum_param":
                setDeviceParam(action.params);
                break;
            case "write_midi":
                writeMidiNotes(action.params);
                break;
            case "modify_midi":
                modifyMidiNotes(action.params);
                break;
            // ... other tools
        }
    }
}

function writeMidiNotes(params) {
    var clipPath = "live_set tracks " + getTrackIndex(params.track) +
                   " clip_slots " + params.slot + " clip";
    var clip = new LiveAPI(clipPath);

    // Clear existing notes
    clip.call("remove_notes_extended", 0, 128, 0, clip.get("length"));

    // Add new notes
    clip.call("add_new_notes", {notes: params.notes});
}

function setDeviceParam(params) {
    var trackIdx = getTrackIndex(params.track);
    var deviceIdx = getDeviceIndex(trackIdx, params.device || "Serum");
    var paramIdx = getParamIndex(trackIdx, deviceIdx, params.param);

    var paramPath = "live_set tracks " + trackIdx +
                    " devices " + deviceIdx +
                    " parameters " + paramIdx;
    var param = new LiveAPI(paramPath);
    param.set("value", params.value);
}
```

### Python Server (inference_server.py)

```python
import asyncio
import websockets
import json
from mlx_lm import load, generate

class InferenceServer:
    def __init__(self, model_path="mlx-community/Qwen3-4B-4bit"):
        self.model, self.tokenizer = load(model_path)
        self.conversation_history = []

    async def handle_connection(self, websocket):
        async for message in websocket:
            state = json.loads(message)

            if state["type"] == "track_state":
                response = await self.process_state(state)
                await websocket.send(json.dumps(response))

    async def process_state(self, state):
        # Build prompt from state
        prompt = self.build_prompt(state)

        # Run inference
        output = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=1024
        )

        # Parse output into reasoning, actions, explanation
        response = self.parse_response(output)
        return response

    def build_prompt(self, state):
        # Format track state + user request into prompt
        system = "You are a music production collaborator..."
        context = json.dumps(state["tracks"], indent=2)
        user_request = state.get("user_request", "Analyze the current arrangement")

        return f"{system}\n\nCurrent State:\n{context}\n\nUser: {user_request}"

    def parse_response(self, output):
        # Extract <think>...</think>, actions, explanation
        # Return structured response
        pass

async def main():
    server = InferenceServer()
    async with websockets.serve(server.handle_connection, "localhost", 9000):
        print("Inference server running on ws://localhost:9000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Audio Streaming for CNN Analysis

For the CNN to analyze audio tracks, we need to stream audio from Ableton:

### Option 1: Periodic Stem Export (Simpler)
- M4L exports short audio buffers (e.g., 1 second) periodically
- Sends as base64 or saves to temp file
- CNN processes offline

### Option 2: Real-time Audio via M4L (Complex)
- Use `pfft~` or `buffer~` objects in M4L
- Extract spectral features in Max
- Send feature vectors via WebSocket
- More efficient but requires Max DSP knowledge

### Recommended Approach

For training data generation, we use Option 1 (stems already rendered).
For live inference, we can start with Option 1 (periodic snapshots) and optimize later.

```javascript
// M4L: Export current audio buffer
function exportTrackAudio(trackIndex, durationSec) {
    var exportPath = "/tmp/track_" + trackIndex + "_analysis.wav";
    // Use render-to-disk or live.object to export
    // Then send path to Python server
    ws.send(JSON.stringify({
        type: "audio_buffer",
        track: trackIndex,
        path: exportPath,
        duration: durationSec
    }));
}
```

---

## Integration with Training Data

The tool schema defined above directly informs how we generate training data:

1. **Tool calls in training examples** must match this exact schema
2. **Context format** mirrors the track_state message structure
3. **LOM paths** are documented for M4L implementation reference

This ensures the fine-tuned model outputs tool calls that the M4L bridge can actually execute.

---

**Part 3 Status**: Added 2025-11-29
**Key Additions**: WebSocket architecture, message protocol, complete tool schema, M4L implementation outline
**Next Steps**: Implement M4L bridge prototype, test tool execution
