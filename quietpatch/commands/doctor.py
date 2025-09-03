from __future__ import annotations

import os
import sys
import time
import webbrowser
from pathlib import Path
from typing import Tuple

MIN_PY = (3, 11)
MAX_PY = (3, 14)  # support 3.11–3.13 inclusive of minors, exclusive of 3.14


def _ok(msg: str) -> Tuple[str, str]:
	return ("OK", msg)


def _warn(msg: str) -> Tuple[str, str]:
	return ("WARN", msg)


def _fail(msg: str) -> Tuple[str, str]:
	return ("FAIL", msg)


def _check_python() -> Tuple[str, str, int | None]:
	v = sys.version_info
	ver = (v.major, v.minor)
	if MIN_PY <= ver < MAX_PY:
		return (*_ok(f"Python {v.major}.{v.minor}"), None)
	# Code 1: missing deps (wrong python)
	return (*_fail(f"Python {v.major}.{v.minor} not in supported range 3.11–3.13"), 1)


def _resolve_pex_root() -> Path:
	custom = os.environ.get("PEX_ROOT")
	if custom:
		return Path(custom)
	if sys.platform == "win32":
		base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
		return base / "quietpatch" / ".pexroot"
	# *nix
	cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
	return cache_home / "quietpatch" / ".pexroot"


def _check_pex_env() -> Tuple[str, str, int | None]:
	pex_root = _resolve_pex_root()
	try:
		pex_root.mkdir(parents=True, exist_ok=True)
		t = pex_root / ".w"
		t.write_text("x", encoding="utf-8")
		t.unlink(missing_ok=True)
		return (*_ok(f"PEX_ROOT OK at {pex_root}"), None)
	except Exception as e:
		# Code 3: write/open error
		return (*_fail(f"PEX_ROOT not writable: {pex_root} ({e})"), 3)


def _find_db_file(explicit: str | None) -> Path | None:
	if explicit:
		return Path(explicit)
	data_dir = Path(os.environ.get("QP_DATA_DIR", "data"))
	# prefer db-latest alias
	for ext in (".tar.zst", ".tar.gz", ".tar.bz2"):
		p = data_dir / f"db-latest{ext}"
		if p.exists():
			return p
	# fall back to newest db-*.tar.*
	candidates = list(data_dir.glob("db-*.tar.*"))
	if not candidates:
		return None
	return max(candidates, key=lambda p: p.stat().st_mtime)


def _check_db_freshness(explicit: str | None) -> Tuple[str, str, int | None]:
	p = _find_db_file(explicit)
	if explicit and (not p or not p.exists()):
		# user requested a specific DB path but it's missing
		return (*_fail(f"DB snapshot not found: {explicit}"), 1)
	if not p or not p.exists():
		# optional in many flows
		return (*_warn("DB snapshot not found (optional)"), None)
	age_days = (time.time() - p.stat().st_mtime) / 86400.0
	if age_days > 30.0:
		# Code 2: DB stale
		return (*_fail(f"DB snapshot is stale ({age_days:.0f} days old): {p.name}"), 2)
	return (*_ok(f"DB snapshot OK ({age_days:.0f} days old): {p.name}"), None)


def _check_report_dir(out_dir: str | None) -> Tuple[str, str, int | None]:
	out = Path(out_dir or "./reports")
	try:
		out.mkdir(parents=True, exist_ok=True)
		t = out / ".w"
		t.write_text("x", encoding="utf-8")
		t.unlink(missing_ok=True)
		return (*_ok(f"Writable report dir {out}"), None)
	except Exception as e:
		# Code 3: write/open error
		return (*_fail(f"Report dir not writable: {out} ({e})"), 3)


def _check_open(open_check: bool) -> Tuple[str, str, int | None]:
	if not open_check:
		return (*_ok("Browser check skipped"), None)
	try:
		webbrowser.get()
		return (*_ok("Browser integration OK"), None)
	except Exception:
		# Code 3: write/open error
		return (*_fail("Default browser not available"), 3)


def run(db: str | None = None, out_dir: str | None = None, open_check: bool = False) -> int:
	checks: list[tuple[str, Tuple[str, str, int | None]]] = [
		("Python", _check_python()),
		("PEX env", _check_pex_env()),
		("DB freshness", _check_db_freshness(db)),
		("Report dir", _check_report_dir(out_dir)),
		("Report open", _check_open(open_check)),
	]

	worst_exit: int | None = None
	for name, (lvl, msg, code) in checks:
		tag = "✅" if lvl == "OK" else ("⚠️" if lvl == "WARN" else "❌")
		print(f"{tag} {name}: {msg}")
		if code is not None:
			worst_exit = max(worst_exit or 0, code)

	return int(worst_exit or 0)