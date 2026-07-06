"""
build_aggregator_device.py — the REAL multichannel analysis aggregator: ONE M4L
device that runs the calibrated biquad bank on N input pairs at once, replacing N
per-track devices (kills the per-instance Max-runtime overhead that saturates Live).

Proven viable by the routing probe (see aggregator-routing-viable memory): a device's
plugin~ input pairs are scriptable output-routing channels, so N source tracks are
fed in via thin capture tracks under script control.

Per pair k (0..N-1):
  plugin~(2k+1)+plugin~(2k+2) -> +~ (mono) -> 7x biquad~ <calibrated coeffs+gains>
  -> average~ RMS -> snapshot~ -> pak(7) -> prepend /agg/ch/<k>/spectrum -> udpsend 9886

Raw per-band RMS per channel goes to :9886; a Python receiver maps channel->track-id
(the provisioning map) + normalizes (v^2/total, same as track_ears) into the existing
TrackState pipeline. Coeffs + per-band gains are IDENTICAL to build_pertrack_device
(bandpass_coeffs + pink_gains.json), so a channel reads the same as a per-track device.

Run:  python build_aggregator_device.py [n_pairs]   (default 8)
"""

import json
import sys
from pathlib import Path

import bands
from build_pertrack_device import FS, bandpass_coeffs, _load_gains

HERE = Path(__file__).resolve().parent
BASE = HERE / "Mix Analysis Hub.maxpat"
OSC_PORT = 9886


def box(id_, text, x, y, ins, outs, outtypes):
    return {"box": {"id": id_, "maxclass": "newobj", "numinlets": ins,
                    "numoutlets": outs, "outlettype": list(outtypes),
                    "patching_rect": [float(x), float(y), 150.0, 22.0], "text": text}}


def line(src, so, dst, di):
    return {"patchline": {"source": [src, so], "destination": [dst, di]}}


def main(n_pairs=8):
    d = json.loads(BASE.read_text())
    p = d["patcher"]
    boxes, lines = [], []

    edges = bands.band_edges()
    names = bands.band_names()
    nb = len(edges)
    import math
    gains = _load_gains() or [1.0] * nb
    coeffs = []
    for (lo, hi), g in zip(edges, gains):
        fc = math.sqrt(lo * hi)
        Q = fc / (hi - lo)
        coeffs.append(" ".join("%.8f" % v for v in bandpass_coeffs(fc, Q, g)))

    boxes.append(box("obj-udp", "udpsend 127.0.0.1 %d" % OSC_PORT, 40, 40, 1, 0, []))

    for k in range(n_pairs):
        lo_ch, hi_ch = 2 * k + 1, 2 * k + 2
        x0, y0 = 40 + (k % 4) * 340, 90 + (k // 4) * 260
        pl_lo, pl_hi = "p%d" % lo_ch, "p%d" % hi_ch
        boxes.append(box(pl_lo, "plugin~ %d" % lo_ch, x0, y0, 0, 1, ["signal"]))
        boxes.append(box(pl_hi, "plugin~ %d" % hi_ch, x0, y0 + 20, 0, 1, ["signal"]))
        summ = "sum%d" % k
        boxes.append(box(summ, "+~", x0 + 100, y0, 2, 1, ["signal"]))
        lines.append(line(pl_lo, 0, summ, 0))
        lines.append(line(pl_hi, 0, summ, 1))
        # per-band biquad -> rms -> snapshot -> pak
        pak = "obj-pak%d" % k
        boxes.append(box(pak, "pak " + " ".join(["0."] * nb), x0 + 100, y0 + 200, nb, 1, [""]))
        prep = "obj-prep%d" % k
        boxes.append(box(prep, "prepend /agg/ch/%d/spectrum" % k, x0 + 100, y0 + 224, 1, 1, [""]))
        lines.append(line(pak, 0, prep, 0))
        lines.append(line(prep, 0, "obj-udp", 0))
        for b in range(nb):
            bp, av, sn = "bp%d_%d" % (k, b), "av%d_%d" % (k, b), "sn%d_%d" % (k, b)
            yy = y0 + 40 + b * 22
            boxes.append(box(bp, "biquad~ %s" % coeffs[b], x0 + 160, yy, 6, 1, ["signal"]))
            boxes.append(box(av, "average~ 1024 @mode rms", x0 + 200, yy, 150, 1, ["signal"]))
            boxes.append(box(sn, "snapshot~ 60", x0 + 240, yy, 90, 1, [""]))
            lines.append(line(summ, 0, bp, 0))
            lines.append(line(bp, 0, av, 0))
            lines.append(line(av, 0, sn, 0))
            lines.append(line(sn, 0, pak, b))

    # valid audio effect: pass pair 1 through
    boxes.append(box("obj-out", "plugout~ 1 2", 40, 62, 2, 0, []))
    lines.append(line("p1", 0, "obj-out", 0))
    lines.append(line("p2", 0, "obj-out", 1))

    boxes.append({"box": {"id": "obj-title", "maxclass": "comment",
                          "patching_rect": [40.0, 16.0, 600.0, 20.0],
                          "text": "MIX ANALYSIS AGGREGATOR - %d pairs x %d-band biquad -> /agg/ch/<k>/spectrum :%d"
                                  % (n_pairs, nb, OSC_PORT)}})

    p["boxes"], p["lines"] = boxes, lines
    out = HERE / ("Mix Analysis Aggregator %dch.maxpat" % (n_pairs * 2))
    out.write_text(json.dumps(d, indent=1))
    json.loads(out.read_text())
    print("wrote %s: %d boxes, %d lines (%d pairs, %d bands, FS=%g, OSC :%d)"
          % (out.name, len(boxes), len(lines), n_pairs, nb, FS, OSC_PORT))
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(n)
