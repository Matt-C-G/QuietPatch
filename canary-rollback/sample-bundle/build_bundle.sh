#!/bin/bash
# Build script to generate SHA256 hashes for bundle artifacts
# Usage: ./build_bundle.sh

set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$BUNDLE_DIR/manifest.json"

echo "Building QuietPatch bundle with SHA256 hashes..."

# Function to calculate SHA256
calc_sha256() {
    local file="$1"
    if [ -f "$file" ]; then
        shasum -a 256 "$file" | awk '{print tolower($1)}'
    else
        echo "FILE_NOT_FOUND"
    fi
}

# Update Windows artifacts
echo "Processing Windows artifacts..."
win_artifact_hash=$(calc_sha256 "$BUNDLE_DIR/artifacts/win/7zip-23.01-x64.msi")
win_rollback_hash=$(calc_sha256 "$BUNDLE_DIR/artifacts/win/7zip-22.01-x64.msi")

# Update macOS artifacts  
echo "Processing macOS artifacts..."
mac_artifact_hash=$(calc_sha256 "$BUNDLE_DIR/artifacts/mac/iterm2-3.5.12.pkg")
mac_rollback_hash=$(calc_sha256 "$BUNDLE_DIR/artifacts/mac/iterm2-3.5.10.pkg")

# Update Linux artifacts
echo "Processing Linux artifacts..."
linux_artifact_hash=$(calc_sha256 "$BUNDLE_DIR/artifacts/linux/vscode_1.93.1_amd64.deb")
linux_rollback_hash=$(calc_sha256 "$BUNDLE_DIR/artifacts/linux/vscode_1.91.0_amd64.deb")

# Create updated manifest with real hashes
python3 - <<EOF
import json
import sys

with open('$MANIFEST', 'r') as f:
    manifest = json.load(f)

# Update Windows target
for target in manifest['targets']:
    if target['os'] == 'windows':
        target['sha256']['artifact'] = '$win_artifact_hash'
        target['sha256']['rollback_artifact'] = '$win_rollback_hash'
    elif target['os'] == 'macos':
        target['sha256']['artifact'] = '$mac_artifact_hash'
        target['sha256']['rollback_artifact'] = '$mac_rollback_hash'
    elif target['os'] == 'linux':
        target['sha256']['artifact'] = '$linux_artifact_hash'
        target['sha256']['rollback_artifact'] = '$linux_rollback_hash'

# Write updated manifest
with open('$MANIFEST', 'w') as f:
    json.dump(manifest, f, indent=2)

print("Updated manifest with SHA256 hashes")
EOF

echo "Bundle build complete!"
echo ""
echo "SHA256 Hashes:"
echo "Windows artifact: $win_artifact_hash"
echo "Windows rollback: $win_rollback_hash"
echo "macOS artifact: $mac_artifact_hash"
echo "macOS rollback: $mac_rollback_hash"
echo "Linux artifact: $linux_artifact_hash"
echo "Linux rollback: $linux_rollback_hash"
echo ""
echo "Ready for deployment!"
