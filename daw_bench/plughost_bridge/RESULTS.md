# Tracktion ↔ plughost bridge: results (2026-11-08)

M4 Max (12 performance + 4 efficiency cores, 128 GB), macOS 26. Serum 2.1.5 with the track-66
patch on every track, a note every beat at 126 BPM, 44.1 kHz. Run data in
`sandbox_sessions/bridge_bench/` (not in git): `run2/`, `native_nostop/`, `kill_parallel/`,
`memory/`.

## Verdict

**The seam works, and it beats in-process hosting at 128 samples.**
- Tracktion renders through the bridge bit-identically to in-process.
- Its delay compensation absorbs the bridge's latency exactly.
- Playback through the bridge ran 64 tracks of Serum with zero dropouts. In-process Tracktion
  already dropped out at 1 track.
- When every helper is killed mid-playback, the engine never stutters, and each track is back
  in 0.71 s.

The price is 2.9–5.8 ms of added latency (one or two blocks) and about 0.25 GB per track.

## Gates

| Gate | Target | Result |
|---|---|---|
| Offline render through the bridge vs in process | null | **bit-identical** (residual −600 dBFS) |
| Delay compensation | sample-exact | **exact.** The bridge reports 512 samples; Tracktion compensates with no alignment needed |
| Added time per audio callback (128 samples) | ≤ 0.3 ms | **median 0.03–0.3 ms, p99 0.07–1.2 ms** over 1–64 tracks; this is the whole engine callback, below in-process |
| Realtime dropouts at 128 samples | 0 | **0 after warm-up, up to 64 tracks** at 2 quanta; at 1 quantum, 0 up to 32 tracks and 2 at 64 |
| Kill the plugin processes, engine keeps running | yes | **yes: 0 engine overruns**; all 4 chains recovered in parallel in 0.61 s; each track silent for 0.71 s |
| ≥ 300 tracks of a 6-plugin chain | | not reached: Serum's memory caps this machine near 32–40 tracks (below) |

### Realtime ramp: dropouts after a 1 s warm-up (engine overruns + bridge missed quanta)

| Tracks | 1 | 2 | 4 | 8 | 16 | 32 | 64 |
|---|---|---|---|---|---|---|---|
| In process (Tracktion's own graph) | 3 | 6 | 25 | 58 | 73 | 97 | – |
| Bridge, 1 quantum (+2.9 ms) | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| Bridge, 2 quanta (+5.8 ms) | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

- **In process,** Serum's note-on processing pushes Tracktion's callback past the 2.9 ms
  deadline: p99 1.5 → 5.5 ms, max 5.7 → 94 ms.
- **Through the bridge,** each Serum runs in its own helper on a real-time worker. With a
  quantum or two of slack, those spikes no longer land on the engine's deadline. The engine
  callback only copies shared memory: median 0.04 ms at 1 track, 0.29 ms at 64.
- **Warm-up is the weak spot:** bringing up many helpers at once misses quanta (270 at
  64 tracks) and stalls a callback for up to 300 ms. A real engine starts helpers before
  playback, or staggers them.

### Memory (macOS `footprint`, physical)

| Tracks | In process | Bridge |
|---|---|---|
| 1 | 3.30 GB | 3.52 GB |
| 8 | 26.0 GB | 28.0 GB |

- **Serum 2 is about 3.2 GB per instance, in process or not.** The bridge adds about
  **0.25 GB per track (+8%)**, and the engine process itself is 13 MB.
- Track count on this machine is limited by Serum, not by the bridge. The 64-track runs ran
  under memory compression and still had no dropouts after warm-up.

## How the seam works (and three bugs it surfaced)
1. **Tracktion builds delay compensation from the latency read at prepare, and its Renderer
   switches to offline afterwards.** The offline path therefore delays its output by the
   endpoint's extra latency, so the plugin keeps one latency in both modes. Without this, an
   offline render came out exactly 512 samples early.
2. **plughost refuses blocking processing while a realtime endpoint runs.** So
   `setNonRealtime(true)` stops the endpoint first. Without this, offline renders were silent.
3. **Recovery has to wait for playback.** A helper that dies before its endpoint exists cannot
   be recovered (`NotPrepared`). The kill test now waits for a "playing" marker. A real engine
   should restart a helper that dies at startup, not recover it.

## Not covered / caveats
- **State persistence through Tracktion** (`getStateInformation`) is not wired in this spike.
- **Block sizes must equal the quantum.** A block of another size is counted and silenced;
  none occurred, since Tracktion kept the device block size.

---

# Track-ramp gate on a real CoreAudio device (2026-11-09)

Gate (plan §12.1 #1): **≥ 300 tracks of a fixed 6-plugin chain at 64 and 128 samples, zero
dropouts.** Run data: `sandbox_sessions/bridge_bench/gate_b128/` (not in git).

## Verdict

**Not met at 128 samples, and so not at 64.** Two causes, both measured, both in the bridge's
realtime path and both fixable:
1. **Each helper creates its own CoreAudio workgroup interval** (`AudioWorkIntervalCreate`
   in plughost-helper's realtime schedule). This goes through coreaudiod, and each new one
   costs more the more helpers already run. Startup goes from ~5 s at 64 tracks to 15–45 s
   at 128 and over an hour at 256. Once, at 128 tracks, coreaudiod (126% CPU) stopped
   delivering device callbacks at all. Without the interval (a patched helper), startup is
   0.5–0.8 s at 128–300 tracks, but helpers miss quanta at light load (8–11k misses per 20 s
   at 128 tracks). The scheduler no longer knows their deadlines. **Fix: one shared
   workgroup, the device's, joined by every helper** (os_workgroup ports cross processes),
   instead of one interval per helper.
2. **The engine pays ~4–8 µs per bridged track per callback** on top of Tracktion's own
   track cost. At 300 tracks that overruns the 2.9 ms period: engine callback median 2.9 ms,
   p99 3.8–4.1 ms, with zero missed quanta, so it isn't the plugins. Tracktion alone plays
   300 audio tracks in 0.52 ms. **Fix: fewer cross-process wake-ups per callback**: batch the
   endpoints, or host several tracks' chains per helper.

The in-process alternative is worse on every workload measured. Through the bridge,
Tracktion runs **4× the heavy chain** and **8× the light chain** before dropping out.

## Setup
- **Device:** MacBook Pro Speakers via CoreAudio, 44.1 kHz, 128-sample buffer.
- **Engine path:** Tracktion's own device path (`DeviceManager` is the IO callback). Its
  graph threads join the device's audio workgroup (`EditPlaybackContext::enableAudioWorkgroup`).
- **CPU guard off:** Tracktion's CPU-mute guard (silence above 98% load) is disabled, since
  it would hide overloads.
- **Callback wrapper:** times each callback, records the output, then zeroes it before the
  speakers.
- **Dropouts:** CoreAudio processor-overload notifications, plus engine callbacks longer than
  the period, plus bridge quanta missed, all counted after a 2 s warm-up. A silent recording
  counts as a failed run.
- **Workload:** each track plays a stereo audio clip through the chain. Bridged = one helper
  per track running the whole 6-plugin chain (`slots`, one latency quantum).
- **Shared machine:** Live, Brave and other jobs were running; a Blender render ruined one
  attempt and was waited out. So each point is 3 runs, native and bridge interleaved.
  "Best" is the fewest dropouts of the 3 (what the engine can do), "median" the typical
  result.

## Chains

| Chain | Plugins (VST3, defaults) | Cost per 128-sample block, 1 track, offline |
|---|---|---|
| heavy | SSL 4K E → SSL Native Bus Compressor 2 → FabFilter Saturn 2 → kHs Delay → ValhallaRoom → FabFilter Pro-L 2 | **0.137 ms (4.7% of a core)** |
| light | kHs 3-Band EQ → Compressor → Distortion → Delay → Reverb → Limiter | ~0.004 ms |

- **The heavy chain caps any host on this machine near 255 tracks.** That's 12 performance
  cores at 100%, so "300 tracks" depends on the chain. The plan never fixed one, and the
  ~405-track Logic figure presumably used light stock plugins. Live on the same chain is the
  baseline the plan calls for, and is not yet measured.
- **The light chain** isolates host and engine overhead per plugin and per track.

## Results (dropouts after warm-up, 10 s runs; best / median of 3)

| Tracks | Heavy, in process | Heavy, bridge | Light, in process | Light, bridge | No plugins |
|---|---|---|---|---|---|
| 8 | 0 / 0 | 0 / 0 | | | |
| 16 | 0 / 6 | 0 / 0 | 0 / 2 | 0 / 0 | |
| 32 | **1 / 2** | 0 / 0 | **silent (1 of 3)**, 4 / 8 | 0 / 2 | 0 / 0 |
| 64 | | 0 / 0 | | 0 / 2 | |
| 96 | | **3584 / 5045** | | | 0 / 2 |
| 128 | | | | 0 / 0 | 0 / 0 |
| 256 | | | | startup > 1 h (stock); 1675 / 2274 (patched helper) | |
| 300 | | | | startup > 1 h (stock); 8191 / 8503 (patched helper) | 0 / 4 |

**Engine callback median (p99), ms:**
- Heavy bridged: 0.12 at 8 tracks, 0.52 at 32, 1.31 (2.16) at 64, 2.55 (3.84) at 96.
- Light bridged: 0.82 (1.01) at 128.
- No plugins: 0.52 (0.67) at 300.

**Memory:** heavy chain bridged ≈ 0.24 GB per track (21.9 GB at 96); light bridged 0.11 GB per
track (33 GB at 300); in process 0.07 GB per track (heavy).

## Findings
- **Heavy chain, bridged, cliff at 96.** The engine callback goes past the period while most
  helpers keep up (68 of 96 missed no quanta). Below 96, 64 tracks of a real mix chain play
  with no dropouts. In process stops at 16.
- **In process, Kilohearts goes silent beyond ~96–144 instances per process.** Every
  instance, so the whole mix, outputs digital silence with no error. 16 tracks of the light
  chain (96 instances) play; 24 (144) and 32 × six copies of one EQ (192) are silent. Bridged,
  each helper holds 6 and plays. Out-of-process hosting avoids a whole class of per-process
  plugin limits.
- **Two Plugin Alliance plugins output silence on this machine:** bx_console SSL 4000 E and
  Lindell 80 Bus, probably licence muting. They "passed" the host bake-off only because two
  silent renders null against each other. **That bake-off check must also require non-silent
  output.**
- **`ph_rt_start` has no timeout.** It runs from Tracktion's `prepareToPlay` on the message
  thread, so one slow helper blocks the engine from starting. The real engine needs helper
  start as asynchronous, bounded work.
- **A 600-track edit** pegged one core for over 15 minutes in edit or playback-graph setup,
  before playback, with no plugins. Not investigated (above the gate).

## Next (in order)
1. **Shared workgroup.** Pass the device's `os_workgroup` port to each helper and join it
   instead of `AudioWorkIntervalCreate` (a plughost-helper change; propose upstream). Expect
   startup in about a second and deadline-aware helpers.
2. **Cut the engine's per-track bridge cost.** Profile `ph_rt_process` at 300 tracks, then
   batch the helper wake-ups or move several tracks into one helper.
3. **Re-run 300 × light at 128 and 64,** and the heavy chain against Live on the same chain
   (the baseline the plan requires).
