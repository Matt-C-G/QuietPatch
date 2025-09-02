from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping
import json, time

def to_json(apps: Iterable[Mapping[str, Any]], policy: Mapping[str, Any], meta: Mapping[str, Any] | None = None) -> str:
    """
    Produce a stable, machine-readable JSON.
    Expected 'apps' items shape:
      { name, version, vendor?, cves: [ {id, severity, cvss?, epss?, kev?, summary?, action? } ] }
    """
    ts = int(time.time())
    doc = {
        "schema": "quietpatch.report/v1",
        "generated_at_utc": ts,
        "policy": policy or {},
        "meta": meta or {},
        "summary": _summarize(apps),
        "apps": _normalize_apps(apps),
    }
    return json.dumps(doc, sort_keys=True, separators=(",", ":"))

def _summarize(apps: Iterable[Mapping[str, Any]]) -> Dict[str, int]:
    counts = {"apps":0,"vuln_apps":0,"critical":0,"high":0,"medium":0,"low":0,"kev":0,"unknown":0}
    for app in apps or []:
        counts["apps"] += 1
        cves = app.get("cves") or []
        if cves:
            counts["vuln_apps"] += 1
        for c in cves:
            sev = (c.get("severity") or "").lower()
            if sev not in ("critical","high","medium","low"):
                sev = "unknown"
            counts[sev] += 1
            if c.get("kev") is True or c.get("is_kev") is True:
                counts["kev"] += 1
    return counts

def _normalize_apps(apps: Iterable[Mapping[str, Any]]) -> list[dict]:
    out = []
    for a in apps or []:
        row = {
            "name": a.get("name") or a.get("app") or a.get("app_name"),
            "version": a.get("version"),
            "vendor": a.get("vendor"),
            "cves": [],
        }
        # Support both 'cves' and 'vulnerabilities' keys
        vulns = a.get("cves")
        if not vulns:
            vulns = a.get("vulnerabilities") or []
        for c in vulns or []:
            row["cves"].append({
                "id": c.get("id") or c.get("cve_id"),
                "severity": (c.get("severity") or "low").lower(),
                "cvss": c.get("cvss"),
                "epss": c.get("epss"),
                "kev": bool(c.get("kev") or c.get("is_kev")),
                "summary": c.get("summary"),
                "action": c.get("action") or c.get("actions"),
            })
        out.append(row)
    return out
