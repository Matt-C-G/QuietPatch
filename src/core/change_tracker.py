from __future__ import annotations
from pathlib import Path
import json, os
from src.config.encryptor_v3 import encrypt_file

def compute_changes(outdir: Path) -> str | None:
    apps_path = outdir / "apps.json"
    prev_path = outdir / "apps_prev.json"
    if not apps_path.exists():
        return None

    try:
        apps = json.loads(apps_path.read_text())
    except Exception:
        return None

    try:
        prev = json.loads(prev_path.read_text()) if prev_path.exists() else []
    except Exception:
        prev = []

    def kv(lst):
        return {(a.get("app") or a.get("name") or ""): (a.get("version") or "") for a in lst}

    prev_map = kv(prev)
    curr_map = kv(apps)

    added   = sorted([a for a in curr_map if a and a not in prev_map])
    removed = sorted([a for a in prev_map if a and a not in curr_map])
    changed = sorted([a for a in curr_map if a in prev_map and curr_map[a] != prev_map[a]])

    changes = {
        "added":   added,
        "removed": removed,
        "changed": [{"app": a, "from": prev_map[a], "to": curr_map[a]} for a in changed],
    }

    changes_path = outdir / "changes.json"
    changes_path.write_text(json.dumps(changes, indent=2))
    prev_path.write_text(json.dumps(apps, indent=2))

    recipients = [r.strip() for r in os.environ.get("QP_AGE_RECIPIENTS","").split(",") if r.strip()]
    include_keychain = os.environ.get("QP_INCLUDE_KEYCHAIN_WRAP","0") == "1"
    enc_path = outdir / "changes.json.enc"
    encrypt_file(changes_path, enc_path, age_recipients=recipients, include_keychain_wrap=include_keychain)
    return str(enc_path)
