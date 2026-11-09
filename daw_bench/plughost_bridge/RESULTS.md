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
- **No CoreAudio audio workgroup.** The paced engine thread uses the macOS time-constraint
  policy, like a CoreAudio IO thread, but does not join a device's workgroup. That may
  handicap in-process Tracktion's worker threads. Re-run on a real device before taking the
  in-process numbers as final.
- **Only one plugin.** One Serum per track. The 300-track gate assumes 6-plugin chains. One
  helper per track's chain (plughost supports multi-slot chains) is the next measurement.
- **State persistence through Tracktion** (`getStateInformation`) is not wired in this spike.
- **Block sizes must equal the quantum.** A block of another size is counted and silenced;
  none occurred, since Tracktion kept the device block size.
