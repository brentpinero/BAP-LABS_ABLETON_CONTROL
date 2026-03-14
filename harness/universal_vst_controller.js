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
        log("DEBUG: parts=" + parts.join("|") + " length=" + parts.length + "\n");
        if (parts.length >= 3) {
            var slotNum = parseInt(parts[1]);
            var action = parts[2];
            log("DEBUG: slotNum=" + slotNum + " action=[" + action + "]\n");

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
                else if (action === "dumpparams") {
                    startParamDump(slotNum);
                }
                else if (action === "dumpparams2") {
                    log("DEBUG: dumpparams2 action matched for slot " + slotNum + "\n");
                    startParamDumpIterative(slotNum);
                }
                else if (action === "paramcount") {
                    getParamCount(slotNum);
                }
                else if (action === "paramname" && args.length >= 2) {
                    getParamName(slotNum, parseInt(args[1]));
                }
                // Shell plugin commands (for WaveShell, etc.)
                else if (action === "getsubnames") {
                    getSubNames(slotNum);
                }
                else if (action === "printids") {
                    printIds(slotNum);
                }
                else if (action === "subname" && args.length >= 2) {
                    loadSubPlugin(slotNum, args[1]);
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
 * Get parameter list from plugin (dumps to Max console)
 */
function getParams(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "params");
    log("Requesting params for slot " + slot + "\n");
}

// Track param dump state
var paramDumpState = {
    active: false,
    slot: 0,
    currentIndex: 1,
    totalParams: 0,
    params: [],
    lines: []  // Accumulate all lines here
};

/**
 * Start a param dump - use "params" message which streams param names to outlet 2
 */
function startParamDump(slot) {
    if (slot < 1 || slot > 8) return;

    paramDumpState.active = true;
    paramDumpState.slot = slot;
    paramDumpState.currentIndex = 0;
    paramDumpState.totalParams = 0;
    paramDumpState.params = [];
    paramDumpState.lines = [];

    // Add header to lines buffer
    paramDumpState.lines.push("=== PARAM DUMP FOR SLOT " + slot + " ===");
    paramDumpState.lines.push("Plugin: " + (slots[slot].name || "Unknown"));
    paramDumpState.lines.push("Path: " + (slots[slot].path || "Unknown"));
    paramDumpState.lines.push("---");

    log("Starting param dump for slot " + slot + "...\n");

    // Send "params" - streams parameter names through outlet 2 (6th from right)
    // Each param name arrives as a symbol, we'll count them as they come
    outlet(slot - 1, "params");

    // Set a timeout to finish the dump after params stop streaming
    // Use Task to delay the finish
    var finishTask = new Task(function() {
        if (paramDumpState.active && paramDumpState.slot === slot) {
            finishParamDump();
        }
    });
    finishTask.schedule(2000);  // 2 second timeout
}

/**
 * Finish the param dump - write all accumulated lines to file
 */
function finishParamDump() {
    paramDumpState.lines.push("---");
    paramDumpState.lines.push("=== END DUMP ===");

    // Write all lines at once
    var PARAM_LOG = "/Users/brentpinero/Documents/serum_llm_2/vst_param_dump.txt";
    try {
        var f = new File(PARAM_LOG, "write", "TEXT");
        if (f.isopen) {
            for (var i = 0; i < paramDumpState.lines.length; i++) {
                f.writeline(paramDumpState.lines[i]);
            }
            f.close();
            log("Param dump complete! " + (paramDumpState.totalParams) + " params written to vst_param_dump.txt\n");
        } else {
            log("ERROR: Could not open param dump file for writing\n");
        }
    } catch (e) {
        log("ERROR writing param dump: " + e + "\n");
    }

    paramDumpState.active = false;
}

// State for iterative param dump (dumpparams2)
var iterativeDumpState = {
    active: false,
    slot: 0,
    totalParams: 0,
    currentIndex: 0,
    lines: [],
    waitingForCount: false,
    waitingForName: false
};

/**
 * Start iterative param dump - uses getparamcount + getparamname loop
 * More reliable for VST3 plugins that don't respond to "params" message
 */
function startParamDumpIterative(slot) {
    if (slot < 1 || slot > 8) return;

    iterativeDumpState.active = true;
    iterativeDumpState.slot = slot;
    iterativeDumpState.totalParams = 0;
    iterativeDumpState.currentIndex = 0;
    iterativeDumpState.lines = [];
    iterativeDumpState.waitingForCount = true;
    iterativeDumpState.waitingForName = false;

    // Add header
    iterativeDumpState.lines.push("=== PARAM DUMP FOR SLOT " + slot + " ===");
    iterativeDumpState.lines.push("Plugin: " + (slots[slot].name || "Unknown"));
    iterativeDumpState.lines.push("Path: " + (slots[slot].path || "Unknown"));
    iterativeDumpState.lines.push("---");

    log("Starting iterative param dump for slot " + slot + "...\n");

    // First, get the param count using "get -4"
    outlet(slot - 1, "get", -4);
}

/**
 * Handle param count response for iterative dump
 * Called when vst~ returns the param count
 */
function handleParamCountResponse(slot, count) {
    if (!iterativeDumpState.active || iterativeDumpState.slot !== slot) return;
    if (!iterativeDumpState.waitingForCount) return;

    iterativeDumpState.waitingForCount = false;
    iterativeDumpState.totalParams = count;

    log("Got param count: " + count + " for slot " + slot + "\n");

    if (count <= 0) {
        // No params, finish immediately
        finishIterativeDump();
        return;
    }

    // Start getting param names
    iterativeDumpState.currentIndex = 0;
    getNextParamName();
}

/**
 * Get the next param name in the iteration
 */
function getNextParamName() {
    if (!iterativeDumpState.active) return;

    if (iterativeDumpState.currentIndex >= iterativeDumpState.totalParams) {
        // Done with all params
        finishIterativeDump();
        return;
    }

    iterativeDumpState.waitingForName = true;
    // Use "get <index>" to get param info - index is 1-based in vst~
    outlet(iterativeDumpState.slot - 1, "get", iterativeDumpState.currentIndex + 1);
}

/**
 * Handle param name response for iterative dump
 */
function handleParamNameResponse(slot, index, name) {
    if (!iterativeDumpState.active || iterativeDumpState.slot !== slot) return;
    if (!iterativeDumpState.waitingForName) return;

    iterativeDumpState.waitingForName = false;

    // Add to lines (1-indexed for display)
    iterativeDumpState.lines.push((index + 1) + ": " + name);

    // Move to next param
    iterativeDumpState.currentIndex++;

    // Small delay to avoid flooding, then get next
    var nextTask = new Task(function() {
        getNextParamName();
    });
    nextTask.schedule(10);  // 10ms delay between params
}

/**
 * Finish the iterative param dump
 */
function finishIterativeDump() {
    iterativeDumpState.lines.push("---");
    iterativeDumpState.lines.push("=== END DUMP ===");

    var PARAM_LOG = "/Users/brentpinero/Documents/serum_llm_2/vst_param_dump.txt";
    try {
        var f = new File(PARAM_LOG, "write", "TEXT");
        if (f.isopen) {
            for (var i = 0; i < iterativeDumpState.lines.length; i++) {
                f.writeline(iterativeDumpState.lines[i]);
            }
            f.close();
            log("Iterative param dump complete! " + iterativeDumpState.totalParams + " params written to vst_param_dump.txt\n");
        } else {
            log("ERROR: Could not open param dump file for writing\n");
        }
    } catch (e) {
        log("ERROR writing iterative param dump: " + e + "\n");
    }

    iterativeDumpState.active = false;
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
 * Uses "get -4" message which returns param count from outlet 5 (5th from right)
 */
function getParamCount(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "get", -4);
    log("Requesting param count for slot " + slot + " (get -4)\n");
}

/**
 * Get a specific parameter name by index
 * Individual param names come from "get" with positive index
 */
function getParamName(slot, index) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "get", index);
    log("Requesting param " + index + " info for slot " + slot + "\n");
}

/**
 * Get sub-plugin names from a shell plugin (like WaveShell)
 * Output comes from vst~ outlet 7 (2nd from right)
 */
function getSubNames(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "getsubnames");
    log("Requesting sub-plugin names for slot " + slot + " (check outlet 7)\n");
}

/**
 * Print sub-plugin IDs to Max console (for shell plugins)
 */
function printIds(slot) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "printids");
    log("Printing sub-plugin IDs for slot " + slot + " (check Max console)\n");
}

/**
 * Load a specific sub-plugin inside a shell plugin
 * @param {number} slot - The slot number
 * @param {string} subPluginName - The sub-plugin name or ID
 */
function loadSubPlugin(slot, subPluginName) {
    if (slot < 1 || slot > 8) return;
    outlet(slot - 1, "subname", subPluginName);
    log("Loading sub-plugin '" + subPluginName + "' in slot " + slot + "\n");
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

/**
 * Handle vst~ dump output routed back to us
 * Called via "vstdump <slot> <data...>" message
 *
 * For "params" message, vst~ streams individual parameter names as symbols
 * Each arrives as: vstdump <slot> <paramname>
 */
function vstdump() {
    var args = arrayfromargs(arguments);

    // Debug: log what we received
    post("vstdump received: " + args.join(" ") + "\n");

    if (args.length < 2) return;

    var slot = parseInt(args[0]);
    var data = args.slice(1).join(" ");  // Data might have spaces

    // If we're in param dump mode for this slot, capture the param name
    if (paramDumpState.active && paramDumpState.slot === slot) {
        paramDumpState.currentIndex++;
        paramDumpState.lines.push(paramDumpState.currentIndex + ": " + data);
        paramDumpState.totalParams = paramDumpState.currentIndex;
    }
}

/**
 * Handle param count response from vst~
 * Called via "vstparamcount <slot> <count>" message
 * This receives data from vst~ outlet 4 (int outlet) via prepend vstparamcount
 */
function vstparamcount() {
    var args = arrayfromargs(arguments);
    post("vstparamcount received: " + args.join(" ") + "\n");

    if (args.length < 2) return;

    var slot = parseInt(args[0]);
    var count = parseInt(args[1]);

    log("Slot " + slot + " has " + count + " parameters\n");

    // Route to iterative dump handler if active
    handleParamCountResponse(slot, count);
}

/**
 * Handle param info from vst~ outlet 3 (5th from right - list outlet)
 * Called via "vstparams <slot> <data...>" message
 *
 * This receives data from vst~ outlet 3 after "get" commands:
 * - get -4: returns "-4 <paramcount>"
 * - get <positive_index>: returns "<index> <value>" (just the value, not the name!)
 *
 * Note: Parameter NAMES come from "params" message through outlet 2 (vstdump)
 */
function vstparams() {
    var args = arrayfromargs(arguments);
    // Log raw args with explicit quoting for debugging
    var debugStr = "vstparams raw: [";
    for (var i = 0; i < args.length; i++) {
        debugStr += "'" + args[i] + "'";
        if (i < args.length - 1) debugStr += ", ";
    }
    debugStr += "]";
    log(debugStr + "\n");

    if (args.length < 2) return;

    var slot = parseInt(args[0]);
    var firstVal = parseInt(args[1]);
    log("vstparams: slot=" + slot + ", firstVal=" + firstVal + ", args.length=" + args.length + "\n");

    // Check if this is a param count response (get -4 returns: -4 <count>)
    if (firstVal === -4 && args.length >= 3) {
        var count = parseInt(args[2]);
        log("Slot " + slot + " param count from get -4: " + count + "\n");
        handleParamCountResponse(slot, count);
        return;
    }

    // Otherwise it's a param value response (get <index> returns: <index> <value>)
    // Note: This is just the VALUE, not the name!
    if (iterativeDumpState.active && iterativeDumpState.slot === slot) {
        // We can't get names this way - only values
        // Need to use the params message instead
        log("Got param value, index=" + firstVal + ", but need names from params message\n");
    } else {
        var data = args.slice(1).join(" ");
        log("Slot " + slot + " param info: " + data + "\n");
    }
}

/**
 * Handle param name response from vst~
 * Called via "vstparamname <slot> <index> <name>" message
 */
function vstparamname() {
    var args = arrayfromargs(arguments);
    post("vstparamname received: " + args.join(" ") + "\n");

    if (args.length < 3) return;

    var slot = parseInt(args[0]);
    var index = parseInt(args[1]);
    var name = args.slice(2).join(" ");  // Name might have spaces

    // Route to iterative dump handler if active
    handleParamNameResponse(slot, index, name);
}


/**
 * Write param data to a separate file for cleaner capture
 */
function logParamData(msg) {
    var PARAM_LOG = "/Users/brentpinero/Documents/serum_llm_2/vst_param_dump.txt";
    try {
        var f = new File(PARAM_LOG, "write");
        if (f.isopen) {
            // Seek to end for append
            f.position = f.eof;
            f.writeline(msg);
            f.close();
        }
    } catch (e) {
        post("Param log error: " + e + "\n");
    }
}

/**
 * Handle parameter info from vst~ (param index name value)
 * Called via "vstparam <slot> <index> <name> <value>"
 */
function vstparam() {
    var args = arrayfromargs(arguments);
    if (args.length >= 2) {
        var slot = args[0];
        // Rest is param data - could be "index name value" format
        var paramData = args.slice(1).join(" ");
        log("VST" + slot + " PARAM: " + paramData + "\n");
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
