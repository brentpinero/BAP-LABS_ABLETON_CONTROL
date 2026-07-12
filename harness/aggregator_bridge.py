"""
aggregator_bridge.py — translate the multichannel aggregator's per-channel OSC into
the SAME /track/<id>/* messages a per-track device emits, so the existing
MixAnalysisBridge (masking, TrackState, perception frame) consumes it with ZERO changes.

Flow:  aggregator device --/agg/ch/<k>/spectrum (raw per-band RMS)--> :9886 --> this
       bridge looks up channel k -> track-id + meta (the provisioning map), derives an
       overall RMS from the band powers, normalizes to energy fractions, and re-emits
       /track/<id>/meta + /levels + /spectrum + /stereo to :9880 (where the ears
       daemon already listens).

The channel->track map is pushed by the reconcile controller (which owns the routing).
v1 derives loudness from the band RMS (overall = sqrt(sum band_power)); stereo is a
mono placeholder (the aggregator sums L+R) until the device emits per-channel M/S.
"""

from __future__ import annotations

import asyncio
import json
import math
from pathlib import Path

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from perception_config import cfg

SILENCE_DB = -120.0


def load_agg_map(path):
    """Read the provisioning state file and return the channel->meta map as
    {int(global_channel): meta_dict}, or None if it can't be read.

    Returning None (not {}) is the whole point: it lets the hot-reload watcher tell
    "the file vanished / is half-written / is garbage" apart from "the map is genuinely
    empty". On None the watcher KEEPS the live map instead of wiping it — a mid-write
    read (the provision writer and the 2s poll can overlap) must not deafen the daemon."""
    try:
        raw = json.loads(Path(path).read_text())
        m = raw.get("map", {})
        return {int(k): v for k, v in m.items()}
    except Exception:
        return None


def agg_status(mapping, stats=None, n_pairs=None):
    """Substrate snapshot for logs + the MCP surface: how many aggregator devices and
    channels are live, the global-channel span, and OSC throughput. Pure — derives the
    device count from the global channels (device = ch // n_pairs), which is exactly how
    the provisioner allocated them, so it needs no per-device state."""
    n_pairs = int(n_pairs) if n_pairs is not None else int(cfg("aggregator_channels"))
    chans = sorted(int(c) for c in (mapping or {}))
    devices = len({c // n_pairs for c in chans})
    st = stats or {}
    return {
        "devices": devices,
        "channels": len(chans),
        "gch_min": chans[0] if chans else None,
        "gch_max": chans[-1] if chans else None,
        "recv": st.get("recv", 0),
        "sent": st.get("sent", 0),
        "unmapped": st.get("unmapped", 0),
    }


def derive(raw_bands, gate_db=None):
    """Raw per-band RMS (linear) -> (energy fractions summing ~1, overall rms_db, overall linear).

    Band signals partition the spectrum, so total power ~ sum(band_rms^2) and the
    overall RMS ~ sqrt of that — a loudness estimate without extra DSP in the device.

    Below `gate_db` the channel is effectively silent and its normalized spectrum is
    just noise-floor shape (quiet channels read garbage after L1 normalization), so the
    fractions are zeroed — the node then contributes nothing to masking (correct) instead
    of injecting a bogus spectrum."""
    if gate_db is None:
        gate_db = float(cfg("agg_gate_db"))
    powers = [float(b) * float(b) for b in raw_bands]
    tot = sum(powers)
    if tot <= 1e-18:
        return [0.0] * len(raw_bands), SILENCE_DB, 0.0
    lin = math.sqrt(tot)
    rms_db = 20.0 * math.log10(lin) if lin > 1e-9 else SILENCE_DB
    if rms_db < gate_db:
        return [0.0] * len(raw_bands), rms_db, lin      # gated: silent -> no spectrum
    fracs = [p / tot for p in powers]
    return fracs, rms_db, lin


def build_track_messages(track_id, meta, raw_values, scheme):
    """The /track/<id>/* OSC messages equivalent to a per-track device, as
    (address, args) tuples. Shapes match mix_analysis_bridge exactly:
      meta:  name kind group_id band_scheme
      levels: rms_l rms_r peak_l peak_r mid side
      spectrum: b0..bN
      stereo: correlation mid side

    raw_values = N band RMS + 1 side RMS (the aggregator's per-channel payload). Real
    stereo is derived from mid (bands) + side: assuming mid/side are ~uncorrelated,
    correlation ~ (mid_pow - side_pow)/(mid_pow + side_pow)."""
    import bands as _b
    nb = _b.n_bands(scheme)
    raw_bands = list(raw_values[:nb])
    side_lin = float(raw_values[nb]) if len(raw_values) > nb else 0.0
    fracs, _mid_db, mid_lin = derive(raw_bands)
    mid_p, side_p = mid_lin * mid_lin, side_lin * side_lin
    tot = mid_p + side_p
    overall = math.sqrt(tot)
    rms_db = 20.0 * math.log10(overall) if overall > 1e-9 else SILENCE_DB
    corr = (mid_p - side_p) / tot if tot > 1e-18 else 1.0
    base = "/track/%s" % track_id
    return [
        (base + "/meta", [meta.get("name", ""), meta.get("kind", "audio"),
                          str(meta.get("group_id", "-1")), scheme]),
        (base + "/levels", [rms_db, rms_db, rms_db, rms_db, mid_lin, side_lin]),
        (base + "/spectrum", list(fracs)),
        (base + "/stereo", [corr, mid_lin, side_lin]),
    ]


class AggregatorBridge:
    """Receives /agg/ch/<k>/spectrum on :9886, re-emits /track/<id>/* to :9880.

    The reconcile controller calls set_channel/set_map to bind channels to tracks;
    an unmapped channel is dropped (no /track spam)."""

    def __init__(self, send_host=None, send_port=9880, recv_port=None,
                 scheme=None, client=None):
        self.client = client or SimpleUDPClient(send_host or cfg("push_host"), send_port)
        self.recv_port = int(recv_port if recv_port is not None else cfg("agg_osc_port"))
        self.scheme = scheme or cfg("band_scheme")
        self.map = {}                              # channel(int) -> meta dict
        self.stats = {"recv": 0, "sent": 0, "unmapped": 0}

    def set_channel(self, ch, track_id, name, kind, group_id="-1"):
        self.map[int(ch)] = {"track_id": str(track_id), "name": name,
                             "kind": kind, "group_id": str(group_id)}

    def set_map(self, mapping):
        for ch, m in mapping.items():
            self.map[int(ch)] = m

    def clear(self):
        self.map.clear()

    def on_spectrum(self, address, *args):
        """Dispatcher callback for /agg/ch/<k>/spectrum."""
        self.stats["recv"] += 1
        try:
            ch = int(address.split("/")[3])
        except (IndexError, ValueError):
            return
        meta = self.map.get(ch)
        if not meta:
            self.stats["unmapped"] += 1
            return
        for addr, osc_args in build_track_messages(meta["track_id"], meta, list(args), self.scheme):
            self.client.send_message(addr, osc_args)
            self.stats["sent"] += 1

    async def run(self):
        disp = Dispatcher()
        disp.map("/agg/ch/*/spectrum", self.on_spectrum)
        server = AsyncIOOSCUDPServer(("127.0.0.1", self.recv_port), disp, asyncio.get_event_loop())
        transport, _ = await server.create_serve_endpoint()
        try:
            while True:
                await asyncio.sleep(3600)
        finally:
            transport.close()
