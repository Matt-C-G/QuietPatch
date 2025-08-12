# cve_mapper_new.py (enhanced with allow/deny, normalization, severity sorting, CPE-first querying)
from __future__ import annotations
import os, time, json, re
import requests
from typing import List, Dict
from difflib import get_close_matches
from .scanner_new import scan_installed
from pathlib import Path
from ..config.encryptor_new import encrypt_file, decrypt_file, get_or_create_key
from ..config.config_new import load_config
from ..match.cpe_resolver import CPEResolver

def _severity_bucket(score: float|None, thresholds: dict) -> str:
    if score is None: return "unknown"
    if score >= thresholds.get("critical", 9.0): return "critical"
    if score >= thresholds.get("high", 7.5): return "high"
    if score >= thresholds.get("medium", 4.0): return "medium"
    if score >= thresholds.get("low", 0.1): return "low"
    return "none"

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def _normalize(name: str, normalize_map: Dict[str,str]) -> str:
    base = name.strip()
    nlower = base.lower()
    for k,v in normalize_map.items():
        if k.lower() in nlower:
            return v
    return base

def _matches(token_list: List[str], text: str) -> bool:
    t = text.lower()
    return any(tok.lower() in t for tok in token_list)

def query_nvd_cpe(cpe: str, api_key: str|None) -> List[Dict]:
    """Query NVD using CPE string for more accurate results"""
    params = {"cpeName": cpe}
    headers = {}
    if api_key:
        headers["apiKey"] = api_key
    
    try:
        r = requests.get(NVD_API, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("vulnerabilities", [])
    except Exception:
        return []

def query_nvd(query: str, version: str|None, api_key: str|None) -> List[Dict]:
    params = {"keywordSearch": query}
    if version:
        params["version"] = version
    headers = {}
    if api_key:
        headers["apiKey"] = api_key
    r = requests.get(NVD_API, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data.get("vulnerabilities", [])

def map_apps_to_cves(apps: List[Dict[str,str]], cfg: Dict) -> List[Dict]:
    allowlist = cfg.get("allowlist", [])
    denylist = cfg.get("denylist", [])
    normalize_map = cfg.get("normalize_map", {})
    per_app_limit = int(cfg["nvd"].get("per_app_limit", 5))
    throttle = float(cfg["nvd"].get("throttle_seconds", 1.2))
    api_key = os.environ.get(cfg["nvd"].get("api_key_env", "NVD_API_KEY"))
    thresholds = cfg.get("severity_thresholds", {})
    
    # Initialize CPE resolver
    cpe_resolver = CPEResolver()

    # Filter + normalize
    filtered=[]
    for app in apps:
        name = _normalize(app["app"], normalize_map)
        if allowlist and not _matches(allowlist, name):
            continue
        if denylist and _matches(denylist, name):
            continue
        filtered.append({"app": name, "version": app.get("version") or ""})

    results=[]
    for app in filtered:
        name = app["app"]
        ver = app.get("version") or ""
        vulns=[]
        
        try:
            # Try CPE-first querying
            cpe = cpe_resolver.resolve_best_cpe(name, ver)
            if cpe:
                records = query_nvd_cpe(cpe, api_key)
                if records:
                    # CPE query successful, process results
                    for rec in records[:per_app_limit]:
                        cve = rec.get("cve", {})
                        id_ = cve.get("id")
                        metrics = cve.get("metrics", {})
                        cvss = None
                        for k in ("cvssMetricV31","cvssMetricV30","cvssMetricV2"):
                            if k in metrics and metrics[k]:
                                cvss = metrics[k][0].get("cvssData",{}).get("baseScore")
                                break
                        desc = ""
                        for d in cve.get("descriptions",[]):
                            if d.get("lang")=="en":
                                desc = d.get("value","")
                                break
                        pub = cve.get("published")
                        bucket = _severity_bucket(cvss, thresholds)
                        vulns.append({"cve_id": id_, "cvss": cvss, "severity": bucket, "published": pub, "summary": desc})
            
            # Fallback to keyword search if CPE didn't yield results
            if not vulns:
                q = f"{name} {ver}".strip()
                records = query_nvd(q, ver, api_key)
                for rec in records[:per_app_limit]:
                    cve = rec.get("cve", {})
                    id_ = cve.get("id")
                    metrics = cve.get("metrics", {})
                    cvss = None
                    for k in ("cvssMetricV31","cvssMetricV30","cvssMetricV2"):
                        if k in metrics and metrics[k]:
                            cvss = metrics[k][0].get("cvssData",{}).get("baseScore")
                            break
                    desc = ""
                    for d in cve.get("descriptions",[]):
                        if d.get("lang")=="en":
                            desc = d.get("value","")
                            break
                    pub = cve.get("published")
                    bucket = _severity_bucket(cvss, thresholds)
                    vulns.append({"cve_id": id_, "cvss": cvss, "severity": bucket, "published": pub, "summary": desc})
                    
        except Exception as e:
            vulns.append({"error": str(e)})

        # sort by severity then cvss desc
        rank = {"critical":4, "high":3, "medium":2, "low":1, "none":0, "unknown":-1}
        vulns.sort(key=lambda v: (rank.get(v.get("severity","unknown"), -1), v.get("cvss") or -1), reverse=True)

        results.append({"app": name, "version": ver, "vulnerabilities": vulns})
        time.sleep(throttle)
    return results

def run(output_dir: str = "data") -> Dict[str,str]:
    cfg = load_config()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    apps = scan_installed()
    apps_path = Path(output_dir) / "apps.json"
    apps_path.write_text(json.dumps(apps, indent=2))
    enc_apps = Path(output_dir) / "apps.json.enc"
    encrypt_file(apps_path, enc_apps)

    mapping = map_apps_to_cves(apps, cfg)
    vuln_path = Path(output_dir) / "vuln_log.json"
    vuln_path.write_text(json.dumps(mapping, indent=2))
    enc_vuln = Path(output_dir) / "vuln_log.json.enc"
    encrypt_file(vuln_path, enc_vuln)
    return {"apps": str(enc_apps), "vulns": str(enc_vuln)}
