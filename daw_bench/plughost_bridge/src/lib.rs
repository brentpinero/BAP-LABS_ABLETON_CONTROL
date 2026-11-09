//! plughost_bridge — C ABI over plughost (see plughost_bridge.h) so the C++ engine can host
//! plugins out of process. A `Bridge` lives on the control thread; an `Rt` (plughost's
//! RealtimeEndpoint) lives on the audio thread and is never blocked, locked or allocated in.

use std::ffi::{CStr, c_char};
use std::path::Path;
use std::time::Instant;

use plughost::{
    BlockContext, Chain, ChainSlot, Event, Events, Layout, PluginKind, PluginRef, ProcessMode,
    RealtimeConfig, RealtimeEndpoint, RealtimeOutput, Scanner, SpawnOptions, StatePurpose, Transport,
};
use serde::Deserialize;

#[derive(Deserialize)]
struct Job {
    format: String,
    bundle: Option<String>,
    class_name: Option<String>,
    class_index: Option<usize>,
    au: Option<[String; 3]>,
    sr: f64,
    block: usize,
    #[serde(default)]
    realtime: bool,
    component_state: Option<String>,
    preset: Option<String>,
}

pub struct Bridge {
    chain: Chain,
    plugin: PluginRef,
    name: String,
    vendor: String,
    instrument: bool,
    inputs: usize,
    outputs: usize,
    sr: f64,
    snapshot: Option<Vec<ChainSlot>>,
    produced: Events,
    error: std::ffi::CString,
}

pub struct Rt {
    endpoint: RealtimeEndpoint,
    sr: f64,
    inputs: usize,   // 0, 1 or 2
    outputs: usize,  // 1 or 2
    events: Events,
    produced: Events,
}

#[repr(C)]
pub struct PhMidi {
    offset: u32,
    status: u8,
    data1: u8,
    data2: u8,
    _pad: u8,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct PhTransport {
    tempo: f64,
    sample_position: i64,
    playing: i32,
}

fn describe(error: &dyn std::error::Error) -> String {
    let mut text = error.to_string();
    let mut cause = error.source();
    while let Some(e) = cause {
        text = format!("{text}: {e}");
        cause = e.source();
    }
    text
}

fn au_class_id(codes: &[String; 3]) -> String {
    codes.iter().flat_map(|c| c.as_bytes().iter().take(4).map(|b| format!("{b:02X}")).collect::<Vec<_>>()).collect()
}

/// A VST3 .vstpreset holding one component state (same layout as host_rs's).
fn vstpreset(class_id: &str, component: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(component.len() + 80);
    out.extend_from_slice(b"VST3");
    out.extend_from_slice(&1i32.to_le_bytes());
    out.extend_from_slice(class_id.as_bytes());
    out.extend_from_slice(&(48 + component.len() as i64).to_le_bytes());
    out.extend_from_slice(component);
    out.extend_from_slice(b"List");
    out.extend_from_slice(&1i32.to_le_bytes());
    out.extend_from_slice(b"Comp");
    out.extend_from_slice(&48i64.to_le_bytes());
    out.extend_from_slice(&(component.len() as i64).to_le_bytes());
    out
}

fn context(frames: usize, t: PhTransport, sr: f64) -> BlockContext {
    let ctx = BlockContext::new(frames);
    if t.tempo <= 0.0 {
        return ctx;
    }
    let mut transport = Transport::new(t.sample_position, t.playing != 0);
    transport.tempo = Some(t.tempo);
    transport.beat_position = Some(t.sample_position as f64 / sr * t.tempo / 60.0);
    ctx.with_transport(transport)
}

/// Fills `events` (reserved for one block, so no allocation) from the C array.
fn fill_events(events: &mut Events, ptr: *const PhMidi, n: u32) -> bool {
    events.clear();
    if ptr.is_null() || n == 0 {
        return true;
    }
    let raw = unsafe { std::slice::from_raw_parts(ptr, n as usize) };
    raw.iter().all(|m| events.push(Event::midi(m.offset as usize, [m.status, m.data1, m.data2])).is_ok())
}

/// Borrowed channel slices from C pointer arrays.
unsafe fn slices<'a>(ptrs: *const *const f32, n: usize, frames: usize) -> Vec<&'a [f32]> {
    if ptrs.is_null() { return Vec::new(); }
    (0..n).map(|i| unsafe { std::slice::from_raw_parts(*ptrs.add(i), frames) }).collect()
}

unsafe fn slices_mut<'a>(ptrs: *const *mut f32, n: usize, frames: usize) -> Vec<&'a mut [f32]> {
    (0..n).map(|i| unsafe { std::slice::from_raw_parts_mut(*ptrs.add(i), frames) }).collect()
}

fn open(helper: &Path, job: &Job) -> Result<Bridge, String> {
    let plugin = match job.format.as_str() {
        "au" => PluginRef::audio_unit(au_class_id(job.au.as_ref().ok_or("au job without codes")?)),
        _ => {
            let bundle = job.bundle.as_ref().ok_or("vst3 job without bundle")?;
            let cache = std::env::temp_dir().join(format!("ph-bridge-scan-{}.json", std::process::id()));
            let scanned = Scanner::new(helper, &cache).retry(Path::new(bundle)).map_err(|e| describe(&e))?;
            let _ = std::fs::remove_file(&cache);
            let classes = scanned.plugins();
            let found = match &job.class_name {
                Some(name) => classes.into_iter().find(|(_, i)| &i.name == name),
                None => classes.into_iter().nth(job.class_index.unwrap_or(0)),
            };
            found.map(|(p, _)| p).ok_or(format!("no class in bundle: {:?}", scanned.outcome))?
        }
    };
    let mut chain = Chain::spawn(helper, &[ChainSlot::new(plugin.clone())], &SpawnOptions::default())
        .map_err(|e| describe(&e))?;
    let info = chain.plugins()[0].clone();
    let instrument = info.kind == PluginKind::Instrument;
    let mode = if job.realtime { ProcessMode::Realtime } else { ProcessMode::Offline };
    let mut prepared = None;
    let mut last = String::new();
    for layout in [Layout::Stereo, Layout::Mono] {
        let input = if instrument { Layout::None } else { layout };
        match chain.main_bus_config(job.sr, job.block, input, &[layout])
            .and_then(|c| chain.prepare_audio(&c.with_mode(mode)))
        {
            Ok(_) => { prepared = Some(layout.channels()); break; }
            Err(e) => last = describe(&e),
        }
    }
    let outputs = prepared.ok_or(last)?;
    if let Some(p) = &job.preset {
        let bytes = std::fs::read(p).map_err(|e| e.to_string())?;
        chain.import_preset(0, &bytes).map_err(|e| describe(&e))?;
    }
    if let Some(p) = &job.component_state {
        let state = std::fs::read(p).map_err(|e| e.to_string())?;
        chain.import_preset(0, &vstpreset(plugin.id().class_id().as_str(), &state)).map_err(|e| describe(&e))?;
    }
    Ok(Bridge {
        chain, plugin, name: info.name, vendor: info.vendor, instrument,
        inputs: if instrument { 0 } else { outputs }, outputs, sr: job.sr,
        snapshot: None, produced: Events::for_block(), error: Default::default(),
    })
}

fn write_out(s: &str, out: *mut c_char, len: usize) -> i32 {
    if out.is_null() || len == 0 { return -1; }
    let bytes = s.as_bytes();
    let n = bytes.len().min(len - 1);
    unsafe {
        std::ptr::copy_nonoverlapping(bytes.as_ptr(), out as *mut u8, n);
        *out.add(n) = 0;
    }
    if n < bytes.len() { -1 } else { 0 }
}

impl Bridge {
    fn fail(&mut self, msg: String) -> i32 {
        self.error = std::ffi::CString::new(msg.replace('\0', " ")).unwrap_or_default();
        -1
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_open(helper: *const c_char, job_json: *const c_char, err: *mut c_char, err_len: usize) -> *mut Bridge {
    let result = (|| {
        let helper = unsafe { CStr::from_ptr(helper) }.to_str().map_err(|e| e.to_string())?;
        let json = unsafe { CStr::from_ptr(job_json) }.to_str().map_err(|e| e.to_string())?;
        let job: Job = serde_json::from_str(json).map_err(|e| e.to_string())?;
        open(Path::new(helper), &job)
    })();
    match result {
        Ok(b) => Box::into_raw(Box::new(b)),
        Err(e) => { write_out(&e, err, err_len); std::ptr::null_mut() }
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_close(b: *mut Bridge) {
    if !b.is_null() { drop(unsafe { Box::from_raw(b) }); }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_last_error(b: *const Bridge) -> *const c_char {
    if b.is_null() { return c"null bridge".as_ptr(); }
    unsafe { &*b }.error.as_ptr()
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_info_json(b: *mut Bridge, out: *mut c_char, len: usize) -> i32 {
    let b = unsafe { &mut *b };
    let s = serde_json::json!({"name": b.name, "vendor": b.vendor, "instrument": b.instrument,
        "inputs": b.inputs, "outputs": b.outputs, "latency": b.chain.latency()}).to_string();
    write_out(&s, out, len)
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_process(b: *mut Bridge, inputs: *const *const f32, outputs: *const *mut f32,
                             frames: u32, events: *const PhMidi, num_events: u32, t: PhTransport) -> i32 {
    let b = unsafe { &mut *b };
    let n = frames as usize;
    let ins = unsafe { slices(inputs, b.inputs, n) };
    let mut outs = unsafe { slices_mut(outputs, b.outputs, n) };
    let mut evs = Events::for_block();
    if !fill_events(&mut evs, events, num_events) { return b.fail("too many events".into()); }
    match b.chain.process_audio_f32(&context(n, t, b.sr), &ins, &mut outs, &[], &evs, &mut b.produced) {
        Ok(()) => 0,
        Err(e) => b.fail(describe(&e)),
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_rt_open(b: *mut Bridge, quantum: u32, latency_quanta: u32) -> *mut Rt {
    let b = unsafe { &mut *b };
    let mut config = RealtimeConfig::new(quantum as usize);
    config.latency = latency_quanta.clamp(1, 3) as usize;
    match b.chain.realtime_endpoint(&config) {
        Ok(endpoint) => Box::into_raw(Box::new(Rt {
            endpoint, sr: b.sr, inputs: b.inputs, outputs: b.outputs,
            events: Events::for_block(), produced: Events::for_block(),
        })),
        Err(e) => { b.fail(describe(&e)); std::ptr::null_mut() }
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_rt_close(rt: *mut Rt) {
    if !rt.is_null() { drop(unsafe { Box::from_raw(rt) }); }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_rt_start(b: *mut Bridge, latency_out: *mut u32) -> i32 {
    let b = unsafe { &mut *b };
    match b.chain.start_realtime() {
        Ok(l) => { if !latency_out.is_null() { unsafe { *latency_out = l } } 0 }
        Err(e) => b.fail(describe(&e)),
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_rt_stop(b: *mut Bridge) -> i32 {
    let b = unsafe { &mut *b };
    match b.chain.stop_realtime() { Ok(()) => 0, Err(e) => b.fail(describe(&e)) }
}

/// Audio thread: channel slices live in stack arrays and events in storage reserved up front,
/// so this call does not allocate (plughost's endpoint never waits, locks or allocates either).
#[unsafe(no_mangle)]
pub extern "C" fn ph_rt_process(rt: *mut Rt, inputs: *const *const f32, outputs: *const *mut f32,
                                frames: u32, events: *const PhMidi, num_events: u32, t: PhTransport) -> i32 {
    let rt = unsafe { &mut *rt };
    let n = frames as usize;
    let mut ins: [&[f32]; 2] = [&[], &[]];
    for (c, slot) in ins.iter_mut().enumerate().take(if inputs.is_null() { 0 } else { rt.inputs }) {
        *slot = unsafe { std::slice::from_raw_parts(*inputs.add(c), n) };
    }
    let mut outs: [&mut [f32]; 2] = [&mut [], &mut []];
    for (c, slot) in outs.iter_mut().enumerate().take(rt.outputs) {
        *slot = unsafe { std::slice::from_raw_parts_mut(*outputs.add(c), n) };
    }
    let n_in = if inputs.is_null() { 0 } else { rt.inputs };
    if !fill_events(&mut rt.events, events, num_events) { return -1; }
    match rt.endpoint.process_audio_f32(&context(n, t, rt.sr), &ins[..n_in], &mut outs[..rt.outputs],
                                        &[], &rt.events, &mut rt.produced) {
        Ok(RealtimeOutput::Processed) => 0,
        Ok(_) => 1,
        Err(_) => -1,
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_rt_status_json(b: *mut Bridge, out: *mut c_char, len: usize) -> i32 {
    let b = unsafe { &mut *b };
    let exited = b.chain.helper_monitor().exit_status().is_some();
    let s = match b.chain.realtime_status() {
        Some(st) => serde_json::json!({"running": st.running, "callbacks": st.callbacks,
            "processed": st.processed, "missed": st.missed, "late": st.late, "failures": st.failures,
            "resync": st.resync, "stalled_ms": st.stalled.as_secs_f64() * 1e3,
            "latency": st.latency, "helper_exited": exited}),
        None => serde_json::json!({"running": false, "helper_exited": exited}),
    };
    write_out(&s.to_string(), out, len)
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_snapshot(b: *mut Bridge) -> i32 {
    let b = unsafe { &mut *b };
    match b.chain.save_state(0, StatePurpose::Project) {
        Ok(state) => { b.snapshot = Some(vec![ChainSlot::new(b.plugin.clone()).with_state(state)]); 0 }
        Err(e) => b.fail(describe(&e)),
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_recover_rt(b: *mut Bridge, recover_ms: *mut f64) -> i32 {
    let b = unsafe { &mut *b };
    let slots = b.snapshot.clone().unwrap_or_else(|| vec![ChainSlot::new(b.plugin.clone())]);
    let t = Instant::now();
    match b.chain.recover_realtime(&slots) {
        Ok(chain) => {
            b.chain = chain;
            if !recover_ms.is_null() { unsafe { *recover_ms = t.elapsed().as_secs_f64() * 1e3 } }
            0
        }
        Err(e) => b.fail(describe(&e)),
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn ph_resync_rt(b: *mut Bridge) -> i32 {
    let b = unsafe { &mut *b };
    match b.chain.resync_realtime() { Ok(_) => 0, Err(e) => b.fail(describe(&e)) }
}
