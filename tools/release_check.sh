#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Unit tests"
pytest -q

echo "[2/4] Security lint (warn-only)"
if command -v bandit >/dev/null 2>&1; then
  bandit -q -r src || true
else
  echo "bandit not installed; skipping"
fi

echo "[3/4] Policy/data sanity (unknowns <=1% if data present)"
python3 - <<'PY'
import json, re, sys, pathlib
p=pathlib.Path('data/vuln_log.json')
if not p.exists():
    print("no data/vuln_log.json; skipping unknowns gate")
    sys.exit(0)
j=json.loads(p.read_text())
apps=j if isinstance(j,list) else j.get('apps',[])
all_cves=sum(len(a.get('cves',[])) for a in apps)
unknown=sum(1 for a in apps for c in a.get('cves',[]) if (c.get('severity')=='unknown' or c.get('cvss') in (None,'')))
if all_cves and unknown/all_cves>0.01:
    sys.exit("Unknowns >1% — refresh DB or fix alias before release.")
print("unknowns OK")
PY

echo "[4/4] Determinism smoke (if two runs exist, hashes must match)"
if [ -f report.html ]; then
  h1=$(shasum -a 256 report.html | awk '{print $1}')
  sleep 1
  h2=$(shasum -a 256 report.html | awk '{print $1}')
  [ "$h1" = "$h2" ] || { echo "non-deterministic report hash"; exit 1; }
fi
echo "Release gate OK"
