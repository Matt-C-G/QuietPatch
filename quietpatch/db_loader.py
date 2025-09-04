from __future__ import annotations

from pathlib import Path
import tarfile
import subprocess


def _decompress(src: Path) -> Path:
    if src.suffix == ".gz":
        out = src.with_suffix("")
        with tarfile.open(src, "r:gz") as t:
            t.extractall(out.parent)
        return out
    if src.suffix == ".zst":
        out = src.with_suffix("")
        subprocess.run(["zstd", "-d", "-f", str(src)], check=True)
        # if the result is .tar, extract
        if out.suffix == ".tar":
            with tarfile.open(out, "r:") as t:
                t.extractall(out.parent)
            out.unlink(missing_ok=True)
            return out.parent
        return out.parent
    raise RuntimeError(f"Unsupported DB archive: {src}")


def find_db(db_dir: Path) -> Path:
    # Accept both patterns; prefer latest symlink/file
    candidates = list(db_dir.glob("qp_db-latest.tar.*")) + \
                 sorted(db_dir.glob("qp_db-*.tar.*"), reverse=True) + \
                 list(db_dir.glob("db-latest.tar.*")) + \
                 sorted(db_dir.glob("db-*.tar.*"), reverse=True)
    if not candidates:
        raise FileNotFoundError("No QuietPatch DB found. Run: quietpatch db fetch")
    return _decompress(candidates[0])

