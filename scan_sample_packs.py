#!/usr/bin/env python3
"""
Sample Pack & Project File Scanner
====================================
Scans the filesystem for production assets to build a comprehensive dataset.

Asset Types:
1. Sample Packs with the "Holy Trinity":
   - Presets (.fxp, .SerumPreset, .vital, etc.)
   - MIDI files (.mid, .midi)
   - Audio loops (.wav, .mp3, .aiff)

2. Project Files (Holy Grail):
   - Ableton projects (.als) with folder structure
   - Contains: presets used, MIDI, rendered audio, arrangement

3. MIDI-Preset Pairs:
   - MIDI files that reference specific presets by name

Exclusions:
- Personal projects in ~/Desktop/Current Music Projects (for now)
- System directories, caches, etc.

Output:
- JSON inventory of all found assets with metadata
- Grouped by pack/project for easy pairing

Usage:
    # Scan home directory
    python scan_sample_packs.py --scan-home

    # Scan specific directory
    python scan_sample_packs.py --path /path/to/samples

    # Quick scan (skip deep directories)
    python scan_sample_packs.py --quick

External Hard Drives:
    # Scan specific external drives
    python scan_sample_packs.py --scan-external

    # Your drives:
    #   - /Volumes/BTW HD/BTW - Old HD
    #   - /Volumes/B. Anthony
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import hashlib


# =============================================================================
# CONFIGURATION
# =============================================================================

# File extensions to look for
EXTENSIONS = {
    # Presets
    "presets": {".fxp", ".serumpreset", ".vital", ".nmsv", ".pjunoxl", ".aupreset"},

    # MIDI
    "midi": {".mid", ".midi"},

    # Audio (loops, samples, stems)
    "audio": {".wav", ".mp3", ".aiff", ".aif", ".flac", ".ogg"},

    # Project files
    "projects": {".als", ".flp", ".logic", ".ptx", ".rpp"},
}

# Directories to ALWAYS skip
SKIP_DIRS = {
    ".Trash",
    ".Spotlight-V100",
    ".fseventsd",
    "Library/Caches",
    "Library/Application Support/Google",
    "Library/Application Support/Slack",
    "Library/Application Support/Discord",
    "Library/Application Support/Code",
    "Library/Application Support/Firefox",
    "Library/Safari",
    "node_modules",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    # Time Machine backups (avoid duplicates from external drives)
    "Backups.backupdb",
    ".Trashes",
    ".TemporaryItems",
}

# Directories to EXCLUDE from dataset (personal work, etc.)
EXCLUDE_PATHS = {
    "/Users/brentpinero/Desktop/Current Music Projects",  # Personal projects - add later
}

# =============================================================================
# PERSONAL PROJECT FILTERING (For MIDI and .als files only)
# =============================================================================
# These patterns identify personal Ableton projects vs sample pack content
# Presets are ALWAYS kept - only MIDI and .als files are filtered

# Paths that indicate personal projects (for MIDI/.als filtering)
PERSONAL_PROJECT_PATTERNS = [
    "Ableton Projects",            # Personal working folders
    "/Ableton Project Info/",      # Inside an Ableton project folder
]

# Directory name patterns that indicate personal projects (ends with "Project")
# e.g., "Back And Forth 3 Project", "jazz roller w:oddlaw Project"
PERSONAL_PROJECT_SUFFIX = " Project"

def is_personal_project_path(filepath: str, is_preset: bool = False) -> bool:
    """
    Check if a file is from a personal Ableton project.

    Only filters MIDI and .als files - presets are ALWAYS kept.

    Args:
        filepath: Full path to the file
        is_preset: If True, always return False (keep all presets)

    Returns:
        True if file should be EXCLUDED (personal project)
    """
    # Never filter presets - we want ALL presets regardless of source
    if is_preset:
        return False

    # Check for personal project path patterns
    for pattern in PERSONAL_PROJECT_PATTERNS:
        if pattern in filepath:
            return True

    # Check if any parent directory ends with " Project" (Ableton naming convention)
    parts = Path(filepath).parts
    for part in parts:
        if part.endswith(PERSONAL_PROJECT_SUFFIX):
            return True

    return False

# External hard drive paths (your drives)
EXTERNAL_DRIVES = [
    "/Volumes/BTW HD/BTW - Old HD",
    "/Volumes/B. Anthony",
]

# Likely sample pack directory patterns
SAMPLE_PACK_INDICATORS = {
    "samples", "loops", "presets", "midi", "one shots", "one-shots",
    "drum kit", "drumkit", "pack", "bundle", "collection",
    "splice", "cymatics", "kshmr", "vengeance", "loopmasters",
    "output", "native instruments", "xfer", "serum",
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class AssetInfo:
    """Information about a single asset file."""
    path: str
    filename: str
    extension: str
    asset_type: str  # preset, midi, audio, project
    size_bytes: int
    parent_dir: str

    # Extracted metadata (if available)
    bpm: Optional[int] = None
    key: Optional[str] = None
    category: Optional[str] = None  # bass, lead, pad, etc.
    pack_name: Optional[str] = None


@dataclass
class PackInfo:
    """Information about a sample pack or project."""
    name: str
    path: str
    pack_type: str  # sample_pack, project, midi_preset_pair

    # Asset counts
    preset_count: int = 0
    midi_count: int = 0
    audio_count: int = 0
    project_count: int = 0

    # Asset lists
    presets: List[str] = field(default_factory=list)
    midi_files: List[str] = field(default_factory=list)
    audio_files: List[str] = field(default_factory=list)
    project_files: List[str] = field(default_factory=list)

    # Quality indicators
    has_holy_trinity: bool = False  # presets + midi + audio
    has_midi_preset_pairs: bool = False

    # Metadata
    total_size_mb: float = 0.0


@dataclass
class ScanResult:
    """Complete scan results."""
    scan_time: str
    scan_path: str
    total_files_scanned: int

    # Totals
    total_presets: int = 0
    total_midi: int = 0
    total_audio: int = 0
    total_projects: int = 0

    # Packs found
    packs: List[PackInfo] = field(default_factory=list)
    holy_trinity_packs: List[str] = field(default_factory=list)
    midi_preset_pairs: List[Dict] = field(default_factory=list)

    # Project files (the holy grail)
    project_folders: List[Dict] = field(default_factory=list)


# =============================================================================
# METADATA EXTRACTION
# =============================================================================

def extract_bpm_key(filename: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Extract BPM and key from filename.

    Common patterns:
    - 120_bass_loop_Cmaj.wav
    - TSP_S2PE_126_bass_brassy_Gmin.mid
    - espresso_flip_A#Maj_130bpm
    """
    bpm = None
    key = None

    # BPM patterns
    bpm_patterns = [
        r'(\d{2,3})_?bpm',  # 120bpm, 120_bpm
        r'_(\d{2,3})_',     # _120_
        r'^(\d{2,3})_',     # 120_ at start
    ]

    for pattern in bpm_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            potential_bpm = int(match.group(1))
            if 60 <= potential_bpm <= 200:  # Reasonable BPM range
                bpm = potential_bpm
                break

    # Key patterns (major/minor)
    key_patterns = [
        r'([A-G][#b]?)\s*(maj|min|major|minor)',  # Cmaj, C#min
        r'([A-G][#b]?m(?:aj|in)?)',  # Cm, Cmaj, Cmin
        r'_([A-G][#b]?)_',  # _C_ (less reliable)
    ]

    for pattern in key_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            key = match.group(0).strip('_')
            break

    return bpm, key


def extract_category(filename: str, path: str) -> Optional[str]:
    """Extract sound category from filename or path."""

    categories = {
        "bass": ["bass", "sub", "808", "reese"],
        "lead": ["lead", "synth", "pluck", "arp"],
        "pad": ["pad", "atmosphere", "ambient", "texture"],
        "drums": ["drum", "kick", "snare", "hat", "perc", "clap"],
        "fx": ["fx", "riser", "impact", "sweep", "transition"],
        "vocals": ["vocal", "vox", "acapella", "voice"],
        "keys": ["piano", "keys", "organ", "rhodes"],
        "guitar": ["guitar", "gtr"],
        "strings": ["string", "violin", "cello", "orchestra"],
    }

    text = (filename + " " + path).lower()

    for category, keywords in categories.items():
        if any(kw in text for kw in keywords):
            return category

    return None


def get_pack_name(path: str) -> str:
    """Infer pack name from directory structure."""
    parts = Path(path).parts

    # Look for pack-like directory names
    for part in reversed(parts):
        part_lower = part.lower()
        if any(indicator in part_lower for indicator in SAMPLE_PACK_INDICATORS):
            return part
        # Also check for common pack naming patterns
        if re.match(r'^[A-Z]{2,}_', part):  # e.g., "TSP_S2PE_..."
            return part

    # Fallback to parent directory
    return Path(path).parent.name


# =============================================================================
# SCANNING FUNCTIONS
# =============================================================================

def should_skip_dir(path: str) -> bool:
    """Check if directory should be skipped."""
    path_str = str(path)

    # Check exclusions
    for exclude in EXCLUDE_PATHS:
        if path_str.startswith(exclude):
            return True

    # Check skip patterns
    for skip in SKIP_DIRS:
        if skip in path_str:
            return True

    return False


def scan_directory(
    root_path: str,
    quick_mode: bool = False,
    max_depth: int = 10,
) -> ScanResult:
    """
    Scan directory for sample packs and project files.

    Args:
        root_path: Directory to scan
        quick_mode: Skip deep directories
        max_depth: Maximum directory depth to traverse
    """
    print(f"\n{'='*60}")
    print(f"SCANNING: {root_path}")
    print(f"{'='*60}\n")

    result = ScanResult(
        scan_time=datetime.now().isoformat(),
        scan_path=root_path,
        total_files_scanned=0,
    )

    # Track filtered personal project files
    filtered_midi = 0
    filtered_projects = 0

    # Track assets by directory for pack grouping
    dir_assets: Dict[str, Dict[str, List[AssetInfo]]] = defaultdict(
        lambda: {"presets": [], "midi": [], "audio": [], "projects": []}
    )

    root = Path(root_path)

    for dirpath, dirnames, filenames in os.walk(root):
        # Check depth
        depth = len(Path(dirpath).relative_to(root).parts)
        if quick_mode and depth > 5:
            dirnames.clear()
            continue
        if depth > max_depth:
            dirnames.clear()
            continue

        # Skip excluded directories
        if should_skip_dir(dirpath):
            dirnames.clear()
            continue

        # Filter out hidden and skip directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in SKIP_DIRS]

        for filename in filenames:
            if filename.startswith('.'):
                continue

            filepath = Path(dirpath) / filename
            ext = filepath.suffix.lower()

            # Determine asset type
            asset_type = None
            for atype, extensions in EXTENSIONS.items():
                if ext in extensions:
                    asset_type = atype
                    break

            if asset_type is None:
                continue

            # Filter personal projects for MIDI and .als files (keep ALL presets)
            filepath_str = str(filepath)
            is_preset = (asset_type == "presets")
            if asset_type in ("midi", "projects"):  # Only filter MIDI and project files
                if is_personal_project_path(filepath_str, is_preset=is_preset):
                    if asset_type == "midi":
                        filtered_midi += 1
                    else:
                        filtered_projects += 1
                    continue  # Skip personal project files

            result.total_files_scanned += 1

            # Extract metadata
            bpm, key = extract_bpm_key(filename)
            category = extract_category(filename, dirpath)
            pack_name = get_pack_name(dirpath)

            try:
                size = filepath.stat().st_size
            except:
                size = 0

            asset = AssetInfo(
                path=str(filepath),
                filename=filename,
                extension=ext,
                asset_type=asset_type,
                size_bytes=size,
                parent_dir=dirpath,
                bpm=bpm,
                key=key,
                category=category,
                pack_name=pack_name,
            )

            # Group by parent directory (or project folder)
            group_dir = find_pack_root(dirpath)
            # Map asset_type to dict key
            asset_key_map = {
                "presets": "presets",
                "midi": "midi",
                "audio": "audio",
                "projects": "projects",
            }
            asset_key = asset_key_map.get(asset_type, asset_type)
            dir_assets[group_dir][asset_key].append(asset)

            # Update totals
            if asset_type == "presets":
                result.total_presets += 1
            elif asset_type == "midi":
                result.total_midi += 1
            elif asset_type == "audio":
                result.total_audio += 1
            elif asset_type == "projects":
                result.total_projects += 1

        # Progress update
        if result.total_files_scanned % 1000 == 0:
            print(f"  Scanned {result.total_files_scanned} relevant files...")

    # Report filtered personal projects
    if filtered_midi > 0 or filtered_projects > 0:
        print(f"\n  Filtered personal project files:")
        print(f"    - MIDI files: {filtered_midi:,}")
        print(f"    - Project files (.als): {filtered_projects:,}")

    # Group into packs
    print(f"\n  Grouping into packs...")
    result.packs = group_into_packs(dir_assets)

    # Identify holy trinity packs
    for pack in result.packs:
        if pack.preset_count > 0 and pack.midi_count > 0 and pack.audio_count > 0:
            pack.has_holy_trinity = True
            result.holy_trinity_packs.append(pack.name)

    # Find MIDI-preset pairs
    result.midi_preset_pairs = find_midi_preset_pairs(result.packs)

    # Extract project folder info
    result.project_folders = extract_project_info(result.packs)

    return result


def find_pack_root(dirpath: str) -> str:
    """Find the root directory of a sample pack."""
    path = Path(dirpath)

    # Look for pack indicators going up the tree
    for i, part in enumerate(path.parts):
        if any(indicator in part.lower() for indicator in SAMPLE_PACK_INDICATORS):
            return str(Path(*path.parts[:i+1]))

    # Check for project folder pattern (ends with " Project")
    for i, part in enumerate(path.parts):
        if part.endswith(" Project"):
            return str(Path(*path.parts[:i+1]))

    # Fallback: use parent of parent (common for organized packs)
    if len(path.parts) > 2:
        return str(path.parent.parent)

    return dirpath


def group_into_packs(dir_assets: Dict) -> List[PackInfo]:
    """Group assets by pack/project."""
    packs = []

    for dir_path, assets in dir_assets.items():
        if not any(assets.values()):
            continue

        # Determine pack type
        if any(p.path.endswith('.als') for p in assets.get("projects", [])):
            pack_type = "project"
        elif assets.get("presets") and assets.get("midi"):
            pack_type = "midi_preset_pair"
        else:
            pack_type = "sample_pack"

        pack = PackInfo(
            name=Path(dir_path).name,
            path=dir_path,
            pack_type=pack_type,
            preset_count=len(assets.get("presets", [])),
            midi_count=len(assets.get("midi", [])),
            audio_count=len(assets.get("audio", [])),
            project_count=len(assets.get("projects", [])),
            presets=[a.path for a in assets.get("presets", [])],
            midi_files=[a.path for a in assets.get("midi", [])],
            audio_files=[a.path for a in assets.get("audio", [])[:100]],  # Limit for large packs
            project_files=[a.path for a in assets.get("projects", [])],
        )

        # Calculate total size
        total_size = sum(a.size_bytes for assets_list in assets.values() for a in assets_list)
        pack.total_size_mb = total_size / (1024 * 1024)

        packs.append(pack)

    return packs


def find_midi_preset_pairs(packs: List[PackInfo]) -> List[Dict]:
    """Find MIDI files that match preset names."""
    pairs = []

    for pack in packs:
        if not pack.midi_files or not pack.presets:
            continue

        # Build preset name lookup
        preset_names = {}
        for preset_path in pack.presets:
            name = Path(preset_path).stem.lower()
            # Clean up common prefixes/suffixes
            name = re.sub(r'^(init|default|template)_?', '', name)
            preset_names[name] = preset_path

        # Match MIDI files to presets
        for midi_path in pack.midi_files:
            midi_name = Path(midi_path).stem.lower()

            # Try to find matching preset
            for preset_name, preset_path in preset_names.items():
                if preset_name in midi_name or midi_name in preset_name:
                    pairs.append({
                        "midi": midi_path,
                        "preset": preset_path,
                        "pack": pack.name,
                        "match_confidence": "high" if preset_name == midi_name else "medium",
                    })
                    break

    return pairs


def extract_project_info(packs: List[PackInfo]) -> List[Dict]:
    """Extract detailed info from project folders."""
    projects = []

    for pack in packs:
        if pack.pack_type != "project" or not pack.project_files:
            continue

        for als_path in pack.project_files:
            # Parse project name for metadata
            project_name = Path(als_path).stem
            bpm, key = extract_bpm_key(project_name)

            projects.append({
                "name": project_name,
                "als_path": als_path,
                "folder": pack.path,
                "bpm": bpm,
                "key": key,
                "sample_count": pack.audio_count,
                "has_midi": pack.midi_count > 0,
            })

    return projects


# =============================================================================
# REPORTING
# =============================================================================

def print_summary(result: ScanResult):
    """Print scan summary."""
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    print(f"\nFiles scanned: {result.total_files_scanned:,}")
    print(f"\nAsset totals:")
    print(f"  Presets: {result.total_presets:,}")
    print(f"  MIDI files: {result.total_midi:,}")
    print(f"  Audio files: {result.total_audio:,}")
    print(f"  Project files: {result.total_projects:,}")

    print(f"\nPacks found: {len(result.packs)}")
    print(f"Holy Trinity packs (presets + MIDI + audio): {len(result.holy_trinity_packs)}")
    print(f"MIDI-Preset pairs: {len(result.midi_preset_pairs)}")
    print(f"Project folders: {len(result.project_folders)}")

    if result.holy_trinity_packs:
        print(f"\n{'='*60}")
        print("HOLY TRINITY PACKS (Most Valuable)")
        print(f"{'='*60}")
        for pack_name in result.holy_trinity_packs[:20]:
            print(f"  - {pack_name}")
        if len(result.holy_trinity_packs) > 20:
            print(f"  ... and {len(result.holy_trinity_packs) - 20} more")

    if result.midi_preset_pairs:
        print(f"\n{'='*60}")
        print("MIDI-PRESET PAIRS (High Confidence)")
        print(f"{'='*60}")
        high_confidence = [p for p in result.midi_preset_pairs if p["match_confidence"] == "high"]
        for pair in high_confidence[:10]:
            print(f"  - {Path(pair['midi']).name} <-> {Path(pair['preset']).name}")
        if len(high_confidence) > 10:
            print(f"  ... and {len(high_confidence) - 10} more")


def save_results(result: ScanResult, output_path: str):
    """Save scan results to JSON."""
    # Convert to dict for JSON serialization
    data = {
        "scan_time": result.scan_time,
        "scan_path": result.scan_path,
        "total_files_scanned": result.total_files_scanned,
        "totals": {
            "presets": result.total_presets,
            "midi": result.total_midi,
            "audio": result.total_audio,
            "projects": result.total_projects,
        },
        "holy_trinity_packs": result.holy_trinity_packs,
        "midi_preset_pairs": result.midi_preset_pairs,
        "project_folders": result.project_folders,
        "packs": [asdict(p) for p in result.packs],
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nResults saved to: {output_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Scan for sample packs and project files")

    parser.add_argument('--path', type=str, default=None,
                        help='Directory to scan')
    parser.add_argument('--scan-home', action='store_true',
                        help='Scan home directory')
    parser.add_argument('--scan-documents', action='store_true',
                        help='Scan Documents folder')
    parser.add_argument('--scan-external', action='store_true',
                        help='Scan external hard drives')
    parser.add_argument('--quick', action='store_true',
                        help='Quick scan (limit depth)')
    parser.add_argument('--output', type=str, default='data/sample_pack_inventory.json',
                        help='Output JSON file')
    parser.add_argument('--max-depth', type=int, default=10,
                        help='Maximum directory depth')

    args = parser.parse_args()

    # Determine scan path(s)
    scan_paths = []

    if args.scan_external:
        # Scan external hard drives
        for drive in EXTERNAL_DRIVES:
            if Path(drive).exists():
                scan_paths.append(drive)
            else:
                print(f"[WARNING] External drive not mounted: {drive}")
        if not scan_paths:
            print("[ERROR] No external drives found! Make sure they are connected.")
            return
    elif args.path:
        scan_paths = [args.path]
    elif args.scan_home:
        scan_paths = [str(Path.home())]
    elif args.scan_documents:
        scan_paths = [str(Path.home() / "Documents")]
    else:
        # Default: scan Documents
        scan_paths = [str(Path.home() / "Documents")]

    print("="*60)
    print("SAMPLE PACK & PROJECT SCANNER")
    print("="*60)
    print(f"\nScan paths:")
    for sp in scan_paths:
        print(f"  - {sp}")
    print(f"\nQuick mode: {args.quick}")
    print(f"Max depth: {args.max_depth}")
    print(f"\nExcluding personal projects in:")
    for exclude in EXCLUDE_PATHS:
        print(f"  - {exclude}")

    print(f"\nPersonal project filtering (MIDI/.als only):")
    print(f"  - Paths containing: {PERSONAL_PROJECT_PATTERNS}")
    print(f"  - Directories ending with: '{PERSONAL_PROJECT_SUFFIX}'")

    # Run scan for each path and merge results
    all_results = []
    for scan_path in scan_paths:
        print(f"\n{'='*60}")
        print(f"SCANNING: {scan_path}")
        print("="*60)

        result = scan_directory(
            scan_path,
            quick_mode=args.quick,
            max_depth=args.max_depth,
        )
        all_results.append(result)

    # If multiple paths, merge results
    if len(all_results) == 1:
        final_result = all_results[0]
    else:
        # Merge all results
        final_result = ScanResult(
            scan_time=datetime.now().isoformat(),
            scan_path=", ".join(scan_paths),
            total_files_scanned=sum(r.total_files_scanned for r in all_results),
            total_presets=sum(r.total_presets for r in all_results),
            total_midi=sum(r.total_midi for r in all_results),
            total_audio=sum(r.total_audio for r in all_results),
            total_projects=sum(r.total_projects for r in all_results),
        )
        for r in all_results:
            final_result.packs.extend(r.packs)
            final_result.holy_trinity_packs.extend(r.holy_trinity_packs)
            final_result.midi_preset_pairs.extend(r.midi_preset_pairs)
            final_result.project_folders.extend(r.project_folders)

    # Print summary
    print_summary(final_result)

    # Save results - use different output for external drives
    if args.scan_external:
        output_path = 'data/external_drive_inventory.json'
    else:
        output_path = args.output

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    save_results(final_result, output_path)

    print("\n" + "="*60)
    print("SCAN COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
