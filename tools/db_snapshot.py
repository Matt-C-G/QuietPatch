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


def _copy_db(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        return
    for p in src.glob("*"):
        tgt = dst / p.name
        if p.is_dir():
            import shutil
            shutil.copytree(p, tgt, dirs_exist_ok=True)
        else:
            tgt.write_bytes(p.read_bytes())


def _run_sync(years_back: int, tmp_out: Path) -> None:
    """Try to run your repo's network sync; otherwise copy current DB."""
    tmp_out.mkdir(parents=True, exist_ok=True)
    try:
        from src.datafeed.sync import sync  # your existing feed sync (if present)

        print(f"[db-snapshot] Running online sync for last {years_back} years …")
        # Our sync writes to data/db; call it and then copy artifacts into tmp_out
        sync(years_back=years_back)
        _copy_db(DEFAULT_DB_DIR, tmp_out)
    except Exception as e:
        print(
            f"[db-snapshot] Online sync not available or failed ({e!r})."
            f" Falling back to current {DEFAULT_DB_DIR} …"
        )
        if not DEFAULT_DB_DIR.exists():
            raise SystemExit("No data/db available to bundle; aborting.")
        _copy_db(DEFAULT_DB_DIR, tmp_out)


def _derive_severity_from_score(score) -> str:
    try:
        s = float(score)
    except Exception:
        return "unknown"
    if s == 0:
        return "none"
    if s >= 9.0:
        return "critical"
    if s >= 7.0:
        return "high"
    if s >= 4.0:
        return "medium"
    return "low"


def _normalize_severities(db_dir: Path) -> None:
    """Ensure every CVE in cve_meta.json has a concrete severity; never 'unknown'.
    Adds a 'severity_source' field explaining provenance.
    Guardrails: raise if any invalid value remains.
    """
    meta_path = db_dir / "cve_meta.json"
    if not meta_path.exists():
        return
    try:
        meta = json.loads(meta_path.read_text())
    except Exception as e:
        raise SystemExit(f"[db-snapshot] Failed to read {meta_path}: {e}")

    changed = 0
    for _cid, row in meta.items():
        sev = (row.get("severity") or "").lower()
        if sev in ("critical", "high", "medium", "low", "none"):
            # keep existing, but ensure canonical
            row["severity"] = sev
            continue

        # 1) CVSS base score mapping
        sc = row.get("cvss")
        if sc is not None:
            new_sev = _derive_severity_from_score(sc)
            if new_sev != "unknown":
                row["severity"] = new_sev
                row["severity_source"] = "cvss"
                changed += 1
                continue

        # 2) KEV signal => at least high
        if row.get("kev"):
            row["severity"] = "high"
            row["severity_source"] = "kev"
            changed += 1
            continue

        # 3) EPSS thresholds
        epss = row.get("epss")
        if isinstance(epss, (int, float)):
            if epss >= 0.70:
                row["severity"] = "high"
                row["severity_source"] = "epss"
            elif epss >= 0.30:
                row["severity"] = "medium"
                row["severity_source"] = "epss"
            else:
                row["severity"] = "low"
                row["severity_source"] = "epss"
            changed += 1
            continue

        # 4) Absolute floor
        row["severity"] = "low"
        row["severity_source"] = "floor"
        changed += 1

    meta_path.write_text(json.dumps(meta))

    # Guardrail
    invalid = [r for r in meta.values() if (r.get("severity") not in {"none","low","medium","high","critical"})]
    if invalid:
        raise SystemExit("[snapshot] invalid severity value present after normalization")
    print(f"[db-snapshot] Normalized severities for {changed} CVEs")


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
        _normalize_severities(tmp_out)
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
        out_path.write_bytes(raw.read())

        sha_path = out_path.with_suffix(out_path.suffix + ".sha256")
        sha_path.write_text(_sha256(out_path) + "  " + out_path.name + "\n", encoding="utf-8")
        print(f"[db-snapshot] Wrote {out_path} and {sha_path}")
        return out_path
    finally:
        import shutil

        shutil.rmtree(tmp_out, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years-back", type=int, default=5)
    ap.add_argument("--out", type=Path, default=DIST_DIR)
    args = ap.parse_args()
    build_snapshot(args.years_back, args.out)


if __name__ == "__main__":
    main()
