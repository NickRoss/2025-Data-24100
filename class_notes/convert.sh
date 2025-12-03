#!/bin/bash
set -e

# Check if input file is provided

if [ $# -eq 0 ]; then
    echo "Usage: $0 <input.md>"
    exit 1
fi

# Get input file
INPUT_FILE="$1"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' not found"
    exit 1
fi

# Generate output filename (replace .md with .html)
OUTPUT_FILE="output.html"

# Run pandoc
pandoc "$INPUT_FILE" -o "$OUTPUT_FILE" --from gfm --template=template.html -c style.css --toc

echo "Generated: $OUTPUT_FILE":
