// sub_follower.js — the offline brain of the BAP Labs Sub Follower device.
//
// The Sub Follower makes one Serum sub track play a mono line derived from every MIDI
// track in the bass group, folded into one sub-friendly octave. NOTES NEVER PASS
// THROUGH THIS FILE: [js] runs on Max's low-priority thread, so the live note path
// (gate -> lowest-note priority -> octave fold) is built from plain Max objects in the
// patch. This script only does work that is not timing-critical:
//   * AUTO OCTAVE — score every candidate fold floor against the bass notes and pick
//     the one that keeps the sub in its sweet spot with the fewest octave jumps.
//   * SLOT BOOKKEEPING — keep each source track on the same Follow switch across
//     reloads, so automation on "Follow 3" keeps meaning the same track.
//
// Everything below is pure (no LiveAPI) and exported for Node tests
// (node --test test_sub_follower.js). The LiveAPI glue that discovers the bass group
// and routes sources is added once the MIDI DeviceIO gate probe
// (probe_device_midi_io.py) has picked the device shape.

autowatch = 0;      // dev-only; a byte-wrapped .amxd has no project to resolve it against
inlets = 1;
outlets = 1;

// Sub sweet spot in MIDI numbers (Ableton names 60 "C3", so 28 = E0 = 41.2 Hz and
// 38 = D1 = 73.4 Hz). Mixing guidance puts sub fundamentals around 40-60 Hz and warns
// below ~40 Hz; these are tunable defaults, not hard rules.
var BAND_LO = 28;
var BAND_HI = 38;
var FLOOR_MIN = 24;         // candidate fold floors: C0 (32.7 Hz) ..
var FLOOR_MAX = 31;         // .. G0 (49.0 Hz)
var W_RANGE = 1.0;          // weight: time spent outside the sweet spot
var W_JUMP = 0.5;           // weight: melodic steps the fold turns into octave leaps
var EPS = 1e-6;

var NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

// Fold any pitch into the one-octave window [floor, floor + 11].
function fold(pitch, floor) {
    return floor + (((pitch - floor) % 12) + 12) % 12;
}

function noteHz(pitch) {
    return 440 * Math.pow(2, (pitch - 69) / 12);
}

// Ableton's naming: MIDI 60 is C3.
function noteName(pitch) {
    return NOTE_NAMES[((pitch % 12) + 12) % 12] + (Math.floor(pitch / 12) - 2);
}

// Reduce overlapping notes from all sources to the mono line the device plays:
// at every moment the LOWEST sounding pitch wins (same rule as the patch).
// notes: [{pitch, start, duration}] in absolute beats. Returns [{pitch, start, duration}]
// with adjacent same-pitch segments merged.
function monoLine(notes) {
    var times = [], i;
    for (i = 0; i < notes.length; i++) {
        if (notes[i].duration > EPS) {
            times.push(notes[i].start, notes[i].start + notes[i].duration);
        }
    }
    times.sort(function (a, b) { return a - b; });

    var line = [];
    for (i = 0; i + 1 < times.length; i++) {
        var t0 = times[i], t1 = times[i + 1];
        if (t1 - t0 <= EPS) continue;
        var low = -1;
        for (var j = 0; j < notes.length; j++) {
            var n = notes[j];
            if (n.start <= t0 + EPS && n.start + n.duration >= t1 - EPS &&
                (low < 0 || n.pitch < low)) {
                low = n.pitch;
            }
        }
        if (low < 0) continue;                        // silence between notes
        var last = line[line.length - 1];
        if (last && last.pitch === low && Math.abs(last.start + last.duration - t0) <= EPS) {
            last.duration = t1 - last.start;
        } else {
            line.push({ pitch: low, start: t0, duration: t1 - t0 });
        }
    }
    return line;
}

// Cost of one fold floor for a mono line. Lower is better.
//   rangeCost: duration-weighted semitones outside [BAND_LO, BAND_HI], per beat.
//   jumpCost:  share of note-to-note moves where the folded interval is not the
//              shortest way between the two pitch classes (the fold seam turned a
//              step into a leap).
function scoreFloor(line, floor) {
    var total = 0, outside = 0, moves = 0, jumps = 0;
    for (var i = 0; i < line.length; i++) {
        var p = fold(line[i].pitch, floor);
        total += line[i].duration;
        if (p < BAND_LO) outside += (BAND_LO - p) * line[i].duration;
        else if (p > BAND_HI) outside += (p - BAND_HI) * line[i].duration;
        if (i > 0) {
            var prev = fold(line[i - 1].pitch, floor);
            if (p !== prev) {
                moves++;
                if (Math.abs(p - prev) > 6) jumps++;   // a tritone either way is no leap
            }
        }
    }
    var rangeCost = total > 0 ? outside / total : 0;
    var jumpCost = moves > 0 ? jumps / moves : 0;
    return {
        floor: floor, rangeCost: rangeCost, jumpCost: jumpCost,
        cost: W_RANGE * rangeCost + W_JUMP * jumpCost
    };
}

// Pick the best fold floor for the given source notes. Ties go to the floor nearest
// the bottom of the sweet spot. Returns {floor, scores} (scores for every candidate).
function chooseFloor(notes) {
    var line = monoLine(notes), scores = [], best = null;
    for (var f = FLOOR_MIN; f <= FLOOR_MAX; f++) {
        var s = scoreFloor(line, f);
        scores.push(s);
        if (best === null || s.cost < best.cost - EPS ||
            (Math.abs(s.cost - best.cost) <= EPS &&
             Math.abs(f - BAND_LO) < Math.abs(best.floor - BAND_LO))) {
            best = s;
        }
    }
    return { floor: best.floor, scores: scores };
}

// Keep sources on stable Follow switches.
//   prev:   array of nSlots entries, each a track id or null (the stored mapping)
//   tracks: track ids currently in the bass group, in session order
// Tracks keep their slot, vanished tracks free theirs, new tracks take the lowest free
// slot. Returns {slots, overflow}; overflow lists tracks that did not fit.
function assignSlots(prev, tracks, nSlots) {
    var slots = [], overflow = [], i, t;
    for (i = 0; i < nSlots; i++) {
        var keep = prev && prev[i] !== undefined && prev[i] !== null &&
                   tracks.indexOf(prev[i]) !== -1 && slots.indexOf(prev[i]) === -1;
        slots.push(keep ? prev[i] : null);
    }
    for (t = 0; t < tracks.length; t++) {
        if (slots.indexOf(tracks[t]) !== -1) continue;
        var free = slots.indexOf(null);
        if (free === -1) overflow.push(tracks[t]);
        else slots[free] = tracks[t];
    }
    return { slots: slots, overflow: overflow };
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        fold: fold, noteHz: noteHz, noteName: noteName, monoLine: monoLine,
        scoreFloor: scoreFloor, chooseFloor: chooseFloor, assignSlots: assignSlots,
        BAND_LO: BAND_LO, BAND_HI: BAND_HI, FLOOR_MIN: FLOOR_MIN, FLOOR_MAX: FLOOR_MAX
    };
}
