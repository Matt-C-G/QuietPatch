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


def _get_snapshot_file():
    return Path.home() / ".quietpatch" / "snapshot.json"


def snapshot_system_state(app_list):
    """
    Capture deterministic hash of installed applications.
    """
    snapshot_file = _get_snapshot_file()
    snapshot_file.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(app_list, sort_keys=True).encode()
    digest = hashlib.sha256(data).hexdigest()
    snapshot_file.write_text(json.dumps({"digest": digest}))
    return digest


def run_canary(app_list):
    snapshot_file = _get_snapshot_file()
    if not snapshot_file.exists():
        return "No snapshot found – run snapshot_system_state() first."
    snapshot = json.loads(snapshot_file.read_text())
    current_digest = hashlib.sha256(json.dumps(app_list, sort_keys=True).encode()).hexdigest()
    if snapshot.get("digest") == current_digest:
        return "✅ Canary OK – system state unchanged."
    return "⚠️ Canary WARNING – state changed since last snapshot."


def rollback_last_checkpoint():
    return "Rollback stub invoked (no changes made)."
