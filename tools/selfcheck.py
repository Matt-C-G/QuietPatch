#!/usr/bin/env python3
import os
import tempfile

os.environ.setdefault("PEX_VENV", "1")
os.environ.setdefault("PEX_FORCE_LOCAL", "1")
if "PEX_ROOT" not in os.environ:
    os.environ["PEX_ROOT"] = tempfile.mkdtemp(prefix="qp-pex-")
# tools/selfcheck.py  (run via: PYTHONPATH=. python3 tools/selfcheck.py)
import json
import pathlib
import sys


def ok(m):
    print("OK:", m)


def bad(m):
    print("FAIL:", m)
    sys.exit(1)

p = pathlib.Path("data/vuln_log.json")
if not p.exists():
    bad("missing data/vuln_log.json (did you run scan?)")

apps = json.loads(p.read_text())
if not isinstance(apps, list) or not apps:
    bad("apps list empty")

must = {"app", "version", "vulnerabilities"}
for a in apps:
    if not must.issubset(a.keys()):
        bad(f"missing keys in {a.get('app')}")

ok("structure/integrity")

# Check for actual CVEs (not just API errors or notes)
with_cves = sum(
    1
    for a in apps
    if any("cve_id" in v for v in a.get("vulnerabilities", []) if isinstance(v, dict))
)
if with_cves == 0:
    bad("no CVEs resolved")

ok(f"coverage: {with_cves}/{len(apps)} apps with CVEs")

# Check severity (from vulnerabilities)
sevpos = sum(
    1
    for a in apps
    if any(
        v.get("severity") in ["critical", "high", "medium", "low"]
        for v in a.get("vulnerabilities", [])
        if isinstance(v, dict)
    )
)
if sevpos == 0:
    bad("no app has severity>0 after policy")

ok(f"risk: {sevpos} apps have severity>0")

# Check for local database usage
local_db_usage = sum(
    1
    for a in apps
    if any(
        v.get("source") == "local_db" for v in a.get("vulnerabilities", []) if isinstance(v, dict)
    )
)
if local_db_usage > 0:
    ok(f"local database: {local_db_usage} CVEs from local DB")
else:
    print("Note: No CVEs from local database (may need to refresh DB)")
print("PASS")
