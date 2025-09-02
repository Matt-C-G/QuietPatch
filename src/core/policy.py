# src/core/policy.py
from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# ---------- Severity normalization ----------

# Canonical rank (keep integers stable for tests)
_SEV_RANK: dict[str, int] = {
    "none": 0,
    "low": 2,
    "medium": 3,
    "high": 4,
    "critical": 5,
    "unknown": 0,  # will be remapped by policy if requested
}


def _coerce_sev_label(v: Any) -> str:
    """Accept 'medium', 3, '3', etc. Return canonical label."""
    if isinstance(v, int):
        # reverse map: pick label with matching rank
        for k, n in _SEV_RANK.items():
            if n == v:
                return k
        return "unknown"
    s = str(v).strip().lower()
    if s in _SEV_RANK:
        return s
    # Accept numeric strings
    try:
        n = int(s)
        return _coerce_sev_label(n)
    except Exception:
        return "unknown"


def _sev_to_int(label: str, treat_unknown_as: str) -> int:
    """Map label to rank; remap 'unknown' according to policy."""
    if label == "unknown":
        label = treat_unknown_as
    return _SEV_RANK.get(label, 0)


# ---------- Policy model ----------


@dataclass(frozen=True)
class Policy:
    allow: list[str]
    deny: list[str]
    min_severity: str
    only_with_cves: bool
    limit_per_app: int
    treat_unknown_as: str
    unknown_strategy: str = "infer"  # infer | drop | fail


DEFAULT_POLICY = Policy(
    allow=[],
    deny=[],
    min_severity="medium",
    only_with_cves=True,
    limit_per_app=50,
    treat_unknown_as="low",
    unknown_strategy="infer",
)


def load_policy(path: str | Path = "config/policy.yml") -> Policy:
    p = Path(path)
    if not p.exists():
        return DEFAULT_POLICY
    data = yaml.safe_load(p.read_text()) or {}
    # sanitize unknown_strategy
    raw_strategy = str(data.get("unknown_strategy", DEFAULT_POLICY.unknown_strategy)).strip().lower()
    if raw_strategy not in ("infer", "drop", "fail"):
        raw_strategy = DEFAULT_POLICY.unknown_strategy
    return Policy(
        allow=[str(x) for x in (data.get("allow") or [])],
        deny=[str(x) for x in (data.get("deny") or [])],
        min_severity=_coerce_sev_label(data.get("min_severity", DEFAULT_POLICY.min_severity)),
        only_with_cves=bool(data.get("only_with_cves", DEFAULT_POLICY.only_with_cves)),
        limit_per_app=int(data.get("limit_per_app", DEFAULT_POLICY.limit_per_app)),
        treat_unknown_as=_coerce_sev_label(
            data.get("treat_unknown_as", DEFAULT_POLICY.treat_unknown_as)
        ),
        unknown_strategy=raw_strategy,
    )


# ---------- Scoring / rollup ----------


def _cve_risk_tuple(cve: dict[str, Any], treat_unknown_as: str) -> tuple[int, float, bool, str]:
    # Sort key: severity (desc), cvss (desc), kev (desc), cve id (asc) for stability
    sev_label = _coerce_sev_label(cve.get("severity", "unknown"))
    sev_score = _sev_to_int(sev_label, treat_unknown_as)
    cvss = float(cve.get("cvss") or 0.0)
    kev = bool(cve.get("kev", False))
    cid = str(cve.get("id") or cve.get("cve") or "")
    # Invert kev so True sorts before False (KEV promotes display)
    return (sev_score, cvss, not kev, cid)


def rollup_app_severity(app: dict[str, Any], treat_unknown_as: str) -> int:
    cves = app.get("cves") or []
    if not isinstance(cves, list) or not cves:
        return 0
    return max(_cve_risk_tuple(c, treat_unknown_as)[0] for c in cves)


# ---------- Allow/Deny ----------


def _match_any(globs: list[str], text: str) -> bool:
    text_l = text.lower()
    for pat in globs:
        if fnmatch.fnmatch(text_l, pat.lower()):
            return True
    return False


def _is_denied(app_name: str, deny: list[str]) -> bool:
    return _match_any(deny, app_name)


def _is_allowed(app_name: str, allow: list[str]) -> bool:
    return True if not allow else _match_any(allow, app_name)


# ---------- Main application ----------


def apply_policy(data, policy: Policy):
    """
    Filter and sort CVEs within each app according to policy.
    """
    filtered_apps = []
    # Normalize unknown severity up-front
    for apprec in data:
        new_cves = []
        for cve in apprec["cves"]:
            sev = cve.get("severity", "unknown")
            if sev == "unknown" and policy.treat_unknown_as:
                cve["severity"] = policy.treat_unknown_as.lower()
            new_cves.append(cve)
        apprec["cves"] = new_cves
        filtered_apps.append(apprec)

    # Apply min severity gate and limits
    out = []
    min_rank = _sev_to_int(policy.min_severity, policy.treat_unknown_as)

    for app in filtered_apps:
        cves = app["cves"]

        # Check if app meets minimum severity requirement
        max_sev = max((_SEV_RANK[c.get("severity", "unknown")] for c in cves), default=0)
        if max_sev < min_rank:
            continue

        cves_sorted = sorted(
            cves,
            key=lambda x: (
                -_SEV_RANK[x["severity"]],
                -x.get("cvss", 0),
                0 if x.get("kev") else 1,
                x.get("id", ""),
            ),
        )
        app["cves"] = cves_sorted[: policy.limit_per_app]
        out.append(app)

    # Sort apps themselves by max severity/score
    out.sort(
        key=lambda a: max(
            (_SEV_RANK[c["severity"]] * 10 + int(c.get("cvss", 0)) for c in a["cves"]),
            default=0,
        ),
        reverse=True,
    )
    return out
