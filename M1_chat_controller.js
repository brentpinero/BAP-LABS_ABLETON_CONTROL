/**
 * M1 by Bap Labs - Chat Controller
 * AI-powered Serum preset generator with chat interface
 * Manages vst~ communication, Python API bridge, and chat history
 */

autowatch = 1;
inlets = 1;
outlets = 3;

// Serum 2 configuration
var SERUM2_PARAM_COUNT = 2623;
var serum2_loaded = false;

// Chat state
var chat_history = [];
var MAX_CHAT_HISTORY = 10;
var generating = false;
var current_request = null;

// Server status
var server_running = false;
var last_health_check = 0;
var HEALTH_CHECK_INTERVAL = 5000; // 5 seconds

function loadbang() {
    post("🤖 M1 by Bap Labs - Chat Controller initialized\n");

    // Start health check loop
    check_server_health();

    // Verify Serum 2
    var timer = new Task(function() {
        verify_serum2();
    });
    timer.schedule(1000);
}

function verify_serum2() {
    post("🔍 Verifying Serum 2...\n");
    outlet(0, "get", -4); // Request parameter count
}

function check_server_health() {
    outlet(1, "health"); // Request health check from Python bridge

    // Schedule next health check
    var timer = new Task(check_server_health);
    timer.schedule(HEALTH_CHECK_INTERVAL);
}

function send_message() {
    // Get all arguments (the description comes as multiple arguments from route text)
    var args = arrayfromargs(arguments);
    var description = args.join(" ");

    post("🔍 DEBUG: send_message called with: '" + description + "'\n");
    post("🔍 DEBUG: typeof description: " + typeof description + "\n");
    post("🔍 DEBUG: description length: " + (description ? description.length : "null") + "\n");

    if (!description || description === "") {
        outlet(2, "error", "Please enter a description");
        return;
    }

    if (!server_running) {
        outlet(2, "error", "Server offline. Please start the API server.");
        add_chat_message("system", "⚠️ Server offline. Please start the API server.");
        return;
    }

    if (!serum2_loaded) {
        outlet(2, "error", "Serum 2 not loaded");
        add_chat_message("system", "⚠️ Serum 2 not loaded. Please load Serum 2 VST.");
        return;
    }

    if (generating) {
        outlet(2, "error", "Already generating a preset");
        return;
    }

    // Add user message to chat
    add_chat_message("user", description);

    // Show generating status
    generating = true;
    current_request = description;
    outlet(2, "status", "generating");
    add_chat_message("m1", "✨ Generating preset...");

    // Send to Python bridge
    var request = {
        "action": "generate",
        "description": description
    };
    outlet(1, "generate", JSON.stringify(request));
}

function api_response(response_json) {
    try {
        var response = JSON.parse(response_json);

        // Handle health check response
        if (response.server !== undefined) {
            if (response.status === "success" && response.server === "healthy") {
                server_status("healthy");
            } else {
                server_status("offline");
            }
            return;
        }

        // Handle preset generation response
        if (response.status === "success" && response.preset) {
            apply_preset(response.preset);
        } else {
            generating = false;
            outlet(2, "status", "ready");
            var error_msg = response.message || "Generation failed";
            add_chat_message("m1", "❌ " + error_msg);
            outlet(2, "error", error_msg);
        }
    } catch (e) {
        generating = false;
        outlet(2, "status", "ready");
        add_chat_message("m1", "❌ Failed to parse response");
        outlet(2, "error", "Invalid response from server");
        post("Error parsing API response: " + e + "\n");
    }
}

function apply_preset(preset) {
    if (!preset.parameter_changes) {
        generating = false;
        outlet(2, "status", "ready");
        add_chat_message("m1", "❌ No parameters in response");
        return;
    }

    var param_changes = preset.parameter_changes;
    var param_count = param_changes.length;

    post("📊 Applying " + param_count + " parameters...\n");
    outlet(2, "status", "applying");

    // Apply parameters with slight delays
    for (var i = 0; i < param_changes.length; i++) {
        // Use IIFE to capture variables in closure
        (function(param, idx, total) {
            var delay = idx * 50; // 50ms between each

            var timer = new Task(function() {
                // Send to vst~
                post("   → Sending param " + param.index + " = " + param.value + " (" + param.name + ")\n");
                outlet(0, param.index, param.value);

                // Update progress
                var progress = Math.round(((idx + 1) / total) * 100);
                outlet(2, "progress", progress);

                // When complete
                if (idx === total - 1) {
                    generating = false;
                    outlet(2, "status", "ready");

                    // Build success message
                    var critical = preset.critical_changes || [];
                    var success_msg = "✓ Applied " + total + " parameters";
                    if (critical.length > 0) {
                        success_msg += "\n🔑 Key changes: " + critical.join(", ");
                    }

                    add_chat_message("m1", success_msg);
                    outlet(2, "complete", total);
                }
            });

            timer.schedule(delay);
        })(param_changes[i], i, param_changes.length);
    }
}

function add_chat_message(sender, message) {
    var timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    var chat_msg = {
        "sender": sender,
        "message": message,
        "timestamp": timestamp
    };

    chat_history.push(chat_msg);

    // Keep only last MAX_CHAT_HISTORY messages
    if (chat_history.length > MAX_CHAT_HISTORY) {
        chat_history.shift();
    }

    // Send to UI
    outlet(2, "chat_message", JSON.stringify(chat_msg));
}

function clear_chat() {
    chat_history = [];
    outlet(2, "chat_cleared");
}

function get_chat_history() {
    outlet(2, "chat_history", JSON.stringify(chat_history));
}

// Handle responses from vst~ outlet 3 (parameter values)
function list() {
    var args = arrayfromargs(arguments);

    // Parameter count response: [-4, count]
    if (args.length === 2 && args[0] === -4) {
        var count = args[1];
        if (count === SERUM2_PARAM_COUNT) {
            serum2_loaded = true;
            post("✅ Serum 2 loaded (" + count + " parameters)\n");
            outlet(2, "serum_status", 1);
            add_chat_message("system", "✓ Serum 2 ready");
        }
        return;
    }
}

// Handle server health status
function server_status(status) {
    if (status === "healthy") {
        if (!server_running) {
            server_running = true;
            outlet(2, "server_status", 1);
            add_chat_message("system", "✓ M1 server connected");
        }
    } else {
        if (server_running) {
            server_running = false;
            outlet(2, "server_status", 0);
            add_chat_message("system", "⚠️ M1 server disconnected");
        }
    }
}

// Quick preset templates
function quick_bass() {
    send_message("Deep bass with sub frequencies and gentle movement");
}

function quick_lead() {
    send_message("Bright lead synth with harmonics and energy");
}

function quick_pad() {
    send_message("Lush atmospheric pad with slow evolution");
}

function quick_pluck() {
    send_message("Short plucky sound with quick decay");
}

function quick_fx() {
    send_message("Atmospheric sound effect with movement");
}

// Export functions
this.send_message = send_message;
this.clear_chat = clear_chat;
this.get_chat_history = get_chat_history;
this.server_status = server_status;
this.api_response = api_response;
this.quick_bass = quick_bass;
this.quick_lead = quick_lead;
this.quick_pad = quick_pad;
this.quick_pluck = quick_pluck;
this.quick_fx = quick_fx;
