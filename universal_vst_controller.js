/**
 * UNIVERSAL VST CONTROLLER
 * Routes OSC commands to multiple pre-allocated vst~ slots
 *
 * OSC Commands:
 *   /register <slot> <plugin_path>  - Load plugin into slot (1-8)
 *   /unregister <slot>              - Unload plugin from slot
 *   /<slot>/param <index> <value>   - Set parameter (index is 1-based for vst~)
 *   /<slot>/open                    - Open plugin GUI
 *   /list                           - List registered plugins
 *   /ping                           - Health check
 */

inlets = 1;
outlets = 9;  // 8 vst~ outlets + 1 status outlet

// Track which plugins are loaded in which slots
var slots = {};
for (var i = 1; i <= 8; i++) {
    slots[i] = { loaded: false, path: "", name: "" };
}

/**
 * Handle incoming OSC messages
 * Format: /command arg1 arg2 ...
 */
function anything() {
    var args = arrayfromargs(messagename, arguments);
    var cmd = args[0];

    // Log incoming command
    post("VST Controller received: " + args.join(" ") + "\n");

    // Parse the command
    if (cmd === "/register" && args.length >= 3) {
        registerPlugin(parseInt(args[1]), args[2]);
    }
    else if (cmd === "/unregister" && args.length >= 2) {
        unregisterPlugin(parseInt(args[1]));
    }
    else if (cmd === "/list") {
        listPlugins();
    }
    else if (cmd === "/ping") {
        outlet(8, "pong");
        post("PONG\n");
    }
    else if (cmd === "/select" && args.length >= 2) {
        selectSlot(parseInt(args[1]));
    }
    else if (cmd.indexOf("/") === 0) {
        // Check for slot commands like /1/param, /2/open, etc.
        var parts = cmd.split("/");
        if (parts.length >= 3) {
            var slotNum = parseInt(parts[1]);
            var action = parts[2];

            if (slotNum >= 1 && slotNum <= 8) {
                if (action === "param" && args.length >= 3) {
                    setParam(slotNum, parseInt(args[1]), parseFloat(args[2]));
                }
                else if (action === "open") {
                    openEditor(slotNum);
                }
                else if (action === "close") {
                    closeEditor(slotNum);
                }
                else if (action === "params") {
                    getParams(slotNum);
                }
                else if (action === "paramcount") {
                    getParamCount(slotNum);
                }
                else if (action === "paramname" && args.length >= 2) {
                    getParamName(slotNum, parseInt(args[1]));
                }
            }
        }
    }
}

/**
 * Register/load a plugin into a slot
 */
function registerPlugin(slot, pluginPath) {
    if (slot < 1 || slot > 8) {
        post("Error: Slot must be 1-8, got " + slot + "\n");
        return;
    }

    // Extract plugin name from path
    var pathParts = pluginPath.split("/");
    var pluginName = pathParts[pathParts.length - 1].replace(/\.(vst3|vst|component)$/i, "");

    // Send plug message to the appropriate vst~ outlet
    // Outlet index is slot-1 (0-indexed outlets for 1-indexed slots)
    outlet(slot - 1, "plug", pluginPath);

    // Update slot tracking
    slots[slot] = {
        loaded: true,
        path: pluginPath,
        name: pluginName
    };

    post("Registered slot " + slot + ": " + pluginName + "\n");
    outlet(8, "registered", slot, pluginName);
}

/**
 * Unload a plugin from a slot
 */
function unregisterPlugin(slot) {
    if (slot < 1 || slot > 8) {
        post("Error: Slot must be 1-8\n");
        return;
    }

    outlet(slot - 1, "unplug");

    var oldName = slots[slot].name;
    slots[slot] = { loaded: false, path: "", name: "" };

    post("Unregistered slot " + slot + " (" + oldName + ")\n");
    outlet(8, "unregistered", slot);
}

/**
 * Set a parameter on a plugin
 * Note: vst~ uses 1-based parameter indices
 */
function setParam(slot, paramIndex, value) {
    if (slot < 1 || slot > 8) {
        post("Error: Slot must be 1-8\n");
        return;
    }

    if (!slots[slot].loaded) {
        post("Warning: Slot " + slot + " has no plugin loaded\n");
        // Still send it - the plugin might be loaded but we lost track
    }

    // Clamp value to 0-1 range
    value = Math.max(0, Math.min(1, value));

    // vst~ expects: paramIndex value (1-based index) as a list
    // In Max JS, outlet(n, a, b) sends "a b" which should work as a list
    // But let's try explicit list format to be safe
    outlet(slot - 1, [paramIndex, value]);

    // post("Slot " + slot + " param " + paramIndex + " = " + value + "\n");
}

/**
 * Open the plugin editor GUI
 */
function openEditor(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "open");
    post("Opening editor for slot " + slot + "\n");
}

/**
 * Close the plugin editor GUI
 */
function closeEditor(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "close");
    post("Closing editor for slot " + slot + "\n");
}

/**
 * Get parameter list from plugin
 */
function getParams(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "params");
    post("Requesting params for slot " + slot + "\n");
}

// Track currently selected output slot (for VST Hub)
var selectedSlot = 1;

/**
 * Select which slot outputs audio (for VST Hub instrument)
 * Sends the slot number to outlet 8 with "select" prefix
 * The Max patch routes this to the selector~ objects
 */
function selectSlot(slot) {
    if (slot < 1 || slot > 8) {
        post("Error: Slot must be 1-8\n");
        return;
    }
    selectedSlot = slot;
    outlet(8, "select", slot);
    post("Selected output slot: " + slot + "\n");
}

/**
 * Get parameter count from plugin
 */
function getParamCount(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "getparamcount");
    post("Requesting param count for slot " + slot + "\n");
}

/**
 * Get a specific parameter name by index
 */
function getParamName(slot, index) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "getparamname", index);
    post("Requesting param name " + index + " for slot " + slot + "\n");
}

/**
 * List all registered plugins
 */
function listPlugins() {
    post("\n=== REGISTERED PLUGINS ===\n");
    var count = 0;
    for (var i = 1; i <= 8; i++) {
        if (slots[i].loaded) {
            post("  Slot " + i + ": " + slots[i].name + "\n");
            count++;
        }
    }
    if (count === 0) {
        post("  (no plugins registered)\n");
    }
    post("==========================\n\n");

    // Output slot info to status outlet
    outlet(8, "slots", JSON.stringify(slots));
}

/**
 * Handle raw list input (for direct param setting)
 * Format: slot paramIndex value
 */
function list() {
    var args = arrayfromargs(arguments);
    if (args.length >= 3) {
        setParam(parseInt(args[0]), parseInt(args[1]), parseFloat(args[2]));
    }
}

// Initialization
function loadbang() {
    post("\n");
    post("=====================================\n");
    post("  UNIVERSAL VST CONTROLLER READY\n");
    post("  8 slots available\n");
    post("=====================================\n");
    post("\n");
}
