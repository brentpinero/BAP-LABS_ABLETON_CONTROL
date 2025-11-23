# 🧪 SERUM 2 AUTO-LOADING TEST INSTRUCTIONS

**Current Status**: Serum 2 auto-loading is WORKING in `serum2_autoload_test.maxpat`! These instructions guide you through testing parameter control and MIDI validation.

## OPTION 1: Test the Working Device

1. **Open `serum2_autoload_test.maxpat` in Max**
   - Serum 2 should auto-load immediately (VST3 format)
   - Check Max console for: "✅ Serum 2 loaded successfully"

2. **Test Parameter Discovery**:
   - Click the green "Discover Parameters" button
   - Watch console for parameter list
   - Should show ~2,397 parameters with names

3. **Test Parameter Control**:
   - Click the manual parameter messages (1 0.5, 2 0.3, etc.)
   - These use 1-based indexing (parameter 1, not 0)
   - Watch Serum 2 UI for visual changes

4. **Test Automated Sequence**:
   - Click blue "Test Parameter Control" button
   - Runs through multiple parameter changes
   - Verifies each parameter change in console

## OPTION 2: Manual JavaScript Testing

In Max console, test the JavaScript controller directly:

1. **Open the patcher and Max console**
2. **Send messages to the js object**:
   ```
   ; max script sendbox serum2_autoload_controller verify_serum2
   ; max script sendbox serum2_autoload_controller discover_params
   ; max script sendbox serum2_autoload_controller test_sequence
   ```

3. **Expected responses**:
   - `verify_serum2`: Confirms Serum 2 is loaded
   - `discover_params`: Lists all parameter names
   - `test_sequence`: Runs automated parameter test

## OPTION 3: Create Your Own Test

1. **Create a new patcher**
2. **Add this object**: `vst~ 2 2 Serum2`
   - Auto-loads Serum 2 on creation
   - 2 inputs, 2 outputs, plugin name
3. **Add**: `@prefer VST3` attribute if needed
4. **Test with these messages**:
   - `getplugname` → Should return "Serum2"
   - `params` → Lists all parameters
   - `get` → Returns parameter count

## What We're Looking For:

Successful Serum 2 parameter discovery shows:

```
✅ Serum 2 loaded successfully: Serum2
✅ Serum 2 has 2397 parameters total
📡 Serum 2 parameter: Master Volume (index 1)
📡 Serum 2 parameter: OSC A Level (index 2)
📡 Serum 2 parameter: OSC A Pitch (index 3)
📡 Serum 2 parameter: OSC A Fine (index 4)
...etc (up to 2397 parameters)
```

## Testing Parameter Control:

**IMPORTANT**: Serum 2 uses 1-based indexing!

1. Create message: `1 0.5` (sets Master Volume to 50%)
2. Create message: `2 0.3` (sets OSC A Level to 30%)
3. Connect to vst~ inlet
4. Click messages and watch Serum 2 UI
5. Verify with: `get 1` to read current value

## The Key Messages for Serum 2 VST~:

- `getplugname` - Verify Serum 2 is loaded
- `params` - Get all parameter names (outlet 2)
- `get` - Get parameter count ("paramcount 2397")
- `get 1` - Get value of parameter 1
- `1 0.5` - Set parameter 1 to value 0.5 (1-based!)
- `midievent 144 60 127` - Note On C4
- `midievent 128 60 0` - Note Off C4
- `program 1` - Load preset 1

## Structured Output for LLM Training:

Based on working Serum 2 control, LLM should output:

```json
{
  "preset_name": "Warm Bass",
  "parameter_changes": [
    {"index": 1, "value": 0.7, "name": "Master Volume"},
    {"index": 2, "value": 0.8, "name": "OSC A Level"},
    {"index": 15, "value": 0.3, "name": "Filter Cutoff"},
    {"index": 16, "value": 0.2, "name": "Filter Resonance"}
  ],
  "midi_notes": [
    {"type": "note_on", "note": 36, "velocity": 100}
  ]
}
```

## Next Steps:

1. **Validate all critical parameters** respond correctly
2. **Map parameter names to indices** for training data
3. **Test MIDI note triggering** for instrument presets
4. **Generate training examples** with real parameter changes
5. **Integrate with LLM inference pipeline**

## Troubleshooting:

- **Serum 2 not loading**: Check `/Library/Audio/Plug-Ins/VST3/Serum2.vst3`
- **Wrong version**: Make sure it's Serum 2, not Serum 1
- **Parameters not responding**: Verify 1-based indexing
- **No parameter names**: Try `plug_vst3 Serum2` message