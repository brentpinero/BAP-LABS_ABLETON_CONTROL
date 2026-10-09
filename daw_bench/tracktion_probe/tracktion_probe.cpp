/*
    tracktion_probe — render one Phase 0 probe job through Tracktion Engine.

    Usage: tracktion_probe job.json
    job.json: { "sample_rate": 48000, "tempo": 120.0, "seconds": 3.0,
                "output": "/path/out.wav",
                "clips": [ { "file": "/path/src.wav", "position_beats": 0.0, "pan": 0.0 } ] }

    Each clip goes on its own audio track, unwarped (no auto-tempo, no proxy,
    no time-stretch), with the track panned as requested. The master is
    rendered offline from time 0 for `seconds` to a 32-bit float WAV. Nothing
    else is touched, so whatever the probes measure (pan law, SRC, fades,
    latency) is the engine's default behaviour.
*/

#include <JuceHeader.h>
#include <iostream>

namespace te = tracktion;

static int fail (const juce::String& why)
{
    std::cerr << "tracktion_probe: " << why << "\n";
    return 1;
}

/* Headless UI: the engine's default runTaskWithProgressBar is a no-op that
   expects a GUI, so renders would silently produce nothing. Run the job on a
   thread and pump the message loop until it finishes; surface warnings. */
struct HeadlessUI : public te::UIBehaviour
{
    void runTaskWithProgressBar (te::ThreadPoolJobWithProgress& task) override
    {
        // Same synchronous path as Renderer::renderToFile (useThread = false) and the
        // engine's own tests: the job is incremental, one chunk per call. Running it on
        // the message thread keeps the graph teardown (which hops to that thread) simple.
        while (task.runJob() == juce::ThreadPoolJob::jobNeedsRunningAgain)
        {}
    }

    void showWarningMessage (const juce::String& message) override
    {
        std::cerr << "tracktion_probe warning: " << message << "\n";
    }
};

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI init;

    if (argc < 2)
        return fail ("usage: tracktion_probe job.json");

    const auto job = juce::JSON::parse (juce::File::getCurrentWorkingDirectory().getChildFile (argv[1]));

    if (! job.isObject())
        return fail ("could not parse job json");

    const double sampleRate = job.getProperty ("sample_rate", 48000.0);
    const double tempo      = job.getProperty ("tempo", 120.0);
    const double seconds    = job.getProperty ("seconds", 3.0);
    const juce::File outFile (job.getProperty ("output", juce::var()).toString());
    const auto* clips = job.getProperty ("clips", juce::var()).getArray();

    // Optional engine settings. Absent = Tracktion's own defaults, so a plain job
    // measures the engine as shipped; the probes then re-run with each option to
    // see what the engine CAN do (section 3 of the plan asks for selectable laws).
    const juce::String resampling = job.getProperty ("resampling", "").toString();   // lagrange|sincFast|sincMedium|sincBest
    const juce::String panLawName = job.getProperty ("pan_law", "").toString();      // linear|-2.5|-3|-4.5|-6
    const bool useProxy           = job.getProperty ("use_proxy", false);
    const double edgeFadeMs       = job.getProperty ("edge_fade_ms", 0.0);
    const juce::String warpMode   = job.getProperty ("warp_mode", "").toString();     // signalsmithDefault|signalsmithCheaper

    const auto stretchMode = [&]() -> std::optional<te::TimeStretcher::Mode>
    {
        if (warpMode == "signalsmithDefault") return te::TimeStretcher::signalsmithDefault;
        if (warpMode == "signalsmithCheaper") return te::TimeStretcher::signalsmithCheaper;
        return std::nullopt;
    }();

    const auto panLaw = [&]() -> te::PanLaw
    {
        if (panLawName == "linear") return te::PanLawLinear;
        if (panLawName == "-2.5")   return te::PanLaw2point5dBCenter;
        if (panLawName == "-3")     return te::PanLaw3dBCenter;
        if (panLawName == "-4.5")   return te::PanLaw4point5dBCenter;
        if (panLawName == "-6")     return te::PanLaw6dBCenter;
        return te::PanLawDefault;
    }();

    const auto quality = [&]() -> std::optional<te::ResamplingQuality>
    {
        if (resampling == "lagrange")   return te::ResamplingQuality::lagrange;
        if (resampling == "sincFast")   return te::ResamplingQuality::sincFast;
        if (resampling == "sincMedium") return te::ResamplingQuality::sincMedium;
        if (resampling == "sincBest")   return te::ResamplingQuality::sincBest;
        return std::nullopt;
    }();

    if (clips == nullptr || outFile.getFullPathName().isEmpty())
        return fail ("job needs clips[] and output");

    te::Engine engine { "tracktion_probe", std::make_unique<HeadlessUI>(), std::make_unique<te::EngineBehaviour>() };
    engine.getPluginManager().createBuiltInType<te::LatencyPlugin>();   // for the PDC probe
    auto edit = te::Edit::createSingleTrackEdit (engine, te::Edit::EditRole::forRendering);
    edit->ensureNumberOfAudioTracks (clips->size());
    edit->tempoSequence.getTempo (0)->setBpm (tempo);
    edit->getMasterVolumePlugin()->setVolumeDb (0.0f);   // unity master, as a fresh Live set

    auto tracks = te::getAudioTracks (*edit);

    for (int i = 0; i < clips->size(); ++i)
    {
        const auto& c = clips->getReference (i);
        const juce::File src (c.getProperty ("file", juce::var()).toString());

        if (! src.existsAsFile())
            return fail ("missing clip file: " + src.getFullPathName());

        te::AudioFile af (engine, src);
        const auto start  = edit->tempoSequence.toTime (te::BeatPosition::fromBeats ((double) c.getProperty ("position_beats", 0.0)));
        const auto length = te::TimeDuration::fromSeconds (af.getLength());

        auto clip = te::insertWaveClip (*tracks[i], src.getFileNameWithoutExtension(), src,
                                        te::ClipPosition { te::TimeRange (start, length) },
                                        te::DeleteExistingClips::no);
        if (clip == nullptr)
            return fail ("could not insert clip " + src.getFullPathName());

        clip->setAutoPitch (false);
        clip->setUsesProxy (useProxy);                     // proxy = pre-rendered copy at project rate

        if (stretchMode)
        {
            // warped at ratio 1:1: tell the clip its file is at the edit tempo
            clip->getLoopInfo().setBpm (tempo, af.getInfo());
            clip->setAutoTempo (true);
            clip->setTimeStretchMode (*stretchMode);
        }
        else
        {
            clip->setAutoTempo (false);                    // unwarped: play at file speed
            clip->setTimeStretchMode (te::TimeStretcher::disabled);
        }

        if (quality)
            clip->setResamplingQuality (*quality);

        if (edgeFadeMs > 0.0)
        {
            clip->setFadeIn (te::TimeDuration::fromSeconds (edgeFadeMs / 1000.0));
            clip->setFadeOut (te::TimeDuration::fromSeconds (edgeFadeMs / 1000.0));
        }

        auto* volPan = tracks[i]->getVolumePlugin();
        volPan->setPanLaw (panLaw);
        volPan->setPan ((float) (double) c.getProperty ("pan", 0.0));

        // per-clip extras for the PDC probe: a muted copy, or a pure-delay plugin
        // that reports its latency to the engine
        if ((bool) c.getProperty ("mute", false))
            tracks[i]->setMute (true);

        const double latencyMs = c.getProperty ("latency_ms", 0.0);

        if (latencyMs > 0.0)
        {
            auto latency = te::insertNewPlugin<te::LatencyPlugin> (*tracks[i]);

            if (latency == nullptr)
                return fail ("could not insert LatencyPlugin");

            latency->latencyTimeSeconds = (float) (latencyMs / 1000.0);
        }
    }

    outFile.deleteFile();                                  // the writer appends to an existing file

    te::Renderer::Parameters params (*edit);
    params.destFile = outFile;
    params.audioFormat = engine.getAudioFileFormatManager().getWavFormat();
    params.bitDepth = 32;                                  // float WAV
    params.sampleRateForAudio = sampleRate;
    params.blockSizeForAudio = 512;
    params.time = te::TimeRange (te::TimePosition(), te::TimeDuration::fromSeconds (seconds));
    params.tracksToDo = te::toBitSet (te::getAllTracks (*edit));

    const auto rendered = te::Renderer::renderToFile ("probe", params);

    if (! rendered.existsAsFile())
        return fail ("render produced no file");

    std::cout << rendered.getFullPathName() << "\n";
    return 0;
}
