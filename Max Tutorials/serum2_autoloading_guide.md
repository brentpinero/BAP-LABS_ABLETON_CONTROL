# SERUM 2 AUTO-LOADING GUIDE
## Automatic Plugin Loading in Max VST~ Objects

**Research Date:** September 2024
**Target Plugin:** Serum 2 (VST3/AU format only)

## Key Findings

### Serum 2 vs Original Serum
- **Serum 2 is VST3/AU ONLY** - No VST2 support
- **Plugin Name:** `Serum2` (not `Serum`)
- **Format Preference:** VST3 recommended over AU
- **Installation Path:** `/Library/Audio/Plug-Ins/VST3/Serum2.vst3`

### Auto-Loading Methods

#### Method 1: VST~ Object Arguments (Recommended)
```
vst~ 2 2 Serum2
```
**Structure:**
- `2 2` = 2 inputs, 2 outputs
- `Serum2` = plugin name argument
- Automatically loads on patcher open

#### Method 2: Loadbang + Message
```
[loadbang] → [plug_vst3 Serum2] → [vst~]
```

#### Method 3: Prefer Attribute + Generic Loading
```
vst~ @prefer VST3
[plug Serum2] → [vst~]
```

### Complete JSON Configuration

```json
{
  "box": {
    "id": "obj-vst",
    "maxclass": "newobj",
    "text": "vst~ 2 2 Serum2",
    "numinlets": 2,
    "numoutlets": 8,
    "outlettype": ["signal", "signal", "", "list", "", "", "", ""],
    "patching_rect": [15, 195, 400, 22],
    "saved_object_attributes": {
      "parameter_enable": 0,
      "prefer": "VST3",
      "autosave": 1
    }
  }
}
```

### Critical Attributes

| Attribute | Value | Purpose |
|-----------|-------|---------|
| `prefer` | `"VST3"` | Force VST3 format selection |
| `autosave` | `1` | Save plugin state with patch |
| `parameter_enable` | `0` | Disable Live automation (for testing) |

### Loading Verification

**Check if Serum 2 loaded:**
```
[getplugname] → [vst~] → [print plugin_name]
```

**Expected output:** Should contain "Serum" in the plugin name

### Common Loading Issues

#### Issue: "Unknown" Plugin in Inspector
**Causes:**
- Plugin name mismatch (`Serum` vs `Serum2`)
- VST3 not installed properly
- Max search path doesn't include VST3 folder

**Solutions:**
- Use exact name `Serum2`
- Set `@prefer VST3`
- Verify installation path

#### Issue: Double-click Doesn't Show Plugin List
**Causes:**
- VST scan incomplete
- Plugin path not in Max preferences
- Plugin format conflicts

**Solutions:**
- Rescan VST plugins in Max preferences
- Add `/Library/Audio/Plug-Ins/VST3/` to search paths
- Use `plug_vst3` message instead

#### Issue: Plugin Loads But No Parameters
**Causes:**
- Plugin still initializing
- Parameter discovery timing
- Plugin format issues

**Solutions:**
- Add delay before parameter discovery
- Use `params` message after confirmed loading
- Verify plugin responds to `get` messages

### Alternative Loading Approaches

#### Audio Unit Format (macOS only)
```
[plug_au Serum2] → [vst~]
```

#### Generic Plugin Loading
```
[plug Serum2] → [vst~]
```
*Note: Less reliable, use format-specific methods*

#### Manual Plugin Selection
```
[plug] → [vst~]
```
*Opens plugin browser - not suitable for auto-loading*

### State Management

#### Auto-Save Plugin State
```json
"saved_object_attributes": {
  "autosave": 1
}
```

#### Preset Loading
```
[1] → [program] → [vst~]
```

#### Snapshot Management
```
[snapshot] → [vst~] → [save serum2_state.json]
[load serum2_state.json] → [vst~]
```

### Integration with JavaScript

```javascript
function loadbang() {
    // Verify plugin loaded
    outlet(0, "getplugname");

    // Auto-discover parameters after delay
    var timer = new Task(function() {
        outlet(0, "params");
    });
    timer.schedule(2000);
}

function anything() {
    if (messagename === "plugname") {
        var plugin_name = arrayfromargs(arguments).join(" ");
        if (plugin_name.toLowerCase().includes("serum")) {
            post("✅ Serum 2 loaded successfully");
        }
    }
}
```

### Best Practices

1. **Use VST3 Format:** More stable than AU for Serum 2
2. **Include Plugin Argument:** `vst~ 2 2 Serum2` for auto-loading
3. **Verify Loading:** Always check `getplugname` response
4. **Delay Parameter Discovery:** Wait 1-2 seconds after loading
5. **Handle Loading Failures:** Provide fallback loading methods
6. **Save Plugin State:** Use `autosave` for persistence

### Troubleshooting Checklist

- [ ] Serum 2 installed to `/Library/Audio/Plug-Ins/VST3/`
- [ ] Max VST preferences include VST3 path
- [ ] Using exact plugin name `Serum2`
- [ ] Set `@prefer VST3` attribute
- [ ] Plugin responds to `getplugname` message
- [ ] Parameter discovery delayed after loading
- [ ] No VST2 fallback attempts (Serum 2 doesn't support VST2)

This guide ensures reliable Serum 2 auto-loading in Max patches without manual intervention.