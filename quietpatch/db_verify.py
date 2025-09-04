"""Database verification and safe extraction with minisign support"""

from __future__ import annotations
from pathlib import Path
import hashlib
import subprocess
import tarfile
import os
import sys


PUBKEYS = [
    # minisign public keys (id + base64). Rotate by appending, not replacing.
    {"id": "main-2025", "key": "RWQ...YOUR_MINISIGN_PUBKEY..."},
]


def verify_with_minisign(artifact: Path, sig: Path) -> None:
    """Verify artifact signature using minisign."""
    ok = False
    errs = []
    for k in PUBKEYS:
        try:
            subprocess.run(
                ["minisign", "-Vm", str(artifact), "-P", k["key"]],
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE
            )
            ok = True
            break
        except subprocess.CalledProcessError as e:
            errs.append((k["id"], e.stderr.decode(errors="ignore")))
        except FileNotFoundError:
            errs.append((k["id"], "minisign not found"))
    
    if not ok:
        print(f"[DB-SIGN] Signature verification failed for {artifact.name}", file=sys.stderr)
        for key_id, error in errs:
            print(f"  {key_id}: {error}", file=sys.stderr)
        raise SystemExit(1)


def _is_within(base: Path, target: Path) -> bool:
    """Check if target path is within base directory (path traversal protection)."""
    try:
        return target.resolve().is_relative_to(base.resolve())  # py3.9+
    except AttributeError:
        return str(target.resolve()).startswith(str(base.resolve()))


def safe_extract_tar(archive: Path, dest: Path) -> None:
    """Safely extract tar archive with path traversal protection."""
    dest.mkdir(parents=True, exist_ok=True)
    
    with tarfile.open(archive, "r:*") as t:
        for m in t.getmembers():
            # Prohibit absolute paths, symlinks outside, and .. traversal
            if m.islnk() or m.issym():
                raise SystemExit(f"[DB-PATH] Refusing link entry: {m.name}")
            
            # Check for path traversal attempts
            if ".." in m.name or m.name.startswith("/"):
                raise SystemExit(f"[DB-PATH] Unsafe path in archive: {m.name}")
            
            target = dest / m.name
            if not _is_within(dest, target):
                raise SystemExit(f"[DB-PATH] Unsafe path in archive: {m.name}")
        
        # Extract all members after validation
        t.extractall(dest)


def verify_and_extract(db_archive: Path, db_sig: Path, outdir: Path) -> Path:
    """Verify signature and safely extract database archive."""
    if not db_archive.exists():
        raise SystemExit(f"[DB-FILE] Archive not found: {db_archive}")
    
    if not db_sig.exists():
        raise SystemExit(f"[DB-SIG] Signature not found: {db_sig}")
    
    # Verify signature first
    verify_with_minisign(db_archive, db_sig)
    
    # Extract safely
    safe_extract_tar(db_archive, outdir)
    
    return outdir


def verify_manifest_signature(manifest_path: Path, sig_path: Path) -> None:
    """Verify manifest.json signature."""
    if not manifest_path.exists():
        raise SystemExit(f"[MANIFEST] Not found: {manifest_path}")
    
    if not sig_path.exists():
        raise SystemExit(f"[MANIFEST-SIG] Not found: {sig_path}")
    
    verify_with_minisign(manifest_path, sig_path)
