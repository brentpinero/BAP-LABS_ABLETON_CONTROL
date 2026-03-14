# Spatial Audio Data Collection - Approach 1: VSX + Binaural Feature Extraction

**Created**: December 13, 2024
**Goal**: Collect and structure spatial audio data for training a Reasoning + Analysis + Action model
**Target**: Both stereo mixes and multitrack stems

---

## Executive Summary

This approach uses **Slate Digital VSX** to render binaural reference audio, then extracts **IPD/ILD spatial features** to create training data that teaches an LLM to:
1. **Analyze** spatial characteristics of audio
2. **Reason** about what's good/bad and why
3. **Generate** MCP commands to improve the mix

---

## Audio Engineering Foundations

### The Three Dimensions of Mixing

| Dimension | Perception | Controlled By | Measurable Features |
|-----------|------------|---------------|---------------------|
| **Width** | Left - Right | Panning, stereo effects | ILD, stereo correlation, pan position |
| **Depth** | Front - Back | Reverb, volume, HF rolloff | Wet/dry ratio, spectral decay, level |
| **Height** | Low - High frequencies | EQ, frequency balance | Spectral centroid, band energy ratios |

### Binaural Spatial Cues (What VSX Creates)

| Cue | Frequency Range | Function | Max Value |
|-----|-----------------|----------|-----------|
| **ITD** (Interaural Time Difference) | <1.2 kHz | Horizontal position | ~700 microseconds |
| **ILD** (Interaural Level Difference) | >1.5 kHz | Horizontal position (head shadow) | ~20 dB |
| **HRTF/Pinna** | 2-5 kHz peaks | Elevation, front/back | +17 dB at 2.7 kHz |
| **Room Reflections** | Broadband | Distance, environment | Varies by room |

### The Duplex Theory (Lord Rayleigh, 1907)
- **Low frequencies (<1.5 kHz)**: Localized via ITD (time difference)
- **High frequencies (>1.5 kHz)**: Localized via ILD (level difference)
- **Overlap region**: Both cues contribute

---

## VSX Signal Chain

```
Stereo Input
    → Speaker Frequency Response Modeling
    → BRIR Convolution (room reflections)
    → HRTF Application (interaural cues)
    → Headphone Compensation
    → Binaural Output
```

### VSX Technical Details
- **E.C.C.O. system**: Calibrates 2-4kHz ear canal resonance
- **Two HRTF profiles**: A (universal) and B (more 2.5kHz presence)
- **7000+ binaural capture formulas** in development
- **No public API**: Must host as AU/VST3 plugin and tap output

---

## Data Schema

```python
spatial_mix_sample = {
    # === IDENTIFIERS ===
    "id": "mix_001_spatial",
    "metadata": {
        "source": "MixologyDB",  # or "Mixing Secrets", "custom"
        "genre": "rock",
        "bpm": 120,
        "track_count": 8
    },

    # === AUDIO INPUTS (Both scenarios) ===
    "audio": {
        "stereo_mix": "path/to/mix.wav",           # Full mix analysis
        "stems": {                                   # Per-track analysis
            "kick": "path/to/kick.wav",
            "bass": "path/to/bass.wav",
            "guitar_L": "path/to/guitar_L.wav",
            # ...
        }
    },

    # === VSX BINAURAL RENDERS (Spatial Reference) ===
    "vsx_renders": {
        "studio_monitors": {
            "room_model": "SSL_Room",
            "speaker_config": "monitors_nearfield",
            "hrtf_profile": "A",
            "binaural_output": "path/to/binaural_ssl.wav"
        },
        "mastering_suite": {
            "room_model": "Mastering_A",
            "binaural_output": "path/to/binaural_master.wav"
        }
        # Multiple rooms = training data diversity
    },

    # === EXTRACTED SPATIAL FEATURES (Binaural Analysis) ===
    "spatial_features": {
        # Global mix characteristics
        "global": {
            "stereo_width": 0.73,              # 0-1
            "stereo_correlation": 0.45,        # -1 to 1
            "mono_compatibility": 0.89,        # 0-1
            "center_energy_ratio": 0.62,       # % energy in center
            "left_right_balance": 0.02         # -1 to 1
        },

        # Per-frequency-band binaural cues
        "per_band": {
            "low_20_200Hz": {
                "ipd_mean": 0.02,              # rad, should be ~0 for center
                "ipd_coherence": 0.95,         # High = mono-like
                "ild_mean": 0.5,               # dB difference L-R
                "ild_variance": 0.1
            },
            "low_mid_200_500Hz": {"ipd_mean": 0.05, "ipd_coherence": 0.88, "ild_mean": 1.2, "ild_variance": 0.3},
            "mid_500_2kHz": {"ipd_mean": 0.12, "ipd_coherence": 0.72, "ild_mean": 3.4, "ild_variance": 0.8},
            "high_mid_2k_6kHz": {"ipd_mean": 0.08, "ipd_coherence": 0.65, "ild_mean": 5.2, "ild_variance": 1.2},
            "high_6k_20kHz": {"ipd_mean": 0.04, "ipd_coherence": 0.58, "ild_mean": 6.1, "ild_variance": 1.5}
        },

        # Per-track spatial estimates (when stems available)
        "per_track": [
            {
                "name": "kick",
                "pan_estimate": 0.0,           # -1 to 1
                "depth_estimate": 0.2,         # 0=front, 1=back
                "frequency_centroid": 80,      # Hz
                "dynamic_range": 12            # dB
            },
            {
                "name": "guitar_L",
                "pan_estimate": -0.65,
                "depth_estimate": 0.5,
                "frequency_centroid": 1200,
                "dynamic_range": 8
            }
        ]
    },

    # === MEGAMI-STYLE EFFECT EMBEDDINGS (Optional) ===
    "effect_embeddings": {
        # Per-track 2048-dim FxEncoder++ embeddings + 64-dim dynamics
        "kick": {
            "fx_embedding": "[2048-dim vector]",
            "dynamics": {
                "log_rms": -18.2,
                "crest_factor": 12.5,
                "dynamic_spread": 8.3,
                "stereo_width": 0.0,
                "stereo_imbalance": 0.0
            }
        }
    },

    # === MIX STATE (Ground Truth from Ableton via MCP) ===
    "mix_state": {
        "tracks": [
            {
                "name": "Kick",
                "pan": 0.0,                    # Ableton normalized
                "volume": 0.7,                 # Ableton normalized
                "mute": False,
                "solo": False,
                "devices": [
                    {
                        "name": "EQ Eight",
                        "parameters": {
                            "1 Filter On A": 1.0,
                            "1 Filter Type A": 0.14,  # High-pass
                            "1 Frequency A": 0.23,    # ~40Hz
                            "1 Gain A": 0.5,
                            "1 Resonance A": 0.3
                        }
                    }
                ],
                "sends": [
                    {"name": "Reverb", "level": -float('inf')}
                ]
            }
        ],
        "master": {
            "volume": 0.85,
            "devices": []
        }
    },

    # === REASONING CHAIN (For LLM Training) ===
    "analysis": {
        "spatial_assessment": "The stereo image shows moderate width (0.73) with good mono compatibility (0.89). The low-frequency IPD coherence is high (0.95), indicating properly centered bass elements. However, mid-frequency ILD variance (3.4 dB) suggests aggressive panning that may fatigue listeners.",

        "issues_identified": [
            {
                "type": "frequency_masking",
                "severity": "moderate",
                "description": "Bass guitar and kick drum compete in 80-120Hz range. IPD coherence drops in this region.",
                "tracks_affected": ["Kick", "Bass"],
                "spatial_impact": "Muddies the center image, reduces punch"
            },
            {
                "type": "excessive_width",
                "severity": "low",
                "description": "High-frequency stereo width exceeds 0.85, may cause phase issues on some playback systems"
            }
        ],

        "quality_scores": {
            "overall": 0.72,
            "spatial_coherence": 0.78,
            "frequency_balance": 0.68,
            "mono_compatibility": 0.89
        }
    },

    # === RECOMMENDED ACTIONS (MCP Commands) ===
    "recommended_actions": [
        {
            "reasoning": "To reduce masking between kick and bass while maintaining spatial coherence, apply complementary EQ cuts. The bass should make room for kick in the 60-80Hz attack range.",
            "actions": [
                {
                    "type": "set_device_parameter",
                    "track": "Bass",
                    "device": "EQ Eight",
                    "parameter": "2 Frequency A",
                    "value": 0.31,
                    "human_readable": "Cut at 80Hz"
                },
                {
                    "type": "set_device_parameter",
                    "track": "Bass",
                    "device": "EQ Eight",
                    "parameter": "2 Gain A",
                    "value": 0.35,
                    "human_readable": "-4.5dB cut"
                }
            ],
            "expected_improvement": {
                "frequency_masking_score": -0.15,
                "spatial_coherence": 0.05
            }
        }
    ]
}
```

---

## Feature Extraction Pipeline

```
                    ┌─────────────────────────────────────────────────────────┐
                    │              SPATIAL AUDIO DATA PIPELINE                 │
                    └─────────────────────────────────────────────────────────┘
                                            │
            ┌───────────────────────────────┼───────────────────────────────┐
            ▼                               ▼                               ▼
    ┌──────────────┐              ┌──────────────────┐             ┌──────────────┐
    │   RAW AUDIO  │              │   VSX RENDERING  │             │ ABLETON STATE│
    │  (Stems/Mix) │              │  (AVAudioEngine) │             │   (via MCP)  │
    └──────┬───────┘              └────────┬─────────┘             └──────┬───────┘
           │                               │                              │
           ▼                               ▼                              ▼
    ┌──────────────┐              ┌──────────────────┐             ┌──────────────┐
    │   Librosa    │              │    Binaspect     │             │  JSON Export │
    │  Spectral    │              │   IPD/ILD/ITD    │             │  Full Params │
    │  Features    │              │   Extraction     │             │              │
    └──────┬───────┘              └────────┬─────────┘             └──────┬───────┘
           │                               │                              │
           └───────────────────────────────┼──────────────────────────────┘
                                           ▼
                              ┌─────────────────────────┐
                              │   UNIFIED SAMPLE JSON   │
                              │  (spatial_mix_sample)   │
                              └────────────┬────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
           ┌──────────────┐      ┌──────────────────┐    ┌──────────────┐
           │ ANALYSIS LLM │      │ REASONING CHAIN  │    │ ACTION GEN   │
           │  (Spatial    │      │ (What's wrong &  │    │ (MCP cmds to │
           │  assessment) │      │  why?)           │    │  fix it)     │
           └──────────────┘      └──────────────────┘    └──────────────┘
```

---

## Implementation Components

### 1. VSX Rendering (macOS AVAudioEngine)

```swift
// Host VSX as Audio Unit with tap on output node
let engine = AVAudioEngine()
let vsxDescription = AudioComponentDescription(
    componentType: kAudioUnitType_Effect,
    componentSubType: /* VSX subtype */,
    componentManufacturer: /* Slate Digital */,
    componentFlags: 0,
    componentFlagsMask: 0
)

let vstNode = AVAudioUnitEffect(audioComponentDescription: vsxDescription)
engine.attach(vstNode)
engine.connect(engine.mainMixerNode, to: vstNode, format: format)

// Install tap on output for capture
vstNode.installTap(onBus: 0, bufferSize: 4096, format: format) { buffer, time in
    // Capture binaural output to file
    self.writeBuffer(buffer, to: outputFile)
}
```

### 2. IPD/ILD Extraction (Python)

```python
# Using Binaspect library
from binaspect import BinauralAnalyzer

analyzer = BinauralAnalyzer(sample_rate=44100)
ipd, ild = analyzer.extract_interaural_features(
    binaural_audio,
    n_fft=2048,
    hop_length=512,
    frequency_bands=[
        (20, 200),      # Low
        (200, 500),     # Low-mid
        (500, 2000),    # Mid
        (2000, 6000),   # High-mid
        (6000, 20000)   # High
    ]
)

# Alternative: isrish/BinuralAudio
from binaural_audio import extract_ipd_ild
ipd_features, ild_features = extract_ipd_ild(left_channel, right_channel)
```

### 3. Global Stereo Features

```python
import numpy as np

def extract_stereo_features(left, right):
    """Extract global stereo characteristics."""

    # Stereo correlation (-1 to 1)
    correlation = np.corrcoef(left, right)[0, 1]

    # Stereo width (0 to 1)
    mid = (left + right) / 2
    side = (left - right) / 2
    mid_energy = np.sum(mid ** 2)
    side_energy = np.sum(side ** 2)
    width = side_energy / (mid_energy + side_energy + 1e-10)

    # Mono compatibility (0 to 1)
    mono = left + right
    mono_energy = np.sum(mono ** 2)
    stereo_energy = np.sum(left ** 2) + np.sum(right ** 2)
    mono_compat = mono_energy / (stereo_energy + 1e-10)

    # Left-right balance (-1 to 1)
    left_energy = np.sum(left ** 2)
    right_energy = np.sum(right ** 2)
    balance = (right_energy - left_energy) / (right_energy + left_energy + 1e-10)

    return {
        "stereo_correlation": correlation,
        "stereo_width": width,
        "mono_compatibility": min(mono_compat, 1.0),
        "left_right_balance": balance
    }
```

### 4. MEGAMI-Style Dynamics Features

```python
def extract_dynamics_features(audio, sample_rate=44100, frame_size=2048):
    """Extract MEGAMI-style per-track dynamics features."""

    # Frame the audio
    frames = librosa.util.frame(audio, frame_length=frame_size, hop_length=frame_size//2)

    # Log-RMS per frame
    rms = np.sqrt(np.mean(frames ** 2, axis=0))
    log_rms = 20 * np.log10(rms + 1e-10)

    # Crest factor (peak / RMS)
    peaks = np.max(np.abs(frames), axis=0)
    crest_factor = 20 * np.log10(peaks / (rms + 1e-10) + 1e-10)

    # Dynamic spread (RMS variance)
    dynamic_spread = np.std(log_rms)

    return {
        "log_rms": np.mean(log_rms),
        "crest_factor": np.mean(crest_factor),
        "dynamic_spread": dynamic_spread
    }
```

---

## Tools & Libraries

| Component | Tool/Library | Purpose | Link |
|-----------|--------------|---------|------|
| **IPD/ILD Extraction** | Binaspect | Binaural feature analysis | [ResearchGate](https://www.researchgate.net/publication/397040634) |
| **IPD/ILD Extraction** | BinuralAudio | Simple IPD/ILD extraction | [GitHub](https://github.com/isrish/BinuralAudio) |
| **VSX Rendering** | AVAudioEngine | macOS AU hosting | Apple Framework |
| **Effect Embeddings** | FxNorm-automix | MEGAMI-style embeddings | [GitHub](https://github.com/sony/FxNorm-automix) |
| **Spectral Features** | Librosa | MFCC, spectral analysis | [librosa.org](https://librosa.org) |
| **Ableton State** | Ableton MCP | Parameter export | [GitHub](https://github.com/ahujasid/ableton-mcp) |
| **Reasoning Gen** | GPT-4/Claude | Analysis chain generation | OpenAI/Anthropic |

---

## Training Data Generation Strategy

### Phase 1: Audio Collection
1. Source multitracks from MixologyDB, Mixing Secrets, Weathervane
2. Process through VSX with 3-5 different room models
3. Export Ableton session state for each mix via MCP

### Phase 2: Feature Extraction
1. Run Binaspect on all VSX renders (IPD/ILD per band)
2. Extract global stereo features from original mix
3. Extract per-track dynamics if stems available
4. (Optional) Generate FxEncoder++ embeddings

### Phase 3: Reasoning Chain Generation
1. Use GPT-4/Claude to generate spatial assessments
2. Identify issues based on feature thresholds
3. Generate corrective MCP actions
4. Validate actions produce expected feature improvements

### Phase 4: Dataset Assembly
1. Combine all components into unified JSON samples
2. Split into train/validation/test
3. Balance by genre, issue type, severity

---

## Key Insights

### From MEGAMI (Sony, Nov 2024)
- Operating in **effect embedding space** captures mixing intent better than raw audio
- Per-track features: log-RMS, crest factor, dynamic spread, stereo width, stereo imbalance
- **Permutation-equivariant transformer** handles arbitrary track counts
- **Domain adaptation** enables training on wet-only data

### From BAT (Binaural Audio Transformer)
- **Spatial-AST encoder** processes binaural audio for spatial reasoning
- Extracts Direction of Arrival (DoA) and Distance Prediction (DP)
- Enables complex spatial queries via LLM integration

### For Mix Understanding
- Spatial features (IPD/ILD) capture **how it sounds in the room**
- Effect embeddings capture **what processing was applied**
- Both are complementary for complete mix understanding

---

## Pros & Cons of This Approach

### Pros
- **Physically grounded**: IPD/ILD are real perceptual cues
- **Room-agnostic understanding**: VSX normalizes playback environment
- **Rich feature set**: Combines spatial, spectral, and dynamics
- **Actionable**: Direct mapping to MCP commands

### Cons
- **VSX dependency**: Requires Slate Digital license and hardware
- **Batch processing overhead**: Each mix needs multiple VSX renders
- **Feature engineering**: Manual selection of frequency bands, thresholds
- **No end-to-end learning**: Features are hand-crafted, not learned

---

## Open Questions

1. **Optimal frequency bands** for IPD/ILD extraction?
2. **How many VSX room models** needed for diversity?
3. **Threshold values** for issue detection (masking, phase, width)?
4. **Integration with CLAP embeddings** for semantic audio understanding?

---

## References

- [MEGAMI: Automatic Music Mixing (arXiv 2511.08040)](https://arxiv.org/abs/2511.08040)
- [BAT: Binaural Audio Transformer](https://zhishengzheng.com/bat/)
- [Binaspect Library](https://www.researchgate.net/publication/397040634)
- [VSX HRTF Explained](https://stevenslateaudio.zendesk.com/hc/en-us/articles/19264898533527-VSX-HRTF-Explained)
- [Sound Localization - Wikipedia](https://en.wikipedia.org/wiki/Sound_localization)
- [Interaural Time Difference (ScienceDirect)](https://www.sciencedirect.com/topics/neuroscience/interaural-time-difference)
- [3D Mixing Techniques - Audio University](https://audiouniversityonline.com/3d-mixing-techniques/)
