#!/usr/bin/env bash
set -euo pipefail

OWNER="Matt-C-G"
DIST="quietpatch-dist"
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS:$ARCH" in
  Darwin:arm64)   ASSET="quietpatch-macos-arm64-latest.zip" ;;
  Linux:x86_64)   ASSET="quietpatch-linux-x86_64-latest.zip" ;;
  *) echo "Unsupported platform: $OS $ARCH"; exit 1 ;;
esac

TMP="${TMPDIR:-/tmp}/qp.$$"
mkdir -p "$TMP"
DEST="$HOME/.quietpatch/bin"
mkdir -p "$DEST"

URL="https://github.com/${OWNER}/${DIST}/releases/latest/download/${ASSET}"
echo "Downloading ${ASSET} …"
if ! curl -fsSL "$URL" -o "$TMP/pkg.zip"; then
  echo "Public download failed. Trying authenticated fallback with 'gh'…"
  if command -v gh >/dev/null; then
    gh release download -R "${OWNER}/${DIST}" -p "${ASSET}" -D "$TMP"
    mv "$TMP/${ASSET}" "$TMP/pkg.zip"
  else
    echo "Error: cannot download asset. Install GitHub CLI or make repo public."
    exit 1
  fi
fi

unzip -q "$TMP/pkg.zip" -d "$DEST"
chmod +x "$DEST"/* || true
echo "Installed to $DEST"

if ! command -v quietpatch >/dev/null 2>&1; then
  echo "Add to PATH: export PATH=\"$HOME/.quietpatch/bin:\$PATH\""
fi

"$DEST"/run_quietpatch.sh --version 2>/dev/null || "$DEST"/run_quietpatch.command --version 2>/dev/null || true
echo "Done."
