from __future__ import annotations
from typing import Iterable, Mapping, Any
import csv, json, time

_LEVEL = {"critical":"error", "high":"error", "medium":"warning", "low":"note", "unknown":"note", "none":"note"}


def _iter_vulns(app: Mapping[str, Any]):
	vulns = app.get("vulnerabilities") or app.get("cves") or []
	for v in vulns:
		# normalize keys across shapes
		yield {
			"id": v.get("cve_id") or v.get("id") or "",
			"severity": (v.get("severity") or "unknown").lower(),
			"cvss": v.get("cvss"),
			"epss": v.get("epss_score") or v.get("epss"),
			"kev": bool(v.get("is_kev") or v.get("kev")),
			"summary": v.get("summary") or v.get("desc") or "",
			"action": (v.get("action") or ""),
		}


def write_csv(apps: Iterable[Mapping[str, Any]], path: str) -> None:
	fields = ["app","version","cve","severity","cvss","epss","kev","summary","action"]
	with open(path, "w", newline="", encoding="utf-8") as f:
		w = csv.DictWriter(f, fieldnames=fields)
		w.writeheader()
		for a in apps or []:
			name = a.get("app") or a.get("name")
			ver = a.get("version") or ""
			for c in _iter_vulns(a):
				w.writerow({
					"app": name,
					"version": ver,
					"cve": c.get("id"),
					"severity": c.get("severity"),
					"cvss": c.get("cvss"),
					"epss": c.get("epss"),
					"kev": c.get("kev"),
					"summary": c.get("summary"),
					"action": c.get("action"),
				})


def write_sarif(apps: Iterable[Mapping[str, Any]], path: str, tool_name: str = "QuietPatch", tool_version: str | None = None) -> None:
	now = int(time.time())
	rules: dict[str, Any] = {}
	results: list[dict[str, Any]] = []
	for a in apps or []:
		name = a.get("app") or a.get("name") or "app"
		ver = a.get("version") or ""
		for c in _iter_vulns(a):
			sid = (c.get("id") or "").upper() or "UNKNOWN"
			sev = c.get("severity") or "unknown"
			level = _LEVEL.get(sev, "note")
			if sid not in rules:
				rules[sid] = {
					"id": sid,
					"shortDescription": {"text": sid},
					"fullDescription": {"text": c.get("summary") or sid},
					"defaultConfiguration": {"level": level},
					"properties": {"tags": ["cve", f"severity:{sev}"]},
				}
			results.append({
				"ruleId": sid,
				"level": level,
				"message": {"text": f"{name} {ver} vulnerable to {sid} ({sev})"},
				"locations": [{
					"physicalLocation": {"artifactLocation": {"uri": name or "host"}},
				}],
				"properties": {
					"cvss": c.get("cvss"),
					"epss": c.get("epss"),
					"kev": c.get("kev"),
					"action": c.get("action"),
				},
			})
	sarif = {
		"version": "2.1.0",
		"$schema": "https://json.schemastore.org/sarif-2.1.0.json",
		"runs": [{
			"tool": {"driver": {"name": tool_name, "version": tool_version or "", "rules": list(rules.values())}},
			"results": results,
			"invocations": [{"executionSuccessful": True, "endTimeUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}],
		}],
	}
	with open(path, "w", encoding="utf-8") as f:
		json.dump(sarif, f, ensure_ascii=False, indent=2)