from __future__ import annotations
import hashlib, json, os, datetime, math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

UTC = datetime.timezone.utc

def read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())

def deterministic_now_iso() -> str:
    # Always UTC ISO format
    return datetime.datetime.now(UTC).replace(microsecond=0).isoformat()

def safe_int(x: Optional[float]) -> int:
    try:
        return int(x or 0)
    except Exception:
        return 0

def pct(n: int, d: int) -> float:
    return 0.0 if d == 0 else round((n / d) * 100.0, 2)

def sorted_by_keys(items: List[dict], keys: Tuple[str, ...]) -> List[dict]:
    def keyf(it):
        return tuple(str(it.get(k, "")).lower() for k in keys)
    return sorted(items, key=keyf)

def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def kpi_exposure_index(vulns_by_sev: Dict[str,int], assets_scanned: int) -> float:
    weight = {"critical": 1.0, "high": 0.3, "medium": 0.1, "low": 0.03}
    score = sum(vulns_by_sev.get(k,0)*w for k,w in weight.items())
    if assets_scanned <= 0:
        return 0.0
    return round(score / assets_scanned, 2)
