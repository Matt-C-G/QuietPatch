from __future__ import annotations

import json
from pathlib import Path


def load_components(path: str) -> list[dict[str, str]]:
	p = Path(path)
	data = json.loads(p.read_text(encoding="utf-8"))
	out: list[dict[str, str]] = []
	for c in (data.get("components") or []):
		name = c.get("name")
		ver = c.get("version") or ""
		if not name:
			continue
		out.append({"name": str(name), "version": str(ver), "purl": c.get("purl") or ""})
	return out
