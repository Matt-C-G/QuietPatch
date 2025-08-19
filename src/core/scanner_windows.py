import subprocess
import json


def _scan_wmic():
    try:
        output = subprocess.check_output(['wmic', 'product', 'get', 'Name,Version'], text=True)
    except Exception:
        return []
    apps = []
    for line in output.splitlines()[1:]:
        if '  ' in line:
            name, version = line.rsplit('  ', 1)
            apps.append({"app": name.strip(), "version": version.strip()})
    return apps


def _scan_appx():
    ps_cmd = 'Get-AppxPackage | Select-Object Name,Version | ConvertTo-Json'
    try:
        output = subprocess.check_output(["powershell", "-Command", ps_cmd], text=True)
        data = json.loads(output)
    except Exception:
        return []
    return [{"app": e["Name"], "version": e["Version"]} for e in data]


def _scan_winget():
    try:
        output = subprocess.check_output(['winget', 'list'], text=True)
    except Exception:
        return []
    apps = []
    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            version = parts[-1]
            name = " ".join(parts[:-1])
            apps.append({"app": name.strip(), "version": version.strip()})
    return apps


def collect_installed_apps():
    results = _scan_wmic() + _scan_appx() + _scan_winget()
    dedup = {(e["app"], e.get("version")): e for e in results}
    return list(dedup.values())
