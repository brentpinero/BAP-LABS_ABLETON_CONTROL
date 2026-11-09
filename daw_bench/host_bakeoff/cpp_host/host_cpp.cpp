// host_cpp — the C++ side of the plugin-hosting bake-off (daw_bench/host_bakeoff).
//
// Runs the shared probe script (see ../README.md) against one plugin with JUCE's
// AudioPluginFormatManager — the hosting layer Tracktion Engine uses — in THIS process.
// Isolation comes from the harness running one host_cpp process per plugin.
//   load -> prepare -> [setPreset .vstpreset] -> render a -> reset, render b (determinism)
//   -> edit one parameter -> render c -> getState -> fresh instance + setState -> render d
// Audio goes to <out_dir>/{a,b,c,d}.wav (32-bit float, stereo); metrics to result.json.
//
// The probe runs on a worker thread while the main thread pumps the JUCE message loop:
// JUCE requires AUv3 instances to be created off the message thread without blocking it, and
// its state calls lock the message manager.
//
// usage: host_cpp <job.json>

#include <JuceHeader.h>
#include <chrono>

using namespace juce;
using Clock = std::chrono::steady_clock;

// Runs fn on the message thread and waits for it. Plugin modules, instances, bus layouts,
// parameters and state are all touched there (some plugins, e.g. Kontakt, start Qt and need
// NSApplication on the main thread); only reset/processBlock run on the worker.
template <typename Fn>
static void onMain (Fn&& fn)
{
    MessageManager::getInstance()->callFunctionOnMessageThread (
        [] (void* f) -> void* { (*static_cast<Fn*> (f))(); return nullptr; }, &fn);
}

static double msSince (Clock::time_point t)
{
    return std::chrono::duration<double, std::milli> (Clock::now() - t).count();
}

struct Note { int pitch, start, dur, vel; };

struct Job
{
    String format, bundle, preset, inputWav, outDir;
    StringArray au;           // type, subtype, manufacturer
    int classIndex = 0, block = 512, frames = 0;
    double sr = 48000.0;
    bool realtime = false;    // tell the plugin it runs in real time (default: offline)
    double bpm = 0.0;         // > 0: send a playing transport at this tempo
    std::vector<Note> notes;
};

static Job parseJob (const var& v)
{
    Job j;
    j.format = v["format"].toString();
    j.bundle = v["bundle"].toString();
    j.classIndex = (int) v.getProperty ("class_index", 0);
    if (auto* a = v["au"].getArray())
        for (auto& s : *a) j.au.add (s.toString());
    j.sr = (double) v["sr"];
    j.block = (int) v["block"];
    j.frames = (int) v["frames"];
    j.inputWav = v["input_wav"].toString();
    j.preset = v["preset"].toString();
    j.outDir = v["out_dir"].toString();
    j.realtime = (bool) v.getProperty ("realtime", false);
    j.bpm = (double) v.getProperty ("bpm", 0.0);
    if (auto* ns = v["notes"].getArray())
        for (auto& n : *ns)
            j.notes.push_back ({ (int) n["pitch"], (int) n["start"], (int) n["dur"], (int) n["vel"] });
    return j;
}

// A playing transport at a fixed tempo, as the Rust host sends it (tempo, sample and beat position).
struct FixedPlayHead : AudioPlayHead
{
    double bpm = 120.0, sr = 48000.0;
    int64 pos = 0;

    Optional<PositionInfo> getPosition() const override
    {
        PositionInfo info;
        info.setBpm (bpm);
        info.setTimeInSamples (pos);
        info.setTimeInSeconds ((double) pos / sr);
        info.setPpqPosition ((double) pos / sr * bpm / 60.0);
        info.setIsPlaying (true);
        return info;
    }
};

struct Probe
{
    FixedPlayHead playHead;
    Job job;
    DynamicObject::Ptr rep = new DynamicObject();
    AudioPluginFormatManager formats;
    PluginDescription desc;
    bool instrument = false;
    int outs = 2;
    AudioBuffer<float> input;   // effects: stereo, job.frames long

    void set (const char* k, const var& v) { rep->setProperty (k, v); }

    // Finds the plugin class: a VST3 bundle's class, or an Audio Unit by its three codes.
    bool findDescription (String& err)
    {
        OwnedArray<PluginDescription> found;
        for (auto* f : formats.getFormats())
        {
            if (job.format == "au" && f->getName() == "AudioUnit")
                f->findAllTypesForFile (found, "AudioUnit:bakeoff/" + job.au.joinIntoString (","));
            if (job.format == "vst3" && f->getName() == "VST3")
                f->findAllTypesForFile (found, job.bundle);
        }
        if (job.classIndex >= found.size()) { err = "no plugin class found"; return false; }
        desc = *found[job.classIndex];
        return true;
    }

    // Creates an instance through JUCE's async path on the message thread, which works for
    // every format (AUv3 included), and waits here on the worker for the callback.
    std::unique_ptr<AudioPluginInstance> create (String& err)
    {
        WaitableEvent done;
        std::unique_ptr<AudioPluginInstance> instance;
        MessageManager::callAsync ([&]
        {
            formats.createPluginInstanceAsync (desc, job.sr, job.block,
                [&] (std::unique_ptr<AudioPluginInstance> p, const String& e)
                {
                    instance = std::move (p);
                    err = e;
                    done.signal();
                });
        });
        done.wait();
        return instance;
    }

    void start (AudioPluginInstance& p)
    {
        p.setNonRealtime (! job.realtime);   // offline by default, as plughost's ProcessMode::Offline
        p.setRateAndBufferSizeDetails (job.sr, job.block);
        p.prepareToPlay (job.sr, job.block);
    }

    // Stereo out (instruments: no input). Falls back to mono like the Rust host.
    bool prepare (AudioPluginInstance& p)
    {
        for (auto set : { AudioChannelSet::stereo(), AudioChannelSet::mono() })
        {
            AudioProcessor::BusesLayout layout;
            // Instruments that declare a main input (e.g. for sidechain) get it disabled, not dropped:
            // the layout must list every bus the plugin has.
            if (p.getBusCount (true) > 0) layout.inputBuses.add (instrument ? AudioChannelSet::disabled() : set);
            if (p.getBusCount (false) > 0) layout.outputBuses.add (set);
            // Keep any auxiliary buses disabled.
            for (int i = 1; i < p.getBusCount (true); ++i)  layout.inputBuses.add (AudioChannelSet::disabled());
            for (int i = 1; i < p.getBusCount (false); ++i) layout.outputBuses.add (AudioChannelSet::disabled());
            if (p.setBusesLayout (layout))
            {
                outs = set.size();
                start (p);
                return true;
            }
        }
        // Neither layout accepted as asked: keep the plugin's own default layout, as a host would
        // (plughost negotiates per bus; JUCE accepts or rejects the whole layout).
        // Capped at 2: renders are stereo (wider main outputs keep their first two channels).
        outs = jmin (2, p.getBusesLayout().getMainOutputChannels());
        if (outs < 1) return false;
        start (p);
        set ("layout_fallback", p.getBusesLayout().getMainOutputChannelSet().getDescription());
        return true;
    }

    // Fixed-length render in blocks; latency is not trimmed (the Rust host does the same).
    AudioBuffer<float> render (AudioPluginInstance& p, std::vector<double>* times)
    {
        p.reset();
        if (job.bpm > 0.0)
        {
            playHead.bpm = job.bpm;
            playHead.sr = job.sr;
            p.setPlayHead (&playHead);
        }
        AudioBuffer<float> out (2, job.frames);
        out.clear();
        const int chans = jmax (p.getTotalNumInputChannels(), p.getTotalNumOutputChannels(), 2);
        AudioBuffer<float> buf (chans, job.block);
        MidiBuffer midi;
        for (int pos = 0; pos < job.frames; pos += job.block)
        {
            const int n = jmin (job.block, job.frames - pos);
            buf.setSize (chans, n, false, false, true);
            buf.clear();
            if (! instrument)
                for (int c = 0; c < jmin (2, p.getTotalNumInputChannels()); ++c)
                    buf.copyFrom (c, 0, input, c, pos, n);
            midi.clear();
            for (auto& note : job.notes)   // note offs before ons at the same offset
            {
                const int end = note.start + note.dur;
                if (end >= pos && end < pos + n) midi.addEvent (MidiMessage::noteOff (1, note.pitch), end - pos);
            }
            for (auto& note : job.notes)
                if (note.start >= pos && note.start < pos + n)
                    midi.addEvent (MidiMessage::noteOn (1, note.pitch, (uint8) note.vel), note.start - pos);
            playHead.pos = pos;
            auto t = Clock::now();
            p.processBlock (buf, midi);
            if (times) times->push_back (msSince (t));
            for (int c = 0; c < 2; ++c)
                out.copyFrom (c, pos, buf, jmin (c, outs - 1), 0, n);   // mono -> both channels
        }
        return out;
    }

    void writeWav (const String& name, const AudioBuffer<float>& b)
    {
        File f = File (job.outDir).getChildFile (name);
        f.deleteFile();
        WavAudioFormat wav;
        std::unique_ptr<OutputStream> os (f.createOutputStream());
        auto w = wav.createWriterFor (os, AudioFormatWriterOptions{}
                                            .withSampleRate (job.sr).withNumChannels (2)
                                            .withBitsPerSample (32)
                                            .withSampleFormat (AudioFormatWriterOptions::SampleFormat::floatingPoint));
        if (w) w->writeFromAudioSampleBuffer (b, 0, b.getNumSamples());
    }

    bool readInput (String& err)
    {
        WavAudioFormat wav;
        auto r = std::unique_ptr<AudioFormatReader> (wav.createReaderFor (File (job.inputWav).createInputStream().release(), true));
        if (! r) { err = "cannot read input wav"; return false; }
        input.setSize (2, job.frames);
        input.clear();
        r->read (&input, 0, job.frames, 0, true, true);
        return true;
    }

    String run()
    {
        String err;
        File (job.outDir).createDirectory();
        addHeadlessDefaultFormatsToManager (formats);

        set ("stage", "load");
        auto t = Clock::now();
        bool found = false;
        onMain ([&] { found = findDescription (err); });
        if (! found) return err;
        set ("scan_ms", msSince (t));
        t = Clock::now();
        auto plugin = create (err);
        if (! plugin) return "load failed: " + err;
        set ("load_ms", msSince (t));
        instrument = desc.isInstrument;
        set ("name", desc.name);
        set ("vendor", desc.manufacturerName);
        set ("kind", instrument ? "instrument" : "effect");

        set ("stage", "prepare");
        t = Clock::now();
        bool prepared = false;
        onMain ([&] { prepared = prepare (*plugin); });
        if (! prepared) return "no stereo or mono bus layout accepted";
        set ("prepare_ms", msSince (t));
        set ("out_channels", outs);
        set ("latency", plugin->getLatencySamples());

        if (job.preset.isNotEmpty())
        {
            set ("stage", "preset");
            MemoryBlock bytes;
            File (job.preset).loadFileAsData (bytes);
            auto* vst3 = plugin->getVST3Client();
            if (vst3 == nullptr) return "preset given for a plugin that is not a VST3";
            bool accepted = false;
            onMain ([&] { accepted = vst3->setPreset (bytes); });
            if (! accepted) return "setPreset rejected the .vstpreset";
            set ("latency", plugin->getLatencySamples());
        }
        if (! instrument && job.inputWav.isNotEmpty() && ! readInput (err)) return err;

        set ("stage", "render");
        std::vector<double> times;
        times.reserve ((size_t) (job.frames / job.block + 1));   // as the Rust host: no growth mid-render
        t = Clock::now();
        auto a = render (*plugin, &times);
        set ("render_ms", msSince (t));
        writeWav ("a.wav", a);
        std::sort (times.begin(), times.end());
        set ("block_ms_median", times[times.size() / 2]);
        set ("block_ms_p95", times[jmin (times.size() - 1, times.size() * 95 / 100)]);

        set ("stage", "determinism");
        writeWav ("b.wav", render (*plugin, nullptr));

        // State round trip: edit one ordinary parameter so the state differs from the default.
        set ("stage", "state_edit");
        onMain ([&]
        {
            auto& params = plugin->getParameters();
            set ("n_params", params.size());
            for (auto* p : params)
            {
                if (! p->isAutomatable() || p->isMetaParameter() || p == plugin->getBypassParameter()
                    || p->getName (128).toLowerCase().contains ("bypass")) continue;
                const float value = p->getValue() < 0.5f ? 0.75f : 0.25f;
                p->setValueNotifyingHost (value);
                set ("edited_param", p->getName (128));
                set ("edited_value", value);
                break;
            }
        });
        writeWav ("c.wav", render (*plugin, nullptr));

        set ("stage", "state_save");
        MemoryBlock state;
        onMain ([&] { plugin->getStateInformation (state); });
        set ("state_bytes", (int) state.getSize());

        set ("stage", "state_restore");
        t = Clock::now();
        auto fresh = create (err);
        if (! fresh) return "fresh instance failed: " + err;
        onMain ([&]
        {
            fresh->setStateInformation (state.getData(), (int) state.getSize());
            prepared = prepare (*fresh);
        });
        if (! prepared) return "fresh instance rejected the bus layout";
        set ("restore_ms", msSince (t));
        writeWav ("d.wav", render (*fresh, nullptr));

        onMain ([&]      // release and destroy instances on the message thread
        {
            plugin->releaseResources();
            fresh->releaseResources();
            plugin.reset();
            fresh.reset();
        });
        set ("stage", "done");
        set ("ok", true);
        return {};
    }
};

int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI init;
    if (argc < 2) { std::cout << "usage: host_cpp <job.json>\n"; return 2; }

    Probe probe;
    probe.job = parseJob (JSON::parse (File (String (argv[1])).loadFileAsString()));
    probe.set ("host", "cpp_juce");
    probe.set ("ok", false);
    int code = 1;

    // Probe on a worker; the main thread pumps the message loop until it finishes.
    // (runDispatchLoop() returns at once in a macOS console app, so pump explicitly.)
    std::atomic<bool> done { false };
    std::thread worker ([&]
    {
        const String err = probe.run();
        if (err.isNotEmpty()) probe.set ("error", err);
        code = err.isEmpty() ? 0 : 1;
        done = true;
    });
    while (! done)
        MessageManager::getInstance()->runDispatchLoopUntil (5);
    worker.join();

    const String text = JSON::toString (var (probe.rep.get()), true);
    File (probe.job.outDir).getChildFile ("result.json").replaceWithText (text);
    std::cout << text << std::endl;
    return code;
}
