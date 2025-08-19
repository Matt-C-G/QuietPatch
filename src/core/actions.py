# src/core/actions.py
from __future__ import annotations
from typing import Dict, List, Optional

def suggest_actions(app_name: str, cpe: Optional[str], version: Optional[str]) -> List[Dict[str, str]]:
    """
    Return prioritized remediation actions for a given app.
    Each action: {"type": "...", "cmd": "..."} or {"type": "...", "url": "...", "note": "..."}
    """
    n = (app_name or "").lower()
    c = (cpe or "").lower()
    out: List[Dict[str, str]] = []

    # 1) Homebrew caskable common apps
    # (heuristic; we don't require brew to be installed—command is a safe suggestion)
    casks = {
        "zoom.us": "zoom",
        "zoom": "zoom",
        "wireshark": "wireshark",
        "firefox": "firefox",
        "iterm": "iterm2",
        "webex": "webex",
        "openvpn connect": "openvpn-connect",
    }
    for k, v in casks.items():
        if k in n:
            out.append({
                "type": "upgrade",
                "cmd": f'brew upgrade --cask {v} || brew install --cask {v}',
                "note": "Requires Homebrew."
            })
            break

    # 2) Microsoft apps via AutoUpdate (broad update, safe default)
    if "microsoft" in c or any(x in n for x in ["word", "excel", "powerpoint", "onedrive", "teams"]):
        out.append({
            "type": "update",
            "cmd": r'"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --all',
            "note": "Runs Microsoft AutoUpdate for all Office apps."
        })

    # 3) Apple system apps (Safari etc.) -> Software Update
    if "apple:safari" in c or "safari" in n:
        out.append({
            "type": "update",
            "cmd": "softwareupdate -l && sudo softwareupdate -ia",
            "note": "Safari updates ship with macOS."
        })

    # 4) OpenVPN fallback (direct download)
    if "openvpn" in c or "openvpn" in n:
        out.append({
            "type": "upgrade",
            "url": "https://openvpn.net/client",
            "note": "Download latest OpenVPN Connect."
        })

    # 5) Battle.net
    if "battle.net" in n or "blizzard:battle.net" in c:
        out.append({
            "type": "upgrade",
            "url": "https://www.blizzard.com/en-us/apps/battle.net/desktop",
            "note": "Install/Update via Blizzard installer."
        })

    # 6) Generic fallback
    if not out:
        out.append({
            "type": "investigate",
            "note": "Open the app and check its built-in updater or vendor site."
        })

    return out
