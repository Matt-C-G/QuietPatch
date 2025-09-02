#!/usr/bin/env bash
set -euo pipefail
export PEX_ROOT="$(dirname "$0")/.pexroot"
exec /usr/bin/env python3 "$(dirname "$0")/quietpatch-macos-arm64-py311.pex" "$@"
