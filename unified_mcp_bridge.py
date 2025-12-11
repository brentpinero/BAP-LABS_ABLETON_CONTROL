#!/usr/bin/env python3
"""
UNIFIED MCP BRIDGE
Controls Ableton (via socket MCP) and ANY VST plugin (via Universal OSC Controller)

Usage:
    python unified_mcp_bridge.py                    # Interactive mode
    python unified_mcp_bridge.py -c "set tempo 120" # Single command

Ableton commands (via socket to port 9877):
    - set_tempo <bpm>
    - create_midi_track
    - get_session_info
    - load_browser_item <track_index> <uri>
    - set_device_parameter <track> <device> <param> <value>
    - ... (all existing MCP commands)

Universal VST commands (via OSC to port 9878):
    - vst register <slot> <plugin_path>    # Load plugin into slot 1-8
    - vst unregister <slot>                # Unload plugin from slot
    - vst <slot> param <index> <value>     # Set parameter
    - vst <slot> open                      # Open plugin GUI
    - vst list                             # List registered plugins

Legacy Serum shortcuts (uses slot 1 by default):
    - serum_param <index> <value>
    - serum cutoff <value>
    - serum attack <value>
    - ... (named param shortcuts)
"""

import socket
import json
import argparse
from pythonosc import udp_client

# Connection settings
ABLETON_HOST = "localhost"
ABLETON_PORT = 9877
VST_HOST = "localhost"
VST_PORT = 9878

# Default slot for legacy Serum commands
DEFAULT_SERUM_SLOT = 1

# Serum critical parameter indices (from serum2_parameter_mapping_complete.json)
SERUM_PARAMS = {
    "master_volume": 1,
    "main_tuning": 2,
    "amp": 3,
    "osc_a_enable": 21,
    "osc_a_level": 22,
    "osc_a_pan": 23,
    "osc_a_pitch": 29,
    "osc_a_wt_pos": 60,
    "osc_b_enable": 76,
    "osc_b_level": 77,
    "osc_b_pan": 78,
    "osc_b_pitch": 84,
    "osc_b_wt_pos": 115,
    "noise_enable": 186,
    "noise_level": 187,
    "sub_enable": 194,
    "sub_level": 195,
    "filter_1_freq": 206,
    "filter_1_res": 207,
    "filter_1_drive": 208,
    "filter_2_freq": 217,
    "filter_2_res": 218,
    "env_1_attack": 225,
    "env_1_decay": 227,
    "env_1_sustain": 228,
    "env_1_release": 229,
    "env_2_attack": 234,
    "env_2_decay": 236,
    "env_2_sustain": 237,
    "env_2_release": 238,
    "lfo_1_rate": 263,
    "lfo_2_rate": 268,
    "lfo_3_rate": 273,
    "lfo_4_rate": 278,
    "macro_1": 441,
    "macro_2": 442,
    "macro_3": 443,
    "macro_4": 444,
}


class UnifiedMCPBridge:
    def __init__(self):
        self.vst_client = None
        self.ableton_socket = None
        # Track registered plugins locally
        self.registered_plugins = {}

    def connect_vst(self):
        """Connect to Universal VST Controller OSC"""
        try:
            self.vst_client = udp_client.SimpleUDPClient(VST_HOST, VST_PORT)
            print(f"✓ Universal VST Controller ready on port {VST_PORT}")
            return True
        except Exception as e:
            print(f"✗ VST Controller error: {e}")
            return False

    # Legacy alias
    def connect_serum(self):
        return self.connect_vst()

    def connect_ableton(self):
        """Connect to Ableton MCP"""
        try:
            self.ableton_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ableton_socket.settimeout(10)
            self.ableton_socket.connect((ABLETON_HOST, ABLETON_PORT))
            print(f"✓ Ableton MCP connected on port {ABLETON_PORT}")
            return True
        except Exception as e:
            print(f"✗ Ableton MCP error: {e}")
            self.ableton_socket = None
            return False

    def disconnect(self):
        """Clean up connections"""
        if self.ableton_socket:
            try:
                self.ableton_socket.close()
            except:
                pass

    # =========================================================================
    # UNIVERSAL VST COMMANDS
    # =========================================================================

    def vst_register(self, slot: int, plugin_path: str):
        """Register/load a plugin into a slot (1-8)"""
        if not self.vst_client:
            self.connect_vst()

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        self.vst_client.send_message("/register", [slot, plugin_path])
        # Extract plugin name for tracking
        plugin_name = plugin_path.split("/")[-1].replace(".vst3", "").replace(".vst", "").replace(".component", "")
        self.registered_plugins[slot] = {"path": plugin_path, "name": plugin_name}
        return {"status": "success", "slot": slot, "plugin": plugin_name}

    def vst_unregister(self, slot: int):
        """Unload a plugin from a slot"""
        if not self.vst_client:
            self.connect_vst()

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        self.vst_client.send_message("/unregister", [slot])
        if slot in self.registered_plugins:
            del self.registered_plugins[slot]
        return {"status": "success", "slot": slot, "message": "unregistered"}

    def vst_set_param(self, slot: int, index: int, value: float):
        """Set a parameter on a plugin in a slot"""
        if not self.vst_client:
            self.connect_vst()

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        value = max(0.0, min(1.0, value))
        self.vst_client.send_message(f"/{slot}/param", [int(index), float(value)])
        return {"status": "success", "slot": slot, "param": index, "value": value}

    def vst_open(self, slot: int):
        """Open the plugin GUI for a slot"""
        if not self.vst_client:
            self.connect_vst()

        self.vst_client.send_message(f"/{slot}/open", [])
        return {"status": "success", "slot": slot, "message": "opening GUI"}

    def vst_list(self):
        """List registered plugins"""
        if not self.vst_client:
            self.connect_vst()

        self.vst_client.send_message("/list", [])
        return {"status": "success", "registered": self.registered_plugins}

    def vst_ping(self):
        """Ping the VST controller"""
        if not self.vst_client:
            self.connect_vst()
        self.vst_client.send_message("/ping", [1])
        return {"status": "success", "message": "ping sent"}

    # =========================================================================
    # LEGACY SERUM COMMANDS (use slot 1 by default)
    # =========================================================================

    def serum_set_param(self, index: int, value: float):
        """Set a Serum parameter by index (legacy - uses slot 1)"""
        return self.vst_set_param(DEFAULT_SERUM_SLOT, index, value)

    def serum_set_param_name(self, name: str, value: float):
        """Set a Serum parameter by name (legacy - uses slot 1)"""
        if name not in SERUM_PARAMS:
            return {"status": "error", "message": f"Unknown param: {name}"}

        index = SERUM_PARAMS[name]
        return self.serum_set_param(index, value)

    def serum_ping(self):
        """Ping (legacy alias)"""
        return self.vst_ping()

    def serum_list_params(self):
        """List available Serum parameter names"""
        return {"status": "success", "params": list(SERUM_PARAMS.keys())}

    # =========================================================================
    # ABLETON COMMANDS
    # =========================================================================

    def ableton_command(self, cmd_type: str, params: dict = None):
        """Send a command to Ableton MCP"""
        if not self.ableton_socket:
            if not self.connect_ableton():
                return {"status": "error", "message": "Not connected to Ableton"}

        if params is None:
            params = {}

        command = {"type": cmd_type, "params": params}

        try:
            self.ableton_socket.sendall(json.dumps(command).encode('utf-8'))
            response = self.ableton_socket.recv(65536).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            # Try to reconnect once
            self.ableton_socket = None
            if self.connect_ableton():
                try:
                    self.ableton_socket.sendall(json.dumps(command).encode('utf-8'))
                    response = self.ableton_socket.recv(65536).decode('utf-8')
                    return json.loads(response)
                except Exception as e2:
                    return {"status": "error", "message": str(e2)}
            return {"status": "error", "message": str(e)}

    def get_session_info(self):
        return self.ableton_command("get_session_info")

    def set_tempo(self, tempo: float):
        return self.ableton_command("set_tempo", {"tempo": tempo})

    def create_midi_track(self, index: int = -1):
        return self.ableton_command("create_midi_track", {"index": index})

    def load_browser_item(self, track_index: int, item_uri: str):
        return self.ableton_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": item_uri
        })

    def set_device_parameter(self, track_index: int, device_index: int,
                             parameter_index: int, value: float):
        return self.ableton_command("set_device_parameter", {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "value": value
        })

    def get_device_parameters(self, track_index: int, device_index: int):
        return self.ableton_command("get_device_parameters", {
            "track_index": track_index,
            "device_index": device_index
        })

    # =========================================================================
    # NATURAL LANGUAGE PARSER (simple)
    # =========================================================================

    def process_command(self, text: str):
        """Process a natural language command"""
        text = text.strip()
        parts = text.split()

        if not parts:
            return {"status": "error", "message": "Empty command"}

        cmd = parts[0].lower()

        # =====================================================================
        # VST COMMANDS (new universal approach)
        # =====================================================================
        if cmd == "vst":
            if len(parts) < 2:
                return {"status": "error", "message": "VST command incomplete"}

            subcmd = parts[1].lower()

            # vst register <slot> <path>
            if subcmd == "register" and len(parts) >= 4:
                try:
                    slot = int(parts[2])
                    # Path might have spaces, rejoin everything after slot
                    plugin_path = " ".join(parts[3:])
                    return self.vst_register(slot, plugin_path)
                except ValueError:
                    return {"status": "error", "message": "Invalid slot number"}

            # vst unregister <slot>
            if subcmd == "unregister" and len(parts) >= 3:
                try:
                    slot = int(parts[2])
                    return self.vst_unregister(slot)
                except ValueError:
                    return {"status": "error", "message": "Invalid slot number"}

            # vst list
            if subcmd == "list":
                return self.vst_list()

            # vst ping
            if subcmd == "ping":
                return self.vst_ping()

            # vst <slot> param <index> <value>
            # vst <slot> open
            try:
                slot = int(subcmd)
                if len(parts) >= 3:
                    action = parts[2].lower()

                    if action == "param" and len(parts) >= 5:
                        index = int(parts[3])
                        value = float(parts[4])
                        return self.vst_set_param(slot, index, value)

                    if action == "open":
                        return self.vst_open(slot)

            except ValueError:
                pass

            return {"status": "error", "message": f"Unknown VST command: {text}"}

        # =====================================================================
        # LEGACY SERUM COMMANDS (uses slot 1)
        # =====================================================================
        if cmd == "serum":
            if len(parts) < 2:
                return {"status": "error", "message": "Serum command incomplete"}

            subcmd = parts[1].lower()

            if subcmd == "ping":
                return self.serum_ping()

            if subcmd == "list":
                return self.serum_list_params()

            if subcmd == "param" and len(parts) >= 4:
                try:
                    index = int(parts[2])
                    value = float(parts[3])
                    return self.serum_set_param(index, value)
                except ValueError:
                    return {"status": "error", "message": "Invalid param index or value"}

            if subcmd == "set" and len(parts) >= 4:
                name = parts[2].lower()
                try:
                    value = float(parts[3])
                    return self.serum_set_param_name(name, value)
                except ValueError:
                    return {"status": "error", "message": "Invalid value"}

            # Shortcuts
            shortcuts = {
                "cutoff": "filter_1_freq",
                "filter": "filter_1_freq",
                "res": "filter_1_res",
                "resonance": "filter_1_res",
                "attack": "env_1_attack",
                "release": "env_1_release",
                "decay": "env_1_decay",
                "sustain": "env_1_sustain",
                "wt": "osc_a_wt_pos",
                "wavetable": "osc_a_wt_pos",
                "level": "osc_a_level",
            }

            if subcmd in shortcuts and len(parts) >= 3:
                try:
                    value = float(parts[2])
                    return self.serum_set_param_name(shortcuts[subcmd], value)
                except ValueError:
                    return {"status": "error", "message": "Invalid value"}

            return {"status": "error", "message": f"Unknown Serum command: {text}"}

        # =====================================================================
        # ABLETON COMMANDS
        # =====================================================================
        if cmd == "tempo" and len(parts) >= 2:
            try:
                tempo = float(parts[1])
                return self.set_tempo(tempo)
            except ValueError:
                return {"status": "error", "message": "Invalid tempo"}

        if cmd == "session" or (cmd == "get" and len(parts) > 1 and parts[1].lower() == "session"):
            return self.get_session_info()

        if cmd == "create" and len(parts) > 1 and parts[1].lower() == "track":
            return self.create_midi_track()

        return {"status": "error", "message": f"Unknown command: {text}"}


def main():
    parser = argparse.ArgumentParser(description="Unified MCP Bridge for Ableton & VST Plugins")
    parser.add_argument("-c", "--command", help="Single command to execute")
    args = parser.parse_args()

    bridge = UnifiedMCPBridge()

    # Connect to both
    bridge.connect_vst()
    bridge.connect_ableton()

    if args.command:
        # Single command mode
        result = bridge.process_command(args.command)
        print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        print()
        print("=" * 60)
        print("  UNIFIED MCP BRIDGE")
        print("  Ableton + Universal VST Control (8 slots)")
        print("=" * 60)
        print()
        print("VST Commands:")
        print("  vst register <slot> <path>      - Load plugin into slot 1-8")
        print("  vst unregister <slot>           - Unload plugin from slot")
        print("  vst <slot> param <idx> <val>    - Set parameter")
        print("  vst <slot> open                 - Open plugin GUI")
        print("  vst list                        - List registered plugins")
        print("  vst ping                        - Test connection")
        print()
        print("Legacy Serum (slot 1):")
        print("  serum cutoff <val>              - Filter cutoff shortcut")
        print("  serum set <name> <val>          - Set param by name")
        print("  serum list                      - List Serum param names")
        print()
        print("Ableton Commands:")
        print("  tempo <bpm>                     - Set tempo")
        print("  session                         - Get session info")
        print("  create track                    - Create MIDI track")
        print()
        print("  quit                            - Exit")
        print()

        while True:
            try:
                cmd = input("> ").strip()
                if cmd.lower() in ["quit", "exit", "q"]:
                    break
                if not cmd:
                    continue

                result = bridge.process_command(cmd)
                print(json.dumps(result, indent=2))
                print()
            except KeyboardInterrupt:
                break
            except EOFError:
                break

    bridge.disconnect()
    print("Goodbye!")


if __name__ == "__main__":
    main()
