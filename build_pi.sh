#!/bin/bash
# Build ebook_reader for Raspberry Pi (Linux/ARM)
# Usage: bash build_pi.sh

# Install dependencies if needed
pip3 install --user pyinstaller pymupdf ebooklib

# Build the executable
pyinstaller --onefile --noconsole --add-data "ebooks:ebooks" ebook_reader.py

echo "Build complete. Find your executable in the dist/ folder."
