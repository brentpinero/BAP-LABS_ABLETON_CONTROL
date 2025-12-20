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
VST_HOST = "127.0.0.1"
VST_HUB_PORT = 9878    # VST Hub (Instrument) - synths
VST_FX_PORT = 9879     # VST FX Chain (Audio Effect) - effects

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
        self.vst_hub_client = None   # Port 9878 - synths
        self.vst_fx_client = None    # Port 9879 - effects
        self.ableton_socket = None
        # Track registered plugins locally (separate for hub vs fx)
        self.hub_plugins = {}
        self.fx_plugins = {}

    def connect_vst_hub(self):
        """Connect to VST Hub (Instrument) on port 9878"""
        try:
            self.vst_hub_client = udp_client.SimpleUDPClient(VST_HOST, VST_HUB_PORT)
            print(f"✓ VST Hub (synths) ready on port {VST_HUB_PORT}")
            return True
        except Exception as e:
            print(f"✗ VST Hub error: {e}")
            return False

    def connect_vst_fx(self):
        """Connect to VST FX Chain (Audio Effect) on port 9879"""
        try:
            self.vst_fx_client = udp_client.SimpleUDPClient(VST_HOST, VST_FX_PORT)
            print(f"✓ VST FX Chain (effects) ready on port {VST_FX_PORT}")
            return True
        except Exception as e:
            print(f"✗ VST FX Chain error: {e}")
            return False

    def connect_vst(self):
        """Connect to both VST controllers"""
        hub_ok = self.connect_vst_hub()
        fx_ok = self.connect_vst_fx()
        return hub_ok and fx_ok

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
    # UNIVERSAL VST COMMANDS (target = "hub" or "fx")
    # =========================================================================

    def _get_client(self, target: str = "hub"):
        """Get the appropriate OSC client for the target device"""
        if target == "fx":
            if not self.vst_fx_client:
                self.connect_vst_fx()
            return self.vst_fx_client, self.fx_plugins
        else:
            if not self.vst_hub_client:
                self.connect_vst_hub()
            return self.vst_hub_client, self.hub_plugins

    def vst_register(self, slot: int, plugin_path: str, target: str = "hub"):
        """Register/load a plugin into a slot (1-8)"""
        client, plugins = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message("/register", [slot, plugin_path])
        plugin_name = plugin_path.split("/")[-1].replace(".vst3", "").replace(".vst", "").replace(".component", "")
        plugins[slot] = {"path": plugin_path, "name": plugin_name}
        return {"status": "success", "target": target, "slot": slot, "plugin": plugin_name}

    def vst_unregister(self, slot: int, target: str = "hub"):
        """Unload a plugin from a slot"""
        client, plugins = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message("/unregister", [slot])
        if slot in plugins:
            del plugins[slot]
        return {"status": "success", "target": target, "slot": slot, "message": "unregistered"}

    def vst_set_param(self, slot: int, index: int, value: float, target: str = "hub"):
        """Set a parameter on a plugin in a slot"""
        client, _ = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        value = max(0.0, min(1.0, value))
        client.send_message(f"/{slot}/param", [int(index), float(value)])
        return {"status": "success", "target": target, "slot": slot, "param": index, "value": value}

    def vst_open(self, slot: int, target: str = "hub"):
        """Open the plugin GUI for a slot"""
        client, _ = self._get_client(target)
        client.send_message(f"/{slot}/open", [])
        return {"status": "success", "target": target, "slot": slot, "message": "opening GUI"}

    def vst_list(self, target: str = "hub"):
        """List registered plugins"""
        client, plugins = self._get_client(target)
        client.send_message("/list", [])
        return {"status": "success", "target": target, "registered": plugins}

    def vst_ping(self, target: str = "hub"):
        """Ping the VST controller"""
        client, _ = self._get_client(target)
        client.send_message("/ping", [1])
        return {"status": "success", "target": target, "message": "ping sent"}

    def vst_select(self, slot: int):
        """Select which slot outputs audio (VST Hub only)"""
        client, _ = self._get_client("hub")

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message("/select", [slot])
        return {"status": "success", "slot": slot, "message": f"Selected slot {slot} for output"}

    def vst_close(self, slot: int, target: str = "hub"):
        """Close the plugin GUI for a slot"""
        client, _ = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message(f"/{slot}/close", [])
        return {"status": "success", "target": target, "slot": slot, "message": "closing GUI"}

    def vst_get_params(self, slot: int, target: str = "hub"):
        """Request parameter list from a plugin"""
        client, _ = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message(f"/{slot}/params", [])
        return {"status": "success", "target": target, "slot": slot, "message": "params requested (check Max console)"}

    def vst_dump_params(self, slot: int, target: str = "hub"):
        """Dump all parameters to file (iterates through each param)"""
        client, _ = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message(f"/{slot}/dumpparams", [])
        return {"status": "success", "target": target, "slot": slot, "message": "param dump started (check vst_param_dump.txt)"}

    def vst_param_count(self, slot: int, target: str = "hub"):
        """Get parameter count from a plugin"""
        client, _ = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message(f"/{slot}/paramcount", [])
        return {"status": "success", "target": target, "slot": slot, "message": "paramcount requested (check Max console)"}

    def vst_param_name(self, slot: int, index: int, target: str = "hub"):
        """Get a specific parameter name by index"""
        client, _ = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message(f"/{slot}/paramname", [int(index)])
        return {"status": "success", "target": target, "slot": slot, "index": index, "message": "paramname requested (check Max console)"}

    def vst_dump_params_iterative(self, slot: int, target: str = "hub"):
        """Dump params using iterative method (getparamcount + getparamname loop)"""
        client, _ = self._get_client(target)

        if slot < 1 or slot > 8:
            return {"status": "error", "message": "Slot must be 1-8"}

        client.send_message(f"/{slot}/dumpparams2", [])
        return {"status": "success", "target": target, "slot": slot, "message": "iterative param dump started (check vst_param_dump.txt)"}

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

            # vst select <slot> - for VST Hub slot switching
            if subcmd == "select" and len(parts) >= 3:
                try:
                    slot = int(parts[2])
                    return self.vst_select(slot)
                except ValueError:
                    return {"status": "error", "message": "Invalid slot number"}

            # vst <slot> param <index> <value>
            # vst <slot> open
            # vst <slot> close
            # vst <slot> params
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

                    if action == "close":
                        return self.vst_close(slot)

                    if action == "params":
                        return self.vst_get_params(slot)

                    if action == "dumpparams":
                        return self.vst_dump_params(slot)

                    if action == "dumpparams2":
                        return self.vst_dump_params_iterative(slot)

                    if action == "paramcount":
                        return self.vst_param_count(slot)

                    if action == "paramname" and len(parts) >= 4:
                        index = int(parts[3])
                        return self.vst_param_name(slot, index)

            except ValueError:
                pass

            return {"status": "error", "message": f"Unknown VST command: {text}"}

        # =====================================================================
        # FX CHAIN COMMANDS (port 9879) - same as vst but targets fx chain
        # =====================================================================
        if cmd == "fx":
            if len(parts) < 2:
                return {"status": "error", "message": "FX command incomplete"}

            subcmd = parts[1].lower()

            # fx register <slot> <path>
            if subcmd == "register" and len(parts) >= 4:
                try:
                    slot = int(parts[2])
                    plugin_path = " ".join(parts[3:])
                    return self.vst_register(slot, plugin_path, target="fx")
                except ValueError:
                    return {"status": "error", "message": "Invalid slot number"}

            # fx unregister <slot>
            if subcmd == "unregister" and len(parts) >= 3:
                try:
                    slot = int(parts[2])
                    return self.vst_unregister(slot, target="fx")
                except ValueError:
                    return {"status": "error", "message": "Invalid slot number"}

            # fx list
            if subcmd == "list":
                return self.vst_list(target="fx")

            # fx ping
            if subcmd == "ping":
                return self.vst_ping(target="fx")

            # fx <slot> param <index> <value>
            # fx <slot> open / close / params
            try:
                slot = int(subcmd)
                if len(parts) >= 3:
                    action = parts[2].lower()

                    if action == "param" and len(parts) >= 5:
                        index = int(parts[3])
                        value = float(parts[4])
                        return self.vst_set_param(slot, index, value, target="fx")

                    if action == "open":
                        return self.vst_open(slot, target="fx")

                    if action == "close":
                        return self.vst_close(slot, target="fx")

                    if action == "params":
                        return self.vst_get_params(slot, target="fx")

                    if action == "dumpparams":
                        return self.vst_dump_params(slot, target="fx")

                    if action == "dumpparams2":
                        return self.vst_dump_params_iterative(slot, target="fx")

                    if action == "paramcount":
                        return self.vst_param_count(slot, target="fx")

                    if action == "paramname" and len(parts) >= 4:
                        index = int(parts[3])
                        return self.vst_param_name(slot, index, target="fx")

            except ValueError:
                pass

            return {"status": "error", "message": f"Unknown FX command: {text}"}

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

        # =====================================================================
        # DEVICE PARAMETER COMMANDS (for Ableton stock plugins)
        # =====================================================================
        if cmd == "device":
            if len(parts) < 2:
                return {"status": "error", "message": "Usage: device params <track> <device> OR device set <track> <device> <param> <value>"}

            subcmd = parts[1].lower()

            # device params <track_index> <device_index>
            if subcmd == "params" and len(parts) >= 4:
                try:
                    track_idx = int(parts[2])
                    device_idx = int(parts[3])
                    return self.get_device_parameters(track_idx, device_idx)
                except ValueError:
                    return {"status": "error", "message": "Invalid track or device index"}

            # device set <track_index> <device_index> <param_index> <value>
            if subcmd == "set" and len(parts) >= 6:
                try:
                    track_idx = int(parts[2])
                    device_idx = int(parts[3])
                    param_idx = int(parts[4])
                    value = float(parts[5])
                    return self.set_device_parameter(track_idx, device_idx, param_idx, value)
                except ValueError:
                    return {"status": "error", "message": "Invalid indices or value"}

            return {"status": "error", "message": f"Unknown device command: {subcmd}"}

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
        # Small delay to ensure UDP packets are sent before exit
        import time
        time.sleep(0.15)
    else:
        # Interactive mode
        print()
        print("=" * 60)
        print("  UNIFIED MCP BRIDGE")
        print("  Ableton + VST Hub (9878) + FX Chain (9879)")
        print("=" * 60)
        print()
        print("VST Hub Commands (port 9878 - synths):")
        print("  vst register <slot> <path>      - Load synth into slot 1-8")
        print("  vst <slot> param <idx> <val>    - Set parameter (0-1 range)")
        print("  vst <slot> open / close         - Open/close plugin GUI")
        print("  vst select <slot>               - Select which slot outputs audio")
        print("  vst list / ping                 - List plugins / test connection")
        print()
        print("FX Chain Commands (port 9879 - effects):")
        print("  fx register <slot> <path>       - Load effect into slot 1-8")
        print("  fx <slot> param <idx> <val>     - Set parameter (0-1 range)")
        print("  fx <slot> open / close          - Open/close plugin GUI")
        print("  fx list / ping                  - List plugins / test connection")
        print()
        print("Ableton Commands:")
        print("  tempo <bpm>                     - Set tempo")
        print("  session                         - Get session info")
        print("  create track                    - Create MIDI track")
        print()
        print("Device Parameter Commands (stock plugins):")
        print("  device params <track> <device>  - Get all params for a device")
        print("  device set <t> <d> <p> <val>    - Set param value on device")
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
