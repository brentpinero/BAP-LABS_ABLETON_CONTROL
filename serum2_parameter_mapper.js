/**
 * 🎛️ SERUM 2 PARAMETER MAPPER
 * Maps all 2,623 parameter names to their indices
 * This is THE critical piece for LLM control
 */

autowatch = 1;

// Global state
var SERUM2_PARAM_COUNT = 2623;
var parameter_map = {};  // name -> index mapping
var index_to_name = {};  // index -> name mapping
var discovery_complete = false;
var current_discovery_index = 0;
var discovery_in_progress = false;

// Storage for organized parameters
var organized_params = {
    oscillators: {},
    filters: {},
    envelopes: {},
    lfos: {},
    effects: {},
    matrix: {},
    global: {},
    unknown: {}
};

function loadbang() {
    post("🎛️ SERUM 2 PARAMETER MAPPER\n");
    post("================================\n");
    post("This will map all 2,623 parameter names to indices\n");
    post("\n");
    post("Commands:\n");
    post("- start_discovery() - Begin mapping all parameters\n");
    post("- save_mapping() - Save to JSON file\n");
    post("- test_param('Filter Cutoff') - Test a specific parameter\n");
    post("- show_categories() - Show organized parameters\n");
    post("\n");
}

function start_discovery() {
    if (discovery_in_progress) {
        post("⚠️ Discovery already in progress...\n");
        return;
    }

    post("\n🚀 STARTING PARAMETER DISCOVERY\n");
    post("================================\n");
    post("This will take a few seconds to map all 2,623 parameters...\n");

    discovery_in_progress = true;
    parameter_map = {};
    index_to_name = {};
    current_discovery_index = 0;

    // First, request all parameter names
    outlet(0, "params");

    // After getting names, we'll need to test each parameter
    // to build the index mapping
    post("Requesting parameter names from Serum 2...\n");
}

// This receives parameter names from outlet 2
function anything() {
    var param_name = messagename;
    var args = arrayfromargs(arguments);

    // Skip if we've seen this parameter
    if (parameter_map[param_name] !== undefined) {
        return;
    }

    // Increment discovery index
    current_discovery_index++;

    // Store the mapping
    parameter_map[param_name] = current_discovery_index;
    index_to_name[current_discovery_index] = param_name;

    // Categorize the parameter
    categorize_parameter(param_name, current_discovery_index);

    // Progress indicator
    if (current_discovery_index % 100 === 0) {
        post("📊 Mapped " + current_discovery_index + " parameters...\n");
    }

    // Check if complete (with some flexibility for the exact count)
    if (current_discovery_index >= SERUM2_PARAM_COUNT - 10) {
        discovery_complete = true;
        discovery_in_progress = false;
        post("\n✅ DISCOVERY COMPLETE!\n");
        post("Mapped " + current_discovery_index + " parameters\n");
        show_summary();
    }
}

function categorize_parameter(name, index) {
    var lower_name = name.toLowerCase();

    // Categorize based on parameter name
    if (lower_name.indexOf("osc") !== -1 ||
        lower_name.indexOf("oscillator") !== -1 ||
        lower_name.indexOf("wt") !== -1 ||
        lower_name.indexOf("wavetable") !== -1) {
        organized_params.oscillators[name] = index;
    }
    else if (lower_name.indexOf("filter") !== -1 ||
             lower_name.indexOf("cutoff") !== -1 ||
             lower_name.indexOf("resonance") !== -1) {
        organized_params.filters[name] = index;
    }
    else if (lower_name.indexOf("env") !== -1 ||
             lower_name.indexOf("attack") !== -1 ||
             lower_name.indexOf("decay") !== -1 ||
             lower_name.indexOf("sustain") !== -1 ||
             lower_name.indexOf("release") !== -1) {
        organized_params.envelopes[name] = index;
    }
    else if (lower_name.indexOf("lfo") !== -1) {
        organized_params.lfos[name] = index;
    }
    else if (lower_name.indexOf("fx") !== -1 ||
             lower_name.indexOf("effect") !== -1 ||
             lower_name.indexOf("reverb") !== -1 ||
             lower_name.indexOf("delay") !== -1 ||
             lower_name.indexOf("chorus") !== -1 ||
             lower_name.indexOf("distortion") !== -1 ||
             lower_name.indexOf("compressor") !== -1) {
        organized_params.effects[name] = index;
    }
    else if (lower_name.indexOf("matrix") !== -1 ||
             lower_name.indexOf("mod") !== -1 ||
             lower_name.indexOf("source") !== -1 ||
             lower_name.indexOf("dest") !== -1) {
        organized_params.matrix[name] = index;
    }
    else if (lower_name.indexOf("master") !== -1 ||
             lower_name.indexOf("volume") !== -1 ||
             lower_name.indexOf("pan") !== -1 ||
             lower_name.indexOf("global") !== -1) {
        organized_params.global[name] = index;
    }
    else {
        organized_params.unknown[name] = index;
    }
}

function show_summary() {
    post("\n📊 PARAMETER CATEGORIES\n");
    post("======================\n");
    post("Oscillators: " + Object.keys(organized_params.oscillators).length + " parameters\n");
    post("Filters: " + Object.keys(organized_params.filters).length + " parameters\n");
    post("Envelopes: " + Object.keys(organized_params.envelopes).length + " parameters\n");
    post("LFOs: " + Object.keys(organized_params.lfos).length + " parameters\n");
    post("Effects: " + Object.keys(organized_params.effects).length + " parameters\n");
    post("Matrix: " + Object.keys(organized_params.matrix).length + " parameters\n");
    post("Global: " + Object.keys(organized_params.global).length + " parameters\n");
    post("Unknown: " + Object.keys(organized_params.unknown).length + " parameters\n");
}

function show_categories() {
    post("\n🎛️ KEY SERUM 2 PARAMETERS\n");
    post("=========================\n");

    // Show first 5 from each category
    var categories = ["oscillators", "filters", "envelopes", "lfos", "effects"];

    for (var i = 0; i < categories.length; i++) {
        var cat = categories[i];
        var params = organized_params[cat];
        var keys = Object.keys(params);

        post("\n" + cat.toUpperCase() + ":\n");
        for (var j = 0; j < Math.min(5, keys.length); j++) {
            var name = keys[j];
            var index = params[name];
            post("  [" + index + "] " + name + "\n");
        }
        if (keys.length > 5) {
            post("  ... and " + (keys.length - 5) + " more\n");
        }
    }
}

function test_param(param_name) {
    if (!discovery_complete) {
        post("❌ Run start_discovery() first!\n");
        return;
    }

    var index = parameter_map[param_name];
    if (index === undefined) {
        post("❌ Parameter '" + param_name + "' not found\n");
        post("Try similar names:\n");

        // Find similar parameter names
        var similar = find_similar(param_name);
        for (var i = 0; i < Math.min(5, similar.length); i++) {
            post("  - " + similar[i] + " [" + parameter_map[similar[i]] + "]\n");
        }
        return;
    }

    post("✅ Found: '" + param_name + "' = index " + index + "\n");
    post("Getting current value...\n");
    outlet(0, "get", index);

    post("Setting to 0.5...\n");
    outlet(0, index, 0.5);

    // Verify after 200ms
    var timer = new Task(function() {
        outlet(0, "get", index);
    });
    timer.schedule(200);
}

function find_similar(search_term) {
    var results = [];
    var search_lower = search_term.toLowerCase();

    for (var param_name in parameter_map) {
        if (param_name.toLowerCase().indexOf(search_lower) !== -1) {
            results.push(param_name);
        }
    }

    return results;
}

function force_complete() {
    post("🔧 FORCING DISCOVERY COMPLETE\n");
    post("Current parameter count: " + current_discovery_index + "\n");
    discovery_complete = true;
    discovery_in_progress = false;
    show_summary();
}

function save_mapping() {
    if (!discovery_complete && current_discovery_index === 0) {
        post("❌ No parameters discovered! Run start_discovery() first\n");
        return;
    }

    // Allow saving if we have any parameters
    if (current_discovery_index > 0) {
        discovery_complete = true;
    }

    post("\n💾 SAVING PARAMETER MAPPING\n");
    post("==========================\n");

    var output = {
        "plugin": "Serum 2",
        "parameter_count": SERUM2_PARAM_COUNT,
        "mapping_version": "1.0",
        "discovery_date": new Date().toISOString(),
        "parameter_map": parameter_map,
        "index_to_name": index_to_name,
        "organized": organized_params,
        "critical_parameters": {
            "master_volume": parameter_map["Master Volume"] || null,
            "osc_a_level": parameter_map["OSC A Level"] || null,
            "osc_a_pitch": parameter_map["OSC A Pitch"] || null,
            "osc_b_level": parameter_map["OSC B Level"] || null,
            "osc_b_pitch": parameter_map["OSC B Pitch"] || null,
            "filter_cutoff": find_filter_cutoff(),
            "filter_resonance": find_filter_resonance(),
            "amp_attack": find_amp_attack(),
            "amp_decay": find_amp_decay(),
            "amp_sustain": find_amp_sustain(),
            "amp_release": find_amp_release()
        }
    };

    // Output as JSON
    post("\n" + JSON.stringify(output, null, 2) + "\n");
    post("\n✅ Copy this JSON and save as 'serum2_parameter_mapping.json'\n");

    return output;
}

function find_filter_cutoff() {
    var candidates = ["Filter Cutoff", "Cutoff", "Filter 1 Cutoff", "Filter A Cutoff"];
    for (var i = 0; i < candidates.length; i++) {
        if (parameter_map[candidates[i]] !== undefined) {
            return parameter_map[candidates[i]];
        }
    }
    return null;
}

function find_filter_resonance() {
    var candidates = ["Filter Resonance", "Resonance", "Filter 1 Resonance", "Filter Res"];
    for (var i = 0; i < candidates.length; i++) {
        if (parameter_map[candidates[i]] !== undefined) {
            return parameter_map[candidates[i]];
        }
    }
    return null;
}

function find_amp_attack() {
    var candidates = ["Amp Attack", "Attack", "Env 1 Attack", "Amplitude Attack"];
    for (var i = 0; i < candidates.length; i++) {
        if (parameter_map[candidates[i]] !== undefined) {
            return parameter_map[candidates[i]];
        }
    }
    return null;
}

function find_amp_decay() {
    var candidates = ["Amp Decay", "Decay", "Env 1 Decay", "Amplitude Decay"];
    for (var i = 0; i < candidates.length; i++) {
        if (parameter_map[candidates[i]] !== undefined) {
            return parameter_map[candidates[i]];
        }
    }
    return null;
}

function find_amp_sustain() {
    var candidates = ["Amp Sustain", "Sustain", "Env 1 Sustain", "Amplitude Sustain"];
    for (var i = 0; i < candidates.length; i++) {
        if (parameter_map[candidates[i]] !== undefined) {
            return parameter_map[candidates[i]];
        }
    }
    return null;
}

function find_amp_release() {
    var candidates = ["Amp Release", "Release", "Env 1 Release", "Amplitude Release"];
    for (var i = 0; i < candidates.length; i++) {
        if (parameter_map[candidates[i]] !== undefined) {
            return parameter_map[candidates[i]];
        }
    }
    return null;
}

// Handle parameter value responses from outlet 3
function list() {
    var args = arrayfromargs(arguments);

    if (args.length === 2 && typeof args[0] === "number" && args[0] > 0) {
        var index = args[0];
        var value = args[1];
        var name = index_to_name[index] || "Unknown";
        post("📊 [" + index + "] " + name + " = " + value + "\n");
    }
}

// Export functions
this.start_discovery = start_discovery;
this.save_mapping = save_mapping;
this.test_param = test_param;
this.show_categories = show_categories;
this.find_similar = find_similar;
this.force_complete = force_complete;