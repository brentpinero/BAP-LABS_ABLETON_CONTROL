// track_ears.js — the addressing brain for the per-track Mix Analysis Hub device.
//
// One device sits on every track/group/master. The patch DSP computes levels /
// stereo / a 7-band spectrum and feeds the raw numbers here as tagged messages.
// This object:
//   1. SELF-IDENTIFIES via the Live Object Model — but ONLY after live.thisdevice
//      fires (the LOM is not ready at loadbang; resolving there returns undefined).
//   2. NORMALIZES the raw per-band values into energy fractions (sum ~1).
//   3. STAMPS  /track/<id>/<msg>  and emits to [udpsend 127.0.0.1 9880].
//
// The patch wires live.thisdevice -> this object's inlet (a bang) so identity is
// resolved at the right time, and a slow metro re-bangs for refresh. Until identity
// resolves, data messages are suppressed (no /track/unknown/ spam).
//
// Send this object:  levels …6 | stereo …3 | spectrum …N | bang (resolve+meta)

// autowatch is a DEV-only convenience (hot-reload this script while editing it in a
// saved Max patch). In a shipping/byte-wrapped .amxd it has no valid project context to
// resolve the script path, which makes Max throw "a project without a name is like a day
// without sunshine. fatal." Keep it 0 in production; flip to 1 only when live-editing.
autowatch = 0;
inlets = 1;
outlets = 1;

var BAND_SCHEME = "v1_7band";      // must match a scheme in harness/bands.py

var trackId = "unknown";
var trackName = "";
var trackKind = "";
var groupId = "-1";

function first(v) {                 // LOM get() may return ["x"] or "x"
    return (v && v.length !== undefined && typeof v !== "string") ? v[0] : v;
}
function numf(v) {
    return (v && v.length !== undefined) ? Number(v[0]) : Number(v);
}

// Resolve which track this device sits on. Returns true on success.
function resolveIdentity() {
    // canonical_parent of a device on a track IS the track (LOM navigation).
    var tr;
    try {
        tr = new LiveAPI(null, "this_device canonical_parent");
        if (!tr || !tr.id || Number(tr.id) === 0) return false;   // LOM not ready yet
        trackId = String(tr.id);
    } catch (e) {
        post("[track_ears] id resolve failed: " + e + "\n");
        return false;
    }
    // Each field is best-effort: one failing LOM property must NOT block meta.
    try { trackName = String(first(tr.get("name"))); } catch (e) { }
    try {
        var p = "";
        try { p = tr.unquotedpath || ""; } catch (ep) { p = ""; }
        if (p.indexOf("master_track") !== -1)        trackKind = "master";
        else if (p.indexOf("return_tracks") !== -1)  trackKind = "return";
        else if (numf(tr.get("is_foldable")) === 1)  trackKind = "group";
        else trackKind = (numf(tr.get("has_midi_input")) === 1) ? "midi" : "audio";
    } catch (e) { if (!trackKind) trackKind = "audio"; }
    try {
        var g = tr.get("group_track");                // ["id", N] or 0
        var gid = (g && g.length >= 2) ? Number(g[1]) : Number(g || 0);
        groupId = (gid && gid !== 0) ? String(gid) : "-1";
    } catch (e) { }
    return true;                                       // id resolved -> always emit meta
}

function loadbang() { }              // deliberately empty — LOM not ready this early
function bang() { if (resolveIdentity()) emitMeta(); }   // fired by live.thisdevice + metro

function emitMeta() {
    outlet(0, "/track/" + trackId + "/meta", trackName, trackKind, groupId, BAND_SCHEME);
}

function levels() {
    if (arguments.length < 6 || trackId === "unknown") return;
    outlet(0, "/track/" + trackId + "/levels",
           arguments[0], arguments[1], arguments[2],
           arguments[3], arguments[4], arguments[5]);
}

function stereo() {
    if (arguments.length < 3 || trackId === "unknown") return;
    outlet(0, "/track/" + trackId + "/stereo",
           arguments[0], arguments[1], arguments[2]);
}

// raw per-band energy in -> normalized fractions out (sum ~1)
function spectrum() {
    var n = arguments.length;
    if (n < 1 || trackId === "unknown") return;
    var e = [], total = 0.0;
    for (var i = 0; i < n; i++) {
        var v = Math.abs(arguments[i]);   // band signal RMS (linear, >=0)
        var energy = v * v;
        e.push(energy);
        total += energy;
    }
    if (total <= 0) total = 1.0;
    var out = ["/track/" + trackId + "/spectrum"];
    for (var j = 0; j < n; j++) out.push(e[j] / total);
    outlet(0, out);
}
