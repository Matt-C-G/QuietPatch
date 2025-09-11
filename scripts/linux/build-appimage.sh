#!/usr/bin/env bash
set -euo pipefail
mkdir -p AppDir/usr/bin release
cp dist/QuietPatchWizard AppDir/usr/bin/QuietPatch
printf "[Desktop Entry]
Type=Application
Name=QuietPatch
Exec=QuietPatch
Icon=QuietPatch
Categories=Utility;System;
" > AppDir/QuietPatch.desktop
cp assets/QuietPatch.png AppDir/QuietPatch.png || true
appimagetool AppDir QuietPatch-v0.4.0-x86_64.AppImage
mv QuietPatch-v0.4.0-x86_64.AppImage release/
