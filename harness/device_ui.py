"""
device_ui.py — presentation-view meter codegen shared by the Mix Analysis device
builders (build_pertrack_device, build_master_device, build_aggregator_device,
build_probe_device).

The devices are pure meters in Live's device strip: every tracked signal gets a
visible meter, no buttons (the enable toggle is auto-started and stays out of
presentation). Two display primitives:

  * live.meter~  — signal-rate meter with Live's own dB scale/ballistics, fed
    straight from the SAME average~ RMS (or raw plugin~) signals the OSC path
    already computes, so the display can never drift from what is emitted.
  * multislider  — one compact list display per aggregator pair, fed from the
    pak that already collects that pair's band+side values (control rate,
    updates at the existing snapshot~ cadence).

All layout fits M4L's fixed device height (DEVICE_H); device width follows the
rightmost presentation rect.
"""

DEVICE_H = 169.0          # Live's fixed M4L device-strip height (px)
METER_TOP = 18.0          # meters start below the header row
METER_H = 122.0           # vertical meter height
LABEL_Y = 144.0           # per-column label row
LABEL_H = 16.0


def _pres(b, x, y, w, h):
    """Mark a box visible in presentation at the given rect."""
    b["box"]["presentation"] = 1
    b["box"]["presentation_rect"] = [float(x), float(y), float(w), float(h)]
    return b


def meter(id_, px, py, pw=14.0, ph=METER_H, x=0.0, y=0.0, interval=50):
    """A live.meter~ (signal in, Live-style dB meter) shown in presentation."""
    b = {"box": {"id": id_, "maxclass": "live.meter~", "numinlets": 1,
                 "numoutlets": 1, "outlettype": [""], "interval": interval,
                 "parameter_enable": 0,
                 "patching_rect": [float(x), float(y), float(pw), float(ph)]}}
    return _pres(b, px, py, pw, ph)


def mslider(id_, size, px, py, pw, ph, hi=0.3, x=0.0, y=0.0):
    """A multislider list display (0..hi linear) shown in presentation."""
    b = {"box": {"id": id_, "maxclass": "multislider", "numinlets": 1,
                 "numoutlets": 2, "outlettype": ["", ""], "parameter_enable": 0,
                 "setminmax": [0.0, float(hi)], "size": int(size),
                 "patching_rect": [float(x), float(y), float(pw), float(ph)]}}
    return _pres(b, px, py, pw, ph)


def plabel(id_, text, px, py, pw, ph=LABEL_H, fontsize=8.0, x=0.0, y=0.0):
    """A small comment label shown in presentation."""
    b = {"box": {"id": id_, "maxclass": "comment", "fontsize": float(fontsize),
                 "text": text,
                 "patching_rect": [float(x), float(y), float(pw), float(ph)]}}
    return _pres(b, px, py, pw, ph)


def pnum(id_, px, py, pw=48.0, ph=18.0, x=0.0, y=0.0):
    """A read-only float display (correlation etc.) shown in presentation."""
    b = {"box": {"id": id_, "maxclass": "flonum", "numinlets": 1,
                 "numoutlets": 2, "outlettype": ["", "bang"],
                 "parameter_enable": 0, "cantchange": 1,
                 "patching_rect": [float(x), float(y), float(pw), float(ph)]}}
    return _pres(b, px, py, pw, ph)


def _param(b, longname, **valueof):
    """Turn a live.* box into a Live parameter (automatable unless invisible)."""
    b["box"]["parameter_enable"] = 1
    b["box"]["varname"] = longname
    b["box"]["saved_attribute_attributes"] = {"valueof": dict(
        valueof, parameter_longname=longname, parameter_shortname=longname)}
    return b


def ptoggle(id_, longname, px, py, pw=18.0, ph=18.0, initial=1, x=0.0, y=0.0):
    """An automatable on/off live.toggle shown in presentation."""
    b = {"box": {"id": id_, "maxclass": "live.toggle", "numinlets": 1,
                 "numoutlets": 1, "outlettype": [""],
                 "patching_rect": [float(x), float(y), float(pw), float(ph)]}}
    _param(b, longname, parameter_type=2, parameter_mmax=1,
           parameter_enum=["off", "on"], parameter_initial=[initial],
           parameter_initial_enable=1)
    return _pres(b, px, py, pw, ph)


def pintbox(id_, longname, lo, hi, initial, px, py, pw=44.0, ph=16.0, x=0.0, y=0.0,
            note=False):
    """An automatable integer live.numbox; note=True displays MIDI note names."""
    b = {"box": {"id": id_, "maxclass": "live.numbox", "numinlets": 1,
                 "numoutlets": 2, "outlettype": ["", "float"],
                 "patching_rect": [float(x), float(y), float(pw), float(ph)]}}
    _param(b, longname, parameter_type=1, parameter_unitstyle=8 if note else 0,
           parameter_mmin=float(lo), parameter_mmax=float(hi),
           parameter_initial=[initial], parameter_initial_enable=1)
    return _pres(b, px, py, pw, ph)


def pbutton(id_, longname, text, px, py, pw=44.0, ph=16.0, x=0.0, y=0.0):
    """A momentary live.text button (bang on click); hidden from automation."""
    b = {"box": {"id": id_, "maxclass": "live.text", "mode": 0, "text": text,
                 "numinlets": 1, "numoutlets": 2, "outlettype": ["", ""],
                 "patching_rect": [float(x), float(y), float(pw), float(ph)]}}
    _param(b, longname, parameter_type=2, parameter_mmax=1,
           parameter_enum=["val1", "val2"], parameter_invisible=2)
    return _pres(b, px, py, pw, ph)


def pstatus(id_, text, px, py, pw, ph=16.0, x=0.0, y=0.0):
    """A read-only text line shown in presentation; a message box updated with 'set …'."""
    b = {"box": {"id": id_, "maxclass": "message", "text": text, "numinlets": 2,
                 "numoutlets": 1, "outlettype": [""],
                 "patching_rect": [float(x), float(y), float(pw), float(ph)]}}
    return _pres(b, px, py, pw, ph)


def codebox(id_, code, x, y, inlets=1, outlets=1, w=420.0, h=240.0):
    """A v8.codebox with the JavaScript embedded in the patcher (no external .js file to
    ship). Runs on Max's low-priority thread: configuration only, never the note path."""
    return {"box": {"id": id_, "maxclass": "v8.codebox", "filename": "none",
                    "code": code.strip().replace("\n", "\r\n"),
                    "fontface": 0, "fontname": "Menlo", "fontsize": 11.0,
                    "numinlets": int(inlets), "numoutlets": int(outlets),
                    "outlettype": [""] * int(outlets),
                    "patching_rect": [float(x), float(y), float(w), float(h)],
                    "saved_object_attributes": {"parameter_enable": 0}}}


def enable_presentation(patcher):
    """Open the device in presentation view (Live shows presentation for .amxd)."""
    patcher["openinpresentation"] = 1


def _line(src, so, dst, di):
    return {"patchline": {"source": [src, so], "destination": [dst, di]}}


def add_hub_meters(boxes, lines, band_names, header,
                   extra_meters=(), corr_src="obj-snapshot-corr"):
    """
    The shared hub meter strip (per-track + master devices use identical ids):
      L / R (raw plugin~ signals), S (side signal), one meter per spectrum band
      (each band's average~ RMS signal), a correlation readout, and any
      `extra_meters` [(source_id, label), ...] appended on the right.
    Signal sources must already exist in `boxes`; meters only fan out from them.
    """
    ids = {b["box"]["id"] for b in boxes}
    cols = [("obj-plugin-in-L", "L"), ("obj-plugin-in-R", "R"),
            ("obj-side-scale", "S")]
    cols += [(f"obj-avg-{i}", nm) for i, nm in enumerate(band_names)]
    cols += list(extra_meters)

    x = 6.0
    pitch = 22.0
    strip_w = len(cols) * pitch + 10.0 + 48.0        # meters + corr readout
    boxes.append(plabel("obj-ui-header", header, x, 2.0, strip_w, 14.0,
                        fontsize=9.0, x=40.0, y=740.0))
    for j, (src, label) in enumerate(cols):
        assert src in ids, f"meter source {src} missing from patch"
        mid, lid = f"obj-ui-meter-{j}", f"obj-ui-mlabel-{j}"
        px = x + j * pitch
        boxes.append(meter(mid, px, METER_TOP, x=40.0 + j * 30.0, y=770.0))
        boxes.append(plabel(lid, label, px - 3.0, LABEL_Y, pitch + 6.0,
                            x=40.0 + j * 30.0, y=800.0))
        lines.append(_line(src, 0, mid, 0))

    # correlation readout to the right of the meter strip (control-rate float)
    ids_now = {b["box"]["id"] for b in boxes}
    if corr_src in ids_now:
        cx = x + len(cols) * pitch + 10.0
        boxes.append(pnum("obj-ui-corr", cx, METER_TOP, x=40.0, y=830.0))
        boxes.append(plabel("obj-ui-corr-label", "corr", cx, METER_TOP + 20.0,
                            48.0, x=100.0, y=830.0))
        lines.append(_line(corr_src, 0, "obj-ui-corr", 0))
