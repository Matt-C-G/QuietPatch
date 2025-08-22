#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.2.1}"
PLATFORMS="${2:-all}"

echo "🚀 Building QuietPatch ${VERSION} for ${PLATFORMS}"

# Build the Python zipapp first
echo "📦 Building Python zipapp..."
bash tools/build_pyz.sh

# Build platform-specific packages
case "$PLATFORMS" in
    "macos"|"all")
        echo "🍎 Building macOS package..."
        cd packaging/macos
        bash mkpkg.sh "$VERSION"
        cd ../..
        echo "✅ macOS package: quietpatch-${VERSION}.pkg"
        ;;
esac

case "$PLATFORMS" in
    "windows"|"all")
        echo "🪟 Building Windows MSI..."
        echo "⚠️  Windows MSI requires WiX Toolset and EV code signing cert"
        echo "📁 WiX source: packaging/windows/Product.wxs"
        echo "📝 Post-install: packaging/windows/after_install.ps1"
        ;;
esac

case "$PLATFORMS" in
    "linux"|"all")
        echo "🐧 Building Linux packages..."
        echo "📁 Debian: packaging/deb/"
        echo "📁 systemd: packaging/systemd/quietpatch.service"
        echo "📝 Build with: dpkg-deb --build packaging/deb/ quietpatch-${VERSION}.deb"
        ;;
esac

echo ""
echo "🎯 Next steps:"
echo "1. Sign packages with your certificates"
echo "2. Test installers on target platforms"
echo "3. Upload to your distribution system"
echo "4. Update manifest.json with download URLs"
echo ""
echo "📚 Documentation: packaging/README.md"
