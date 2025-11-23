/**
 * 🎛️ SERUM 2 WORKING CONTROLLER - Based on Diagnostic Results
 * Parameter count: 2,623 (not 2,397!)
 * Responses come from different outlets than expected
 */

autowatch = 1;

// Serum 2 actual specs from testing
var SERUM2_PARAM_COUNT = 2623;
var serum2_loaded = false;
var parameter_names = [];
var current_preset = 1;

function loadbang() {
    post("🎛️ Serum 2 Working Controller initialized\n");
    post("Based on diagnostic testing with confirmed responses\n");
    post("\n");
    post("VERIFIED WORKING COMMANDS:\n");
    post("- params → Get parameter names (outlet 2)\n");
    post("- get -4 → Returns param count: 2,623 (outlet 3)\n");
    post("- get [n] → Get parameter n value (outlet 3)\n");
    post("- pgmnames → List all 128 preset slots (outlet 5)\n");
    post("- open → Open Serum 2 GUI\n");
    post("- [n] [value] → Set parameter n to value\n");
    post("\n");

    // Auto-verify after loading
    var timer = new Task(function() {
        verify_serum2();
    });
    timer.schedule(1000);
}

function verify_serum2() {
    post("\n🔍 VERIFYING SERUM 2 STATUS\n");
    post("============================\n");

    // Get parameter count to verify loading
    outlet(0, "get", -4);

    // Also request first parameter value
    outlet(0, "get", 1);

    post("Requesting parameter count and first value...\n");
}

function discover_params() {
    post("\n🔍 DISCOVERING SERUM 2 PARAMETERS\n");
    post("==================================\n");
    post("Requesting all " + SERUM2_PARAM_COUNT + " parameter names...\n");

    parameter_names = [];
    outlet(0, "params");
}

function test_parameters() {
    post("\n🚀 TESTING SERUM 2 PARAMETER CONTROL\n");
    post("=====================================\n");
    post("Testing parameter control with 1-based indexing\n");

    // Test first 10 parameters
    var test_params = [
        {index: 1, value: 0.7, name: "Parameter 1 (likely Master Volume)"},
        {index: 2, value: 0.5, name: "Parameter 2 (likely OSC A Level)"},
        {index: 3, value: 0.3, name: "Parameter 3 (likely OSC A Pitch)"},
        {index: 10, value: 0.6, name: "Parameter 10"},
        {index: 100, value: 0.4, name: "Parameter 100"},
        {index: 500, value: 0.5, name: "Parameter 500"}
    ];

    for (var i = 0; i < test_params.length; i++) {
        var p = test_params[i];
        var delay = i * 1000;

        var timer = new Task(function(param) {
            post("\n🎛️ Setting " + param.name + "\n");
            post("   Index: " + param.index + ", Value: " + param.value + "\n");

            // Set parameter
            outlet(0, param.index, param.value);

            // Verify after 200ms
            var verify_timer = new Task(function(idx) {
                outlet(0, "get", idx);
            }, param.index);
            verify_timer.schedule(200);

        }, p);
        timer.schedule(delay);
    }
}

function load_preset(preset_num) {
    if (preset_num < 1 || preset_num > 128) {
        post("❌ Preset must be 1-128\n");
        return;
    }

    post("📦 Loading preset " + preset_num + "\n");
    outlet(0, "program", preset_num);
    current_preset = preset_num;
}

function open_gui() {
    post("🖼️ Opening Serum 2 GUI\n");
    outlet(0, "open");
}

function get_all_values() {
    post("\n📊 GETTING FIRST 20 PARAMETER VALUES\n");
    post("====================================\n");

    for (var i = 1; i <= 20; i++) {
        outlet(0, "get", i);
    }
}

// Handle responses from VST~ outlet 3 (parameter values)
function list() {
    var args = arrayfromargs(arguments);

    // Parameter count response: [-4, count]
    if (args.length === 2 && args[0] === -4) {
        var count = args[1];
        post("✅ Serum 2 has " + count + " parameters\n");
        if (count === SERUM2_PARAM_COUNT) {
            serum2_loaded = true;
            post("✅ Serum 2 verified and ready!\n");
        }
        return;
    }

    // Parameter value response: [index, value]
    if (args.length === 2 && typeof args[0] === "number" && args[0] > 0) {
        post("📊 Parameter " + args[0] + " = " + args[1] + "\n");
        return;
    }

    // Other list responses
    post("📡 List response: " + args.join(" ") + "\n");
}

// Handle parameter names from outlet 2
function anything() {
    var msg = messagename;
    var args = arrayfromargs(arguments);

    // Parameter name responses
    if (parameter_names.indexOf(msg) === -1) {
        parameter_names.push(msg);
        post("🎛️ Parameter " + parameter_names.length + ": " + msg + "\n");

        // Show progress every 100 parameters
        if (parameter_names.length % 100 === 0) {
            post("   ...discovered " + parameter_names.length + " parameters\n");
        }

        if (parameter_names.length === SERUM2_PARAM_COUNT) {
            post("\n✅ All " + SERUM2_PARAM_COUNT + " parameters discovered!\n");
        }
    }
}

// Export functions
this.verify_serum2 = verify_serum2;
this.discover_params = discover_params;
this.test_parameters = test_parameters;
this.load_preset = load_preset;
this.open_gui = open_gui;
this.get_all_values = get_all_values;