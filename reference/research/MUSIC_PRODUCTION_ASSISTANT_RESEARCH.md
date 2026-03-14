# AI Music Production Assistant Research Document
**Last Updated**: December 6, 2025  
**Project Goal**: End-to-end music production assistant using Qwen3-4B reasoning LLM  
**Target Platform**: M4 Max MacBook Pro (128GB unified memory)

---

## Executive Summary

Building an AI assistant that actively helps with writing, mixing, and mastering in Ableton Live Suite 12. The approach combines self-play RL (Noam Brown style) with spatial audio understanding. Key components:

1. **Ableton control harness** - MCP-based programmatic DAW control
2. **Optimal mix dataset** - Training targets for optimization
3. **Spatial audio representation** - Beyond 2D spectrograms (binaural/HRTF)
4. **Plugin Parameter Observatory** - 1:1 parameter mapping between plugins

---

## Part 1: Spatial Audio Understanding

### 1.1 VSX Technology Analysis

Slate Digital VSX uses standard binaural room impulse response (BRIR) + HRTF processing:

**Signal Chain**:
```
Stereo Input → Speaker Frequency Response Modeling → BRIR Convolution (room reflections) 
→ HRTF Application (interaural cues) → Headphone Compensation → Binaural Output
```

**Key Components**:
- E.C.C.O. system calibrates 2-4kHz ear canal resonance
- Two HRTF profiles (A/B) for different ear shapes
- No public API/SDK - functions as standard AU/VST3 plugin

**Capture Method**: Custom macOS app using AVAudioEngine framework:
```swift
// Host VSX as Audio Unit with tap on output node
let engine = AVAudioEngine()
let vstNode = AVAudioUnitEffect(audioComponentDescription: vsxDescription)
engine.attach(vstNode)
engine.connect(engine.mainMixerNode, to: vstNode, format: format)
// Install tap on output for capture
vstNode.installTap(onBus: 0, bufferSize: 4096, format: format) { buffer, time in
    // Capture binaural output
}
```

Supports offline manual rendering mode for batch processing (faster than real-time).

### 1.2 BAT Architecture Adaptation

The Binaural Audio Transformer (BAT) from zhishengzheng.com/bat/ demonstrates spatial audio + LLM reasoning integration:

**Original BAT**: Spatial-AST encoder processes mel-spectrograms + Interaural Phase Difference (IPD) features, connects to LLaMA-2 7B for spatial reasoning.

**Adaptation Mapping for Music Production**:
| BAT Capability | Music Production Application |
|----------------|------------------------------|
| Sound event localization | Stereo field analysis, pan position detection |
| Distance estimation | Reverb depth analysis, instrument "closeness" |
| Multi-source separation | Frequency masking detection between tracks |
| Spatial reasoning | Mix coherence evaluation |

### 1.3 MEGAMI Architecture (Sony, Nov 2024)

More directly applicable: **MEGAMI (Multitrack Embedding Generative Auto Mixing)**

- Conditional diffusion model in effect embedding space
- Permutation-equivariant transformer (~70M params) + track-agnostic effect processor (~9M params)
- Key innovation: Domain adaptation via CLAP embedding space enables training on wet stems only

**MEGAMI Representation Template**:
```python
representation = {
    "per_track": {
        "effect_embedding": "2048-dim FxEncoder++ embeddings",
        "dynamics": ["log-RMS", "crest_factor", "dynamic_spread", "stereo_width", "stereo_imbalance"],
        "spectral": "Fourier feature expansion to 64 dimensions"
    },
    "inter_track": {
        "frequency_masking": "Pairwise frequency masking matrices",
        "phase_correlation": "Phase correlation between tracks"
    }
}
```

---

## Part 2: Ableton Control Infrastructure

### 2.1 Ableton MCP (Model Context Protocol)

**Primary Implementation**: AbletonMCP_Extended Remote Script

**Installation**:
```bash
# Copy harness/AbletonMCP_Extended/ to Ableton Remote Scripts directory
```

**Architecture**:
```
AI Model → MCP Server (Python) → Socket → Ableton Remote Script → Live API
```

**Capabilities** (including PR #26 additions):
- Track manipulation (create, delete, rename)
- Instrument/effect loading
- MIDI clip creation
- Parameter control
- Session control
- Return tracks and send levels
- Track volume control
- Comprehensive device parameter control
- EQ Eight precision control

### 2.2 AbletonOSC Alternative

**Repository**: ideoforms/AbletonOSC (637 stars, MIT license)

**PyLive Wrapper** provides Pythonic interface to Live Object Model (LOM):
```python
import live
set = live.Set()
set.scan()
for track in set.tracks:
    for device in track.devices:
        for param in device.parameters:
            print(f"{track.name}/{device.name}/{param.name}: {param.value}")
```

**LOM Path Notation**: `live_set tracks 0 devices 0 parameters 1`

### 2.3 Batch Export Challenge

Ableton lacks native scripting for audio export. Workarounds:
1. GUI automation (pyautogui) - fragile
2. Custom Max for Live device for internal audio capture to buffer

---

## Part 3: Training Datasets

### 3.1 MixAssist Dataset

**Location**: https://huggingface.co/datasets/mclemcrew/MixAssist

**Stats**:
- 640 total rows (340 train / 50 validation / 250 test)
- Multi-turn expert/amateur dialogue from 7 collaborative mixing sessions (12 producers)
- 431 audio-grounded conversational turns

**Structure**:
```python
from datasets import load_dataset
dataset = load_dataset("mclemcrew/MixAssist")
# Filter for substantive responses
substantive = dataset.filter(lambda x: x['has_content'] == True)
```

**Value**: Audio-grounded instruction pairs, multi-turn dialogue captures iterative mixing decisions, expert reasoning with substantive responses.

### 3.2 MixologyDB / MixParams Dataset

**Location**: https://huggingface.co/datasets/mclemcrew/MixologyDB  
**GitHub**: https://github.com/mclemcrew/MixologyDB

**Current Status**: Only 1 mix visible (will contain 114 mixes when complete)

**Structure**:
```json
{
  "mix-name": "Song_v1",
  "song-name": "Song Title",
  "artist-name": "Artist",
  "genre": "Rock",
  "mix evaluation": [
    {"score": 0.85, "description": "Good separation, clear vocals"}
  ],
  "tracks": [
    {
      "track-name": "KOut",
      "track-type": "AUDIO",
      "channel-mode": "MONO",
      "parameters": {
        "gain": 0.7,
        "pan": [0],
        "eq": [
          {"type": "HP", "value": {"freq": 31.3, "q": 18, "gain": null}},
          {"type": "NOTCH", "value": {"freq": 80, "q": 1.44, "gain": 5.1}}
        ],
        "reverb": [{"name": "LexRoom", "type": "ROOM", "gain": -11.1, "pan": [0]}],
        "compression": {
          "name": "BF-76", "attack": 3.1, "release": 7,
          "input": 24.5, "output": 21.5, "ratio": "4:1"
        }
      }
    }
  ]
}
```

**Audio Sources**: Mix Evaluation Dataset, Mixing Secrets, Weathervane, Open Multitrack Testbed (external resources, not included).

### 3.3 Critical Dataset Compatibility Issue

**MixologyDB is NOT Ableton-compatible.** Parameters are from Logic Pro, Pro Tools, or Reaper.

| Aspect | MixologyDB | Ableton MCP |
|--------|------------|-------------|
| EQ Type | String: "HP", "NOTCH", "LP" | Numeric index via '1 Filter Type A' (0-7) |
| Frequency | Absolute Hz: 514.6, 80, 2860 | **Normalized 0-1** (log scale 10Hz-22kHz) |
| Q/Resonance | Absolute: 1.44, 3.97, 18 | **Normalized 0-1** |
| Gain | dB values: 5.1, -6.6 | Normalized or different dB range |
| Parameter Names | Generic: freq, q, gain | Ableton-specific: '1 Frequency A', '1 Gain A' |
| Plugins | "BF-76", "LexRoom", "D3 CL" | Ableton stock: Compressor, Reverb, EQ Eight |

---

## Part 4: Training Methodology

### 4.1 GRPO (Group Relative Policy Optimization)

From DeepSeek - eliminates separate critic network via group-relative advantages.

**Best For**: Objective technical metrics
- LUFS levels
- Spectral balance
- Stereo width
- Dynamic range
- Frequency masking scores

**Recent Results**: 18.4% relative WER improvement with rule-based rewards in speech recognition.

### 4.2 DPO (Direct Preference Optimization)

"Your language model is secretly a reward model" insight.

**Best For**: Subjective quality dimensions
- Clarity
- Excitement
- Production value
- Genre appropriateness

**Audio Applications**: Tango 2 (text-to-audio), DiffRhythm 2 (song generation)

### 4.3 Recommended Pipeline

```
Phase 1: GRPO + rule-based rewards for objective metrics
    ↓
Phase 2: DPO for subjective quality from human preferences
    ↓
Phase 3: Multi-preference alignment (DiffRhythm 2 cross-pair strategy)
    ↓
Phase 4: Distributional rewards matching professional mix distributions
```

---

## Part 5: Implementation Roadmap

### Phase 1: Control Harness Integration (Week 1-2)

**Objectives**:
- Extend AbletonMCP_Extended with training-specific functionality
- Parameter enumeration, systematic sweeps, state serialization
- Custom Max for Live device for internal audio capture
- Integrate AbletonOSC for comprehensive parameter access

**Deliverables**:
- [ ] Forked MCP with parameter sweep capability
- [ ] Max for Live audio capture device
- [ ] Complete Ableton stock plugin parameter database (JSON)

### Phase 1.5: Plugin Parameter Observatory (Week 2-3) ⭐ NEW

**Core Challenge**: MixologyDB uses Logic/Pro Tools/Reaper plugins. We need 1:1 parameter semantic mapping to Ableton, not rough approximations.

**Architecture**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLUGIN PARAMETER OBSERVATORY                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  AU/VST3 Scanner │  │ Ableton Exporter │  │ MixologyDB Parser│  │
│  │  (pyobjc/JUCE)   │  │  (Max for Live)  │  │   (HuggingFace)  │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │             │
│           ▼                     ▼                     ▼             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              PARAMETER METADATA DATABASE (SQLite)             │  │
│  │  - plugin_id, param_id, name, unit, min, max, scale_type     │  │
│  │  - category (frequency, gain, time, ratio, resonance, etc.)  │  │
│  │  - semantic embedding (MiniLM-L6-v2)                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              SEMANTIC PARAMETER MATCHER                       │  │
│  │  - Category matching (frequency↔frequency, gain↔gain)        │  │
│  │  - Unit compatibility (Hz, dB, ms, %)                        │  │
│  │  - Embedding similarity (cosine distance)                    │  │
│  │  - Confidence scoring                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              VALUE TRANSFORMATION ENGINE                      │  │
│  │  - Linear ↔ Logarithmic scale conversion                     │  │
│  │  - Range normalization (Hz→0-1, Q→0-1)                       │  │
│  │  - Discrete mapping (filter types)                           │  │
│  │  - Custom calibration functions                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              AUDIO-BASED CALIBRATION                          │  │
│  │  - Test signal generation (sweep, noise, impulse)            │  │
│  │  - Frequency response measurement via deconvolution          │  │
│  │  - Perceptually-weighted error calculation                   │  │
│  │  - Transformer optimization (scipy minimize)                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 5.1 Audio Unit Parameter Extraction

Apple's AU framework exposes full parameter metadata:

```python
# Key AU Parameter Units (critical for mapping)
AU_PARAMETER_UNITS = {
    0: 'Generic',           # Normalized 0-1
    1: 'Indexed',           # Discrete integer
    2: 'Boolean',           # 0 or 1
    3: 'Percent',           # 0-100
    4: 'Seconds',           # Time in seconds
    8: 'Hertz',             # Frequency in Hz
    13: 'Decibels',         # dB
    14: 'LinearGain',       # Linear amplitude
    18: 'Pan',              # -1 to 1
    24: 'Milliseconds',     # Time in ms
    25: 'Ratio',            # Compression ratio, etc.
}
```

#### 5.2 Ableton Parameter Database Export

Max for Live device to export complete parameter database:

```javascript
// enumerate_ableton_params.js (Max for Live)
function bang() {
    var api = new LiveAPI("live_set");
    var result = { devices: {} };
    
    // Iterate all tracks and devices
    var track_count = api.get("tracks").length / 2;
    for (var t = 0; t < track_count; t++) {
        var track_api = new LiveAPI("live_set tracks " + t);
        var device_count = track_api.get("devices").length / 2;
        
        for (var d = 0; d < device_count; d++) {
            var device_api = new LiveAPI("live_set tracks " + t + " devices " + d);
            var device_class = device_api.get("class_name").toString();
            
            if (!result.devices[device_class]) {
                result.devices[device_class] = {
                    parameters: []
                };
                
                var param_count = device_api.get("parameters").length / 2;
                for (var p = 0; p < param_count; p++) {
                    var param_api = new LiveAPI("live_set tracks " + t + 
                                                " devices " + d + " parameters " + p);
                    
                    result.devices[device_class].parameters.push({
                        index: p,
                        name: param_api.get("name").toString(),
                        min: param_api.get("min"),
                        max: param_api.get("max"),
                        default_value: param_api.get("default_value"),
                        is_quantized: param_api.get("is_quantized"),
                        value_items: param_api.get("value_items")
                    });
                }
            }
        }
    }
    outlet(0, JSON.stringify(result, null, 2));
}
```

#### 5.3 Semantic Parameter Matching

```python
from sentence_transformers import SentenceTransformer
from enum import Enum

class ParameterCategory(Enum):
    FREQUENCY = "frequency"
    GAIN = "gain"
    TIME = "time"
    RATIO = "ratio"
    RESONANCE = "resonance"
    PAN = "pan"
    MIX = "mix"
    THRESHOLD = "threshold"
    ATTACK = "attack"
    RELEASE = "release"
    FILTER_TYPE = "filter_type"
    BOOLEAN = "boolean"

class ParameterMatcher:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.category_keywords = {
            ParameterCategory.FREQUENCY: ['freq', 'frequency', 'hz', 'cutoff', 'pitch'],
            ParameterCategory.GAIN: ['gain', 'level', 'volume', 'db', 'amplitude'],
            ParameterCategory.TIME: ['time', 'ms', 'sec', 'delay', 'decay'],
            ParameterCategory.RESONANCE: ['resonance', 'q', 'bandwidth', 'width'],
            ParameterCategory.ATTACK: ['attack', 'att'],
            ParameterCategory.RELEASE: ['release', 'rel'],
            ParameterCategory.THRESHOLD: ['threshold', 'thresh'],
        }
    
    def match_parameters(self, source_params, target_params):
        """Match parameters using category + unit + embedding similarity."""
        matches = []
        for source in source_params:
            best_match, best_score = None, 0.0
            for target in target_params:
                score = self._compute_match_score(source, target)
                if score > best_score:
                    best_score, best_match = score, target
            if best_match and best_score > 0.5:
                matches.append((source, best_match, best_score))
        return matches
```

#### 5.4 Value Transformation Functions

```python
import math

class FrequencyTransformer:
    """Hz ↔ Ableton normalized (0-1 log scale)"""
    
    @staticmethod
    def hz_to_ableton_normalized(hz, min_hz=10, max_hz=22000):
        if hz <= min_hz: return 0.0
        if hz >= max_hz: return 1.0
        return (math.log(hz) - math.log(min_hz)) / (math.log(max_hz) - math.log(min_hz))
    
    @staticmethod
    def ableton_normalized_to_hz(normalized, min_hz=10, max_hz=22000):
        return math.exp(normalized * (math.log(max_hz) - math.log(min_hz)) + math.log(min_hz))

class QTransformer:
    """Q factor ↔ Ableton normalized resonance"""
    
    @staticmethod
    def q_to_ableton_normalized(q, min_q=0.1, max_q=18):
        if q <= min_q: return 0.0
        if q >= max_q: return 1.0
        return (math.log(q) - math.log(min_q)) / (math.log(max_q) - math.log(min_q))

class FilterTypeMapper:
    """MixologyDB filter types → Ableton EQ Eight indices"""
    
    MAPPING = {
        'HP': 1,      # High-pass 48dB
        'LP': 7,      # Low-pass 48dB
        'NOTCH': 3,   # Bell/Peak
        'PEAK': 3,    # Bell/Peak
        'SHELF_LOW': 2,   # Low Shelf
        'SHELF_HIGH': 5,  # High Shelf
    }
```

#### 5.5 Audio-Based Calibration & Validation

**Critical for achieving near-perfect mappings** - verify transformations by comparing audio output:

```python
import numpy as np
from scipy import signal

class PluginCalibrator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.test_signals = {
            'sine_sweep': self._generate_log_sweep(20, 20000, 2.0),
            'white_noise': np.random.randn(sample_rate * 2) * 0.5,
            'impulse': self._generate_impulse(sample_rate * 2),
        }
    
    def measure_frequency_response(self, processed, original):
        """Measure transfer function via deconvolution."""
        n_fft = 8192
        H_processed = np.fft.rfft(processed, n=n_fft)
        H_original = np.fft.rfft(original, n=n_fft)
        H = H_processed / (H_original + 1e-10)
        magnitude_db = 20 * np.log10(np.abs(H) + 1e-10)
        frequencies = np.fft.rfftfreq(n_fft, 1 / self.sample_rate)
        return frequencies, magnitude_db
    
    def compare_eq_settings(self, source_processed, target_processed, original):
        """Compare two EQs with supposedly equivalent settings."""
        freq, source_response = self.measure_frequency_response(source_processed, original)
        _, target_response = self.measure_frequency_response(target_processed, original)
        
        audible_mask = (freq >= 20) & (freq <= 20000)
        difference = source_response[audible_mask] - target_response[audible_mask]
        
        return {
            'mean_absolute_error_db': np.mean(np.abs(difference)),
            'max_error_db': np.max(np.abs(difference)),
            'rms_error_db': np.sqrt(np.mean(difference ** 2)),
            'correlation': np.corrcoef(source_response[audible_mask], 
                                       target_response[audible_mask])[0, 1],
        }
```

#### 5.6 Complete MixologyDB → Ableton Transformer

```python
class MixologyToAbletonTransformer:
    """Transform MixologyDB tracks to Ableton MCP commands."""
    
    def transform_track(self, mixology_track):
        commands = []
        params = mixology_track.get('parameters', {})
        
        # EQ
        if 'eq' in params:
            commands.extend(self._transform_eq(params['eq']))
        
        # Compression
        if 'compression' in params:
            commands.extend(self._transform_compression(params['compression']))
        
        # Reverb
        if 'reverb' in params:
            commands.extend(self._transform_reverb(params['reverb']))
        
        # Volume & Pan
        if 'gain' in params:
            commands.append({
                'type': 'set_track_volume',
                'params': {'value': self._transform_gain(params['gain'])}
            })
        
        return commands
    
    def _transform_eq(self, eq_bands):
        """Transform EQ bands to EQ Eight commands."""
        commands = []
        for i, band in enumerate(eq_bands[:8]):  # EQ Eight has 8 bands
            band_num = i + 1
            
            # Enable band
            commands.append({
                'type': 'set_device_parameter',
                'params': {
                    'device_name': 'EQ Eight',
                    'parameter_name': f'{band_num} Filter On A',
                    'value': 1.0
                }
            })
            
            # Filter type
            if 'type' in band:
                filter_type = FilterTypeMapper.MAPPING.get(band['type'], 3)
                commands.append({
                    'type': 'set_device_parameter',
                    'params': {
                        'device_name': 'EQ Eight',
                        'parameter_name': f'{band_num} Filter Type A',
                        'value': float(filter_type) / 7.0
                    }
                })
            
            # Frequency
            if 'value' in band and 'freq' in band['value']:
                freq_norm = FrequencyTransformer.hz_to_ableton_normalized(band['value']['freq'])
                commands.append({
                    'type': 'set_device_parameter',
                    'params': {
                        'device_name': 'EQ Eight',
                        'parameter_name': f'{band_num} Frequency A',
                        'value': freq_norm
                    }
                })
            
            # Q/Resonance
            if 'value' in band and 'q' in band['value']:
                q_norm = QTransformer.q_to_ableton_normalized(band['value']['q'])
                commands.append({
                    'type': 'set_device_parameter',
                    'params': {
                        'device_name': 'EQ Eight',
                        'parameter_name': f'{band_num} Resonance A',
                        'value': q_norm
                    }
                })
            
            # Gain
            if 'value' in band and band['value'].get('gain') is not None:
                gain_norm = (band['value']['gain'] + 15) / 30.0  # -15 to +15 dB
                commands.append({
                    'type': 'set_device_parameter',
                    'params': {
                        'device_name': 'EQ Eight',
                        'parameter_name': f'{band_num} Gain A',
                        'value': max(0.0, min(1.0, gain_norm))
                    }
                })
        
        return commands
```

#### 5.7 Phase 1.5 Deliverables

- [ ] Plugin scanner for all installed AU/VST3 plugins (pyobjc)
- [ ] Max for Live parameter exporter for Ableton stock plugins
- [ ] SQLite database schema for parameter metadata
- [ ] Semantic parameter matcher with confidence scoring
- [ ] Value transformation functions (frequency, Q, gain, filter type)
- [ ] Audio calibration pipeline with test signals
- [ ] MixologyDB → Ableton transformer with validation
- [ ] Training dataset export (JSON with confidence scores)

**Key Insight**: We'll never get 1:1 *sonic* equivalence (a Waves SSL ≠ Ableton Glue Compressor), but we CAN achieve 1:1 **parameter semantic mapping** that preserves mixing *intent*, which is what matters for training.

---

### Phase 2: Spatial Audio Capture Pipeline (Week 3-4)

**Objectives**:
- macOS app hosting VSX via AVAudioEngine with output taps
- Batch rendering system processing audio through VSX configurations
- Extract binaural features (IPD, ILD, spectral characteristics)

**Deliverables**:
- [ ] VSX hosting application
- [ ] Batch processing script for multiple room/speaker configs
- [ ] Feature extraction pipeline (IPD, ILD, pinna cues)

### Phase 3: Training Data Generation (Week 4-5)

**Objectives**:
- Parameter sweep automation (EQ, compression, reverb, stereo)
- Before/after audio pair capture with full parameter state
- Instruction dataset generation

**Instruction Format**:
```json
{
  "task": "Reduce muddiness in bass guitar",
  "context": {
    "track_type": "Bass Guitar",
    "current_issues": ["frequency_masking_with_kick", "undefined_low_end"]
  },
  "reasoning": "The bass is competing with the kick drum around 80-100Hz. A high-pass filter at 40Hz will clean up sub frequencies while a cut around 200Hz will reduce boominess.",
  "actions": [
    {
      "type": "set_device_parameter",
      "device": "EQ Eight",
      "parameter": "1 Filter Type A",
      "value": 0.14,
      "human_readable": "High-pass 48dB"
    },
    {
      "type": "set_device_parameter", 
      "device": "EQ Eight",
      "parameter": "1 Frequency A",
      "value": 0.23,
      "human_readable": "40 Hz"
    }
  ],
  "audio_analysis": {
    "before": {"low_end_rms": -18.2, "masking_score": 0.73},
    "after": {"low_end_rms": -22.1, "masking_score": 0.41}
  }
}
```

### Phase 4: Model Adaptation (Week 5-6)

**Objectives**:
- Fine-tune Qwen3-4B on instruction dataset
- Integrate audio understanding (MEGAMI-style or adapted Spatial-AST)
- Apply GRPO for objective metrics, DPO for preference alignment

**Model Architecture**:
```
Audio Input → Audio Encoder (Spatial-AST/MEGAMI-style) → Projection Layer
                                                              ↓
                                                        Qwen3-4B LLM
                                                              ↓
                                                     Tool Calls (MCP)
```

---

## Part 6: Key Resources

### Datasets
- **MixAssist**: https://huggingface.co/datasets/mclemcrew/MixAssist
- **MixologyDB**: https://huggingface.co/datasets/mclemcrew/MixologyDB
- **Project Website**: https://mclemcrew.github.io/mixassist-website/

### Code & Tools
- **AbletonMCP_Extended**: Local Remote Script (see `harness/AbletonMCP_Extended/`)
- **AbletonOSC**: https://github.com/ideoforms/AbletonOSC
- **PyLive**: https://github.com/ideoforms/pylive
- **MixologyDB Annotation Tool**: https://github.com/mclemcrew/MixologyDB

### Research Papers
- **BAT (Binaural Audio Transformer)**: https://zhishengzheng.com/bat/
- **MEGAMI**: arXiv Nov 2024 (Sony)
- **MixAssist Paper**: arXiv:2507.06329
- **GRPO**: DeepSeek technical report
- **DPO**: "Direct Preference Optimization" (Rafailov et al.)

### Documentation
- **Live Object Model**: https://docs.cycling74.com/apiref/lom/
- **Ableton Remote Scripts**: Python scripts in Ableton installation

---

## Appendix A: Ableton EQ Eight Parameter Reference

```python
ABLETON_EQ_EIGHT = {
    'device_class': 'Eq8',
    'bands': 8,
    'parameters_per_band': [
        '{n} Filter On A',      # Boolean (0 or 1)
        '{n} Filter Type A',    # Indexed (0-7)
        '{n} Frequency A',      # Float (0-1, log scale 10Hz-22kHz)
        '{n} Gain A',           # Float (0-1, maps to -15 to +15 dB)
        '{n} Resonance A',      # Float (0-1, maps to Q 0.1-18)
    ],
    'filter_types': {
        0: 'Low-cut 12dB',
        1: 'Low-cut 48dB',
        2: 'Low Shelf',
        3: 'Bell (Peak)',
        4: 'Notch',
        5: 'High Shelf',
        6: 'High-cut 12dB',
        7: 'High-cut 48dB',
    },
    'global_parameters': [
        'Scale',        # 0-200%
        'Output Gain',  # -15 to +15 dB
    ]
}
```

## Appendix B: Plugin Mapping Reference

```python
MIXOLOGYDB_TO_ABLETON_PLUGINS = {
    # Compressors
    'BF-76': 'Compressor',      # 1176-style (different attack/release curves)
    'D3 CL': 'Glue Compressor', # SSL-style bus compressor
    
    # Reverbs  
    'LexRoom': ('Reverb', 'Room'),
    'LexHall': ('Reverb', 'Hall'),
    'LexPlate': ('Reverb', 'Plate'),
    
    # EQ
    'Generic EQ': 'EQ Eight',
}

# Note: Behavioral differences mean these are SEMANTIC mappings,
# not sonic equivalents. The model learns mixing INTENT.
```
