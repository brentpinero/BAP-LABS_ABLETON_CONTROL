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

    if (clips == nullptr || outFile.getFullPathName().isEmpty())
        return fail ("job needs clips[] and output");

    te::Engine engine { "tracktion_probe" };
    auto edit = te::Edit::createSingleTrackEdit (engine, te::Edit::EditRole::forRendering);
    edit->ensureNumberOfAudioTracks (clips->size());
    edit->tempoSequence.getTempo (0)->setBpm (tempo);

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

        clip->setAutoTempo (false);                        // unwarped: play at file speed
        clip->setAutoPitch (false);
        clip->setUsesProxy (false);                        // read the file itself, no cached proxy
        clip->setTimeStretchMode (te::TimeStretcher::disabled);

        tracks[i]->getVolumePlugin()->setPan ((float) (double) c.getProperty ("pan", 0.0));
    }

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
