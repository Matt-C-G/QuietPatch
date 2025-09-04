#!/usr/bin/env python3
"""
QuietPatch Catalog Updater
- Fetches manifest.json
- Chooses latest snapshot
- Verifies minisign
- Enforces epoch/rollback
- Extracts safely
"""

from pathlib import Path
import json
import os
import sys
import urllib.request
from typing import Dict, Any

from quietpatch.db_verify import verify_and_extract, verify_manifest_signature
from quietpatch.db_state import check_epoch_protection, check_rollback_protection, update_state


QP_HOME = Path(os.environ.get("QUIETPATCH_HOME", Path.home() / ".quietpatch"))
DBDIR = QP_HOME / "db"
MANIFEST_URL = os.environ.get("QP_MANIFEST_URL", "https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/manifest.json")


def download(url: str, dest: Path) -> Path:
    """Download file from URL to destination."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Downloading {url} -> {dest}")
    
    with urllib.request.urlopen(url, timeout=30) as r:
        with open(dest, "wb") as f:
            f.write(r.read())
    
    return dest


def load_manifest() -> Dict[str, Any]:
    """Load and verify the catalog manifest."""
    manifest_path = DBDIR / "manifest.json"
    manifest_sig_path = DBDIR / "manifest.json.minisig"
    
    # Download manifest and signature
    download(MANIFEST_URL, manifest_path)
    download(MANIFEST_URL + ".minisig", manifest_sig_path)
    
    # Verify manifest signature
    verify_manifest_signature(manifest_path, manifest_sig_path)
    
    # Load manifest
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    return manifest


def check_client_version(manifest: Dict[str, Any]) -> None:
    """Check if client version meets minimum requirements."""
    try:
        from quietpatch import __version__
        client_version = __version__
    except ImportError:
        try:
            import importlib.metadata
            client_version = importlib.metadata.version("quietpatch")
        except Exception:
            client_version = "0.0.0"
    
    min_client = manifest["catalog"].get("min_client", "0.0.0")
    
    # Simple version comparison (assumes semantic versioning)
    def version_tuple(v):
        return tuple(map(int, v.split('.')[:3]))
    
    if version_tuple(client_version) < version_tuple(min_client):
        raise SystemExit(f"[CLIENT-VERSION] Client {client_version} < required {min_client}")


def main():
    """Main catalog update process."""
    print("🔄 Starting QuietPatch catalog update...")
    
    # Load and verify manifest
    manifest = load_manifest()
    catalog = manifest["catalog"]
    
    # Check client version
    check_client_version(manifest)
    
    # Extract catalog info
    epoch = int(catalog["epoch"])
    snapshot_date = catalog["snapshot_date"]
    latest_url = catalog["latest"]
    signature_ext = catalog["signature_ext"]
    
    print(f"📋 Catalog epoch: {epoch}, date: {snapshot_date}")
    
    # Enforce epoch protection
    check_epoch_protection(epoch, allow_downgrade=os.environ.get("QP_ALLOW_DOWNGRADE") == "1")
    
    # Enforce rollback protection
    check_rollback_protection(snapshot_date, allow_downgrade=os.environ.get("QP_ALLOW_DOWNGRADE") == "1")
    
    # Prepare file paths
    zst_path = DBDIR / "qp_db-latest.tar.zst"
    sig_path = DBDIR / "qp_db-latest.tar.zst.minisig"
    
    # Download database and signature
    download(latest_url, zst_path)
    download(latest_url + signature_ext, sig_path)
    
    # Verify and extract
    print("🔐 Verifying signature and extracting...")
    verify_and_extract(zst_path, sig_path, DBDIR)
    
    # Update state
    update_state(snapshot_date, epoch)
    
    print("✅ Catalog updated successfully!")
    print(f"   Epoch: {epoch}")
    print(f"   Date: {snapshot_date}")
    print(f"   Location: {DBDIR}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Update failed: {e}")
        sys.exit(1)
