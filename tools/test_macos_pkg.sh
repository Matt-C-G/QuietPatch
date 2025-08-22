#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Testing macOS package installation..."

# Check if package exists
if [ ! -f "packaging/macos/quietpatch-0.2.1.pkg" ]; then
    echo "❌ Package not found. Build it first with:"
    echo "   cd packaging/macos && ./mkpkg.sh 0.2.1"
    exit 1
fi

echo "📦 Package found: $(ls -lh packaging/macos/quietpatch-0.2.1.pkg)"

# Check package contents
echo "🔍 Package contents:"
pkgutil --expand packaging/macos/quietpatch-0.2.1.pkg /tmp/quietpatch-expand
find /tmp/quietpatch-expand -type f | head -20

# Test installation (dry run first)
echo "📋 Installation dry run:"
installer -pkg packaging/macos/quietpatch-0.2.1.pkg -target / -pkginfo

echo ""
echo "✅ Package test completed successfully!"
echo ""
echo "To install for real:"
echo "  sudo installer -pkg packaging/macos/quietpatch-0.2.1.pkg -target /"
echo ""
echo "To test the service:"
echo "  sudo launchctl kickstart -k system/com.quietpatch.agent"
echo "  sudo tail -f /var/log/quietpatch.out /var/log/quietpatch.err"
