# Per-Track Live Ears — setup & smoke test

The per-track listening layer: a Mix Analysis Hub device on every track/group/master
streams per-node loudness, stereo, and a 7-band spectrum over OSC; the bridge caches
it and computes **group-vs-group masking** the model can query.

Files:
- `harness/Mix Analysis Hub (Per-Track).maxpat` — the device (generated from the master
  patch by `harness/build_pertrack_device.py`; original left intact as reference).
- `harness/track_ears.js` — self-IDs the track via the LOM, stamps `/track/<id>/…`, normalizes bands.
- `harness/bands.py` — the 7-band scheme (swappable). `harness/masking.py` — the clash math.
- Bridge/cache: `harness/mix_analysis_bridge.py`, `harness/live_ears.py`.

## What is verified vs not

- **Verified (pure-Python, 10 tests):** OSC routing, per-track cache, band scheme swap,
  masking (group-vs-group + master congestion), the `.maxpat` is structurally valid JSON.
- **NOT yet verified (needs Max/Ableton):** the device's DSP + LOM self-identification only
  run inside Max. The smoke test below is how we confirm the producer side.

## Smoke test (in Ableton)

1. Start the cache daemon: `python run_harness.py ears`  (owns OSC :9880, writes the snapshot).
2. In Ableton, drop **Mix Analysis Hub (Per-Track)** on a couple of tracks, a group, and the master.
   Put `track_ears.js` where Max can find it (same folder / Max search path).
3. Toggle **Enable OSC** on each device. Press play.
4. Confirm the daemon logs rising `tracks_live`, then check the model surface:
   `get_live_ears_status` (fresh? tracks_live>0) and `get_masking_report` (clashes + congestion).

## Expected wire contract (what the device emits)

```
/track/<id>/meta      name kind group_id band_scheme
/track/<id>/levels    rmsL rmsR peakL peakR mid side
/track/<id>/spectrum  b0 b1 b2 b3 b4 b5 b6      (energy fractions, sum ~1)
/track/<id>/stereo    correlation mid side
/mix/transport        playing bpm bar beat      (global, unchanged)
```

`<id>` is the Live track id (self-resolved). Master bus reports as its own node.

## If something's off

- No `tracks_live`: check each device's Enable toggle and that `track_ears.js` loaded
  (Max console). The js `loadbang`/`bang` re-resolves identity and emits `meta`.
- Wrong/duplicate ids: a device couldn't resolve its track path — check the Max console for
  `[track_ears] identity resolve failed`.
- Bands look wrong: filterbank is `hip~ lo → lop~ hi` per band at `bands.py` edges; adjust the
  scheme in `bands.py` and re-run `build_pertrack_device.py` to regenerate.

## Tuning knobs (expected to revisit)

- **Band resolution** — add a scheme to `bands.py` (e.g. `v2_10band`), point `track_ears.js`
  `BAND_SCHEME` + the device at it, regenerate. Cache is data-driven; nothing else changes.
- **Masking sensitivity** — `masking.compute_masking(floor=…, congestion_frac=…, audible_db=…)`.
