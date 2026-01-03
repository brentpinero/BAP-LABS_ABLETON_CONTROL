# Ableton MCP Functionality Audit

## Current Status: 54 MCP Commands + 27 Automator Commands

---

## What We Have

### MCP Commands (via Remote Script API)

| Category | Commands |
|----------|----------|
| **Session** | get_session_info, get_session_summary, set_tempo, start_playback, stop_playback |
| **Tracks** | create_midi_track, create_audio_track, delete_track, create_return_track, get_track_info, get_track_routing, set_track_name, set_track_color, fold_track |
| **Mixer** | set_track_volume, set_track_pan, set_send_level, set_track_mute, set_track_solo, get_return_tracks, set_return_track_volume |
| **Session Clips** | create_clip, add_notes_to_clip, set_clip_name, fire_clip, stop_clip |
| **Arrangement Clips** | create_arrangement_clip, add_notes_to_arrangement_clip, duplicate_clip_to_arrangement, get_arrangement_clips, get_arrangement_clip_notes |
| **Audio Clip Properties** | get_audio_clip_properties, set_clip_gain, set_clip_pitch, set_clip_loop, set_clip_warp_mode, get_clip_warp_markers |
| **Clip Editing** | set_clip_mute, set_clip_start_end, set_clip_color |
| **Devices** | get_device_parameters, set_device_parameter, set_device_parameter_by_name, set_device_enabled, delete_device |
| **Master** | get_master_track, set_master_volume, get_master_device_parameters, set_master_device_parameter |
| **Browser** | get_browser_tree, get_browser_items_at_path, get_all_presets, load_browser_item |
| **Transport** | get_current_position, set_current_position |
| **Selection** | select_track, select_clip |

### Automator Commands (via AppleScript/GUI)

| Category | Commands |
|----------|----------|
| **Editing** | split_clip (Cmd+E), consolidate (Cmd+J), duplicate (Cmd+D), quantize (Cmd+U) |
| **Clipboard** | copy, paste, cut, delete_selection, select_all |
| **Undo/Redo** | undo (Cmd+Z), redo (Cmd+Shift+Z) |
| **File** | save (Cmd+S), export_audio (Cmd+Shift+R) |
| **Track Organization** | group_tracks (Cmd+G), ungroup_tracks (Cmd+Shift+G), move_track_up (Cmd+Up), move_track_down (Cmd+Down), select_tracks_range*, select_track_click* |
| **Track Processing** | freeze_track, flatten_track, reverse_clip |
| **View Toggles** | toggle_loop (Cmd+L), toggle_automation_mode, toggle_draw_mode |
| **Navigation** | navigate (arrow keys) |

---

## GAPS - Missing for Real-Time Producer Workflow

### Priority 1: Critical for Basic Workflow

#### 1. Transport & Navigation
```
IMPLEMENTED:
- get_current_position() → {position, is_playing, tempo}  # Where is the playhead?
- set_current_position(position: float)                   # Move playhead

STILL MISSING:
- get_loop_brace() → {start, end}            # Loop region
- set_loop_brace(start, end)                 # Set loop region
```
**Status:** Core transport implemented. Loop brace still needed for "loop bars 17-24".

#### 2. Track Selection & Arming
```
IMPLEMENTED:
- select_track(track_index)                  # Focus a track
- select_clip(track_index, clip_index)       # Select arrangement clip

STILL MISSING:
- arm_track(track_index, armed: bool)        # Arm for recording
- get_track_arm_state(track_index) → bool    # Check arm state
```
**Status:** Selection implemented. Arming still needed for "record on track 3".

#### 3. Clip Movement
```
MISSING:
- move_clip(track_index, clip_index, new_start_time)  # Reposition clip
- duplicate_clip_in_place(track_index, clip_index)    # Clone at same position
```
**Why needed:** Producer says "move that clip to bar 9" or "double that section"

### Priority 2: Enhanced Workflow

#### 4. Scenes (Session View)
```
MISSING:
- get_scenes() → list                        # List all scenes
- fire_scene(scene_index)                    # Trigger entire row
- stop_all_clips()                           # Global stop
- create_scene(index)                        # Add new scene
```
**Why needed:** Live performance, idea sketching, launching song sections

#### 5. Markers/Locators
```
MISSING:
- get_markers() → list                       # List all cue points
- add_marker(position, name)                 # Create marker
- delete_marker(marker_index)                # Remove marker
- jump_to_marker(marker_index)               # Navigate to marker
```
**Why needed:** Producer says "mark the chorus" or "jump to verse 2"

#### 6. MIDI Note Manipulation
```
MISSING:
- delete_notes(track, clip, start, end, pitch_range)  # Remove notes
- transpose_clip(track, clip, semitones)              # Pitch shift
- move_notes(track, clip, time_offset, pitch_offset)  # Shift notes
```
**Why needed:** Producer says "delete the wrong notes" or "move melody up an octave"

### Priority 3: Advanced Features

#### 7. Time Signature
```
MISSING:
- get_time_signature() → {numerator, denominator}
- set_time_signature(num, denom)
```
**Why needed:** Polyrhythmic sections, odd meters

#### 8. Recording
```
MISSING:
- start_recording()                          # Begin recording (vs playback)
- set_overdub(enabled: bool)                 # Layering mode
- get_record_state() → bool                  # Is recording?
```
**Why needed:** "Record a new take" or "overdub more drums"

#### 9. Automation
```
MISSING:
- get_automation_points(track, device, param) → list
- add_automation_point(track, device, param, time, value)
- delete_automation(track, device, param, start, end)
```
**Why needed:** "Automate the filter" or "copy that automation"

#### 10. Clip Selection
```
MISSING:
- select_clip(track_index, clip_index)       # Select specific clip
- select_time_range(start_beats, end_beats)  # Select region
- get_selected_clips() → list                # What's selected?
```
**Why needed:** Operations that require selection (split, consolidate, etc.)

---

## Test Coverage Gaps

### Missing Tests for Existing Commands

1. **Clip Movement Tests:**
   - `set_clip_start_end` - Currently skipped as "can disrupt timing"
   - `duplicate_clip_to_arrangement` - Not tested

2. **MIDI Note Tests:**
   - `get_arrangement_clip_notes` - Not tested
   - `add_notes_to_arrangement_clip` - Tested in integration only

3. **Browser/Loading:**
   - `load_browser_item` to master track - Not possible via MCP

---

## Implementation Recommendations

### Quick Wins (Can Add Now)

1. **Transport** - Live Object Model has:
   - `song.current_song_time` (read/write)
   - `song.loop_start`, `song.loop_length`
   - `song.is_playing`, `song.record_mode`

2. **Track Arming** - Live Object Model has:
   - `track.arm` (read/write)
   - `track.can_be_armed` (read-only)

3. **Scene Firing** - Live Object Model has:
   - `song.scenes[i].fire()`
   - `song.stop_all_clips()`

### Requires Automator (No API)

1. **Selection** - Must use keyboard/mouse automation
2. **Some menu commands** - Already using click_menu()

### May Not Be Possible

1. **Automation points** - Limited API access
2. **Detailed MIDI editing** - API is limited

---

## Vision-Based Workflow (TODO)

### The Problem

Click-based track selection (`select_tracks_range`, `select_track_click`) uses hardcoded pixel coordinates which are **brittle** because:
- Track heights vary based on zoom level
- Mixer position changes based on window layout
- Group folders expand/collapse, shifting positions
- Window size/position affects all coordinates

### The Solution: Screenshot → Vision → Action

A robust workflow would use vision analysis:

```
1. Take screenshot of Ableton
2. Send to Claude/Vision model: "Find track headers for tracks X and Y, return click coordinates"
3. Parse response for precise {x, y} coordinates
4. Execute clicks at those coordinates
5. Verify with another screenshot if needed
```

### Implementation Notes

- `automator_bridge.py` already has `get_window_position()` and `click_at_position()`
- Need to add `take_screenshot()` that returns image data
- Vision analysis can identify:
  - Track header positions (name labels)
  - Mixer section boundaries
  - Currently selected tracks (highlight color)
  - Group folder expand/collapse state

### Current State

| Command | Status |
|---------|--------|
| `automator_group` | ✅ Works (Cmd+G) - requires tracks pre-selected |
| `automator_ungroup` | ✅ Works (Cmd+Shift+G) |
| `automator_move_track_up` | ✅ Works (Cmd+Up) - single track |
| `automator_move_track_down` | ✅ Works (Cmd+Down) - single track |
| `select_tracks_range` | ⚠️ Functional but brittle (needs vision) |
| `select_track_click` | ⚠️ Functional but brittle (needs vision) |

---

## Next Steps

1. ~~Add Priority 1 commands (transport, arming, clip movement)~~ ✅ Done (transport, selection)
2. **Implement vision-based click targeting** for reliable multi-track selection
3. Add scene-related commands
4. Add marker commands
5. Add track arming commands
6. Expand test coverage for existing commands
