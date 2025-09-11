#!/usr/bin/env bash
set -euo pipefail
mkdir -p dist/macos
create-dmg --volname "QuietPatch v0.4.0" --window-size 600 400 \
  --icon-size 100 --background assets/dmg-bg.png \
  --app-drop-link 450 200 \
  dist/macos/QuietPatch-v0.4.0.dmg dist/macos/
cp dist/macos/QuietPatch-v0.4.0.dmg release/
