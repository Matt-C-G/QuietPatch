#!/usr/bin/env bash
set -euo pipefail

# ---- Config ----
REPO="matt-c-g/quietpatch"
API="https://api.github.com/repos/${REPO}/releases/latest"
PREFIX="${PREFIX:-$HOME/.quietpatch}"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"
WITH_DB="${WITH_DB:-1}"   # set WITH_DB=0 to skip DB download
CURL="${CURL:-curl -fsSL}"
AUTH_HEADER=()
if [ -n "${GH_TOKEN:-}" ]; then
  AUTH_HEADER=( -H "Authorization: Bearer ${GH_TOKEN}" )
fi

mkdir -p "$PREFIX" "$BIN_DIR"

# ---- Helpers ----
have() { command -v "$1" >/dev/null 2>&1; }
fatal() { echo "ERROR: $*" >&2; exit 1; }
note()  { echo "==> $*" >&2; }

require() {
  for x in "$@"; do have "$x" || fatal "Missing dependency: $x"
  done
}

json_get() {
  # Prefer jq; fallback to Python, then Node, then awk (last-resort).
  if have jq; then
    jq -r "$1"
  elif have python3; then
    python3 - "$1" <<'PY'
import json,sys
expr=sys.argv[1]
data=json.load(sys.stdin)
# tiny jq-ish: only supports top-level .assets filtering we use
if expr=='.assets[].browser_download_url':
    for a in data.get('assets',[]): print(a.get('browser_download_url',''))
else:
    import re
    m=re.search(r'\.assets\[\]\s*\|\s*select\(\.name\s*\|\s*test\("(.+)"\)\)\s*\|\s*\.browser_download_url',expr)
    pat=m.group(1) if m else None
    for a in data.get('assets',[]):
        if pat and __import__('re').search(pat,a.get('name',''),__import__('re').I):
            print(a.get('browser_download_url',''))
PY
  elif have node; then
    node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{const j=JSON.parse(d);(j.assets||[]).forEach(a=>console.log(a.browser_download_url||''))})"
  else
    # crude: print all browser_download_url lines
    grep -oE '"browser_download_url":\s*"[^"]+"' | sed -E 's/.*"\s*:\s*"([^"]+)".*/\1/'
  fi
}

# ---- Detect platform ----
OS="$(uname -s)"
ARCH="$(uname -m)"
case "$OS" in
  Darwin)  os_tag="macos";;
  Linux)   os_tag="linux";;
  *) fatal "Unsupported OS: $OS";;
esac

case "$ARCH" in
  arm64|aarch64) arch_tag="arm64";;
  x86_64|amd64)  arch_tag="x86_64|amd64";;
  *) fatal "Unsupported arch: $ARCH";;
esac

PATTERN="${os_tag}.+(${arch_tag})"
note "Platform: ${OS}/${ARCH} → pattern: ${PATTERN}"

# ---- Query latest release ----
note "Fetching latest release metadata…"
REL_JSON="$(${CURL} "${AUTH_HEADER[@]}" "${API}")" || fatal "GitHub API failed (releases/latest)"
if printf '%s' "$REL_JSON" | grep -qi "rate limit"; then
  fatal "GitHub API rate-limited. Set GH_TOKEN to increase limits."
fi
ASSET_URL="$(
  printf '%s' "$REL_JSON" | json_get ".assets[] | select(.name | test(\"${PATTERN}\"; \"i\")) | .browser_download_url" | head -n1
)"

[ -n "${ASSET_URL}" ] || fatal "No asset matched pattern: ${PATTERN}"

# Try to pick SHA256SUMS too (optional)
SUMS_URL="$(printf '%s' "$REL_JSON" | json_get '.assets[] | select(.name | test("SHA256SUMS")) | .browser_download_url' | head -n1 || true)"

# Latest DB snapshot (optional)
if [ "${WITH_DB}" = "1" ]; then
  DB_URL="$(printf '%s' "$REL_JSON" | json_get '.assets[] | select(.name | test("^db-.*\\.(tar\\.(zst|gz))$";"i")) | .browser_download_url' | head -n1 || true)"
else
  DB_URL=""
fi

note "Asset: $ASSET_URL"
[ -n "$SUMS_URL" ] && note "Checksums: $SUMS_URL"
[ -n "$DB_URL" ]   && note "DB: $DB_URL"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

cd "$tmp"
note "Downloading asset…"
$CURL "${AUTH_HEADER[@]}" -o asset "$ASSET_URL"

# Optional checksums
if [ -n "$SUMS_URL" ] && (have shasum || have sha256sum); then
  $CURL "${AUTH_HEADER[@]}" -o SHA256SUMS "$SUMS_URL"
  if have shasum; then
    note "Verifying checksum with shasum…"
    grep -F "$(basename "$ASSET_URL")" SHA256SUMS > SUM
    shasum -a 256 -c SUM
  else
    note "Verifying checksum with sha256sum…"
    grep -F "$(basename "$ASSET_URL")" SHA256SUMS > SUM
    sha256sum -c SUM
  fi
else
  note "Skipping checksum verification (tool or SUMS not available)."
fi

# Extract / install
mkdir -p "$PREFIX"/current
case "$ASSET_URL" in
  *.zip)
    require unzip
    unzip -q asset -d "$PREFIX/current"
    ;;
  *.tar.gz|*.tgz)
    require tar
    tar -xzf asset -C "$PREFIX/current"
    ;;
  *.tar.zst)
    require tar unzstd
    unzstd -c asset | tar -x -C "$PREFIX/current"
    ;;
  *.pex)
    install -m 0755 asset "$PREFIX/current/quietpatch.pex"
    ;;
  *)
    # fallback: just drop whatever it is
    install -m 0644 asset "$PREFIX/current/$(basename "$ASSET_URL")"
    ;;
esac

# Create shim (bin/quietpatch)
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/quietpatch" <<"SH"
#!/usr/bin/env bash
set -euo pipefail
SELF="${0}"
# prefer wrapper scripts if present, else pex
ROOT="${HOME}/.quietpatch/current"
export PEX_ROOT="${HOME}/.quietpatch/.pexroot"
if [ -x "${ROOT}/run_quietpatch.sh" ]; then
  exec "${ROOT}/run_quietpatch.sh" "$@"
elif [ -x "${ROOT}/quietpatch-macos"*".pex" ] || [ -x "${ROOT}/quietpatch-linux"*".pex" ] || [ -f "${ROOT}/quietpatch.pex" ]; then
  PY="${PYTHON:-$(command -v python3.11 || command -v python3 || command -v python)}"
  [ -n "$PY" ] || { echo "Python not found. Install Python 3.11+."; exit 86; }
  PEX="$(ls "${ROOT}"/quietpatch*.pex 2>/dev/null | head -n1)"
  exec "$PY" "$PEX" "$@"
elif [ -x "${ROOT}/quietpatch" ]; then
  exec "${ROOT}/quietpatch" "$@"
else
  echo "QuietPatch runtime not found in ${ROOT}" >&2
  exit 1
fi
SH
chmod +x "$BIN_DIR/quietpatch"

# Optional DB snapshot download
if [ -n "$DB_URL" ]; then
  mkdir -p "$PREFIX/db"
  note "Downloading offline DB…"
  $CURL "${AUTH_HEADER[@]}" -o "$PREFIX/db/$(basename "$DB_URL")" "$DB_URL"
fi

# PATH notice
if ! printf "%s" "$PATH" | tr ':' '\n' | grep -Fxq "$BIN_DIR"; then
  echo
  echo "Add to PATH (shell rc), e.g.:"
  echo "  export PATH=\"$BIN_DIR:\$PATH\""
fi

echo
echo "✅ Installed. Try:"
echo "  quietpatch scan --also-report --open"
[ -n "$DB_URL" ] && echo "  (offline DB at $PREFIX/db/$(basename "$DB_URL"))"
