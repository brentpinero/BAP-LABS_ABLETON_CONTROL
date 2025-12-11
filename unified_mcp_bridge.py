#!/usr/bin/env python3
"""
UNIFIED MCP BRIDGE
Controls both Ableton (via socket MCP) and Serum (via OSC)

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

Serum commands (via OSC to port 9878):
    - serum_param <index> <value>
    - serum_filter_cutoff <value>
    - serum_filter_res <value>
    - serum_osc_a_level <value>
    - serum_wt_pos <value>
    - serum_attack <value>
    - serum_release <value>
    - ... (named param shortcuts)
"""

import socket
import json
import argparse
from pythonosc import udp_client

# Connection settings
ABLETON_HOST = "localhost"
ABLETON_PORT = 9877
SERUM_HOST = "localhost"
SERUM_PORT = 9878

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
        self.serum_client = None
        self.ableton_socket = None

    def connect_serum(self):
        """Connect to Serum OSC"""
        try:
            self.serum_client = udp_client.SimpleUDPClient(SERUM_HOST, SERUM_PORT)
            print(f"✓ Serum OSC ready on port {SERUM_PORT}")
            return True
        except Exception as e:
            print(f"✗ Serum OSC error: {e}")
            return False

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
    # SERUM COMMANDS
    # =========================================================================

    def serum_set_param(self, index: int, value: float):
        """Set a Serum parameter by index (0-1 range)"""
        if not self.serum_client:
            self.connect_serum()

        value = max(0.0, min(1.0, value))
        self.serum_client.send_message("/set_param", [int(index), float(value)])
        return {"status": "success", "param": index, "value": value}

    def serum_set_param_name(self, name: str, value: float):
        """Set a Serum parameter by name"""
        if name not in SERUM_PARAMS:
            return {"status": "error", "message": f"Unknown param: {name}"}

        index = SERUM_PARAMS[name]
        return self.serum_set_param(index, value)

    def serum_ping(self):
        """Ping Serum"""
        if not self.serum_client:
            self.connect_serum()
        self.serum_client.send_message("/ping", [1])
        return {"status": "success", "message": "ping sent"}

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
        text = text.lower().strip()
        parts = text.split()

        if not parts:
            return {"status": "error", "message": "Empty command"}

        # SERUM COMMANDS
        if parts[0] == "serum":
            if len(parts) < 2:
                return {"status": "error", "message": "Serum command incomplete"}

            if parts[1] == "ping":
                return self.serum_ping()

            if parts[1] == "list":
                return self.serum_list_params()

            if parts[1] == "param" and len(parts) >= 4:
                try:
                    index = int(parts[2])
                    value = float(parts[3])
                    return self.serum_set_param(index, value)
                except ValueError:
                    return {"status": "error", "message": "Invalid param index or value"}

            if parts[1] == "set" and len(parts) >= 4:
                name = parts[2]
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

            if parts[1] in shortcuts and len(parts) >= 3:
                try:
                    value = float(parts[2])
                    return self.serum_set_param_name(shortcuts[parts[1]], value)
                except ValueError:
                    return {"status": "error", "message": "Invalid value"}

        # ABLETON COMMANDS
        if parts[0] == "tempo" and len(parts) >= 2:
            try:
                tempo = float(parts[1])
                return self.set_tempo(tempo)
            except ValueError:
                return {"status": "error", "message": "Invalid tempo"}

        if parts[0] == "session" or (parts[0] == "get" and len(parts) > 1 and parts[1] == "session"):
            return self.get_session_info()

        if parts[0] == "create" and len(parts) > 1 and parts[1] == "track":
            return self.create_midi_track()

        return {"status": "error", "message": f"Unknown command: {text}"}


def main():
    parser = argparse.ArgumentParser(description="Unified MCP Bridge for Ableton & Serum")
    parser.add_argument("-c", "--command", help="Single command to execute")
    args = parser.parse_args()

    bridge = UnifiedMCPBridge()

    # Connect to both
    bridge.connect_serum()
    bridge.connect_ableton()

    if args.command:
        # Single command mode
        result = bridge.process_command(args.command)
        print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        print()
        print("=" * 50)
        print("  UNIFIED MCP BRIDGE")
        print("  Ableton + Serum Control")
        print("=" * 50)
        print()
        print("Commands:")
        print("  serum ping              - Test Serum connection")
        print("  serum list              - List Serum params")
        print("  serum param <idx> <val> - Set param by index")
        print("  serum set <name> <val>  - Set param by name")
        print("  serum cutoff <val>      - Filter cutoff shortcut")
        print("  tempo <bpm>             - Set Ableton tempo")
        print("  session                 - Get session info")
        print("  quit                    - Exit")
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
