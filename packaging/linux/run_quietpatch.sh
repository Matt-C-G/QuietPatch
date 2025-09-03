#!/usr/bin/env bash
set -euo pipefail
export PEX_ROOT="${XDG_CACHE_HOME:-$HOME/.cache}/quietpatch/.pexroot"
exec python3 "$(dirname "$0")/quietpatch-linux-x86_64.pex" "$@"
