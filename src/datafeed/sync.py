from __future__ import annotations

import gzip
import io
import json
import time
from pathlib import Path

import requests

DB_DIR = Path("data/db")
DB_DIR.mkdir(parents=True, exist_ok=True)
CPE_TO_CVES = DB_DIR / "cpe_to_cves.json"
CVE_META = DB_DIR / "cve_meta.json"
AFFECTS = DB_DIR / "affects.json"  # new: vendor/product -> list of rules


def _get(u: str, tries=5, backoff=1.6) -> bytes:
    s = requests.Session()
    s.headers["User-Agent"] = "QuietPatch/1.0"
    for i in range(tries):
        r = s.get(u, timeout=60)
        if r.ok and r.content:
            return r.content
        time.sleep(backoff**i)
    r.raise_for_status()


def _gunzip(b: bytes) -> bytes:
    with gzip.GzipFile(fileobj=io.BytesIO(b)) as z:
        return z.read()


def nvd_year_feed(year: int) -> str:
    return f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.gz"


def nvd_recent_feed() -> str:
    return "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz"


def kev_feed() -> str:
    return "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def epss_feed() -> str:
    return "https://epss.cyentia.com/epss_scores-current.csv.gz"


def _ingest_nvd_json(
    obj: dict,
    cpe_to_cves: dict[str, set],
    cve_meta: dict[str, dict],
    affects: dict[str, dict[str, list]],
) -> None:
    items = obj.get("CVE_Items") or obj.get("vulnerabilities") or []
    for it in items:
        if "cve" not in it:
            continue

        # CVE id + meta
        if "CVE_data_meta" in it.get("cve", {}):
            cve = it["cve"]["CVE_data_meta"]["ID"]
            metrics = it.get("impact", {})
            descs = it["cve"].get("description", {}).get("description_data", [])
            desc = next((d.get("value") for d in descs if d.get("value")), "")
            cvss = None
            sev = "unknown"
            for k in ("baseMetricV31", "baseMetricV3", "baseMetricV2"):
                if k in metrics:
                    m = (
                        metrics[k].get("cvssV31")
                        or metrics[k].get("cvssV30")
                        or metrics[k].get("cvssV2")
                    )
                    if m:
                        cvss = m.get("baseScore")
                        sev = (m.get("baseSeverity") or "unknown").lower()
                    break
        else:
            # NVD 2.0 schema path
            cve = (it.get("cve") or {}).get("id")
            if not cve:
                continue
            metrics = (it.get("cve") or {}).get("metrics", {})
            desc = ""
            cvss = None
            sev = "unknown"
            for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                arr = metrics.get(key) or []
                if arr:
                    cv = arr[0].get("cvssData", {})
                    cvss = cv.get("baseScore")
                    sev = (arr[0].get("baseSeverity") or "unknown").lower()
                    break

        # configurations → cpe matches + version ranges
        conf = it.get("configurations") or (it.get("cve") or {}).get("configurations") or {}
        for node in conf.get("nodes", []):
            for m in node.get("cpe_match", []):
                if not m.get("vulnerable"):
                    continue
                uri = m.get("cpe23Uri")
                if not uri:
                    continue

                # aggregate mapping
                cpe_to_cves.setdefault(uri, set()).add(cve)

                # range rule for vendor/product
                parts = uri.split(":")
                if len(parts) >= 6:
                    vendor, product, ver = parts[3], parts[4], parts[5]
                    rule = {
                        "cve": cve,
                        "vendor": vendor,
                        "product": product,
                        "ver": ver,  # may be '*'
                        "vsi": m.get("versionStartIncluding"),
                        "vse": m.get("versionStartExcluding"),
                        "vei": m.get("versionEndIncluding"),
                        "vee": m.get("versionEndExcluding"),
                    }
                    affects.setdefault(vendor, {}).setdefault(product, []).append(rule)

        cve_meta.setdefault(cve, {"cvss": cvss, "severity": sev, "desc": desc})


def _load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def sync(years_back: int = 2) -> None:
    # load existing (if any)
    cpe_to_cves = {k: set(v) for k, v in _load_json(CPE_TO_CVES).items()}
    cve_meta = _load_json(CVE_META)
    affects = _load_json(AFFECTS)  # vendor -> product -> [rules]

    # NVD recent + years
    recent = _gunzip(_get(nvd_recent_feed()))
    _ingest_nvd_json(json.loads(recent.decode("utf-8", "ignore")), cpe_to_cves, cve_meta, affects)

    from datetime import datetime

    y = datetime.utcnow().year
    for yr in range(y, y - years_back, -1):
        try:
            data = _gunzip(_get(nvd_year_feed(yr)))
            _ingest_nvd_json(
                json.loads(data.decode("utf-8", "ignore")), cpe_to_cves, cve_meta, affects
            )
        except Exception:
            pass  # keep going

    # KEV / EPSS ingestion stays as-is above this line in your file
    try:
        kev = json.loads(_get(kev_feed()).decode("utf-8", "ignore"))
        kev_ids = {row.get("cveID") for row in kev.get("vulnerabilities", []) if row.get("cveID")}
        for k in kev_ids:
            cve_meta.setdefault(k, {}).update({"kev": True})
    except Exception:
        pass
    # EPSS
    try:
        import csv
        import gzip as gz

        raw = _get(epss_feed())
        with gz.GzipFile(fileobj=io.BytesIO(raw)) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")):
                cid = row.get("cve")
                epss = float((row.get("epss") or "0") or 0)
                if cid:
                    cve_meta.setdefault(cid, {}).update({"epss": epss})
    except Exception:
        pass

    # write atomically
    CPE_TO_CVES.write_text(json.dumps({k: sorted(list(v)) for k, v in cpe_to_cves.items()}))
    CVE_META.write_text(json.dumps(cve_meta))
    AFFECTS.write_text(json.dumps(affects))
