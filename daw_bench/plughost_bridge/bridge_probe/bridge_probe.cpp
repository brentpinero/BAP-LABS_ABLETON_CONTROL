/*
    bridge_probe — Phase 1 spike: Tracktion Engine hosting plugins out of process through
    plughost (Rust), via a custom JUCE AudioPluginFormat ("Plughost") and the C ABI in
    ../plughost_bridge.h. Tracktion sees ordinary ExternalPlugins; delay compensation,
    automation and transport all go through Tracktion's own code.

    The bridged instance has two audio paths:
      offline (the Renderer sets setNonRealtime(true)): blocking ph_process per block
      realtime (playback):                             plughost's RealtimeEndpoint, one call per
                                                       quantum, never blocking the audio thread
    and reports each path's latency to Tracktion (the endpoint adds latency_quanta * quantum).

    usage: bridge_probe job.json      (prints a JSON report on stdout)
    job: { "mode": "offline" | "realtime",
           "plugin": "bridge" | "native",              native = in-process VST3 (the control)
           "bundle": "/Library/.../Serum2.vst3", "class_name": "Serum 2", "class_id": "<32 hex>",
           "component_state": path?,  "tracks": N, "sample_rate": 44100, "block": 128,
           "tempo": 126, "seconds": 8, "output": "out.wav",
           "helper": "<plughost-helper executable>", "latency_quanta": 1 }
*/

#include <JuceHeader.h>
#include "../plughost_bridge.h"
#include <atomic>
#include <chrono>
#include <mach/mach.h>
#include <mach/mach_time.h>
#include <mach/thread_policy.h>
#include <pthread.h>
#include <iostream>
#include <thread>

namespace te = tracktion;
using Clock = std::chrono::steady_clock;

//==============================================================================
// A JUCE plugin instance whose processing runs in a plughost helper process.
class PlughostInstance : public juce::AudioPluginInstance
{
public:
    PlughostInstance (juce::String spec, juce::String helper, ph_bridge* b, juce::var info,
                      double sr, int block)
        : juce::AudioPluginInstance (busesFor (info)), spec (std::move (spec)), helper (std::move (helper)),
          bridge (b), info (std::move (info)), openRate (sr), openBlock (block)
    {
        events.reserve (4096);
        setLatencySamples ((int) this->info["latency"]);
        instances().add (this);
    }

    ~PlughostInstance() override
    {
        if (recoveryThread.joinable()) recoveryThread.join();
        instances().removeFirstMatchingValue (this);
        closeRt();
        ph_close (bridge);
    }

    static juce::Array<PlughostInstance*>& instances() { static juce::Array<PlughostInstance*> a; return a; }

    static BusesProperties busesFor (const juce::var& info)
    {
        BusesProperties b;
        const int outs = (int) info["outputs"], ins = (int) info["inputs"];
        if (ins > 0) b = b.withInput ("Input", juce::AudioChannelSet::canonicalChannelSet (ins), true);
        return b.withOutput ("Output", juce::AudioChannelSet::canonicalChannelSet (juce::jmax (1, outs)), true);
    }

    //==============================================================================
    const juce::String getName() const override             { return info["name"].toString(); }
    bool acceptsMidi() const override                        { return (bool) info["instrument"]; }
    bool producesMidi() const override                       { return false; }
    double getTailLengthSeconds() const override             { return 0.0; }
    bool hasEditor() const override                          { return false; }
    juce::AudioProcessorEditor* createEditor() override      { return nullptr; }
    int getNumPrograms() override                            { return 1; }
    int getCurrentProgram() override                         { return 0; }
    void setCurrentProgram (int) override                    {}
    const juce::String getProgramName (int) override         { return {}; }
    void changeProgramName (int, const juce::String&) override {}
    void getStateInformation (juce::MemoryBlock&) override   {}   // spike: state = the job spec
    void setStateInformation (const void*, int) override     {}

    void fillInPluginDescription (juce::PluginDescription& d) const override
    {
        d.name = d.descriptiveName = getName();
        d.pluginFormatName = "Plughost";
        d.fileOrIdentifier = spec;
        d.manufacturerName = info["vendor"].toString();
        d.isInstrument = (bool) info["instrument"];
        d.uniqueId = d.deprecatedUid = spec.hashCode();
        d.numInputChannels = (int) info["inputs"];
        d.numOutputChannels = (int) info["outputs"];
    }

    // Tracktion's Renderer calls this AFTER prepareToPlay, so an offline render arrives with the
    // realtime endpoint already running (plughost refuses blocking processing while it runs), and
    // with delay compensation already built from the realtime latency, which Tracktion does not
    // re-read. So: stop the endpoint here, and keep ONE latency for both paths: the offline path
    // delays its output by the endpoint's extra latency (latency_quanta * quantum).
    void setNonRealtime (bool offline) noexcept override
    {
        juce::AudioPluginInstance::setNonRealtime (offline);
        if (offline)
            closeRt();
    }

    //==============================================================================
    void prepareToPlay (double sr, int block) override
    {
        closeRt();
        if (sr != openRate || block > openBlock)
            reopen (sr, block);

        // One latency for both paths: the chain's plus the endpoint's extra quanta.
        quantum = block;
        extra = latencyQuanta * quantum;
        delay.setSize (2, extra + 8192);
        delay.clear();
        delayPos = 0;
        setLatencySamples ((int) info["latency"] + extra);
        if (isNonRealtime())
            return;
        // Realtime: one endpoint call per quantum = the engine's block size.
        rt = ph_rt_open (bridge, (uint32_t) quantum, latencyQuanta);
        uint32_t total = 0;
        if (rt == nullptr || ph_rt_start (bridge, &total) != 0)
            DBG ("plughost realtime start failed: " << ph_last_error (bridge));
        jassert ((int) total == getLatencySamples());
        ph_snapshot (bridge);
    }

    void releaseResources() override { closeRt(); }

    void processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midi) override
    {
        const int n = buffer.getNumSamples();
        events.clear();
        for (const auto m : midi)
            if (m.numBytes <= 3 && events.size() < events.capacity())
                events.push_back ({ (uint32_t) m.samplePosition, m.data[0],
                                    m.numBytes > 1 ? m.data[1] : (uint8_t) 0,
                                    m.numBytes > 2 ? m.data[2] : (uint8_t) 0, 0 });

        ph_transport t { 0.0, 0, 0 };
        if (auto* ph = getPlayHead())
            if (auto pos = ph->getPosition())
            {
                t.tempo = pos->getBpm().orFallback (0.0);
                t.sample_position = pos->getTimeInSamples().orFallback (0);
                t.playing = pos->getIsPlaying() ? 1 : 0;
            }

        const int ins = (int) info["inputs"], outs = (int) info["outputs"];
        const float* in[2] = { buffer.getReadPointer (0), buffer.getReadPointer (juce::jmin (1, buffer.getNumChannels() - 1)) };
        float* out[2] = { scratch.getWritePointer (0), scratch.getWritePointer (1) };
        scratch.setSize (2, n, false, false, true);
        out[0] = scratch.getWritePointer (0);
        out[1] = scratch.getWritePointer (1);

        int r;
        if (isNonRealtime() || rt == nullptr)
        {
            r = ph_process (bridge, ins > 0 ? in : nullptr, out, (uint32_t) n, events.data(), (uint32_t) events.size(), t);
            delayBy (n);   // match the realtime path's latency
        }
        else
        {
            r = (n == quantum) ? ph_rt_process (rt, ins > 0 ? in : nullptr, out, (uint32_t) n,
                                                events.data(), (uint32_t) events.size(), t)
                               : -2;   // a block of another size: plughost would resync
            if (r == 1) fallbacks.fetch_add (1);
            if (r == -2) { sizeMismatches.fetch_add (1); scratch.clear(); }
        }
        if (r < 0 && r != -2) { errors.fetch_add (1); scratch.clear(); }

        for (int c = 0; c < buffer.getNumChannels(); ++c)
            buffer.copyFrom (c, 0, scratch, juce::jmin (c, outs - 1), 0, n);
    }

    //==============================================================================
    // Control thread: recover the realtime chain from the snapshot after a crash or hang.
    juce::var pollAndRecover (double hangMs)
    {
        char buf[1024];
        ph_rt_status_json (bridge, buf, sizeof (buf));
        auto st = juce::JSON::parse (juce::String (buf));
        if (((bool) st["helper_exited"] || (double) st["stalled_ms"] > hangMs)
            && recoveries.size() < 3 && ! recovering.exchange (true))
        {
            if (recoveries.isEmpty())
            {
                errorsAtExit = errors.load();
                statusAtExit = st;
                hadRt = rt != nullptr;
            }
            // Each chain recovers on its own thread, so several crashed tracks come back together.
            if (recoveryThread.joinable()) recoveryThread.join();
            recoveryThread = std::thread ([this]
            {
                double ms = -1;
                const int r = ph_recover_rt (bridge, &ms);
                const juce::ScopedLock sl (recoveryLock);
                recoveries.add (juce::var (r == 0 ? ms : -1.0));
                if (r != 0)
                    recoveryErrors.add (juce::String (juce::CharPointer_UTF8 (ph_last_error (bridge))));
                recovering = false;
            });
        }
        return st;
    }

    // Called once when warm-up ends: later reports give missed/late since then.
    void markWarm()
    {
        char buf[1024];
        ph_rt_status_json (bridge, buf, sizeof (buf));
        warm = juce::JSON::parse (juce::String (buf));
        errorsAtWarm = errors.load();
    }

    juce::var report()
    {
        if (recoveryThread.joinable()) recoveryThread.join();
        const juce::ScopedLock sl (recoveryLock);
        char buf[1024];
        ph_rt_status_json (bridge, buf, sizeof (buf));
        auto* o = new juce::DynamicObject();
        auto st = juce::JSON::parse (juce::String (buf));
        o->setProperty ("status", st);
        if (warm.isObject())
        {
            o->setProperty ("missed_after_warmup", (int) st["missed"] - (int) warm["missed"]);
            o->setProperty ("late_after_warmup", (int) st["late"] - (int) warm["late"]);
        }
        o->setProperty ("fallbacks", (int) fallbacks.load());
        o->setProperty ("size_mismatches", (int) sizeMismatches.load());
        o->setProperty ("errors", (int) errors.load());
        o->setProperty ("latency", getLatencySamples());
        o->setProperty ("recoveries_ms", recoveries);
        o->setProperty ("recovery_errors", recoveryErrors);
        o->setProperty ("errors_at_warm", errorsAtWarm);
        o->setProperty ("errors_at_exit", errorsAtExit);
        o->setProperty ("status_at_exit", statusAtExit);
        o->setProperty ("had_rt_at_exit", hadRt);
        return o;
    }

    static int latencyQuanta;

private:
    // Delays scratch[0..n) by `extra` samples through a circular buffer.
    void delayBy (int n)
    {
        if (extra <= 0) return;
        const int size = delay.getNumSamples();
        for (int c = 0; c < 2; ++c)
        {
            auto* d = delay.getWritePointer (c);
            auto* x = scratch.getWritePointer (c);
            for (int i = 0; i < n; ++i)
            {
                const int w = (delayPos + i) % size;
                const int r = (w - extra + size) % size;
                d[w] = x[i];
                x[i] = d[r];
            }
        }
        delayPos = (delayPos + n) % size;
    }

    void closeRt()
    {
        if (rt != nullptr) { ph_rt_stop (bridge); ph_rt_close (rt); rt = nullptr; }
    }

    void reopen (double sr, int block)
    {
        auto job = juce::JSON::parse (spec.fromFirstOccurrenceOf ("plughost:", false, false));
        job.getDynamicObject()->setProperty ("sr", sr);
        job.getDynamicObject()->setProperty ("block", block);
        char err[1024] = {};
        if (auto* b = ph_open (helper.toRawUTF8(), juce::JSON::toString (job, true).toRawUTF8(), err, sizeof (err)))
        {
            ph_close (bridge);
            bridge = b;
            openRate = sr;
            openBlock = block;
            char buf[1024];
            ph_info_json (bridge, buf, sizeof (buf));
            info = juce::JSON::parse (juce::String (buf));
        }
        else
            DBG ("plughost reopen failed: " << err);
    }

    juce::String spec, helper;
    ph_bridge* bridge = nullptr;
    ph_rt* rt = nullptr;
    juce::var info;
    double openRate = 0;
    int openBlock = 0, quantum = 0, extra = 0, delayPos = 0;
    juce::AudioBuffer<float> delay { 2, 8192 };
    std::vector<ph_midi> events;
    juce::AudioBuffer<float> scratch { 2, 4096 };
    std::atomic<int> fallbacks { 0 }, sizeMismatches { 0 }, errors { 0 };
    juce::Array<juce::var> recoveries;
    juce::StringArray recoveryErrors;
    std::atomic<bool> recovering { false };
    std::thread recoveryThread;
    juce::CriticalSection recoveryLock;
    juce::var warm, statusAtExit;
    int errorsAtWarm = -1, errorsAtExit = -1;
    bool hadRt = false;
};

int PlughostInstance::latencyQuanta = 1;

//==============================================================================
// fileOrIdentifier = "plughost:" + JSON job for ph_open (without sr/block).
class PlughostFormat : public juce::AudioPluginFormat
{
public:
    explicit PlughostFormat (juce::String helperPath) : helper (std::move (helperPath)) {}

    juce::String getName() const override { return "Plughost"; }

    void findAllTypesForFile (juce::OwnedArray<juce::PluginDescription>& results, const juce::String& id) override
    {
        if (! fileMightContainThisPluginType (id)) return;
        auto d = std::make_unique<juce::PluginDescription>();
        d->pluginFormatName = getName();
        d->fileOrIdentifier = id;
        d->name = getNameOfPluginFromIdentifier (id);
        d->uniqueId = d->deprecatedUid = id.hashCode();
        results.add (d.release());
    }

    bool fileMightContainThisPluginType (const juce::String& id) override { return id.startsWith ("plughost:"); }
    juce::String getNameOfPluginFromIdentifier (const juce::String& id) override
    {
        return juce::JSON::parse (id.fromFirstOccurrenceOf ("plughost:", false, false))["class_name"].toString();
    }
    bool pluginNeedsRescanning (const juce::PluginDescription&) override { return false; }
    bool doesPluginStillExist (const juce::PluginDescription&) override  { return true; }
    bool canScanForPlugins() const override                              { return false; }
    bool isTrivialToScan() const override                                { return true; }
    juce::StringArray searchPathsForPlugins (const juce::FileSearchPath&, bool, bool) override { return {}; }
    juce::FileSearchPath getDefaultLocationsToSearch() override         { return {}; }
    bool requiresUnblockedMessageThreadDuringCreation (const juce::PluginDescription&) const override { return false; }

    void createPluginInstance (const juce::PluginDescription& d, double sr, int block,
                               PluginCreationCallback callback) override
    {
        auto job = juce::JSON::parse (d.fileOrIdentifier.fromFirstOccurrenceOf ("plughost:", false, false));
        job.getDynamicObject()->setProperty ("sr", sr);
        job.getDynamicObject()->setProperty ("block", juce::jmax (block, 4096));   // room for any block size
        char err[1024] = {};
        auto* b = ph_open (helper.toRawUTF8(), juce::JSON::toString (job, true).toRawUTF8(), err, sizeof (err));
        if (b == nullptr) { callback (nullptr, "plughost: " + juce::String (juce::CharPointer_UTF8 (err))); return; }
        char buf[1024];
        ph_info_json (b, buf, sizeof (buf));
        callback (std::make_unique<PlughostInstance> (d.fileOrIdentifier, helper, b,
                                                      juce::JSON::parse (juce::String (buf)), sr, juce::jmax (block, 4096)),
                  {});
    }

private:
    juce::String helper;
};

//==============================================================================
struct HeadlessUI : public te::UIBehaviour
{
    void runTaskWithProgressBar (te::ThreadPoolJobWithProgress& task) override
    {
        while (task.runJob() == juce::ThreadPoolJob::jobNeedsRunningAgain) {}
    }
    void showWarningMessage (const juce::String& m) override { std::cerr << "warning: " << m << "\n"; }
};

static juce::MemoryBlock vstpreset (const juce::String& classId, const juce::MemoryBlock& comp)
{
    juce::MemoryOutputStream o;
    o.write ("VST3", 4); o.writeInt (1); o.write (classId.toRawUTF8(), 32);
    o.writeInt64 (48 + (juce::int64) comp.getSize());
    o.write (comp.getData(), comp.getSize());
    o.write ("List", 4); o.writeInt (1); o.write ("Comp", 4);
    o.writeInt64 (48); o.writeInt64 ((juce::int64) comp.getSize());
    return o.getMemoryBlock();
}

static void printJson (const juce::var& v) { std::cout << juce::JSON::toString (v, true) << std::endl; }

int run (const juce::var& job)
{
    const juce::String mode = job["mode"], kind = job["plugin"];
    const double sr = job.getProperty ("sample_rate", 44100.0), tempo = job.getProperty ("tempo", 120.0),
                 seconds = job.getProperty ("seconds", 8.0);
    const int block = job.getProperty ("block", 128), numTracks = job.getProperty ("tracks", 1);
    const juce::String helper = job["helper"].toString();
    PlughostInstance::latencyQuanta = job.getProperty ("latency_quanta", 1);

    te::Engine engine { "bridge_probe", std::make_unique<HeadlessUI>(), std::make_unique<te::EngineBehaviour>() };
    auto& pm = engine.getPluginManager();
    pm.pluginFormatManager.addFormat (std::make_unique<PlughostFormat> (helper));

    auto& hosted = engine.getDeviceManager().getHostedAudioDeviceInterface();
    if (mode == "realtime")
    {
        te::HostedAudioDeviceInterface::Parameters p;
        p.sampleRate = sr; p.blockSize = block; p.inputChannels = 0; p.outputChannels = 2;
        hosted.initialise (p);
    }

    // The plugin description: bridged (Plughost format) or native in-process VST3 (control).
    juce::PluginDescription desc;
    if (kind == "bridge")
    {
        auto* spec = new juce::DynamicObject();
        spec->setProperty ("format", "vst3");
        spec->setProperty ("bundle", job["bundle"]);
        spec->setProperty ("class_name", job["class_name"]);
        spec->setProperty ("realtime", mode == "realtime");
        if (job.hasProperty ("component_state")) spec->setProperty ("component_state", job["component_state"]);
        juce::OwnedArray<juce::PluginDescription> found;
        pm.pluginFormatManager.getFormat (pm.pluginFormatManager.getNumFormats() - 1)
            ->findAllTypesForFile (found, "plughost:" + juce::JSON::toString (juce::var (spec), true));
        desc = *found[0];
    }
    else
    {
        juce::OwnedArray<juce::PluginDescription> found;
        for (auto* f : pm.pluginFormatManager.getFormats())
            if (f->getName() == "VST3") f->findAllTypesForFile (found, job["bundle"].toString());
        for (auto* d : found)
            if (d->name == job["class_name"].toString()) desc = *d;
    }
    pm.knownPluginList.addType (desc);

    auto edit = te::Edit::createSingleTrackEdit (engine, mode == "realtime" ? te::Edit::EditRole::forEditing
                                                                            : te::Edit::EditRole::forRendering);
    edit->ensureNumberOfAudioTracks (numTracks);
    edit->tempoSequence.getTempo (0)->setBpm (tempo);
    edit->getMasterVolumePlugin()->setVolumeDb (0.0f);

    juce::MemoryBlock comp;
    if (job.hasProperty ("component_state")) juce::File (job["component_state"].toString()).loadFileAsData (comp);

    auto tracks = te::getAudioTracks (*edit);
    for (auto* track : tracks)
    {
        // One MIDI clip: a note on every beat (alternating pitch) for the whole length.
        auto clip = track->insertMIDIClip ({ te::TimePosition(), te::TimeDuration::fromSeconds (seconds) }, nullptr);
        const int beats = (int) (seconds * tempo / 60.0);
        for (int b = 0; b < beats; ++b)
            clip->getSequence().addNote (b % 2 ? 41 : 36, te::BeatPosition::fromBeats (b),
                                         te::BeatDuration::fromBeats (0.75), 100, 0, nullptr);
        auto plugin = edit->getPluginCache().createNewPlugin (te::ExternalPlugin::xmlTypeName, desc);
        track->pluginList.insertPlugin (plugin, 0, nullptr);
        if (auto* ext = dynamic_cast<te::ExternalPlugin*> (plugin.get()))
        {
            if (ext->getAudioPluginInstance() == nullptr)
                return std::cerr << "plugin failed to load: " << ext->getLoadError() << "\n", 1;
            if (kind == "native" && comp.getSize() > 0)
                if (auto* v3 = ext->getAudioPluginInstance()->getVST3Client())
                    v3->setPreset (vstpreset (job["class_id"].toString(), comp));
        }
    }

    const juce::File outFile (job["output"].toString());
    outFile.deleteFile();
    auto* report = new juce::DynamicObject();
    report->setProperty ("mode", mode);
    report->setProperty ("plugin", kind);
    report->setProperty ("tracks", numTracks);

    if (mode == "offline")
    {
        te::Renderer::Parameters params (*edit);
        params.destFile = outFile;
        params.audioFormat = engine.getAudioFileFormatManager().getWavFormat();
        params.bitDepth = 32;
        params.sampleRateForAudio = sr;
        params.blockSizeForAudio = block;
        params.time = te::TimeRange (te::TimePosition(), te::TimeDuration::fromSeconds (seconds));
        params.tracksToDo = te::toBitSet (te::getAllTracks (*edit));
        const auto t0 = Clock::now();
        const auto rendered = te::Renderer::renderToFile ("bridge", params);
        report->setProperty ("render_s", std::chrono::duration<double> (Clock::now() - t0).count());
        report->setProperty ("ok", rendered.existsAsFile());
        juce::Array<juce::var> per;
        for (auto* inst : PlughostInstance::instances()) per.add (inst->report());
        report->setProperty ("bridged", per);
        printJson (report);
        return rendered.existsAsFile() ? 0 : 1;
    }

    // Realtime: drive the hosted device from a thread paced to wall-clock time, one block per
    // period, as an audio device would; a control thread recovers bridged plugins that crash.
    // As Tracktion's EngineInPluginDemo: allocate the playback context on the hosted device
    // (forced, after the edit is built) and restart playback before playing.
    hosted.prepareToPlay (sr, block);
    edit->playInStopEnabled = true;
    edit->getTransport().ensureContextAllocated (true);
    edit->restartPlayback();
    edit->getTransport().setPosition (te::TimePosition());
    // restartPlayback rebuilds the context asynchronously: pump messages until play() sticks.
    for (int i = 0; i < 300 && ! edit->getTransport().isPlaying(); ++i)
    {
        juce::MessageManager::getInstance()->runDispatchLoopUntil (10);
        edit->getTransport().play (false);
    }
    if (! edit->getTransport().isPlaying())
        return std::cerr << "transport did not start\n", 1;
    // Lets an external test (the kill test) act only once playback is running.
    if (job.hasProperty ("playing_marker"))
        juce::File (job["playing_marker"].toString()).replaceWithText ("playing");

    const double period = block / sr;
    const int callbacks = (int) (seconds / period);
    std::vector<float> rec ((size_t) callbacks * block * 2);
    std::vector<double> cbMs ((size_t) callbacks);
    std::atomic<bool> done { false }, warmMarked { false };
    int overruns = 0, overrunsWarmup = 0;
    const double warmupS = job.getProperty ("warmup_s", 1.0);
    const int warmCallbacks = (int) (warmupS / period);

    std::thread control ([&]
    {
        const auto start = Clock::now();
        while (! done)
        {
            if (! warmMarked && std::chrono::duration<double> (Clock::now() - start).count() >= warmupS)
            {
                for (auto* inst : PlughostInstance::instances()) inst->markWarm();
                warmMarked = true;
            }
            for (auto* inst : PlughostInstance::instances()) inst->pollAndRecover (300.0);
            std::this_thread::sleep_for (std::chrono::milliseconds (50));
        }
    });

    std::thread audio ([&]
    {
        // Real-time scheduling like a CoreAudio IO thread (and plughost's helper worker): the
        // time-constraint policy with period = one block and a computation budget of half of it.
        {
            mach_timebase_info_data_t tb;
            mach_timebase_info (&tb);
            const auto toAbs = [&] (double s) { return (uint32_t) (s * 1e9 * tb.denom / tb.numer); };
            thread_time_constraint_policy_data_t policy { toAbs (period), toAbs (period * 0.5),
                                                          toAbs (period), 1 };
            const auto kr = thread_policy_set (pthread_mach_thread_np (pthread_self()), THREAD_TIME_CONSTRAINT_POLICY,
                                               (thread_policy_t) &policy, THREAD_TIME_CONSTRAINT_POLICY_COUNT);
            report->setProperty ("rt_policy", kr == KERN_SUCCESS);
        }
        juce::AudioBuffer<float> buf (2, block);
        juce::MidiBuffer midi;
        auto next = Clock::now();
        for (int i = 0; i < callbacks; ++i)
        {
            std::this_thread::sleep_until (next);
            const auto t = Clock::now();
            buf.clear();
            midi.clear();
            hosted.processBlock (buf, midi);
            const double ms = std::chrono::duration<double, std::milli> (Clock::now() - t).count();
            cbMs[(size_t) i] = ms;
            if (ms > period * 1e3) (i < warmCallbacks ? overrunsWarmup : overruns)++;
            for (int s = 0; s < block; ++s)
                for (int c = 0; c < 2; ++c)
                    rec[((size_t) i * block + s) * 2 + c] = buf.getSample (c, s);
            next += std::chrono::duration_cast<Clock::duration> (std::chrono::duration<double> (period));
        }
        done = true;
    });

    while (! done) juce::MessageManager::getInstance()->runDispatchLoopUntil (10);
    audio.join();
    control.join();
    // Diagnostics: did the edit actually play on the hosted device?
    report->setProperty ("transport_playing", edit->getTransport().isPlaying());
    report->setProperty ("transport_position_s", edit->getTransport().getPosition().inSeconds());
    if (auto* dev = engine.getDeviceManager().deviceManager.getCurrentAudioDevice())
        report->setProperty ("audio_device", dev->getTypeName() + "/" + dev->getName());
    if (auto* out = engine.getDeviceManager().getDefaultWaveOutDevice())
        report->setProperty ("default_wave_out", out->getName() + (out->isEnabled() ? " (enabled)" : " (disabled)"));
    edit->getTransport().stop (false, false);

    std::vector<double> sorted (cbMs);
    std::sort (sorted.begin(), sorted.end());
    report->setProperty ("block", block);
    report->setProperty ("period_ms", period * 1e3);
    report->setProperty ("callbacks", callbacks);
    report->setProperty ("overruns", overruns);                 // after warm-up
    report->setProperty ("overruns_warmup", overrunsWarmup);
    report->setProperty ("warmup_s", warmupS);
    report->setProperty ("cb_ms_median", sorted[sorted.size() / 2]);
    report->setProperty ("cb_ms_p99", sorted[(size_t) (sorted.size() * 0.99)]);
    report->setProperty ("cb_ms_max", sorted.back());
    juce::Array<juce::var> per;
    for (auto* inst : PlughostInstance::instances()) per.add (inst->report());
    report->setProperty ("bridged", per);

    // Write the recording (32-bit float stereo).
    juce::WavAudioFormat wav;
    if (auto os = std::unique_ptr<juce::OutputStream> (outFile.createOutputStream()))
        if (auto w = std::unique_ptr<juce::AudioFormatWriter> (wav.createWriterFor (os.get(), sr, 2, 32, {}, 0)))
        {
            os.release();
            juce::AudioBuffer<float> b (2, (int) (rec.size() / 2));
            for (int s = 0; s < b.getNumSamples(); ++s)
                for (int c = 0; c < 2; ++c) b.setSample (c, s, rec[(size_t) s * 2 + c]);
            w->writeFromAudioSampleBuffer (b, 0, b.getNumSamples());
        }
    report->setProperty ("ok", true);
    printJson (report);
    return 0;
}

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI init;
    if (argc < 2) { std::cerr << "usage: bridge_probe job.json\n"; return 2; }
    const auto job = juce::JSON::parse (juce::File::getCurrentWorkingDirectory().getChildFile (argv[1]));
    return run (job);
}
