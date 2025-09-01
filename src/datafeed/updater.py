# src/datafeed/updater.py
from __future__ import annotations
import os, io, sys, json, time, gzip, shutil, hashlib, tempfile, subprocess, logging
from pathlib import Path
from typing import Iterable, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests

from src.datafeed.snapshot_manifest import SnapshotManifest, ManifestFile

LOG = logging.getLogger("quietpatch.updater")

# Files we expect after install (decompressed names)
TARGET_FILENAMES = {
    "cpe_to_cves.json",
    "cve_meta.json",
    "kev.json",
    "epss.csv",
    "aliases.json",
    "affects.json",
}

# Map compressed source -> decompressed target name
# (Accept .json, .json.gz, .json.zst ; .csv/.csv.gz similarly)
def _target_name(src_name: str) -> str:
    n = src_name
    for suf in (".zst", ".gz"):
        if n.endswith(suf):
            n = n[: -len(suf)]
    return n

def _requests_session(tor_socks: Optional[str], privacy: str, timeout: int) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "QuietPatch/0",
        # Avoid conditionals; keep requests boring & uniform
        "Cache-Control": "no-store",
        "Pragma": "no-cache",
    })
    if tor_socks:
        proxy = f"socks5h://{tor_socks}"
        s.proxies.update({"http": proxy, "https": proxy})
    # Disable redirects in strict privacy if you want; here we allow but log.
    s.max_redirects = 3
    s.request = _wrap_request(s.request, timeout=timeout)
    return s

def _wrap_request(fn, timeout: int):
    def _inner(method, url, **kw):
        kw.setdefault("timeout", timeout)
        # Avoid conditional GETs (no ETag/If-Modified-Since)
        for h in ("If-Modified-Since", "If-None-Match"):
            if kw.get("headers") and h in kw["headers"]:
                del kw["headers"][h]
        return fn(method, url, **kw)
    return _inner

def _read_url(url: str, sess: requests.Session) -> bytes:
    p = urlparse(url)
    if p.scheme in ("file", ""):
        path = p.path if p.scheme == "file" else url
        with open(path, "rb") as f:
            return f.read()
    r = sess.get(url, allow_redirects=True, stream=True)
    r.raise_for_status()
    buf = io.BytesIO()
    for chunk in r.iter_content(1024 * 1024):
        buf.write(chunk)
    return buf.getvalue()

def _minisign_verify_if_available(manifest_bytes: bytes, sig_bytes: bytes, pubkey_path: Optional[str]) -> Tuple[bool, str]:
    """
    Verify manifest with minisign if both minisign and pubkey are present.
    Returns (ok, msg). If minisign or pubkey is missing, returns (True, "skipped").
    """
    minisign = shutil.which("minisign")
    if not minisign or not pubkey_path:
        return True, "minisign not used"
    with tempfile.TemporaryDirectory() as td:
        m = Path(td, "manifest.json"); m.write_bytes(manifest_bytes)
        s = Path(td, "manifest.json.minisig"); s.write_bytes(sig_bytes)
        cmd = [minisign, "-Vm", str(m), "-P", pubkey_path, "-q"]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode == 0:
            return True, "minisign OK"
        return False, f"minisign failed: {r.stderr.decode('utf-8', 'ignore').strip()}"

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _decompress_if_needed(data: bytes, name: str) -> bytes:
    if name.endswith(".gz"):
        return gzip.decompress(data)
    if name.endswith(".zst"):
        try:
            import zstandard as zstd  # optional
        except Exception as e:
            raise RuntimeError("zstandard not installed but .zst used") from e
        d = zstd.ZstdDecompressor().decompress(data)
        return d
    return data

def refresh_db(
    data_dir: str,
    mirrors: Iterable[str],
    tor_socks: Optional[str] = None,
    privacy: str = "strict",
    timeout: int = 30,
    pubkey_path: Optional[str] = None,
) -> dict:
    """
    Download snapshot manifest & objects, verify, install atomically into data_dir/db
    Returns summary dict.
    """
    data_root = Path(data_dir)
    db_root = data_root / "db"
    staging = data_root / ".db.staging"
    staging.mkdir(parents=True, exist_ok=True)

    sess = _requests_session(tor_socks, privacy, timeout)

    last_err = None
    manifest_b = None
    manifest_sig_b = None
    used_mirror = None

    # 1) get manifest + optional signature
    for base in mirrors:
        try:
            base = base.rstrip("/") + "/"
            m_url = urljoin(base, "manifest.json")
            manifest_b = _read_url(m_url, sess)
            try:
                manifest_sig_b = _read_url(urljoin(base, "manifest.json.minisig"), sess)
            except Exception:
                manifest_sig_b = None
            used_mirror = base
            LOG.info("Fetched manifest from %s", base)
            break
        except Exception as e:
            last_err = e
            LOG.warning("Mirror failed: %s (%s)", base, e)

    if not manifest_b:
        raise RuntimeError(f"All mirrors failed. Last error: {last_err}")

    # 2) verify signature if possible
    if manifest_sig_b is not None:
        ok, msg = _minisign_verify_if_available(manifest_b, manifest_sig_b, pubkey_path)
        LOG.info("Manifest signature check: %s", msg)
        if not ok:
            raise RuntimeError("Manifest signature invalid")

    # 3) parse manifest
    man = SnapshotManifest.load_bytes(manifest_b)

    # 4) download each file & verify content hash
    downloaded = []
    for mf in man.files:
        src_name = mf.name
        url = urljoin(used_mirror, src_name)
        raw = _read_url(url, sess)
        calc = _sha256(raw)
        if calc != mf.sha256:
            raise RuntimeError(f"Hash mismatch for {src_name}: got {calc}, want {mf.sha256}")

        # decompress if needed; write to staging with target filename
        target = _target_name(src_name)
        out_path = staging / target
        out_path.parent.mkdir(parents=True, exist_ok=True)
        content = _decompress_if_needed(raw, src_name)
        with open(out_path, "wb") as f:
            f.write(content)
        downloaded.append(target)

    # 5) sanity: ensure expected keys exist
    missing = [n for n in TARGET_FILENAMES if n not in downloaded]
    if missing:
        LOG.warning("Snapshot missing optional files: %s", ", ".join(missing))

    # 6) atomic swap
    tmp_old = data_root / f".db.old.{int(time.time())}"
    if db_root.exists():
        db_root.rename(tmp_old)
    staging.rename(db_root)
    if tmp_old.exists():
        shutil.rmtree(tmp_old, ignore_errors=True)

    # write receipt
    (db_root / "manifest.json").write_bytes(manifest_b)

    return {
        "mirror": used_mirror,
        "version": man.version,
        "files": downloaded,
    }


