#!/usr/bin/env bash
# QA smoke test script for QuietPatch release artifacts

set -euo pipefail

echo "🧪 QuietPatch QA Smoke Test"
echo "============================"

# 1) Verify presence of artifacts
echo "📦 Checking release artifacts..."

if [ -f "release/QuietPatch-Setup-v0.4.0.exe" ]; then
    echo "✅ Windows installer found"
    ls -l release/QuietPatch-Setup-v0.4.0.exe
else
    echo "❌ Windows installer missing"
fi

if [ -f "release/QuietPatch-v0.4.0.dmg" ]; then
    echo "✅ macOS DMG found"
    ls -l release/QuietPatch-v0.4.0.dmg
else
    echo "❌ macOS DMG missing"
fi

if [ -f "release/QuietPatch-v0.4.0-x86_64.AppImage" ]; then
    echo "✅ Linux AppImage found"
    ls -l release/QuietPatch-v0.4.0-x86_64.AppImage
else
    echo "❌ Linux AppImage missing"
fi

# 2) Check sums file present and minisign signature exists
echo ""
echo "🔐 Checking verification files..."

if [ -f "release/SHA256SUMS.txt" ]; then
    echo "✅ SHA256SUMS.txt found"
    echo "   Checksums:"
    head -3 release/SHA256SUMS.txt
else
    echo "❌ SHA256SUMS.txt missing"
fi

if [ -f "release/SHA256SUMS.txt.minisig" ]; then
    echo "✅ Minisign signature found"
else
    echo "❌ Minisign signature missing"
fi

# 3) Check documentation files
echo ""
echo "📚 Checking documentation..."

if [ -f "release/VERIFY.md" ]; then
    echo "✅ VERIFY.md found"
else
    echo "❌ VERIFY.md missing"
fi

if [ -f "release/README-QuickStart.md" ]; then
    echo "✅ README-QuickStart.md found"
else
    echo "❌ README-QuickStart.md missing"
fi

if [ -f "release/LICENSE.txt" ]; then
    echo "✅ LICENSE.txt found"
else
    echo "❌ LICENSE.txt missing"
fi

# 4) Test minisign verification if available
echo ""
echo "🔍 Testing verification..."

if command -v minisign >/dev/null 2>&1; then
    if [ -f "release/SHA256SUMS.txt" ] && [ -f "release/SHA256SUMS.txt.minisig" ]; then
        echo "Testing minisign verification..."
        # Extract public key from VERIFY.md
        PUBKEY=$(grep -o 'RWQ[^<]*' release/VERIFY.md 2>/dev/null | head -1)
        if [ -n "$PUBKEY" ]; then
            if minisign -Vm release/SHA256SUMS.txt -P "$PUBKEY" 2>/dev/null; then
                echo "✅ Minisign signature verification passed"
            else
                echo "❌ Minisign signature verification failed"
            fi
        else
            echo "⚠️  Public key not found in VERIFY.md"
        fi
    else
        echo "⚠️  Cannot test minisign - files missing"
    fi
else
    echo "⚠️  minisign not installed, skipping signature verification"
fi

# 5) Check file sizes are reasonable
echo ""
echo "📏 Checking file sizes..."

for file in release/*.exe release/*.dmg release/*.AppImage; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "   $(basename "$file"): $size"
    fi
done

echo ""
echo "✅ QA smoke test complete!"
echo ""
echo "📋 Next steps:"
echo "1. Download each OS artifact from the GitHub Release (not Actions artifacts)"
echo "2. Run verification steps exactly as written in VERIFY.md"
echo "3. Test installation and first run on each platform"
echo "4. Confirm landing page buttons resolve to v0.4.0 assets (no 404)"
echo "5. Test robots.txt and sitemap.xml over HTTPS"
echo ""
echo "See RELEASE_CHECKLIST.md for detailed testing instructions"
