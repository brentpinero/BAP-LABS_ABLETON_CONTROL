#!/usr/bin/env python3
"""
🎛️ SERUM PARAMETER MAPPER
Maps our dataset parameter categories to actual Serum VST parameter indices
"""

import json
import re
from pathlib import Path

class SerumParameterMapper:
    def __init__(self):
        """Initialize with known Serum 2 parameter structure"""

        # Known Serum 2 parameter categories and their typical indices
        # Based on Serum architecture and common parameter ordering
        self.parameter_mapping = {
            # OSCILLATOR A
            "OSC_A_LEVEL": {"indices": [0, 1], "description": "Oscillator A Level/Volume"},
            "OSC_A_PITCH": {"indices": [2, 3], "description": "Oscillator A Pitch/Tune"},
            "OSC_A_WAVETABLE": {"indices": [4, 5, 6], "description": "Oscillator A Wavetable Position"},
            "OSC_A_DETUNE": {"indices": [7, 8], "description": "Oscillator A Fine Tune/Detune"},

            # OSCILLATOR B
            "OSC_B_LEVEL": {"indices": [20, 21], "description": "Oscillator B Level/Volume"},
            "OSC_B_PITCH": {"indices": [22, 23], "description": "Oscillator B Pitch/Tune"},
            "OSC_B_WAVETABLE": {"indices": [24, 25, 26], "description": "Oscillator B Wavetable Position"},
            "OSC_B_DETUNE": {"indices": [27, 28], "description": "Oscillator B Fine Tune/Detune"},

            # FILTER
            "FILTER_CUTOFF": {"indices": [40, 41], "description": "Filter Cutoff Frequency"},
            "FILTER_RESONANCE": {"indices": [42, 43], "description": "Filter Resonance"},
            "FILTER_TYPE": {"indices": [44, 45], "description": "Filter Type Selection"},
            "FILTER_DRIVE": {"indices": [46, 47], "description": "Filter Drive/Saturation"},

            # ENVELOPES
            "ENV_ATTACK": {"indices": [60, 61, 62], "description": "Envelope Attack Times"},
            "ENV_DECAY": {"indices": [63, 64, 65], "description": "Envelope Decay Times"},
            "ENV_SUSTAIN": {"indices": [66, 67, 68], "description": "Envelope Sustain Levels"},
            "ENV_RELEASE": {"indices": [69, 70, 71], "description": "Envelope Release Times"},

            # LFO
            "LFO_RATE": {"indices": [80, 81, 82, 83], "description": "LFO Rate/Speed"},
            "LFO_AMOUNT": {"indices": [84, 85, 86, 87], "description": "LFO Modulation Amount"},
            "LFO_SHAPE": {"indices": [88, 89, 90, 91], "description": "LFO Waveform Shape"},

            # EFFECTS
            "REVERB_SIZE": {"indices": [100, 101], "description": "Reverb Room Size"},
            "REVERB_MIX": {"indices": [102, 103], "description": "Reverb Wet/Dry Mix"},
            "DELAY_TIME": {"indices": [104, 105], "description": "Delay Time"},
            "DELAY_FEEDBACK": {"indices": [106, 107], "description": "Delay Feedback"},
            "DISTORTION_AMOUNT": {"indices": [108, 109], "description": "Distortion/Saturation"},

            # GLOBAL
            "MASTER_VOLUME": {"indices": [120], "description": "Master Output Level"},
            "MASTER_TUNE": {"indices": [121], "description": "Master Pitch Tune"},
            "PORTAMENTO": {"indices": [122], "description": "Portamento/Glide"}
        }

        # Map our dataset categories to Serum parameter categories
        self.dataset_to_serum_mapping = {
            # Oscillator parameters
            "osc_a_level": "OSC_A_LEVEL",
            "osc_a_pitch": "OSC_A_PITCH",
            "osc_a_wave_pos": "OSC_A_WAVETABLE",
            "osc_a_detune": "OSC_A_DETUNE",
            "osc_b_level": "OSC_B_LEVEL",
            "osc_b_pitch": "OSC_B_PITCH",
            "osc_b_wave_pos": "OSC_B_WAVETABLE",
            "osc_b_detune": "OSC_B_DETUNE",

            # Filter parameters
            "filter_cutoff": "FILTER_CUTOFF",
            "filter_resonance": "FILTER_RESONANCE",
            "filter_type": "FILTER_TYPE",
            "filter_drive": "FILTER_DRIVE",

            # Envelope parameters
            "env_attack": "ENV_ATTACK",
            "env_decay": "ENV_DECAY",
            "env_sustain": "ENV_SUSTAIN",
            "env_release": "ENV_RELEASE",

            # LFO parameters
            "lfo_rate": "LFO_RATE",
            "lfo_amount": "LFO_AMOUNT",
            "lfo_shape": "LFO_SHAPE",

            # Effects parameters
            "reverb_size": "REVERB_SIZE",
            "reverb_mix": "REVERB_MIX",
            "delay_time": "DELAY_TIME",
            "delay_feedback": "DELAY_FEEDBACK",
            "distortion": "DISTORTION_AMOUNT",

            # Global parameters
            "master_vol": "MASTER_VOLUME",
            "master_tune": "MASTER_TUNE",
            "portamento": "PORTAMENTO"
        }

    def load_categorized_presets(self):
        """Load our categorized preset data"""
        categorized_file = Path("enriched_serum_training_dataset.json")

        if not categorized_file.exists():
            print("❌ enriched_serum_training_dataset.json not found")
            return []

        with open(categorized_file, 'r') as f:
            full_data = json.load(f)

        # Extract the training ready presets from the enriched dataset
        if isinstance(full_data, dict) and 'metadata' in full_data:
            # This is the enriched dataset structure - find the presets
            presets = []
            for key, value in full_data.items():
                if isinstance(value, list):
                    presets = value
                    break

            if not presets:
                print("❌ No preset data found in enriched dataset")
                return []

            print(f"📊 Loaded {len(presets)} presets from enriched dataset")
            return presets
        else:
            # This is a direct list
            print(f"📊 Loaded {len(full_data)} categorized presets")
            return full_data

    def analyze_parameter_usage(self, presets_data):
        """Analyze which parameters are most commonly used in our dataset"""

        parameter_usage = {}
        total_presets = len(presets_data)

        for preset in presets_data:
            if 'selected_parameters' in preset:
                for param_name in preset['selected_parameters']:
                    if param_name not in parameter_usage:
                        parameter_usage[param_name] = 0
                    parameter_usage[param_name] += 1

        # Sort by usage frequency
        sorted_params = sorted(parameter_usage.items(), key=lambda x: x[1], reverse=True)

        print(f"\n📈 PARAMETER USAGE ANALYSIS:")
        print("=" * 50)

        for param_name, count in sorted_params[:20]:  # Top 20
            percentage = (count / total_presets) * 100
            serum_category = self.dataset_to_serum_mapping.get(param_name, "UNMAPPED")

            print(f"{param_name:<20} | {count:>4} presets ({percentage:>5.1f}%) | {serum_category}")

        return sorted_params

    def create_test_sequences(self, parameter_usage):
        """Create test sequences for Max for Live based on parameter usage"""

        test_sequences = {
            "bass_test": {
                "description": "Test sequence for bass sounds",
                "parameters": []
            },
            "lead_test": {
                "description": "Test sequence for lead sounds",
                "parameters": []
            },
            "pad_test": {
                "description": "Test sequence for pad sounds",
                "parameters": []
            },
            "pluck_test": {
                "description": "Test sequence for pluck sounds",
                "parameters": []
            }
        }

        # Get top parameters for each category
        top_params = parameter_usage[:15]  # Top 15 most used parameters

        for param_name, usage_count in top_params:
            if param_name in self.dataset_to_serum_mapping:
                serum_category = self.dataset_to_serum_mapping[param_name]
                serum_mapping = self.parameter_mapping.get(serum_category)

                if serum_mapping:
                    param_info = {
                        "dataset_name": param_name,
                        "serum_category": serum_category,
                        "vst_indices": serum_mapping["indices"],
                        "description": serum_mapping["description"],
                        "usage_count": usage_count
                    }

                    # Add to relevant test sequences based on parameter type
                    if "osc" in param_name or "filter" in param_name:
                        test_sequences["bass_test"]["parameters"].append(param_info)
                        test_sequences["lead_test"]["parameters"].append(param_info)
                    elif "env" in param_name:
                        test_sequences["pad_test"]["parameters"].append(param_info)
                        test_sequences["pluck_test"]["parameters"].append(param_info)
                    elif "lfo" in param_name or "reverb" in param_name:
                        test_sequences["pad_test"]["parameters"].append(param_info)
                    else:
                        # Add to all sequences for global parameters
                        for sequence in test_sequences.values():
                            sequence["parameters"].append(param_info)

        return test_sequences

    def generate_max_javascript(self, test_sequences):
        """Generate JavaScript code for Max for Live testing"""

        js_code = '''/**
 * 🎛️ SERUM PARAMETER TEST - Dataset Mapped
 * Generated parameter mapping from categorized preset dataset
 */

autowatch = 1;

// Parameter mapping from our dataset
var parameter_tests = ''' + json.dumps(test_sequences, indent=4) + ''';

var current_test = "";
var test_step = 0;

function loadbang() {
    post("🎛️ Serum Parameter Mapper loaded");
    post("Available tests: bass_test, lead_test, pad_test, pluck_test");
    post("Use: run_test <test_name>");
}

function run_test(test_name) {
    if (!(test_name in parameter_tests)) {
        post("❌ Unknown test: " + test_name);
        post("Available: " + Object.keys(parameter_tests).join(", "));
        return;
    }

    current_test = test_name;
    test_step = 0;

    var test_data = parameter_tests[test_name];
    post("\\n🚀 RUNNING TEST: " + test_name);
    post("Description: " + test_data.description);
    post("Testing " + test_data.parameters.length + " parameters...");

    run_parameter_sequence(test_data.parameters);
}

function run_parameter_sequence(parameters) {
    for (var i = 0; i < parameters.length; i++) {
        var param = parameters[i];
        var delay = i * 1000; // 1 second between each test

        var timer = new Task(function(p) {
            test_parameter(p);
        }, param);

        timer.schedule(delay);
    }
}

function test_parameter(param_info) {
    post("\\n🎛️ Testing: " + param_info.dataset_name);
    post("   Category: " + param_info.serum_category);
    post("   Description: " + param_info.description);
    post("   Usage in dataset: " + param_info.usage_count + " presets");

    // Test each VST index for this parameter
    var indices = param_info.vst_indices;
    var test_value = 0.7; // 70% value for testing

    for (var j = 0; j < indices.length; j++) {
        var vst_index = indices[j];
        post("   Setting VST parameter " + vst_index + " to " + test_value);

        // Send to VST
        outlet(0, vst_index, test_value);

        // Get the value back to confirm
        var verify_timer = new Task(function(index) {
            outlet(0, "get", index);
        }, vst_index);
        verify_timer.schedule(200);
    }
}

// Quick test functions for Max buttons
function test_bass() { run_test("bass_test"); }
function test_lead() { run_test("lead_test"); }
function test_pad() { run_test("pad_test"); }
function test_pluck() { run_test("pluck_test"); }

// Handle VST responses
function list() {
    var args = arrayfromargs(arguments);
    post("✅ VST parameter " + args[0] + " = " + args[1]);
}

// Export functions
this.run_test = run_test;
this.test_bass = test_bass;
this.test_lead = test_lead;
this.test_pad = test_pad;
this.test_pluck = test_pluck;
'''

        return js_code

    def run_analysis(self):
        """Run the complete analysis and generate Max for Live code"""

        print("🎛️ SERUM PARAMETER MAPPER")
        print("=" * 50)

        # Load data
        presets_data = self.load_categorized_presets()
        if not presets_data:
            return

        # Analyze parameter usage
        parameter_usage = self.analyze_parameter_usage(presets_data)

        # Create test sequences
        test_sequences = self.create_test_sequences(parameter_usage)

        print(f"\n🚀 GENERATED TEST SEQUENCES:")
        for test_name, test_data in test_sequences.items():
            print(f"{test_name}: {len(test_data['parameters'])} parameters")

        # Generate Max JavaScript
        js_code = self.generate_max_javascript(test_sequences)

        # Save JavaScript file
        js_file = Path("serum_dataset_mapper.js")
        with open(js_file, 'w') as f:
            f.write(js_code)

        print(f"\n✅ Generated: {js_file}")
        print("Use this JavaScript file in your Max for Live device!")

        # Save mapping data
        mapping_file = Path("parameter_mapping_analysis.json")
        mapping_data = {
            "parameter_usage": dict(parameter_usage[:20]),
            "test_sequences": test_sequences,
            "serum_mapping": self.parameter_mapping,
            "dataset_mapping": self.dataset_to_serum_mapping
        }

        with open(mapping_file, 'w') as f:
            json.dump(mapping_data, f, indent=2)

        print(f"✅ Saved analysis: {mapping_file}")

if __name__ == "__main__":
    mapper = SerumParameterMapper()
    mapper.run_analysis()