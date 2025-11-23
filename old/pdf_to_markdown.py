#!/usr/bin/env python3
"""
PDF to Markdown converter using Microsoft's markitdown library
Simple and effective conversion for better chunking
"""

import sys
from pathlib import Path
from markitdown import MarkItDown

def convert_pdf_to_markdown(pdf_path, output_path=None):
    """
    Convert PDF to markdown using markitdown

    Args:
        pdf_path: Path to input PDF file
        output_path: Optional output path (defaults to same name with .md extension)
    """
    # Initialize markitdown converter
    md_converter = MarkItDown()

    # Convert the PDF
    print(f"Converting: {pdf_path}")
    result = md_converter.convert(pdf_path)

    # Determine output path
    if output_path is None:
        output_path = Path(pdf_path).with_suffix('.md')

    # Write markdown to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.text_content)

    print(f"Conversion complete! Output saved to: {output_path}")
    return output_path

def main():
    # Input and output paths
    pdf_file = "Serum 2 User Guide.pdf"
    output_file = "Serum_2_User_Guide.md"

    # Check if PDF exists
    if not Path(pdf_file).exists():
        print(f"Error: {pdf_file} not found in current directory")
        sys.exit(1)

    # Perform conversion
    convert_pdf_to_markdown(pdf_file, output_file)

if __name__ == "__main__":
    main()