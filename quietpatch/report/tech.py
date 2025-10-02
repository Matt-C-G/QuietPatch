from __future__ import annotations
from typing import Dict, Any, List
import copy
from .util import read_json, deterministic_now_iso, sorted_by_keys, ensure_dir, pct, kpi_exposure_index, sha256_file
from .html import jinja_env, render_template, compute_html_hash
from .pdf import html_to_pdf
from . import charts

def _aggregate(scan: Dict[str,Any]) -> Dict[str,int]:
    sev = {"critical":0,"high":0,"medium":0,"low":0}
    for a in scan.get("assets", []):
        for v in a.get("vulns", []):
            s = v.get("severity", "").lower()
            if s in sev:
                sev[s]+=1
    return sev

def _diff(current: Dict[str,Any], prev: Dict[str,Any]) -> Dict[str,int]:
    cur = {(a["asset_id"], v["cve"]) for a in current.get("assets",[]) for v in a.get("vulns",[])}
    prv = {(a["asset_id"], v["cve"]) for a in prev.get("assets",[]) for v in a.get("vulns",[])}
    added = len(cur - prv)
    removed = len(prv - cur)
    return {"added": added, "removed": removed, "net": added-removed}

def _heat_by_bu(scan: Dict[str,Any]) -> Dict[str,Dict[str,int]]:
    table = {}
    for a in scan.get("assets",[]):
        bu = a.get("bu","(unassigned)")
        table.setdefault(bu, {})
        for v in a.get("vulns",[]):
            s = v.get("severity","").lower()
            table[bu][s] = table[bu].get(s,0)+1
    return table

def compute_model(scan_path: str, policy_path: str|None, bundle_path: str|None, prev_scan_path: str|None) -> Dict[str,Any]:
    scan = read_json(scan_path)
    policy = read_json(policy_path) if policy_path else {"policy_version":"(none)","rules":[],"decisions":[]}
    prev = read_json(prev_scan_path) if prev_scan_path else {"assets":[]}
    sev = _aggregate(scan)
    assets_total = len(scan.get("assets",[]))
    kev_count = sum(1 for a in scan.get("assets",[]) for v in a.get("vulns",[]) if v.get("kev"))
    critical = sev.get("critical",0)
    exposure = kpi_exposure_index(sev, assets_total)

    # Deterministic asset list
    assets = copy.deepcopy(scan.get("assets",[]))
    for a in assets:
        a["vulns"] = sorted_by_keys(a.get("vulns",[]), ("severity","cve"))
    assets = sorted_by_keys(assets, ("bu","os","hostname","asset_id"))

    # Charts (SVG inline)
    sev_svg = charts.sev_bar(sev)
    heat = _heat_by_bu(scan)
    bus = sorted(heat.keys())
    cols = ["critical","high","medium","low"]
    heat_svg = charts.heatmap(heat, bus, cols, title="Findings by BU × Severity")

    bundle_sha = sha256_file(bundle_path) if bundle_path else None
    model = {
        "now": deterministic_now_iso(),
        "run": scan.get("run_id","(unknown)"),
        "catalog": scan.get("catalog",{}),
        "assets_total": assets_total,
        "vulns_by_sev": sev,
        "kev_count": kev_count,
        "exposure_idx": exposure,
        "assets": assets,
        "policy": policy,
        "diff": _diff(scan, prev),
        "bundle": {
            "path": bundle_path,
            "sha256": bundle_sha
        },
        "charts": {
            "sev_svg": sev_svg.decode("utf-8"),
            "heat_svg": heat_svg.decode("utf-8"),
        }
    }
    return model

def build_tech_report(template_dir: str, scan: str, out_html: str, policy: str|None=None, bundle: str|None=None,
                      prev_scan: str|None=None, out_pdf: str|None=None, watermark: str|None=None, approval: str|None=None, sign: bool=False, sign_key: str|None=None):
    env = jinja_env(template_dir)
    model = compute_model(scan, policy, bundle, prev_scan)
    model["watermark"] = (watermark or "").strip()
    model["approval"] = read_json(approval) if approval else None
    html = render_template(env, "tech_report.html.j2", model)
    # deterministic footer hash
    doc_hash = compute_html_hash(html)
    html = html.replace("{{__DOC_SHA256__}}", doc_hash)
    ensure_dir(out_html)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    if out_pdf:
        ensure_dir(out_pdf)
        html_to_pdf(html, out_pdf)
    
    # Optional signing
    if sign and sign_key:
        from .sign import sign_file
        sign_file(out_html, sign_key, comment="QuietPatch tech report")
        if out_pdf:
            sign_file(out_pdf, sign_key, comment="QuietPatch tech report (PDF)")
