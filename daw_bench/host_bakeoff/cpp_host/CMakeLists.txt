cmake_minimum_required(VERSION 3.15)
project(host_cpp VERSION 0.1.0)

# JUCE from the Tracktion Engine checkout (the same hosting code Tracktion uses). GPLv3 build.
set(TRACKTION_ENGINE_DIR "$ENV{HOME}/Documents/third_party/tracktion_engine"
    CACHE PATH "Path to a tracktion_engine clone with modules/juce populated")

if (APPLE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE INTERNAL "")
endif()

add_subdirectory(${TRACKTION_ENGINE_DIR}/modules/juce juce_build)

juce_add_console_app(host_cpp NEEDS_CURL FALSE NEEDS_WEB_BROWSER FALSE)
juce_generate_juce_header(host_cpp)
target_compile_features(host_cpp PRIVATE cxx_std_20)
target_sources(host_cpp PRIVATE host_cpp.cpp)

target_compile_definitions(host_cpp PRIVATE
    JUCE_PLUGINHOST_AU=1
    JUCE_PLUGINHOST_VST3=1
    JUCE_MODAL_LOOPS_PERMITTED=1
    JUCE_USE_CURL=0
    JUCE_WEB_BROWSER=0)

target_link_libraries(host_cpp PRIVATE
    juce::juce_audio_formats
    juce::juce_audio_processors
    juce::juce_audio_utils)
