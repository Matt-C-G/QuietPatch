# config_new.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATHS = [
    Path.cwd() / "config" / "quietpatch.json",
    Path.home() / ".quietpatch" / "config.json",
]

DEFAULTS: dict[str, Any] = {
    "allowlist": [],  # if non-empty, ONLY apps matching any token show (substring, case-insensitive)
    "denylist": [],  # apps matching any token are excluded (substring, case-insensitive)
    "normalize_map": {},  # e.g., {"ms edge": "Microsoft Edge", "adobe acrobat reader": "Acrobat Reader"}
    "nvd": {"api_key_env": "NVD_API_KEY", "per_app_limit": 5, "throttle_seconds": 1.2},
    "severity_thresholds": {  # CVSS v3.x
        "critical": 9.0,
        "high": 7.5,
        "medium": 4.0,
        "low": 0.1,
    },
}


def load_config() -> dict[str, Any]:
    # Merge user config (first found) over defaults
    cfg = json.loads(json.dumps(DEFAULTS))
    for p in DEFAULT_CONFIG_PATHS:
        if p.exists():
            try:
                user = json.loads(p.read_text())
                _deep_merge(cfg, user)
                break
            except Exception:
                pass
    return cfg


def _deep_merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
