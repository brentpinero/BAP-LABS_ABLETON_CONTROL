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
           "helper": "<plughost-helper executable>", "latency_quanta": 1,
           "chain": [{"bundle", "class_name"}, ...]?   per-track plugin chain instead of bundle/
                                                       class_name (bridge: ONE helper per track)
           "audio_file": path?                         tracks play this clip instead of MIDI notes
           "device": "coreaudio"?, "device_name": "MacBook Pro Speakers", "workgroup": true
                 realtime on a real CoreAudio device: Tracktion's own DeviceManager drives the
                 edit (and joins the device's audio workgroup); output is recorded, then zeroed
                 so nothing reaches the speakers. Without "device", a paced thread drives
                 Tracktion's HostedAudioDeviceInterface.
           "prespawn_parallel": 8                      bridges: start every helper up front, this
                                                       many at once, before playback }
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
#include <map>
#include <mutex>
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

    static std::string openJob (const juce::String& id, double sr, int block)
    {
        auto job = juce::JSON::parse (id.fromFirstOccurrenceOf ("plughost:", false, false));
        job.getDynamicObject()->setProperty ("sr", sr);
        job.getDynamicObject()->setProperty ("block", juce::jmax (block, 4096));   // room for any block size
        return juce::JSON::toString (job, true).toStdString();
    }

    // Starts `count` helpers for plugin `id` up front, `parallel` at a time, as an engine would
    // when it loads a set: createPluginInstance then takes a running one from the pool.
    void prespawn (const juce::String& id, double sr, int block, int count, int parallel)
    {
        const auto job = openJob (id, sr, block);
        const auto helperPath = helper.toStdString();
        std::atomic<int> next { 0 };
        std::vector<std::thread> threads;
        for (int t = 0; t < juce::jmax (1, parallel); ++t)
            threads.emplace_back ([&]
            {
                while (next.fetch_add (1) < count)
                {
                    char err[1024] = {};
                    auto* b = ph_open (helperPath.c_str(), job.c_str(), err, sizeof (err));
                    const std::lock_guard<std::mutex> lock (poolLock);
                    if (b != nullptr) pool[job].push_back (b);
                    else prespawnErrors.add (juce::String (juce::CharPointer_UTF8 (err)));
                }
            });
        for (auto& t : threads) t.join();
    }

    juce::StringArray prespawnErrors;

    void createPluginInstance (const juce::PluginDescription& d, double sr, int block,
                               PluginCreationCallback callback) override
    {
        const auto job = openJob (d.fileOrIdentifier, sr, block);
        ph_bridge* b = nullptr;
        {
            const std::lock_guard<std::mutex> lock (poolLock);
            if (auto& ready = pool[job]; ! ready.empty()) { b = ready.back(); ready.pop_back(); }
        }
        char err[1024] = {};
        if (b == nullptr)
            b = ph_open (helper.toRawUTF8(), job.c_str(), err, sizeof (err));
        if (b == nullptr) { callback (nullptr, "plughost: " + juce::String (juce::CharPointer_UTF8 (err))); return; }
        char buf[1024];
        ph_info_json (b, buf, sizeof (buf));
        callback (std::make_unique<PlughostInstance> (d.fileOrIdentifier, helper, b,
                                                      juce::JSON::parse (juce::String (buf)), sr, juce::jmax (block, 4096)),
                  {});
    }

private:
    juce::String helper;
    std::mutex poolLock;
    std::map<std::string, std::vector<ph_bridge*>> pool;
};

//==============================================================================
// Sits between the CoreAudio device and Tracktion's DeviceManager: times each engine callback,
// records the output once armed, then zeroes it so nothing plays through the speakers.
struct DeviceTimer : public juce::AudioIODeviceCallback
{
    DeviceTimer (juce::AudioIODeviceCallback& e, int maxCallbacks, int block)
        : engineCallback (e), ms ((size_t) maxCallbacks), sizes ((size_t) maxCallbacks),
          rec ((size_t) maxCallbacks * (size_t) block * 2), maxBlock (block) {}

    void audioDeviceIOCallbackWithContext (const float* const* in, int numIns, float* const* out, int numOuts,
                                           int n, const juce::AudioIODeviceCallbackContext& ctx) override
    {
        const auto t = Clock::now();
        engineCallback.audioDeviceIOCallbackWithContext (in, numIns, out, numOuts, n, ctx);
        const double took = std::chrono::duration<double, std::milli> (Clock::now() - t).count();
        const int i = count.load (std::memory_order_relaxed);
        if (armed.load (std::memory_order_relaxed) && i < (int) ms.size())
        {
            ms[(size_t) i] = took;
            sizes[(size_t) i] = n;
            for (int s = 0; s < juce::jmin (n, maxBlock); ++s)
                for (int c = 0; c < 2; ++c)
                    rec[((size_t) i * (size_t) maxBlock + (size_t) s) * 2 + (size_t) c]
                        = c < numOuts && out[c] != nullptr ? out[c][s] : 0.0f;
            count.store (i + 1, std::memory_order_release);
        }
        for (int c = 0; c < numOuts; ++c)
            if (out[c] != nullptr) juce::FloatVectorOperations::clear (out[c], n);
    }
    void audioDeviceAboutToStart (juce::AudioIODevice* d) override { engineCallback.audioDeviceAboutToStart (d); }
    void audioDeviceStopped() override                             { engineCallback.audioDeviceStopped(); }
    void audioDeviceError (const juce::String& e) override         { engineCallback.audioDeviceError (e); }

    juce::AudioIODeviceCallback& engineCallback;
    std::vector<double> ms;
    std::vector<int> sizes;
    std::vector<float> rec;
    const int maxBlock;
    std::atomic<int> count { 0 };
    std::atomic<bool> armed { false };
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
    const juce::String mode = job["mode"], kind = job["plugin"], device = job["device"].toString();
    const bool onDevice = mode == "realtime" && device == "coreaudio";
    const double sr = job.getProperty ("sample_rate", 44100.0), tempo = job.getProperty ("tempo", 120.0),
                 seconds = job.getProperty ("seconds", 8.0);
    const int block = job.getProperty ("block", 128), numTracks = job.getProperty ("tracks", 1);
    const juce::String helper = job["helper"].toString();
    PlughostInstance::latencyQuanta = job.getProperty ("latency_quanta", 1);

    te::Engine engine { "bridge_probe", std::make_unique<HeadlessUI>(), std::make_unique<te::EngineBehaviour>() };
    auto& pm = engine.getPluginManager();
    auto* plughostFormat = new PlughostFormat (helper);
    pm.pluginFormatManager.addFormat (std::unique_ptr<juce::AudioPluginFormat> (plughostFormat));
    auto* report = new juce::DynamicObject();
    const juce::var reportVar (report);

    auto& tdm = engine.getDeviceManager();
    auto& jdm = tdm.deviceManager;
    auto& hosted = tdm.getHostedAudioDeviceInterface();
    std::unique_ptr<DeviceTimer> timed;
    const double period = block / sr;
    const int callbacks = (int) (seconds / period);
    if (onDevice)
    {
        // Tracktion's own device path, as the real engine will run: its DeviceManager is the
        // CoreAudio callback, and its graph threads join the device's audio workgroup. Its CPU
        // guard (silence output above 98% load) would hide overloads, so it is off.
        tdm.setCpuLimitBeforeMuting (1.0e9);
        te::EditPlaybackContext::enableAudioWorkgroup ((bool) job.getProperty ("workgroup", true));
        tdm.initialise (0, 2);
        jdm.setCurrentAudioDeviceType ("CoreAudio", true);
        auto setup = jdm.getAudioDeviceSetup();
        setup.outputDeviceName = job.getProperty ("device_name", "MacBook Pro Speakers").toString();
        setup.inputDeviceName = {};
        setup.useDefaultInputChannels = false;
        setup.inputChannels.clear();
        setup.useDefaultOutputChannels = true;
        setup.sampleRate = sr;
        setup.bufferSize = block;
        if (auto err = jdm.setAudioDeviceSetup (setup, true); err.isNotEmpty())
            return std::cerr << "device: " << err << "\n", 1;
        auto* dev = jdm.getCurrentAudioDevice();
        if (dev == nullptr) return std::cerr << "no audio device\n", 1;
        report->setProperty ("audio_device", dev->getTypeName() + "/" + dev->getName());
        report->setProperty ("device_rate", dev->getCurrentSampleRate());
        report->setProperty ("device_block", dev->getCurrentBufferSizeSamples());
        report->setProperty ("device_latency_out", dev->getOutputLatencyInSamples());
        if (dev->getCurrentSampleRate() != sr || dev->getCurrentBufferSizeSamples() != block)
            return std::cerr << "device runs at " << dev->getCurrentSampleRate() << " Hz / "
                             << dev->getCurrentBufferSizeSamples() << " samples, asked "
                             << sr << " / " << block << "\n", 1;
        const auto wg = jdm.getDeviceAudioWorkgroup();
        report->setProperty ("workgroup_valid", (bool) wg);
        report->setProperty ("workgroup_max_threads", (int) (wg ? wg.getMaxParallelThreadCount() : 0));
        report->setProperty ("engine_cpus", engine.getEngineBehaviour().getNumberOfCPUsToUseForAudio());
        // Put the timing wrapper between the device and Tracktion. DeviceManager inherits the
        // callback privately; a C-style cast is the one cast allowed to reach a private base.
        auto* engineCallback = (juce::AudioIODeviceCallback*) &tdm;
        timed = std::make_unique<DeviceTimer> (*engineCallback, callbacks, block);
        jdm.removeAudioCallback (engineCallback);
        jdm.addAudioCallback (timed.get());
    }
    else if (mode == "realtime")
    {
        te::HostedAudioDeviceInterface::Parameters p;
        p.sampleRate = sr; p.blockSize = block; p.inputChannels = 0; p.outputChannels = 2;
        hosted.initialise (p);
    }

    // The chain each track gets: `chain` entries, or the single bundle/class_name.
    juce::Array<juce::var> chain;
    if (auto* c = job["chain"].getArray()) chain = *c;
    else
    {
        auto* one = new juce::DynamicObject();
        one->setProperty ("bundle", job["bundle"]);
        one->setProperty ("class_name", job["class_name"]);
        chain.add (juce::var (one));
    }

    // Plugin descriptions per track: ONE bridged plugin running the whole chain in one helper,
    // or one in-process VST3 per chain entry (the control).
    juce::Array<juce::PluginDescription> descs;
    if (kind == "bridge")
    {
        auto* spec = new juce::DynamicObject();
        const juce::var specVar (spec);
        spec->setProperty ("realtime", mode == "realtime");
        if (job["chain"].isArray())
        {
            spec->setProperty ("slots", job["chain"]);
            spec->setProperty ("class_name", "chain");
        }
        else
        {
            spec->setProperty ("format", "vst3");
            spec->setProperty ("bundle", job["bundle"]);
            spec->setProperty ("class_name", job["class_name"]);
            if (job.hasProperty ("component_state")) spec->setProperty ("component_state", job["component_state"]);
        }
        juce::OwnedArray<juce::PluginDescription> found;
        plughostFormat->findAllTypesForFile (found, "plughost:" + juce::JSON::toString (specVar, true));
        descs.add (*found[0]);
        if (int par = job.getProperty ("prespawn_parallel", 0); par > 0)
        {
            const auto t0 = Clock::now();
            plughostFormat->prespawn (descs[0].fileOrIdentifier, sr, block, numTracks, par);
            report->setProperty ("prespawn_s", std::chrono::duration<double> (Clock::now() - t0).count());
            report->setProperty ("prespawn_errors", plughostFormat->prespawnErrors.size());
            if (! plughostFormat->prespawnErrors.isEmpty())
                std::cerr << "prespawn: " << plughostFormat->prespawnErrors[0] << "\n";
        }
    }
    else
    {
        for (auto& entry : chain)
        {
            juce::OwnedArray<juce::PluginDescription> found;
            for (auto* f : pm.pluginFormatManager.getFormats())
                if (f->getName() == "VST3") f->findAllTypesForFile (found, entry["bundle"].toString());
            const juce::PluginDescription* match = nullptr;
            for (auto* d : found)
                if (entry["class_name"].isVoid() || d->name == entry["class_name"].toString()) { match = d; break; }
            if (match == nullptr)
                return std::cerr << "no VST3 class in " << entry["bundle"].toString() << "\n", 1;
            descs.add (*match);
        }
    }
    for (auto& d : descs) pm.knownPluginList.addType (d);

    auto edit = te::Edit::createSingleTrackEdit (engine, mode == "realtime" ? te::Edit::EditRole::forEditing
                                                                            : te::Edit::EditRole::forRendering);
    edit->ensureNumberOfAudioTracks (numTracks);
    edit->tempoSequence.getTempo (0)->setBpm (tempo);
    edit->getMasterVolumePlugin()->setVolumeDb (0.0f);

    juce::MemoryBlock comp;
    if (job.hasProperty ("component_state")) juce::File (job["component_state"].toString()).loadFileAsData (comp);
    const juce::File audioFile (job["audio_file"].toString());
    const bool audioSource = job.hasProperty ("audio_file");

    const auto tBuild = Clock::now();
    auto tracks = te::getAudioTracks (*edit);
    for (auto* track : tracks)
    {
        if (audioSource)
        {
            // One audio clip for the whole length, feeding the chain.
            track->insertWaveClip ("source", audioFile, { { te::TimePosition(), te::TimeDuration::fromSeconds (seconds) },
                                                          te::TimeDuration() }, false);
        }
        else
        {
            // One MIDI clip: a note on every beat (alternating pitch) for the whole length.
            auto clip = track->insertMIDIClip ({ te::TimePosition(), te::TimeDuration::fromSeconds (seconds) }, nullptr);
            const int beats = (int) (seconds * tempo / 60.0);
            for (int b = 0; b < beats; ++b)
                clip->getSequence().addNote (b % 2 ? 41 : 36, te::BeatPosition::fromBeats (b),
                                             te::BeatDuration::fromBeats (0.75), 100, 0, nullptr);
        }
        int index = 0;
        for (auto& desc : descs)
        {
            auto plugin = edit->getPluginCache().createNewPlugin (te::ExternalPlugin::xmlTypeName, desc);
            track->pluginList.insertPlugin (plugin, index++, nullptr);
            if (auto* ext = dynamic_cast<te::ExternalPlugin*> (plugin.get()))
            {
                if (ext->getAudioPluginInstance() == nullptr)
                    return std::cerr << "plugin failed to load: " << ext->getLoadError() << "\n", 1;
                if (kind == "native" && comp.getSize() > 0 && descs.size() == 1)
                    if (auto* v3 = ext->getAudioPluginInstance()->getVST3Client())
                        v3->setPreset (vstpreset (job["class_id"].toString(), comp));
            }
        }
    }
    report->setProperty ("build_s", std::chrono::duration<double> (Clock::now() - tBuild).count());

    const juce::File outFile (job["output"].toString());
    outFile.deleteFile();
    report->setProperty ("mode", mode);
    report->setProperty ("plugin", kind);
    report->setProperty ("tracks", numTracks);
    report->setProperty ("plugins_per_track", descs.size());

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
        printJson (reportVar);
        return rendered.existsAsFile() ? 0 : 1;
    }

    // Realtime. Paced: as Tracktion's EngineInPluginDemo, allocate the playback context on the
    // hosted device (forced, after the edit is built) and restart playback before playing.
    // Start-up: preparing every plugin (for bridges: starting each helper's realtime endpoint,
    // one after another on this thread) until the transport plays.
    const auto tStart = Clock::now();
    if (! onDevice)
        hosted.prepareToPlay (sr, block);
    edit->playInStopEnabled = true;
    edit->getTransport().ensureContextAllocated (true);
    if (! onDevice)
        edit->restartPlayback();
    edit->getTransport().setPosition (te::TimePosition());
    // The context is (re)built asynchronously: pump messages until play() sticks.
    for (int i = 0; i < 300 && ! edit->getTransport().isPlaying(); ++i)
    {
        juce::MessageManager::getInstance()->runDispatchLoopUntil (10);
        edit->getTransport().play (false);
    }
    if (! edit->getTransport().isPlaying())
        return std::cerr << "transport did not start\n", 1;
    report->setProperty ("playback_start_s", std::chrono::duration<double> (Clock::now() - tStart).count());
    // Lets an external test (the kill test) act only once playback is running.
    if (job.hasProperty ("playing_marker"))
        juce::File (job["playing_marker"].toString()).replaceWithText ("playing");

    std::vector<float> rec;
    std::vector<double> cbMs;
    std::atomic<bool> done { false }, warmMarked { false };
    int overruns = 0, overrunsWarmup = 0;
    const double warmupS = job.getProperty ("warmup_s", 1.0);
    const int warmCallbacks = (int) (warmupS / period);
    int xrunsAtWarm = 0;
    std::vector<double> cpu;   // JUCE's device load (callback time / period, smoothed), per 50 ms

    // Control thread: marks the end of warm-up, polls/recovers bridged chains, samples load.
    auto startControl = [&]
    {
        return std::thread ([&]
        {
            const auto start = Clock::now();
            while (! done)
            {
                if (! warmMarked && std::chrono::duration<double> (Clock::now() - start).count() >= warmupS)
                {
                    for (auto* inst : PlughostInstance::instances()) inst->markWarm();
                    if (onDevice && jdm.getCurrentAudioDevice() != nullptr)
                        xrunsAtWarm = jdm.getCurrentAudioDevice()->getXRunCount();
                    warmMarked = true;
                }
                for (auto* inst : PlughostInstance::instances()) inst->pollAndRecover (300.0);
                if (onDevice && warmMarked) cpu.push_back (jdm.getCpuUsage());
                std::this_thread::sleep_for (std::chrono::milliseconds (50));
            }
        });
    };

    if (onDevice)
    {
        // The device calls back on its own IO thread; record `callbacks` of them from now on.
        timed->armed = true;
        auto control = startControl();
        const auto deadline = Clock::now() + std::chrono::duration<double> (seconds * 3 + 30);
        while (timed->count.load() < callbacks && Clock::now() < deadline)
            juce::MessageManager::getInstance()->runDispatchLoopUntil (10);
        timed->armed = false;
        done = true;
        control.join();
        auto* dev = jdm.getCurrentAudioDevice();
        const int xruns = dev != nullptr ? dev->getXRunCount() : -1;
        report->setProperty ("device_xruns", xruns - xrunsAtWarm);       // after warm-up
        report->setProperty ("device_xruns_warmup", xrunsAtWarm);
        const int got = timed->count.load();
        cbMs.assign (timed->ms.begin(), timed->ms.begin() + got);
        rec.assign (timed->rec.begin(), timed->rec.begin() + (size_t) got * (size_t) block * 2);
        int odd = 0;
        for (int i = 0; i < got; ++i) odd += timed->sizes[(size_t) i] != block;
        report->setProperty ("odd_block_sizes", odd);
        for (int i = 0; i < got; ++i)
            if (cbMs[(size_t) i] > period * 1e3) (i < warmCallbacks ? overrunsWarmup : overruns)++;
        if (! cpu.empty())
        {
            std::sort (cpu.begin(), cpu.end());
            report->setProperty ("cpu_load_median", cpu[cpu.size() / 2]);
            report->setProperty ("cpu_load_max", cpu.back());
        }
    }
    else
    {
        // Paced: drive the hosted device from a thread paced to wall-clock time, one block per
        // period, as an audio device would.
        rec.resize ((size_t) callbacks * block * 2);
        cbMs.resize ((size_t) callbacks);
        auto control = startControl();
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
        if (auto* dev = jdm.getCurrentAudioDevice())
            report->setProperty ("audio_device", dev->getTypeName() + "/" + dev->getName());
    }
    // Diagnostics: did the edit actually play?
    report->setProperty ("transport_playing", edit->getTransport().isPlaying());
    report->setProperty ("transport_position_s", edit->getTransport().getPosition().inSeconds());
    if (auto* out = tdm.getDefaultWaveOutDevice())
        report->setProperty ("default_wave_out", out->getName() + (out->isEnabled() ? " (enabled)" : " (disabled)"));
    edit->getTransport().stop (false, false);
    if (onDevice)
    {
        jdm.removeAudioCallback (timed.get());
        jdm.closeAudioDevice();
    }
    if (cbMs.empty())
        return std::cerr << "no callbacks recorded\n", 1;

    std::vector<double> sorted (cbMs);
    std::sort (sorted.begin(), sorted.end());
    report->setProperty ("block", block);
    report->setProperty ("period_ms", period * 1e3);
    report->setProperty ("callbacks", (int) cbMs.size());
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
    printJson (reportVar);
    return 0;
}

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI init;
    if (argc < 2) { std::cerr << "usage: bridge_probe job.json\n"; return 2; }
    const auto job = juce::JSON::parse (juce::File::getCurrentWorkingDirectory().getChildFile (argv[1]));
    return run (job);
}
