#!/usr/bin/env bash
set -euo pipefail
rm -rf dist && mkdir -p dist

# Create a clean build directory with only necessary files
mkdir -p dist_build
cp -r src dist_build/
cp -r config dist_build/
cp qp_cli.py dist_build/
cp requirements.txt dist_build/ 2>/dev/null || true

# Build the zipapp from the clean directory
python3 -m zipapp dist_build -m "qp_cli:main" -o dist/quietpatch.pyz

# Clean up build directory
rm -rf dist_build

# Create simple wrappers
printf '%s\n' '#!/usr/bin/env bash' 'exec python3 "$(dirname "$0")/quietpatch.pyz" "$@"' > dist/quietpatch
chmod +x dist/quietpatch
printf '%s\r\n' '@echo off' 'python "%~dp0quietpatch.pyz" %*' > dist/quietpatch.cmd

echo "Built dist/quietpatch.pyz (+ wrappers)"
echo "Size: $(du -h dist/quietpatch.pyz | cut -f1)"
