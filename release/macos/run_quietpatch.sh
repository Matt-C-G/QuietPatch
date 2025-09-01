#!/bin/bash
# QuietPatch wrapper script
# This ensures we use the correct Python version and handle arguments properly

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PEX_PATH="$SCRIPT_DIR/quietpatch.pex"

if [ ! -f "$PEX_PATH" ]; then
    echo "Error: quietpatch.pex not found at $PEX_PATH"
    exit 1
fi

# Handle --once flag for manual runs
if [[ "$*" == *"--once"* ]]; then
    # Manual run - scan to specified output
    exec "$PEX_PATH" scan -o /var/lib/quietpatch "$@"
else
    # Service run - use default arguments
    exec "$PEX_PATH" "$@"
fi


