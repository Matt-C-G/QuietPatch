#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
JQ_BIN="${JQ_BIN:-/usr/bin/jq}"

manifest="$DIR/manifest.json"
logdir="$(/usr/bin/python3 - <<'PY'
import json,sys,os; m=json.load(open(sys.argv[1])); print(m["logging"]["dir_posix"])
PY
"$manifest")"
mkdir -p "$logdir"; exec > >(tee -a "$logdir/detect_$(date +%Y%m%d_%H%M%S).log") 2>&1

target=$(cat "$manifest" | "$JQ_BIN" -r '.targets[] | select(.os=="macos")')
path=$(printf "%s" "$target" | "$JQ_BIN" -r '.verify.path')
want=$(printf "%s" "$target" | "$JQ_BIN" -r '.verify.version')

if [ ! -d "$path" ]; then
  echo "App not found: $path"; exit 2
fi
ver=$(/usr/bin/defaults read "${path}/Contents/Info.plist" CFBundleShortVersionString || true)
echo "Detected $path version [$ver], want [$want]"
[ "$ver" = "$want" ] && exit 0 || exit 1
