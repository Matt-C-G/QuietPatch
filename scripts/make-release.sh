#!/usr/bin/env bash
set -euo pipefail
VERSION="$1"

rm -rf dist release && mkdir -p dist release

# 1. Build PyInstaller binaries
pyinstaller build/quietpatch_wizard.spec
pyinstaller build/quietpatch_cli.spec

# 2. Package per OS (run on respective OS builders)
# Windows: use Inno Setup to produce QuietPatch-Setup-$VERSION.exe
# macOS: create-dmg for QuietPatch-$VERSION.dmg
# Linux: appimagetool for QuietPatch-$VERSION-x86_64.AppImage

# Copy artifacts into release/
cp Output/QuietPatch-Setup-$VERSION.exe release/ || true
cp dist/macos/QuietPatch-$VERSION.dmg release/ || true
cp QuietPatch-$VERSION-x86_64.AppImage release/ || true
cp dist/*.zip dist/*.tar.gz release/ || true

# 3. Generate checksums
cd release
sha256sum * > SHA256SUMS.txt

# 4. Sign with minisign (requires MINISIGN_SECRET_KEY in env)
echo "$MINISIGN_SECRET_KEY" > ../minisign.key
chmod 600 ../minisign.key
minisign -Sm SHA256SUMS.txt -s ../minisign.key

# 5. Copy VERIFY.md, LICENSE.txt, README-QuickStart.md
cp ../VERIFY.md .
cp ../LICENSE.txt .
cp ../README-QuickStart.md .

cd ..
echo "Release artifacts ready in release/"
