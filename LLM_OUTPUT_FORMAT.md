# 🤖 SERUM 2 LLM OUTPUT FORMAT

Based on confirmed working VST~ control in Max for Live, the LLM should output structured commands for Serum 2 automation.

## Confirmed Working Parameters

- **Total Parameters**: 2,623 (verified with `get -4`)
- **Indexing**: 1-based (1, 2, 3... not 0, 1, 2...)
- **Value Range**: 0.0 to 1.0
- **Preset Slots**: 128 programs (Prog 1-128)

## LLM Output Structure

The LLM should output JSON that maps to Max for Live messages:

```json
{
  "request": "Make a warm, fat bass sound with some movement",
  "preset_name": "Warm Fat Bass",
  "category": "Bass",
  "parameter_changes": [
    {
      "index": 1,
      "value": 0.7,
      "name": "Master Volume",
      "reason": "Set moderate volume"
    },
    {
      "index": 2,
      "value": 0.8,
      "name": "OSC A Level",
      "reason": "Strong oscillator A for body"
    },
    {
      "index": 3,
      "value": -0.12,
      "name": "OSC A Pitch",
      "reason": "Detune down an octave for bass"
    },
    {
      "index": 15,
      "value": 0.3,
      "name": "Filter Cutoff",
      "reason": "Low cutoff for warmth"
    },
    {
      "index": 16,
      "value": 0.25,
      "name": "Filter Resonance",
      "reason": "Slight resonance for character"
    }
  ],
  "midi_test": {
    "note": 36,
    "velocity": 100,
    "description": "C1 bass note"
  }
}
```

## Max Message Translation

The JSON translates to these Max messages:

```
; Set parameters
1 0.7
2 0.8
3 -0.12
15 0.3
16 0.25

; Test with MIDI
midievent 144 36 100
midievent 128 36 0
```

## Critical Parameter Indices (Estimated)

Based on typical Serum layout, these are likely indices:

### Oscillators (1-100)
- 1: Master Volume
- 2: OSC A Level
- 3: OSC A Pitch
- 4: OSC A Fine
- 5: OSC A Pan
- 10-20: OSC A Wavetable controls
- 30-50: OSC B controls

### Filter (100-200)
- 100-120: Filter cutoff, resonance, type
- 120-140: Filter envelope

### Envelopes (200-400)
- 200-250: Env 1 (Amp envelope)
- 250-300: Env 2
- 300-350: Env 3

### LFOs (400-600)
- 400-450: LFO 1
- 450-500: LFO 2
- 500-550: LFO 3
- 550-600: LFO 4

### Effects (600-1000)
- Various effect parameters

### Matrix & Modulation (1000-2623)
- Modulation routing and amounts

## Training Data Format

For LLM training, combine request → parameter mapping:

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "Make a bright, cutting lead sound"
    },
    {
      "role": "assistant",
      "content": {
        "analysis": "Creating a bright lead requires high filter cutoff, strong oscillators, and fast attack",
        "parameters": [
          {"index": 1, "value": 0.6, "name": "Master Volume"},
          {"index": 2, "value": 1.0, "name": "OSC A Level"},
          {"index": 100, "value": 0.8, "name": "Filter Cutoff"},
          {"index": 101, "value": 0.4, "name": "Filter Resonance"},
          {"index": 200, "value": 0.01, "name": "Amp Attack"}
        ]
      }
    }
  ]
}
```

## Implementation Pipeline

1. **User Request** → Natural language description
2. **LLM Processing** → Structured parameter changes
3. **Max Translation** → Convert to VST~ messages
4. **Serum Control** → Apply parameters in real-time
5. **Feedback Loop** → Verify values with `get` messages

## Validation Commands

After setting parameters, validate with:
```
get 1    ; Check parameter 1 value
get 2    ; Check parameter 2 value
get -4   ; Verify still 2623 parameters
```

## Next Steps

1. **Map Critical Parameters**: Test indices 1-100 to identify key controls
2. **Build Training Dataset**: Pair descriptions with parameter sets
3. **Test Automation**: Verify smooth parameter transitions
4. **Create Presets**: Save successful combinations
5. **Train LLM**: Fine-tune on parameter mappings

## Success Metrics

- ✅ Parameters respond correctly (verified with diagnostic test)
- ✅ 1-based indexing confirmed
- ✅ 2,623 total parameters available
- ⏳ Need to map parameter names to indices
- ⏳ Need to test parameter ranges and curves
- ⏳ Need to validate modulation routing