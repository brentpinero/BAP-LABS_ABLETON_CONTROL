"""
automator_bridge.py
Bridge to execute Ableton operations via macOS AppleScript/System Events

For operations not available via the Live Object Model API:
- Split clip at position (Cmd+E)
- Consolidate clips (Cmd+J)
- Undo/Redo (Cmd+Z, Cmd+Shift+Z)
- Export audio (Cmd+Shift+R)
- Freeze/Flatten/Reverse track (menu commands)

Usage:
    from automator_bridge import AbletonAutomatorBridge
    bridge = AbletonAutomatorBridge()
    bridge.split_clip()
    bridge.consolidate()
    bridge.undo()

Security Note:
    Requires macOS Accessibility permissions for the Python environment.
    System Preferences > Security & Privacy > Privacy > Accessibility
"""

import subprocess
import time
from typing import List, Tuple, Optional, Dict, Any


class AbletonAutomatorBridge:
    """Execute Ableton operations via AppleScript System Events"""

    ABLETON_APP_NAME = "Ableton Live 12 Suite"  # App name for activation
    ABLETON_PROCESS_NAME = "Live"  # Process name for System Events
    MAX_RETRIES = 3
    RETRY_DELAY = 0.5
    ACTIVATION_DELAY = 0.3

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

    def __init__(self, app_name: str = None):
        """Initialize the automator bridge.

        Args:
            app_name: Override the default Ableton app name (e.g., "Ableton Live 11 Suite")
        """
        if app_name:
            self.ABLETON_APP_NAME = app_name
        self.last_error: Optional[str] = None

    def _run_applescript(self, script: str) -> Tuple[int, str, str]:
        """Execute AppleScript and return (returncode, stdout, stderr)"""
        result = subprocess.run(
            ['/usr/bin/osascript', '-'],
            input=script,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def _with_retry(self, func, max_attempts: int = None) -> bool:
        """Retry wrapper for automator functions"""
        attempts = max_attempts or self.MAX_RETRIES
        for attempt in range(attempts):
            if func():
                return True
            time.sleep(self.RETRY_DELAY)
        return False

    def activate_ableton(self) -> bool:
        """Bring Ableton to foreground"""
        script = f'tell application "{self.ABLETON_APP_NAME}" to activate'
        code, _, err = self._run_applescript(script)
        if code != 0:
            self.last_error = err
            return False
        time.sleep(self.ACTIVATION_DELAY)
        return True

    def send_keystroke(self, key: str, modifiers: List[str] = None) -> bool:
        """Send a keystroke to Ableton with optional modifiers.

        Args:
            key: Single character or key name ('return', 'tab', 'space', 'delete', 'escape', arrows)
            modifiers: List of modifiers ['command', 'shift', 'option', 'control']
                      Aliases: 'cmd'='command', 'alt'='option', 'ctrl'='control'

        Returns:
            True if keystroke was sent successfully
        """
        if not self.activate_ableton():
            return False

        modifiers = modifiers or []
        modifier_str = ""
        if modifiers:
            mod_map = {
                'command': 'command down',
                'cmd': 'command down',
                'shift': 'shift down',
                'option': 'option down',
                'alt': 'option down',
                'control': 'control down',
                'ctrl': 'control down'
            }
            mods = [mod_map.get(m.lower(), m) for m in modifiers]
            modifier_str = f" using {{{', '.join(mods)}}}"

        # Check if it's a special key
        if key.lower() in self.KEY_CODES:
            script = f'''
            tell application "System Events"
                tell process "{self.ABLETON_PROCESS_NAME}"
                    key code {self.KEY_CODES[key.lower()]}{modifier_str}
                end tell
            end tell
            '''
        else:
            script = f'''
            tell application "System Events"
                tell process "{self.ABLETON_PROCESS_NAME}"
                    keystroke "{key}"{modifier_str}
                end tell
            end tell
            '''

        code, _, err = self._run_applescript(script)
        if code != 0:
            self.last_error = err
            return False
        return True

    def click_menu(self, menu_path: List[str]) -> bool:
        """Click a menu item by path.

        Args:
            menu_path: List like ["Edit", "Split"] or ["Edit", "Freeze Track"]

        Returns:
            True if menu was clicked successfully
        """
        if not self.activate_ableton() or len(menu_path) < 2:
            self.last_error = "Menu path must have at least 2 elements"
            return False

        menu_bar = menu_path[0]
        menu_item = menu_path[1]

        script = f'''
        tell application "System Events"
            tell process "{self.ABLETON_PROCESS_NAME}"
                click menu item "{menu_item}" of menu 1 of menu bar item "{menu_bar}" of menu bar 1
            end tell
        end tell
        '''

        code, _, err = self._run_applescript(script)
        if code != 0:
            self.last_error = err
            return False
        return True

    def wait_for_dialog(self, dialog_title: str, timeout: float = 10.0) -> bool:
        """Wait for a dialog window to appear.

        Args:
            dialog_title: The title of the dialog to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            True if dialog appeared within timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            script = f'''
            tell application "System Events"
                tell process "{self.ABLETON_PROCESS_NAME}"
                    return exists window "{dialog_title}"
                end tell
            end tell
            '''
            code, out, _ = self._run_applescript(script)
            if code == 0 and out.lower() == "true":
                return True
            time.sleep(0.2)
        return False

    def click_dialog_button(self, button_name: str) -> bool:
        """Click a button in the frontmost dialog.

        Args:
            button_name: The name of the button to click

        Returns:
            True if button was clicked successfully
        """
        script = f'''
        tell application "System Events"
            tell process "{self.ABLETON_PROCESS_NAME}"
                click button "{button_name}" of front window
            end tell
        end tell
        '''
        code, _, err = self._run_applescript(script)
        if code != 0:
            self.last_error = err
            return False
        return True

    # =========================================================================
    # HIGH-LEVEL ABLETON OPERATIONS
    # =========================================================================

    def split_clip(self) -> Dict[str, Any]:
        """Split clip at current position (Cmd+E)"""
        success = self._with_retry(lambda: self.send_keystroke("e", ["command"]))
        return {
            "success": success,
            "operation": "split",
            "shortcut": "Cmd+E",
            "error": self.last_error if not success else None
        }

    def consolidate(self) -> Dict[str, Any]:
        """Consolidate selected clips/time range (Cmd+J)"""
        success = self._with_retry(lambda: self.send_keystroke("j", ["command"]))
        return {
            "success": success,
            "operation": "consolidate",
            "shortcut": "Cmd+J",
            "error": self.last_error if not success else None
        }

    def duplicate(self) -> Dict[str, Any]:
        """Duplicate selection (Cmd+D)"""
        success = self._with_retry(lambda: self.send_keystroke("d", ["command"]))
        return {
            "success": success,
            "operation": "duplicate",
            "shortcut": "Cmd+D",
            "error": self.last_error if not success else None
        }

    def undo(self) -> Dict[str, Any]:
        """Undo last action (Cmd+Z)"""
        success = self._with_retry(lambda: self.send_keystroke("z", ["command"]))
        return {
            "success": success,
            "operation": "undo",
            "shortcut": "Cmd+Z",
            "error": self.last_error if not success else None
        }

    def redo(self) -> Dict[str, Any]:
        """Redo (Cmd+Shift+Z)"""
        success = self._with_retry(lambda: self.send_keystroke("z", ["command", "shift"]))
        return {
            "success": success,
            "operation": "redo",
            "shortcut": "Cmd+Shift+Z",
            "error": self.last_error if not success else None
        }

    def select_all(self) -> Dict[str, Any]:
        """Select all (Cmd+A)"""
        success = self._with_retry(lambda: self.send_keystroke("a", ["command"]))
        return {
            "success": success,
            "operation": "select_all",
            "shortcut": "Cmd+A",
            "error": self.last_error if not success else None
        }

    def copy(self) -> Dict[str, Any]:
        """Copy (Cmd+C)"""
        success = self._with_retry(lambda: self.send_keystroke("c", ["command"]))
        return {
            "success": success,
            "operation": "copy",
            "shortcut": "Cmd+C",
            "error": self.last_error if not success else None
        }

    def paste(self) -> Dict[str, Any]:
        """Paste (Cmd+V)"""
        success = self._with_retry(lambda: self.send_keystroke("v", ["command"]))
        return {
            "success": success,
            "operation": "paste",
            "shortcut": "Cmd+V",
            "error": self.last_error if not success else None
        }

    def cut(self) -> Dict[str, Any]:
        """Cut (Cmd+X)"""
        success = self._with_retry(lambda: self.send_keystroke("x", ["command"]))
        return {
            "success": success,
            "operation": "cut",
            "shortcut": "Cmd+X",
            "error": self.last_error if not success else None
        }

    def delete_selection(self) -> Dict[str, Any]:
        """Delete selection (Delete key)"""
        success = self._with_retry(lambda: self.send_keystroke("delete"))
        return {
            "success": success,
            "operation": "delete",
            "shortcut": "Delete",
            "error": self.last_error if not success else None
        }

    def save(self) -> Dict[str, Any]:
        """Save (Cmd+S)"""
        success = self._with_retry(lambda: self.send_keystroke("s", ["command"]))
        return {
            "success": success,
            "operation": "save",
            "shortcut": "Cmd+S",
            "error": self.last_error if not success else None
        }

    def export_audio(self) -> Dict[str, Any]:
        """Open Export Audio dialog (Cmd+Shift+R)"""
        success = self._with_retry(lambda: self.send_keystroke("r", ["command", "shift"]))
        return {
            "success": success,
            "operation": "export",
            "shortcut": "Cmd+Shift+R",
            "note": "Opens export dialog - use wait_for_dialog and click_dialog_button to complete",
            "error": self.last_error if not success else None
        }

    def toggle_loop(self) -> Dict[str, Any]:
        """Toggle loop (Cmd+L)"""
        success = self._with_retry(lambda: self.send_keystroke("l", ["command"]))
        return {
            "success": success,
            "operation": "toggle_loop",
            "shortcut": "Cmd+L",
            "error": self.last_error if not success else None
        }

    def zoom_to_selection(self) -> Dict[str, Any]:
        """Zoom to selection (Z)"""
        success = self._with_retry(lambda: self.send_keystroke("z"))
        return {
            "success": success,
            "operation": "zoom_to_selection",
            "shortcut": "Z",
            "error": self.last_error if not success else None
        }

    def toggle_automation_mode(self) -> Dict[str, Any]:
        """Toggle automation mode (A)"""
        success = self._with_retry(lambda: self.send_keystroke("a"))
        return {
            "success": success,
            "operation": "toggle_automation",
            "shortcut": "A",
            "error": self.last_error if not success else None
        }

    def toggle_draw_mode(self) -> Dict[str, Any]:
        """Toggle draw mode (B)"""
        success = self._with_retry(lambda: self.send_keystroke("b"))
        return {
            "success": success,
            "operation": "toggle_draw_mode",
            "shortcut": "B",
            "error": self.last_error if not success else None
        }

    def quantize(self) -> Dict[str, Any]:
        """Quantize selection (Cmd+U)"""
        success = self._with_retry(lambda: self.send_keystroke("u", ["command"]))
        return {
            "success": success,
            "operation": "quantize",
            "shortcut": "Cmd+U",
            "error": self.last_error if not success else None
        }

    def group_tracks(self) -> Dict[str, Any]:
        """Group selected tracks (Cmd+G)"""
        success = self._with_retry(lambda: self.send_keystroke("g", ["command"]))
        return {
            "success": success,
            "operation": "group_tracks",
            "shortcut": "Cmd+G",
            "note": "First select tracks with select_track or Shift+Click",
            "error": self.last_error if not success else None
        }

    def ungroup_tracks(self) -> Dict[str, Any]:
        """Ungroup selected group track (Cmd+Shift+G)"""
        success = self._with_retry(lambda: self.send_keystroke("g", ["command", "shift"]))
        return {
            "success": success,
            "operation": "ungroup_tracks",
            "shortcut": "Cmd+Shift+G",
            "error": self.last_error if not success else None
        }

    def move_track_up(self) -> Dict[str, Any]:
        """Move selected track up in arrangement (Cmd+Up)"""
        success = self._with_retry(lambda: self.send_keystroke("up", ["command"]))
        return {
            "success": success,
            "operation": "move_track_up",
            "shortcut": "Cmd+Up",
            "note": "First select track with select_track",
            "error": self.last_error if not success else None
        }

    def move_track_down(self) -> Dict[str, Any]:
        """Move selected track down in arrangement (Cmd+Down)"""
        success = self._with_retry(lambda: self.send_keystroke("down", ["command"]))
        return {
            "success": success,
            "operation": "move_track_down",
            "shortcut": "Cmd+Down",
            "note": "First select track with select_track",
            "error": self.last_error if not success else None
        }

    def freeze_track(self) -> Dict[str, Any]:
        """Freeze track - requires menu click"""
        success = self._with_retry(lambda: self.click_menu(["Edit", "Freeze Track"]))
        return {
            "success": success,
            "operation": "freeze_track",
            "menu": "Edit > Freeze Track",
            "error": self.last_error if not success else None
        }

    def flatten_track(self) -> Dict[str, Any]:
        """Flatten track - requires menu click"""
        success = self._with_retry(lambda: self.click_menu(["Edit", "Flatten"]))
        return {
            "success": success,
            "operation": "flatten_track",
            "menu": "Edit > Flatten",
            "error": self.last_error if not success else None
        }

    def reverse_clip(self) -> Dict[str, Any]:
        """Reverse clip - requires menu click"""
        success = self._with_retry(lambda: self.click_menu(["Edit", "Reverse"]))
        return {
            "success": success,
            "operation": "reverse_clip",
            "menu": "Edit > Reverse",
            "error": self.last_error if not success else None
        }

    def navigate(self, direction: str) -> Dict[str, Any]:
        """Navigate in given direction (up, down, left, right)"""
        success = self._with_retry(lambda: self.send_keystroke(direction))
        return {
            "success": success,
            "operation": "navigate",
            "direction": direction,
            "error": self.last_error if not success else None
        }

    def get_window_position(self) -> Optional[Dict[str, int]]:
        """Get the position and size of Ableton's main window"""
        script = f'''
        tell application "System Events"
            tell process "{self.ABLETON_PROCESS_NAME}"
                set frontWindow to front window
                set winPos to position of frontWindow
                set winSize to size of frontWindow
                set posX to item 1 of winPos as integer
                set posY to item 2 of winPos as integer
                set sizeW to item 1 of winSize as integer
                set sizeH to item 2 of winSize as integer
                return "" & posX & "|" & posY & "|" & sizeW & "|" & sizeH
            end tell
        end tell
        '''
        code, out, err = self._run_applescript(script)
        if code != 0:
            self.last_error = err
            return None

        try:
            parts = out.strip().split("|")
            return {
                "x": int(parts[0]),
                "y": int(parts[1]),
                "width": int(parts[2]),
                "height": int(parts[3])
            }
        except Exception as e:
            self.last_error = f"Parse error: {e}, output was: {out}"
            return None

    def click_at_position(self, x: int, y: int, modifiers: List[str] = None) -> bool:
        """Click at absolute screen coordinates with optional modifiers held.

        Args:
            x: Screen X coordinate
            y: Screen Y coordinate
            modifiers: List of modifiers to hold during click ['shift', 'command', 'option']
        """
        if not self.activate_ableton():
            return False

        # Build modifier key down/up commands
        mod_down = ""
        mod_up = ""
        if modifiers:
            for mod in modifiers:
                mod_name = mod.lower()
                if mod_name in ['shift', 'command', 'cmd', 'option', 'alt', 'control', 'ctrl']:
                    if mod_name == 'cmd':
                        mod_name = 'command'
                    elif mod_name == 'alt':
                        mod_name = 'option'
                    elif mod_name == 'ctrl':
                        mod_name = 'control'
                    mod_down += f"key down {mod_name}\n"
                    mod_up = f"key up {mod_name}\n" + mod_up  # Reverse order for key up

        script = f'''
        tell application "System Events"
            {mod_down}
            click at {{{x}, {y}}}
            {mod_up}
        end tell
        '''

        code, _, err = self._run_applescript(script)
        if code != 0:
            self.last_error = err
            return False
        return True

    def select_track_by_click(self, track_index: int, add_to_selection: bool = False,
                               track_height: int = 64, header_x_offset: int = 100,
                               top_offset: int = 150) -> Dict[str, Any]:
        """Select a track by clicking on its header.

        Args:
            track_index: The track index to select
            add_to_selection: If True, Shift+Click to add to existing selection
            track_height: Approximate height of each track in pixels (default 64)
            header_x_offset: X offset from window left for track header click
            top_offset: Y offset from window top to first track

        Note: You may need to adjust track_height based on your Ableton zoom level.
        """
        if not self.activate_ableton():
            return {"success": False, "error": "Could not activate Ableton"}

        # Get window position
        win = self.get_window_position()
        if not win:
            return {"success": False, "error": "Could not get window position"}

        # Calculate click position
        click_x = win["x"] + header_x_offset
        click_y = win["y"] + top_offset + (track_index * track_height) + (track_height // 2)

        # Click with or without shift
        modifiers = ["shift"] if add_to_selection else None
        success = self.click_at_position(click_x, click_y, modifiers)

        return {
            "success": success,
            "operation": "select_track_by_click",
            "track_index": track_index,
            "add_to_selection": add_to_selection,
            "click_position": {"x": click_x, "y": click_y},
            "error": self.last_error if not success else None
        }

    def select_tracks_range(self, start_track: int, end_track: int,
                            track_height: int = 64, header_x_offset: int = 100,
                            top_offset: int = 150) -> Dict[str, Any]:
        """Select a range of tracks by clicking first, then Shift+clicking last.

        Args:
            start_track: First track index to select
            end_track: Last track index to select (will select all in between)
            track_height: Approximate height of each track in pixels
            header_x_offset: X offset from window left for track header
            top_offset: Y offset from window top to first track
        """
        if not self.activate_ableton():
            return {"success": False, "error": "Could not activate Ableton"}

        # Get window position
        win = self.get_window_position()
        if not win:
            return {"success": False, "error": "Could not get window position"}

        # Calculate click positions
        click_x = win["x"] + header_x_offset
        click_y1 = win["y"] + top_offset + (start_track * track_height) + (track_height // 2)
        click_y2 = win["y"] + top_offset + (end_track * track_height) + (track_height // 2)

        # Click on first track (no modifiers)
        success1 = self.click_at_position(click_x, click_y1)
        if not success1:
            return {"success": False, "error": f"Failed to click first track: {self.last_error}"}

        time.sleep(0.1)

        # Shift+Click on second track to select range
        success2 = self.click_at_position(click_x, click_y2, ["shift"])
        if not success2:
            return {"success": False, "error": f"Failed to shift+click second track: {self.last_error}"}

        return {
            "success": True,
            "operation": "select_tracks_range",
            "start_track": start_track,
            "end_track": end_track,
            "tracks_selected": abs(end_track - start_track) + 1,
            "click_positions": [
                {"x": click_x, "y": click_y1},
                {"x": click_x, "y": click_y2}
            ]
        }


# Convenience function for quick operations
def ableton_keystroke(key: str, modifiers: list = None) -> bool:
    """Quick helper to send a keystroke to Ableton.

    Example:
        ableton_keystroke("e", ["command"])  # Split clip
        ableton_keystroke("j", ["command"])  # Consolidate
    """
    bridge = AbletonAutomatorBridge()
    return bridge.send_keystroke(key, modifiers)


# Handler for MCP integration
def handle_automator_command(command_type: str, params: dict = None) -> Dict[str, Any]:
    """Handle automator commands from MCP bridge.

    Args:
        command_type: The automator command (e.g., "automator_split", "automator_undo")
        params: Optional parameters (e.g., key and modifiers for automator_keystroke)

    Returns:
        Result dictionary with success status and operation details
    """
    params = params or {}
    bridge = AbletonAutomatorBridge()

    if command_type == "automator_split":
        return bridge.split_clip()
    elif command_type == "automator_consolidate":
        return bridge.consolidate()
    elif command_type == "automator_undo":
        return bridge.undo()
    elif command_type == "automator_redo":
        return bridge.redo()
    elif command_type == "automator_export":
        return bridge.export_audio()
    elif command_type == "automator_save":
        return bridge.save()
    elif command_type == "automator_duplicate":
        return bridge.duplicate()
    elif command_type == "automator_quantize":
        return bridge.quantize()
    elif command_type == "automator_freeze":
        return bridge.freeze_track()
    elif command_type == "automator_flatten":
        return bridge.flatten_track()
    elif command_type == "automator_reverse":
        return bridge.reverse_clip()
    elif command_type == "automator_group":
        return bridge.group_tracks()
    elif command_type == "automator_ungroup":
        return bridge.ungroup_tracks()
    elif command_type == "automator_move_track_up":
        return bridge.move_track_up()
    elif command_type == "automator_move_track_down":
        return bridge.move_track_down()
    elif command_type == "automator_select_tracks_range":
        start = params.get("start_track", 0)
        end = params.get("end_track", 1)
        track_height = params.get("track_height", 64)
        return bridge.select_tracks_range(start, end, track_height=track_height)
    elif command_type == "automator_select_track_click":
        track_index = params.get("track_index", 0)
        add_to_selection = params.get("add_to_selection", False)
        track_height = params.get("track_height", 64)
        return bridge.select_track_by_click(track_index, add_to_selection, track_height=track_height)
    elif command_type == "automator_keystroke":
        key = params.get("key", "")
        modifiers = params.get("modifiers", [])
        success = bridge.send_keystroke(key, modifiers)
        return {
            "success": success,
            "operation": "keystroke",
            "key": key,
            "modifiers": modifiers,
            "error": bridge.last_error if not success else None
        }
    else:
        return {
            "success": False,
            "error": f"Unknown automator command: {command_type}"
        }


if __name__ == "__main__":
    # Test the bridge
    print("Testing AbletonAutomatorBridge...")
    bridge = AbletonAutomatorBridge()

    print("\n1. Testing undo (safe operation)...")
    result = bridge.undo()
    print(f"   Result: {result}")

    print("\n2. Testing keystroke 'z' with command modifier...")
    success = bridge.send_keystroke("z", ["command"])
    print(f"   Success: {success}")

    print("\nDone! Check Ableton to verify operations.")
