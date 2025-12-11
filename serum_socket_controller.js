/**
 * SERUM SOCKET CONTROLLER
 * M4L JS that receives commands via socket and controls Serum vst~ by parameter index
 *
 * Commands (JSON over socket):
 *   {"type": "set_param", "index": 206, "value": 0.5}
 *   {"type": "get_param", "index": 206}
 *   {"type": "get_all_params"}
 *   {"type": "load_preset", "path": "/path/to/preset.fxp"}
 *   {"type": "ping"}
 */

autowatch = 1;
inlets = 2;   // inlet 0: commands, inlet 1: vst~ param responses
outlets = 2;  // outlet 0: to vst~, outlet 1: status/responses

// Parameter mapping from our JSON
var PARAM_COUNT = 2623;

// Critical parameter shortcuts (from serum2_parameter_mapping_complete.json)
var CRITICAL_PARAMS = {
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
    "arp_enable": 524
};

// Pending get requests (for async responses)
var pending_gets = {};

function loadbang() {
    post("\n");
    post("===========================================\n");
    post("  SERUM SOCKET CONTROLLER v1.0\n");
    post("  Ready to receive commands\n");
    post("===========================================\n");
    post("\n");

    // Output ready status
    outlet(1, "status", "ready");
}

// Main inlet - receives commands
function anything() {
    var cmd = messagename;
    var args = arrayfromargs(arguments);

    // Handle JSON command string
    if (cmd === "json") {
        try {
            var json_str = args.join(" ");
            var command = JSON.parse(json_str);
            process_command(command);
        } catch (e) {
            post("Error parsing JSON: " + e + "\n");
            outlet(1, "error", "Invalid JSON: " + e);
        }
        return;
    }

    // Handle direct commands
    if (cmd === "set_param") {
        // set_param <index> <value>
        if (args.length >= 2) {
            set_param(parseInt(args[0]), parseFloat(args[1]));
        }
        return;
    }

    if (cmd === "set_param_name") {
        // set_param_name <name> <value>
        if (args.length >= 2) {
            var name = args[0];
            var value = parseFloat(args[1]);
            if (CRITICAL_PARAMS[name] !== undefined) {
                set_param(CRITICAL_PARAMS[name], value);
            } else {
                post("Unknown parameter name: " + name + "\n");
                outlet(1, "error", "Unknown parameter: " + name);
            }
        }
        return;
    }

    if (cmd === "get_param") {
        // get_param <index>
        if (args.length >= 1) {
            get_param(parseInt(args[0]));
        }
        return;
    }

    if (cmd === "list_params") {
        list_critical_params();
        return;
    }

    if (cmd === "ping") {
        outlet(1, "pong", Date.now());
        return;
    }

    if (cmd === "open") {
        // Open Serum GUI
        outlet(0, "open");
        return;
    }

    if (cmd === "close") {
        // Close Serum GUI
        outlet(0, "wclose");
        return;
    }
}

function process_command(command) {
    var cmd_type = command.type;

    switch (cmd_type) {
        case "set_param":
            set_param(command.index, command.value);
            break;

        case "set_param_name":
            var idx = CRITICAL_PARAMS[command.name];
            if (idx !== undefined) {
                set_param(idx, command.value);
            } else {
                outlet(1, "error", "Unknown parameter: " + command.name);
            }
            break;

        case "get_param":
            get_param(command.index);
            break;

        case "get_all_params":
            get_all_params();
            break;

        case "load_preset":
            load_preset(command.path);
            break;

        case "ping":
            outlet(1, "pong", Date.now());
            break;

        case "open_gui":
            outlet(0, "open");
            break;

        case "close_gui":
            outlet(0, "wclose");
            break;

        case "list_critical":
            list_critical_params();
            break;

        default:
            post("Unknown command type: " + cmd_type + "\n");
            outlet(1, "error", "Unknown command: " + cmd_type);
    }
}

function set_param(index, value) {
    if (index < 0 || index >= PARAM_COUNT) {
        post("Parameter index out of range: " + index + "\n");
        outlet(1, "error", "Index out of range: " + index);
        return;
    }

    // Clamp value to 0-1 range
    value = Math.max(0, Math.min(1, value));

    // Send to vst~: <index> <value>
    outlet(0, index, value);

    // Confirm
    outlet(1, "param_set", index, value);
}

function get_param(index) {
    if (index < 0 || index >= PARAM_COUNT) {
        post("Parameter index out of range: " + index + "\n");
        outlet(1, "error", "Index out of range: " + index);
        return;
    }

    // Mark as pending
    pending_gets[index] = true;

    // Request from vst~
    outlet(0, "get", index);
}

function get_all_params() {
    post("Getting all " + PARAM_COUNT + " parameters...\n");
    outlet(0, "params");
}

function load_preset(path) {
    post("Loading preset: " + path + "\n");
    outlet(0, "read", path);
    outlet(1, "preset_loaded", path);
}

function list_critical_params() {
    post("\nCRITICAL PARAMETERS:\n");
    post("====================\n");
    for (var name in CRITICAL_PARAMS) {
        post("  " + name + ": " + CRITICAL_PARAMS[name] + "\n");
    }
    post("\n");

    // Also output as JSON
    outlet(1, "critical_params", JSON.stringify(CRITICAL_PARAMS));
}

// Inlet 1 - receives param values from vst~ outlet 3
function list() {
    var args = arrayfromargs(arguments);

    // vst~ sends: <index> <value>
    if (args.length >= 2) {
        var index = args[0];
        var value = args[1];

        // If this was a pending get, send the response
        if (pending_gets[index]) {
            delete pending_gets[index];
            outlet(1, "param_value", index, value);
        }
    }
}

// Handle param name responses from vst~
function msg_string(param_name) {
    // This receives parameter names when we send "params"
    outlet(1, "param_name", param_name);
}

// Utility: Set multiple params at once
function set_multiple(params_json) {
    try {
        var params = JSON.parse(params_json);
        for (var i = 0; i < params.length; i++) {
            var p = params[i];
            set_param(p.index, p.value);
        }
        outlet(1, "multiple_set", params.length);
    } catch (e) {
        post("Error parsing params: " + e + "\n");
        outlet(1, "error", "Invalid params JSON");
    }
}

// Utility: Ramp a parameter over time
var ramp_tasks = {};

function ramp_param(index, target_value, duration_ms) {
    // Cancel existing ramp on this param
    if (ramp_tasks[index]) {
        ramp_tasks[index].cancel();
    }

    var steps = Math.floor(duration_ms / 20); // 20ms per step
    var current_step = 0;

    // Get current value first (we'll estimate from 0.5 for now)
    var start_value = 0.5;
    var step_size = (target_value - start_value) / steps;

    var task = new Task(function() {
        current_step++;
        var new_value = start_value + (step_size * current_step);
        set_param(index, new_value);

        if (current_step >= steps) {
            set_param(index, target_value); // Ensure we hit exact target
            ramp_tasks[index] = null;
        } else {
            task.schedule(20);
        }
    });

    ramp_tasks[index] = task;
    task.schedule(20);

    outlet(1, "ramp_started", index, target_value, duration_ms);
}
