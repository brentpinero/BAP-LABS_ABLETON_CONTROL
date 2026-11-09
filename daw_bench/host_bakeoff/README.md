# Plugin-hosting bake-off (Phase 1 spike)

Decides the language of the agent-native DAW's out-of-process plugin host by measurement.
Two hosts run the same probe on the same plugins, and one harness scores both
(plan: `docs/agentic_daw_research.md`, Phase 1 gates).

| Host | Built on | Plugin runs in |
|---|---|---|
| `host_cpp` (`cpp_host/`) | JUCE `AudioPluginFormatManager`, the layer Tracktion Engine hosts with | the host process (the harness gives each probe its own process) |
| `host_rs` (`rust_host/`) | [plughost](https://github.com/emulette/plughost) 0.2.1 (MIT/Apache) | a separate helper process, over shared memory |

## Probe (identical in both hosts)

Each host reads one `job.json`:
1. Load the plugin and prepare it (48 kHz, 512-sample blocks, stereo; offline mode unless `realtime`).
2. Optionally import a `.vstpreset`.
3. Render `a.wav`, then reset and render `b.wav`. a vs b measures determinism.
4. Edit one ordinary parameter and render `c.wav`.
5. Save state, restore it into a fresh instance and render `d.wav`. c vs d measures state restore.

Each host writes `result.json` (timings, latency, per-block wall time, errors by stage).
Latency is not trimmed, so renders from the two hosts compare sample for sample.

## Build

```bash
# C++ (JUCE from the Tracktion clone at ~/Documents/third_party/tracktion_engine)
cmake -S daw_bench/host_bakeoff/cpp_host -B build/host_cpp -DCMAKE_BUILD_TYPE=Release
cmake --build build/host_cpp --config Release -j 12

# Rust (needs Rust >= 1.92), then sign the helper as a background .app
cargo build --release --manifest-path daw_bench/host_bakeoff/rust_host/Cargo.toml --target-dir build/host_rs
sh daw_bench/host_bakeoff/package_helper.sh build/host_rs/release/plughost-helper build/host_rs
```

## Run

```bash
python daw_bench/host_bakeoff/bakeoff.py              # compat + serum + kill
python daw_bench/host_bakeoff/bakeoff.py --only serum # or compat | kill; --limit N for a subset
python -m pytest daw_bench/host_bakeoff/test_bakeoff.py -v
```

Output goes to `sandbox_sessions/host_bakeoff/<timestamp>/`: `report.json`, `compat.json`,
`serum.json`, `kill.json`, plus every probe's job, result and wavs.

| Part | What it measures | Phase 1 gate |
|---|---|---|
| compat | 50 plugins (`plugin_list.json`, 25 VST3 + 25 AU). A plugin passes if the probe finishes, output is finite, and the restore holds. Deterministic plugins (a vs b ≤ −80 dBFS) must null after restore (≤ −80 dBFS). Other plugins: the restored render's 8-band spectrum must sit within twice the plugin's own repeat variation of the edited render; if the edit is not visible in the spectrum, the restore is marked inconclusive | ≥ 95% |
| overhead | Rust out-of-process per-block wall time minus C++ in-process per-block wall time, per plugin | ≤ 0.3 ms |
| kill | SIGKILL the Rust helper mid-render: the host must survive, recover from its snapshot and finish | engine keeps running |
| serum | Track-66 Serum 2 patch (`daw_bench/fixtures/serum2_track66`) in both hosts, offline and realtime mode, vs the Ableton freeze, per band in 20–250 Hz | ≤ 1 dB |

Excluded from the rate, with the reason in the summary: plugins with an `"excluded"` field in
`plugin_list.json` (e.g. unlicensed on this machine), and VST3s with no arm64 slice (no native
host, Live included, can load them on Apple Silicon). Re-score a finished run with the current
rules: `python daw_bench/host_bakeoff/bakeoff.py --summarize sandbox_sessions/host_bakeoff/<run>`.

Notes:
- Loading plugins natively can show licence or authorisation dialogs. Run the harness while
  logged in, and expect a dialog to count as a timeout (240 s).
- The C++ probe runs on a worker thread while the main thread pumps the JUCE message loop.
  JUCE requires AUv3 instances to be created that way, and `runDispatchLoop()` returns at once
  in a macOS console app, so the loop is pumped with `runDispatchLoopUntil`.
