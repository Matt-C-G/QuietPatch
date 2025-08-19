#!/usr/bin/env bash
set -euo pipefail
mkdir -p release
cp -f dist/quietpatch.pyz dist/quietpatch dist/quietpatch.cmd release/ 2>/dev/null || true

# Generate checksums
( cd release && { command -v sha256sum >/dev/null && sha256sum * > SHA256SUMS || shasum -a 256 * > SHA256SUMS; } )

# Generate manifest
python3 tools/gen_manifest.py

echo "Release prepared: release/SHA256SUMS + manifest.json"
echo "Note: Install minisign for cryptographic signatures: brew install minisign"
