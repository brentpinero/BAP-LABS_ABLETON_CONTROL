"""
build_pertrack_device.py — generate the per-track Mix Analysis Hub device by
surgically mutating the PROVEN master-bus patch (valid .maxpat JSON), so we never
hand-author fragile JSON.

What it changes vs "Mix Analysis Hub.maxpat":
  * routes levels + stereo through [js track_ears.js] so every message is
    addressed to /track/<this track's id>/... (self-identified via the LOM),
  * adds an N-band spectrum chain (biquad~ BANDPASS bank -> average~ rms ->
    snapshot~ per band, centers/Q from bands.py) -> pak -> [js] -> /spectrum,
  * keeps the master DSP (RMS/peak/mid-side) and transport untouched.

FILTER TOPOLOGY: a biquad~ bandpass bank (RBJ cookbook, geometric-center +
constant-Q derived from each band's edges), replacing the earlier onepole~
lowpass-DIFFERENCE bank. Calibration proved the onepole bank (6 dB/oct) smeared
the top end — an 8 kHz tone read dominant in hi_mid instead of presence. True
bandpass filters (12 dB/oct, specified center+Q per band) separate the wide upper
bands cleanly. Coefficients are sample-rate dependent (built at FS below).

PER-BAND GAIN: `gains` (default all 1.0) is folded straight into each biquad's
numerator coefficients (scaling a filter's output = scaling its numerator). This
is the broadband-calibration hook — after measuring the live pink-noise spectrum
we recompute gains so the bank matches the FFT ruler for broadband too. It lives
in the device (per-instance), NOT in the shared track_ears.js, so recalibrating
never hot-touches the live devices.

Output: "Mix Analysis Hub (Per-Track Biquad).maxpat" — a SEPARATE file so the
onepole device already loaded on live tracks is undisturbed until this is proven.
Run:  python build_pertrack_device.py
"""

import json
import math
from pathlib import Path

import bands
import device_ui

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
OUT = HERE / "Mix Analysis Hub (Per-Track Biquad).maxpat"

FS = 44100.0                 # coefficient sample rate (matches project + ref tones)


def bandpass_coeffs(fc, Q, gain=1.0, fs=FS):
    """RBJ cookbook bandpass (constant 0 dB peak), scaled by `gain`, in Max
    biquad~ order: ff0 ff1 ff2 fb1 fb2, where
      y = ff0 x0 + ff1 x1 + ff2 x2 - fb1 y1 - fb2 y2.
    gain scales the numerator (ff*) → scales the band's output level."""
    w0 = 2.0 * math.pi * fc / fs
    alpha = math.sin(w0) / (2.0 * Q)
    a0 = 1.0 + alpha
    return [gain * alpha / a0, 0.0, gain * (-alpha) / a0,
            (-2.0 * math.cos(w0)) / a0, (1.0 - alpha) / a0]


def box(id_, text, x, y, w=130, numinlets=1, numoutlets=1, outlettype=("signal",)):
    return {"box": {"id": id_, "maxclass": "newobj", "numinlets": numinlets,
                    "numoutlets": numoutlets, "outlettype": list(outlettype),
                    "patching_rect": [float(x), float(y), float(w), 22.0], "text": text}}


def line(src, so, dst, di):
    return {"patchline": {"source": [src, so], "destination": [dst, di]}}


GAINS_FILE = HERE.parent / "sandbox_sessions" / "calibration" / "pink_gains.json"


def _load_gains():
    """Calibrated per-band broadband gains (from the live pink-noise pass), if present.
    Falls back to unity so a fresh checkout still builds a working (uncalibrated) device."""
    try:
        return json.loads(GAINS_FILE.read_text())["gains"]
    except Exception:
        return None


def main(gains=None):
    if gains is None:
        gains = _load_gains()
    d = json.loads(BASE.read_text())
    p = d["patcher"]
    boxes, lines = p["boxes"], p["lines"]

    ids = {b["box"]["id"] for b in boxes}
    assert "obj-mid-scale" in ids, "expected mid signal source obj-mid-scale"
    toggle_id = next((b["box"]["id"] for b in boxes if b["box"].get("maxclass") == "toggle"), None)

    # 1) the addressing brain
    boxes.append(box("obj-track-js", "js track_ears.js", 360, 660, 140, 1, 1, [""]))
    lines.append(line("obj-track-js", 0, "obj-udpsend", 0))

    # 2) reroute levels + stereo through the js (retag, redirect to js)
    retag = {"obj-prepend-levels": "prepend levels", "obj-prepend-stereo": "prepend stereo"}
    for b in boxes:
        if b["box"]["id"] in retag:
            b["box"]["text"] = retag[b["box"]["id"]]
    for l in lines:
        pl = l["patchline"]
        if pl["source"][0] in retag and pl["destination"][0] == "obj-udpsend":
            pl["destination"][0] = "obj-track-js"   # -> js instead of straight to udpsend
    # (transport stays /mix/transport -> udpsend: it is global, not per-track)

    # 3) N-band spectrum from the mono mid signal via a biquad~ BANDPASS bank.
    #    One true bandpass per band (center = geometric mean of edges, Q = fc/BW so
    #    the -3 dB points sit at the band edges), then running RMS -> snapshot -> pak.
    #    biquad~ is core MSP; coefficients baked in from bands.py + FS + gains.
    edges = bands.band_edges()                       # [(lo,hi), ...] from bands.py
    names = bands.band_names()
    n = len(edges)
    if gains is None:
        gains = [1.0] * n
    assert len(gains) == n, f"gains must have {n} entries, got {len(gains)}"

    pak = "pak " + " ".join(["0."] * n)
    boxes.append(box("obj-spec-pak", pak, 1040, 600, 160, n, 1, [""]))
    boxes.append(box("obj-spec-prepend", "prepend spectrum", 1040, 632, 160, 1, 1, [""]))
    lines.append(line("obj-spec-pak", 0, "obj-spec-prepend", 0))
    lines.append(line("obj-spec-prepend", 0, "obj-track-js", 0))

    # band_i: biquad~ bandpass(mid signal) -> running RMS -> snapshot -> pak inlet i
    y = 180
    for i, (lo, hi) in enumerate(edges):
        fc = math.sqrt(lo * hi)                      # geometric center (log-spaced)
        Q = fc / (hi - lo)                           # -3 dB points ~ band edges
        c = bandpass_coeffs(fc, Q, gains[i])
        coeff_txt = " ".join(f"{v:.8f}" for v in c)
        bp, av, sn = f"obj-bp-{i}", f"obj-avg-{i}", f"obj-snap-{i}"
        # biquad~: signal in left inlet (0); 5 creation args set the coefficients.
        boxes.append(box(bp, f"biquad~ {coeff_txt}", 620, y, 300, 6, 1, ["signal"]))
        boxes.append(box(av, "average~ 1024 @mode rms", 940, y, 150, 1, 1, ["signal"]))
        boxes.append(box(sn, "snapshot~ 50", 1020, y + 24, 90, 1, 1, [""]))
        lines.append(line("obj-mid-scale", 0, bp, 0))   # mono mid -> bandpass input
        lines.append(line(bp, 0, av, 0))
        lines.append(line(av, 0, sn, 0))
        lines.append(line(sn, 0, "obj-spec-pak", i))
        y += 40

    # 4) resolve identity + AUTOSTART when the LOM is ready. live.thisdevice
    #    (obj-loadbang-tempo) bangs once the device is fully loaded — the correct
    #    time to query the LOM (loadbang is too early). Fan it out to:
    #      - the js (bang -> resolve track identity + emit meta),
    #      - the enable toggle (bang flips it on -> OSC streams with no manual step).
    lines.append(line("obj-loadbang-tempo", 0, "obj-track-js", 0))
    if toggle_id:
        lines.append(line("obj-loadbang-tempo", 0, toggle_id, 0))        # autostart
        # periodic meta refresh + late identity retry
        boxes.append(box("obj-meta-metro", "metro 2000", 360, 620, 90, 2, 1, [""]))
        lines.append(line(toggle_id, 0, "obj-meta-metro", 0))
        lines.append(line("obj-meta-metro", 0, "obj-track-js", 0))

    # 5) presentation meters: everything this device tracks (L/R level, side,
    #    every spectrum band, correlation), no buttons — fed from the SAME
    #    signals the OSC path uses, so display and emission can never drift.
    device_ui.add_hub_meters(boxes, lines, names, "MIX ANALYSIS — PER-TRACK")
    device_ui.enable_presentation(p)

    # 6) retitle
    for b in boxes:
        if b["box"]["id"] == "obj-title":
            b["box"]["text"] = ("MIX ANALYSIS HUB (PER-TRACK) v22 BIQUAD+METERS - self-IDs "
                                "via LOM, biquad~ bandpass bank, OSC /track/<id>/* @ 9880")

    OUT.write_text(json.dumps(d, indent=1))
    # validate round-trips and report
    json.loads(OUT.read_text())
    print(f"wrote {OUT.name}: {len(boxes)} boxes, {len(lines)} lines  (FS={FS:g}Hz)")
    print(f"biquad bandpass bands ({n}): " +
          ", ".join(f"{nm}[{lo:g}-{hi:g}] fc={math.sqrt(lo*hi):.0f} Q={math.sqrt(lo*hi)/(hi-lo):.2f} g={g:.2f}"
                    for (nm, (lo, hi), g) in zip(names, edges, gains)))


if __name__ == "__main__":
    main()
