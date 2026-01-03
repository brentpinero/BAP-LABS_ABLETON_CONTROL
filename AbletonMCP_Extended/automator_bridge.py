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

    ABLETON_APP_NAME = "Ableton Live 12 Suite"  # Adjust for your version
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
            tell process "{self.ABLETON_APP_NAME}"
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
                tell process "{self.ABLETON_APP_NAME}"
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
            tell process "{self.ABLETON_APP_NAME}"
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
