#!/usr/bin/env bash
set -euo pipefail

OWNER="Matt-C-G"
REPO="QuietPatch"
PREFIX="${QUIETPATCH_PREFIX:-$HOME/.quietpatch}"
BIN_DIR="$PREFIX/bin"

echo "🗑️  Uninstalling QuietPatch..."

# Check if installation exists
if [ ! -d "$BIN_DIR" ]; then
    echo "❌ QuietPatch installation not found at $BIN_DIR"
    echo "   Nothing to uninstall."
    exit 0
fi

# Remove symlink from /usr/local/bin if it exists
if [ -L "/usr/local/bin/quietpatch" ]; then
    echo "→ Removing symlink from /usr/local/bin/quietpatch"
    rm -f "/usr/local/bin/quietpatch"
fi

# Remove the installation directory
echo "→ Removing installation directory: $BIN_DIR"
rm -rf "$BIN_DIR"

# Remove cache directory
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/quietpatch"
if [ -d "$CACHE_DIR" ]; then
    echo "→ Removing cache directory: $CACHE_DIR"
    rm -rf "$CACHE_DIR"
fi

# Remove the parent directory if it's empty
if [ -d "$PREFIX" ] && [ -z "$(ls -A "$PREFIX" 2>/dev/null)" ]; then
    echo "→ Removing empty parent directory: $PREFIX"
    rmdir "$PREFIX"
fi

echo ""
echo "✓ QuietPatch uninstalled successfully!"
echo ""
echo "Note: You may need to restart your terminal or run 'hash -r' to clear command cache."
