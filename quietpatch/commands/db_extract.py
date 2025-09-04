"""Database extraction with dual format support (.zst + .gz fallback)"""

import os
import tarfile
from pathlib import Path
from typing import Optional


def extract_db(db_path: Path, extract_to: Path) -> bool:
    """
    Extract database with fallback from .zst to .gz if needed.
    
    Args:
        db_path: Path to the database file
        extract_to: Directory to extract to
        
    Returns:
        True if extraction succeeded, False otherwise
    """
    extract_to.mkdir(parents=True, exist_ok=True)
    
    # Try .zst first
    if db_path.suffix == '.zst':
        try:
            import zstandard
            with zstandard.open(db_path, 'rb') as zst_file:
                with tarfile.open(fileobj=zst_file, mode='r|*') as tar:
                    tar.extractall(extract_to)
            return True
        except ImportError:
            print("[DB-DECOMP] zstandard not available; falling back to .gz", flush=True)
            # Look for .gz version
            gz_path = db_path.with_suffix('.tar.gz')
            if gz_path.exists():
                return extract_db(gz_path, extract_to)
            else:
                print(f"[DB-DECOMP] No .gz fallback found for {db_path.name}", flush=True)
                return False
        except Exception as e:
            print(f"[DB-DECOMP] .zst extraction failed: {e}; falling back to .gz", flush=True)
            # Look for .gz version
            gz_path = db_path.with_suffix('.tar.gz')
            if gz_path.exists():
                return extract_db(gz_path, extract_to)
            else:
                print(f"[DB-DECOMP] No .gz fallback found for {db_path.name}", flush=True)
                return False
    
    # Try .gz
    elif db_path.suffix == '.gz':
        try:
            with tarfile.open(db_path, 'r:gz') as tar:
                tar.extractall(extract_to)
            return True
        except Exception as e:
            print(f"[DB-DECOMP] .gz extraction failed: {e}", flush=True)
            return False
    
    # Try .bz2
    elif db_path.suffix == '.bz2':
        try:
            with tarfile.open(db_path, 'r:bz2') as tar:
                tar.extractall(extract_to)
            return True
        except Exception as e:
            print(f"[DB-DECOMP] .bz2 extraction failed: {e}", flush=True)
            return False
    
    else:
        print(f"[DB-DECOMP] Unsupported format: {db_path.suffix}", flush=True)
        return False


def find_best_db(data_dir: Path) -> Optional[Path]:
    """
    Find the best available database file, preferring .zst over .gz.
    
    Args:
        data_dir: Directory to search in
        
    Returns:
        Path to the best database file, or None if none found
    """
    # Look for db-latest first
    for ext in ['.tar.zst', '.tar.gz', '.tar.bz2']:
        latest_path = data_dir / f'db-latest{ext}'
        if latest_path.exists():
            return latest_path
    
    # Look for dated files, preferring .zst
    candidates = []
    for ext in ['.tar.zst', '.tar.gz', '.tar.bz2']:
        candidates.extend(data_dir.glob(f'db-*{ext}'))
    
    if not candidates:
        return None
    
    # Sort by modification time, newest first
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Prefer .zst files
    zst_candidates = [p for p in candidates if p.suffix == '.zst']
    if zst_candidates:
        return zst_candidates[0]
    
    # Fall back to any format
    return candidates[0]
