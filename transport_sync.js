/**
 * transport_sync.js - Live Transport State Reader for Mix Analysis Hub
 *
 * Reads transport state from Ableton Live via Live Object Model (LOM)
 * and outputs via OSC for bar-accurate context tracking.
 *
 * Outlets:
 *   0: Transport data list [playing, bpm, bar, beat, song_length_bars]
 *   1: Bar change bang (fires when bar number changes)
 *   2: Status messages
 *
 * Author: BAP Labs
 */

autowatch = 1;
inlets = 1;
outlets = 3;

// Live API objects
var live_set = null;
var last_bar = -1;
var initialized = false;

/**
 * Initialize Live API connection
 */
function init() {
    try {
        live_set = new LiveAPI("live_set");

        if (live_set.id == 0) {
            outlet(2, "error", "Could not connect to Live - is this running in M4L?");
            return;
        }

        initialized = true;
        outlet(2, "status", "Connected to Live");

        // Initial read
        bang();

    } catch (e) {
        outlet(2, "error", "Init failed: " + e.message);
    }
}

/**
 * Read and output current transport state
 */
function bang() {
    if (!initialized) {
        init();
        if (!initialized) return;
    }

    try {
        // Read transport values
        var is_playing = live_set.get("is_playing")[0];
        var tempo = live_set.get("tempo")[0];
        var current_time = live_set.get("current_song_time")[0];  // in beats
        var song_length = live_set.get("song_length")[0];  // in beats
        var time_sig_num = live_set.get("signature_numerator")[0];
        var time_sig_den = live_set.get("signature_denominator")[0];

        // Calculate bar and beat (0-indexed bars)
        var beats_per_bar = time_sig_num;
        var current_bar = Math.floor(current_time / beats_per_bar);
        var current_beat = current_time % beats_per_bar;
        var song_length_bars = Math.ceil(song_length / beats_per_bar);

        // Output transport data
        outlet(0, is_playing ? 1 : 0, tempo, current_bar, current_beat, song_length_bars, time_sig_num, time_sig_den);

        // Check for bar change
        if (current_bar !== last_bar) {
            outlet(1, "bang");  // Bar changed
            last_bar = current_bar;
        }

    } catch (e) {
        outlet(2, "error", "Read failed: " + e.message);
    }
}

/**
 * Get selected track info for focus tracking
 */
function get_focus() {
    if (!initialized) {
        init();
        if (!initialized) return;
    }

    try {
        var view = new LiveAPI("live_set view");
        var selected_track = new LiveAPI("live_set view selected_track");

        if (selected_track.id == 0) {
            outlet(2, "focus", "No track selected");
            return;
        }

        var track_name = selected_track.get("name")[0];
        var track_index = selected_track.get("index")[0] || 0;
        var is_foldable = selected_track.get("is_foldable")[0];
        var is_grouped = selected_track.get("is_grouped")[0];
        var has_midi_input = selected_track.get("has_midi_input")[0];

        // Determine track type
        var track_type = "audio";
        if (has_midi_input) track_type = "midi";
        if (is_foldable) track_type = "group";

        // Check if master or return
        var master = new LiveAPI("live_set master_track");
        if (selected_track.id == master.id) {
            track_type = "master";
        }

        outlet(2, "focus", track_name, track_index, track_type, is_grouped ? 1 : 0);

    } catch (e) {
        outlet(2, "error", "Focus read failed: " + e.message);
    }
}

/**
 * Get loop brace info
 */
function get_loop() {
    if (!initialized) {
        init();
        if (!initialized) return;
    }

    try {
        var loop_on = live_set.get("loop")[0];
        var loop_start = live_set.get("loop_start")[0];  // beats
        var loop_length = live_set.get("loop_length")[0];  // beats
        var time_sig_num = live_set.get("signature_numerator")[0];

        var loop_start_bar = Math.floor(loop_start / time_sig_num);
        var loop_end_bar = Math.floor((loop_start + loop_length) / time_sig_num);

        outlet(2, "loop", loop_on ? 1 : 0, loop_start_bar, loop_end_bar);

    } catch (e) {
        outlet(2, "error", "Loop read failed: " + e.message);
    }
}

/**
 * Get cue points (locators)
 */
function get_cues() {
    if (!initialized) {
        init();
        if (!initialized) return;
    }

    try {
        var cue_points = live_set.get("cue_points");
        var time_sig_num = live_set.get("signature_numerator")[0];

        // cue_points returns "id X id Y id Z..."
        var cue_list = [];
        for (var i = 1; i < cue_points.length; i += 2) {
            var cue_id = cue_points[i];
            var cue = new LiveAPI("id " + cue_id);
            var cue_name = cue.get("name")[0];
            var cue_time = cue.get("time")[0];  // beats
            var cue_bar = Math.floor(cue_time / time_sig_num);
            cue_list.push(cue_name + ":" + cue_bar);
        }

        outlet(2, "cues", cue_list.join(","));

    } catch (e) {
        outlet(2, "error", "Cue read failed: " + e.message);
    }
}

// Initialize on load
function loadbang() {
    init();
}
