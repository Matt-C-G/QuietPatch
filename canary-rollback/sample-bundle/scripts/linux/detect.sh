#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
manifest="$DIR/manifest.json"
logdir=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); print(m["logging"]["dir_posix"])
PY
"$manifest")
mkdir -p "$logdir"; exec > >(tee -a "$logdir/detect_$(date +%Y%m%d_%H%M%S).log") 2>&1

want=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); 
print([x for x in m["targets"] if x["os"]=="linux"][0]["verify"]["startswith"])
PY
"$manifest")

cmd=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); 
print([x for x in m["targets"] if x["os"]=="linux"][0]["verify"]["cmd"])
PY
"$manifest")

if ! command -v $(echo "$cmd" | awk '{print $1}') >/dev/null 2>&1; then
  echo "Command not found: $(echo "$cmd" | awk '{print $1}')"; exit 2
fi

ver=$($cmd | head -n1)
echo "Detected $ver ; want prefix $want"
[[ "$ver" == "$want"* ]] && exit 0 || exit 1
