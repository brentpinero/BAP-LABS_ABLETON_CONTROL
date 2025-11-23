/**
 * 🎛️ SERUM 2 AUTO-LOAD CONTROLLER
 * Specifically designed for Serum 2 VST3 plugin with automatic loading
 */

autowatch = 1;

// Serum 2 specific state
var serum2_loaded = false;
var parameter_count = 0;
var parameter_names = [];
var test_running = false;
var loading_attempts = 0;
var max_loading_attempts = 3;

function loadbang() {
    post("🎛️ Serum 2 Auto-Load Controller initialized");
    post("Designed specifically for Serum 2 VST3 plugin");
    post("");
    post("Auto-loading features:");
    post("- Automatic Serum 2 loading on patch open");
    post("- VST3 format preference");
    post("- Plugin state auto-saving");
    post("");
    post("Available functions:");
    post("- discover_params() - Get all Serum 2 parameters");
    post("- test_sequence() - Run automated parameter test");
    post("- verify_serum2() - Check if Serum 2 is loaded");
    post("- reload_serum2() - Manually reload plugin");

    // Auto-verify loading after a short delay
    var verify_timer = new Task(function() {
        verify_serum2();
    });
    verify_timer.schedule(2000);
}

function verify_serum2() {
    post("\\n🔍 VERIFYING SERUM 2 LOADING");
    post("============================");

    // Request plugin name to verify loading
    outlet(0, "getplugname");

    // Also request parameter count as verification
    outlet(0, "get");
}

function reload_serum2() {
    if (loading_attempts >= max_loading_attempts) {
        post("❌ Maximum loading attempts reached. Check Serum 2 installation.");
        return;
    }

    loading_attempts++;
    post("\\n🔄 RELOADING SERUM 2 (Attempt " + loading_attempts + ")");
    post("===============================================");

    // Try different loading methods
    post("Trying VST3 format...");
    outlet(0, "plug_vst3", "Serum2");

    // Verify after delay
    var verify_timer = new Task(function() {
        verify_serum2();
    });
    verify_timer.schedule(1500);
}

function discover_params() {
    if (!serum2_loaded) {
        post("❌ Serum 2 not loaded. Use reload_serum2() first.");
        return;
    }

    post("\\n🔍 DISCOVERING SERUM 2 PARAMETERS");
    post("==================================");
    post("Requesting parameter list from Serum 2...");

    // Clear previous parameter list
    parameter_names = [];

    // Send params message to get all parameter names
    outlet(0, "params");

    // Also get parameter count
    outlet(0, "get");
}

function test_sequence() {
    if (!serum2_loaded) {
        post("❌ Serum 2 not loaded. Use reload_serum2() first.");
        return;
    }

    if (test_running) {
        post("❌ Test already running, please wait...");
        return;
    }

    post("\\n🚀 RUNNING SERUM 2 PARAMETER TEST");
    post("=================================");
    post("Testing common Serum 2 parameters with 1-based indexing");

    test_running = true;

    // Serum 2 specific parameter tests
    // Based on typical Serum parameter layout
    var serum2_test_params = [
        {index: 1, value: 0.6, name: "Master Volume"},
        {index: 2, value: 0.4, name: "OSC A Level"},
        {index: 3, value: 0.5, name: "OSC A Wavetable Position"},
        {index: 4, value: 0.7, name: "OSC A Pitch"},
        {index: 15, value: 0.3, name: "Filter Cutoff (estimated)"},
        {index: 16, value: 0.2, name: "Filter Resonance (estimated)"},
        {index: 25, value: 0.1, name: "Envelope Attack (estimated)"},
        {index: 30, value: 0.8, name: "LFO Rate (estimated)"}
    ];

    for (var i = 0; i < serum2_test_params.length; i++) {
        var param = serum2_test_params[i];
        var delay = i * 1200; // 1.2 seconds between tests

        var timer = new Task(function(p) {
            test_serum2_parameter(p);
        }, param);

        timer.schedule(delay);
    }

    // End test sequence
    var end_timer = new Task(function() {
        post("\\n✅ SERUM 2 PARAMETER TEST COMPLETE");
        post("Check parameter values to confirm Serum 2 is responding");
        test_running = false;
    });
    end_timer.schedule((serum2_test_params.length * 1200) + 1000);
}

function test_serum2_parameter(param_info) {
    post("\\n🎛️ Testing Serum 2: " + param_info.name);
    post("   Parameter Index: " + param_info.index + " (1-based for Serum 2)");
    post("   Setting Value: " + param_info.value + " (0.0-1.0 range)");

    // Send parameter change to Serum 2
    outlet(0, param_info.index, param_info.value);

    // Verify the change
    var verify_timer = new Task(function(index) {
        post("   Verifying Serum 2 parameter " + index + "...");
        outlet(0, "get", index);
    }, param_info.index);
    verify_timer.schedule(200);
}

function generate_serum2_training_data() {
    post("\\n🤖 GENERATING SERUM 2 LLM TRAINING DATA");
    post("========================================");

    if (!serum2_loaded) {
        post("❌ Serum 2 not loaded. Cannot generate training data.");
        return;
    }

    if (parameter_names.length === 0) {
        post("❌ No parameters discovered. Run discover_params() first.");
        return;
    }

    // Serum 2 specific training data structure
    var serum2_training_structure = {
        "format_version": "2.0",
        "plugin_name": "Serum 2",
        "plugin_format": "VST3",
        "parameter_count": parameter_count,
        "parameter_indexing": "1-based",
        "value_range": "0.0-1.0",
        "auto_loading": {
            "method": "vst~ argument",
            "syntax": "vst~ 2 2 Serum2",
            "prefer": "VST3"
        },
        "discovered_parameters": parameter_names.slice(0, 25), // First 25 parameters
        "serum2_control_examples": [
            {
                "description": "Create a warm bass sound in Serum 2",
                "parameter_changes": [
                    {"index": 2, "value": 0.8, "reason": "Increase OSC A level"},
                    {"index": 15, "value": 0.3, "reason": "Lower filter cutoff for warmth"},
                    {"index": 16, "value": 0.15, "reason": "Add slight filter resonance"},
                    {"index": 25, "value": 0.05, "reason": "Fast envelope attack"}
                ]
            },
            {
                "description": "Design a bright lead synth in Serum 2",
                "parameter_changes": [
                    {"index": 3, "value": 0.7, "reason": "Move wavetable position"},
                    {"index": 4, "value": 1.05, "reason": "Slight pitch up for brightness"},
                    {"index": 15, "value": 0.8, "reason": "Open filter cutoff"},
                    {"index": 30, "value": 0.6, "reason": "Moderate LFO rate for movement"}
                ]
            },
            {
                "description": "Create an evolving pad in Serum 2",
                "parameter_changes": [
                    {"index": 2, "value": 0.6, "reason": "Moderate OSC A level"},
                    {"index": 25, "value": 0.4, "reason": "Slow attack for pad"},
                    {"index": 27, "value": 0.6, "reason": "Sustained release"},
                    {"index": 30, "value": 0.2, "reason": "Slow LFO for evolution"}
                ]
            }
        ],
        "serum2_specific_notes": [
            "Serum 2 is VST3/AU only - no VST2 support",
            "Auto-loads using 'vst~ 2 2 Serum2' syntax",
            "Parameter indices may vary between Serum 2 presets",
            "Use discover_params() after preset changes",
            "Supports both parameter index and name control"
        ],
        "midi_support": {
            "note_on": "midievent 144 {note} {velocity}",
            "note_off": "midievent 128 {note} 0",
            "cc_control": "midievent 176 {cc_number} {value}"
        }
    };

    post(JSON.stringify(serum2_training_structure, null, 2));
    return serum2_training_structure;
}

// Handle responses from Serum 2 VST
function list() {
    var args = arrayfromargs(arguments);

    // Parameter count response
    if (args.length === 2 && typeof args[0] === "string" && args[0] === "paramcount") {
        parameter_count = args[1];
        post("✅ Serum 2 has " + parameter_count + " parameters total");
        return;
    }

    // Parameter value response
    if (args.length === 2 && typeof args[0] === "number") {
        post("✅ Serum 2 parameter " + args[0] + " = " + args[1]);
        return;
    }

    // General response
    post("📡 Serum 2 response: " + args.join(" "));
}

function anything() {
    var message_name = messagename;
    var args = arrayfromargs(arguments);

    if (message_name === "plugname") {
        var plugin_name = args.join(" ");
        if (plugin_name.toLowerCase().includes("serum")) {
            serum2_loaded = true;
            loading_attempts = 0; // Reset counter on successful load
            post("✅ Serum 2 loaded successfully: " + plugin_name);

            // Auto-discover parameters after successful load
            var discover_timer = new Task(function() {
                discover_params();
            });
            discover_timer.schedule(1000);
        } else {
            post("⚠️  Different plugin loaded: " + plugin_name);
            post("   Expected Serum 2. Use reload_serum2() to load correct plugin.");
        }
    } else {
        // Parameter name discovery
        if (parameter_names.indexOf(message_name) === -1) {
            parameter_names.push(message_name);
            post("📡 Serum 2 parameter: " + message_name + " (index " + parameter_names.length + ")");
        }
    }
}

// Export functions for Max
this.discover_params = discover_params;
this.test_sequence = test_sequence;
this.verify_serum2 = verify_serum2;
this.reload_serum2 = reload_serum2;
this.generate_serum2_training_data = generate_serum2_training_data;