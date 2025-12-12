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
 *   /clearlog                       - Clear the log file
 */

inlets = 1;
outlets = 9;  // 8 vst~ outlets + 1 status outlet

// Log file path for external reading (Claude can read this)
var LOG_FILE_PATH = "/Users/brentpinero/Documents/serum_llm_2/max_console.log";
var MAX_LOG_LINES = 500;  // Keep log file manageable

/**
 * Log to both Max console and file
 */
function log(msg) {
    post(msg);
    logToFile(msg.replace(/\n$/, ""));  // Strip trailing newline for file
}

/**
 * Write a message to the log file (append mode)
 */
function logToFile(msg) {
    try {
        var f = new File(LOG_FILE_PATH, "write");
        if (f.isopen) {
            f.eof = f.eof;  // seek to end for append
            var timestamp = new Date().toISOString();
            f.writeline(timestamp + " | " + msg);
            f.close();
        } else {
            // Try creating the file
            f = new File(LOG_FILE_PATH, "write", "TEXT");
            if (f.isopen) {
                var timestamp = new Date().toISOString();
                f.writeline(timestamp + " | " + msg);
                f.close();
            }
        }
    } catch (e) {
        post("Log file error: " + e + "\n");
    }
}

/**
 * Clear the log file
 */
function clearLog() {
    try {
        var f = new File(LOG_FILE_PATH, "write", "TEXT");
        if (f.isopen) {
            f.writeline("=== MAX VST CONTROLLER LOG ===");
            f.writeline("Cleared at: " + new Date().toISOString());
            f.writeline("==============================");
            f.close();
            post("Log file cleared\n");
        } else {
            post("Could not open log file for writing\n");
        }
    } catch (e) {
        post("Clear log error: " + e + "\n");
    }
}

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
    log("VST Controller received: " + args.join(" ") + "\n");

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
        log("PONG\n");
    }
    else if (cmd === "/clearlog") {
        clearLog();
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
                // Preset/Program commands
                else if (action === "program" && args.length >= 2) {
                    setProgram(slotNum, parseInt(args[1]));
                }
                else if (action === "pgmnames") {
                    getProgramNames(slotNum);
                }
                else if (action === "pgmcount") {
                    getProgramCount(slotNum);
                }
                else if (action === "getprogram") {
                    getCurrentProgram(slotNum);
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
        log("Error: Slot must be 1-8, got " + slot + "\n");
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

    log("Registered slot " + slot + ": " + pluginName + "\n");
    outlet(8, "registered", slot, pluginName);
}

/**
 * Unload a plugin from a slot
 */
function unregisterPlugin(slot) {
    if (slot < 1 || slot > 8) {
        log("Error: Slot must be 1-8\n");
        return;
    }

    outlet(slot - 1, "unplug");

    var oldName = slots[slot].name;
    slots[slot] = { loaded: false, path: "", name: "" };

    log("Unregistered slot " + slot + " (" + oldName + ")\n");
    outlet(8, "unregistered", slot);
}

/**
 * Set a parameter on a plugin
 * Note: vst~ uses 1-based parameter indices
 */
function setParam(slot, paramIndex, value) {
    if (slot < 1 || slot > 8) {
        log("Error: Slot must be 1-8\n");
        return;
    }

    if (!slots[slot].loaded) {
        log("Warning: Slot " + slot + " has no plugin loaded\n");
        // Still send it - the plugin might be loaded but we lost track
    }

    // Clamp value to 0-1 range
    value = Math.max(0, Math.min(1, value));

    // vst~ expects: paramIndex value (1-based index) as a list
    // In Max JS, outlet(n, a, b) sends "a b" which should work as a list
    // But let's try explicit list format to be safe
    outlet(slot - 1, [paramIndex, value]);

    log("Slot " + slot + " param " + paramIndex + " = " + value + "\n");
}

/**
 * Open the plugin editor GUI
 */
function openEditor(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "open");
    log("Opening editor for slot " + slot + "\n");
}

/**
 * Close the plugin editor GUI
 */
function closeEditor(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "close");
    log("Closing editor for slot " + slot + "\n");
}

/**
 * Get parameter list from plugin
 */
function getParams(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "params");
    log("Requesting params for slot " + slot + "\n");
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
        log("Error: Slot must be 1-8\n");
        return;
    }
    selectedSlot = slot;
    outlet(8, "select", slot);
    log("Selected output slot: " + slot + "\n");
}

/**
 * Get parameter count from plugin
 */
function getParamCount(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "getparamcount");
    log("Requesting param count for slot " + slot + "\n");
}

/**
 * Get a specific parameter name by index
 */
function getParamName(slot, index) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "getparamname", index);
    log("Requesting param name " + index + " for slot " + slot + "\n");
}

/**
 * Set program/preset by index
 */
function setProgram(slot, programNum) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "pgm", programNum);
    log("Setting program " + programNum + " for slot " + slot + "\n");
}

/**
 * Get all program/preset names
 */
function getProgramNames(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "pgmnames");
    log("Requesting program names for slot " + slot + "\n");
}

/**
 * Get program count
 */
function getProgramCount(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "pgmcount");
    log("Requesting program count for slot " + slot + "\n");
}

/**
 * Get current program number
 */
function getCurrentProgram(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "getpgm");
    log("Requesting current program for slot " + slot + "\n");
}

/**
 * List all registered plugins
 */
function listPlugins() {
    log("\n=== REGISTERED PLUGINS ===\n");
    var count = 0;
    for (var i = 1; i <= 8; i++) {
        if (slots[i].loaded) {
            log("  Slot " + i + ": " + slots[i].name + "\n");
            count++;
        }
    }
    if (count === 0) {
        log("  (no plugins registered)\n");
    }
    log("==========================\n\n");

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
    // Clear log on startup
    clearLog();

    log("\n");
    log("=====================================\n");
    log("  UNIVERSAL VST CONTROLLER READY\n");
    log("  8 slots available\n");
    log("  Log file: " + LOG_FILE_PATH + "\n");
    log("=====================================\n");
    log("\n");
}
