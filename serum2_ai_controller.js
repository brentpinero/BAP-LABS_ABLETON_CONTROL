/**
 * 🤖 SERUM 2 AI CONTROLLER
 * Connects to local Flask API (http://localhost:8080) to generate Serum presets from text
 * Based on serum2_working_controller.js
 */

autowatch = 1;

// Serum 2 specs
var SERUM2_PARAM_COUNT = 2623;
var API_URL = "http://localhost:8080";

// State
var serum2_loaded = false;
var server_running = false;
var current_description = "";
var applying_preset = false;

function loadbang() {
    post("🤖 Serum 2 AI Controller initialized\n");
    post("Connects to local AI server at " + API_URL + "\n");
    post("\n");
    post("COMMANDS:\n");
    post("- check_server → Verify AI server is running\n");
    post("- generate [description] → Generate preset from text\n");
    post("- verify_serum2 → Check Serum 2 status\n");
    post("\n");

    // Auto-verify after loading
    var timer = new Task(function() {
        verify_serum2();
        check_server();
    });
    timer.schedule(1000);
}

function verify_serum2() {
    post("\n🔍 VERIFYING SERUM 2 STATUS\n");
    post("============================\n");

    // Get parameter count to verify loading
    outlet(0, "get", -4);
    post("Requesting parameter count...\n");
}

function check_server() {
    post("\n🔍 CHECKING AI SERVER\n");
    post("=====================\n");

    var url = API_URL + "/health";
    post("Checking: " + url + "\n");

    // Use Max's ajax object to check health endpoint
    // Note: We'll need to connect this via [ajax] object in the patcher
    outlet(1, "health_check", url);
}

function generate() {
    var args = arrayfromargs(arguments);
    current_description = args.join(" ");

    if (!current_description) {
        post("❌ No description provided\n");
        return;
    }

    if (!server_running) {
        post("❌ AI server not running. Make sure SerumAI.app is running.\n");
        return;
    }

    if (!serum2_loaded) {
        post("❌ Serum 2 not loaded. Load Serum 2 VST first.\n");
        return;
    }

    post("\n🎨 GENERATING PRESET FROM AI\n");
    post("=============================\n");
    post("Description: " + current_description + "\n");

    // Send request to Flask API via [ajax] object
    var request_data = {
        "description": current_description
    };

    outlet(1, "generate", JSON.stringify(request_data));
}

function apply_preset(json_response) {
    post("\n🎛️ APPLYING AI-GENERATED PRESET\n");
    post("================================\n");

    try {
        var preset = JSON.parse(json_response);

        if (!preset.parameter_changes) {
            post("❌ Invalid response: missing parameter_changes\n");
            return;
        }

        var param_changes = preset.parameter_changes;
        post("Applying " + param_changes.length + " parameter changes...\n");

        applying_preset = true;

        // Apply each parameter with slight delays to prevent overwhelming VST
        for (var i = 0; i < param_changes.length; i++) {
            var param = param_changes[i];
            var delay = i * 50; // 50ms between each parameter

            var timer = new Task(function(p, idx, total) {
                // Set parameter
                outlet(0, p.index, p.value);

                post("   [" + (idx + 1) + "/" + total + "] " + p.name + " → " + p.value.toFixed(3) + "\n");

                // Mark complete when done
                if (idx === total - 1) {
                    applying_preset = false;
                    post("\n✅ Preset applied successfully!\n");

                    // Output critical changes for UI display
                    if (preset.critical_changes) {
                        post("🔑 Critical changes: " + preset.critical_changes.join(", ") + "\n");
                        outlet(2, "critical_changes", preset.critical_changes.join(", "));
                    }
                }
            }, param, i, param_changes.length);

            timer.schedule(delay);
        }

    } catch (e) {
        post("❌ Failed to parse JSON response: " + e + "\n");
        applying_preset = false;
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
            outlet(2, "serum_status", "ready");
        }
        return;
    }

    // Parameter value response: [index, value]
    if (args.length === 2 && typeof args[0] === "number" && args[0] > 0) {
        if (!applying_preset) {
            post("📊 Parameter " + args[0] + " = " + args[1] + "\n");
        }
        return;
    }
}

// Handle server responses
function server_status(status) {
    if (status === "healthy") {
        server_running = true;
        post("✅ AI server is running\n");
        outlet(2, "server_status", "running");
    } else {
        server_running = false;
        post("❌ AI server not responding\n");
        outlet(2, "server_status", "down");
    }
}

// Handle error from ajax
function error(msg) {
    post("❌ Error: " + msg + "\n");
    server_running = false;
    outlet(2, "server_status", "error");
}

// Export functions
this.verify_serum2 = verify_serum2;
this.check_server = check_server;
this.generate = generate;
this.apply_preset = apply_preset;
this.server_status = server_status;
this.error = error;
