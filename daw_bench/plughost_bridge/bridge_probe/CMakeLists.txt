cmake_minimum_required(VERSION 3.15)
project(bridge_probe VERSION 0.1.0)

# Tracktion Engine (with JUCE) + the plughost bridge static library (Rust, built by cargo:
#   cargo build --release --manifest-path daw_bench/plughost_bridge/Cargo.toml --target-dir build/plughost_bridge)
set(TRACKTION_ENGINE_DIR "$ENV{HOME}/Documents/third_party/tracktion_engine"
    CACHE PATH "Path to a tracktion_engine clone with modules/juce populated")
set(PLUGHOST_BRIDGE_LIB "${CMAKE_CURRENT_SOURCE_DIR}/../../../build/plughost_bridge/release/libplughost_bridge.a"
    CACHE FILEPATH "libplughost_bridge.a")

if (APPLE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "15.0" CACHE INTERNAL "")   # plughost requires macOS 15+
endif()

set(TE_ADD_EXAMPLES OFF CACHE BOOL "" FORCE)
add_subdirectory(${TRACKTION_ENGINE_DIR} tracktion_build)

juce_add_console_app(bridge_probe NEEDS_CURL FALSE NEEDS_WEB_BROWSER FALSE)
juce_generate_juce_header(bridge_probe)
target_compile_features(bridge_probe PRIVATE cxx_std_20)
target_sources(bridge_probe PRIVATE bridge_probe.cpp)

target_compile_definitions(bridge_probe PRIVATE
    JUCE_PLUGINHOST_AU=1
    JUCE_PLUGINHOST_VST3=1
    JUCE_MODAL_LOOPS_PERMITTED=1
    JUCE_USE_CURL=0
    JUCE_WEB_BROWSER=0
    TRACKTION_LOG_DEVICES=0)

target_link_libraries(bridge_probe PRIVATE
    tracktion::tracktion_core
    tracktion::tracktion_engine
    tracktion::tracktion_graph
    juce::juce_audio_devices
    juce::juce_audio_processors
    juce::juce_audio_utils
    ${PLUGHOST_BRIDGE_LIB}
    "-framework CoreFoundation" "-framework Security" "-framework SystemConfiguration"
    "-framework AudioToolbox" "-framework AVFAudio" "-framework CoreAudioKit" "-framework AppKit")

if (APPLE)
    target_compile_options(bridge_probe PRIVATE "-fno-aligned-allocation")
endif()
