import json
from pathlib import Path

META = Path("data/db/cve_meta.json")
d = json.loads(META.read_text())


def sev_from_score(s):
    try:
        s = float(s)
    except Exception:
        return "unknown"
    if s == 0:
        return "none"
    if s >= 9.0:
        return "critical"
    if s >= 7.0:
        return "high"
    if s >= 4.0:
        return "medium"
    return "low"


changed = 0
for _cve, m in d.items():
    sev = (m.get("severity") or "").lower()
    if sev not in ("critical", "high", "medium", "low", "none"):
        sc = m.get("cvss")
        if sc is not None:
            m["severity"] = sev_from_score(sc)
            changed += 1

META.write_text(json.dumps(d))
print("updated", changed, "CVE severities")
