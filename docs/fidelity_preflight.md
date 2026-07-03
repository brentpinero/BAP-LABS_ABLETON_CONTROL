# Fidelity Preflight Findings (Phase A)

Probed 2026-07-03 on pedalboard 0.9.17, macOS, Serum VST3.

| Probe | Result | Consequence |
|---|---|---|
| `pedalboard.load_plugin(Serum.vst3)` | OK | Headless hosting works |
| `plug.parameters` | **2,397 named params** (matches `xfer_serum.json.parameter_count`) | Named-param state transfer viable |
| Named param set roundtrip | OK | `set_device_parameter_by_name`-equivalent works headless |
| `plug.raw_state` get/set roundtrip | **OK** (8,704 bytes) | Complete plugin-state transfer without preset files |
| `plug.preset_data` | present | Alternative surface if needed |
| `plug.load_preset(<.fxp>)` | **FAILS** (`RuntimeError: Plugin failed to load data from preset file`) | As per pedalboard GH #187 — .fxp (VST2-era) rejected by VST3 Serum. Do NOT build on load_preset. |

## State-transfer strategy (decided)
1. **Primary: named param dicts** — capture from Live via `get_device_parameters` (or from the
   repo's parsed-preset corpus: 7,583 Serum presets with all 2,397 values extracted), apply
   headless via `plug.parameters` setattr. Same mechanism both sides → comparable renders.
2. **Secondary: `raw_state` bytes** — for exact full-state snapshots (captured headless-side;
   Live-side raw chunk lives in the .als, extractable via `als_parser` if ever needed).
3. **Rejected: `load_preset(.fxp)`** — unreliable (confirmed locally + upstream issue).

## Deferred to Phase D (needs Ableton open + user consent)
- Freeze dry-run: select_track → automator_freeze → wav in `<Project>/Samples/Processed/Freeze/`
  → verify 32-bit float + SR from header → automator_undo.

## Determinism (Phase B capstone)
Serum VST3, same state, two headless renders: **null depth 120 dB (bit-identical), latency 0**.
Measurement noise floor ≈ 0 — divergence vs Live is real signal. Calibration re-checks
determinism per preset (free-running LFOs / noise-osc phase can break it).
