# Dataset Curation Strategy for Qwen3-4B Fine-Tuning

**Created**: 2025-11-28
**Purpose**: Transform 4,644 Serum presets into training data that teaches practical parameter manipulation

---

## The Problem We're Solving

Qwen3-4B baseline scores:
- **E1 (MCQ - Parameter ID)**: 80% - Strong conceptual knowledge
- **E2 (Open - Parameter Adjustment)**: 30% - **WEAK** - Fine-tuning target
- **E3 (Scenario - Preset Analysis)**: 60% - Good reasoning

The model knows WHAT parameters are, but struggles with HOW to use them practically.

---

## Question Type Taxonomy (5 Types)

### Type 1: Direct Parameter Queries (20% of dataset)
**Purpose**: Ground truth knowledge of what parameters do

```
Q: "What parameters control the growl in a bass sound?"
A: "The growl comes from a combination of:
   1. Wavetable position (a_wtpos) - moving to more complex wavetables
   2. LFO modulating wavetable position - for movement
   3. Filter resonance (fil_reso 0.5-0.8) - for that nasal quality
   4. Oscillator B detuned slightly against A for thickness"
```

**Validation**: Match Serum's actual behavior, use producer language

---

### Type 2: Sound Goal → Parameter Recipe (35% of dataset)
**Purpose**: Translating aesthetic goals to parameter settings (E2 weakness)

```
Q: "I want a punchy 808 kick that hits hard but decays quickly"
A: "For a punchy 808:
   - Sub oscillator (sub_osc_level: 0.7-0.8) for the fundamental
   - Short attack envelope (env1_atk: 0-5ms) for punch
   - Quick decay (env1_dec: 100-200ms) with sustain at 0
   - Low wavetable position (a_wtpos: 0.0) for pure sine
   - Light saturation on the filter for warmth"
```

**Difficulty Levels**:
| Level | Description | Example |
|-------|-------------|---------|
| Easy | Single-dimension changes | "make it brighter" → filter cutoff |
| Medium | Multi-parameter coordination | "make it fatter" → unison + detuning + sub |
| Hard | Genre-specific techniques | "dubstep wobble" → LFO routing + wavetable + filter automation |

---

### Type 3: Preset Analysis/Explanation (25% of dataset)
**Purpose**: Given actual preset data, explain what's happening

```
Q: "This bass preset has a_wtpos: 0.85, fil_reso: 0.7, a_unison: 4, a_unidet: 0.35. What sound does this create?"
A: "This creates an aggressive, detuned bass sound:
   - High wavetable position (0.85) = complex harmonics, not a pure tone
   - High resonance (0.7) = pronounced, nasal midrange character
   - 4-voice unison with 0.35 detune = very wide, thick sound
   This would work well for dubstep or heavy bass music - it's designed to cut through a mix with attitude."
```

---

### Type 4: Comparative/Adjustment Requests (15% of dataset)
**Purpose**: Teaching relative thinking, not absolute values

```
Q: "This lead sounds too thin. Current settings: a_unison: 1, a_unidet: 0, a_octave: 0. How do I fatten it up?"
A: "To fatten a thin lead:
   1. Add unison voices (1 → 4 or more)
   2. Add slight detune (0.1-0.2) for width
   3. Consider adding Oscillator B an octave down (b_octave: -1)
   4. Layer with sub oscillator if you need low-end weight

   Start with unison + detune - that's the quickest path to thickness."
```

---

### Type 5: Genre/Style Templates (5% of dataset)
**Purpose**: Holistic sound design for common use cases

```
Q: "Set up a future bass supersaw chord preset"
A: "Future bass supersaw recipe:
   - Both oscillators on saw wavetable (a_wtpos: 0, b_wtpos: 0)
   - High unison on both (a_unison: 7, b_unison: 7)
   - Moderate detune (a_unidet: 0.15-0.25)
   - Osc B slightly detuned from A (b_fine: +/- 5 cents)
   - Filter cutoff modulated by envelope for movement
   - Reverb for space, slight chorus for shimmer"
```

---

## Producer Language Guidelines

### Use These Phrases:
| Producer Term | Technical Meaning |
|---------------|-------------------|
| "punchy" | fast attack/decay, compression |
| "thick/fat" | unison, detuning, layering |
| "aggressive/angry" | distortion, high resonance, complex wavetables |
| "smooth/warm" | low pass filter, sine-based, slow attack |
| "growl" | wavetable modulation, resonance, formant-like |
| "plucky" | short attack/decay envelope |
| "airy/breathy" | noise layer, high frequencies, reverb |
| "squelchy" | high resonance, filter movement |
| "wide" | stereo spread, unison, pan modulation |
| "tight" | mono, short release, no reverb |

### Anti-Patterns to Avoid:
- ❌ "Adjust the oscillator amplitude envelope attack time parameter"
- ✅ "Shorten the attack so it hits faster"
- ❌ "The frequency cutoff of the low-pass filter"
- ✅ "Roll off the highs with the filter"

---

## Difficulty Distribution

| Difficulty | % of Dataset | Rationale |
|------------|--------------|-----------|
| **Easy** | 25% | Foundation - single parameter changes |
| **Medium** | 45% | Core competency - multi-param coordination |
| **Hard** | 25% | Mastery - complex sound design chains |
| **Expert** | 5% | Edge cases - unusual techniques |

---

## Data Generation Strategy: Tiered LLM Approach (REVISED 2025-11-29)

**⚠️ UPDATE**: Template-based generation is being replaced with tiered LLM generation.

### Tiered Model Selection via Batch API

| Tier | Model | Task Types | % of Data | Batch Cost |
|------|-------|-----------|-----------|------------|
| 1 | **Haiku 3.5** | Simple queries, basic descriptions | 40% | ~$3.60 |
| 2 | **Sonnet 4.5** | Modifications, comparisons, context | 45% | ~$20.25 |
| 3 | **Opus 4.5** | Complex workflows, troubleshooting | 15% | ~$20.25 |

**Total Est. Cost**: ~$44.10 for 10,000 Q&A pairs via Batch API (50% discount)

### Task-to-Model Mapping

```
TIER 1 - Haiku 3.5 (Simple):
├── sound_description (basic)
├── parameter_identification (single param)
└── direct queries ("What is X?")

TIER 2 - Sonnet 4.5 (Medium):
├── sound_modification (multi-param)
├── preset analysis with reasoning
├── comparison questions
├── musical_context recommendations
└── sound_matching (how to recreate)

TIER 3 - Opus 4.5 (Complex):
├── genre-specific synthesis techniques
├── complex troubleshooting scenarios
├── multi-step sound design workflows
├── advanced MIDI-aware reasoning
└── edge cases and unusual techniques
```

### Implementation Files
- **Generator Script**: `generate_qa_with_llm.py`
- **Task Type Definitions**: 8 task types with system prompts per type
- **Batch API Integration**: Async processing with 50% cost savings

### Why This Approach

1. **Quality-Cost Optimization**: Opus only for complex reasoning
2. **Diversity**: Different models produce varied phrasing
3. **Validation Built-In**: LLM understands domain context
4. **Scalable**: Batch API handles 100K requests per batch

See: [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md#decision-7-tiered-llm-qa-generation-strategy)

---

### Pre-Generation Step: External Hard Drive Scan

**IMPORTANT**: Before running expensive batch generation, scan external drives for more data:

```bash
python scan_sample_packs.py --scan-external
```

Why? More MIDI-preset pairs and project files = better Q&A context

See: [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md#decision-8-external-hard-drive-data-scan-next-priority)

---

## Sample Size Targets

| Approach | Examples | Notes |
|----------|----------|-------|
| Minimum | ~4,600 | 1 Q&A per preset |
| **Recommended** | ~14,000 | 3 Q&A per preset |
| Maximum | ~23,000 | 5 Q&A per preset |

Sweet spot for LoRA fine-tuning: **10-15k high-quality examples**

---

## Validation Pipeline

1. **Parameter Accuracy**: Values within Serum's valid ranges
2. **Causal Correctness**: "X causes Y" statements technically accurate
3. **Language Quality**: Producer vocabulary, not engineering jargon
4. **Diversity Check**: No more than 5% identical phrasings
5. **Coverage Check**: All major parameter categories represented

---

## Integration with Preset Data

Each preset provides:
- `preset_name`: Context for genre/style
- `categorization.instrument.type`: bass, lead, pad, etc.
- `categorization.genre`: trap, dubstep, etc. (when available)
- `parameters.tier_1_essential`: ~21 key parameters
- `synthesis_analysis.complexity`: simple/complex

Use these fields to generate contextually appropriate Q&A pairs.

---

---

## Preset Data Schema (from ultimate_serum_dataset_expanded.json)

```python
{
    "format": "fxp_converted",
    "source_file": "/path/to/preset.fxp",
    "preset_name": "BASS - Heavy Wobble",
    "parameters": {
        # 2,397 parameters - key ones for training:
        "a_wtpos": 0.0-1.0,      # Osc A wavetable position
        "a_unison": 1-16,         # Unison voices
        "a_unidet": 0.0-1.0,      # Unison detune
        "a_octave": -4 to +4,     # Octave shift
        "b_wtpos": 0.0-1.0,       # Osc B wavetable position
        "fil_cutoff": 0.0-1.0,    # Filter cutoff
        "fil_reso": 0.0-1.0,      # Filter resonance
        "env1_atk": 0.0-1.0,      # Amp env attack
        "env1_dec": 0.0-1.0,      # Amp env decay
        "env1_sus": 0.0-1.0,      # Amp env sustain
        "env1_rel": 0.0-1.0,      # Amp env release
        "sub_osc_level": 0.0-1.0, # Sub oscillator level
        # ... 2385 more parameters
    },
    "analysis": {
        "instrument_type": "Bass",  # Bass, Lead, Pad, FX, Arp, Keys, Unknown
        "characteristics": ["bass-heavy", "aggressive"],
        "complexity_score": 0.22,
        "parameter_stats": {...}
    }
}
```

**Preset Distribution** (7,583 total):
- Unknown: 5,286 (69.7%)
- Bass: 1,651 (21.8%)
- Lead: 308 (4.1%)
- Pad: 148 (2.0%)
- FX: 72 (0.9%)
- Arp: 70 (0.9%)
- Keys: 48 (0.6%)

---

## Audio File Mapping

Audio files are organized as:
```
data/rendered_audio/{category}/{preset_name}___{note}.wav
data/mel_specs/{category}/{preset_name}___{note}.npy
```

Example: `data/rendered_audio/bass/16_bass_02___________________C3.wav`

Each preset has ~12 notes rendered (C1-C5 typical), giving 111,732 total audio files.

---

## Template Generator Specifications

### Template Structure (Python)

```python
# templates.py

TEMPLATES = {
    "type1_direct_query": [
        {
            "template": "What parameters control the {sound_quality} in a {instrument_type} sound?",
            "answer_template": "The {sound_quality} comes from: {parameter_explanation}",
            "variables": ["sound_quality", "instrument_type"],
            "difficulty": "easy"
        },
        {
            "template": "How do I add more {sound_quality} to my {instrument_type}?",
            "answer_template": "To add {sound_quality}: {step_by_step}",
            "variables": ["sound_quality", "instrument_type"],
            "difficulty": "medium"
        },
    ],

    "type2_sound_goal": [
        {
            "template": "I want a {adjective} {instrument_type} that {characteristic}",
            "answer_template": "For a {adjective} {instrument_type}:\n{parameter_recipe}",
            "variables": ["adjective", "instrument_type", "characteristic"],
            "difficulty": "medium"
        },
    ],

    "type3_preset_analysis": [
        {
            "template": "This {instrument_type} preset has {param_summary}. What sound does this create?",
            "answer_template": "This creates a {sound_description}:\n{parameter_breakdown}",
            "variables": ["instrument_type", "param_summary"],
            "difficulty": "medium"
        },
    ],

    "type4_adjustment": [
        {
            "template": "This {instrument_type} sounds too {problem}. Current settings: {current_params}. How do I fix it?",
            "answer_template": "To fix the {problem}:\n{adjustment_steps}",
            "variables": ["instrument_type", "problem", "current_params"],
            "difficulty": "medium"
        },
    ],

    "type5_genre": [
        {
            "template": "Set up a {genre} {instrument_type} preset",
            "answer_template": "{genre} {instrument_type} recipe:\n{full_recipe}",
            "variables": ["genre", "instrument_type"],
            "difficulty": "hard"
        },
    ]
}

# Sound quality mappings
SOUND_QUALITIES = {
    "growl": {
        "params": ["a_wtpos", "fil_reso", "lfo1_rate"],
        "explanation": "Wavetable position (a_wtpos > 0.5) + high resonance + LFO modulation"
    },
    "punch": {
        "params": ["env1_atk", "env1_dec", "fil_cutoff"],
        "explanation": "Fast attack (< 5ms) + quick decay + filter envelope"
    },
    "width": {
        "params": ["a_unison", "a_unidet", "a_pan"],
        "explanation": "Unison voices (4+) + moderate detune (0.1-0.3)"
    },
    "warmth": {
        "params": ["fil_cutoff", "a_wtpos", "sub_osc_level"],
        "explanation": "Low-pass filter + sine-based wavetable + sub oscillator"
    },
    # ... more mappings
}

# Genre templates
GENRE_RECIPES = {
    "dubstep_bass": {
        "a_wtpos": "0.5-0.9 (complex harmonics)",
        "fil_reso": "0.6-0.8 (nasal, aggressive)",
        "a_unison": "4-8 voices",
        "lfo1_rate": "1-8 Hz (wobble speed)",
        # ...
    },
    "future_bass_chord": {
        "a_wtpos": "0.0 (saw)",
        "a_unison": "7-8 voices",
        "a_unidet": "0.15-0.25",
        # ...
    },
    # ... more genres
}
```

---

## Claude Prompt Template for Expansion

```
You are helping generate training data for a music production AI assistant.
Given a Serum preset with the following parameters, generate a natural-sounding
Q&A pair that teaches practical sound design.

PRESET INFO:
- Name: {preset_name}
- Type: {instrument_type}
- Key Parameters:
  {param_list}

Generate a {question_type} Q&A pair at {difficulty} difficulty level.

GUIDELINES:
1. Use producer vocabulary (punchy, fat, growl, squelchy) not engineering jargon
2. Be specific about parameter values and their effects
3. Explain WHY each parameter contributes to the sound
4. Keep answers concise but complete (3-6 bullet points)

Output as JSON:
{
  "question": "...",
  "answer": "...",
  "difficulty": "{difficulty}",
  "type": "{question_type}",
  "preset_source": "{preset_name}"
}
```

---

## Tier 1 Essential Parameters (21 params for training focus)

These are the highest-impact parameters that should appear most frequently:

| Parameter | Range | Sound Effect |
|-----------|-------|--------------|
| `a_wtpos` | 0-1 | Timbre brightness/complexity |
| `a_unison` | 1-16 | Thickness, width |
| `a_unidet` | 0-1 | Detuning, chorus effect |
| `a_octave` | -4 to +4 | Pitch range |
| `b_wtpos` | 0-1 | Second oscillator timbre |
| `b_level` | 0-1 | Osc B volume |
| `fil_cutoff` | 0-1 | Brightness |
| `fil_reso` | 0-1 | Nasal/squelchy character |
| `fil_type` | enum | Filter character |
| `env1_atk` | 0-1 | Punch vs smooth |
| `env1_dec` | 0-1 | Plucky vs sustained |
| `env1_sus` | 0-1 | Sustained level |
| `env1_rel` | 0-1 | Note tail |
| `env2_amt` | 0-1 | Filter envelope depth |
| `lfo1_rate` | 0-1 | Modulation speed |
| `lfo1_amt` | 0-1 | Modulation depth |
| `sub_osc_level` | 0-1 | Low-end weight |
| `noise_level` | 0-1 | Air/texture |
| `fx_dist_amt` | 0-1 | Aggression/saturation |
| `fx_reverb_mix` | 0-1 | Space |
| `master_vol` | 0-1 | Output level |

---

---

## 🎯 PART 2: Realistic Producer Communication (Added 2025-11-29)

**The Problem**: Templates produce sterile, uniform prompts that don't reflect how real producers talk.

Real producers range from hyper-verbose to barely coherent:

```
VERBOSE: "Hey so I've got this bass preset but it's sounding kind of
muddy in the low mids and I want it to cut through the mix better,
especially when the kick hits. What parameters should I be tweaking?"

LAZY: "bass muddy fix"

TECHNICAL: "Reduce ENV1 attack to 5ms, increase FLT1 resonance to 0.7"

VAGUE: "make it sound more future bass-y you know?"

FRUSTRATED: "why does this sound like trash"

COMPARATIVE: "I want it to sound like that one Skrillex bass, you know the one"
```

---

### Producer Communication Archetypes

#### Archetype 1: The Verbose Explainer (15%)
**Characteristics:**
- Provides full context
- Describes the problem AND desired outcome
- Often includes what they've already tried
- May ramble or over-explain

**Example Prompts:**
```
"So I'm working on this track and I have this lead sound that's pretty
nice but it feels kind of static, like it doesn't move enough. I tried
adding some LFO modulation but it made it sound wobbly in a bad way.
I want it to feel alive but still be usable as a main lead. What would
you suggest?"

"Okay so this is kind of a weird request but I'm trying to recreate
this sound I heard in a track, it was like a plucky bass but with
this metallic quality to it, almost like someone was hitting a pipe
or something. My current preset is way too soft and round."

"I've been tweaking this for like an hour and I can't figure out why
it sounds so thin. I've got the unison set to 4 voices and the detune
is at like 30% but it still doesn't have that big fat supersound feel."
```

#### Archetype 2: The Terse Minimalist (25%)
**Characteristics:**
- Bare minimum words
- Expects AI to fill in context
- Often just states the problem, not the goal
- May use fragments or single words

**Example Prompts:**
```
"too bright"
"needs more low end"
"attack slower"
"more movement"
"sounds cheap"
"make it wider"
"punch"
"thicken this"
"less harsh"
"wobble"
"future bass that shit"
"dubstep it up"
```

#### Archetype 3: The Technical Producer (20%)
**Characteristics:**
- Uses correct parameter names
- Knows what they want technically
- May ask for specific values
- Sometimes over-specific

**Example Prompts:**
```
"Reduce the filter envelope decay to around 200ms"
"Set OSC A detune to +7 cents and OSC B to -7 cents"
"Route LFO 2 to filter cutoff with 50% depth at 1/4 sync"
"What's the FM modulation depth currently set to?"
"Increase the sub oscillator by about 6dB"
"Add a gentle HPF around 80Hz to clean up the low end"
```

#### Archetype 4: The Vague Describer (20%)
**Characteristics:**
- Uses subjective/emotional language
- References vibes, feelings, genres
- Struggles to articulate technically
- Common among newer producers

**Example Prompts:**
```
"make it sound more professional"
"it needs to feel more alive"
"I want it to be dark but not too dark"
"give it that modern sound"
"make it breathe more"
"it sounds too digital"
"needs more soul"
"too vanilla"
"something's off but I can't tell what"
"warmer but still present"
```

#### Archetype 5: The Reference Chaser (10%)
**Characteristics:**
- References specific artists/songs
- Wants to recreate existing sounds
- May provide incorrect technical descriptions
- Common for bass music producers

**Example Prompts:**
```
"I want it to sound like that Virtual Riot bass"
"you know that Illenium pluck? That vibe"
"make it more Disclosure-y"
"like a Skrillex growl but not exactly"
"Porter Robinson supersaw vibes"
"that Flume organic feel"
"deadmau5 lead tone"
```

#### Archetype 6: The Frustrated Troubleshooter (10%)
**Characteristics:**
- Something's wrong and they're annoyed
- Often blame the tool not themselves
- Need diagnosis not just solutions
- Emotional language

**Example Prompts:**
```
"why does this sound like garbage"
"this preset is broken"
"it was working fine yesterday wtf"
"everything I do makes it worse"
"how do I fix this mess"
"why is there so much noise"
"it keeps clipping and I don't know why"
"this sounds nothing like the preview"
```

---

### Scenario Categories (Beyond Simple Q&A)

#### Category A: Sound Modification Tasks (40%)
**Subcategories:**
1. **Tonal Adjustment** - brightness, warmth, darkness
2. **Dynamic Shaping** - attack, sustain, punch
3. **Spatial Enhancement** - width, depth, stereo image
4. **Movement/Modulation** - adding life, wobble, rhythm
5. **Cleanup** - removing harshness, muddiness, noise

#### Category B: Sound Design Goals (25%)
**Subcategories:**
1. **Genre-Specific** - "make it dubstep", "house stab vibes"
2. **Instrument Emulation** - "more like a real piano", "guitar-like"
3. **Mood/Emotion** - "darker", "happier", "aggressive"
4. **Production Context** - "needs to sit in mix", "too dominant"

#### Category C: Troubleshooting (15%)
**Subcategories:**
1. **Diagnostic** - "why does it sound like X"
2. **Comparison** - "doesn't match the preview"
3. **Undo** - "I messed it up, how to fix"
4. **Conflict Resolution** - "clashes with my kick"

#### Category D: Educational/Exploratory (10%)
**Subcategories:**
1. **Parameter Learning** - "what does X do"
2. **Technique Queries** - "how do I make Y"
3. **Best Practices** - "should I do X or Y"
4. **Sound Analysis** - "describe this preset"

#### Category E: Composition & Arrangement (10%)
**Subcategories:**
1. **MIDI Writing** - "write a bass line"
2. **Pattern Design** - "need a drum pattern"
3. **Harmonic Help** - "what chords work here"
4. **Arrangement Advice** - "how should this drop hit"

---

### Response Format Variations

The model needs to handle varied inputs AND produce appropriate outputs:

#### Response Type 1: Direct Action + Brief Explanation
**For:** Terse inputs, clear intent
```json
{
  "reasoning": "<think>User wants brightness reduced. High filter cutoff and resonance likely culprits.</think>",
  "actions": [
    {"tool": "set_serum_param", "params": {"param": "FLT1_CUTOFF", "value": 0.45}},
    {"tool": "set_serum_param", "params": {"param": "FLT1_RES", "value": 0.2}}
  ],
  "explanation": "Rolled off the filter cutoff and dropped the resonance - should tame those highs."
}
```

#### Response Type 2: Diagnostic + Clarifying Question
**For:** Vague inputs, unclear intent
```json
{
  "reasoning": "<think>User says 'sounds cheap' - could mean many things. Need to narrow down.</think>",
  "actions": [],
  "explanation": "Couple things could make it sound 'cheap' - is it thin and lacking body, harsh and digital, or just not sitting right in the mix? Knowing which one helps me fix it better."
}
```

#### Response Type 3: Multi-Step Solution + Education
**For:** Complex modifications, learning opportunity
```json
{
  "reasoning": "<think>User wants 'movement' - likely needs modulation. Will add subtle LFO to cutoff and explain why.</think>",
  "actions": [
    {"tool": "set_serum_param", "params": {"param": "LFO1_RATE", "value": "1/4"}},
    {"tool": "set_serum_param", "params": {"param": "LFO1_DEPTH_TO_FLT1", "value": 0.25}}
  ],
  "explanation": "Added a synced LFO gently modulating the filter - this creates that subtle breathing motion without making it wobbly. Try different rates (1/8, 1/2) to see what fits your track's tempo."
}
```

#### Response Type 4: Reference Translation
**For:** Artist/song references
```json
{
  "reasoning": "<think>User wants 'Virtual Riot bass' - heavy FM, aggressive movement, growl character. Need to add FM and distortion.</think>",
  "actions": [
    {"tool": "set_serum_param", "params": {"param": "OSC_A_FM_DEPTH", "value": 0.6}},
    {"tool": "set_serum_param", "params": {"param": "FX_DIST_DRIVE", "value": 0.7}},
    {"tool": "set_serum_param", "params": {"param": "LFO1_RATE", "value": "1/8"}}
  ],
  "explanation": "Virtual Riot's signature is heavy FM modulation and aggressive movement. I've cranked the FM depth and added distortion for that growl. The LFO adds that rhythmic character."
}
```

---

### Prompt Generation Strategy (Revised)

#### Phase 1: Archetype-Based Generation
Generate prompts from each archetype's perspective:

```python
ARCHETYPE_TEMPLATES = {
    "verbose_explainer": {
        "patterns": [
            "So I'm working on this {instrument} and {problem_description}. I tried {attempted_solution} but {result}. What would you suggest?",
            "Okay so this is kind of a {qualifier} request but I'm trying to {goal}. My current preset {current_state}.",
            "I've been {action_verb} this for {time_period} and I can't figure out why {problem}. I've got {current_settings} but {result}."
        ],
        "fillers": {
            "qualifier": ["weird", "specific", "unusual", "particular"],
            "time_period": ["like an hour", "ages", "way too long", "a while now"],
            "action_verb": ["tweaking", "messing with", "adjusting", "playing with"]
        }
    },
    "terse_minimalist": {
        "patterns": [
            "too {adjective}",
            "{adjective}",
            "less {adjective}",
            "more {adjective}",
            "{verb} this",
            "{adjective} it up",
            "{noun}"
        ],
        "fillers": {
            "adjective": ["bright", "harsh", "muddy", "thin", "weak", "boring", "static"],
            "verb": ["thicken", "widen", "punch", "fatten", "clean"],
            "noun": ["punch", "width", "depth", "movement", "wobble", "growl"]
        }
    },
    # ... other archetypes
}
```

#### Phase 2: LLM-Augmented Variation
Use Claude to generate realistic variations:

```python
VARIATION_PROMPT = """
Given this base request: "{base_prompt}"

Generate 10 variations that real producers might say, varying:
1. Verbosity (1-word to full paragraph)
2. Technical precision (vague to specific)
3. Emotional tone (neutral, frustrated, curious)
4. Context inclusion (none, some, full)

Keep them realistic - producers are human, they misspell, use slang, and ramble.
Don't be too polished.

Examples of realistic variations:
- "yo this is way too [X]"
- "can u make it more [adjective]?"
- "ugh its still not right... needs more [quality]"
"""
```

#### Phase 3: Context-Aware Scenarios
Include realistic musical context:

```python
scenario = {
    "preset_name": "Heavy Wobble Bass",
    "preset_category": "Bass > Dubstep",
    "current_params": {...},  # Actual Serum state
    "track_context": {
        "genre": "dubstep",
        "tempo": 150,
        "key": "F minor",
        "section": "drop",
        "other_elements": ["sub bass", "snare hits", "vocal chops"]
    },
    "user_request": "too harsh when the vocal comes in",
    "history": [  # Multi-turn context
        {"user": "make it more aggressive", "assistant": "...", "actions": [...]},
        {"user": "good but now it's clashing with vocals", "assistant": "..."}
    ]
}
```

#### Phase 4: Persona-Based Generation
Generate from different producer perspectives:

```python
PRODUCER_PERSONAS = {
    "bedroom_producer": {
        "experience": "1-2 years",
        "vocabulary": "limited technical, heavy slang",
        "patience": "wants quick fixes",
        "style": "asks simple questions, gets confused easily",
        "common_phrases": ["yo can you", "make it more", "why is it", "how do I"]
    },
    "semi_pro": {
        "experience": "3-5 years",
        "vocabulary": "mixed technical and vibe-based",
        "patience": "willing to learn",
        "style": "asks why, references artists",
        "common_phrases": ["like that [artist] sound", "what if I", "should I use"]
    },
    "professional": {
        "experience": "5+ years",
        "vocabulary": "precise technical",
        "patience": "knows what they want",
        "style": "direct, efficient, rarely asks basic questions",
        "common_phrases": ["set the", "adjust", "route X to Y", "increase by"]
    }
}
```

---

### Distribution Targets (Revised)

| Archetype | % of Dataset | Primary Model |
|-----------|-------------|---------------|
| Verbose Explainer | 15% | Sonnet |
| Terse Minimalist | 25% | Haiku |
| Technical Producer | 20% | Haiku/Sonnet |
| Vague Describer | 20% | Sonnet |
| Reference Chaser | 10% | Opus |
| Frustrated Troubleshooter | 10% | Sonnet |

| Scenario Category | % of Dataset | Primary Model |
|-------------------|-------------|---------------|
| Sound Modification | 40% | Haiku/Sonnet |
| Sound Design Goals | 25% | Sonnet/Opus |
| Troubleshooting | 15% | Sonnet |
| Educational | 10% | Haiku |
| Composition | 10% | Opus |

---

### Quality Assurance

#### Response Validation Criteria:
1. **Action Validity** - Are the parameter names real? Are values in range?
2. **Reasoning Quality** - Does the thinking make musical sense?
3. **Explanation Clarity** - Is it understandable to the prompt's archetype?
4. **Consistency** - Does the action match the explanation?
5. **Archetype Appropriateness** - Does response style match input style?

#### Automated Checks:
```python
def validate_response(response, preset_params, archetype):
    """Validate generated Q&A pairs"""
    # Check all param names are valid Serum params
    for action in response.get("actions", []):
        if action["tool"] == "set_serum_param":
            assert action["params"]["param"] in VALID_SERUM_PARAMS
            assert is_valid_value(action["params"]["value"])

    # Check reasoning mentions relevant musical concepts
    reasoning = response.get("reasoning", "")
    assert any(concept in reasoning.lower() for concept in
               ["brightness", "attack", "filter", "tone", "frequency", "muddy", ...])

    # Check explanation length matches archetype expectations
    explanation = response.get("explanation", "")
    if archetype == "terse_minimalist":
        assert len(explanation.split()) < 50  # Keep it brief
    elif archetype == "verbose_explainer":
        assert len(explanation.split()) > 30  # Give them detail
```

---

### Cost Estimate (Revised for 50K pairs)

| Tier | Model | % of 50K | Est. Tokens | Batch Cost |
|------|-------|----------|-------------|------------|
| Simple | Haiku 3.5 | 35% | 17.5M in / 8.75M out | ~$14 |
| Medium | Sonnet 4.5 | 50% | 25M in / 12.5M out | ~$130 |
| Complex | Opus 4.5 | 15% | 7.5M in / 3.75M out | ~$190 |

**Total Estimated: ~$334 for 50K high-quality Q&A pairs via Batch API**

With validation filtering (~80% pass rate): ~40K usable pairs

---

## Next Steps

1. [x] Document preset data schema
2. [x] Define template generator specs
3. [x] Create Claude prompt template
4. [x] Map essential parameters
5. [x] **Define producer archetypes (NEW)**
6. [x] **Define scenario categories (NEW)**
7. [x] **Define response format variations (NEW)**
8. [ ] Update `generate_qa_with_llm.py` with archetype routing
9. [ ] Implement Batch API support
10. [ ] Generate pilot batch (500 examples across all archetypes)
11. [ ] Human review for archetype authenticity
12. [ ] Scale to full 50K dataset
