# src/core/actions.py
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Fallback defaults keyed by either app name or vendor:product
_DEFAULT_ACTIONS = {
    "Safari": "softwareupdate -l && sudo softwareupdate -ia",
    "apple:safari": "softwareupdate -l && sudo softwareupdate -ia",
    "Microsoft Word": '"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --apps WORD',
    "microsoft:word": '"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --apps WORD',
    "Microsoft Excel": '"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --apps XCEL',
    "microsoft:excel": '"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --apps XCEL',
    "Microsoft PowerPoint": '"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --apps PPT3',
    "microsoft:powerpoint": '"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --apps PPT3',
    "Zoom": "brew upgrade --cask zoom || brew install --cask zoom",
    "zoom:zoom": "brew upgrade --cask zoom || brew install --cask zoom",
    "Wireshark": "brew upgrade --cask wireshark || brew install --cask wireshark",
    "wireshark:wireshark": "brew upgrade --cask wireshark || brew install --cask wireshark",
    "Firefox": "brew upgrade --cask firefox || brew install --cask firefox",
    "mozilla:firefox": "brew upgrade --cask firefox || brew install --cask firefox",
    "OpenVPN Connect": "brew upgrade --cask openvpn-connect || brew install --cask openvpn-connect",
    "openvpn:connect": "brew upgrade --cask openvpn-connect || brew install --cask openvpn-connect",
    "Numbers": "softwareupdate -l && sudo softwareupdate -ia",
    "Pages": "softwareupdate -l && sudo softwareupdate -ia",
    "Keynote": "softwareupdate -l && sudo softwareupdate -ia",
    "OneDrive": '"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --apps ONDR',
    "microsoft:onedrive": '"/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate" --install --apps ONDR',
    "Discord": "open https://discord.com/download",
    "discord:discord": "open https://discord.com/download",
    "PDFgear": "open https://pdfgear.com/download",
    "pdfgear:pdfgear": "open https://pdfgear.com/download",
    "Raycast": "brew upgrade --cask raycast || brew install --cask raycast",
    "raycast:raycast": "brew upgrade --cask raycast || brew install --cask raycast",
    # Fallback generic
    "__generic__": "Open the app → Check built-in updater or vendor site for updates.",
}


def load_actions(path: Path | None) -> dict[str, str]:
    try:
        if path and path.exists():
            data = yaml.safe_load(path.read_text()) or {}
            if isinstance(data, dict):
                # Merge file over defaults so users can override
                return {**_DEFAULT_ACTIONS, **data}
    except Exception:
        pass
    return dict(_DEFAULT_ACTIONS)


def _lookup_action(app: dict[str, Any], actions: dict[str, str]) -> str:
    # Try by CPE first if present
    cpe = (app.get("cpe") or "").lower()
    if cpe:
        # cpe:2.3:a:vendor:product:version:...
        parts = cpe.split(":")
        if len(parts) >= 5:
            key = f"{parts[3]}:{parts[4]}"  # vendor:product
            if key in actions:
                return actions[key]
    # Try by App name
    name = str(app.get("app") or app.get("name") or "").strip()
    if name and name in actions:
        return actions[name]
    return actions.get("__generic__", "")


def decorate_actions(
    apps: list[dict[str, Any]], actions_map: dict[str, str]
) -> list[dict[str, Any]]:
    out = []
    for a in apps:
        a2 = dict(a)
        a2["actions"] = [_lookup_action(a, actions_map)] if actions_map else []
        out.append(a2)
    return out
