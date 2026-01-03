# Ableton MCP Extensions for Multi-Agent Music Production

## Overview

This document outlines recommended extensions to the AbletonMCP_Extended Remote Script to support the three specialized agents (Additive, Subtractive, Transformative) in the multi-agent music production system.

**Current State:** The existing MCP implementation provides basic track, clip, device, and browser access.

**Goal:** Extend the MCP to expose the full capabilities available in Ableton's Live Object Model (LOM), plus integrate macOS Automator for operations not accessible via the API.

---

## Table of Contents

1. [Priority 1: Mixer Controls](#priority-1-mixer-controls)
2. [Priority 2: Audio Clip Properties](#priority-2-audio-clip-properties)
3. [Priority 3: Track Organization](#priority-3-track-organization)
4. [Priority 4: Device Chain Management](#priority-4-device-chain-management)
5. [Priority 5: Arrangement Editing](#priority-5-arrangement-editing)
6. [Priority 6: Master Track](#priority-6-master-track)
7. [API Limitations](#api-limitations)
8. [macOS Automator Integration](#macos-automator-integration)
9. [Agent Capability Matrix](#agent-capability-matrix)

---

## Priority 1: Mixer Controls

**Agent Impact:** Critical for Transformative (mixing) and Subtractive (gain staging) agents.

### Commands to Add

```python
# Add to _process_command in __init__.py

elif command_type == "set_track_volume":
    track_index = params.get("track_index", 0)
    volume = params.get("volume", 0.85)  # 0.0 to 1.0
    result = self._set_track_volume(track_index, volume)

elif command_type == "set_track_pan":
    track_index = params.get("track_index", 0)
    pan = params.get("pan", 0.0)  # -1.0 to 1.0
    result = self._set_track_pan(track_index, pan)

elif command_type == "set_send_level":
    track_index = params.get("track_index", 0)
    send_index = params.get("send_index", 0)
    level = params.get("level", 0.0)  # 0.0 to 1.0
    result = self._set_send_level(track_index, send_index, level)

elif command_type == "set_track_mute":
    track_index = params.get("track_index", 0)
    mute = params.get("mute", False)
    result = self._set_track_mute(track_index, mute)

elif command_type == "set_track_solo":
    track_index = params.get("track_index", 0)
    solo = params.get("solo", False)
    result = self._set_track_solo(track_index, solo)

elif command_type == "get_return_tracks":
    result = self._get_return_tracks()

elif command_type == "set_return_track_volume":
    return_index = params.get("return_index", 0)
    volume = params.get("volume", 0.85)
    result = self._set_return_track_volume(return_index, volume)
```

### Implementation

```python
def _set_track_volume(self, track_index, volume):
    """Set track volume (0.0 to 1.0)"""
    if track_index < 0 or track_index >= len(self._song.tracks):
        raise IndexError("Track index out of range")
    track = self._song.tracks[track_index]
    clamped = max(0.0, min(1.0, volume))
    track.mixer_device.volume.value = clamped
    return {
        "track_index": track_index,
        "volume": track.mixer_device.volume.value,
        "volume_db": self._value_to_db(track.mixer_device.volume.value)
    }

def _set_track_pan(self, track_index, pan):
    """Set track pan (-1.0 left to 1.0 right)"""
    if track_index < 0 or track_index >= len(self._song.tracks):
        raise IndexError("Track index out of range")
    track = self._song.tracks[track_index]
    clamped = max(-1.0, min(1.0, pan))
    track.mixer_device.panning.value = clamped
    return {
        "track_index": track_index,
        "pan": track.mixer_device.panning.value
    }

def _set_send_level(self, track_index, send_index, level):
    """Set send level to return track"""
    if track_index < 0 or track_index >= len(self._song.tracks):
        raise IndexError("Track index out of range")
    track = self._song.tracks[track_index]
    sends = track.mixer_device.sends
    if send_index < 0 or send_index >= len(sends):
        raise IndexError(f"Send index out of range. Track has {len(sends)} sends.")
    clamped = max(0.0, min(1.0, level))
    sends[send_index].value = clamped
    return {
        "track_index": track_index,
        "send_index": send_index,
        "level": sends[send_index].value
    }

def _set_track_mute(self, track_index, mute):
    """Set track mute state"""
    track = self._song.tracks[track_index]
    track.mute = mute
    return {"track_index": track_index, "mute": track.mute}

def _set_track_solo(self, track_index, solo):
    """Set track solo state"""
    track = self._song.tracks[track_index]
    track.solo = solo
    return {"track_index": track_index, "solo": track.solo}

def _get_return_tracks(self):
    """Get info about all return tracks"""
    returns = []
    for i, track in enumerate(self._song.return_tracks):
        returns.append({
            "index": i,
            "name": track.name,
            "volume": track.mixer_device.volume.value,
            "pan": track.mixer_device.panning.value,
            "mute": track.mute,
            "solo": track.solo,
            "devices": [{"name": d.name, "class": d.class_name} for d in track.devices]
        })
    return {"return_tracks": returns, "count": len(returns)}

def _set_return_track_volume(self, return_index, volume):
    """Set return track volume"""
    if return_index < 0 or return_index >= len(self._song.return_tracks):
        raise IndexError("Return track index out of range")
    track = self._song.return_tracks[return_index]
    clamped = max(0.0, min(1.0, volume))
    track.mixer_device.volume.value = clamped
    return {"return_index": return_index, "volume": track.mixer_device.volume.value}

def _value_to_db(self, value):
    """Convert 0-1 volume value to approximate dB"""
    import math
    if value <= 0:
        return "-inf"
    db = 20 * math.log10(value)
    return round(db, 1)
```

---

## Priority 2: Audio Clip Properties

**Agent Impact:** Critical for Subtractive (clip-level gain staging, cleanup) and Transformative (pitch manipulation).

### Commands to Add

```python
elif command_type == "get_audio_clip_properties":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    result = self._get_audio_clip_properties(track_index, clip_index)

elif command_type == "set_clip_gain":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    gain = params.get("gain", 1.0)  # 0.0 to 1.0
    result = self._set_clip_gain(track_index, clip_index, gain)

elif command_type == "set_clip_pitch":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    semitones = params.get("semitones", 0)  # -48 to 48
    cents = params.get("cents", 0)  # -50 to 49
    result = self._set_clip_pitch(track_index, clip_index, semitones, cents)

elif command_type == "set_clip_loop":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    loop_start = params.get("loop_start", None)
    loop_end = params.get("loop_end", None)
    looping = params.get("looping", None)
    result = self._set_clip_loop(track_index, clip_index, loop_start, loop_end, looping)

elif command_type == "set_clip_warp_mode":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    warp_mode = params.get("warp_mode", 0)
    result = self._set_clip_warp_mode(track_index, clip_index, warp_mode)

elif command_type == "get_clip_warp_markers":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    result = self._get_clip_warp_markers(track_index, clip_index)
```

### Implementation

```python
def _get_audio_clip_properties(self, track_index, clip_index):
    """Get comprehensive audio clip properties"""
    clip = self._get_arrangement_clip(track_index, clip_index)
    
    if not clip.is_audio_clip:
        raise ValueError("Not an audio clip")
    
    result = {
        "name": clip.name,
        "gain": clip.gain,
        "gain_display": clip.gain_display_string,
        "pitch_coarse": clip.pitch_coarse,
        "pitch_fine": clip.pitch_fine,
        "warping": clip.warping,
        "warp_mode": clip.warp_mode,
        "loop_start": clip.loop_start,
        "loop_end": clip.loop_end,
        "looping": clip.looping,
        "start_marker": clip.start_marker,
        "end_marker": clip.end_marker,
        "length": clip.length,
        "muted": clip.muted,
        "color_index": clip.color_index,
    }
    
    try:
        result["file_path"] = clip.file_path
    except:
        pass
    
    return result

def _set_clip_gain(self, track_index, clip_index, gain):
    """Set audio clip gain (0.0 to 1.0)"""
    clip = self._get_arrangement_clip(track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Not an audio clip")
    
    clamped = max(0.0, min(1.0, gain))
    clip.gain = clamped
    
    return {
        "gain": clip.gain,
        "gain_display": clip.gain_display_string
    }

def _set_clip_pitch(self, track_index, clip_index, semitones, cents):
    """Set audio clip pitch shift"""
    clip = self._get_arrangement_clip(track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Not an audio clip")
    
    semitones = max(-48, min(48, semitones))
    cents = max(-50, min(49, cents))
    
    clip.pitch_coarse = semitones
    clip.pitch_fine = cents
    
    return {
        "pitch_coarse": clip.pitch_coarse,
        "pitch_fine": clip.pitch_fine
    }

def _set_clip_loop(self, track_index, clip_index, loop_start, loop_end, looping):
    """Set clip loop parameters"""
    clip = self._get_arrangement_clip(track_index, clip_index)
    
    if looping is not None:
        clip.looping = looping
    if loop_start is not None:
        clip.loop_start = loop_start
    if loop_end is not None:
        clip.loop_end = loop_end
    
    return {
        "looping": clip.looping,
        "loop_start": clip.loop_start,
        "loop_end": clip.loop_end
    }

def _set_clip_warp_mode(self, track_index, clip_index, warp_mode):
    """Set audio clip warp mode
    0=Beats, 1=Tones, 2=Texture, 3=Re-Pitch, 4=Complex, 5=Complex Pro
    """
    clip = self._get_arrangement_clip(track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Not an audio clip")
    
    clip.warp_mode = warp_mode
    return {"warp_mode": clip.warp_mode}

def _get_clip_warp_markers(self, track_index, clip_index):
    """Get warp markers for audio clip (Live 11+)"""
    clip = self._get_arrangement_clip(track_index, clip_index)
    if not clip.is_audio_clip:
        raise ValueError("Not an audio clip")
    
    try:
        markers = clip.warp_markers
        return {"warp_markers": markers}
    except:
        return {"warp_markers": [], "note": "Requires Live 11+"}

def _get_arrangement_clip(self, track_index, clip_index):
    """Helper to get arrangement clip"""
    if track_index < 0 or track_index >= len(self._song.tracks):
        raise IndexError("Track index out of range")
    track = self._song.tracks[track_index]
    
    if not hasattr(track, 'arrangement_clips'):
        raise ValueError("Track has no arrangement clips")
    
    clips = list(track.arrangement_clips)
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError("Clip index out of range")
    
    return clips[clip_index]
```

---

## Priority 3: Track Organization

**Agent Impact:** Important for Subtractive (session prep, organization).

### Commands to Add

```python
elif command_type == "set_track_color":
    track_index = params.get("track_index", 0)
    color_index = params.get("color_index", 0)
    result = self._set_track_color(track_index, color_index)

elif command_type == "create_audio_track":
    index = params.get("index", -1)
    result = self._create_audio_track(index)

elif command_type == "delete_track":
    track_index = params.get("track_index", 0)
    result = self._delete_track(track_index)

elif command_type == "create_return_track":
    result = self._create_return_track()

elif command_type == "get_track_routing":
    track_index = params.get("track_index", 0)
    result = self._get_track_routing(track_index)

elif command_type == "fold_track":
    track_index = params.get("track_index", 0)
    fold = params.get("fold", True)
    result = self._fold_track(track_index, fold)
```

### Implementation

```python
def _set_track_color(self, track_index, color_index):
    """Set track color by index"""
    track = self._song.tracks[track_index]
    track.color_index = color_index
    return {"color_index": track.color_index}

def _create_audio_track(self, index):
    """Create a new audio track"""
    self._song.create_audio_track(index)
    new_index = len(self._song.tracks) - 1 if index == -1 else index
    return {"index": new_index, "name": self._song.tracks[new_index].name}

def _delete_track(self, track_index):
    """Delete a track"""
    if track_index < 0 or track_index >= len(self._song.tracks):
        raise IndexError("Track index out of range")
    self._song.delete_track(track_index)
    return {"deleted": True, "track_index": track_index}

def _create_return_track(self):
    """Create a new return track"""
    self._song.create_return_track()
    new_index = len(self._song.return_tracks) - 1
    return {"index": new_index, "name": self._song.return_tracks[new_index].name}

def _get_track_routing(self, track_index):
    """Get track input/output routing info"""
    track = self._song.tracks[track_index]
    return {
        "input_routing_type": str(track.input_routing_type.display_name) 
            if hasattr(track.input_routing_type, 'display_name') else None,
        "output_routing_type": str(track.output_routing_type.display_name) 
            if hasattr(track.output_routing_type, 'display_name') else None,
    }

def _fold_track(self, track_index, fold):
    """Fold/unfold a group track"""
    track = self._song.tracks[track_index]
    if hasattr(track, 'fold_state'):
        track.fold_state = 1 if fold else 0
        return {"fold_state": track.fold_state}
    else:
        raise ValueError("Track is not a group track")
```

---

## Priority 4: Device Chain Management

**Agent Impact:** Important for Transformative (effect chain manipulation).

### Commands to Add

```python
elif command_type == "delete_device":
    track_index = params.get("track_index", 0)
    device_index = params.get("device_index", 0)
    result = self._delete_device(track_index, device_index)

elif command_type == "set_device_enabled":
    track_index = params.get("track_index", 0)
    device_index = params.get("device_index", 0)
    enabled = params.get("enabled", True)
    result = self._set_device_enabled(track_index, device_index, enabled)

elif command_type == "set_device_parameter_by_name":
    track_index = params.get("track_index", 0)
    device_index = params.get("device_index", 0)
    param_name = params.get("param_name", "")
    value = params.get("value", 0.0)
    result = self._set_device_parameter_by_name(track_index, device_index, param_name, value)
```

### Implementation

```python
def _delete_device(self, track_index, device_index):
    """Delete a device from track"""
    track = self._song.tracks[track_index]
    if device_index < 0 or device_index >= len(track.devices):
        raise IndexError("Device index out of range")
    device_name = track.devices[device_index].name
    track.delete_device(device_index)
    return {"deleted": device_name}

def _set_device_enabled(self, track_index, device_index, enabled):
    """Enable/disable a device"""
    track = self._song.tracks[track_index]
    device = track.devices[device_index]
    for param in device.parameters:
        if param.name == "Device On":
            param.value = 1.0 if enabled else 0.0
            return {"enabled": param.value == 1.0}
    raise ValueError("Device does not have on/off control")

def _set_device_parameter_by_name(self, track_index, device_index, param_name, value):
    """Set device parameter by name (fuzzy match)"""
    track = self._song.tracks[track_index]
    device = track.devices[device_index]
    
    param_name_lower = param_name.lower()
    
    # Try exact match first
    for param in device.parameters:
        if param.name.lower() == param_name_lower:
            clamped = max(param.min, min(param.max, value))
            param.value = clamped
            return {
                "parameter_name": param.name,
                "value": param.value,
                "min": param.min,
                "max": param.max
            }
    
    # Try partial match
    for param in device.parameters:
        if param_name_lower in param.name.lower():
            clamped = max(param.min, min(param.max, value))
            param.value = clamped
            return {
                "parameter_name": param.name,
                "value": param.value,
                "min": param.min,
                "max": param.max,
                "note": "Partial match"
            }
    
    raise ValueError(f"Parameter '{param_name}' not found on device '{device.name}'")
```

---

## Priority 5: Arrangement Editing

**Agent Impact:** Important for Subtractive (clip organization).

### Commands to Add

```python
elif command_type == "set_clip_mute":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    muted = params.get("muted", True)
    result = self._set_clip_mute(track_index, clip_index, muted)

elif command_type == "set_clip_start_end":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    start_marker = params.get("start_marker", None)
    end_marker = params.get("end_marker", None)
    result = self._set_clip_start_end(track_index, clip_index, start_marker, end_marker)

elif command_type == "set_clip_color":
    track_index = params.get("track_index", 0)
    clip_index = params.get("clip_index", 0)
    color_index = params.get("color_index", 0)
    result = self._set_clip_color(track_index, clip_index, color_index)
```

### Implementation

```python
def _set_clip_mute(self, track_index, clip_index, muted):
    """Mute/unmute a clip"""
    clip = self._get_arrangement_clip(track_index, clip_index)
    clip.muted = muted
    return {"muted": clip.muted}

def _set_clip_start_end(self, track_index, clip_index, start_marker, end_marker):
    """Set clip start/end markers"""
    clip = self._get_arrangement_clip(track_index, clip_index)
    if start_marker is not None:
        clip.start_marker = start_marker
    if end_marker is not None:
        clip.end_marker = end_marker
    return {
        "start_marker": clip.start_marker,
        "end_marker": clip.end_marker
    }

def _set_clip_color(self, track_index, clip_index, color_index):
    """Set clip color"""
    clip = self._get_arrangement_clip(track_index, clip_index)
    clip.color_index = color_index
    return {"color_index": clip.color_index}
```

---

## Priority 6: Master Track

**Agent Impact:** Important for Transformative (mastering chain).

### Commands to Add

```python
elif command_type == "get_master_track":
    result = self._get_master_track()

elif command_type == "set_master_volume":
    volume = params.get("volume", 0.85)
    result = self._set_master_volume(volume)

elif command_type == "get_master_device_parameters":
    device_index = params.get("device_index", 0)
    result = self._get_master_device_parameters(device_index)

elif command_type == "set_master_device_parameter":
    device_index = params.get("device_index", 0)
    parameter_index = params.get("parameter_index", 0)
    value = params.get("value", 0.0)
    result = self._set_master_device_parameter(device_index, parameter_index, value)
```

### Implementation

```python
def _get_master_track(self):
    """Get master track info"""
    master = self._song.master_track
    devices = []
    for i, device in enumerate(master.devices):
        devices.append({
            "index": i,
            "name": device.name,
            "class_name": device.class_name
        })
    
    return {
        "volume": master.mixer_device.volume.value,
        "pan": master.mixer_device.panning.value,
        "devices": devices,
        "device_count": len(devices)
    }

def _set_master_volume(self, volume):
    """Set master track volume"""
    master = self._song.master_track
    clamped = max(0.0, min(1.0, volume))
    master.mixer_device.volume.value = clamped
    return {"volume": master.mixer_device.volume.value}

def _get_master_device_parameters(self, device_index):
    """Get parameters for a device on master track"""
    master = self._song.master_track
    if device_index >= len(master.devices):
        raise IndexError("Device index out of range")
    device = master.devices[device_index]
    
    parameters = []
    for i, param in enumerate(device.parameters):
        parameters.append({
            "index": i,
            "name": param.name,
            "value": param.value,
            "min": param.min,
            "max": param.max
        })
    
    return {
        "device_name": device.name,
        "parameters": parameters
    }

def _set_master_device_parameter(self, device_index, parameter_index, value):
    """Set a parameter on a master track device"""
    master = self._song.master_track
    device = master.devices[device_index]
    param = device.parameters[parameter_index]
    clamped = max(param.min, min(param.max, value))
    param.value = clamped
    return {
        "device_name": device.name,
        "parameter_name": param.name,
        "value": param.value
    }
```

---

## API Limitations

The following operations are **NOT accessible** via the Live Object Model API:

| Operation | API Status | Workaround |
|-----------|------------|------------|
| Split clip at position | ❌ Not available | Use Automator (Cmd+E) |
| Consolidate clips | ❌ Not available | Use Automator (Cmd+J) |
| Apply fades to arrangement clips | ❌ Limited | Envelope-based |
| Move clips in arrangement | ❌ Not available | Delete and recreate |
| Crop audio clips | ❌ Not available | Agent recommends, human executes |
| Track reordering | ❌ Not available | Duplicate/delete workaround |
| Group tracks | ⚠️ Create only | `create_group_track()` exists |
| Bounce/render | ❌ Not available | Use Automator (Cmd+Shift+R) |
| Real-time audio analysis | ❌ Not available | Requires Max for Live |
| Undo/Redo | ❌ Not available | Use Automator (Cmd+Z) |

---

## macOS Automator Integration

For operations not available via the Live API, we can use macOS Automator/AppleScript to simulate keyboard shortcuts and menu commands.

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LLM Agent     │────▶│  Python MCP     │────▶│  Live API       │
│                 │     │  Client         │     │  (Remote Script)│
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         │                       │ For unsupported ops
         │                       ▼
         │              ┌─────────────────┐     ┌─────────────────┐
         │              │  osascript      │────▶│  System Events  │
         │              │  subprocess     │     │  (keystrokes)   │
         └──────────────┴─────────────────┘     └─────────────────┘
```

### Python AppleScript Execution Module

Create `automator_bridge.py`:

```python
"""
automator_bridge.py
Bridge to execute Ableton operations via macOS AppleScript/Automator
"""

import subprocess
import time
from typing import Optional, Tuple, List

class AbletonAutomatorBridge:
    """Execute Ableton operations via AppleScript System Events"""
    
    ABLETON_APP_NAME = "Ableton Live 12 Suite"  # Adjust for your version
    
    # Key codes for special keys
    KEY_CODES = {
        "return": 36,
        "tab": 48,
        "space": 49,
        "delete": 51,
        "escape": 53,
        "left": 123,
        "right": 124,
        "down": 125,
        "up": 126,
    }
    
    def __init__(self):
        self.last_error = None
    
    def _run_applescript(self, script: str) -> Tuple[int, str, str]:
        """Execute AppleScript and return (returncode, stdout, stderr)"""
        result = subprocess.run(
            ['/usr/bin/osascript', '-e', script],
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    
    def _run_applescript_multiline(self, script: str) -> Tuple[int, str, str]:
        """Execute multi-line AppleScript"""
        result = subprocess.run(
            ['/usr/bin/osascript', '-'],
            input=script,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    
    def activate_ableton(self) -> bool:
        """Bring Ableton to foreground"""
        script = f'tell application "{self.ABLETON_APP_NAME}" to activate'
        code, out, err = self._run_applescript(script)
        if code != 0:
            self.last_error = err
            return False
        time.sleep(0.3)
        return True
    
    def send_keystroke(self, key: str, modifiers: List[str] = None) -> bool:
        """Send a keystroke to Ableton
        
        Args:
            key: Single character or key name ('return', 'tab', etc.)
            modifiers: List of modifiers ['command', 'shift', 'option', 'control']
        """
        if not self.activate_ableton():
            return False
        
        modifiers = modifiers or []
        modifier_str = ""
        if modifiers:
            mod_map = {
                'command': 'command down',
                'shift': 'shift down',
                'option': 'option down',
                'control': 'control down',
                'cmd': 'command down',
                'alt': 'option down',
                'ctrl': 'control down'
            }
            mods = [mod_map.get(m.lower(), m) for m in modifiers]
            modifier_str = f" using {{{', '.join(mods)}}}"
        
        # Check if it's a special key
        if key.lower() in self.KEY_CODES:
            script = f'''
            tell application "System Events"
                tell process "{self.ABLETON_APP_NAME}"
                    key code {self.KEY_CODES[key.lower()]}{modifier_str}
                end tell
            end tell
            '''
        else:
            script = f'''
            tell application "System Events"
                tell process "{self.ABLETON_APP_NAME}"
                    keystroke "{key}"{modifier_str}
                end tell
            end tell
            '''
        
        code, out, err = self._run_applescript_multiline(script)
        if code != 0:
            self.last_error = err
            return False
        return True
    
    def click_menu(self, menu_path: List[str]) -> bool:
        """Click a menu item by path
        
        Args:
            menu_path: List like ["Edit", "Split"] or ["Edit", "Consolidate Time"]
        """
        if not self.activate_ableton():
            return False
        
        if len(menu_path) < 2:
            self.last_error = "Menu path must have at least 2 elements"
            return False
        
        menu_bar = menu_path[0]
        menu_item = menu_path[1]
        
        script = f'''
        tell application "System Events"
            tell process "{self.ABLETON_APP_NAME}"
                click menu item "{menu_item}" of menu 1 of menu bar item "{menu_bar}" of menu bar 1
            end tell
        end tell
        '''
        
        code, out, err = self._run_applescript_multiline(script)
        if code != 0:
            self.last_error = err
            return False
        return True
    
    # =========================================================================
    # HIGH-LEVEL ABLETON OPERATIONS
    # =========================================================================
    
    def split_clip(self) -> bool:
        """Split clip at current position (Cmd+E)"""
        return self.send_keystroke("e", ["command"])
    
    def consolidate(self) -> bool:
        """Consolidate selected clips/time range (Cmd+J)"""
        return self.send_keystroke("j", ["command"])
    
    def duplicate(self) -> bool:
        """Duplicate selection (Cmd+D)"""
        return self.send_keystroke("d", ["command"])
    
    def undo(self) -> bool:
        """Undo (Cmd+Z)"""
        return self.send_keystroke("z", ["command"])
    
    def redo(self) -> bool:
        """Redo (Cmd+Shift+Z)"""
        return self.send_keystroke("z", ["command", "shift"])
    
    def select_all(self) -> bool:
        """Select all (Cmd+A)"""
        return self.send_keystroke("a", ["command"])
    
    def copy(self) -> bool:
        """Copy (Cmd+C)"""
        return self.send_keystroke("c", ["command"])
    
    def paste(self) -> bool:
        """Paste (Cmd+V)"""
        return self.send_keystroke("v", ["command"])
    
    def cut(self) -> bool:
        """Cut (Cmd+X)"""
        return self.send_keystroke("x", ["command"])
    
    def delete_selection(self) -> bool:
        """Delete selection"""
        return self.send_keystroke("delete")
    
    def save(self) -> bool:
        """Save (Cmd+S)"""
        return self.send_keystroke("s", ["command"])
    
    def export_audio(self) -> bool:
        """Open Export Audio dialog (Cmd+Shift+R)"""
        return self.send_keystroke("r", ["command", "shift"])
    
    def toggle_loop(self) -> bool:
        """Toggle loop (Cmd+L)"""
        return self.send_keystroke("l", ["command"])
    
    def zoom_to_selection(self) -> bool:
        """Zoom to selection (Z)"""
        return self.send_keystroke("z")
    
    def toggle_automation_mode(self) -> bool:
        """Toggle automation mode (A)"""
        return self.send_keystroke("a")
    
    def toggle_draw_mode(self) -> bool:
        """Toggle draw mode (B)"""
        return self.send_keystroke("b")
    
    def quantize(self) -> bool:
        """Quantize selection (Cmd+U)"""
        return self.send_keystroke("u", ["command"])
    
    def group_tracks(self) -> bool:
        """Group selected tracks (Cmd+G)"""
        return self.send_keystroke("g", ["command"])
    
    def freeze_track(self) -> bool:
        """Freeze track - requires menu"""
        return self.click_menu(["Edit", "Freeze Track"])
    
    def flatten_track(self) -> bool:
        """Flatten track - requires menu"""
        return self.click_menu(["Edit", "Flatten"])
    
    def reverse_clip(self) -> bool:
        """Reverse clip - requires menu"""
        return self.click_menu(["Edit", "Reverse"])
    
    def navigate(self, direction: str) -> bool:
        """Navigate in given direction"""
        return self.send_keystroke(direction)
    
    def wait_for_dialog(self, dialog_title: str, timeout: float = 10.0) -> bool:
        """Wait for a dialog window to appear"""
        start = time.time()
        while time.time() - start < timeout:
            script = f'''
            tell application "System Events"
                tell process "{self.ABLETON_APP_NAME}"
                    return exists window "{dialog_title}"
                end tell
            end tell
            '''
            code, out, err = self._run_applescript_multiline(script)
            if code == 0 and out.lower() == "true":
                return True
            time.sleep(0.2)
        return False
    
    def click_dialog_button(self, button_name: str) -> bool:
        """Click a button in the frontmost dialog"""
        script = f'''
        tell application "System Events"
            tell process "{self.ABLETON_APP_NAME}"
                click button "{button_name}" of front window
            end tell
        end tell
        '''
        code, out, err = self._run_applescript_multiline(script)
        if code != 0:
            self.last_error = err
            return False
        return True


# Convenience function
def ableton_keystroke(key: str, modifiers: list = None) -> bool:
    """Quick helper to send a keystroke to Ableton"""
    bridge = AbletonAutomatorBridge()
    return bridge.send_keystroke(key, modifiers)
```

### Usage Examples

```python
from automator_bridge import AbletonAutomatorBridge

bridge = AbletonAutomatorBridge()

# Split clip at current position
bridge.split_clip()

# Consolidate selection
bridge.consolidate()

# Export audio (opens dialog)
bridge.export_audio()

# Wait for export dialog and click OK
if bridge.wait_for_dialog("Export Audio/Video", timeout=5.0):
    bridge.click_dialog_button("OK")

# Freeze and flatten a track
bridge.freeze_track()
time.sleep(2)  # Wait for freeze to complete
bridge.flatten_track()

# Custom keystroke sequence
bridge.send_keystroke("a", ["command"])  # Select all
bridge.send_keystroke("j", ["command"])  # Consolidate
```

### MCP Extension for Automator Commands

Add to MCP `_process_command`:

```python
elif command_type == "automator_split":
    result = self._automator_split()

elif command_type == "automator_consolidate":
    result = self._automator_consolidate()

elif command_type == "automator_keystroke":
    key = params.get("key", "")
    modifiers = params.get("modifiers", [])
    result = self._automator_keystroke(key, modifiers)

elif command_type == "automator_undo":
    result = self._automator_undo()

elif command_type == "automator_export":
    result = self._automator_export()
```

Implementation:

```python
import subprocess

def _run_osascript(self, script):
    """Run AppleScript via osascript"""
    result = subprocess.run(
        ['/usr/bin/osascript', '-'],
        input=script,
        capture_output=True,
        text=True
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if result.returncode != 0 else None
    }

def _automator_keystroke(self, key, modifiers):
    """Send keystroke via System Events"""
    app_name = "Ableton Live 12 Suite"
    
    modifier_str = ""
    if modifiers:
        mod_map = {
            'command': 'command down',
            'shift': 'shift down', 
            'option': 'option down',
            'control': 'control down'
        }
        mods = [mod_map.get(m.lower(), m) for m in modifiers]
        modifier_str = f" using {{{', '.join(mods)}}}"
    
    script = f'''
    tell application "{app_name}" to activate
    delay 0.2
    tell application "System Events"
        tell process "{app_name}"
            keystroke "{key}"{modifier_str}
        end tell
    end tell
    '''
    return self._run_osascript(script)

def _automator_split(self):
    """Split clip at current position"""
    return self._automator_keystroke("e", ["command"])

def _automator_consolidate(self):
    """Consolidate selection"""
    return self._automator_keystroke("j", ["command"])

def _automator_undo(self):
    """Undo last action"""
    return self._automator_keystroke("z", ["command"])

def _automator_export(self):
    """Open export dialog"""
    return self._automator_keystroke("r", ["command", "shift"])
```

### Security & Permissions

For Automator/AppleScript to work:

1. **System Preferences → Security & Privacy → Privacy → Accessibility**
   - Add Terminal.app (for testing)
   - Add your Python environment
   - Add any app running the MCP client

2. **System Preferences → Security & Privacy → Privacy → Automation**
   - Allow your app to control "System Events"
   - Allow your app to control "Ableton Live"

### Caveats & Best Practices

| Issue | Mitigation |
|-------|------------|
| **Timing** | Add delays between operations (0.2-0.5s) |
| **Focus** | Always call `activate_ableton()` first |
| **State** | Cannot verify GUI state; assume success |
| **Reliability** | Build retry logic (3 attempts) |
| **User interruption** | Warn user not to switch apps |

### Retry Wrapper

```python
def with_retry(func, max_attempts=3, delay=0.5):
    """Retry an automator function on failure"""
    for attempt in range(max_attempts):
        if func():
            return True
        time.sleep(delay)
    return False

# Usage
with_retry(bridge.split_clip)
```

---

## Agent Capability Matrix

After implementing all extensions:

| Capability | Additive | Subtractive | Transformative |
|------------|----------|-------------|----------------|
| **Create MIDI content** | ✅ Full | — | — |
| **Load instruments/presets** | ✅ Full | — | ✅ Full |
| **Set device parameters** | ✅ Full | ✅ Full | ✅ Full |
| **Track volume/pan** | ✅ P1 | ✅ P1 | ✅ P1 |
| **Send levels** | — | — | ✅ P1 |
| **Clip gain** | — | ✅ P2 | ✅ P2 |
| **Clip pitch** | — | — | ✅ P2 |
| **Track mute/solo** | — | ✅ P1 | ✅ P1 |
| **Track naming/color** | — | ✅ P3 | — |
| **Clip mute** | — | ✅ P5 | — |
| **Master track control** | — | — | ✅ P6 |
| **Split clips** | — | ⚠️ Automator | — |
| **Consolidate clips** | — | ⚠️ Automator | — |
| **Real-time spectrum** | ❌ | ❌ | ❌ (needs M4L) |

**Legend:**
- ✅ Full: Native API support
- ✅ Pn: Available after implementing Priority n
- ⚠️ Automator: Available via GUI automation
- ❌: Not possible

---

## Implementation Checklist

### Phase 1: Core API Extensions
- [ ] Implement Priority 1 (Mixer Controls)
- [ ] Implement Priority 2 (Audio Clip Properties)
- [ ] Test with all three agents

### Phase 2: Organization & Chain
- [ ] Implement Priority 3 (Track Organization)
- [ ] Implement Priority 4 (Device Chain Management)
- [ ] Implement Priority 6 (Master Track)

### Phase 3: Automator Bridge
- [ ] Create `automator_bridge.py`
- [ ] Configure macOS permissions
- [ ] Implement MCP commands for automator operations
- [ ] Build timing/retry logic

### Phase 4: Integration
- [ ] Add formal tool schemas for each agent's action space
- [ ] Update reward functions to account for new capabilities
- [ ] Create training data templates using new operations

---

## References

- [Live Object Model Documentation](https://docs.cycling74.com/legacy/max8/vignettes/live_object_model)
- [Ableton Keyboard Shortcuts](https://www.ableton.com/en/manual/live-keyboard-shortcuts/)
- [AppleScript Language Guide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/)
- [osascript Python Package](https://pypi.org/project/osascript/)
