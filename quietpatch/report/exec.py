from __future__ import annotations
from typing import Dict, Any, List
import glob, json, os
from .util import read_json, deterministic_now_iso, ensure_dir, kpi_exposure_index
from .html import jinja_env, render_template, compute_html_hash
from .pdf import html_to_pdf
from . import charts

def _trend_series(trend_dir: str, key: str) -> list[float]:
    # expects multiple scan.json files in a directory; sort by filename for determinism
    files = sorted(glob.glob(os.path.join(trend_dir, "*.json")))
    vals = []
    for p in files[-12:]:  # last 12 runs
        try:
            data = read_json(p)
            sev = {"critical":0,"high":0,"medium":0,"low":0}
            for a in data.get("assets",[]):
                for v in a.get("vulns",[]):
                    s = v.get("severity","").lower()
                    if s in sev: sev[s]+=1
            ex = kpi_exposure_index(sev, len(data.get("assets",[])))
            vals.append(ex)
        except Exception:
            vals.append(0)
    return vals or [0]

def summarize_for_exec(scan_path: str, kpi_path: str|None, trend_dir: str|None):
    scan = read_json(scan_path)
    sev = {"critical":0,"high":0,"medium":0,"low":0}
    for a in scan.get("assets",[]):
        for v in a.get("vulns",[]):
            s = v.get("severity","").lower()
            if s in sev: sev[s]+=1
    assets_total = len(scan.get("assets",[]))
    exposure = kpi_exposure_index(sev, assets_total)
    kev = sum(1 for a in scan.get("assets",[]) for v in a.get("vulns",[]) if v.get("kev"))

    # Trend sparkline
    trend_vals = _trend_series(trend_dir, "exposure") if trend_dir else [exposure]
    spark_svg = charts.sparkline(trend_vals, title="Exposure (last runs)").decode("utf-8")

    kpi = read_json(kpi_path) if kpi_path else {
        "assets_total": assets_total,
        "assets_scanned": assets_total,
        "exposure_index": exposure,
        "kev_backlog": kev,
        "sla": {"critical_7d": 0.0, "high_30d": 0.0}
    }

    return {
        "now": deterministic_now_iso(),
        "run": scan.get("run_id","(unknown)"),
        "kpi": kpi,
        "vulns_by_sev": sev,
        "spark_svg": spark_svg,
        "catalog": scan.get("catalog",{})
    }

def build_exec_report(template_dir: str, scan: str, out_pdf: str, kpi: str|None=None, trend_dir: str|None=None, out_html: str|None=None, watermark: str|None=None, approval: str|None=None, sign: bool=False, sign_key: str|None=None):
    env = jinja_env(template_dir)
    model = summarize_for_exec(scan, kpi, trend_dir)
    model["watermark"] = (watermark or "").strip()
    model["approval"] = read_json(approval) if approval else None
    html = render_template(env, "exec_report.html.j2", model)
    doc_hash = compute_html_hash(html)
    html = html.replace("{{__DOC_SHA256__}}", doc_hash)
    if out_html:
        ensure_dir(out_html)
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
    if out_pdf:
        ensure_dir(out_pdf)
        html_to_pdf(html, out_pdf)
    
    # Optional signing
    if sign and sign_key:
        from .sign import sign_file
        if out_html:
            sign_file(out_html, sign_key, comment="QuietPatch exec report (HTML)")
        sign_file(out_pdf, sign_key, comment="QuietPatch exec report (PDF)")
