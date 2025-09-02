#!/usr/bin/env bash
set -euo pipefail

PREFIX="${QUIETPATCH_PREFIX:-$HOME/.quietpatch}"
BIN_DIR="$PREFIX/bin"

echo "🗑️  Uninstalling QuietPatch..."

# Check if installation exists
if [ ! -d "$BIN_DIR" ]; then
    echo "❌ QuietPatch installation not found at $BIN_DIR"
    echo "   Nothing to uninstall."
    exit 0
fi

echo "→ Removing QuietPatch from $BIN_DIR"
rm -rf "$BIN_DIR"

# Remove symlink if present
if [ -L /usr/local/bin/quietpatch ]; then
    sudo rm -f /usr/local/bin/quietpatch
    echo "✓ Removed symlink /usr/local/bin/quietpatch"
fi

# Cache cleanup
CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/quietpatch"
if [ -d "$CACHE" ]; then
    rm -rf "$CACHE"
    echo "✓ Removed cache $CACHE"
fi

# Remove the parent directory if it's empty
if [ -d "$PREFIX" ] && [ -z "$(ls -A "$PREFIX" 2>/dev/null)" ]; then
    rmdir "$PREFIX"
    echo "✓ Removed empty parent directory: $PREFIX"
fi

echo "✓ QuietPatch uninstalled"
