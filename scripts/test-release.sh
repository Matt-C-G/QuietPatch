#!/usr/bin/env bash
# Test script for QuietPatch release artifacts

set -euo pipefail

VERSION="0.4.0"
RELEASE_DIR="release-test"

echo "🧪 QuietPatch $VERSION Release Test Script"
echo "=========================================="

# Create test directory
mkdir -p "$RELEASE_DIR"
cd "$RELEASE_DIR"

echo "📥 Downloading release artifacts..."

# Download artifacts (replace with actual GitHub release URL)
REPO_URL="https://github.com/OWNER/REPO/releases/download/v$VERSION"

# Windows
echo "  • Windows installer..."
curl -L -o "QuietPatch-Setup-v$VERSION.exe" "$REPO_URL/QuietPatch-Setup-v$VERSION.exe" || echo "❌ Windows download failed"

# macOS
echo "  • macOS DMG..."
curl -L -o "QuietPatch-v$VERSION.dmg" "$REPO_URL/QuietPatch-v$VERSION.dmg" || echo "❌ macOS download failed"

# Linux
echo "  • Linux AppImage..."
curl -L -o "QuietPatch-v$VERSION-x86_64.AppImage" "$REPO_URL/QuietPatch-v$VERSION-x86_64.AppImage" || echo "❌ Linux download failed"

# Common files
echo "  • SHA256SUMS..."
curl -L -o "SHA256SUMS.txt" "$REPO_URL/SHA256SUMS.txt" || echo "❌ SHA256SUMS download failed"

echo "  • Minisign signature..."
curl -L -o "SHA256SUMS.txt.minisig" "$REPO_URL/SHA256SUMS.txt.minisig" || echo "❌ Signature download failed"

echo "  • VERIFY.md..."
curl -L -o "VERIFY.md" "$REPO_URL/VERIFY.md" || echo "❌ VERIFY.md download failed"

echo ""
echo "🔍 Verifying checksums..."

# Verify checksums
if command -v sha256sum >/dev/null 2>&1; then
    CMD=sha256sum
elif command -v shasum >/dev/null 2>&1; then
    CMD="shasum -a 256"
else
    echo "❌ No SHA256 tool found"
    exit 1
fi

echo "Running: $CMD"
$CMD *.exe *.dmg *.AppImage 2>/dev/null | while read -r hash file; do
    if grep -q "$hash" SHA256SUMS.txt 2>/dev/null; then
        echo "✅ $file"
    else
        echo "❌ $file (checksum mismatch)"
    fi
done

echo ""
echo "🔐 Verifying minisign signature..."

if command -v minisign >/dev/null 2>&1; then
    # Extract public key from VERIFY.md
    PUBKEY=$(grep -o 'RWQ[^<]*' VERIFY.md | head -1)
    if [ -n "$PUBKEY" ]; then
        if minisign -Vm SHA256SUMS.txt -P "$PUBKEY" 2>/dev/null; then
            echo "✅ Minisign signature verified"
        else
            echo "❌ Minisign signature verification failed"
        fi
    else
        echo "⚠️  Public key not found in VERIFY.md"
    fi
else
    echo "⚠️  minisign not installed, skipping signature verification"
fi

echo ""
echo "📊 Test summary:"
echo "  • Windows installer: $(ls -lh QuietPatch-Setup-v$VERSION.exe 2>/dev/null | awk '{print $5}' || echo 'Not found')"
echo "  • macOS DMG: $(ls -lh QuietPatch-v$VERSION.dmg 2>/dev/null | awk '{print $5}' || echo 'Not found')"
echo "  • Linux AppImage: $(ls -lh QuietPatch-v$VERSION-x86_64.AppImage 2>/dev/null | awk '{print $5}' || echo 'Not found')"

echo ""
echo "🧪 Manual testing required:"
echo "  1. Install and run each platform's package"
echo "  2. Test the wizard interface"
echo "  3. Run a scan and verify report generation"
echo "  4. Check that verification instructions work"

cd ..
echo "✅ Test artifacts downloaded to $RELEASE_DIR/"
