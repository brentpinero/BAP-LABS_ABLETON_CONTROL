#!/usr/bin/env python3
"""
🎛️ CLAUDE SERUM MISTRAL PIPELINE
Ultra-high quality synthetic data generation for Mistral instruction finetuning
Using Claude Sonnet 4 with best practices from 2024-2025 research
"""

import json
import os
import asyncio
import time
import re
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field
import logging
from dotenv import load_dotenv
import openai
from concurrent.futures import ThreadPoolExecutor
import random
from collections import defaultdict

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PresetContext:
    """Rich context analysis for preset"""
    name: str
    raw_parameters: Dict[str, float]
    mapped_parameters: Dict[str, float]

    # Inferred characteristics
    genre: Optional[str] = None
    instrument_type: Optional[str] = None
    sound_character: List[str] = field(default_factory=list)
    technical_features: List[str] = field(default_factory=list)
    complexity_score: float = 0.0

    # Parameter insights
    primary_oscillators: List[str] = field(default_factory=list)
    filter_characteristics: Dict[str, str] = field(default_factory=dict)
    envelope_profile: Dict[str, str] = field(default_factory=dict)
    modulation_depth: str = "none"

@dataclass
class SynthenticExample:
    """Complete synthetic training example with quality metrics"""
    instruction: str
    response: Dict
    mistral_template: str

    # Quality metrics
    instruction_quality: float = 0.0
    response_quality: float = 0.0
    diversity_score: float = 0.0
    technical_accuracy: float = 0.0
    overall_quality: float = 0.0

    # Metadata
    generation_method: str = ""
    persona_used: str = ""
    evolution_level: str = "base"

class EnhancedParameterMapper:
    """Advanced parameter mapping with deep analysis"""

    def __init__(self, parameter_mapping_file: str):
        with open(parameter_mapping_file, 'r') as f:
            self.mapping_data = json.load(f)

        self.param_map = self.mapping_data["parameter_map"]
        self.critical_params = self.mapping_data["critical_parameters"]
        self.param_categories = self.mapping_data.get("parameter_categories", {})

        # Build comprehensive mappings
        self.shorthand_to_index = self._build_shorthand_mapping()
        self.index_to_name = {str(v): k for k, v in self.param_map.items()}

        # Analysis patterns
        self.genre_patterns = self._build_genre_patterns()
        self.instrument_patterns = self._build_instrument_patterns()

    def _build_shorthand_mapping(self) -> Dict[str, int]:
        """Comprehensive parameter name mapping"""
        mapping = {}

        # Core parameter mappings with multiple variants
        mappings = {
            # Master/Global
            "mastervol": "Main Vol", "master_vol": "Main Vol", "main_vol": "Main Vol",
            "maintuning": "Main Tuning", "main_tuning": "Main Tuning", "tuning": "Main Tuning",
            "amp": "Amp", "amplitude": "Amp", "main_amp": "Amp",

            # Oscillator A
            "a_vol": "A Level", "a_level": "A Level", "osc_a_vol": "A Level", "osca_vol": "A Level",
            "a_pan": "A Pan", "osc_a_pan": "A Pan", "osca_pan": "A Pan",
            "a_octave": "A Octave", "a_oct": "A Octave", "osc_a_octave": "A Octave",
            "a_semi": "A Semi", "a_semitones": "A Semi", "osc_a_semi": "A Semi",
            "a_fine": "A Fine", "a_fine_tune": "A Fine", "osc_a_fine": "A Fine",
            "a_coarsepit": "A Coarse Pitch", "a_coarse_pitch": "A Coarse Pitch",
            "a_wtpos": "A WT Pos", "a_wt_pos": "A WT Pos", "a_wavetable_pos": "A WT Pos",
            "a_phase": "A Phase", "osc_a_phase": "A Phase",

            # Oscillator B
            "b_vol": "B Level", "b_level": "B Level", "osc_b_vol": "B Level", "oscb_vol": "B Level",
            "b_pan": "B Pan", "osc_b_pan": "B Pan", "oscb_pan": "B Pan",
            "b_octave": "B Octave", "b_oct": "B Octave", "osc_b_octave": "B Octave",
            "b_semi": "B Semi", "b_semitones": "B Semi", "osc_b_semi": "B Semi",
            "b_fine": "B Fine", "b_fine_tune": "B Fine", "osc_b_fine": "B Fine",
            "b_coarsepit": "B Coarse Pitch", "b_coarse_pitch": "B Coarse Pitch",
            "b_wtpos": "B WT Pos", "b_wt_pos": "B WT Pos", "b_wavetable_pos": "B WT Pos",
            "b_phase": "B Phase", "osc_b_phase": "B Phase",

            # Filters
            "filter1_freq": "Filter 1 Freq", "filter_1_freq": "Filter 1 Freq", "cutoff1": "Filter 1 Freq",
            "filter1_res": "Filter 1 Res", "filter_1_res": "Filter 1 Res", "resonance1": "Filter 1 Res",
            "filter1_drive": "Filter 1 Drive", "filter_1_drive": "Filter 1 Drive", "drive1": "Filter 1 Drive",
            "filter2_freq": "Filter 2 Freq", "filter_2_freq": "Filter 2 Freq", "cutoff2": "Filter 2 Freq",
            "filter2_res": "Filter 2 Res", "filter_2_res": "Filter 2 Res", "resonance2": "Filter 2 Res",
            "filter2_drive": "Filter 2 Drive", "filter_2_drive": "Filter 2 Drive", "drive2": "Filter 2 Drive",

            # Envelopes
            "env1_attack": "Env 1 Attack", "env_1_attack": "Env 1 Attack", "attack1": "Env 1 Attack",
            "env1_decay": "Env 1 Decay", "env_1_decay": "Env 1 Decay", "decay1": "Env 1 Decay",
            "env1_sustain": "Env 1 Sustain", "env_1_sustain": "Env 1 Sustain", "sustain1": "Env 1 Sustain",
            "env1_release": "Env 1 Release", "env_1_release": "Env 1 Release", "release1": "Env 1 Release",
            "env2_attack": "Env 2 Attack", "env_2_attack": "Env 2 Attack", "attack2": "Env 2 Attack",
            "env2_decay": "Env 2 Decay", "env_2_decay": "Env 2 Decay", "decay2": "Env 2 Decay",
            "env2_sustain": "Env 2 Sustain", "env_2_sustain": "Env 2 Sustain", "sustain2": "Env 2 Sustain",
            "env2_release": "Env 2 Release", "env_2_release": "Env 2 Release", "release2": "Env 2 Release",

            # LFOs
            "lfo1_rate": "LFO 1 Rate", "lfo_1_rate": "LFO 1 Rate", "lfo1_speed": "LFO 1 Rate",
            "lfo2_rate": "LFO 2 Rate", "lfo_2_rate": "LFO 2 Rate", "lfo2_speed": "LFO 2 Rate",
            "lfo1_smooth": "LFO 1 Smooth", "lfo_1_smooth": "LFO 1 Smooth",
            "lfo2_smooth": "LFO 2 Smooth", "lfo_2_smooth": "LFO 2 Smooth",

            # Macros
            "macro1": "Macro 1", "macro_1": "Macro 1", "m1": "Macro 1",
            "macro2": "Macro 2", "macro_2": "Macro 2", "m2": "Macro 2",
            "macro3": "Macro 3", "macro_3": "Macro 3", "m3": "Macro 3",
            "macro4": "Macro 4", "macro_4": "Macro 4", "m4": "Macro 4",

            # Sub/Noise
            "sub_level": "Sub Level", "sub_vol": "Sub Level", "sub": "Sub Level",
            "noise_level": "Noise Level", "noise_vol": "Noise Level", "noise": "Noise Level"
        }

        for shorthand, full_name in mappings.items():
            if full_name in self.param_map:
                mapping[shorthand] = self.param_map[full_name]

        return mapping

    def _build_genre_patterns(self) -> Dict[str, Dict]:
        """Build comprehensive genre detection patterns"""
        return {
            "dubstep": {
                "keywords": ["dubstep", "wobble", "bass", "drop", "brostep", "riddim"],
                "characteristics": ["heavy_bass", "filter_modulation", "aggressive"]
            },
            "trap": {
                "keywords": ["808", "trap", "drill", "hip hop", "rap", "bounce"],
                "characteristics": ["punchy_kick", "short_decay", "sub_heavy"]
            },
            "house": {
                "keywords": ["house", "tech house", "deep house", "garage", "four on floor"],
                "characteristics": ["steady_rhythm", "filtered_sweeps", "groove"]
            },
            "techno": {
                "keywords": ["techno", "minimal", "industrial", "acid", "detroit"],
                "characteristics": ["driving", "hypnotic", "repetitive"]
            },
            "trance": {
                "keywords": ["trance", "uplifting", "progressive", "psy", "goa"],
                "characteristics": ["long_builds", "emotional", "arpeggiated"]
            },
            "ambient": {
                "keywords": ["ambient", "drone", "atmospheric", "cinematic", "pad"],
                "characteristics": ["evolving", "slow_attack", "spacious"]
            },
            "dnb": {
                "keywords": ["dnb", "drum and bass", "jungle", "liquid", "neuro"],
                "characteristics": ["fast_tempo", "complex_rhythms", "sub_bass"]
            }
        }

    def _build_instrument_patterns(self) -> Dict[str, Dict]:
        """Build instrument type detection patterns"""
        return {
            "bass": {
                "keywords": ["bass", "sub", "808", "kick", "low", "bottom"],
                "freq_range": "low", "typical_params": ["sub_level", "filter1_freq"]
            },
            "lead": {
                "keywords": ["lead", "melody", "solo", "main", "synth"],
                "freq_range": "mid_high", "typical_params": ["filter1_res", "env1_attack"]
            },
            "pad": {
                "keywords": ["pad", "strings", "choir", "ambient", "texture"],
                "freq_range": "full", "typical_params": ["env1_attack", "lfo1_rate"]
            },
            "pluck": {
                "keywords": ["pluck", "stab", "bell", "piano", "harp"],
                "freq_range": "mid", "typical_params": ["env1_decay", "env1_release"]
            },
            "arp": {
                "keywords": ["arp", "sequence", "pattern", "gate"],
                "freq_range": "mid", "typical_params": ["lfo1_rate", "env1_release"]
            },
            "fx": {
                "keywords": ["fx", "noise", "sweep", "riser", "crash"],
                "freq_range": "wide", "typical_params": ["noise_level", "filter1_freq"]
            }
        }

    def analyze_preset_deep(self, preset_data: Dict) -> PresetContext:
        """Deep analysis of preset with rich context"""
        name = self._clean_name(preset_data.get("preset_name", "Unknown"))
        raw_params = preset_data.get("parameters", {})

        # Map parameters - COMPLETE SET!
        mapped_params = self._map_parameters_complete(raw_params)

        # Build context
        context = PresetContext(
            name=name,
            raw_parameters=raw_params,
            mapped_parameters=mapped_params,
            genre=self._analyze_genre(name, mapped_params),
            instrument_type=self._analyze_instrument_type(name, mapped_params),
            sound_character=self._analyze_sound_character(mapped_params),
            technical_features=self._analyze_technical_features(mapped_params),
            complexity_score=self._calculate_complexity_score(mapped_params),
            primary_oscillators=self._analyze_oscillators(mapped_params),
            filter_characteristics=self._analyze_filters(mapped_params),
            envelope_profile=self._analyze_envelopes(mapped_params),
            modulation_depth=self._analyze_modulation(mapped_params)
        )

        return context

    def _map_parameters_complete(self, raw_params: Dict[str, float]) -> Dict[str, float]:
        """Map ALL parameters - let Claude determine importance"""
        mapped = {}

        for param_name, value in raw_params.items():
            # Try to map parameter - NO FILTERING!
            if param_name in self.shorthand_to_index:
                index = self.shorthand_to_index[param_name]
                normalized = max(0.0, min(1.0, float(value)))

                # Include EVERYTHING - zeros, ones, defaults, all values
                mapped[str(index)] = normalized

        return mapped

    def _clean_name(self, name: str) -> str:
        """Clean and normalize preset name"""
        cleaned = re.sub(r'\x00+', '', name)  # Remove null bytes
        cleaned = re.sub(r'[^\w\s\-\(\)]', '', cleaned)  # Keep only safe chars
        cleaned = cleaned.strip()
        return cleaned if cleaned else "Generated Preset"

    def _analyze_genre(self, name: str, mapped_params: Dict[str, float]) -> Optional[str]:
        """Multi-factor genre analysis"""
        name_lower = name.lower()

        # Score each genre
        genre_scores = {}
        for genre, patterns in self.genre_patterns.items():
            score = 0

            # Name keyword matching
            for keyword in patterns["keywords"]:
                if keyword in name_lower:
                    score += 2

            # Parameter pattern matching (simplified for now)
            # This could be expanded with ML-based pattern recognition

            if score > 0:
                genre_scores[genre] = score

        # Return highest scoring genre
        if genre_scores:
            return max(genre_scores, key=genre_scores.get)
        return None

    def _analyze_instrument_type(self, name: str, mapped_params: Dict[str, float]) -> Optional[str]:
        """Multi-factor instrument analysis"""
        name_lower = name.lower()

        # Score each instrument type
        instrument_scores = {}
        for instrument, patterns in self.instrument_patterns.items():
            score = 0

            # Name keyword matching
            for keyword in patterns["keywords"]:
                if keyword in name_lower:
                    score += 2

            # Parameter presence matching
            for param in patterns.get("typical_params", []):
                if param in self.shorthand_to_index:
                    param_idx = str(self.shorthand_to_index[param])
                    if param_idx in mapped_params:
                        score += 1

            if score > 0:
                instrument_scores[instrument] = score

        if instrument_scores:
            return max(instrument_scores, key=instrument_scores.get)
        return None

    def _analyze_sound_character(self, mapped_params: Dict[str, float]) -> List[str]:
        """Analyze sound characteristics from parameters"""
        characteristics = []

        # Filter analysis
        filter_freq = mapped_params.get("206")  # Filter 1 Freq
        filter_res = mapped_params.get("207")   # Filter 1 Res
        filter_drive = mapped_params.get("208") # Filter 1 Drive

        if filter_freq is not None:
            if filter_freq < 0.3:
                characteristics.append("dark")
            elif filter_freq > 0.7:
                characteristics.append("bright")
            else:
                characteristics.append("balanced")

        if filter_res is not None:
            if filter_res > 0.6:
                characteristics.append("resonant")

        if filter_drive is not None:
            if filter_drive > 0.5:
                characteristics.append("driven")

        # Envelope analysis
        attack = mapped_params.get("225")  # Env 1 Attack
        if attack is not None:
            if attack < 0.1:
                characteristics.append("punchy")
            elif attack > 0.5:
                characteristics.append("evolving")

        # Oscillator analysis
        osc_a_level = mapped_params.get("22")   # A Level
        osc_b_level = mapped_params.get("77")   # B Level

        if osc_a_level and osc_b_level:
            if abs(osc_a_level - osc_b_level) > 0.3:
                characteristics.append("layered")

        return characteristics

    def _analyze_technical_features(self, mapped_params: Dict[str, float]) -> List[str]:
        """Identify technical features"""
        features = []

        # Check for unison
        if "45" in mapped_params:  # A Unison
            features.append("unison_a")
        if "100" in mapped_params:  # B Unison
            features.append("unison_b")

        # Check for wavetable scanning
        if "60" in mapped_params:   # A WT Pos
            features.append("wavetable_a")
        if "115" in mapped_params:  # B WT Pos
            features.append("wavetable_b")

        # Check for modulation
        lfo_params = [k for k in mapped_params.keys() if k in ["263", "268", "273"]]  # LFO rates
        if lfo_params:
            features.append("lfo_modulation")

        # Check for macro usage
        macro_params = [k for k in mapped_params.keys() if k in ["441", "442", "443", "444"]]
        if macro_params:
            features.append("macro_control")

        return features

    def _calculate_complexity_score(self, mapped_params: Dict[str, float]) -> float:
        """Calculate complexity based on parameter usage and variance"""
        if not mapped_params:
            return 0.0

        # Parameter count factor
        param_count = len(mapped_params)
        count_score = min(param_count / 25.0, 1.0)

        # Parameter variance factor
        values = list(mapped_params.values())
        if len(values) > 1:
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            variance_score = min(variance * 4, 1.0)
        else:
            variance_score = 0.0

        # Technical feature bonus
        tech_features = self._analyze_technical_features(mapped_params)
        tech_score = min(len(tech_features) / 4.0, 0.3)

        return (count_score * 0.5 + variance_score * 0.3 + tech_score * 0.2)

    def _analyze_oscillators(self, mapped_params: Dict[str, float]) -> List[str]:
        """Analyze oscillator usage"""
        oscillators = []

        if "22" in mapped_params:  # A Level
            oscillators.append("osc_a")
        if "77" in mapped_params:  # B Level
            oscillators.append("osc_b")
        if "132" in mapped_params: # C Level
            oscillators.append("osc_c")
        if "187" in mapped_params: # Noise Level
            oscillators.append("noise")
        if "195" in mapped_params: # Sub Level
            oscillators.append("sub")

        return oscillators

    def _analyze_filters(self, mapped_params: Dict[str, float]) -> Dict[str, str]:
        """Analyze filter characteristics"""
        filters = {}

        # Filter 1
        if "206" in mapped_params:  # Filter 1 Freq
            freq = mapped_params["206"]
            if freq < 0.3:
                filters["filter_1_type"] = "lowpass"
            elif freq > 0.7:
                filters["filter_1_type"] = "highpass"
            else:
                filters["filter_1_type"] = "bandpass"

        # Filter 2
        if "217" in mapped_params:  # Filter 2 Freq
            freq = mapped_params["217"]
            if freq < 0.3:
                filters["filter_2_type"] = "lowpass"
            elif freq > 0.7:
                filters["filter_2_type"] = "highpass"
            else:
                filters["filter_2_type"] = "bandpass"

        return filters

    def _analyze_envelopes(self, mapped_params: Dict[str, float]) -> Dict[str, str]:
        """Analyze envelope characteristics"""
        envelopes = {}

        # Envelope 1
        attack = mapped_params.get("225")   # Env 1 Attack
        decay = mapped_params.get("227")    # Env 1 Decay
        release = mapped_params.get("229")  # Env 1 Release

        if attack is not None:
            if attack < 0.1:
                envelopes["env_1_attack"] = "fast"
            elif attack > 0.5:
                envelopes["env_1_attack"] = "slow"
            else:
                envelopes["env_1_attack"] = "medium"

        if release is not None:
            if release < 0.2:
                envelopes["env_1_release"] = "short"
            elif release > 0.6:
                envelopes["env_1_release"] = "long"
            else:
                envelopes["env_1_release"] = "medium"

        return envelopes

    def _analyze_modulation(self, mapped_params: Dict[str, float]) -> str:
        """Analyze modulation depth"""
        lfo_count = sum(1 for k in mapped_params.keys() if k in ["263", "268", "273", "278"])
        macro_count = sum(1 for k in mapped_params.keys() if k in ["441", "442", "443", "444"])

        total_mod = lfo_count + macro_count

        if total_mod == 0:
            return "none"
        elif total_mod <= 2:
            return "light"
        elif total_mod <= 4:
            return "moderate"
        else:
            return "heavy"

class ClaudeInstructionGenerator:
    """Claude Sonnet 4 powered instruction generation"""

    def __init__(self, api_key: str, parameter_mapper=None):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.parameter_mapper = parameter_mapper  # Need access to parameter mappings
        self.index_to_name = parameter_mapper.index_to_name if parameter_mapper else {}

        # Producer personas for diversity
        self.personas = {
            "beginner_producer": "You're a beginner producer learning sound design, asking simple, direct questions about creating basic sounds.",
            "pro_producer": "You're a professional producer with deep technical knowledge, making specific requests with precise sound design terminology.",
            "genre_specialist": "You're a genre specialist who knows the exact sound characteristics needed for specific musical styles.",
            "live_performer": "You're a live electronic performer who needs sounds that work well in a performance context with real-time control.",
            "sound_designer": "You're a sound designer focused on creating unique, innovative sounds that push creative boundaries.",
            "remix_artist": "You're a remix artist who needs to recreate and modify existing sound styles for new contexts.",
            "beat_maker": "You're a beat maker focused on rhythm and groove, needing sounds that fit perfectly in the mix."
        }

        # Evolution techniques (from research)
        self.evolution_methods = {
            "in_depth": "Expand simple requests into detailed, technical specifications",
            "in_breadth": "Create variations exploring different aspects of the same sound",
            "contextual": "Add musical context and usage scenarios",
            "emotional": "Include emotional and vibe descriptors",
            "technical": "Focus on specific synthesis parameters and techniques"
        }

    async def generate_instructions(self, context: PresetContext, count: int = 1) -> List[Dict]:
        """Generate diverse instructions using Claude Sonnet 4"""

        # Build comprehensive analysis prompt
        analysis_prompt = self._build_analysis_prompt(context)

        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=16000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )

            # Extract text from response, handling thinking blocks
            content_parts = []
            for block in response.content:
                if hasattr(block, 'text'):
                    content_parts.append(block.text)
                elif block.type == 'text':
                    content_parts.append(block.text)
            content = '\n'.join(content_parts)
            logger.info(f"Claude raw response length: {len(content) if content else 0}")
            logger.debug(f"GPT-5 raw response: {content[:500] if content else 'None'}")
            instructions = self._parse_claude_response(content)

            # Apply evolution techniques
            evolved_instructions = await self._evolve_instructions(instructions, context)

            return evolved_instructions[:count]

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            logger.error(f"Model: {self.model}, Preset: {context.name}")
            logger.error(f"Falling back to default instructions")
            return self._fallback_instructions(context)

    def _build_system_prompt(self) -> str:
        """Comprehensive system prompt for Claude"""
        return """You are an expert music producer and sound designer with deep knowledge of Serum synthesizer.

Your task: Analyze preset data and generate natural, diverse instructions that real producers would use.

IMPORTANT GUIDELINES:
1. Generate 5-7 varied instruction types
2. Use natural, conversational language producers actually use
3. Include technical terms appropriately for different skill levels
4. Consider musical context and usage scenarios
5. Vary complexity from simple to advanced requests
6. Use diverse vocabulary and avoid repetitive patterns

INSTRUCTION TYPES TO INCLUDE:
- Genre-based: "Create a dubstep wobble bass"
- Character-based: "I need something dark and aggressive"
- Technical: "Make a bass with filter automation"
- Context-based: "Something for the breakdown section"
- Vibe/mood: "Design something mysterious and evolving"
- Comparison: "Like [reference] but more [characteristic]"
- Problem-solving: "I need a lead that cuts through the mix"

OUTPUT FORMAT:
Return exactly this JSON structure:
{
  "instructions": [
    {"text": "instruction 1", "type": "genre", "complexity": "simple"},
    {"text": "instruction 2", "type": "character", "complexity": "moderate"},
    ...
  ]
}"""

    def _build_analysis_prompt(self, context: PresetContext) -> str:
        """Build COMPLETE analysis prompt for Claude with FULL parameter set"""

        # Count active parameters (non-zero)
        active_params = {idx: val for idx, val in context.mapped_parameters.items() if abs(val) > 1e-6}

        # Format ALL parameters for Claude analysis
        param_display = []
        param_count = 0
        for idx, val in context.mapped_parameters.items():
            # Include parameter name if we have it
            param_name = self.index_to_name.get(idx, f"param_{idx}")
            param_display.append(f"  [{idx}] {param_name}: {val:.3f}")
            param_count += 1

            # Break into chunks for readability
            if param_count % 20 == 0:
                param_display.append("")  # Add blank line every 20 params

        # Create comprehensive parameter summary
        full_param_listing = "\n".join(param_display) if param_display else "No parameters mapped"

        prompt = f"""
COMPLETE PRESET ANALYSIS - ALL {len(context.mapped_parameters)} PARAMETERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎹 PRESET: "{context.name}"

📊 FULL PARAMETER DATA ({len(context.mapped_parameters)} total, {len(active_params)} active):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{full_param_listing}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 INITIAL ANALYSIS:
   Genre: {context.genre or 'analyze from parameters'}
   Instrument: {context.instrument_type or 'analyze from parameters'}
   Sound Character: {', '.join(context.sound_character) or 'analyze from parameters'}
   Technical Features: {', '.join(context.technical_features) or 'analyze from parameters'}

🎛️ SYNTHESIS DETAILS:
   Primary Oscillators: {', '.join(context.primary_oscillators) or 'analyze from parameters'}
   Filter Profile: {context.filter_characteristics or 'analyze from parameters'}
   Envelope Profile: {context.envelope_profile or 'analyze from parameters'}
   Modulation Depth: {context.modulation_depth}
   Complexity Score: {context.complexity_score:.2f}/1.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 CLAUDE DEEP ANALYSIS TASK:

Analyze this COMPLETE parameter set to understand:
1. What this preset actually sounds like
2. The vibe, character, and feel of the sound
3. What genre/musical context would use this sound
4. What the sound designer was going for

Then generate 1 CASUAL instruction that real producers/musicians would actually say when making music.

CRITICAL INSTRUCTION STYLE GUIDELINES:
- MAXIMUM 15 WORDS PER INSTRUCTION - NO EXCEPTIONS!
- Write like texting a producer friend, not writing a manual
- Focus on FEEL and VIBE only - no technical details whatsoever
- Use everyday producer slang and casual language
- NO processing chains, NO frequency ranges, NO BPM mentions, NO mixing advice
- NO bullet points, NO specifications, NO "variants" or options
- Think: "What's the shortest way to describe this sound's character?"

PERFECT EXAMPLES (short & natural):
- "Warm bass that sits under everything"
- "Bright stabby thing for the drop"
- "Classic 808 kick sound"
- "Dusty neo-soul keys"
- "Chunky saw lead"
- "Dark and rubbery 808"
- "Shimmery pad for the chorus"

TERRIBLE EXAMPLES (too long/technical):
- "Design a clean, modern trap 808 kick that slams in the mix with tight attack..."
- "For a bass-focused element in a moody, downtempo electronic track at 72-88 BPM..."
- "Include recommended processing chain and settings"
- "Provide two variants: one slightly saturated for analog grit..."

If it's longer than a text message, it's too long. Keep it simple and natural!
"""

        return prompt

    def _parse_claude_response(self, content: str) -> List[Dict]:
        """Parse Claude JSON response with fallback"""
        try:
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("instructions", [])
        except:
            pass

        # Fallback: parse as text list
        instructions = []
        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Match various list formats
            if re.match(r'^\d+[\.\)]\s*', line):
                instruction = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
            elif line.startswith('- ') or line.startswith('• '):
                instruction = line[2:].strip()
            elif len(line) > 15 and not any(char in line for char in [':', '━', '=']):
                instruction = line
            else:
                continue

            if instruction:
                instructions.append({
                    "text": instruction,
                    "type": "general",
                    "complexity": "moderate"
                })

        return instructions[:7]

    async def _evolve_instructions(self, instructions: List[Dict], context: PresetContext) -> List[Dict]:
        """Apply evolution techniques to instructions"""
        evolved = []

        for instruction in instructions:
            base_instruction = instruction.copy()
            evolved.append(base_instruction)

            # Apply random evolution technique
            if len(evolved) < 10 and random.random() < 0.6:  # 60% chance to evolve
                evolution_type = random.choice(list(self.evolution_methods.keys()))
                evolved_instruction = await self._apply_evolution(instruction, context, evolution_type)
                if evolved_instruction:
                    evolved.append(evolved_instruction)

        return evolved

    async def _apply_evolution(self, instruction: Dict, context: PresetContext, evolution_type: str) -> Optional[Dict]:
        """Apply specific evolution technique"""

        evolution_prompts = {
            "in_depth": f"Expand this request with technical details: '{instruction['text']}'",
            "in_breadth": f"Create a variation of this request: '{instruction['text']}'",
            "contextual": f"Add musical context to this request: '{instruction['text']}'",
            "emotional": f"Add emotional/vibe descriptors to this request: '{instruction['text']}'",
            "technical": f"Make this request more technically specific: '{instruction['text']}'"
        }

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a music producer. Transform the given instruction as requested. Return only the new instruction, nothing else."},
                    {"role": "user", "content": evolution_prompts[evolution_type]}
                ],
                max_completion_tokens=16000,  # Also need high limit for evolution
                reasoning_effort="minimal"  # Fast evolution
            )

            evolved_text = response.choices[0].message.content.strip()

            return {
                "text": evolved_text,
                "type": instruction["type"],
                "complexity": "evolved",
                "evolution_method": evolution_type
            }

        except Exception as e:
            logger.error(f"Evolution error: {e}")
            return None

    def _fallback_instructions(self, context: PresetContext) -> List[Dict]:
        """Fallback instructions if Claude fails"""
        base_type = context.instrument_type or "synth"
        genre = context.genre or "electronic"

        fallback = [
            {"text": f"Create a {genre} {base_type} preset", "type": "genre", "complexity": "simple"},
            {"text": f"I need a {base_type} for {genre} music", "type": "context", "complexity": "simple"},
            {"text": f"Design a {base_type} with character", "type": "character", "complexity": "moderate"},
            {"text": f"Make me a {base_type} sound", "type": "general", "complexity": "simple"}
        ]

        return fallback

class QualityValidator:
    """Advanced quality validation system"""

    def __init__(self):
        self.min_parameters = 1  # Even single parameter changes can be valid
        self.max_parameters = 2623  # Full Serum parameter space!
        self.min_instruction_length = 10
        self.max_instruction_length = 5000  # Allow very detailed Claude instructions

    def validate_example(self, example: SynthenticExample) -> Tuple[bool, List[str], Dict[str, float]]:
        """Comprehensive validation with detailed scoring"""
        issues = []
        scores = {}

        # Instruction quality
        inst_score = self._score_instruction_quality(example.instruction, issues)
        scores["instruction"] = inst_score

        # Response quality
        resp_score = self._score_response_quality(example.response, issues)
        scores["response"] = resp_score

        # Technical accuracy
        tech_score = self._score_technical_accuracy(example.response, issues)
        scores["technical"] = tech_score

        # Diversity score (based on uniqueness)
        div_score = 0.7  # Would be calculated against existing dataset
        scores["diversity"] = div_score

        # Overall score
        overall = (inst_score * 0.3 + resp_score * 0.3 + tech_score * 0.3 + div_score * 0.1)
        scores["overall"] = overall

        is_valid = overall >= 0.6 and len(issues) == 0

        return is_valid, issues, scores

    def _score_instruction_quality(self, instruction: str, issues: List[str]) -> float:
        """Score instruction quality"""
        score = 1.0

        # Length check
        if len(instruction) < self.min_instruction_length:
            issues.append(f"Instruction too short: {len(instruction)}")
            score *= 0.5
        elif len(instruction) > self.max_instruction_length:
            issues.append(f"Instruction too long: {len(instruction)}")
            score *= 0.8

        # Quality indicators
        if any(word in instruction.lower() for word in ["create", "make", "design", "generate", "build"]):
            score *= 1.1  # Good action words

        if any(word in instruction.lower() for word in ["bass", "lead", "pad", "pluck", "arp"]):
            score *= 1.1  # Good instrument terms

        # Penalize generic terms
        if "sound" in instruction.lower() and len(instruction.split()) < 6:
            score *= 0.9  # Too generic

        return min(score, 1.0)

    def _score_response_quality(self, response: Dict, issues: List[str]) -> float:
        """Score response structure and content"""
        score = 1.0

        # Required fields
        if "preset_name" not in response:
            issues.append("Missing preset_name")
            score *= 0.5

        if "parameter_changes" not in response:
            issues.append("Missing parameter_changes")
            return 0.0

        param_changes = response["parameter_changes"]
        param_count = len(param_changes)

        # Parameter count
        if param_count < self.min_parameters:
            issues.append(f"Too few parameters: {param_count}")
            score *= 0.6
        elif param_count > self.max_parameters:
            issues.append(f"Too many parameters: {param_count}")
            score *= 0.8

        return score

    def _score_technical_accuracy(self, response: Dict, issues: List[str]) -> float:
        """Score technical accuracy of parameters"""
        score = 1.0

        param_changes = response.get("parameter_changes", [])

        # Handle both dict (old format) and list (new format)
        if isinstance(param_changes, dict):
            param_items = list(param_changes.items())
        else:
            param_items = [(str(p["index"]), p["value"]) for p in param_changes]

        for param_idx, value in param_items:
            # Valid index
            try:
                idx = int(param_idx)
                if not (1 <= idx <= 448):
                    issues.append(f"Invalid parameter index: {idx}")
                    score *= 0.9
            except ValueError:
                issues.append(f"Non-numeric parameter index: {param_idx}")
                score *= 0.8

            # Valid value range
            if not isinstance(value, (int, float)):
                issues.append(f"Invalid parameter value type: {type(value)}")
                score *= 0.8
            elif not (0.0 <= value <= 1.0):
                issues.append(f"Parameter value out of range: {value}")
                score *= 0.9

        return score

class MistralFormatter:
    """Format examples into Mistral training format"""

    def __init__(self, parameter_mapper=None):
        self.parameter_mapper = parameter_mapper
        self.system_prompt = (
            "You are a Serum 2 synthesizer preset generator. Create parameter "
            "settings as structured JSON responses with normalized values (0.0-1.0) "
            "and proper parameter indices (1-448)."
        )

    def format_example(self, instruction_data: Dict, context: PresetContext) -> SynthenticExample:
        """Format complete training example"""

        # Build response with array format for Max for Live compatibility
        parameter_changes_array = []
        for idx, value in context.mapped_parameters.items():
            param_name = self.parameter_mapper.index_to_name.get(idx, f"param_{idx}")
            parameter_changes_array.append({
                "index": int(idx),
                "value": value,
                "name": param_name
            })

        response = {
            "preset_name": context.name,
            "parameter_changes": parameter_changes_array
        }

        # Add critical parameters for transparency
        critical_changes = self._extract_critical_params(context.mapped_parameters)
        if critical_changes:
            response["critical_changes"] = critical_changes

        # Create Mistral template
        response_json = json.dumps(response, separators=(',', ':'))
        mistral_template = (
            f"<s>[INST] <<SYS>>\n{self.system_prompt}\n<</SYS>>\n\n"
            f"{instruction_data['text']} [/INST] {response_json} </s>"
        )

        example = SynthenticExample(
            instruction=instruction_data["text"],
            response=response,
            mistral_template=mistral_template,
            generation_method="gpt5_with_thinking",
            persona_used="",  # Would be set if persona was used
            evolution_level=instruction_data.get("evolution_method", "base")
        )

        return example

    def _extract_critical_params(self, mapped_parameters: Dict[str, float]) -> Dict[str, float]:
        """Extract critical parameters with human names"""
        critical_map = {
            "1": "master_volume",
            "22": "osc_a_level",
            "77": "osc_b_level",
            "206": "filter_1_freq",
            "207": "filter_1_res",
            "208": "filter_1_drive",
            "225": "env_1_attack",
            "227": "env_1_decay",
            "229": "env_1_release"
        }

        critical = {}
        for idx, value in mapped_parameters.items():
            if idx in critical_map:
                critical[critical_map[idx]] = value

        return critical

class SerumClaudePipeline:
    """Main Claude Sonnet 4 powered pipeline"""

    def __init__(self, config: Dict):
        self.config = config
        self.parameter_mapper = EnhancedParameterMapper(config["parameter_mapping_file"])
        self.claude_generator = ClaudeInstructionGenerator(
            config["anthropic_api_key"],
            parameter_mapper=self.parameter_mapper
        )
        self.quality_validator = QualityValidator()
        self.mistral_formatter = MistralFormatter(parameter_mapper=self.parameter_mapper)

        # Processing controls
        self.request_delay = config.get("request_delay", 1.0)
        self.max_concurrent = config.get("max_concurrent", 5)
        self.quality_threshold = config.get("quality_threshold", 0.6)

    async def process_preset(self, preset_data: Dict) -> List[SynthenticExample]:
        """Process single preset with Claude analysis"""

        try:
            # Deep analysis
            context = self.parameter_mapper.analyze_preset_deep(preset_data)

            # NO FILTERING! Let GPT-5 analyze everything
            # Even presets with few parameters might have unique characteristics

            # Generate instructions with Claude
            logger.info(f"Processing preset: {context.name}")
            instructions = await self.claude_generator.generate_instructions(context)
            logger.info(f"🎯 Claude generated {len(instructions)} instructions for {context.name}")

            # Create training examples
            examples = []
            for instruction_data in instructions:
                example = self.mistral_formatter.format_example(instruction_data, context)

                # Validate quality
                is_valid, issues, scores = self.quality_validator.validate_example(example)

                if is_valid and scores["overall"] >= self.quality_threshold:
                    # Set quality scores
                    example.instruction_quality = scores["instruction"]
                    example.response_quality = scores["response"]
                    example.technical_accuracy = scores["technical"]
                    example.diversity_score = scores["diversity"]
                    example.overall_quality = scores["overall"]

                    examples.append(example)
                    logger.info(f"✅ Accepted example: overall={scores['overall']:.2f} ({instruction_data.get('text', '')[:50]}...)")
                else:
                    logger.info(f"❌ Filtered example: overall={scores['overall']:.2f}, valid={is_valid}, issues={issues}")

            # Rate limiting
            await asyncio.sleep(self.request_delay)

            return examples

        except Exception as e:
            logger.error(f"Error processing preset {preset_data.get('preset_name', 'Unknown')}: {e}")
            return []

    def _save_progress(self, output_file: str, results: List[SynthenticExample], batch_num: int, total_batches: int):
        """Save progress after each batch"""
        progress_file = output_file.replace('.json', f'_progress_batch{batch_num}.json')

        output_data = {
            "metadata": {
                "total_examples": len(results),
                "batches_completed": f"{batch_num}/{total_batches}",
                "average_quality": sum(ex.overall_quality for ex in results) / len(results) if results else 0,
                "quality_threshold": self.quality_threshold,
                "status": "in_progress" if batch_num < total_batches else "complete"
            },
            "examples": [
                {
                    "instruction": ex.instruction,
                    "response": ex.response,
                    "mistral_template": ex.mistral_template,
                    "quality_scores": {
                        "instruction": ex.instruction_quality,
                        "response": ex.response_quality,
                        "technical": ex.technical_accuracy,
                        "diversity": ex.diversity_score,
                        "overall": ex.overall_quality
                    },
                    "metadata": {
                        "generation_method": ex.generation_method,
                        "evolution_level": ex.evolution_level
                    }
                } for ex in results
            ]
        }

        with open(progress_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"💾 Progress saved to {progress_file}")

    async def generate_dataset(self, input_file: str, output_file: str, max_presets: Optional[int] = None):
        """Generate complete synthetic dataset"""

        logger.info("🎛️ Starting Claude Sonnet 4 Powered Serum Pipeline...")
        logger.info(f"🤖 Using Claude Sonnet 4")

        # Load dataset
        with open(input_file, 'r') as f:
            presets = json.load(f)

        if max_presets:
            presets = presets[:max_presets]
            logger.info(f"Processing {len(presets)} presets")

        # Process with controlled concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_with_semaphore(preset):
            async with semaphore:
                return await self.process_preset(preset)

        # Create tasks
        tasks = [process_with_semaphore(preset) for preset in presets]

        # Process all
        logger.info(f"🔄 Processing {len(tasks)} presets with max {self.max_concurrent} concurrent...")
        results = []

        # Process in batches for better monitoring
        batch_size = 20
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, list):
                    results.extend(result)

            batch_num = i//batch_size + 1
            total_batches = (len(tasks) + batch_size - 1)//batch_size
            logger.info(f"Completed batch {batch_num}/{total_batches} - Total examples so far: {len(results)}")

            # Save progress after each batch
            self._save_progress(output_file, results, batch_num, total_batches)

        # Sort by quality
        results.sort(key=lambda x: x.overall_quality, reverse=True)

        # Save results
        output_data = {
            "metadata": {
                "total_examples": len(results),
                "presets_processed": len([r for r in results if r]),
                "average_quality": sum(ex.overall_quality for ex in results) / len(results) if results else 0,
                "quality_threshold": self.quality_threshold,
                "system_prompt": self.mistral_formatter.system_prompt,
                "gpt5_config": {
                    "model": "gpt-5",
                    "reasoning_effort": "medium",
                    "summary": "auto"
                },
                "generation_config": self.config
            },
            "examples": [
                {
                    "instruction": ex.instruction,
                    "response": ex.response,
                    "mistral_template": ex.mistral_template,
                    "quality_scores": {
                        "instruction": ex.instruction_quality,
                        "response": ex.response_quality,
                        "technical": ex.technical_accuracy,
                        "diversity": ex.diversity_score,
                        "overall": ex.overall_quality
                    },
                    "metadata": {
                        "generation_method": ex.generation_method,
                        "evolution_level": ex.evolution_level
                    }
                }
                for ex in results
            ]
        }

        # Save JSON
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        # Save JSONL for training
        jsonl_file = output_file.replace('.json', '.jsonl')
        with open(jsonl_file, 'w') as f:
            for example in results:
                f.write(json.dumps({"text": example.mistral_template}) + '\n')

        # Save high-quality subset
        high_quality = [ex for ex in results if ex.overall_quality >= 0.8]
        if high_quality:
            hq_file = output_file.replace('.json', '_high_quality.json')
            hq_data = output_data.copy()
            hq_data["metadata"]["total_examples"] = len(high_quality)
            hq_data["examples"] = output_data["examples"][:len(high_quality)]

            with open(hq_file, 'w') as f:
                json.dump(hq_data, f, indent=2)

        # Statistics
        logger.info("✅ Claude Pipeline Complete!")
        logger.info(f"📊 Generated {len(results)} total examples")
        logger.info(f"⭐ Average quality: {output_data['metadata']['average_quality']:.3f}")
        logger.info(f"🏆 High quality (≥0.8): {len(high_quality)} examples")
        logger.info(f"💾 Saved to {output_file} and {jsonl_file}")

        return output_data

def main():
    """Main execution with environment setup"""

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("❌ ANTHROPIC_API_KEY not found in environment!")
        logger.error("Add your Anthropic API key to .env file")
        return

    logger.info("🤖 Anthropic API key loaded successfully")

    # Configuration - UNLEASHED FOR FULL PARAMETER POWER!
    config = {
        "anthropic_api_key": api_key,
        "parameter_mapping_file": "data/serum2_parameter_mapping_final.json",
        "input_dataset": "data/claude_presets_500.json",
        "output_file": "data/serum_claude_mistral_500_dataset.json",
        "max_presets": 500,  # Full generation with casual instructions
        "quality_threshold": 0.5,  # Lower threshold since we want diversity
        "request_delay": 0.5,  # Slightly faster
        "max_concurrent": 5,    # More parallel processing
        "full_parameter_mode": True,  # NEW FLAG!
        "max_tokens": 4000,
        "reasoning_effort": "high"
    }

    # Create pipeline
    pipeline = SerumClaudePipeline(config)

    # Run async
    async def run_pipeline():
        return await pipeline.generate_dataset(
            config["input_dataset"],
            config["output_file"],
            config["max_presets"]
        )

    try:
        results = asyncio.run(run_pipeline())

        print("\n🎉 GPT-5 Pipeline Complete!")
        print(f"📊 Total examples: {results['metadata']['total_examples']}")
        print(f"⭐ Average quality: {results['metadata']['average_quality']:.3f}")
        print("🚀 Ready for Mistral finetuning!")

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()