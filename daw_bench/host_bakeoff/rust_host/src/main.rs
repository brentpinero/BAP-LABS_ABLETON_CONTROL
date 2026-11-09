//! host_rs — the Rust side of the plugin-hosting bake-off (daw_bench/host_bakeoff).
//!
//! Runs the shared probe script (see ../README.md) against one plugin through plughost, which
//! loads the plugin in a separate helper process:
//!   load -> prepare -> [import .vstpreset] -> render a -> reset, render b (determinism)
//!   -> edit one parameter -> render c -> save state -> fresh chain with that state -> render d
//! Audio goes to <out_dir>/{a,b,c,d}.wav (32-bit float, stereo); metrics to result.json.
//!
//! usage: host_rs <job.json> <helper executable>

use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::Instant;

use plughost::{
    BlockContext, Chain, ChainSlot, Event, Events, Layout, PluginKind, PluginRef, ProcessMode,
    Scanner, SpawnOptions, StatePurpose, Transport,
};
use serde::Deserialize;
use serde_json::{Value, json};

#[derive(Deserialize)]
struct Note {
    pitch: u8,
    start: usize, // samples
    dur: usize,   // samples
    vel: u8,
}

#[derive(Deserialize)]
struct Job {
    format: String,                     // "vst3" | "au"
    bundle: Option<String>,             // .vst3 bundle path
    class_index: Option<usize>,         // class within the bundle (default 0)
    au: Option<[String; 3]>,            // Audio Unit type, subtype, manufacturer (4-char codes)
    sr: f64,
    block: usize,
    frames: usize,
    input_wav: Option<String>,          // effects: stereo input, exactly `frames` long
    #[serde(default)]
    notes: Vec<Note>,                   // instruments
    preset: Option<String>,             // .vstpreset to import before rendering
    #[serde(default)]
    realtime: bool,
    stop_after: Option<String>,
    bpm: Option<f64>,                   // send a playing transport at this tempo (default: none)         // "a": return after render a (the kill test)                     // tell the plugin it runs in real time (default: offline)
    out_dir: String,
}

/// The stage that is running, so a failure says where it happened.
struct Report {
    out: serde_json::Map<String, Value>,
    path: PathBuf,
}

impl Report {
    fn set(&mut self, key: &str, value: Value) {
        self.out.insert(key.into(), value);
    }
    fn write(&self) {
        let text = serde_json::to_string(&Value::Object(self.out.clone())).unwrap_or_default();
        let _ = std::fs::write(&self.path, &text);
        let _ = writeln!(std::io::stdout(), "{text}");
    }
}

fn ms(t: Instant) -> f64 {
    t.elapsed().as_secs_f64() * 1e3
}

/// Audio Unit class ID as plughost spells it: type, subtype, manufacturer as 24 hex digits.
fn au_class_id(codes: &[String; 3]) -> String {
    codes
        .iter()
        .flat_map(|c| c.as_bytes().iter().take(4).map(|b| format!("{b:02X}")).collect::<Vec<_>>())
        .collect()
}

fn read_input(path: &str, frames: usize) -> Result<[Vec<f32>; 2], String> {
    let mut reader = hound::WavReader::open(path).map_err(|e| e.to_string())?;
    let spec = reader.spec();
    let samples: Vec<f32> = reader.samples::<f32>().collect::<Result<_, _>>().map_err(|e| e.to_string())?;
    let ch = spec.channels as usize;
    let mut out = [vec![0.0f32; frames], vec![0.0f32; frames]];
    for i in 0..frames.min(samples.len() / ch) {
        out[0][i] = samples[i * ch];
        out[1][i] = samples[i * ch + (ch - 1).min(1)];
    }
    Ok(out)
}

fn write_wav(path: &Path, channels: &[Vec<f32>], sr: f64) -> Result<(), String> {
    let spec = hound::WavSpec {
        channels: channels.len() as u16,
        sample_rate: sr as u32,
        bits_per_sample: 32,
        sample_format: hound::SampleFormat::Float,
    };
    let mut w = hound::WavWriter::create(path, spec).map_err(|e| e.to_string())?;
    for i in 0..channels[0].len() {
        for c in channels {
            w.write_sample(c[i]).map_err(|e| e.to_string())?;
        }
    }
    w.finalize().map_err(|e| e.to_string())
}

/// Renders the job's input through a prepared chain in fixed blocks. Latency is not trimmed
/// (the C++ host does the same); per-block wall times are returned for the overhead gate.
fn render(chain: &mut Chain, job: &Job, input: &Option<[Vec<f32>; 2]>, outs: usize)
    -> Result<(Vec<Vec<f32>>, Vec<f64>), String> {
    chain.reset().map_err(|e| describe(&e))?;
    let mut output = vec![vec![0.0f32; job.frames]; outs];
    let mut times = Vec::with_capacity(job.frames / job.block + 1);
    let mut produced = Events::for_block();
    let mut pos = 0;
    while pos < job.frames {
        let n = job.block.min(job.frames - pos);
        // Note on/off events that fall inside this block, in offset order.
        let mut evs: Vec<(usize, u8, u8, bool)> = Vec::new();
        for note in &job.notes {
            if note.start >= pos && note.start < pos + n {
                evs.push((note.start - pos, note.pitch, note.vel, true));
            }
            let end = note.start + note.dur;
            if end >= pos && end < pos + n {
                evs.push((end - pos, note.pitch, 0, false));
            }
        }
        evs.sort_by_key(|e| (e.0, e.3)); // offs before ons at the same offset
        let events: Events = evs
            .iter()
            .map(|&(o, k, v, on)| if on { Event::note_on(o, 0, k, v) } else { Event::note_off(o, 0, k, 0) })
            .collect();
        let ins: Vec<&[f32]> = match input {
            Some(buf) => buf.iter().take(outs).map(|c| &c[pos..pos + n]).collect(),
            None => Vec::new(),
        };
        let mut block_out: Vec<Vec<f32>> = vec![vec![0.0; n]; outs];
        let mut outs_ref: Vec<&mut [f32]> = block_out.iter_mut().map(|c| c.as_mut_slice()).collect();
        // Optional transport: tempo-synced plugins (LFOs, delays) otherwise fall back to their
        // own default tempo. Built before the timed call.
        let mut context = BlockContext::new(n);
        if let Some(bpm) = job.bpm {
            let mut transport = Transport::new(pos as i64, true);
            transport.tempo = Some(bpm);
            transport.beat_position = Some(pos as f64 / job.sr * bpm / 60.0);
            context = context.with_transport(transport);
        }
        let t = Instant::now();
        chain
            .process_audio_f32(&context, &ins, &mut outs_ref, &[], &events, &mut produced)
            .map_err(|e| describe(&e))?;
        times.push(ms(t));
        for (c, buf) in block_out.iter().enumerate() {
            output[c][pos..pos + n].copy_from_slice(buf);
        }
        pos += n;
    }
    // Mono plugins are written as two identical channels so every render is stereo.
    if outs == 1 {
        output.push(output[0].clone());
    }
    Ok((output, times))
}

/// Prepares a chain: stereo in/out for effects, no input for instruments; mono as a fallback.
fn prepare(chain: &mut Chain, instrument: bool, job: &Job) -> Result<usize, String> {
    let mut last = String::new();
    let mode = if job.realtime { ProcessMode::Realtime } else { ProcessMode::Offline };
    for layout in [Layout::Stereo, Layout::Mono] {
        let input = if instrument { Layout::None } else { layout };
        let config = match chain.main_bus_config(job.sr, job.block, input, &[layout]) {
            Ok(c) => c.with_mode(mode),
            Err(e) => {
                last = describe(&e);
                continue;
            }
        };
        match chain.prepare_audio(&config) {
            Ok(_) => return Ok(layout.channels()),
            Err(e) => last = describe(&e),
        }
    }
    Err(last)
}

fn run(job: &Job, helper: &Path, rep: &mut Report) -> Result<(), String> {
    let out = PathBuf::from(&job.out_dir);
    std::fs::create_dir_all(&out).map_err(|e| e.to_string())?;

    rep.set("stage", json!("load"));
    let t = Instant::now();
    let plugin: PluginRef = match job.format.as_str() {
        "au" => PluginRef::audio_unit(au_class_id(job.au.as_ref().ok_or("au job without codes")?)),
        _ => {
            let bundle = job.bundle.as_ref().ok_or("vst3 job without bundle")?;
            let cache = std::env::temp_dir().join(format!("bakeoff-scan-{}.json", std::process::id()));
            let scanned = Scanner::new(helper, &cache).retry(Path::new(bundle)).map_err(|e| describe(&e))?;
            let _ = std::fs::remove_file(&cache);
            scanned
                .plugins()
                .into_iter()
                .nth(job.class_index.unwrap_or(0))
                .map(|(p, _)| p)
                .ok_or(format!("no class in bundle: {:?}", scanned.outcome))?
        }
    };
    rep.set("scan_ms", json!(ms(t)));
    let t = Instant::now();
    let mut chain = Chain::spawn(helper, &[ChainSlot::new(plugin.clone())], &SpawnOptions::default())
        .map_err(|e| describe(&e))?;
    rep.set("load_ms", json!(ms(t)));
    let info = chain.plugins()[0].clone();
    let instrument = info.kind == PluginKind::Instrument;
    rep.set("name", json!(info.name));
    rep.set("vendor", json!(info.vendor));
    rep.set("kind", json!(if instrument { "instrument" } else { "effect" }));

    rep.set("stage", json!("prepare"));
    let t = Instant::now();
    let outs = prepare(&mut chain, instrument, job)?;
    rep.set("prepare_ms", json!(ms(t)));
    rep.set("out_channels", json!(outs));
    rep.set("latency", json!(chain.latency()));

    if let Some(preset) = &job.preset {
        rep.set("stage", json!("preset"));
        let bytes = std::fs::read(preset).map_err(|e| e.to_string())?;
        chain.import_preset(0, &bytes).map_err(|e| describe(&e))?;
        rep.set("latency", json!(chain.latency()));
    }

    let input = match (&job.input_wav, instrument) {
        (Some(p), false) => Some(read_input(p, job.frames)?),
        _ => None,
    };

    // Last known good state, as an engine keeps it: if the helper dies mid-render, recover the
    // chain in a new helper from this snapshot and render again (the crash-isolation gate).
    let snapshot = chain.snapshot().ok();
    rep.set("stage", json!("render"));
    let t = Instant::now();
    let (a, mut times) = match render(&mut chain, job, &input, outs) {
        Ok(r) => r,
        Err(e) => {
            let monitor = chain.helper_monitor();
            let _ = monitor.wait_for_exit(std::time::Duration::from_millis(200));
            let Some(snap) = snapshot.as_ref().filter(|_| monitor.exit_status().is_some()) else {
                return Err(e);
            };
            rep.set("crash_error", json!(e));
            let r = Instant::now();
            chain = chain.recover(&snap.slots).map_err(|e| describe(&e))?;
            rep.set("recover_ms", json!(ms(r)));
            rep.set("recovered", json!(true));
            render(&mut chain, job, &input, outs)?
        }
    };
    rep.set("render_ms", json!(ms(t)));
    write_wav(&out.join("a.wav"), &a, job.sr)?;
    if job.stop_after.as_deref() == Some("a") {
        rep.set("stage", json!("done"));
        rep.set("ok", json!(true));
        return Ok(());
    }
    times.sort_by(|x, y| x.total_cmp(y));
    rep.set("block_ms_median", json!(times[times.len() / 2]));
    rep.set("block_ms_p95", json!(times[(times.len() * 95 / 100).min(times.len() - 1)]));

    rep.set("stage", json!("determinism"));
    let (b, _) = render(&mut chain, job, &input, outs)?;
    write_wav(&out.join("b.wav"), &b, job.sr)?;

    // State round trip: edit one ordinary parameter so the state differs from the default.
    rep.set("stage", json!("state_edit"));
    let params = chain.parameters(0).map_err(|e| describe(&e))?;
    rep.set("n_params", json!(params.len()));
    let pick = params.iter().find(|(p, v)| {
        p.flags.automatable && !p.flags.read_only && !p.flags.bypass && !p.flags.hidden
            && !p.flags.program_change && v.is_some()
            && !p.title.to_lowercase().contains("bypass")
    });
    if let Some((p, v)) = pick {
        let value = if v.unwrap_or(0.0) < 0.5 { 0.75 } else { 0.25 };
        chain.set_parameter(0, p.id, value).map_err(|e| describe(&e))?;
        rep.set("edited_param", json!(p.title));
        rep.set("edited_value", json!(value));
    }
    let (c, _) = render(&mut chain, job, &input, outs)?;
    write_wav(&out.join("c.wav"), &c, job.sr)?;

    rep.set("stage", json!("state_save"));
    let state = chain.save_state(0, StatePurpose::Project).map_err(|e| describe(&e))?;
    rep.set("state_bytes", json!(state.to_bytes().len()));

    rep.set("stage", json!("state_restore"));
    let t = Instant::now();
    let mut fresh = Chain::spawn(helper, &[ChainSlot::new(plugin).with_state(state)], &SpawnOptions::default())
        .map_err(|e| describe(&e))?;
    prepare(&mut fresh, instrument, job)?;
    rep.set("restore_ms", json!(ms(t)));
    let (d, _) = render(&mut fresh, job, &input, outs)?;
    write_wav(&out.join("d.wav"), &d, job.sr)?;

    rep.set("stage", json!("done"));
    rep.set("ok", json!(true));
    Ok(())
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

fn main() -> std::process::ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let (Some(job_path), Some(helper)) = (args.first(), args.get(1)) else {
        let _ = writeln!(std::io::stdout(), "usage: host_rs <job.json> <helper executable>");
        return std::process::ExitCode::from(2);
    };
    let job: Job = match std::fs::read_to_string(job_path)
        .map_err(|e| e.to_string())
        .and_then(|t| serde_json::from_str(&t).map_err(|e| e.to_string()))
    {
        Ok(j) => j,
        Err(e) => {
            let _ = writeln!(std::io::stdout(), "{}", json!({"ok": false, "error": e}));
            return std::process::ExitCode::from(2);
        }
    };
    let mut rep = Report {
        out: serde_json::Map::new(),
        path: PathBuf::from(&job.out_dir).join("result.json"),
    };
    rep.set("host", json!("rust_plughost"));
    rep.set("ok", json!(false));
    let _ = std::fs::create_dir_all(&job.out_dir);
    let code = match run(&job, Path::new(helper), &mut rep) {
        Ok(()) => 0,
        Err(e) => {
            rep.set("error", json!(e));
            1
        }
    };
    rep.write();
    std::process::ExitCode::from(code)
}
