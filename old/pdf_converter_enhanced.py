#!/usr/bin/env python3
"""
Enhanced PDF to Markdown converter using markitdown
Includes post-processing to clean up formatting issues
"""

import re
import sys
from pathlib import Path
from markitdown import MarkItDown

def clean_markdown(content):
    """
    Clean up markdown content from PDF conversion
    """
    lines = content.split('\n')
    cleaned_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        # Skip if we marked this line for skipping
        if skip_next:
            skip_next = False
            continue

        # Remove standalone page numbers (lines with just numbers 1-999)
        if re.match(r'^[0-9]{1,3}$', line.strip()):
            continue

        # Remove "Serum 2 User Guide" followed by page number pattern
        if line.strip() == "Serum 2 User Guide":
            # Check if next line is a page number
            if i + 1 < len(lines) and re.match(r'^[0-9]{1,3}$', lines[i + 1].strip()):
                skip_next = True
                continue
            continue

        # Clean up table of contents dots
        line = re.sub(r'(\s+\.){2,}', ' ', line)

        # Fix hyphenated line breaks (merge words split across lines)
        if line.endswith('-') and i + 1 < len(lines):
            # Check if next line starts with lowercase or continues word
            next_line = lines[i + 1].strip()
            if next_line and next_line[0].islower():
                line = line[:-1] + next_line
                skip_next = True

        # Try to identify headers and add markdown formatting
        # Look for lines that are all caps or title case followed by empty line
        if line and i + 1 < len(lines) and not lines[i + 1].strip():
            # Check if it might be a header (short, no punctuation at end except colon)
            if len(line) < 60 and not line.strip().endswith('.'):
                # Main sections (all caps or specific patterns)
                if line.isupper() or line in ['Welcome', 'Getting Started', 'Exploring Serum']:
                    line = f"# {line}"
                # Subsections (title case, not ending with period)
                elif line[0].isupper() and len(line.split()) <= 8:
                    line = f"## {line}"

        cleaned_lines.append(line)

    # Join lines and clean up excessive whitespace
    result = '\n'.join(cleaned_lines)

    # Remove multiple consecutive empty lines
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result

def convert_pdf_enhanced(pdf_path, output_path=None):
    """
    Convert PDF to clean markdown
    """
    # Initialize converter
    md_converter = MarkItDown()

    print(f"Converting: {pdf_path}")
    result = md_converter.convert(pdf_path)

    # Clean up the markdown
    print("Cleaning up formatting...")
    cleaned_content = clean_markdown(result.text_content)

    # Determine output path
    if output_path is None:
        output_path = Path(pdf_path).with_suffix('.md')

    # Write cleaned markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"Conversion complete! Clean output saved to: {output_path}")

    # Show stats
    original_lines = len(result.text_content.split('\n'))
    cleaned_lines = len(cleaned_content.split('\n'))
    print(f"Reduced from {original_lines} to {cleaned_lines} lines")

    return output_path

def main():
    pdf_file = "Serum 2 User Guide.pdf"
    output_file = "Serum_2_User_Guide_Clean.md"

    if not Path(pdf_file).exists():
        print(f"Error: {pdf_file} not found")
        sys.exit(1)

    convert_pdf_enhanced(pdf_file, output_file)

if __name__ == "__main__":
    main()