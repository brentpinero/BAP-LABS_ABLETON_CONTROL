#!/usr/bin/env python3
"""
Professional PDF to Markdown converter with comprehensive cleaning
Handles PDFs with complex formatting, removes artifacts, improves structure
"""

import re
import sys
from pathlib import Path
from markitdown import MarkItDown

def clean_markdown_comprehensive(content):
    """
    Comprehensive markdown cleanup with multiple passes
    """
    lines = content.split('\n')
    cleaned_lines = []
    skip_next = False
    in_code_block = False

    for i, line in enumerate(lines):
        # Skip if marked
        if skip_next:
            skip_next = False
            continue

        # Track code blocks to avoid processing them
        if '```' in line:
            in_code_block = not in_code_block
            cleaned_lines.append(line)
            continue

        # Don't process lines inside code blocks
        if in_code_block:
            cleaned_lines.append(line)
            continue

        # Remove standalone page numbers
        if re.match(r'^[0-9]{1,3}$', line.strip()):
            continue

        # Remove "Serum 2 User Guide" footer/header patterns
        if line.strip() in ["Serum 2 User Guide", "Serum User Guide"]:
            if i + 1 < len(lines) and re.match(r'^[0-9]{1,3}$', lines[i + 1].strip()):
                skip_next = True
            continue

        # Clean table of contents with dots
        line = re.sub(r'\.(\s+\.)+\s*', ' ', line)

        # Fix word breaks with hyphens at line end
        if line.endswith('-') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # Check if it's actually a word break
            if next_line and next_line[0].islower():
                # Merge the hyphenated word
                word_end = next_line.split()[0] if next_line else ""
                rest_of_next = ' '.join(next_line.split()[1:]) if len(next_line.split()) > 1 else ""
                line = line[:-1] + word_end
                if rest_of_next:
                    lines[i + 1] = rest_of_next
                else:
                    skip_next = True

        # Remove empty button/icon references (spaces between words that represent missing icons)
        line = re.sub(r'\s{2,}(button|icon|symbol)', ' [button]', line)
        line = re.sub(r'the\s+\s+button', 'the [button]', line)
        line = re.sub(r'click\s+\s+to', 'click [icon] to', line)
        line = re.sub(r'the\s+\s+\(', 'the [icon] (', line)

        # Fix lines that are just continuation of previous line (merge short fragments)
        if i > 0 and line and len(line) < 50 and not line[0].isupper() and not cleaned_lines[-1].endswith('.'):
            # Likely a continuation - merge with previous
            if cleaned_lines:
                cleaned_lines[-1] = cleaned_lines[-1] + ' ' + line.strip()
                continue

        # Header detection and formatting improvement
        stripped = line.strip()
        if stripped and i + 1 < len(lines):
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

            # Main sections (typically all caps or specific known sections)
            if (stripped.isupper() and len(stripped.split()) <= 5) or \
               stripped in ['Welcome', 'Getting Started', 'Exploring Serum', 'Table of Contents']:
                if not stripped.startswith('#'):
                    line = f"# {stripped}"

            # Subsections (Title Case, short, followed by content or empty line)
            elif (len(stripped) < 60 and
                  not stripped.endswith('.') and
                  not stripped.endswith(':') and
                  stripped[0].isupper() and
                  sum(1 for c in stripped if c.isupper()) >= 2):  # Has multiple capitals
                if not stripped.startswith('#'):
                    # Check if it looks like a section header
                    if not next_line or next_line[0].isupper() or len(stripped.split()) <= 6:
                        line = f"## {stripped}"

        cleaned_lines.append(line)

    # Join and do final cleanup
    result = '\n'.join(cleaned_lines)

    # Remove multiple blank lines
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    result = re.sub(r'\n{3}', '\n\n', result)

    # Fix spacing around headers
    result = re.sub(r'(#+ [^\n]+)\n([^\n#])', r'\1\n\n\2', result)

    # Clean up any remaining page number artifacts
    result = re.sub(r'\n\d{1,3}\n', '\n', result)

    return result

def convert_pdf_pro(pdf_path, output_path=None):
    """
    Professional PDF to markdown conversion with comprehensive cleaning
    """
    # Initialize converter
    md_converter = MarkItDown()

    print(f"Converting: {pdf_path}")
    result = md_converter.convert(pdf_path)

    # Apply comprehensive cleaning
    print("Applying comprehensive formatting cleanup...")
    cleaned_content = clean_markdown_comprehensive(result.text_content)

    # Output path
    if output_path is None:
        output_path = Path(pdf_path).stem + "_pro.md"

    # Write the cleaned content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    # Stats
    original_lines = len(result.text_content.split('\n'))
    cleaned_lines = len(cleaned_content.split('\n'))
    file_size_kb = len(cleaned_content) / 1024

    print(f"✅ Conversion complete!")
    print(f"📁 Output: {output_path}")
    print(f"📊 Stats: {original_lines} → {cleaned_lines} lines")
    print(f"💾 Size: {file_size_kb:.1f} KB")

    return output_path

def main():
    pdf_file = "Serum 2 User Guide.pdf"
    output_file = "Serum_2_User_Guide_Pro.md"

    if not Path(pdf_file).exists():
        print(f"❌ Error: {pdf_file} not found")
        sys.exit(1)

    convert_pdf_pro(pdf_file, output_file)

if __name__ == "__main__":
    main()