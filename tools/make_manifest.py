# tools/make_manifest.py
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from src.datafeed.snapshot_manifest import ManifestFile, SnapshotManifest, sha256_file


def _maybe_gzip(path: Path, gz: bool) -> Path:
    if not gz:
        return path
    out = path.with_suffix(path.suffix + ".gz")
    with open(path, "rb") as fi, gzip.open(out, "wb", compresslevel=9) as fo:
        while True:
            b = fi.read(1024 * 1024)
            if not b:
                break
            fo.write(b)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Directory with raw db files")
    ap.add_argument("--out", required=True, help="Destination snapshot dir")
    ap.add_argument("--version", required=True, help="e.g. 2025-08-22")
    ap.add_argument("--gzip", action="store_true", help="Emit .gz files")
    args = ap.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # the raw filenames your app expects post-install
    want = [
        "cpe_to_cves.json",
        "cve_meta.json",
        "kev.json",
        "epss.csv",
        "aliases.json",
        "affects.json",
    ]
    files: list[ManifestFile] = []
    for w in want:
        raw = src / w
        if not raw.exists():
            print(f"WARNING: missing {w}")
            continue
        emit = _maybe_gzip(raw, args.gzip)
        rel = emit.name
        h = sha256_file(str(emit))
        files.append(ManifestFile(name=rel, sha256=h, size=emit.stat().st_size))

        # copy payload into snapshot out dir
        (out / rel).write_bytes(emit.read_bytes())

    man = SnapshotManifest(version=args.version, files=files).__dict__
    man["files"] = [f.__dict__ for f in files]
    (out / "manifest.json").write_text(json.dumps(man, indent=2))
    print(f"snapshot wrote: {out / 'manifest.json'}")
    print("Remember to sign it: minisign -Sm manifest.json  (produces manifest.json.minisig)")


if __name__ == "__main__":
    main()
