from src.core.rollback import snapshot_system_state, run_canary
import json
from pathlib import Path

def test_snapshot_and_canary(tmp_path, monkeypatch):
    # Mock the _get_snapshot_file function to return our test path
    from src.core import rollback
    monkeypatch.setattr(rollback, "_get_snapshot_file", lambda: tmp_path / ".quietpatch" / "snapshot.json")
    
    apps = [{"app": "Example", "version": "1.0"}]
    digest = snapshot_system_state(apps)
    assert (tmp_path / ".quietpatch" / "snapshot.json").exists()

    result = run_canary(apps)
    assert "OK" in result
