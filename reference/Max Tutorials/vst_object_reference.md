# VST~ Object Reference Documentation
## Official Cycling74 Documentation

Source: https://docs.cycling74.com/reference/vst~/

## Overview

The vst~ object hosts VST, VST3, and Audio Unit plugins in Max, allowing real-time audio processing of plugins within Max patches.

## Basic Usage

### Loading Plugins

**Direct argument loading:**
```
vst~ pluginname
```

**Message-based loading:**
```
plug pluginname          // Generic plugin load
plug_vst pluginname      // Specifically load VST2
plug_vst3 pluginname     // Specifically load VST3
plug_au pluginname       // Specifically load Audio Unit (Mac)
```

### Object Variants
- `vst~` - Standard single-channel version
- `mc.vst~` - Multichannel version for complex routing

## Parameter Control

### Parameter Numbering
- **Parameters start at index 1** (not 0!)
- Value range: **0.0 to 1.0** (normalized)
- Parameters can be controlled by index or name

### Parameter Control Messages

**By Index:**
```
list 1 0.5              // Set parameter 1 to 50%
1 0.75                  // Set parameter 1 to 75%
```

**By Name:**
```
parametername 0.25      // Set named parameter to 25%
```

**Getting Parameter Information:**
```
get                     // Get all parameter values
get 1                   // Get parameter 1 value
params                  // List all parameter names
```

### Parameter Output
Parameters output through rightmost outlets in various formats controlled by `valuemode` attribute.

## MIDI Handling

### MIDI Event Messages
```
midievent type data1 data2
midievent type data1 data2 offset
midievent type data1 data2 offset detune
```

**Examples:**
```
midievent 144 60 127    // Note On C4, velocity 127
midievent 128 60 0      // Note Off C4
midievent 176 1 64      // CC 1 (mod wheel) to 64
```

### MPE Events
```
mpeevent type data1 data2 channel
```

## Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `bypass` | int | Disable plugin processing (0/1) |
| `valuemode` | int | Parameter output format |
| `transport` | symbol | Sync with specific transport |
| `prefer` | symbol | Plugin type preference (vst/vst3/au) |
| `editor` | int | Show/hide plugin editor |
| `saveparams` | int | Save parameter states with patch |

## Inlet/Outlet Configuration

### Inlets
- **Inlet 1 (leftmost)**: Control messages, MIDI events
- **Inlet 2+**: Audio signal inputs (matches plugin requirements)

### Outlets
- **Outlets 1-N**: Audio signal outputs (matches plugin outputs)
- **Rightmost outlets**: Parameter/MIDI information output

## Common Messages

| Message | Purpose | Example |
|---------|---------|---------|
| `open` | Open plugin GUI | `open` |
| `close` | Close plugin GUI | `close` |
| `plug` | Load plugin | `plug Serum` |
| `params` | List parameters | `params` |
| `get` | Get parameter values | `get 1` |
| `clear` | Remove loaded plugin | `clear` |
| `bypass` | Bypass processing | `bypass 1` |
| `editor` | Show/hide editor | `editor 1` |

## Parameter Discovery Workflow

**Step 1: Load Plugin**
```
plug "Plugin Name"
```

**Step 2: Get Parameter Count**
```
get
// Outputs: paramcount N
```

**Step 3: List Parameter Names**
```
params
// Outputs parameter names through outlet
```

**Step 4: Control Parameters**
```
1 0.5           // Set parameter 1 to 50%
paramname 0.75  // Set named parameter to 75%
```

## VST~ with Serum Example

**Loading Serum:**
```
plug Serum
// or
plug_vst3 Serum
```

**Getting Serum Parameters:**
```
params          // Lists all ~100+ Serum parameters
get             // Gets current values of all parameters
```

**Controlling Serum:**
```
1 0.5           // Set first parameter (usually volume)
10 0.8          // Set parameter 10
OSC_A_LEVEL 0.6 // Set by name (if available)
```

**Sending MIDI to Serum:**
```
midievent 144 60 127  // Note On C4
midievent 128 60 0    // Note Off C4
```

## Important Notes & Limitations

### Parameter Indexing
- **VST~ uses 1-based indexing** (parameter 1, 2, 3...)
- **Some documentation shows 0-based** - always test!
- Parameter indices may change between preset loads

### Plugin Compatibility
- Not all plugins expose parameters to Max
- Some plugins have proprietary parameter systems
- Generic editor support varies by plugin

### Performance Considerations
- Plugin GUI can impact performance
- Use `bypass` for temporary disable
- Close editors when not needed

### Platform Differences
- VST2/VST3 behavior may differ
- Audio Unit only available on Mac
- Plugin paths vary by OS

## Debugging Tips

**Check Plugin Loading:**
```
// Listen for these messages from vst~:
plugname        // Confirms plugin loaded
paramcount N    // Number of available parameters
```

**Parameter Monitoring:**
```
print paramout  // Connect to parameter outlet
// Shows parameter changes and names
```

**MIDI Debugging:**
```
print midiout   // Connect to MIDI outlet
// Shows MIDI events going to plugin
```

## Common Error Messages

- `"vst~: no such plugin"` - Plugin not found in search paths
- `"vst~: plugin failed to load"` - Plugin compatibility issue
- `"vst~: parameter out of range"` - Invalid parameter index

## Best Practices

1. **Always test parameter indices** with `get` and `params`
2. **Use normalized values** (0.0-1.0) for parameters
3. **Check plugin compatibility** before building patches
4. **Save parameter states** when needed
5. **Close plugin GUIs** to improve performance
6. **Use appropriate plugin type** (VST2/VST3/AU) for best compatibility

This documentation provides the foundation for proper VST~ object usage in Max patches.