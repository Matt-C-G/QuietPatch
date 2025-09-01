# encryptor_new.py
from __future__ import annotations

import os
from pathlib import Path

from cryptography.fernet import Fernet

DEFAULT_KEY_PATH = Path(
    os.environ.get("QUIETPATCH_KEY_PATH", Path.home() / ".quietpatch" / "key.key")
)


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def generate_key() -> bytes:
    return Fernet.generate_key()


def get_or_create_key(path: Path | None = None) -> bytes:
    key_path = Path(path) if path else DEFAULT_KEY_PATH
    if key_path.exists():
        return key_path.read_bytes()
    _ensure_parent(key_path)
    key = generate_key()
    key_path.write_bytes(key)
    try:
        os.chmod(key_path, 0o600)
    except Exception:
        pass
    return key


def encrypt_bytes(data: bytes, key: bytes | None = None) -> bytes:
    key = key or get_or_create_key()
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_bytes(data: bytes, key: bytes | None = None) -> bytes:
    key = key or get_or_create_key()
    f = Fernet(key)
    return f.decrypt(data)


def encrypt_file(input_path: str | os.PathLike, output_path: str | os.PathLike) -> str:
    key = get_or_create_key()
    raw = Path(input_path).read_bytes()
    enc = encrypt_bytes(raw, key)
    op = Path(output_path)
    _ensure_parent(op)
    op.write_bytes(enc)
    return str(op)


def decrypt_file(input_path: str | os.PathLike) -> bytes:
    key = get_or_create_key()
    enc = Path(input_path).read_bytes()
    dec = decrypt_bytes(enc, key)
    return dec
