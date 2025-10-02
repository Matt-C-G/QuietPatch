#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
manifest="$DIR/manifest.json"
logdir=$(/usr/bin/python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); print(m["logging"]["dir_posix"])
PY
"$manifest")
mkdir -p "$logdir"; exec > >(tee -a "$logdir/rollback_$(date +%Y%m%d_%H%M%S).log") 2>&1

artifact=$(python3 - <<'PY'
import json,sys,os; m=json.load(open(sys.argv[1])); 
t=[x for x in m["targets"] if x["os"]=="macos"][0]; print(os.path.join(os.path.dirname(sys.argv[1]), t["rollback_artifact"]))
PY
"$manifest")

# Verify rollback artifact integrity if SHA256 provided
expect_hash=$(python3 - <<'PY'
import json,sys; m=json.load(open(sys.argv[1])); 
t=[x for x in m["targets"] if x["os"]=="macos"][0]; print(t["sha256"]["rollback_artifact"])
PY
"$manifest")

if [ "$expect_hash" != "<FILL_AT_BUILD>" ] && [ -n "$expect_hash" ]; then
  calc_hash=$(shasum -a 256 "$artifact" | awk '{print tolower($1)}')
  if [ "$calc_hash" != "$(echo "$expect_hash" | tr 'A-Z' 'a-z')" ]; then
    echo "SHA256 mismatch for rollback artifact $artifact. Expected: $expect_hash, Got: $calc_hash"
    exit 3
  fi
fi

echo "Rollback with $artifact"
sudo /usr/sbin/installer -pkg "$artifact" -target /
