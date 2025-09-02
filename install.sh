#!/usr/bin/env bash
set -euo pipefail

OWNER="${OWNER:-Matt-C-G}"
REPO="${REPO:-QuietPatch}"
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
API="https://api.github.com/repos/${OWNER}/${REPO}"
UA="curl/quietpatch-installer"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing $1"; exit 127; }; }
need curl
need unzip
need jq

platform="$(
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64)  echo "macos-arm64" ;;
    Linux-x86_64)  echo "linux_x86_64_legacy" ;; # see mapping below
    Linux-x86-64)  echo "linux_x86_64_legacy" ;;
    *) echo "unsupported" ;;
  esac
)"
if [ "$platform" = "unsupported" ]; then echo "Unsupported platform" >&2; exit 1; fi

# Asset names you publish
case "$platform" in
  macos-arm64)  ASSET="quietpatch-macos-arm64.zip" ;;
  linux_x86_64_legacy) ASSET="quietpatch-linux-x86_64.zip" ;;
esac

download() {
  out="$1"
  if [ -n "$TOKEN" ]; then
    rel_json="$(curl -fsSL -H "Authorization: Bearer ${TOKEN}" -H "User-Agent: ${UA}" "${API}/releases/latest")"
    id="$(printf '%s' "$rel_json" | jq -r --arg n "$ASSET" '.assets[]?|select(.name==$n)|.id')"
    [ -n "$id" ] && [ "$id" != "null" ] || { echo "Asset $ASSET not found in latest release"; exit 66; }
    curl -fL --retry 3 \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Accept: application/octet-stream" \
      -H "User-Agent: ${UA}" \
      -o "$out" \
      "${API}/releases/assets/${id}"
  else
    curl -fL --retry 3 -o "$out" \
      "https://github.com/${OWNER}/${REPO}/releases/latest/download/${ASSET}"
  fi
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Downloading ${ASSET}..."
download "${TMP}/${ASSET}"

echo "Installing..."
mkdir -p "${HOME}/.local/bin"
unzip -q "${TMP}/${ASSET}" -d "${TMP}/pkg"

# Install launcher as 'quietpatch'
if [ -f "${TMP}/pkg/run_quietpatch.sh" ]; then
  install -m 0755 "${TMP}/pkg/run_quietpatch.sh" "${HOME}/.local/bin/quietpatch"
elif [ -f "${TMP}/pkg/quietpatch" ]; then
  install -m 0755 "${TMP}/pkg/quietpatch" "${HOME}/.local/bin/quietpatch"
elif [ -f "${TMP}/pkg/run_quietpatch.command" ]; then
  install -m 0755 "${TMP}/pkg/run_quietpatch.command" "${HOME}/.local/bin/quietpatch"
else
  echo "No launcher found in package" >&2; exit 65
fi

echo "Installed to ${HOME}/.local/bin/quietpatch"
echo "Version:"
"${HOME}/.local/bin/quietpatch" --version || true
