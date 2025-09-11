#!/bin/bash
# Build script for macOS QuietPatch v0.4.0
# Freezes the working build order with embedded CLI

set -e

echo "Building QuietPatch v0.4.0 for macOS..."

# Clean previous builds
rm -rf dist/QuietPatch.app dist/quietpatch build/stage

# Build CLI onefile
echo "Building CLI..."
.venv311/bin/pyinstaller --clean build/quietpatch_cli.spec

# Stage CLI for GUI bundling
echo "Staging CLI..."
mkdir -p build/stage/quietpatch-cli
cp -f dist/quietpatch build/stage/quietpatch-cli/quietpatch
chmod +x build/stage/quietpatch-cli/quietpatch

# Build GUI with embedded CLI
echo "Building GUI..."
.venv311/bin/pyinstaller --clean build/quietpatch_wizard.spec

echo "Build complete! App bundle: dist/QuietPatch.app"
echo "CLI embedded via _MEIPASS - not visible in Contents/MacOS/"
