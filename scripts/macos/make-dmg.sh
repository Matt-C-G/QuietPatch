#!/bin/bash
# Create macOS DMG for QuietPatch
# Usage: ./scripts/macos/make-dmg.sh

set -euxo pipefail

APP="dist/QuietPatch.app"
STAGE="dist/dmg_stage"
DMG="dist/macos/QuietPatch-v0.4.0.dmg"
VOL="QuietPatch v0.4.0"

echo "Creating DMG for QuietPatch v0.4.0..."

# 0) cleanup any stale mounts named like the volume
hdiutil info | awk -v vol="$VOL" '$0 ~ vol {print prev} {prev=$0}' | awk '{print $1}' | xargs -I{} hdiutil detach {} || true
rm -rf "$STAGE" "$DMG"
mkdir -p "$STAGE" "dist/macos"

# 1) stage the app (no nesting)
cp -R "$APP" "$STAGE/QuietPatch.app"
xattr -dr com.apple.quarantine "$STAGE/QuietPatch.app"

# 2) create compressed DMG (HFS+ is fine)
hdiutil create -srcfolder "$STAGE" -volname "$VOL" -fs HFS+ -format UDZO -ov "$DMG"

# 3) sanity
hdiutil verify "$DMG"

echo "DMG created: $DMG"
echo "Size: $(du -h "$DMG" | cut -f1)"
