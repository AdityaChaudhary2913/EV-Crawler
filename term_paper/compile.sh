#!/bin/bash

# LaTeX Compilation Script for Term Paper
# This script compiles the main.tex file and handles bibliography

echo "==================================="
echo "Compiling LaTeX Term Paper"
echo "==================================="

# Check if pdflatex is installed
if ! command -v pdflatex &> /dev/null
then
    echo "Error: pdflatex is not installed"
    echo "Please install LaTeX distribution:"
    echo "  macOS: brew install mactex"
    echo "  Ubuntu: sudo apt-get install texlive-full"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -f main.aux main.bbl main.blg main.log main.out main.toc main.pdf

# First pass
echo "Running pdflatex (1st pass)..."
pdflatex -interaction=nonstopmode main.tex

# Generate bibliography
echo "Running bibtex..."
bibtex main

# Second pass (resolve references)
echo "Running pdflatex (2nd pass)..."
pdflatex -interaction=nonstopmode main.tex

# Third pass (finalize)
echo "Running pdflatex (3rd pass)..."
pdflatex -interaction=nonstopmode main.tex

# Check if PDF was created
if [ -f "main.pdf" ]; then
    echo ""
    echo "==================================="
    echo "Compilation successful!"
    echo "Output: main.pdf"
    echo "==================================="
    
    # Open PDF if on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Opening PDF..."
        open main.pdf
    fi
else
    echo ""
    echo "==================================="
    echo "Compilation failed!"
    echo "Check main.log for errors"
    echo "==================================="
    exit 1
fi

# Clean auxiliary files
echo "Cleaning auxiliary files..."
rm -f main.aux main.bbl main.blg main.log main.out main.toc

echo "Done!"
