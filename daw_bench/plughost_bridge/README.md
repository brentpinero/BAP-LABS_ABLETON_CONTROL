# Tracktion ↔ plughost bridge (Phase 1 spike)

The bake-off (`../host_bakeoff/RESULTS.md`) chose plughost (Rust, out-of-process) as the
plugin host and Tracktion Engine (C++) as the engine. This spike connects the two and measures
the seam.

```
Tracktion Edit ── te::ExternalPlugin ── PlughostInstance (JUCE AudioPluginInstance, "Plughost" format)
                                            │  C ABI: plughost_bridge.h  (libplughost_bridge.a, Rust)
                                            ▼
                                     plughost Chain ── shared memory ── helper process ── plugin
```

- **Seam: a custom JUCE `AudioPluginFormat`.** Tracktion treats bridged plugins as ordinary
  `ExternalPlugin`s, so its delay compensation, transport and graph code are unmodified.
  Hooks used: `pluginFormatManager.addFormat`, `createNewPlugin(ExternalPlugin::xmlTypeName, desc)`.
- **Two audio paths:**
  - **Offline** (Tracktion's Renderer calls `setNonRealtime(true)`): blocking `ph_process` per block.
  - **Realtime** (playback): plughost's `RealtimeEndpoint`, one `ph_rt_process` per block. It
    never waits, locks or allocates, and adds `latency_quanta × block` frames of latency.
- **One latency for both paths.** Tracktion builds delay compensation once, and the Renderer
  switches to offline after `prepareToPlay`. So the offline path delays its output by the
  endpoint's extra latency, and the plugin reports the same latency either way.
- **Crash recovery:** a control thread polls each bridge. When the helper exits or stalls
  for more than 300 ms, it calls `ph_recover_rt`, which recovers the chain from its snapshot
  into a new helper. The audio thread keeps its `ph_rt` handle throughout.

## Build

```bash
cargo build --release --manifest-path daw_bench/plughost_bridge/Cargo.toml --target-dir build/plughost_bridge
cmake -S daw_bench/plughost_bridge/bridge_probe -B build/bridge_probe -DCMAKE_BUILD_TYPE=Release
cmake --build build/bridge_probe --config Release -j 12
# plus the plughost helper app from ../host_bakeoff/README.md (build/host_rs/PlughostHelper.app)
```

## Run

```bash
python daw_bench/plughost_bridge/bridge_bench.py               # null + ramp + kill
python daw_bench/plughost_bridge/bridge_bench.py --only ramp --max-tracks 64
```

`bridge_probe` drives Tracktion's `HostedAudioDeviceInterface` from a thread paced to wall-clock
time. That thread uses macOS's time-constraint (real-time) policy, like a CoreAudio IO thread.
The probe plays nothing through your speakers; it records the output to a wav.

## Spike limitations
- `PlughostInstance` does not persist plugin state through Tracktion's
  `getStateInformation`; the job spec carries it.
- Realtime requires the engine's block size to equal the endpoint quantum. A block of another
  size is counted (`size_mismatches`) and played as silence.
- The paced thread is not in a CoreAudio audio workgroup, as a real device's IO thread would be.
