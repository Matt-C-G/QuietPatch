#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
manifest="$DIR/manifest.json"
logdir=$(/usr/bin/python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); print(m["logging"]["dir_posix"])
PY
"$manifest")
mkdir -p "$logdir"; exec > >(tee -a "$logdir/verify_$(date +%Y%m%d_%H%M%S).log") 2>&1

path=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); 
print([x for x in m["targets"] if x["os"]=="macos"][0]["verify"]["path"])
PY
"$manifest")
want=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); 
print([x for x in m["targets"] if x["os"]=="macos"][0]["verify"]["version"])
PY
"$manifest")

[ -d "$path" ] || { echo "Missing app: $path"; exit 2; }
ver=$(/usr/bin/defaults read "${path}/Contents/Info.plist" CFBundleShortVersionString || true)
echo "Version $ver ; expect $want"
[ "$ver" = "$want" ] && exit 0 || exit 1
