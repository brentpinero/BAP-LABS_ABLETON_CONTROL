// plughost_bridge.h — C ABI over plughost (Rust) for a C++ engine.
//
// Two handles, two threads:
//   ph_bridge  control/message thread: open a plugin in a helper process, prepare, query,
//              blocking per-block processing (offline renders), realtime start/stop, recovery.
//   ph_rt      the audio thread only: one ph_rt_process call per quantum. Never blocks,
//              locks or allocates (plughost's RealtimeEndpoint).
// Every call returns 0 on success; on failure, ph_last_error(bridge) holds the message.
#pragma once
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ph_bridge ph_bridge;
typedef struct ph_rt ph_rt;

// A MIDI 1.0 channel message at a sample offset inside the block.
typedef struct { uint32_t offset; uint8_t status, data1, data2, _pad; } ph_midi;

// Transport for one block; tempo <= 0 sends none.
typedef struct { double tempo; int64_t sample_position; int32_t playing; } ph_transport;

// Opens a plugin in a new helper. job_json: {"format":"vst3"|"au", "bundle":..., "class_name":...,
// "class_index":..., "au":[type,subtype,manufacturer], "sr":..., "block":..., "realtime":bool,
// "component_state":path?, "preset":path?}, or {"slots":[{those plugin fields}, ...], "sr", "block",
// "realtime"} for a serial chain in one helper. Thread-safe: bridges may open in parallel.
// Returns NULL on failure, with the message in err.
ph_bridge* ph_open (const char* helper_path, const char* job_json, char* err, size_t err_len);
void ph_close (ph_bridge*);
const char* ph_last_error (const ph_bridge*);

// {"name","vendor","instrument":bool,"inputs":n,"outputs":n,"latency":frames}
int ph_info_json (ph_bridge*, char* out, size_t out_len);

// One block through the chain, blocking on the helper (offline rendering; not realtime safe).
int ph_process (ph_bridge*, const float* const* inputs, float* const* outputs, uint32_t frames,
                const ph_midi* events, uint32_t num_events, ph_transport transport);

// Realtime: create the endpoint (quantum <= prepared block size; latency_quanta 1..3), start it
// (total latency in frames written to *latency_out), stop it.
ph_rt* ph_rt_open (ph_bridge*, uint32_t quantum, uint32_t latency_quanta);
int ph_rt_start (ph_bridge*, uint32_t* latency_out);
int ph_rt_stop (ph_bridge*);
void ph_rt_close (ph_rt*);
// Returns 0 = processed, 1 = fallback played (priming, missed, resync, stopped), -1 = error.
int ph_rt_process (ph_rt*, const float* const* inputs, float* const* outputs, uint32_t frames,
                   const ph_midi* events, uint32_t num_events, ph_transport transport);
// {"running","callbacks","processed","missed","late","failures","stalled_ms","helper_exited","resync"}
int ph_rt_status_json (ph_bridge*, char* out, size_t out_len);
// Keeps a state snapshot (call while healthy); recovers the realtime chain from it in a new
// helper after a crash or hang. The ph_rt handle keeps working across the recovery.
int ph_snapshot (ph_bridge*);
int ph_recover_rt (ph_bridge*, double* recover_ms_out);
int ph_resync_rt (ph_bridge*);

#ifdef __cplusplus
}
#endif
