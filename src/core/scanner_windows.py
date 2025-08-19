import subprocess
import json
import tempfile
from pathlib import Path


def _exec(cmd, shell=False):
    try:
        return subprocess.check_output(cmd, text=True, shell=shell)
    except Exception:
        return ""


def _scan_wmic():
    output = _exec(['wmic', 'product', 'get', 'Name,Version'])
    apps = []
    for line in output.splitlines()[1:]:
        if '  ' in line:
            name, version = line.rsplit('  ', 1)
            apps.append({"app": name.strip(), "version": version.strip()})
    return apps


def _scan_appx():
    ps_cmd = 'Get-AppxPackage | Select-Object -Property Name,Version | ConvertTo-Json'
    output = _exec(["powershell", "-Command", ps_cmd])
    apps = []
    try:
        data = json.loads(output)
        for entry in data:
            apps.append({"app": entry["Name"], "version": entry["Version"]})
    except Exception:
        pass
    return apps


def _scan_winget():
    output = _exec(['winget', 'list'])
    apps = []
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 3:
            # assume last item is version
            version = parts[-1]
            name = " ".join(parts[:-1])
            apps.append({"app": name.strip(), "version": version.strip()})
    return apps


def collect_installed_apps() -> list[dict]:
    results = []
    results.extend(_scan_wmic())
    results.extend(_scan_appx())
    results.extend(_scan_winget())
    # dedup
    seen = set()
    dedup = []
    for e in results:
        key = (e["app"], e.get("version"))
        if key not in seen:
            seen.add(key)
            dedup.append(e)
    return dedup
