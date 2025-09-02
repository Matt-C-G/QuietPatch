#!/usr/bin/env bash
set -euo pipefail

OWNER="Matt-C-G"
REPO="QuietPatch"
PREFIX="${QUIETPATCH_PREFIX:-$HOME/.quietpatch}"
BIN_DIR="$PREFIX/bin"
DB_NAME="db-latest.tar.zst"

# Detect platform
os="$(uname -s)"
arch="$(uname -m)"
case "$os" in
  Darwin) asset="quietpatch-macos-arm64.zip"; ;;
  Linux)  asset="quietpatch-linux-x86_64.zip"; ;;
  *) echo "Unsupported OS: $os" >&2; exit 1;;
esac

mkdir -p "$BIN_DIR"
cd "$BIN_DIR"

echo "→ Downloading latest $asset..."
curl -fsSL -O "https://github.com/$OWNER/$REPO/releases/latest/download/$asset"

echo "→ Verifying checksum..."
curl -fsSL -o SHA256SUMS "https://github.com/$OWNER/$REPO/releases/latest/download/SHA256SUMS"
if command -v sha256sum >/dev/null 2>&1; then
  grep " $asset$" SHA256SUMS | sha256sum -c -
else
  grep " $asset$" SHA256SUMS | shasum -a 256 -c -
fi

echo "→ Extracting…"
unzip -q -o "$asset"

echo "→ Fetching offline DB snapshot ($DB_NAME)…"
curl -fsSL -O "https://github.com/$OWNER/$REPO/releases/latest/download/$DB_NAME"
# optional: verify DB too
if grep -q "$DB_NAME" SHA256SUMS; then
  if command -v sha256sum >/dev/null 2>&1; then
    grep " $DB_NAME$" SHA256SUMS | sha256sum -c -
  else
    grep " $DB_NAME$" SHA256SUMS | shasum -a 256 -c -
  fi
fi

# Create PATH shim
cat > quietpatch <<'SH'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PEX_ROOT="${XDG_CACHE_HOME:-$HOME/.cache}/quietpatch/.pexroot"
if command -v python3.11 >/dev/null 2>&1; then PY=python3.11; else PY=python3; fi
if [[ "$OSTYPE" == darwin* ]]; then
  PEX="$ROOT/quietpatch-macos-arm64-py311.pex"
else
  PEX="$ROOT/quietpatch-linux-x86_64-py311.pex"
fi
exec "$PY" "$PEX" "$@"
SH
chmod +x quietpatch

# Try to symlink into /usr/local/bin if writable
if [ -w /usr/local/bin ]; then
  ln -sf "$BIN_DIR/quietpatch" /usr/local/bin/quietpatch
  echo "✓ Installed: /usr/local/bin/quietpatch"
else
  echo "Add to PATH: export PATH=\"$BIN_DIR:\$PATH\""
fi

echo "Done. Try: quietpatch scan --db \"$BIN_DIR/$DB_NAME\" --also-report --open"
