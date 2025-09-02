from __future__ import annotations

from typing import Any, Iterable, Mapping
import json


def to_sarif(apps: Iterable[Mapping[str, Any]], policy: Mapping[str, Any] | None = None, meta: Mapping[str, Any] | None = None) -> str:
    """
    Build a minimal SARIF v2.1.0 document from normalized QuietPatch data.

    Expected 'apps' items shape (normalized, like jsonout._normalize_apps):
      { name, version, vendor?, cves: [ {id, severity, cvss?, epss?, kev?, summary?, action? } ] }
    """
    rules_index: dict[str, dict] = {}
    results: list[dict] = []

    for app in apps or []:
        for c in app.get("cves", []) or []:
            cve_id = c.get("id") or "UNKNOWN"
            if cve_id not in rules_index:
                rules_index[cve_id] = {
                    "id": cve_id,
                    "name": cve_id,
                    "shortDescription": {"text": c.get("summary") or cve_id},
                    "fullDescription": {"text": c.get("summary") or cve_id},
                    "defaultConfiguration": {"level": _sarif_level(c.get("severity"))},
                }
            results.append(
                {
                    "ruleId": cve_id,
                    "level": _sarif_level(c.get("severity")),
                    "message": {"text": f"{app.get('name')} {app.get('version')} vulnerable to {cve_id}"},
                    "properties": {
                        "cvss": c.get("cvss"),
                        "epss": c.get("epss"),
                        "kev": bool(c.get("kev")),
                        "vendor": app.get("vendor"),
                    },
                }
            )

    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "QuietPatch",
                        "semanticVersion": (meta or {}).get("version", ""),
                        "rules": list(rules_index.values()),
                    }
                },
                "results": results,
                "conversion": {"tool": {"driver": {"name": "quietpatch.report.sarif"}}},
                "properties": {"policy": policy or {}, **(meta or {})},
            }
        ],
    }
    return json.dumps(sarif, sort_keys=True, separators=(",", ":"))


def _sarif_level(severity: str | None) -> str:
    sev = (severity or "").lower()
    if sev in ("critical", "high"):
        return "error"
    if sev == "medium":
        return "warning"
    if sev == "low":
        return "note"
    return "none"

