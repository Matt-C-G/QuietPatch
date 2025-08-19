import os, json, platform, shutil, tempfile, stat, subprocess
from pathlib import Path
import pytest

AGE = shutil.which("age")
PLUGIN = shutil.which("age-plugin-ssh") or shutil.which("age")  # plugin is bundled on some installs
pytestmark = pytest.mark.skipif(not AGE, reason="age CLI not installed")

from src.config.encryptor_v3 import encrypt_file, decrypt_file

def gen_age_identity(tmp: Path):
    ident = tmp / "id.agekey"
    recip = tmp / "id.pub"
    # pure-age identity
    subprocess.run(["age-keygen", "-o", str(ident)], check=True, capture_output=True)
    out = subprocess.check_output(["age-keygen", "-y", str(ident)])
    recip.write_bytes(out)
    return str(ident), str(recip)

def test_v3_roundtrip_and_perms(tmp_path: Path):
    ident, recip = gen_age_identity(tmp_path)
    plain = tmp_path / "v.json"
    enc = tmp_path / "v.json.enc"
    plain.write_text(json.dumps({"ok": True}))

    encrypt_file(plain, enc, age_recipients=[recip], include_keychain_wrap=False)
    # v3 envelope & perms 0600 (skip strict on Windows)
    text = enc.read_text()
    assert text.startswith('{"v":3,')
    if platform.system() != "Windows":
        mode = stat.S_IMODE(os.stat(enc).st_mode)
        assert mode == 0o600

    # decrypt via identity
    raw = decrypt_file(enc, age_identities=[ident], allow_keychain=False)
    assert json.loads(raw.decode()) == {"ok": True}

def test_multi_wrap_prefers_age(tmp_path: Path, monkeypatch):
    ident, recip = gen_age_identity(tmp_path)
    p = tmp_path / "v.json"; e = tmp_path / "v.json.enc"
    p.write_text('{"x":1}')
    # include a keychain wrap if v2 is present (won't be used)
    encrypt_file(p, e, age_recipients=[recip], include_keychain_wrap=True)
    raw = decrypt_file(e, age_identities=[ident], allow_keychain=True)
    assert json.loads(raw.decode()) == {"x":1}
