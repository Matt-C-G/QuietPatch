from __future__ import annotations

import re
from pathlib import Path


def compute_unknown_count_from_html(html_path: str | Path) -> int:
    p = Path(html_path)
    if not p.exists():
        return 0
    html = p.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'<meta[^>]+name=["\']unknown-count["\'][^>]+content=["\'](\d+)["\']', html)
    if not m:
        # fallback: scan for severity="unknown" marker
        return 1 if re.search(r'\bdata-severity=\"unknown\"', html) else 0
    return int(m.group(1))

