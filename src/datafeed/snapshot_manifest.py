# src/datafeed/snapshot_manifest.py
from __future__ import annotations
import dataclasses, json, hashlib, os
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ManifestFile:
    name: str
    sha256: str
    size: int | None = None

@dataclass
class SnapshotManifest:
    version: str                # e.g., "2025-08-22"
    files: List[ManifestFile]   # ordered
    meta: Dict[str, Any] | None = None

    @staticmethod
    def load_bytes(b: bytes) -> "SnapshotManifest":
        d = json.loads(b.decode("utf-8"))
        files = [ManifestFile(**f) for f in d["files"]]
        return SnapshotManifest(version=d["version"], files=files, meta=d.get("meta"))

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


