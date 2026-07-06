"""
maxpat_to_amxd.py — wrap a .maxpat patcher into a Max for Live .amxd device.

An .amxd is a tiny binary header followed by the patcher JSON:

    "ampf" | version(u32) | <type "aaaa"|"iiii"|"mmmm"> |
    "meta" | size(u32) | payload | "ptch" | size(u32) | <patcher JSON> \n\0

We reuse the header from an EXISTING valid .amxd of the same device type (so the
device-type + meta chunk are exactly right) and swap in our patcher JSON, fixing
the "ptch" chunk size. Byte-for-byte safe: only the JSON payload + its size change.

Usage:
    python maxpat_to_amxd.py <source.maxpat> <template.amxd> <output.amxd>
"""

import struct
import sys
from pathlib import Path

PTCH_SIZE_OFFSET = 28   # bytes 24-27 = "ptch", 28-31 = little-endian payload size
PAYLOAD_OFFSET = 32


def wrap(maxpat_path: str, template_amxd: str, out_amxd: str) -> None:
    template = Path(template_amxd).read_bytes()
    assert template[:4] == b"ampf", f"{template_amxd} is not an .amxd (no 'ampf' magic)"
    assert template[24:28] == b"ptch", "unexpected .amxd layout (no 'ptch' chunk at 24)"

    json_text = Path(maxpat_path).read_text()
    # Mirror how Max stores the payload: JSON text then a newline + null terminator.
    payload = json_text.rstrip("\n").encode("utf-8") + b"\n\x00"

    header = template[:PTCH_SIZE_OFFSET]                 # through the "ptch" tag
    out = header + struct.pack("<I", len(payload)) + payload
    Path(out_amxd).write_bytes(out)

    dtype = template[8:12].decode("ascii", "replace")
    print(f"wrote {out_amxd}")
    print(f"  device type: {dtype}  payload: {len(payload)} bytes  total: {len(out)} bytes")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        raise SystemExit(2)
    wrap(sys.argv[1], sys.argv[2], sys.argv[3])
