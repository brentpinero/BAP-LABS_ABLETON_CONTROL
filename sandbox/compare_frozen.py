"""
compare_frozen.py — watch the project Freeze folder for a user's manual freeze,
then null-test it against a headless render. Safe: read-only on Live's side.

Usage:
    python sandbox/compare_frozen.py \
        --project-dir "<open Live project folder>" \
        --headless "<headless.wav>" \
        --clip-start-beats 32 --bpm 126 --window 10.6
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import fidelity  # noqa: E402
import soundfile as sf, numpy as np  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--headless", required=True)
    ap.add_argument("--clip-start-beats", type=float, default=0.0)
    ap.add_argument("--bpm", type=float, default=120.0)
    ap.add_argument("--window", type=float, default=10.0, help="seconds to slice from clip start")
    ap.add_argument("--registry-key", default="serum2:track66_realpatch")
    args = ap.parse_args()

    fd = Path(args.project_dir) / "Samples" / "Processed" / "Freeze"
    before = set(fd.glob("*.wav")) if fd.exists() else set()
    print(f"Watching {fd}\n-> In Live: right-click track 66's header -> Freeze Track. Waiting...")
    wav = None
    for _ in range(600):
        new = sorted((set(fd.glob("*.wav")) - before), key=lambda p: p.stat().st_mtime)
        stable = [f for f in new if f.stat().st_size > 1000
                  and time.time() - f.stat().st_mtime > 1.5]
        if stable:
            wav = stable[-1]
            break
        time.sleep(1.0)
    if not wav:
        print("No new freeze detected (10 min). Freeze track 66 and re-run.")
        return 1
    print(f"Found freeze: {wav.name}")

    live, sr = sf.read(str(wav), dtype="float64", always_2d=False)
    m = live.mean(axis=1) if live.ndim == 2 else live
    t0 = args.clip_start_beats * 60.0 / args.bpm
    seg = m[int(t0 * sr): int((t0 + args.window) * sr)]
    slice_path = Path(args.headless).with_name("live_slice.wav")
    sf.write(slice_path, seg.astype("float32"), sr)

    res = fidelity.compare(args.headless, slice_path)
    print("\n=== HEADLESS vs LIVE (real track-66 patch) ===")
    for k in ("null_depth_db", "label", "latency_samples", "gain_delta_db", "lufs_delta"):
        print(f"  {k}: {res[k]}")
    print(f"  band_diff_db: {res['band_diff_db']}")

    reg = fidelity.Registry()
    if args.registry_key in reg.data:
        e = reg.data[args.registry_key]
        e["results"], e["label"] = res, res["label"]
        e["audio_pair"]["live"] = str(slice_path)
        reg.save()
        print(f"\nregistry updated -> play both in the review UI (Fidelity tab)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
