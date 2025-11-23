#!/usr/bin/env python3
"""
🤖 AI INFERENCE SERVER 🤖
Handles natural language to Serum parameter translation
"""

from flask import Flask, request, jsonify, cors
import json
import logging
from pathlib import Path
import re
from typing import Dict, List, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SerumAIEngine:
    """AI engine for translating natural language to Serum parameters"""

    def __init__(self):
        self.load_parameter_mappings()
        self.load_sound_characteristics()
        self.setup_nlp_patterns()

    def load_parameter_mappings(self):
        """Load Serum parameter mappings"""
        try:
            # Load our analyzed parameter data
            with open('serum_parameter_analysis.json', 'r') as f:
                self.param_analysis = json.load(f)

            # Extract Tier 1 essential parameters
            self.tier1_params = self.param_analysis['final_recommendations']['tier_1_essential']['params']

            logger.info(f"Loaded {len(self.tier1_params)} Tier 1 parameters")

        except FileNotFoundError:
            logger.warning("Parameter analysis file not found, using defaults")
            self.tier1_params = [
                'mastervol', 'a_vol', 'b_vol', 'c_vol',
                'fil_cutoff', 'fil_reso', 'fil_drive',
                'env1_att', 'env1_dec', 'env1_sus', 'env1_rel',
                'a_wtpos', 'b_wtpos', 'a_warp', 'b_warp',
                'lfo1_rate', 'lfo1_amt'
            ]

    def load_sound_characteristics(self):
        """Load sound characteristic mappings"""
        self.sound_mappings = {
            'warm': {
                'fil_cutoff': {'value': 0.3, 'reason': 'Lower cutoff for warmth'},
                'fil_reso': {'value': 0.2, 'reason': 'Gentle resonance'},
                'a_warp': {'value': 0.1, 'reason': 'Subtle warp for character'}
            },
            'bright': {
                'fil_cutoff': {'value': 0.8, 'reason': 'Higher cutoff for brightness'},
                'fil_reso': {'value': 0.4, 'reason': 'Resonance for presence'},
                'env1_att': {'value': 0.02, 'reason': 'Quick attack for clarity'}
            },
            'dark': {
                'fil_cutoff': {'value': 0.2, 'reason': 'Low cutoff for darkness'},
                'fil_drive': {'value': 0.3, 'reason': 'Drive for character'},
                'a_vol': {'value': 0.6, 'reason': 'Reduced volume for depth'}
            },
            'punch': {
                'env1_att': {'value': 0.01, 'reason': 'Fast attack for punch'},
                'env1_dec': {'value': 0.3, 'reason': 'Quick decay for impact'},
                'fil_envelope': {'value': 0.6, 'reason': 'Filter envelope for punch'}
            },
            'soft': {
                'env1_att': {'value': 0.4, 'reason': 'Slow attack for softness'},
                'env1_rel': {'value': 0.8, 'reason': 'Long release for smoothness'},
                'fil_cutoff': {'value': 0.5, 'reason': 'Moderate filtering'}
            },
            'aggressive': {
                'fil_reso': {'value': 0.8, 'reason': 'High resonance for aggression'},
                'fil_drive': {'value': 0.7, 'reason': 'Drive for bite'},
                'env1_att': {'value': 0.005, 'reason': 'Very fast attack'}
            },
            'movement': {
                'lfo1_rate': {'value': 0.4, 'reason': 'LFO for movement'},
                'lfo1_amt': {'value': 0.6, 'reason': 'LFO amount for modulation'},
                'fil_cutoff': {'value': 0.6, 'reason': 'Cutoff for LFO target'}
            },
            'deep': {
                'a_octave': {'value': -1, 'reason': 'Lower octave for depth'},
                'sub_level': {'value': 0.8, 'reason': 'Sub oscillator for depth'},
                'fil_cutoff': {'value': 0.4, 'reason': 'Moderate low-pass'}
            },
            'fat': {
                'unison_voices': {'value': 8, 'reason': 'More voices for fatness'},
                'unison_detune': {'value': 0.15, 'reason': 'Detune for width'},
                'a_vol': {'value': 0.8, 'reason': 'Higher volume'}
            },
            'thin': {
                'unison_voices': {'value': 1, 'reason': 'Single voice'},
                'fil_cutoff': {'value': 0.7, 'reason': 'Higher cutoff'},
                'a_vol': {'value': 0.6, 'reason': 'Reduced volume'}
            }
        }

    def setup_nlp_patterns(self):
        """Setup natural language processing patterns"""
        self.intensity_words = {
            'more': 1.2,
            'much': 1.4,
            'very': 1.3,
            'extremely': 1.5,
            'slightly': 0.8,
            'little': 0.9,
            'bit': 0.9,
            'less': 0.7,
            'much less': 0.5
        }

        self.action_words = {
            'make': 'modify',
            'add': 'increase',
            'increase': 'increase',
            'boost': 'increase',
            'reduce': 'decrease',
            'lower': 'decrease',
            'cut': 'decrease',
            'remove': 'decrease'
        }

    def process_natural_language(self, description: str, current_params: Dict = None) -> Dict:
        """Process natural language description into parameter changes"""
        logger.info(f"Processing: '{description}'")

        # Normalize description
        desc_lower = description.lower().strip()

        # Extract characteristics and actions
        characteristics = self.extract_characteristics(desc_lower)
        actions = self.extract_actions(desc_lower)
        intensity = self.extract_intensity(desc_lower)

        # Generate parameter changes
        parameter_changes = []

        # Apply characteristic-based changes
        for char in characteristics:
            if char in self.sound_mappings:
                for param, config in self.sound_mappings[char].items():
                    value = config['value'] * intensity
                    value = max(0.0, min(1.0, value))  # Clamp to 0-1

                    parameter_changes.append({
                        'parameter': param,
                        'value': value,
                        'reason': config['reason'],
                        'confidence': 0.8
                    })

        # Apply action-based changes
        for action in actions:
            param_changes = self.process_action(action, intensity, current_params)
            parameter_changes.extend(param_changes)

        # Remove duplicates and prioritize
        parameter_changes = self.deduplicate_parameters(parameter_changes)

        return {
            'success': True,
            'parameter_changes': parameter_changes,
            'reasoning': f"Analyzed '{description}' -> {len(characteristics)} characteristics, {len(actions)} actions",
            'characteristics_found': characteristics,
            'intensity_modifier': intensity
        }

    def extract_characteristics(self, description: str) -> List[str]:
        """Extract sound characteristics from description"""
        characteristics = []

        for char in self.sound_mappings.keys():
            if char in description:
                characteristics.append(char)

        # Handle synonyms and variations
        synonyms = {
            'warm': ['warmer', 'warmth', 'smooth', 'mellow'],
            'bright': ['brighter', 'crisp', 'clear', 'sharp'],
            'dark': ['darker', 'deep', 'mysterious', 'moody'],
            'aggressive': ['harsh', 'biting', 'intense', 'brutal'],
            'soft': ['softer', 'gentle', 'smooth', 'mellow'],
            'movement': ['motion', 'moving', 'dynamic', 'evolving']
        }

        for char, words in synonyms.items():
            if any(word in description for word in words):
                if char not in characteristics:
                    characteristics.append(char)

        return characteristics

    def extract_actions(self, description: str) -> List[Dict]:
        """Extract specific actions from description"""
        actions = []

        # Pattern: "make it [characteristic]"
        make_pattern = r'make.*?(warm|bright|dark|soft|aggressive|punchy|fat|thin)'
        matches = re.findall(make_pattern, description)
        for match in matches:
            actions.append({
                'type': 'make',
                'target': match,
                'intensity': 1.0
            })

        # Pattern: "add [characteristic]"
        add_pattern = r'add.*?(warmth|brightness|punch|movement|character)'
        matches = re.findall(add_pattern, description)
        for match in matches:
            actions.append({
                'type': 'add',
                'target': match.rstrip('ness'),  # Remove suffix
                'intensity': 0.6  # Adding is less intense than making
            })

        return actions

    def extract_intensity(self, description: str) -> float:
        """Extract intensity modifier from description"""
        intensity = 1.0

        for word, modifier in self.intensity_words.items():
            if word in description:
                intensity *= modifier

        return max(0.1, min(2.0, intensity))  # Clamp to reasonable range

    def process_action(self, action: Dict, intensity: float, current_params: Dict) -> List[Dict]:
        """Process a specific action into parameter changes"""
        changes = []

        target = action['target']
        action_type = action['type']

        if target in self.sound_mappings:
            for param, config in self.sound_mappings[target].items():
                value = config['value']

                # Modify based on action type
                if action_type == 'add':
                    # Add means increase current value
                    current_val = current_params.get(param, 0.5) if current_params else 0.5
                    value = current_val + (value * 0.3 * intensity)
                elif action_type == 'make':
                    # Make means set to target value
                    value = value * intensity

                value = max(0.0, min(1.0, value))

                changes.append({
                    'parameter': param,
                    'value': value,
                    'reason': f"{action_type.title()} {target}: {config['reason']}",
                    'confidence': 0.7
                })

        return changes

    def deduplicate_parameters(self, parameter_changes: List[Dict]) -> List[Dict]:
        """Remove duplicate parameters, keeping highest confidence"""
        param_dict = {}

        for change in parameter_changes:
            param = change['parameter']
            if param not in param_dict or change['confidence'] > param_dict[param]['confidence']:
                param_dict[param] = change

        return list(param_dict.values())

# Initialize AI engine
ai_engine = SerumAIEngine()

@app.route('/generate', methods=['POST'])
def generate_parameters():
    """Generate parameter changes from natural language description"""
    try:
        data = request.get_json()

        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Description is required'
            }), 400

        description = data['description']
        current_params = data.get('current_parameters', {})
        device_type = data.get('device_type', 'serum')

        if device_type != 'serum':
            return jsonify({
                'success': False,
                'error': 'Only Serum device type is supported'
            }), 400

        # Process the description
        start_time = time.time()
        result = ai_engine.process_natural_language(description, current_params)
        processing_time = time.time() - start_time

        # Add metadata
        result['processing_time'] = processing_time
        result['model_info'] = {
            'engine': 'rule_based_nlp',
            'version': '1.0',
            'parameters_supported': len(ai_engine.tier1_params)
        }

        logger.info(f"Generated {len(result['parameter_changes'])} parameter changes in {processing_time:.3f}s")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'engine': 'serum_ai_engine',
        'parameters_loaded': len(ai_engine.tier1_params),
        'characteristics_supported': len(ai_engine.sound_mappings)
    })

@app.route('/characteristics', methods=['GET'])
def get_characteristics():
    """Get supported sound characteristics"""
    return jsonify({
        'characteristics': list(ai_engine.sound_mappings.keys()),
        'intensity_words': list(ai_engine.intensity_words.keys()),
        'action_words': list(ai_engine.action_words.keys())
    })

@app.route('/test', methods=['POST'])
def test_generation():
    """Test endpoint with sample descriptions"""
    test_descriptions = [
        "Make it warmer and deeper",
        "Add some aggressive character with movement",
        "Make it much brighter and punchier",
        "Softer and more gentle",
        "Very dark and mysterious"
    ]

    results = []
    for desc in test_descriptions:
        result = ai_engine.process_natural_language(desc)
        results.append({
            'description': desc,
            'parameters': len(result['parameter_changes']),
            'characteristics': result['characteristics_found']
        })

    return jsonify({
        'test_results': results,
        'engine_status': 'operational'
    })

if __name__ == '__main__':
    logger.info("🤖 Starting Serum AI Inference Server...")
    logger.info(f"Loaded {len(ai_engine.tier1_params)} Tier 1 parameters")
    logger.info(f"Supports {len(ai_engine.sound_mappings)} sound characteristics")

    # Enable CORS for Max for Live
    from flask_cors import CORS
    CORS(app)

    # Start server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )