# .MAXPAT STRUCTURE RESEARCH
## Definitive Guide to Proper Max Patcher JSON Format

**Research Date:** September 2024
**Purpose:** Eliminate "patchcord destination not found" errors and create properly formatted Max patches

## 1. Object ID Conventions

### Format Rules
- **Format:** `"obj-X"` where X is a sequential number
- **Examples:** `"obj-1"`, `"obj-2"`, `"obj-15"`, `"obj-100"`
- **Requirements:**
  - Must be unique within the patcher
  - Can be any sequential numbering (doesn't have to start at 1)
  - Referenced exactly in patchcord connections
  - Case-sensitive string matching

### Best Practices
```json
✅ CORRECT:
"boxes": [
  {"box": {"id": "obj-1", ...}},
  {"box": {"id": "obj-2", ...}}
],
"lines": [
  {"patchline": {"source": ["obj-1", 0], "destination": ["obj-2", 0]}}
]

❌ INCORRECT:
"lines": [
  {"patchline": {"source": ["obj-1", 0], "destination": ["obj-99", 0]}}
]
// obj-99 doesn't exist in boxes array!
```

## 2. Valid maxclass Names

### Core Max Objects
| maxclass | Purpose | Example |
|----------|---------|---------|
| `"newobj"` | Processing objects | `"text": "print hello"` |
| `"message"` | Message boxes | `"text": "bang"` |
| `"button"` | Bang buttons | No text needed |
| `"toggle"` | Toggle switches | No text needed |
| `"comment"` | Text labels | `"text": "Volume Control"` |
| `"number"` | Integer numbers | No text needed |
| `"flonum"` | Float numbers | No text needed |
| `"inlet"` | Patch inlets | No text needed |
| `"outlet"` | Patch outlets | No text needed |

### Audio Objects
| maxclass | Purpose | Notes |
|----------|---------|-------|
| `"vst~"` | VST host | **NO "vst3~" - this doesn't exist!** |
| `"mc.vst~"` | Multichannel VST | For complex routing |
| `"ezdac~"` | Audio output | Simple DAC |
| `"ezadc~"` | Audio input | Simple ADC |

### Max for Live Objects
| maxclass | Purpose | Automation |
|----------|---------|------------|
| `"live.dial"` | Circular knobs | ✅ Yes |
| `"live.slider"` | Linear sliders | ✅ Yes |
| `"live.menu"` | Dropdown menus | ✅ Yes |
| `"live.button"` | Live buttons | ✅ Yes |
| `"live.text"` | Text buttons | ✅ Yes |
| `"live.toggle"` | Toggle buttons | ✅ Yes |

## 3. VST~ Object Structure

### Basic VST~ Object
```json
{
  "box": {
    "id": "obj-vst",
    "maxclass": "newobj",
    "text": "vst~",
    "numinlets": 2,
    "numoutlets": 8,
    "outlettype": ["signal", "signal", "", "list", "", "", "", ""],
    "patching_rect": [50, 100, 200, 22],
    "saved_object_attributes": {
      "parameter_enable": 0,
      "parameter_mappable": 0
    }
  }
}
```

### VST~ with Plugin Pre-loaded
```json
{
  "box": {
    "id": "obj-serum",
    "maxclass": "newobj",
    "text": "vst~",
    "numinlets": 2,
    "numoutlets": 8,
    "outlettype": ["signal", "signal", "", "list", "", "", "", ""],
    "patching_rect": [50, 100, 200, 22],
    "saved_object_attributes": {
      "parameter_enable": 0,
      "prefer": "VST3"
    },
    "saved_state": {
      "pluginname": "Serum",
      "pluginpath": "C74_VST3:/Serum"
    }
  }
}
```

### VST~ Outlets Explained
| Outlet | Type | Purpose |
|--------|------|---------|
| 0 | signal | Left audio output |
| 1 | signal | Right audio output |
| 2 | list | Parameter names/info |
| 3 | list | Parameter values |
| 4 | list | MIDI events |
| 5 | list | Plugin info |
| 6 | list | Additional data |
| 7 | list | Additional data |

## 4. Patchcord Connection Format

### Structure Requirements
```json
{
  "patchline": {
    "destination": ["target_object_id", inlet_number],
    "source": ["source_object_id", outlet_number]
  }
}
```

### Numbering Convention: **0-BASED INDEXING**
```
Object inlets/outlets:  [0] [1] [2] [3] [4]
                         ↑   ↑   ↑   ↑   ↑
                      First Second Third etc.
```

### Example Connections
```json
// Button -> Message -> VST~
{
  "lines": [
    {
      "patchline": {
        "destination": ["obj-message", 0],  // Message inlet 0
        "source": ["obj-button", 0]        // Button outlet 0
      }
    },
    {
      "patchline": {
        "destination": ["obj-vst", 0],      // VST~ inlet 0 (control)
        "source": ["obj-message", 0]       // Message outlet 0
      }
    },
    {
      "patchline": {
        "destination": ["obj-print", 0],    // Print inlet 0
        "source": ["obj-vst", 2]           // VST~ outlet 2 (parameters)
      }
    }
  ]
}
```

## 5. Common Error Patterns

### "patchcord destination not found"
**Causes:**
1. Object ID doesn't exist in boxes array
2. Typo in object ID string
3. Wrong inlet/outlet number (exceeds object's actual inlets/outlets)

**Examples:**
```json
❌ BAD:
"boxes": [{"box": {"id": "obj-1", "maxclass": "button", "numoutlets": 1}}],
"lines": [{"patchline": {"source": ["obj-1", 5]}}]  // Button only has outlet 0!

❌ BAD:
"lines": [{"patchline": {"destination": ["obj-999", 0]}}]  // obj-999 doesn't exist

✅ GOOD:
"boxes": [{"box": {"id": "obj-1", "maxclass": "button", "numoutlets": 1}}],
"lines": [{"patchline": {"source": ["obj-1", 0]}}]  // Outlet 0 exists
```

### "no such object"
**Causes:**
1. Invalid maxclass name
2. Object not available in current Max version
3. Typo in maxclass

**Examples:**
```json
❌ BAD: "maxclass": "vst3~"     // Doesn't exist!
✅ GOOD: "maxclass": "newobj", "text": "vst~"

❌ BAD: "maxclass": "prin"      // Typo
✅ GOOD: "maxclass": "newobj", "text": "print"
```

## 6. Max for Live Automation Objects

### Automatable Object Structure
```json
{
  "box": {
    "id": "obj-dial1",
    "maxclass": "live.dial",
    "parameter_enable": 1,      // REQUIRED for automation
    "patching_rect": [50, 50, 44, 44],
    "saved_attribute_attributes": {
      "valueof": {
        "parameter_longname": "Cutoff",    // Shows in Live
        "parameter_shortname": "Cutoff",
        "parameter_type": 0,               // 0=float, 1=int, 2=enum
        "parameter_unitstyle": 1           // 0=int, 1=float, 5=Hz, etc.
      }
    },
    "varname": "cutoff_dial"    // For script access
  }
}
```

## 7. Complete Working Template

### Error-Free Basic VST Controller
```json
{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 8,
      "minor": 2,
      "revision": 0,
      "architecture": "x64"
    },
    "classnamespace": "box",
    "rect": [100, 100, 500, 400],
    "boxes": [
      {
        "box": {
          "id": "obj-1",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "patching_rect": [50, 50, 24, 24]
        }
      },
      {
        "box": {
          "id": "obj-2",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "text": "params",
          "patching_rect": [50, 90, 50, 22]
        }
      },
      {
        "box": {
          "id": "obj-3",
          "maxclass": "newobj",
          "text": "vst~",
          "numinlets": 2,
          "numoutlets": 8,
          "outlettype": ["signal", "signal", "", "list", "", "", "", ""],
          "patching_rect": [50, 130, 200, 22]
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "text": "print vst_params",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [150, 180, 100, 22]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "destination": ["obj-2", 0],
          "source": ["obj-1", 0]
        }
      },
      {
        "patchline": {
          "destination": ["obj-3", 0],
          "source": ["obj-2", 0]
        }
      },
      {
        "patchline": {
          "destination": ["obj-4", 0],
          "source": ["obj-3", 2]
        }
      }
    ]
  }
}
```

## 8. VST Parameter Control Implementation

### Using Official VST~ Documentation
Based on the official docs, here's the proper parameter control:

```json
// Parameter control messages (1-based indexing for parameters!)
{
  "box": {
    "id": "obj-param1",
    "maxclass": "message",
    "text": "1 0.5",     // Set parameter 1 to 50%
    "numinlets": 2,
    "numoutlets": 1,
    "patching_rect": [50, 200, 50, 22]
  }
}

// Connect to VST~ inlet 0
{
  "patchline": {
    "destination": ["obj-vst", 0],
    "source": ["obj-param1", 0]
  }
}
```

### Parameter Discovery Pattern
```
[button] → [params] → [vst~] → [print param_names]
           [get] ↗         ↘ [print param_values]
```

## 9. Implementation Checklist

**Before Creating .maxpat:**
- [ ] Plan all object IDs sequentially
- [ ] Verify all maxclass names are valid
- [ ] Count inlets/outlets for each object type
- [ ] Use only `vst~` (not `vst3~`)

**During JSON Creation:**
- [ ] Unique object IDs in boxes array
- [ ] All patchline references match existing object IDs
- [ ] 0-based indexing for inlet/outlet numbers
- [ ] Correct `numinlets`/`numoutlets` counts

**For VST Control:**
- [ ] Use 1-based parameter indexing (1, 2, 3...)
- [ ] Parameter values 0.0-1.0 range
- [ ] Connect VST~ outlet 2 for parameter info
- [ ] Use `params` and `get` messages for discovery

**For Max for Live:**
- [ ] Use `live.*` objects for automation
- [ ] Set `parameter_enable: 1` for automatable controls
- [ ] Provide `parameter_longname` for Live identification

This research eliminates the guesswork and provides definitive patterns for error-free Max patch creation.