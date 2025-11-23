#!/usr/bin/env python3
"""
🎯 CLEAN DUPLICATE SUMMARY 🎯
Extract actionable duplicate information from the detection results
Focus on exact filename matches and parameter fingerprint matches only
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_clean_duplicates():
    """Generate clean summary of actual duplicates"""
    print("🎯 GENERATING CLEAN DUPLICATE SUMMARY")
    print("=" * 50)

    # Load the detection results
    report_path = "/Users/brentpinero/Documents/serum_llm_2/duplicate_analysis/duplicate_detection_report.json"

    print("📊 Analyzing detection results...")

    # Read just the summary section to avoid memory issues
    with open(report_path, 'r') as f:
        # Read line by line until we get the summary
        content = ""
        brace_count = 0
        in_summary = False

        for line in f:
            content += line
            brace_count += line.count('{') - line.count('}')

            if '"detection_summary"' in line:
                in_summary = True

            # Stop after we get the main structure (don't read all detailed matches)
            if in_summary and brace_count == 0:
                break

        # Parse what we have so far
        partial_data = json.loads(content + "}")

    summary = partial_data['detection_summary']

    print(f"📋 DUPLICATE DETECTION SUMMARY:")
    print(f"   🎯 Exact filename matches: {summary['exact_filename_matches']}")
    print(f"   📝 Preset name matches: {summary['preset_name_matches']}")
    print(f"   🔢 Parameter fingerprint matches: {summary['parameter_fingerprint_matches']}")

    # The exact filename matches are definitely duplicates
    exact_filename_count = summary['exact_filename_matches']
    parameter_exact_count = summary['parameter_fingerprint_matches']

    print(f"\\n🚫 RECOMMENDED ACTIONS:")
    print(f"   • SKIP {exact_filename_count} files with exact filename matches")
    print(f"   • REVIEW {parameter_exact_count} files with exact parameter matches")
    print(f"   • IGNORE {summary['preset_name_matches']} preset name matches (too many false positives)")

    # Calculate clean numbers
    total_new_files = 4223  # From our earlier count
    definite_duplicates = exact_filename_count
    potential_exact_duplicates = parameter_exact_count
    unique_new_presets = total_new_files - definite_duplicates

    print(f"\\n📊 FINAL NUMBERS:")
    print(f"   📁 Total new files found: {total_new_files}")
    print(f"   🚫 Definite duplicates (exact filename): {definite_duplicates}")
    print(f"   🔍 Potential exact duplicates (same parameters): {potential_exact_duplicates}")
    print(f"   ✅ Likely unique presets: ~{unique_new_presets}")
    print(f"   📈 Potential dataset growth: ~{unique_new_presets / 3857 * 100:.1f}%")

    return {
        'total_new_files': total_new_files,
        'exact_filename_duplicates': exact_filename_count,
        'parameter_exact_duplicates': parameter_exact_count,
        'estimated_unique': unique_new_presets
    }

def extract_duplicate_file_list():
    """Extract just the list of duplicate files to skip"""
    print("\\n📝 EXTRACTING DUPLICATE FILE LIST...")

    # We'll parse just the high confidence duplicates section
    duplicate_files = []

    # Since the file is huge, let's just focus on exact filename matches
    # These are definitely duplicates and should be skipped
    report_path = "/Users/brentpinero/Documents/serum_llm_2/duplicate_analysis/duplicate_detection_report.json"

    print("   Reading exact filename matches...")
    with open(report_path, 'r') as f:
        in_high_confidence = False
        brace_count = 0
        current_item = ""

        for line in f:
            if '"high_confidence_duplicates"' in line:
                in_high_confidence = True
                continue

            if in_high_confidence:
                current_item += line
                brace_count += line.count('{') - line.count('}')

                # If we have a complete item
                if '"match_type": "exact_filename"' in current_item and brace_count == 0:
                    try:
                        # Extract the new_file path
                        lines = current_item.split('\\n')
                        for item_line in lines:
                            if '"new_file":' in item_line:
                                # Extract file path
                                file_path = item_line.split('"new_file": "')[1].split('"')[0]
                                duplicate_files.append(file_path)
                                break
                    except:
                        pass
                    current_item = ""

                # Stop if we've moved past high confidence section
                if '"medium_confidence_duplicates"' in line:
                    break

    # Save the list of files to skip
    output_file = "/Users/brentpinero/Documents/serum_llm_2/duplicate_analysis/files_to_skip.txt"
    with open(output_file, 'w') as f:
        f.write('\\n'.join(duplicate_files))

    print(f"✅ Saved {len(duplicate_files)} duplicate files to: {output_file}")

    # Show a few examples
    print(f"\\n📝 EXAMPLES OF DUPLICATES TO SKIP:")
    for i, dup_file in enumerate(duplicate_files[:5]):
        print(f"   {i+1}. {Path(dup_file).name}")

    if len(duplicate_files) > 5:
        print(f"   ... and {len(duplicate_files) - 5} more")

    return duplicate_files

def main():
    """Generate clean duplicate analysis"""

    # Analyze duplicates
    summary = analyze_clean_duplicates()

    # Extract file list
    duplicate_files = extract_duplicate_file_list()

    print(f"\\n🎉 CLEAN DUPLICATE ANALYSIS COMPLETE!")
    print("=" * 50)
    print(f"📊 Analysis saved to: duplicate_analysis/")
    print(f"🚫 {len(duplicate_files)} files identified for skipping")
    print(f"📈 Estimated {summary['estimated_unique']} unique new presets to add")

if __name__ == "__main__":
    main()