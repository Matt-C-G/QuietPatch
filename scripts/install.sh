#!/usr/bin/env bash
set -euo pipefail

# 0) Require Python ≥3.11 (Homebrew/pyenv/system)—pick best available
pick_py() {
  for c in python3.12 python3.11 python3; do
    if command -v "$c" >/dev/null 2>&1; then
      ver=$($c -c 'import sys;print(".".join(map(str,sys.version_info[:3])))')
      pyok=$($c - <<'PY'
import sys; exit(0 if (sys.version_info[:2] >= (3,11)) else 1)
PY
) && echo "$c" && return 0 || true
    fi
  done
  echo "ERROR: Python ≥3.11 not found. Install via Homebrew: brew install python@3.12" >&2
  exit 1
}
PYBIN=$(pick_py)

# 1) Ensure pipx (isolated install)
if ! command -v pipx >/dev/null 2>&1; then
  $PYBIN -m pip install --user pipx
  $PYBIN -m pipx ensurepath
  export PATH="$HOME/.local/bin:$PATH"
fi

# 2) Install/upgrade QuietPatch from release
PKG="quietpatch"
pipx install --force "quietpatch==${QUIETPATCH_VERSION:-0.3.0}"

# 3) Fetch offline DB (accept latest or dated)
QP_HOME="${QUIETPATCH_HOME:-$HOME/.quietpatch}"
mkdir -p "$QP_HOME/db"
DB_BASE="https://github.com/Matt-C-G/QuietPatch/releases/download/${QUIETPATCH_DB_TAG:-db}"
DBFILE="${QUIETPATCH_DB_FILE:-qp_db-latest.tar.zst}"
curl -fsSL "$DB_BASE/$DBFILE" -o "$QP_HOME/db/$DBFILE"

# 4) Extract (supports .zst or .gz)
cd "$QP_HOME/db"
case "$DBFILE" in
  *.zst) command -v zstd >/dev/null 2>&1 || { echo "Installing zstd via Homebrew..."; brew install zstd >/dev/null || true; }
         zstd -d -f "$DBFILE" ;;
  *.gz)  gunzip -f "$DBFILE" ;;
  *)     echo "Unknown db extension: $DBFILE" >&2; exit 1 ;;
esac

echo "✅ QuietPatch installed. Run: quietpatch scan --offline"

