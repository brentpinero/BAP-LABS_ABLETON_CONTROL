"""
build_master_device.py — generate the SPECIALIZED master Mix Analysis device.

Why a dedicated master device (vs. bolting master logic into the bridge): the master
is the only node that needs a bar-aligned TIME-SERIES — the /mix/* bar cache that the
bridge's handle_levels / handle_stereo / handle_transport were built to feed. The
per-track biquad Hub emits ONLY /track/<id>/*, so when it sits on the master the bar
cache starves (sample_count never leaves 0 -> cached_bars stays 0), even though
per_track + masking keep working. Rather than special-case the master in the hot
per-track path, we give it its own device that speaks the /mix/* dialect the bridge
already understands.

This device is the base "Mix Analysis Hub.maxpat" (which already emits /mix/levels +
/mix/stereo) with these changes:
  * ADD a calibrated biquad bandpass bank (same bank + pink-noise gains as the
    per-track device) -> /mix/spectrum, so the bar cache gets a real master spectrum.
  * STRIP the base hub's plugsync~/live.observer transport cluster: it fails to bind on
    a fresh M4L load (frozen tempo/bar). Transport is now LOM-sourced in the daemon
    (live_ears._transport_poller), so it's dead weight here.
  * NO js / track_ears.js: on the master bus that script's `new LiveAPI("this_device
    canonical_parent")` throws "a project without a name is like a day without sunshine.
    fatal." on every meta-metro tick. The master perception node is instead synthesized
    in the daemon from the /mix/* stream (MixAnalysisBridge), so nothing regresses.

Pure /mix metering: emits /mix/levels + /mix/stereo + /mix/spectrum only.

One instance on the master bus, so no M4L saturation concern (that was an N-instance
problem, solved by aggregation elsewhere). Reuses the codegen helpers + calibration
from build_pertrack_device so the two devices never drift.

Output: "Mix Analysis Hub (Master).maxpat" — compile to .amxd and load on the master.
Run:  python build_master_device.py
"""

import json
import math
from pathlib import Path

import bands
# reuse the proven codegen + calibration so master/per-track banks never drift
from build_pertrack_device import FS, _load_gains, bandpass_coeffs, box, line
from perception_config import cfg

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
OUT = HERE / "Mix Analysis Hub (Master).maxpat"


def main(gains=None):
    if gains is None:
        gains = _load_gains()
    d = json.loads(BASE.read_text())
    p = d["patcher"]
    boxes, lines = p["boxes"], p["lines"]

    ids = {b["box"]["id"] for b in boxes}
    for need in ("obj-mid-scale", "obj-pack-levels", "obj-pack-stereo",
                 "obj-udpsend", "obj-loadbang-tempo"):
        assert need in ids, f"base hub missing expected object {need}"
    toggle_id = next((b["box"]["id"] for b in boxes if b["box"].get("maxclass") == "toggle"), None)

    # 1) calibrated biquad bandpass bank from the mono mid signal -> pak -> /mix/spectrum.
    #    NO js / LiveAPI: the master runs a `js track_ears.js` on regular tracks fine, but
    #    on the MASTER its `new LiveAPI("this_device canonical_parent")` throws "a project
    #    without a name is like a day without sunshine. fatal." on every meta-metro tick.
    #    The bar cache only needs /mix/*, so this device is pure /mix metering; the daemon
    #    synthesizes the master perception node from the same /mix/* stream (see
    #    MixAnalysisBridge.handle_levels/stereo/spectrum), so nothing regresses.
    edges = bands.band_edges()
    names = bands.band_names()
    n = len(edges)
    if gains is None:
        gains = [1.0] * n
    assert len(gains) == n, f"gains must have {n} entries, got {len(gains)}"

    pak = "pak " + " ".join(["0."] * n)
    boxes.append(box("obj-spec-pak", pak, 1040, 600, 160, n, 1, [""]))
    boxes.append(box("obj-mix-spec-prep", "prepend /mix/spectrum", 1040, 632, 180, 1, 1, [""]))
    lines.append(line("obj-spec-pak", 0, "obj-mix-spec-prep", 0))
    lines.append(line("obj-mix-spec-prep", 0, "obj-udpsend", 0))

    # band_i: biquad~ bandpass(mid) -> running RMS -> snapshot -> pak inlet i
    y = 180
    for i, (lo, hi) in enumerate(edges):
        fc = math.sqrt(lo * hi)                      # geometric center (log-spaced)
        Q = fc / (hi - lo)                           # -3 dB points ~ band edges
        c = bandpass_coeffs(fc, Q, gains[i])
        coeff_txt = " ".join(f"{v:.8f}" for v in c)
        bp, av, sn = f"obj-bp-{i}", f"obj-avg-{i}", f"obj-snap-{i}"
        boxes.append(box(bp, f"biquad~ {coeff_txt}", 620, y, 300, 6, 1, ["signal"]))
        boxes.append(box(av, "average~ 1024 @mode rms", 940, y, 150, 1, 1, ["signal"]))
        boxes.append(box(sn, "snapshot~ 50", 1020, y + 24, 90, 1, 1, [""]))
        lines.append(line("obj-mid-scale", 0, bp, 0))   # mono mid -> bandpass input
        lines.append(line(bp, 0, av, 0))
        lines.append(line(av, 0, sn, 0))
        lines.append(line(sn, 0, "obj-spec-pak", i))
        y += 40

    # 1b) SHARP-ONSET TAP: a SHORT-window (~6 ms) RMS envelope of the mono master, sampled
    #     at 200 Hz to a DEDICATED port. The main /mix RMS uses average~ 2048 (smooth CONTENT
    #     but ~46 ms-smeared, useless for onset timing); this fast tap gives ~5-6 ms onset
    #     resolution for latency calibration. Only the calibrate probe listens on this port.
    onset_port = int(cfg("onset_osc_port"))
    boxes.append(box("obj-onset-env", "average~ 256 @mode rms", 620, 560, 170, 1, 1, ["signal"]))
    boxes.append(box("obj-onset-snap", "snapshot~ 5", 620, 588, 110, 1, 1, [""]))
    boxes.append(box("obj-onset-prep", "prepend /mix/onset", 620, 616, 150, 1, 1, [""]))
    boxes.append(box("obj-onset-udp", "udpsend 127.0.0.1 %d" % onset_port, 620, 644, 170, 1, 0, []))
    lines.append(line("obj-mid-scale", 0, "obj-onset-env", 0))    # mono master -> fast envelope
    lines.append(line("obj-onset-env", 0, "obj-onset-snap", 0))
    lines.append(line("obj-onset-snap", 0, "obj-onset-prep", 0))
    lines.append(line("obj-onset-prep", 0, "obj-onset-udp", 0))

    # 2) AUTOSTART the device DSP when loaded (live.thisdevice -> the enable toggle). No js
    #    bang / meta-metro anymore — there is no js to identify.
    if toggle_id:
        lines.append(line("obj-loadbang-tempo", 0, toggle_id, 0))

    # 3) STRIP the per-device transport cluster. Transport is sourced from the LOM in the
    #    daemon (live_ears._transport_poller polls get_session_info) because the M4L
    #    plugsync~/live.observer/live.path path SILENTLY fails to bind on a fresh device
    #    load (tempo stuck at 120, bar frozen). Verified these objects only feed each other
    #    + udpsend (no external dependents); the audio DSP is signal/self-driven.
    STRIP = {"obj-plugsync", "obj-live-path", "obj-tempo-observer", "obj-tempo-f",
             "obj-playing-i", "obj-playing-snap", "obj-beats-snap", "obj-beats-f",
             "obj-bar-calc", "obj-beat-calc", "obj-metro", "obj-trig-transport",
             "obj-pack-transport", "obj-prepend-transport"}
    p["boxes"] = [b for b in boxes if b["box"]["id"] not in STRIP]
    p["lines"] = [l for l in lines
                  if l["patchline"]["source"][0] not in STRIP
                  and l["patchline"]["destination"][0] not in STRIP]
    boxes, lines = p["boxes"], p["lines"]
    kept = {b["box"]["id"] for b in boxes}
    for must in ("obj-toggle", "obj-loadbang-tempo", "obj-udpsend", "obj-spec-pak",
                 "obj-prepend-levels", "obj-prepend-stereo", "obj-mix-spec-prep"):
        assert must in kept, f"strip removed required object {must}"
    for l in lines:                                  # no dangling references remain
        for end in ("source", "destination"):
            assert l["patchline"][end][0] in kept, "stripped id still referenced by a line"
    assert not any(b["box"].get("text", "").startswith("js ") for b in boxes), \
        "master device must carry NO js (LiveAPI throws on the master bus)"

    # 4) retitle
    for b in boxes:
        if b["box"]["id"] == "obj-title":
            b["box"]["text"] = ("MIX ANALYSIS HUB (MASTER) v2 - pure /mix/levels+stereo+"
                                "spectrum metering, biquad bank, OSC @ 9880. NO js/LiveAPI "
                                "(master node synthesized in the daemon); transport LOM-sourced")

    OUT.write_text(json.dumps(d, indent=1))
    json.loads(OUT.read_text())                      # validate round-trip
    print(f"wrote {OUT.name}: {len(boxes)} boxes, {len(lines)} lines  (FS={FS:g}Hz)")
    print("emits: /mix/levels /mix/stereo /mix/spectrum @ :9880  +  /mix/onset (fast env, "
          "200Hz) @ :%d for latency calibration" % int(cfg("onset_osc_port")))
    print(f"biquad bandpass bands ({n}): " +
          ", ".join(f"{nm}[{lo:g}-{hi:g}] fc={math.sqrt(lo*hi):.0f} g={g:.2f}"
                    for (nm, (lo, hi), g) in zip(names, edges, gains)))


if __name__ == "__main__":
    main()
