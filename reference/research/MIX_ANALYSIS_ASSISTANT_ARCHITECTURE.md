# Real-Time Mix Analysis Assistant - Native Ableton Architecture

**Created**: December 13, 2024
**Updated**: December 13, 2024
**Goal**: Build an LLM-powered mix assistant that analyzes audio in real-time and takes action via MCP
**Design Principle**: Zero-friction - works out of the box for any Ableton Live 12 Suite user

---

## Executive Summary

This document defines the complete architecture for a **real-time mix analysis assistant** that:

1. **Analyzes** audio via custom Max for Live device (spectrum, stereo, dynamics)
2. **Understands context** via 32-bar sliding window with intelligent pre-scanning
3. **Tracks user focus** via track selection and behavior patterns
4. **Reasons** about mix issues using a local LLM (Qwen3-4B on MLX)
5. **Acts** on the mix via MCP tool calls to Ableton

Unlike Approach 1 (VSX-dependent binaural analysis), this works for **any producer with Ableton Live Suite** - no additional hardware or software required.

### Key Insights

1. Ableton's native **Spectrum device doesn't expose data via the Live API** - we must build custom FFT analysis in Max
2. **Track selection is the #1 context signal** - it reflects immediate user intent
3. **32 bars of context** (~3,200 tokens) is sufficient for phrase-level reasoning
4. **Pre-scanning future bars** eliminates latency when user jumps around

---

## Ableton Live 12 Suite - Complete Audio Effects Index

### Analysis & Metering Devices

| Device | Purpose | Data Accessible via LOM? |
|--------|---------|--------------------------|
| **Spectrum** | FFT frequency analyzer | NO - visual only |
| **Tuner** | Pitch detection | NO - visual only |
| **EQ Eight** | 8-band EQ with analyzer | Parameters YES, analyzer NO |

### Utility & Routing Devices

| Device | Purpose | Key Parameters |
|--------|---------|----------------|
| **Utility** | Gain, width, mono, phase | Width (0-200%), Phz-L, Phz-R, Mono, Gain |
| **External Audio Effect** | External routing | Send/Return levels |

### Dynamics Processors

| Device | Purpose | Key Parameters |
|--------|---------|----------------|
| **Compressor** | Dynamic range control | Threshold, Ratio, Attack, Release, Knee, GR Meter |
| **Glue Compressor** | SSL-style bus comp | Threshold, Ratio, Attack, Release, Range, Makeup |
| **Limiter** | Peak limiting | Ceiling, Gain, Release, Mid/Side mode (Live 12) |
| **Multiband Dynamics** | 3-band compression | Per-band Threshold, Ratio, Attack, Release |
| **Gate** | Noise gate | Threshold, Attack, Hold, Release, Floor |

### EQ & Filters

| Device | Purpose | Key Parameters |
|--------|---------|----------------|
| **EQ Eight** | 8-band parametric | Per-band: Freq, Gain, Q, Type, On/Off |
| **EQ Three** | DJ-style 3-band | Low, Mid, High gains + Kill switches |
| **Channel EQ** | Adaptive 3-band | Low, Mid, High + Spectrum display |
| **Auto Filter** | Resonant filter + LFO | Freq, Resonance, Env, LFO Rate |

### Saturation & Distortion

| Device | Purpose | Key Parameters |
|--------|---------|----------------|
| **Saturator** | Waveshaping + warmth | Drive, Type, Output, Base (Bass Shaper in Live 12) |
| **Overdrive** | Soft clipping | Drive, Tone, Dynamics |
| **Pedal** | Guitar pedal emulation | Gain, Type (OD/Distort/Fuzz), Output |
| **Dynamic Tube** | Tube saturation | Drive, Tone, Bias, Envelope |
| **Amp** | Guitar amp modeling | Gain, Bass, Mid, Treble, Presence |
| **Roar** | Multi-stage saturation (Live 12) | 3 stages, Mid/Side, Multiband |

### Time-Based Effects

| Device | Purpose | Key Parameters |
|--------|---------|----------------|
| **Delay** | Dual delay lines | Time L/R, Feedback, Filter, Dry/Wet |
| **Echo** | Modulated delay | Time, Feedback, Reverb, Modulation |
| **Reverb** | Algorithmic reverb | Size, Decay, Reflect, Diffuse, Dry/Wet |
| **Grain Delay** | Granular delay | Time, Spray, Frequency, Pitch |
| **Filter Delay** | 3-band filtered delay | Per-band: Time, Feedback, Filter |

### Modulation Effects

| Device | Purpose | Key Parameters |
|--------|---------|----------------|
| **Chorus-Ensemble** | Chorus/ensemble | Rate, Width, Delay, Feedback |
| **Flanger** | Flanging | Delay, Feedback, Frequency |
| **Phaser** | Phase shifting | Poles, Frequency, Feedback, Spin |
| **Auto Pan-Tremolo** | Stereo modulation | Rate, Shape, Phase, Amount |
| **Frequency Shifter** | Ring mod / pitch shift | Coarse, Fine, Drive, Dry/Wet |

### Special Effects

| Device | Purpose | Key Parameters |
|--------|---------|----------------|
| **Beat Repeat** | Stutter/glitch | Interval, Grid, Variation, Pitch |
| **Corpus** | Resonator | Type, Size, Decay, Material |
| **Resonators** | Tuned resonators | 5 resonator pitches + decay |
| **Vocoder** | Carrier/modulator | Bands, Bandwidth, Formant, Depth |
| **Redux** | Bit crush / downsample | Bit Depth, Sample Rate |
| **Erosion** | Digital degradation | Frequency, Amount, Mode |
| **Vinyl Distortion** | Lo-fi character | Tracing, Pinch, Drive, Crackle |

### Pitch & Vocal

| Device | Purpose | Key Parameters |
|--------|---------|----------------|
| **Auto Shift** | Pitch correction (Live 12) | Scale, Key, Amount, Vibrato |

---

## Max for Live Analysis Capabilities

### What CAN Be Accessed via Live API (LOM)

```
live_set
├── tracks[]
│   ├── mixer_device
│   │   ├── volume (DeviceParameter)
│   │   ├── panning (DeviceParameter)
│   │   └── sends[] (DeviceParameter)
│   ├── devices[]
│   │   ├── parameters[] (DeviceParameter)
│   │   │   ├── value
│   │   │   ├── min
│   │   │   ├── max
│   │   │   ├── name
│   │   │   └── is_quantized
│   │   └── name
│   ├── clip_slots[]
│   └── output_meter_level (float, READ-ONLY)
├── master_track
│   └── output_meter_level (float, READ-ONLY)
└── return_tracks[]
```

### What CANNOT Be Accessed

- Native Spectrum device frequency bin data
- EQ Eight analyzer visualization data
- Tuner pitch detection values
- Internal metering beyond output_meter_level

### Solution: Build Custom Analysis in Max

Since we can't read native analyzer data, we build our own using Max/MSP objects:

| Analysis Type | Max Objects | Output |
|---------------|-------------|--------|
| **Spectrum** | `fft~`, `pfft~`, `cartopol~` | Frequency bins + magnitudes |
| **RMS Level** | `average~`, `snapshot~` | dB value |
| **Peak Level** | `peakamp~`, `snapshot~` | dB value |
| **Stereo Correlation** | Custom (cross-correlation) | -1 to +1 |
| **Stereo Width** | Mid/Side calculation | 0 to 1 |
| **LUFS** | `mc.limi~` or external | dB LUFS |

---

## Proposed Architecture: Mix Analysis Hub M4L Device

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MIX ANALYSIS HUB (Max for Live)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   Audio Input   │    │   Audio Input   │    │   Audio Input   │        │
│  │   (Track 1)     │    │   (Track 2)     │    │   (Master)      │        │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘        │
│           │                      │                      │                  │
│           ▼                      ▼                      ▼                  │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                    ANALYSIS ENGINE (per channel)                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   SPECTRUM   │  │   DYNAMICS   │  │   STEREO     │              │   │
│  │  │   fft~ 2048  │  │   RMS/Peak   │  │   M/S Width  │              │   │
│  │  │   cartopol~  │  │   Crest      │  │   Correlation│              │   │
│  │  │   25 bands   │  │   Dynamic    │  │   Balance    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│           │                      │                      │                  │
│           ▼                      ▼                      ▼                  │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                        DATA AGGREGATOR                              │   │
│  │  Combines all analysis into structured JSON                         │   │
│  │  Updates at configurable rate (10-60 Hz)                           │   │
│  └─────────────────────────────────┬──────────────────────────────────┘   │
│                                    │                                       │
│           ┌────────────────────────┼────────────────────────┐             │
│           ▼                        ▼                        ▼             │
│  ┌──────────────┐         ┌──────────────┐        ┌──────────────┐       │
│  │  OSC Output  │         │  UDP Socket  │        │  File Logger │       │
│  │  Port 9880   │         │  Port 9881   │        │  JSON Lines  │       │
│  └──────────────┘         └──────────────┘        └──────────────┘       │
│                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Schema (Streaming Format)

```json
{
  "timestamp": 1702483200.123,
  "transport": {
    "playing": true,
    "bpm": 128.0,
    "position_beats": 16.25,
    "time_signature": [4, 4]
  },

  "master": {
    "levels": {
      "peak_L": -3.2,
      "peak_R": -2.8,
      "rms_L": -14.5,
      "rms_R": -14.2,
      "lufs_short": -12.3,
      "lufs_integrated": -14.1,
      "true_peak": -2.1
    },
    "stereo": {
      "correlation": 0.72,
      "width": 0.65,
      "balance": 0.02,
      "mono_compatible": true
    },
    "spectrum": {
      "bands": [
        {"freq": 31, "magnitude": -24.5},
        {"freq": 63, "magnitude": -18.2},
        {"freq": 125, "magnitude": -12.8},
        {"freq": 250, "magnitude": -15.3},
        {"freq": 500, "magnitude": -16.1},
        {"freq": 1000, "magnitude": -14.7},
        {"freq": 2000, "magnitude": -18.2},
        {"freq": 4000, "magnitude": -22.4},
        {"freq": 8000, "magnitude": -28.1},
        {"freq": 16000, "magnitude": -35.6}
      ],
      "spectral_centroid": 1842.5,
      "spectral_rolloff": 6234.0,
      "spectral_flux": 0.023
    },
    "dynamics": {
      "crest_factor": 12.3,
      "dynamic_range": 18.5
    }
  },

  "tracks": [
    {
      "index": 0,
      "name": "Kick",
      "levels": {
        "peak": -6.2,
        "rms": -18.4
      },
      "pan": 0.0,
      "volume": 0.75,
      "muted": false,
      "soloed": false,
      "spectrum_summary": {
        "low_energy": 0.65,
        "mid_energy": 0.28,
        "high_energy": 0.07
      }
    },
    {
      "index": 1,
      "name": "Bass",
      "levels": {
        "peak": -8.1,
        "rms": -16.2
      },
      "pan": 0.0,
      "volume": 0.70,
      "muted": false,
      "soloed": false,
      "spectrum_summary": {
        "low_energy": 0.72,
        "mid_energy": 0.24,
        "high_energy": 0.04
      }
    }
  ],

  "analysis": {
    "frequency_masking": [
      {
        "track_a": "Kick",
        "track_b": "Bass",
        "frequency_range": "60-120Hz",
        "overlap_score": 0.73,
        "severity": "moderate"
      }
    ],
    "stereo_field": {
      "center_weight": 0.62,
      "left_weight": 0.19,
      "right_weight": 0.19,
      "hole_in_middle": false
    }
  }
}
```

---

## Implementation: Max for Live Analysis Engine

### 1. Spectrum Analysis (25 Bark Bands)

```maxpat
// Using analyzer~ external or custom fft~
[adc~ 1 2]
    |
[pfft~ spectrum_analysis 2048 4]
    |
// Inside pfft~ subpatch:
// [fftin~ 1]
//     |
// [cartopol~]  // Convert to magnitude/phase
//     |
// [fftout~ 1]

// Alternative: Tristan Jehan's analyzer~
[analyzer~ 25 0.02]  // 25 bark bands, 20ms smoothing
    |
[route pitch loudness bark]
         |
    [zl slice 25]  // Get all 25 bands
```

### 2. Stereo Correlation Calculation

```maxpat
// Input: Left and Right channels
[adc~ 1]          [adc~ 2]
    |                 |
[*~]────────────[*~]  // Square each channel
    |                 |
[average~ 4096]  [average~ 4096]  // Energy of each
    |                 |
[sqrt~]          [sqrt~]           // RMS
    |                 |
    └────[*~]─────────┘             // Product of RMS values
              |
              ▼
         [/~]                        // Divide cross-correlation by product
              |
         [snapshot~ 30]              // Output 30x per second
              |
    correlation (-1 to +1)
```

### 3. Stereo Width (Mid/Side)

```maxpat
[adc~ 1]          [adc~ 2]
    |                 |
    └──[+~ 0.5]───────┘    // Mid = (L + R) / 2
    └──[-~ 0.5]───────┘    // Side = (L - R) / 2
          |                      |
    [average~ 4096]        [average~ 4096]
          |                      |
     mid_energy              side_energy
          |                      |
          └────[/]───────────────┘
                    |
           width = side / (mid + side)
```

### 4. OSC Output

```maxpat
// Aggregate all analysis data
[pack f f f f f f ...]  // All values
    |
[prepend /mix/analysis]
    |
[udpsend 127.0.0.1 9880]
```

---

## Optimal Device Chain for Mix Analysis

### Master Bus Setup

```
┌─────────────────────────────────────────────────────┐
│                   MASTER TRACK                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [1] Mix Analysis Hub M4L    ← Our custom device    │
│      └── Receives sidechain from all tracks         │
│                                                      │
│  [2] EQ Eight                ← For visual reference │
│      └── Analyzer ON                                │
│                                                      │
│  [3] Utility                 ← Mono check           │
│      └── Width = 100% (or 0% for mono test)        │
│                                                      │
│  [4] Limiter                 ← Final stage          │
│      └── True Peak mode                             │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Per-Track Analysis (Optional)

For detailed per-track analysis, each track gets a lightweight M4L device:

```
┌─────────────────────────────────────────────────────┐
│                   AUDIO TRACK                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [Pre-FX] Track Analyzer M4L (lightweight)          │
│           └── RMS, Peak, Spectrum summary           │
│           └── Sends data to Master Hub              │
│                                                      │
│  [...] Other effects                                │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Comparison: What We CAN vs CANNOT Measure

### CAN Measure (via M4L)

| Feature | Method | Accuracy |
|---------|--------|----------|
| Frequency spectrum | fft~/pfft~ | High |
| RMS level | average~ | High |
| Peak level | peakamp~ | High |
| Stereo correlation | Cross-correlation | High |
| Stereo width | Mid/Side ratio | High |
| Spectral centroid | Weighted average | High |
| LUFS | mc.limi~ or external | Medium-High |
| Crest factor | Peak/RMS | High |
| Track pan/volume | Live API | Exact |
| Device parameters | Live API | Exact |

### CANNOT Measure (Limitations)

| Feature | Reason |
|---------|--------|
| EQ Eight analyzer data | Not exposed in API |
| Native Spectrum bins | Not exposed in API |
| Tuner pitch values | Not exposed in API |
| Inter-track masking | Requires multi-sidechain analysis |

---

## User Flow (Minimal Friction)

### Setup (One-Time)

1. User installs "Mix Analysis Hub" M4L device
2. Drops device on Master track
3. (Optional) Enable per-track analysis via button

### Usage (Zero Friction)

1. User produces music normally
2. Mix Analysis Hub streams data in background
3. LLM receives real-time mix state
4. LLM can query current state or historical data
5. LLM generates mixing suggestions/actions

### Data Collection Mode

1. User enables "Capture Mode" button
2. Hub logs all analysis data to JSON file
3. User makes mixing decisions
4. Hub logs parameter changes via Live API
5. Creates training pairs: (audio_state, user_action)

---

## Integration with LLM

### Real-Time Query

```
User: "How's my low end?"

LLM receives:
- spectrum bands 31-125 Hz
- kick/bass track energies
- frequency masking scores

LLM responds:
"Your low end is accumulating around 80Hz. The kick and bass
are both fighting for that frequency. I'd suggest cutting
the bass around 80Hz by 3-4dB to let the kick punch through."
```

### Action Generation

```python
# LLM generates MCP command
{
    "type": "set_device_parameter",
    "track": "Bass",
    "device": "EQ Eight",
    "parameter": "2 Frequency A",
    "value": 0.31,  # ~80Hz
    "reasoning": "Cut bass at 80Hz to reduce masking with kick"
}
```

---

## Existing M4L Devices to Leverage

| Device | Author | Features | Link |
|--------|--------|----------|------|
| **SL Oscilloscope** | Searchlife | Goniometer, Correlation, Balance, Peak | [maxforlive.com](https://maxforlive.com/library/device/9064/sl-oscilloscope) |
| **Swiss Army Meter** | NoirLabs | LUFS, RMS, True Peak, LRA | [maxforlive.com](https://maxforlive.com/library/device/9055/swiss-army-meter) |
| **Multi Analyser XL** | Mark Towers | Multi-track spectrum | [isotonikstudios.com](https://isotonikstudios.com/product/multi-analyser-xl-upgraded-analysis-for-ableton-live/) |
| **Flufs** | lostmybass | LUFS with CSV export | [maxforlive.com](https://maxforlive.com) |
| **Live.API Explorer** | matcham | LOM exploration tool | [maxforlive.com](https://www.maxforlive.com/library/device/331/live-api-explorer) |

### Build vs Buy Decision

| Component | Build Custom | Use Existing |
|-----------|--------------|--------------|
| Spectrum analysis | Yes (need OSC output) | - |
| Stereo correlation | Yes (need OSC output) | SL Oscilloscope (visual only) |
| LUFS metering | Yes (need data stream) | Swiss Army Meter (visual only) |
| Live API access | Yes (need automation) | Live.API Explorer (manual) |

**Conclusion**: Build custom Hub that combines all features with data streaming.

---

## Pros & Cons

### Pros

- **Zero external dependencies** - Works with stock Ableton + M4L
- **Any producer can use it** - No special hardware
- **Real-time streaming** - Continuous data flow
- **Accurate measurements** - Direct signal analysis
- **Full Live API access** - Can read/write all parameters
- **Training data collection** - Capture user decisions

### Cons

- **CPU overhead** - FFT analysis uses resources
- **Limited to what's audible** - No "spatial reference" like VSX
- **Single listening environment** - No room simulation
- **Requires M4L** - Suite or Standard + M4L add-on

---

## Comparison: Approach 1 vs Approach 2

| Aspect | Approach 1 (VSX) | Approach 2 (Native) |
|--------|------------------|---------------------|
| **Dependencies** | VSX hardware + license | M4L only |
| **User friction** | High (must own VSX) | Low (Suite users) |
| **Spatial reference** | Yes (binaural HRTF) | No |
| **IPD/ILD features** | Yes | No |
| **Real-time streaming** | Batch processing | Yes |
| **Training data capture** | Offline | Real-time |
| **Universal applicability** | Limited | High |

---

## Implementation Roadmap

### Phase 1: Core Analysis Hub
- [ ] Build fft~ spectrum analyzer (25 bands)
- [ ] Implement stereo correlation meter
- [ ] Implement stereo width meter
- [ ] Add RMS/Peak metering
- [ ] OSC output stream

### Phase 2: Live API Integration
- [ ] Track enumeration
- [ ] Device parameter reading
- [ ] Real-time parameter change detection
- [ ] Transport state monitoring

### Phase 3: Data Logging
- [ ] JSON line format logger
- [ ] Session state snapshots
- [ ] Parameter change history
- [ ] Audio state correlation

### Phase 4: LLM Integration
- [ ] OSC receiver in Python
- [ ] State → LLM prompt formatting
- [ ] Action parsing from LLM response
- [ ] MCP command execution

---

## Context Priority Hierarchy

The LLM needs to understand **what audio to analyze** and **when**. This hierarchy determines context assembly:

### Level 1: Track Selection (Immediate User Focus)

**The user's track selection is the #1 priority signal.** This reflects their immediate intent.

```python
class FocusTracker:
    """Monitors user's track selection to determine analysis focus."""

    def __init__(self, live_api):
        self.live_api = live_api
        self.last_selection = None

    def get_current_focus(self) -> dict:
        """Get current user focus based on track selection."""
        selected_track = self.live_api.get("live_set.view.selected_track")

        return {
            "track": {
                "name": selected_track.get("name"),
                "type": self.classify_track_type(selected_track),
                "index": selected_track.get("index"),
                "is_group": selected_track.get("is_foldable"),
                "group_parent": self.get_group_parent(selected_track)
            },
            "multi_select": self.detect_multi_track_selection(),
            "selection_changed": self.check_selection_changed(selected_track),
            "view_mode": self.get_view_mode()  # Session vs Arrangement
        }

    def classify_track_type(self, track) -> str:
        """Classify track type for context assembly."""
        if track.get("is_master"):
            return "master"
        elif track.get("is_return"):
            return "return"
        elif track.get("is_foldable"):
            return "group"
        elif track.get("has_midi_input"):
            return "midi"
        else:
            return "audio"

    def detect_multi_track_selection(self) -> list:
        """Check if user has multiple tracks selected (shift-click)."""
        # Note: Live API doesn't directly expose multi-selection
        # Workaround: Monitor highlighted_clip_slot across tracks
        return self.live_api.get("live_set.view.highlighted_clip_slot")
```

#### Context Assembly by Selection Type

| Selection | Primary Focus | Secondary Context |
|-----------|---------------|-------------------|
| **Single Track** | That track only | Sends → Return tracks |
| **Group Track** | All children | Group bus processing |
| **Return Track** | Return chain | All tracks sending to it |
| **Master Track** | Full mix | All active tracks |
| **Multi-Track** | Selected tracks | Relationship analysis |

### Level 2: Time Region Markers

```python
def get_time_region_context(self) -> dict:
    """Get user-defined time regions."""
    return {
        "loop_brace": {
            "start_beat": self.live_api.get("live_set.loop_start"),
            "end_beat": self.live_api.get("live_set.loop_start") +
                       self.live_api.get("live_set.loop_length"),
            "is_active": self.live_api.get("live_set.loop")
        },
        "cue_points": self.get_cue_points(),  # User-defined markers
        "current_position": self.live_api.get("live_set.current_song_time")
    }

def get_cue_points(self) -> list:
    """Get all locator/cue points from Live."""
    cue_points = self.live_api.get("live_set.cue_points")
    return [
        {"name": cp.get("name"), "time": cp.get("time")}
        for cp in cue_points
    ]
```

### Level 3: Behavior Patterns (Implicit Intent)

```python
class BehaviorTracker:
    """Track user editing patterns to infer focus areas."""

    def __init__(self):
        self.position_history = []  # Last N playhead positions
        self.edit_locations = []    # Where user made changes
        self.loop_count = {}        # How many times each region played

    def record_position(self, beat: float):
        self.position_history.append({
            "beat": beat,
            "timestamp": time.time()
        })
        # Keep last 100 positions
        self.position_history = self.position_history[-100:]

    def detect_focus_region(self) -> dict:
        """Infer which region user is focused on."""
        if len(self.position_history) < 10:
            return None

        # Find most frequent bar range
        bars = [int(p["beat"] / 4) for p in self.position_history]
        bar_counts = Counter(bars)
        most_common = bar_counts.most_common(1)[0]

        return {
            "inferred_focus_bar": most_common[0],
            "confidence": most_common[1] / len(bars),
            "pattern": self.classify_pattern()
        }

    def classify_pattern(self) -> str:
        """Classify user behavior pattern."""
        if self.is_sequential_playback():
            return "linear_listening"
        elif self.is_loop_editing():
            return "loop_refinement"
        elif self.is_jumping_around():
            return "comparison_mode"
        return "unknown"
```

### Level 4: Audio Novelty Detection

When no explicit markers exist, use audio analysis to detect section changes:

```python
def detect_section_boundaries(self, analysis_cache: dict) -> list:
    """
    Detect section boundaries using Foote's checkerboard kernel.
    Research: Foote, J. (2000). "Automatic Audio Segmentation Using
    a Measure of Audio Novelty"
    """
    # Build self-similarity matrix from spectral features
    ssm = self.build_self_similarity_matrix(analysis_cache)

    # Apply checkerboard kernel for novelty detection
    kernel_size = 16  # bars
    novelty_curve = self.checkerboard_kernel_novelty(ssm, kernel_size)

    # Peak picking for boundaries
    boundaries = self.pick_peaks(novelty_curve, min_distance=8)

    return [
        {"bar": b, "novelty_score": novelty_curve[b]}
        for b in boundaries
    ]

def build_self_similarity_matrix(self, cache: dict) -> np.ndarray:
    """Build SSM from cached spectral features."""
    features = np.array([
        cache[bar]["spectrum_10band"]
        for bar in sorted(cache.keys())
    ])
    # Cosine similarity
    norms = np.linalg.norm(features, axis=1, keepdims=True)
    normalized = features / (norms + 1e-8)
    return normalized @ normalized.T
```

### Level 5: Beat-Aligned Grid (Fallback)

When all else fails, use musical structure:

```python
def get_grid_context(self, current_bar: int, window_size: int = 32) -> dict:
    """Fallback: 32-bar context centered on current position."""
    return {
        "start_bar": max(0, current_bar - window_size // 2),
        "end_bar": min(self.song_length, current_bar + window_size // 2),
        "grid_type": "beat_aligned",
        "time_signature": self.live_api.get("live_set.signature_numerator")
    }
```

---

## 32-Bar Context Window Architecture

### Design Decision

**Context window: 16 bars before + 16 bars after current position = 32 bars total**

This provides:
- Sufficient context to understand musical phrases (typically 4-8 bars)
- Two full sections for comparison (verse vs chorus, etc.)
- Forward context for predictive suggestions

### Token Budget Analysis

```
Per-bar data structure:
- bar_number: 4 bytes
- spectrum_10band: 10 floats × 4 bytes = 40 bytes
- levels (rms, peak): 8 bytes
- stereo (correlation, width): 8 bytes
- active_tracks (list of names): ~50 bytes avg
- novelty_score: 4 bytes

Total per bar: ~114 bytes → ~100 tokens

32 bars × ~100 tokens = ~3,200 tokens
```

**Budget: ~10% of 32K context window** - leaves ample room for:
- System prompt
- Conversation history
- LLM reasoning
- Tool calls and responses

### Context Assembly

```python
class ContextAssembler:
    """Assembles 32-bar context window for LLM."""

    def __init__(self, bar_cache: dict, prescan_manager):
        self.bar_cache = bar_cache
        self.prescan_manager = prescan_manager
        self.song_length_bars = 0

    def build_32bar_context(self, current_bar: int, focus: dict) -> dict:
        """
        Build complete context for LLM consumption.

        Args:
            current_bar: Current playhead position (in bars)
            focus: Output from FocusTracker.get_current_focus()
        """
        start_bar = max(0, current_bar - 16)
        end_bar = min(self.song_length_bars, current_bar + 16)

        # Ensure future bars are pre-scanned
        self.prescan_manager.prescan_if_needed(current_bar, end_bar)

        # Assemble bar-by-bar analysis
        bars_data = []
        for bar in range(start_bar, end_bar):
            bar_analysis = self.bar_cache.get(bar)
            if bar_analysis:
                bars_data.append(bar_analysis)
            else:
                # Mark as not-yet-analyzed
                bars_data.append({
                    "bar_number": bar,
                    "status": "pending_prescan"
                })

        return {
            "window": {
                "center_bar": current_bar,
                "start_bar": start_bar,
                "end_bar": end_bar,
                "total_bars": end_bar - start_bar
            },
            "focus": focus,
            "bars": bars_data,
            "section_boundaries": self.get_section_boundaries(start_bar, end_bar),
            "transport": {
                "bpm": self.live_api.get("live_set.tempo"),
                "playing": self.live_api.get("live_set.is_playing"),
                "time_signature": self.live_api.get("live_set.signature_numerator")
            }
        }
```

### Per-Bar Analysis Structure

```python
bar_analysis = {
    "bar_number": 24,
    "timestamp_start": 12.0,  # seconds from song start
    "timestamp_end": 14.0,

    # Spectral (10 bands: 31, 63, 125, 250, 500, 1k, 2k, 4k, 8k, 16k Hz)
    "spectrum_10band": [0.12, 0.34, 0.45, 0.38, 0.42, 0.35, 0.28, 0.22, 0.15, 0.08],
    "spectral_centroid": 1842.5,
    "spectral_flux": 0.023,

    # Dynamics
    "levels": {
        "rms": -14.2,
        "peak": -6.1,
        "crest_factor": 8.1
    },

    # Stereo
    "stereo": {
        "correlation": 0.72,
        "width": 0.58,
        "balance": 0.02
    },

    # Musical context
    "active_tracks": ["Kick", "Bass", "Drums", "Synth Lead"],
    "novelty_score": 0.15,  # Low = similar to previous, High = section change

    # Optional: per-track breakdown (if focused on specific tracks)
    "track_breakdown": {
        "Kick": {"rms": -18.4, "peak": -6.2, "frequency_peak": 65},
        "Bass": {"rms": -16.2, "peak": -8.1, "frequency_peak": 82}
    }
}
```

---

## Pre-Scan System for Future Bars

### Problem

When the user jumps to bar 50, the LLM needs context for bars 50-66 (16 bars ahead). But we haven't analyzed those bars yet if playback hasn't reached them.

### Solution: Quick Pre-Scan

**Pre-scan runs ~50-100x faster than realtime** because:
1. Offline FFT (no real-time constraints)
2. Batch processing (vectorized operations)
3. Lower resolution acceptable (512-point FFT vs 2048)
4. No GUI updates during scan

**Speed estimate**: 16 bars @ 120 BPM = 32 seconds of audio → ~1-2 seconds to scan

### Pre-Scan Manager

```python
class PreScanManager:
    """Manages offline audio analysis for future bars."""

    def __init__(self, audio_accessor, bar_cache: dict):
        self.audio_accessor = audio_accessor  # M4L audio buffer access
        self.bar_cache = bar_cache
        self.scan_queue = []
        self.is_scanning = False
        self.scan_thread = None

    def on_transport_state_change(self, is_playing: bool):
        """Trigger pre-scan when playback stops."""
        if not is_playing and not self.is_scanning:
            self.trigger_prescan()

    def on_user_idle(self, idle_seconds: float):
        """Trigger pre-scan during user idle time."""
        if idle_seconds > 2.0 and not self.is_scanning:
            self.trigger_prescan()

    def on_position_jump(self, new_bar: int):
        """User jumped to new position - prioritize that region."""
        # Clear queue and prioritize new region
        self.scan_queue = []
        self.queue_region(new_bar - 16, new_bar + 16, priority=True)
        self.trigger_prescan()

    def prescan_if_needed(self, start_bar: int, end_bar: int):
        """Ensure bars are scanned, queue if not."""
        missing_bars = [
            bar for bar in range(start_bar, end_bar)
            if bar not in self.bar_cache
        ]

        if missing_bars:
            self.queue_region(min(missing_bars), max(missing_bars) + 1)
            # If critical (user waiting), do synchronous scan
            if len(missing_bars) > 8:
                self.trigger_prescan(blocking=True)

    def trigger_prescan(self, blocking=False):
        """Start background pre-scan."""
        if blocking:
            self._run_scan()
        else:
            if self.scan_thread and self.scan_thread.is_alive():
                return  # Already scanning
            self.scan_thread = threading.Thread(target=self._run_scan)
            self.scan_thread.start()

    def _run_scan(self):
        """Execute pre-scan on queued regions."""
        self.is_scanning = True

        while self.scan_queue:
            bar = self.scan_queue.pop(0)
            if bar in self.bar_cache:
                continue  # Already scanned

            # Get audio for this bar
            audio_data = self.audio_accessor.get_bar_audio(bar)
            if audio_data is None:
                continue

            # Quick FFT analysis (lower resolution)
            analysis = self.quick_analyze(audio_data)
            self.bar_cache[bar] = analysis

        self.is_scanning = False

    def quick_analyze(self, audio: np.ndarray) -> dict:
        """
        Fast offline analysis for pre-scanning.
        Uses 512-point FFT for speed (vs 2048 realtime).
        """
        # Stereo to mono for speed
        if audio.ndim == 2:
            mono = (audio[:, 0] + audio[:, 1]) / 2
            left, right = audio[:, 0], audio[:, 1]
        else:
            mono = audio
            left = right = audio

        # Quick 512-point FFT
        fft_result = np.fft.rfft(mono[:512])
        magnitudes = np.abs(fft_result)

        # Bin to 10 bands
        spectrum_10band = self.bin_to_10bands(magnitudes)

        # Quick level calc
        rms = 20 * np.log10(np.sqrt(np.mean(mono ** 2)) + 1e-10)
        peak = 20 * np.log10(np.max(np.abs(mono)) + 1e-10)

        # Stereo correlation
        correlation = np.corrcoef(left, right)[0, 1] if len(left) > 0 else 0

        return {
            "bar_number": -1,  # Set by caller
            "spectrum_10band": spectrum_10band.tolist(),
            "levels": {"rms": rms, "peak": peak},
            "stereo": {"correlation": correlation},
            "scan_type": "prescan"
        }
```

### Pre-Scan Triggers

| Trigger | Delay | Priority |
|---------|-------|----------|
| Playback stops | Immediate | High |
| User idle > 2s | 2 seconds | Medium |
| Position jump | Immediate | Critical |
| Session load | Background | Low |
| Loop region change | 500ms | High |

---

## MCP Integration

### Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER PRODUCES MUSIC                                 │
│                     (Ableton Live 12 Suite + M4L)                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MIX ANALYSIS HUB (M4L)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [Real-Time Analysis]          [Focus Tracker]          [Pre-Scan]  │   │
│  │  • Spectrum (10 bands)         • Track selection        • Offline   │   │
│  │  • RMS/Peak                    • Multi-select           • Batch FFT │   │
│  │  • Stereo correlation          • View mode              • Caching   │   │
│  │  • Width/Balance               • Selection changes      • Queuing   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                          │
│                          [OSC Stream @ 30Hz]                                │
│                           Port 9880 → Python                                │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MIX ANALYSIS BRIDGE (Python)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [OSC Receiver]     [Bar Cache]      [Context Assembler]            │   │
│  │  • pythonosc        • In-memory      • 32-bar window               │   │
│  │  • Async handler    • LRU eviction   • Focus integration           │   │
│  │  • Rate limiting    • Persistence    • Section boundaries          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                          │
│                       [Structured Context JSON]                             │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MLX LLM (Qwen3-4B)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  INPUT:                          │  OUTPUT:                         │   │
│  │  • 32-bar context (~3K tokens)   │  • Mixing suggestions            │   │
│  │  • Current focus (track/region)  │  • Parameter adjustments         │   │
│  │  • Transport state               │  • MCP tool calls                │   │
│  │  • User query                    │  • Explanations                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                          │
│                          [Parse Tool Calls]                                 │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MCP CLIENT (mcp package)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  AVAILABLE TOOLS (via ableton-mcp):                                 │   │
│  │  • set_tempo                    • create_midi_track                 │   │
│  │  • set_device_parameter         • get_session_info                  │   │
│  │  • add_notes_to_clip           • fire_clip / stop_clip             │   │
│  │  • start_playback / stop_playback                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                          │
│                          [Execute via MCP]                                  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ABLETON LIVE (via Remote Script)                       │
│                    AbletonMCP_Extended Remote Script                          │
│                                                                              │
│             ← CHANGES REFLECTED IN REAL-TIME ←                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Example Interaction

```python
# User asks about the mix while working on bar 24
user_query = "The verse feels muddy, what should I adjust?"

# Context assembled automatically
context = {
    "window": {"center_bar": 24, "start_bar": 8, "end_bar": 40},
    "focus": {
        "track": {"name": "Bass", "type": "midi"},
        "multi_select": False,
        "view_mode": "arrangement"
    },
    "bars": [
        # ... 32 bars of analysis data ...
        {"bar_number": 24, "spectrum_10band": [0.42, 0.65, 0.71, ...], ...}
    ],
    "section_boundaries": [{"bar": 16, "novelty_score": 0.82}]
}

# LLM receives context + query
llm_response = mlx_inference(
    system_prompt=MIXING_ASSISTANT_PROMPT,
    context=json.dumps(context),
    query=user_query
)

# LLM output (example):
"""
Looking at bars 8-40, I see the issue. Your bass and kick are both
heavy around 80-120Hz (spectrum shows 0.65 and 0.71 in those bands).

I recommend:
1. Cut the bass around 80Hz to let the kick punch through
2. Add a slight boost at 200Hz on the bass for definition

<tool_call>
{"name": "set_device_parameter",
 "track": "Bass",
 "device": "EQ Eight",
 "parameter": "2 Gain A",
 "value": -4.0}
</tool_call>
"""

# MCP executes the parameter change
mcp_client.call_tool("set_device_parameter", {
    "track": "Bass",
    "device": "EQ Eight",
    "parameter": "2 Gain A",
    "value": -4.0
})
```

### New MCP Tools Needed

To fully support this architecture, we need to extend ableton-mcp with:

| Tool | Purpose | Status |
|------|---------|--------|
| `get_track_devices` | List all devices on a track | Needed |
| `get_device_parameters` | Get all params for a device | Needed |
| `set_device_parameter` | Set a specific param value | Exists |
| `get_arrangement_position` | Current playhead bar | Needed |
| `get_selected_track` | Which track is selected | Needed |
| `get_cue_points` | Get all locators | Needed |

---

## References

- [Ableton Live 12 Audio Effect Reference](https://www.ableton.com/en/manual/live-audio-effect-reference/)
- [Live Object Model (LOM) Documentation](https://docs.cycling74.com/legacy/max8/vignettes/live_object_model)
- [Max for Live Phase Correlation Meter](https://cycling74.com/tools/max-for-live-phase-correlation-meter)
- [SL Oscilloscope](https://maxforlive.com/library/device/9064/sl-oscilloscope)
- [Swiss Army Meter](https://maxforlive.com/library/device/9055/swiss-army-meter)
- [pfft~ Tutorial](https://docs.cycling74.com/max8/tutorials/14_analysischapter04)
- [Live API Overview](https://docs.cycling74.com/max8/vignettes/live_api_overview)
