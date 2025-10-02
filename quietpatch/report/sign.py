from __future__ import annotations
import shutil, subprocess, tempfile, os, json

def minisign_available() -> bool:
    return shutil.which("minisign") is not None

def sign_file(path: str, key_path: str, comment: str = "") -> str:
    """
    Returns .minisig path. Requires minisign installed and a private key file.
    """
    if not minisign_available():
        raise RuntimeError("minisign not found on PATH")
    sig_path = path + ".minisig"
    # -s secret key, -Sm sign and create .minisig, -c comment
    cmd = ["minisign", "-s", key_path, "-Sm", path]
    if comment:
        cmd.extend(["-c", comment])
    subprocess.run(cmd, check=True)
    return sig_path
