"""Database state management with epoch and rollback protection"""

import json
import time
from pathlib import Path
from typing import Dict, Any


def get_state_file() -> Path:
    """Get the path to the state file."""
    return Path.home() / ".quietpatch" / "state.json"


def read_state() -> Dict[str, Any]:
    """Read the current database state."""
    state_file = get_state_file()
    try:
        return json.loads(state_file.read_text())
    except Exception:
        return {"last_date": "", "epoch": 0, "ts": 0}


def write_state(date: str, epoch: int) -> None:
    """Write the new database state."""
    state_file = get_state_file()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    state = {
        "last_date": date,
        "epoch": epoch,
        "ts": int(time.time())
    }
    
    state_file.write_text(json.dumps(state, indent=2))


def check_epoch_protection(new_epoch: int, allow_downgrade: bool = False) -> None:
    """Check if the new epoch is valid (prevents downgrade attacks)."""
    current_state = read_state()
    current_epoch = current_state.get("epoch", 0)
    
    if new_epoch < current_epoch:
        if allow_downgrade:
            print(f"[DB-EPOCH] Downgrade allowed: {current_epoch} -> {new_epoch}")
        else:
            raise SystemExit(f"[DB-EPOCH] Catalog epoch decreased ({current_epoch} -> {new_epoch}). Refusing downgrade.")


def check_rollback_protection(new_date: str, allow_downgrade: bool = False) -> None:
    """Check if the new date is valid (prevents rollback attacks)."""
    current_state = read_state()
    current_date = current_state.get("last_date", "")
    
    if new_date <= current_date and not allow_downgrade:
        raise SystemExit(f"[DB-ROLLBACK] Snapshot older or equal to installed ({current_date} >= {new_date}). Refusing rollback.")


def update_state(new_date: str, new_epoch: int) -> None:
    """Update the state after successful verification and extraction."""
    write_state(new_date, new_epoch)
    print(f"✅ Database state updated: epoch {new_epoch}, date {new_date}")


def get_state_info() -> Dict[str, Any]:
    """Get current state information for display."""
    state = read_state()
    return {
        "last_date": state.get("last_date", "never"),
        "epoch": state.get("epoch", 0),
        "last_update": state.get("ts", 0)
    }
