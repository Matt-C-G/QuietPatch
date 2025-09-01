#!/usr/bin/env bash
set -euo pipefail
export PEX_ROOT="$(dirname "$0")/.pexroot"
exec /usr/bin/env python3.11 "$(dirname "$0")/quietpatch-linux-x86_64-py311.pex" "$@"
