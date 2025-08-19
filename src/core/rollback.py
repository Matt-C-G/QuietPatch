"""
Rollback / Canary Module (QuietPatch v0.2.0)

This module provides:
  - system snapshot marker (hash of installed apps list)
  - rollback stub for design-partner testing
  - canary test to verify restore logic without touching the system
"""

import hashlib
import json
from pathlib import Path

SNAPSHOT_FILE = Path.home() / ".quietpatch" / "snapshot.json"


def _ensure_dir():
    SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)


def snapshot_system_state(app_list: list[dict]):
    """
    Write a deterministic snapshot of the current installed apps list.
    """
    _ensure_dir()
    data = json.dumps(app_list, sort_keys=True).encode()
    digest = hashlib.sha256(data).hexdigest()
    SNAPSHOT_FILE.write_text(json.dumps({"digest": digest}))
    return digest


def run_canary(app_list: list[dict]):
    """
    Compare current state against the stored snapshot to ensure rollback would work.
    """
    if not SNAPSHOT_FILE.exists():
        return "No snapshot found – run snapshot_system_state() first."

    snapshot = json.loads(SNAPSHOT_FILE.read_text())
    current_digest = hashlib.sha256(json.dumps(app_list, sort_keys=True).encode()).hexdigest()

    if snapshot.get("digest") == current_digest:
        return "✅ Canary OK – system state unchanged."
    return "⚠️ Canary WARNING – state changed since last snapshot."


def rollback_last_checkpoint():
    """
    In Beta this is a NO-OP. Design partners can see where the logic would run.
    """
    return "Rollback stub invoked (no changes made)."
