#!/usr/bin/env python3
"""
Builds an offline DB snapshot (tar.zst) for QuietPatch.

- If your repo has src.datafeed.sync:sync(years_back, outdir), we call it.
- Otherwise we package the existing data/db directory as-is.
- Writes dist/db-YYYYMMDD.tar.zst and a SHA256 alongside.
- Also writes a small db-manifest.json into the tarball.

Usage:
  python3 tools/db_snapshot.py --years-back 5 --out dist
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import tarfile
from pathlib import Path
import sys

# Add repo root if needed when running the script directly
if __package__ is None and str(Path(__file__).resolve().parents[1]) not in sys.path:
	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DEFAULT_DB_DIR = Path("data/db")
DIST_DIR = Path("dist")


def _sha256(path: Path) -> str:
	h = hashlib.sha256()
	with path.open("rb") as f:
		for chunk in iter(lambda: f.read(1024 * 1024), b""):
			h.update(chunk)
	return h.hexdigest()


def _zstd_open(fileobj, level: int = 19):
	# No external deps: use tar with "w:gz" as fallback if zstandard isn't available on host.
	# If you have zstandard installed on CI, prefer it by setting QP_ZSTD=1 in env.
	if os.environ.get("QP_ZSTD") == "1":
		try:
			import zstandard as zstd  # type: ignore

			cctx = zstd.ZstdCompressor(level=level)
			return cctx.stream_writer(fileobj)
		except Exception:
			pass
	# fallback: gzip
	import gzip

	return gzip.GzipFile(fileobj=fileobj, mode="wb", compresslevel=9)


def _run_sync(years_back: int, tmp_out: Path) -> None:
	"""Try to run your repo's network sync; otherwise copy current DB."""
	tmp_out.mkdir(parents=True, exist_ok=True)
	try:
		from quietpatch.datafeed.sync import sync  # your existing feed sync (if present)

		print(f"[db-snapshot] Running online sync for last {years_back} years …")
		sync(years_back=years_back, outdir=str(tmp_out))
		# Expect it to populate cpe_to_cves.json, cve_meta.json, kev.json, epss.json, etc.
	except Exception as e:
		print(
			f"[db-snapshot] Online sync not available or failed ({e!r})."
			f" Falling back to current {DEFAULT_DB_DIR} …"
		)
		if not DEFAULT_DB_DIR.exists():
			raise SystemExit("No data/db available to bundle; aborting.")
		for p in DEFAULT_DB_DIR.glob("*"):
			tgt = tmp_out / p.name
			if p.is_dir():
				import shutil

				shutil.copytree(p, tgt, dirs_exist_ok=True)
			else:
				tgt.write_bytes(p.read_bytes())


def _write_manifest(tmp_out: Path, years_back: int) -> None:
	manifest = {
		"generated_at_utc": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
		"years_back": years_back,
		"source": "sync() if available else packaged data/db",
		"files": sorted([p.name for p in tmp_out.glob("*")]),
		"schema": {
			"cpe_to_cves": "json",
			"cve_meta": "json",
			"kev": "json (optional)",
			"epss": "json/csv converted to json (optional)",
		},
	}
	(tmp_out / "db-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def build_snapshot(years_back: int, out_dir: Path) -> Path:
	out_dir.mkdir(parents=True, exist_ok=True)
	tmp_out = Path(".snapshot_tmp")
	if tmp_out.exists():
		import shutil

		shutil.rmtree(tmp_out)
	tmp_out.mkdir(parents=True)

	try:
		_run_sync(years_back, tmp_out)
		_write_manifest(tmp_out, years_back)

		stamp = dt.datetime.utcnow().strftime("%Y%m%d")
		# Prefer .tar.zst but fall back to .tar.gz if zstd not available.
		use_zstd = os.environ.get("QP_ZSTD") == "1"
		ext = "tar.zst" if use_zstd else "tar.gz"
		out_path = out_dir / f"db-{stamp}.{ext}"

		raw = io.BytesIO()
		with _zstd_open(raw, level=19) as comp:
			with tarfile.open(fileobj=comp, mode="w|") as tf:
				for p in sorted(tmp_out.glob("*")):
					tf.add(p, arcname=p.name)
		raw.seek(0)
		with open(out_path, "wb") as f:
			f.write(raw.read())

		sha = _sha256(out_path)
		(out_path.with_suffix(out_path.suffix + ".sha256")).write_text(sha + "  " + out_path.name)

		return out_path
	finally:
		import shutil

		shutil.rmtree(tmp_out, ignore_errors=True)


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--years-back", type=int, default=5)
	ap.add_argument("--out", type=Path, default=DIST_DIR)
	args = ap.parse_args()

	out_path = build_snapshot(args.years_back, args.out)
	print(f"Wrote {out_path}")


if __name__ == "__main__":
	main()
