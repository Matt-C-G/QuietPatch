import subprocess
from pathlib import Path


def _scan_dpkg():
    try:
        output = subprocess.check_output(["dpkg", "-l"], text=True)
    except Exception:
        return []
    apps = []
    for line in output.splitlines()[5:]:
        parts = line.split()
        if len(parts) >= 3:
            apps.append({"app": parts[1], "version": parts[2]})
    return apps


def _scan_rpm():
    try:
        output = subprocess.check_output(["rpm", "-qa", "--queryformat", "%{NAME} %{VERSION}\n"], text=True)
    except Exception:
        return []
    apps = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 2:
            apps.append({"app": parts[0], "version": parts[1]})
    return apps


def _scan_usr_bin():
    apps = []
    bin_dir = Path("/usr/bin")
    if not bin_dir.exists():
        return apps
    for p in bin_dir.iterdir():
        if p.is_file():
            apps.append({"app": p.name, "version": ""})
    return apps


def collect_installed_apps():
    results = _scan_dpkg() + _scan_rpm() + _scan_usr_bin()
    dedup = { (e["app"], e.get("version")): e for e in results }
    return list(dedup.values())
