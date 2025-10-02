#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
want=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); 
print([x for x in m["targets"] if x["os"]=="linux"][0]["verify"]["startswith"])
PY
"$DIR/manifest.json")
cmd=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); 
print([x for x in m["targets"] if x["os"]=="linux"][0]["verify"]["cmd"])
PY
"$DIR/manifest.json")

logdir=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); print(m["logging"]["dir_posix"])
PY
"$DIR/manifest.json")
mkdir -p "$logdir"; exec > >(tee -a "$logdir/verify_$(date +%Y%m%d_%H%M%S).log") 2>&1

ver=$($cmd | head -n1 || echo "")
echo "Version $ver ; want $want"
[[ "$ver" == "$want"* ]] && exit 0 || exit 1
