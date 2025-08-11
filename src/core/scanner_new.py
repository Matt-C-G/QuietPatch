# scanner_new.py
from __future__ import annotations
import sys, os, platform, subprocess, json, re
from pathlib import Path
from typing import List, Dict, Tuple

App = Dict[str, str]

def _run(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def scan_macos() -> List[App]:
    apps = []
    apps_dir = Path("/Applications")
    if not apps_dir.exists():
        return apps
    for app in apps_dir.glob("*.app"):
        code, out, err = _run(["mdls", "-name", "kMDItemVersion", str(app)])
        ver = None
        if code == 0:
            m = re.search(r'"?kMDItemVersion"?\s*=\s*"?(.*?)"?\n', out) or re.search(r'=(.*)', out)
            if m:
                ver = m.group(1).strip().strip('"')
        apps.append({"app": app.stem, "version": ver or "unknown"})
    return apps

def scan_windows() -> List[App]:
    apps = []
    # Query Uninstall registry via powershell for Name/DisplayVersion
    ps = ["powershell", "-NoProfile", "-Command",
          "Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* ,"
          "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | "
          "Select-Object DisplayName, DisplayVersion | ConvertTo-Json -Compress"]
    code, out, err = _run(ps)
    if code == 0 and out.strip():
        try:
            data = json.loads(out)
            if isinstance(data, dict): data=[data]
            for d in data:
                name = (d.get('DisplayName') or '').strip()
                ver = (d.get('DisplayVersion') or '').strip() or 'unknown'
                if name:
                    apps.append({"app": name, "version": ver})
        except Exception:
            pass
    return apps

def scan_linux() -> List[App]:
    apps=[]
    # dpkg-based
    code, out, err = _run(["bash","-lc","command -v dpkg >/dev/null 2>&1 && dpkg-query -W -f='${Package} ${Version}\n' || true"])
    if out:
        for line in out.splitlines():
            try:
                name, ver = line.split(" ", 1)
                apps.append({"app": name, "version": ver})
            except ValueError:
                continue
    # rpm-based
    code, out, err = _run(["bash","-lc","command -v rpm >/dev/null 2>&1 && rpm -qa --qf '%{NAME} %{VERSION}-%{RELEASE}\n' || true"])
    if out:
        for line in out.splitlines():
            try:
                name, ver = line.split(" ", 1)
                apps.append({"app": name, "version": ver})
            except ValueError:
                continue
    return apps

def scan_installed() -> List[App]:
    sysname = platform.system()
    if sysname == "Darwin":
        return scan_macos()
    if sysname == "Windows":
        return scan_windows()
    return scan_linux()
