#!/usr/bin/env python3
# tools/selfcheck.py  (run via: PYTHONPATH=. python3 tools/selfcheck.py)
import json, pathlib, re, sys

ok=lambda m: print("OK:",m)
bad=lambda m: (print("FAIL:",m), sys.exit(1))

p=pathlib.Path("data/vuln_log.json")
if not p.exists(): bad("missing data/vuln_log.json (did you run scan?)")

apps=json.loads(p.read_text())
if not isinstance(apps,list) or not apps: bad("apps list empty")

must={"app","version","vulnerabilities"}
for a in apps:
  if not must.issubset(a.keys()): bad(f"missing keys in {a.get('app')}")

ok("structure/integrity")

# Check for actual CVEs (not just API errors)
with_cves=sum(1 for a in apps if any('cve_id' in v for v in a.get('vulnerabilities', []) if isinstance(v, dict)))
if with_cves==0: bad("no CVEs resolved")

ok(f"coverage: {with_cves}/{len(apps)} apps with CVEs")

# Check severity (from vulnerabilities)
sevpos=sum(1 for a in apps if any(v.get('severity') in ['critical', 'high', 'medium', 'low'] for v in a.get('vulnerabilities', []) if isinstance(v, dict)))
if sevpos==0: bad("no app has severity>0 after policy")

ok(f"risk: {sevpos} apps have severity>0")
print("PASS")
