from __future__ import annotations

import json
import os
import secrets
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Optional v2 fallback (Keychain)
try:
    from src.config.encryptor_v2 import decrypt_to_bytes as _v2_decrypt_to_bytes
    from src.crypto.key_provider import get_backend as _get_backend

    _HAS_V2 = True
except Exception:
    _HAS_V2 = False
    _get_backend = None  # type: ignore


class DecryptError(Exception):
    pass


class EncryptError(Exception):
    pass


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    try:
        path.chmod(0o600)
    except Exception:
        pass


def _age_wrap(dek: bytes, recipients: Iterable[str]) -> bytes:
    recs = [r for r in recipients if r]
    if not recs:
        raise EncryptError("No age recipients provided")

    # First try SSH-recipient mode
    cmd = ["age"] + sum([["-r", r] for r in recs], []) + ["-a", "-o", "-"]
    try:
        p = subprocess.run(cmd, input=dek, capture_output=True, check=True)
        return p.stdout
    except subprocess.CalledProcessError:
        raise EncryptError(
            "age wrap failed: see age stderr for details"
        ) from None
    except FileNotFoundError as e:
        raise EncryptError("age CLI not found. Install age + age-plugin-ssh.") from e


def _age_unwrap(armored: bytes, identities: Iterable[str]) -> bytes:
    ids = [i for i in identities if i]
    if not ids:
        raise DecryptError("No age identities provided")
    cmd = ["age", "-d"] + sum([["-i", i] for i in ids], []) + ["-o", "-"]
    try:
        p = subprocess.run(cmd, input=armored, capture_output=True, check=True)
    except FileNotFoundError as e:
        raise DecryptError("age CLI not found. Install age + age-plugin-ssh.") from e
    except subprocess.CalledProcessError as e:
        raise DecryptError(
            f"age unwrap failed: {e.stderr.decode(errors='replace')[:200]}"
        ) from e
    return p.stdout


def encrypt_bytes(
    plain: bytes, age_recipients: Iterable[str] | None = None, include_keychain_wrap: bool = False
) -> dict[str, Any]:
    dek = secrets.token_bytes(32)
    aead = AESGCM(dek)
    iv = secrets.token_bytes(12)
    ct = aead.encrypt(iv, plain, None)

    wraps: list[dict[str, Any]] = []
    env_recip = [r for r in os.environ.get("QP_AGE_RECIPIENTS", "").split(",") if r.strip()]
    recipients = list(age_recipients or env_recip)
    if recipients:
        armored = _age_wrap(dek, recipients).decode("utf-8")
        wraps.append({"type": "age-ssh", "armored": armored})
    if include_keychain_wrap:
        if not _HAS_V2:
            # don't fail the whole encryption; just skip the wrap
            pass
        else:
            try:
                kek = _get_backend().get_or_create_kek()  # type: ignore
                iv2 = secrets.token_bytes(12)
                ct2 = AESGCM(kek).encrypt(iv2, dek, None)
                wraps.append(
                    {"type": "keychain", "alg": "AES-256-GCM", "iv": iv2.hex(), "ct": ct2.hex()}
                )
            except Exception:
                # log-and-continue; hardware recipients still make the envelope valid
                # (optionally: record a note for debugging)
                wraps.append({"type": "note", "keychain_wrap": "failed"})
                # or simply: pass
    if not wraps:
        raise EncryptError("No wraps configured. Provide --age-recipient or enable keychain wrap.")
    return {"v": 3, "alg": "AES-256-GCM", "iv": iv.hex(), "ct": ct.hex(), "wraps": wraps}


def decrypt_to_bytes_v3(
    env: dict[str, Any], *, age_identities: Iterable[str] | None = None, allow_keychain: bool = True
) -> bytes:
    if env.get("v") != 3:
        raise DecryptError("Unsupported envelope")
    dek: bytes | None = None
    ids_env = [i for i in os.environ.get("QP_AGE_IDENTITIES", "").split(",") if i.strip()]
    ids = list(age_identities or ids_env)
    if ids:
        for w in env.get("wraps", []):
            if w.get("type") == "age-ssh":
                try:
                    dek = _age_unwrap(w["armored"].encode(), ids)
                    break
                except Exception:
                    pass
    if dek is None and allow_keychain and _HAS_V2:
        for w in env.get("wraps", []):
            if w.get("type") == "keychain":
                try:
                    kek = _get_backend().get_or_create_kek()  # type: ignore
                    dek = AESGCM(kek).decrypt(bytes.fromhex(w["iv"]), bytes.fromhex(w["ct"]), None)
                    break
                except Exception:
                    pass
    if dek is None:
        raise DecryptError("No usable wrap; provide --age-identity or enable keychain")
    return AESGCM(dek).decrypt(bytes.fromhex(env["iv"]), bytes.fromhex(env["ct"]), None)


def encrypt_file(
    plain_path: Path,
    enc_path: Path,
    *,
    age_recipients: Iterable[str] | None = None,
    include_keychain_wrap: bool = False,
) -> None:
    env = encrypt_bytes(
        plain_path.read_bytes(),
        age_recipients=age_recipients,
        include_keychain_wrap=include_keychain_wrap,
    )
    _atomic_write(enc_path, json.dumps(env).encode())


def decrypt_file(
    enc_path: Path, *, age_identities: Iterable[str] | None = None, allow_keychain: bool = True
) -> bytes:
    t = enc_path.read_text().strip()
    if not t:
        raise DecryptError(f"Empty encrypted file: {enc_path}")
    try:
        env = json.loads(t)
    except json.JSONDecodeError:
        if _HAS_V2:
            try:
                return _v2_decrypt_to_bytes(json.loads(t))
            except Exception:
                pass
        raise DecryptError("Unknown/legacy envelope; regenerate with v3")
    if env.get("v") == 3:
        return decrypt_to_bytes_v3(
            env, age_identities=age_identities, allow_keychain=allow_keychain
        )
    if _HAS_V2:
        return _v2_decrypt_to_bytes(env)
    raise DecryptError("Unsupported envelope and no v2 fallback")
