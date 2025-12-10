#!/usr/bin/env python3
"""
Audio Rendering Pipeline for Serum Presets

Renders all presets as .wav files for CNN training:
- Load each .fxp preset into Serum
- Render across instrument-appropriate note ranges (Option C strategy)
- Capture and save audio output

Uses DawDreamer for offline VST rendering (faster than real-time).

Note Rendering Strategy (Option C - Instrument-Appropriate Ranges):
Each instrument type gets rendered across its musically-relevant octave range.
This gives the CNN:
  1. Key-invariant features (learns character, not just one pitch)
  2. Better generalization across the frequency spectrum
  3. Understanding of how presets transform across octaves
  4. ~100k+ total samples from 4,644 presets

Ranges per instrument type:
  - Bass/Sub: C1-B2 (24 notes) - sub to low-mid territory
  - Lead: C3-B4 (24 notes) - cutting mid to bright highs
  - Pad: C2-B3 (24 notes) - full harmonic development
  - Pluck: C3-B4 (24 notes) - emphasizes transient character
  - Keys: C2-B4 (36 notes) - full piano-like range
  - FX/Misc: C2-B3 (24 notes) - neutral middle range
  - Chord/Arp: C2-B3 (24 notes) - works with voicing
"""

import dawdreamer as daw
import numpy as np
import json
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging
from datetime import datetime
from tqdm import tqdm
import multiprocessing as mp
from functools import partial
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MIDI note reference:
# C1=24, C2=36, C3=48, C4=60, C5=72, C6=84
# Each octave is 12 semitones

# Instrument-appropriate note ranges (Option C)
# Format: (start_note, end_note) inclusive - renders all chromatic notes in range
INSTRUMENT_NOTE_RANGES = {
    # Bass instruments: C1-B2 (MIDI 24-47) - 24 notes
    # Captures sub frequencies and low-mid punch
    'bass': (24, 47),
    'bass_synth': (24, 47),
    '808': (24, 47),
    'sub': (24, 47),

    # Lead instruments: C3-B4 (MIDI 48-71) - 24 notes
    # Showcases brightness, cut, and melodic character
    'lead': (48, 71),
    'synth': (48, 71),

    # Pads: C2-B3 (MIDI 36-59) - 24 notes
    # Full harmonic content with room for sub-harmonics and overtones
    'pad': (36, 59),

    # Plucks: C3-B4 (MIDI 48-71) - 24 notes
    # Emphasizes attack transients and melodic range
    'pluck': (48, 71),

    # Keys: C2-B4 (MIDI 36-71) - 36 notes
    # Full keyboard range for piano/organ/electric piano sounds
    'keys': (36, 71),

    # FX/Misc: C2-B3 (MIDI 36-59) - 24 notes
    # Neutral range that captures most FX character
    'fx': (36, 59),
    'misc': (36, 59),

    # Chord/Arp: C2-B3 (MIDI 36-59) - 24 notes
    # Works well with built-in chord voicing and arpeggiation
    'chord': (36, 59),
    'arp': (36, 59),

    # Default fallback: C2-B3 (MIDI 36-59) - 24 notes
    'default': (36, 59)
}

# Duration per instrument type (some need longer for full envelope/tail)
INSTRUMENT_DURATIONS = {
    'bass': 2.0,       # Bass hits quick, 2s captures attack + sustain
    'bass_synth': 2.0,
    '808': 2.5,        # 808s have long sub decay
    'sub': 3.0,        # Sub needs time to develop
    'lead': 2.0,       # Leads are typically punchy
    'synth': 2.0,
    'pad': 4.0,        # Pads need longer for slow attack + sustain
    'pluck': 1.5,      # Plucks are short by nature - fast decay
    'keys': 2.5,       # Keys need sustain time
    'fx': 3.0,         # FX often have long evolving tails
    'misc': 2.0,
    'chord': 2.5,      # Chords need time for voicing to develop
    'arp': 3.0,        # Arps need time for sequence pattern
    'default': 2.0
}

# Note names for file naming
NOTE_NAMES = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']


def midi_to_note_name(midi_note: int) -> str:
    """Convert MIDI note number to note name (e.g., 60 -> 'C4')."""
    octave = (midi_note // 12) - 1
    note_idx = midi_note % 12
    return f"{NOTE_NAMES[note_idx]}{octave}"


def get_note_range_for_instrument(instrument_type: str) -> Tuple[int, int]:
    """Get optimal MIDI note range for an instrument type."""
    return INSTRUMENT_NOTE_RANGES.get(
        instrument_type.lower(),
        INSTRUMENT_NOTE_RANGES['default']
    )


def get_duration_for_instrument(instrument_type: str) -> float:
    """Get optimal render duration for an instrument type."""
    return INSTRUMENT_DURATIONS.get(
        instrument_type.lower(),
        INSTRUMENT_DURATIONS['default']
    )


def get_all_notes_for_instrument(instrument_type: str) -> List[int]:
    """Get list of all MIDI notes to render for an instrument type."""
    start, end = get_note_range_for_instrument(instrument_type)
    return list(range(start, end + 1))


class SerumAudioRenderer:
    """Renders Serum presets to audio files using DawDreamer."""

    # Serum plugin paths to try (in order of preference)
    # AU components work better with DawDreamer on macOS
    SERUM_PATHS = [
        "/Library/Audio/Plug-Ins/Components/Serum2.component",
        "/Library/Audio/Plug-Ins/Components/Serum.component",
        "/Library/Audio/Plug-Ins/VST/Serum.vst",
        "/Library/Audio/Plug-Ins/VST3/Serum2.vst3",
        "/Library/Audio/Plug-Ins/VST3/Serum.vst3",
    ]

    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 512,
        serum_path: Optional[str] = None
    ):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.serum_path = serum_path  # If None, will auto-detect
        self.engine = None
        self.synth = None

    def initialize(self) -> bool:
        """Initialize DawDreamer engine and load Serum."""
        try:
            logger.info(f"Initializing DawDreamer engine (SR={self.sample_rate}, buffer={self.buffer_size})")
            self.engine = daw.RenderEngine(self.sample_rate, self.buffer_size)

            # Auto-detect Serum path if not specified
            if self.serum_path is None:
                for path in self.SERUM_PATHS:
                    if Path(path).exists():
                        self.serum_path = path
                        break

            if self.serum_path is None:
                logger.error("Could not find Serum plugin. Tried: " + ", ".join(self.SERUM_PATHS))
                return False

            logger.info(f"Loading Serum from: {self.serum_path}")
            self.synth = self.engine.make_plugin_processor("serum", self.serum_path)

            # Verify plugin loaded by checking for a method we know exists
            if hasattr(self.synth, 'get_parameter'):
                # Try to get first parameter as a sanity check
                try:
                    param_name = self.synth.get_parameter_name(0)
                    logger.info(f"Serum loaded successfully (first param: {param_name})")
                except:
                    logger.info("Serum loaded successfully")
            else:
                logger.info("Serum loaded (could not verify parameters)")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    def load_preset(self, preset_path: str) -> bool:
        """Load a .fxp preset into Serum."""
        try:
            # DawDreamer uses load_state for preset loading
            if hasattr(self.synth, 'load_state'):
                self.synth.load_state(preset_path)
            elif hasattr(self.synth, 'load_preset'):
                self.synth.load_preset(preset_path)
            else:
                # Try reading binary and loading
                with open(preset_path, 'rb') as f:
                    preset_data = f.read()
                self.synth.set_state(preset_data)
            return True
        except Exception as e:
            logger.warning(f"Failed to load preset {preset_path}: {e}")
            return False

    def render_note(
        self,
        note: int = 60,  # C3 = MIDI note 60
        velocity: int = 100,
        duration_sec: float = 2.0,
        release_sec: float = 0.5
    ) -> Optional[np.ndarray]:
        """
        Render a single MIDI note through Serum.

        Args:
            note: MIDI note number (60 = C3)
            velocity: Note velocity (0-127)
            duration_sec: Note-on duration in seconds
            release_sec: Additional time after note-off for release tail

        Returns:
            Stereo audio array [samples, 2] or None on failure
        """
        try:
            total_duration = duration_sec + release_sec

            # Clear any previous state
            self.synth.clear_midi()

            # Add MIDI events (time in seconds)
            # Note on at time 0
            self.synth.add_midi_note(note, velocity, 0.0, duration_sec)

            # Set up the render graph
            graph = [
                (self.synth, [])  # Synth with no inputs (it generates audio)
            ]

            self.engine.load_graph(graph)

            # Render
            self.engine.render(total_duration)

            # Get output
            audio = self.engine.get_audio()

            # Transpose to [samples, channels] format
            if audio.shape[0] == 2:  # [2, samples]
                audio = audio.T

            return audio

        except Exception as e:
            logger.error(f"Failed to render note: {e}")
            return None

    def render_preset_to_file(
        self,
        preset_path: str,
        output_path: str,
        note: int = 60,
        velocity: int = 100,
        duration_sec: float = 2.0,
        release_sec: float = 0.5
    ) -> bool:
        """
        Load a preset and render it to a .wav file.

        Args:
            preset_path: Path to .fxp preset file
            output_path: Path for output .wav file
            note: MIDI note to play (default C3)
            velocity: Note velocity
            duration_sec: Note duration
            release_sec: Release tail duration

        Returns:
            True if successful
        """
        # Load preset
        if not self.load_preset(preset_path):
            return False

        # Render note
        audio = self.render_note(note, velocity, duration_sec, release_sec)
        if audio is None:
            return False

        # Normalize to prevent clipping
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.95

        # Save to file
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_path, audio, self.sample_rate)
            return True
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return False


def batch_render_presets(
    dataset_path: str = "data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json",
    output_dir: str = "data/rendered_audio",
    max_presets: Optional[int] = None,
    single_note: Optional[int] = None  # Override to render single note only (for testing)
) -> Dict:
    """
    Batch render all presets from the dataset across instrument-appropriate note ranges.

    Uses the ultimate dataset which contains source_file paths directly.

    Each preset is rendered at every note in its instrument type's range:
    - Bass: 24 notes (C1-B2)
    - Lead: 24 notes (C3-B4)
    - Pad: 24 notes (C2-B3)
    - Keys: 36 notes (C2-B4)
    - etc.

    Args:
        dataset_path: Path to JSON dataset with preset info (ultimate dataset has source_file)
        output_dir: Directory for rendered .wav files
        max_presets: Limit number of presets (for testing)
        single_note: If set, only render this MIDI note (for quick testing)

    Returns:
        Statistics dict with success/failure counts
    """
    # Load dataset
    logger.info(f"Loading dataset from {dataset_path}")
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    # Ultimate dataset is a list, training_ready is a dict with 'presets' key
    if isinstance(dataset, list):
        presets = dataset
    else:
        presets = dataset.get('presets', [])

    if max_presets:
        presets = presets[:max_presets]

    # Detect instrument type from preset name/category
    def get_instrument_type(preset):
        """Infer instrument type from preset data."""
        # Check for categorization (training_ready format)
        if 'categorization' in preset:
            return preset['categorization'].get('instrument', {}).get('type', 'default')

        # Infer from preset_name prefixes (ultimate format)
        name = preset.get('preset_name', '').lower()
        if any(x in name for x in ['bass', 'ba ', 'bd ', 'sub', '808']):
            return 'bass'
        elif any(x in name for x in ['lead', 'ld ', 'saw ']):
            return 'lead'
        elif any(x in name for x in ['pad', 'atm']):
            return 'pad'
        elif any(x in name for x in ['pluck', 'pl ', 'plk']):
            return 'pluck'
        elif any(x in name for x in ['key', 'ky ', 'piano', 'organ']):
            return 'keys'
        elif any(x in name for x in ['fx', 'sfx', 'riser', 'impact']):
            return 'fx'
        elif any(x in name for x in ['chord', 'chd']):
            return 'chord'
        elif any(x in name for x in ['arp']):
            return 'arp'
        return 'default'

    # Calculate total renders
    total_renders = 0
    for preset in presets:
        instrument_type = get_instrument_type(preset)
        if single_note:
            total_renders += 1
        else:
            notes = get_all_notes_for_instrument(instrument_type)
            total_renders += len(notes)

    logger.info(f"Found {len(presets)} presets")
    logger.info(f"Total audio files to render: {total_renders}")

    # Initialize renderer
    renderer = SerumAudioRenderer()
    if not renderer.initialize():
        logger.error("Failed to initialize renderer")
        return {"error": "Initialization failed"}

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Stats tracking
    stats = {
        "total_presets": len(presets),
        "total_renders": total_renders,
        "successful_renders": 0,
        "failed_renders": 0,
        "failed_presets": [],
        "presets_not_found": [],
        "output_dir": str(output_path),
        "timestamp": datetime.now().isoformat(),
        "render_strategy": "Option C - Instrument-Appropriate Ranges",
        "single_note_mode": single_note is not None
    }

    # Progress bar for total renders
    pbar = tqdm(total=total_renders, desc="Rendering audio files")

    # Render each preset
    for preset in presets:
        preset_name = preset.get('preset_name', 'unknown')

        # Get instrument type - use our inference function for ultimate dataset format
        instrument_type = get_instrument_type(preset)

        # Get notes to render for this instrument type
        if single_note:
            notes_to_render = [single_note]
        else:
            notes_to_render = get_all_notes_for_instrument(instrument_type)

        # Get duration for this instrument type
        duration = get_duration_for_instrument(instrument_type)

        # Create safe filename base
        safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in preset_name)

        # Create instrument-type subdirectory for organization
        instrument_dir = output_path / instrument_type
        instrument_dir.mkdir(parents=True, exist_ok=True)

        # Get preset file path - ultimate dataset has source_file directly
        preset_file = preset.get('source_file')

        if preset_file is None:
            logger.warning(f"No source_file for preset: {preset_name}")
            stats["presets_not_found"].append(preset_name)
            stats["failed_renders"] += len(notes_to_render)
            pbar.update(len(notes_to_render))
            continue

        # Fix path issue: dataset has Serum_1_Presets but actual path is Serum_Presets/Serum_1_Presets
        # Check if file exists, if not try the corrected path
        if not Path(preset_file).exists():
            # Try adding Serum_Presets/ to the path
            corrected_file = preset_file.replace('/Serum_1_Presets/', '/Serum_Presets/Serum_1_Presets/')
            if Path(corrected_file).exists():
                preset_file = corrected_file
            else:
                logger.warning(f"Preset file not found: {preset_file}")
                stats["presets_not_found"].append(preset_name)
                stats["failed_renders"] += len(notes_to_render)
                pbar.update(len(notes_to_render))
                continue

        # Load preset once, then render all notes
        if not renderer.load_preset(str(preset_file)):
            logger.warning(f"Failed to load preset: {preset_name}")
            stats["failed_presets"].append({"name": preset_name, "reason": "load_failed"})
            stats["failed_renders"] += len(notes_to_render)
            pbar.update(len(notes_to_render))
            continue

        # Render each note
        preset_success = 0
        for note in notes_to_render:
            note_name = midi_to_note_name(note)
            output_file = instrument_dir / f"{safe_name}_{note_name}.wav"

            # Render note
            audio = renderer.render_note(
                note=note,
                velocity=100,
                duration_sec=duration,
                release_sec=0.5
            )

            if audio is not None:
                # Normalize to prevent clipping
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio / max_val * 0.95

                # Save to file
                try:
                    sf.write(str(output_file), audio, renderer.sample_rate)
                    stats["successful_renders"] += 1
                    preset_success += 1
                except Exception as e:
                    logger.warning(f"Failed to save {output_file}: {e}")
                    stats["failed_renders"] += 1
            else:
                stats["failed_renders"] += 1

            pbar.update(1)

        # Log preset completion
        if preset_success == len(notes_to_render):
            logger.debug(f"Completed {preset_name}: {preset_success}/{len(notes_to_render)} notes")
        else:
            logger.warning(f"Partial render {preset_name}: {preset_success}/{len(notes_to_render)} notes")

    pbar.close()

    # Calculate success rate
    if stats["total_renders"] > 0:
        stats["success_rate"] = round(
            stats["successful_renders"] / stats["total_renders"] * 100, 2
        )

    # Save stats
    stats_file = output_path / "render_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    logger.info(f"Rendering complete!")
    logger.info(f"  Successful: {stats['successful_renders']}/{stats['total_renders']} ({stats.get('success_rate', 0)}%)")
    logger.info(f"  Failed: {stats['failed_renders']}")
    logger.info(f"  Presets not found: {len(stats['presets_not_found'])}")
    logger.info(f"Stats saved to {stats_file}")

    return stats


def find_preset_file(preset_name: str, preset_dir: str) -> Optional[Path]:
    """
    Find the actual .fxp file for a preset name.

    This handles the mapping between dataset preset names and actual file paths.
    """
    preset_root = Path(preset_dir)

    if not preset_root.exists():
        return None

    # Try exact match first
    for ext in ['.fxp', '.SerumPreset']:
        # Search recursively
        matches = list(preset_root.rglob(f"*{preset_name}*{ext}"))
        if matches:
            return matches[0]

    # Try with common variations
    clean_name = preset_name.replace("[", "").replace("]", "").strip()
    for ext in ['.fxp', '.SerumPreset']:
        matches = list(preset_root.rglob(f"*{clean_name}*{ext}"))
        if matches:
            return matches[0]

    return None


# =============================================================================
# PARALLEL RENDERING (Multiprocessing)
# =============================================================================

def render_preset_worker(preset_data: Dict, output_dir: str, single_note: Optional[int] = None, fxp_index: Dict = None) -> Dict:
    """
    Worker function for parallel rendering. Each worker:
    1. Creates its own RenderEngine + Serum instance
    2. Loads one preset
    3. Renders all notes for that preset
    4. Returns stats

    This runs in a separate process - do NOT share state between workers.
    """
    # Import inside worker to avoid serialization issues
    import dawdreamer as daw
    import numpy as np
    import soundfile as sf
    from pathlib import Path

    preset_name = preset_data.get('preset_name', 'unknown')
    preset_file = preset_data.get('source_file')
    instrument_type = preset_data.get('_instrument_type', 'default')

    result = {
        'preset_name': preset_name,
        'successful': 0,
        'failed': 0,
        'error': None
    }

    # Try to find the preset file
    found_file = None

    # 1. Check original path
    if preset_file and Path(preset_file).exists():
        found_file = preset_file
    # 2. Try path correction (Serum_1_Presets -> Serum_Presets/Serum_1_Presets)
    elif preset_file:
        corrected = preset_file.replace('/Serum_1_Presets/', '/Serum_Presets/Serum_1_Presets/')
        if Path(corrected).exists():
            found_file = corrected
    # 3. Try filename lookup in fxp_index
    if not found_file and fxp_index and preset_file:
        filename = Path(preset_file).name
        if filename in fxp_index:
            found_file = fxp_index[filename]

    if not found_file:
        result['error'] = f"File not found: {preset_file}"
        return result

    preset_file = found_file

    # Serum paths to try
    SERUM_PATHS = [
        "/Library/Audio/Plug-Ins/Components/Serum2.component",
        "/Library/Audio/Plug-Ins/Components/Serum.component",
    ]

    # Find Serum
    serum_path = None
    for p in SERUM_PATHS:
        if Path(p).exists():
            serum_path = p
            break

    if not serum_path:
        result['error'] = "Serum not found"
        return result

    try:
        # Create engine in this worker
        engine = daw.RenderEngine(44100, 512)
        synth = engine.make_plugin_processor("serum", serum_path)

        # Load preset
        if hasattr(synth, 'load_state'):
            synth.load_state(preset_file)
        elif hasattr(synth, 'load_preset'):
            synth.load_preset(preset_file)
        else:
            with open(preset_file, 'rb') as f:
                synth.set_state(f.read())

        # Determine notes to render
        if single_note:
            notes_to_render = [single_note]
        else:
            notes_to_render = get_all_notes_for_instrument(instrument_type)

        duration = get_duration_for_instrument(instrument_type)

        # Create output directory
        output_path = Path(output_dir) / instrument_type
        output_path.mkdir(parents=True, exist_ok=True)

        # Safe filename
        safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in preset_name)

        # Render each note
        for note in notes_to_render:
            try:
                synth.clear_midi()
                synth.add_midi_note(note, 100, 0.0, duration)

                graph = [(synth, [])]
                engine.load_graph(graph)
                engine.render(duration + 0.5)

                audio = engine.get_audio()
                if audio.shape[0] == 2:
                    audio = audio.T

                # Normalize
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio / max_val * 0.95

                # Save
                note_name = midi_to_note_name(note)
                output_file = output_path / f"{safe_name}_{note_name}.wav"
                sf.write(str(output_file), audio, 44100)

                result['successful'] += 1

            except Exception as e:
                result['failed'] += 1

    except Exception as e:
        result['error'] = str(e)
        result['failed'] = len(get_all_notes_for_instrument(instrument_type)) if not single_note else 1

    return result


def batch_render_parallel(
    dataset_path: str = "data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json",
    output_dir: str = "data/rendered_audio",
    max_presets: Optional[int] = None,
    single_note: Optional[int] = None,
    num_workers: Optional[int] = None
) -> Dict:
    """
    Parallel batch render using multiprocessing.

    Each worker gets its own RenderEngine + Serum instance to avoid
    thread safety issues. Splits presets across workers.

    Args:
        dataset_path: Path to JSON dataset
        output_dir: Output directory for .wav files
        max_presets: Limit presets (for testing)
        single_note: Override to render only one note
        num_workers: Number of parallel workers (default: cpu_count - 2)

    Returns:
        Statistics dict
    """
    print("=" * 60)
    print("PARALLEL BATCH RENDER")
    print("=" * 60)

    # Build .fxp file index for filename-based lookup
    print("Building .fxp file index...")
    project_root = Path("/Users/brentpinero/Documents/serum_llm_2")
    fxp_index = {}
    for fxp_file in project_root.rglob("*.fxp"):
        filename = fxp_file.name
        if filename not in fxp_index:
            fxp_index[filename] = str(fxp_file)
    print(f"Indexed {len(fxp_index)} unique .fxp files")

    # Load dataset
    print(f"Loading dataset from {dataset_path}")
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    if isinstance(dataset, list):
        presets = dataset
    else:
        presets = dataset.get('presets', [])

    if max_presets:
        presets = presets[:max_presets]

    # Infer instrument types and add to preset data
    def get_instrument_type(preset):
        if 'categorization' in preset:
            return preset['categorization'].get('instrument', {}).get('type', 'default')
        name = preset.get('preset_name', '').lower()
        if any(x in name for x in ['bass', 'ba ', 'bd ', 'sub', '808']):
            return 'bass'
        elif any(x in name for x in ['lead', 'ld ', 'saw ']):
            return 'lead'
        elif any(x in name for x in ['pad', 'atm']):
            return 'pad'
        elif any(x in name for x in ['pluck', 'pl ', 'plk']):
            return 'pluck'
        elif any(x in name for x in ['key', 'ky ', 'piano', 'organ']):
            return 'keys'
        elif any(x in name for x in ['fx', 'sfx', 'riser', 'impact']):
            return 'fx'
        elif any(x in name for x in ['chord', 'chd']):
            return 'chord'
        elif any(x in name for x in ['arp']):
            return 'arp'
        return 'default'

    # Add instrument type to each preset for worker
    for preset in presets:
        preset['_instrument_type'] = get_instrument_type(preset)

    # Calculate expected renders
    total_renders = sum(
        1 if single_note else len(get_all_notes_for_instrument(p['_instrument_type']))
        for p in presets
    )

    # Set up workers
    if num_workers is None:
        num_workers = max(1, mp.cpu_count() - 2)  # Leave 2 cores for system

    print(f"Presets to render: {len(presets)}")
    print(f"Total audio files: {total_renders}")
    print(f"Workers: {num_workers}")
    print(f"Output: {output_dir}")
    print()

    # Create output dir
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Prepare worker function with fixed args (pass fxp_index for filename lookup)
    worker_fn = partial(render_preset_worker, output_dir=output_dir, single_note=single_note, fxp_index=fxp_index)

    # Run parallel
    start_time = datetime.now()

    successful = 0
    failed = 0
    errors = []

    # Use spawn context for macOS compatibility
    ctx = mp.get_context('spawn')

    with ctx.Pool(num_workers) as pool:
        # Use imap for progress bar
        results = list(tqdm(
            pool.imap(worker_fn, presets),
            total=len(presets),
            desc="Rendering presets"
        ))

    # Aggregate results
    for r in results:
        successful += r['successful']
        failed += r['failed']
        if r['error']:
            errors.append({'preset': r['preset_name'], 'error': r['error']})

    elapsed = (datetime.now() - start_time).total_seconds()

    stats = {
        "total_presets": len(presets),
        "total_renders": total_renders,
        "successful_renders": successful,
        "failed_renders": failed,
        "errors": errors[:20],  # Keep first 20 errors
        "output_dir": output_dir,
        "timestamp": datetime.now().isoformat(),
        "render_strategy": "Option C - Instrument-Appropriate Ranges (Parallel)",
        "num_workers": num_workers,
        "elapsed_seconds": round(elapsed, 1),
        "renders_per_second": round(successful / elapsed, 1) if elapsed > 0 else 0
    }

    if total_renders > 0:
        stats["success_rate"] = round(successful / total_renders * 100, 2)

    # Save stats
    stats_file = Path(output_dir) / "render_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print()
    print("=" * 60)
    print("PARALLEL RENDER COMPLETE")
    print("=" * 60)
    print(f"  Successful: {successful}/{total_renders} ({stats.get('success_rate', 0)}%)")
    print(f"  Failed: {failed}")
    print(f"  Time: {elapsed:.1f}s ({stats['renders_per_second']} renders/sec)")
    print(f"  Workers: {num_workers}")
    print(f"  Stats: {stats_file}")

    return stats


def test_single_render():
    """Test rendering a single preset at multiple notes."""
    print("=" * 60)
    print("TESTING SINGLE PRESET RENDER (Multi-Note)")
    print("=" * 60)

    renderer = SerumAudioRenderer()
    if not renderer.initialize():
        print("Failed to initialize")
        return

    # Find a test preset
    test_presets = list(Path("Serum_Presets").rglob("*.fxp"))[:1]
    if not test_presets:
        test_presets = list(Path("Serum_1_Presets").rglob("*.fxp"))[:1]

    if not test_presets:
        print("No .fxp presets found")
        return

    test_preset = test_presets[0]
    print(f"Testing with preset: {test_preset.name}")

    # Test rendering at multiple notes to verify multi-note approach
    test_notes = [36, 48, 60, 72]  # C2, C3, C4, C5
    output_dir = Path("test_renders")
    output_dir.mkdir(exist_ok=True)

    # Load preset once
    if not renderer.load_preset(str(test_preset)):
        print("Failed to load preset")
        return

    print(f"\nRendering at {len(test_notes)} notes:")
    for note in test_notes:
        note_name = midi_to_note_name(note)
        output_file = output_dir / f"test_{note_name}.wav"

        audio = renderer.render_note(
            note=note,
            velocity=100,
            duration_sec=2.0,
            release_sec=0.5
        )

        if audio is not None:
            # Normalize
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val * 0.95

            sf.write(str(output_file), audio, renderer.sample_rate)

            import os
            size = os.path.getsize(output_file)
            print(f"  {note_name} (MIDI {note}): {size / 1024:.1f} KB - {output_file}")
        else:
            print(f"  {note_name} (MIDI {note}): FAILED")

    print(f"\nTest files saved to {output_dir}/")


def estimate_render_stats(dataset_path: str = "data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json"):
    """Estimate total renders and disk space needed."""
    print("=" * 60)
    print("RENDER ESTIMATION")
    print("=" * 60)

    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    # Ultimate dataset is a list, training_ready is a dict with 'presets' key
    if isinstance(dataset, list):
        presets = dataset
    else:
        presets = dataset.get('presets', [])

    # Detect instrument type from preset name/category (same as batch render)
    def get_instrument_type(preset):
        """Infer instrument type from preset data."""
        # Check for categorization (training_ready format)
        if 'categorization' in preset:
            return preset['categorization'].get('instrument', {}).get('type', 'default')

        # Infer from preset_name prefixes (ultimate format)
        name = preset.get('preset_name', '').lower()
        if any(x in name for x in ['bass', 'ba ', 'bd ', 'sub', '808']):
            return 'bass'
        elif any(x in name for x in ['lead', 'ld ', 'saw ']):
            return 'lead'
        elif any(x in name for x in ['pad', 'atm']):
            return 'pad'
        elif any(x in name for x in ['pluck', 'pl ', 'plk']):
            return 'pluck'
        elif any(x in name for x in ['key', 'ky ', 'piano', 'organ']):
            return 'keys'
        elif any(x in name for x in ['fx', 'sfx', 'riser', 'impact']):
            return 'fx'
        elif any(x in name for x in ['chord', 'chd']):
            return 'chord'
        elif any(x in name for x in ['arp']):
            return 'arp'
        return 'default'

    # Count by instrument type
    instrument_counts = {}
    total_renders = 0
    total_duration_sec = 0

    for preset in presets:
        inst_type = get_instrument_type(preset)
        instrument_counts[inst_type] = instrument_counts.get(inst_type, 0) + 1

        notes = get_all_notes_for_instrument(inst_type)
        duration = get_duration_for_instrument(inst_type)
        total_renders += len(notes)
        total_duration_sec += len(notes) * duration

    print(f"\nPresets by instrument type:")
    for inst, count in sorted(instrument_counts.items(), key=lambda x: -x[1]):
        notes = len(get_all_notes_for_instrument(inst))
        duration = get_duration_for_instrument(inst)
        print(f"  {inst:<12}: {count:>4} presets x {notes} notes = {count * notes:>6} renders ({duration}s each)")

    print(f"\nTotals:")
    print(f"  Total presets: {len(presets)}")
    print(f"  Total audio files: {total_renders}")
    print(f"  Total audio duration: {total_duration_sec / 3600:.1f} hours")

    # Estimate disk space (44.1kHz stereo 16-bit = ~176 KB/sec)
    avg_duration = total_duration_sec / total_renders if total_renders > 0 else 2.0
    estimated_size_gb = (total_renders * avg_duration * 176 * 1024) / (1024**3)
    print(f"  Estimated disk space: ~{estimated_size_gb:.1f} GB")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Render Serum presets to audio (Option C - Multi-Note)')
    parser.add_argument('--test', action='store_true', help='Test single preset render at multiple notes')
    parser.add_argument('--estimate', action='store_true', help='Estimate total renders and disk space')
    parser.add_argument('--batch', action='store_true', help='Batch render all presets (sequential)')
    parser.add_argument('--parallel', action='store_true', help='Batch render with multiprocessing (FAST)')
    parser.add_argument('--workers', type=int, default=None, help='Number of parallel workers (default: cpu_count-2)')
    parser.add_argument('--max', type=int, default=None, help='Max presets to render (for testing)')
    parser.add_argument('--single-note', type=int, default=None, help='Override: render only this MIDI note')
    parser.add_argument('--dataset', type=str, default='data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json', help='Path to dataset JSON with source_file paths')
    parser.add_argument('--output-dir', type=str, default='data/rendered_audio', help='Output directory')

    args = parser.parse_args()

    if args.test:
        test_single_render()
    elif args.estimate:
        estimate_render_stats()
    elif args.parallel:
        # Parallel rendering with multiprocessing
        stats = batch_render_parallel(
            dataset_path=args.dataset,
            output_dir=args.output_dir,
            max_presets=args.max,
            single_note=args.single_note,
            num_workers=args.workers
        )
    elif args.batch:
        # Sequential rendering
        stats = batch_render_presets(
            dataset_path=args.dataset,
            output_dir=args.output_dir,
            max_presets=args.max,
            single_note=args.single_note
        )
        print(f"\n{'=' * 60}")
        print("BATCH RENDER COMPLETE")
        print(f"{'=' * 60}")
        print(f"  Successful: {stats.get('successful_renders', 0)}/{stats.get('total_renders', 0)}")
        print(f"  Success rate: {stats.get('success_rate', 0)}%")
        print(f"  Presets not found: {len(stats.get('presets_not_found', []))}")
    else:
        print("Serum Audio Rendering Pipeline (Option C - Instrument-Appropriate Ranges)")
        print("=" * 60)
        print("\nUsage:")
        print("  --test        Test single preset render at multiple notes")
        print("  --estimate    Estimate total renders and disk space needed")
        print("  --batch       Batch render all presets (sequential)")
        print("  --parallel    Batch render with multiprocessing (FAST!)")
        print("  --workers N   Number of parallel workers (default: cpu_count-2)")
        print("  --max N       Limit to N presets (for testing)")
        print("  --single-note N  Override: render only MIDI note N")
        print("\nExamples:")
        print("  python audio_rendering_pipeline.py --estimate")
        print("  python audio_rendering_pipeline.py --test")
        print("  python audio_rendering_pipeline.py --batch --max 10")
        print("  python audio_rendering_pipeline.py --parallel --max 100  # Fast test")
        print("  python audio_rendering_pipeline.py --parallel            # Full parallel render")
