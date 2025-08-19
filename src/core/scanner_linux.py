import subprocess
import os
from pathlib import Path


def _exec(cmd):
    try:
        return subprocess.check_output(cmd, text=True)
    except Exception:
        return ""


def _scan_dpkg():
    output = _exec(["dpkg", "-l"])
    apps = []
    for line in output.splitlines()[5:]:
        parts = line.split()
        if len(parts) >= 3:
            apps.append({"app": parts[1], "version": parts[2]})
    return apps


def _scan_rpm():
    output = _exec(["rpm", "-qa", "--queryformat", "%{NAME} %{VERSION}\n"])
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
    for path in bin_dir.iterdir():
        if path.is_file():
            apps.append({"app": path.name, "version": ""})
    return apps


def collect_installed_apps() -> list[dict]:
    """
    Linux scanner with dpkg + rpm + unmanaged binaries.
    Returns list of {'app': name, 'version': version}.
    """
    results = []
    results.extend(_scan_dpkg())
    results.extend(_scan_rpm())
    results.extend(_scan_usr_bin())
    # remove duplicates
    seen = set()
    dedup = []
    for entry in results:
        key = (entry["app"], entry.get("version"))
        if key not in seen:
            seen.add(key)
            dedup.append(entry)
    return dedup
