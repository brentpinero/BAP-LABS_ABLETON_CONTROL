cmake_minimum_required(VERSION 3.15)
project(tracktion_probe VERSION 0.1.0)

# Tracktion Engine checkout (with its JUCE submodule). GPLv3 build.
set(TRACKTION_ENGINE_DIR "$ENV{HOME}/Documents/third_party/tracktion_engine"
    CACHE PATH "Path to a tracktion_engine clone with modules/juce populated")

if (APPLE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE INTERNAL "")
endif()

set(TE_ADD_EXAMPLES OFF CACHE BOOL "" FORCE)
add_subdirectory(${TRACKTION_ENGINE_DIR} tracktion_build)

juce_add_console_app(tracktion_probe
    NEEDS_CURL FALSE
    NEEDS_WEB_BROWSER FALSE)

juce_generate_juce_header(tracktion_probe)
target_compile_features(tracktion_probe PRIVATE cxx_std_20)
target_sources(tracktion_probe PRIVATE tracktion_probe.cpp)

target_compile_definitions(tracktion_probe PRIVATE
    JUCE_PLUGINHOST_AU=1
    JUCE_PLUGINHOST_VST3=1
    JUCE_STRICT_REFCOUNTEDPOINTER=1
    JUCE_MODAL_LOOPS_PERMITTED=1
    JUCE_USE_CURL=0
    JUCE_WEB_BROWSER=0
    TRACKTION_LOG_DEVICES=0)

target_link_libraries(tracktion_probe PRIVATE
    tracktion::tracktion_core
    tracktion::tracktion_engine
    tracktion::tracktion_graph
    juce::juce_audio_devices
    juce::juce_audio_processors
    juce::juce_audio_utils)

if (APPLE)
    target_compile_options(tracktion_probe PRIVATE "-fno-aligned-allocation")
endif()
