# scanner.py
import os
import platform
import subprocess


def scan_installed_apps():
    os_name = platform.system()
    if os_name == "Darwin":
        return scan_mac_applications()
    elif os_name == "Windows":
        return scan_windows_programs()
    elif os_name == "Linux":
        return scan_linux_packages()
    else:
        print("❌ Unsupported OS for scanning.")
        return []


def scan_mac_applications():
    apps = []
    app_dir = "/Applications"
    for app in os.listdir(app_dir):
        if app.endswith(".app"):
            name = app.replace(".app", "")
            version = "N/A"
            apps.append({"name": name, "version": version})
    return apps


def scan_windows_programs():
    apps = []
    try:
        output = subprocess.check_output(
            ["powershell", "Get-ItemProperty", "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",
             "| Select-Object DisplayName, DisplayVersion"],
            stderr=subprocess.DEVNULL
        ).decode(errors="ignore")

        for line in output.splitlines():
            if "DisplayName" in line:
                name = line.split(":")[-1].strip()
            elif "DisplayVersion" in line:
                version = line.split(":")[-1].strip()
                apps.append({"name": name, "version": version})
    except Exception as e:
        print(f"⚠️ Windows scan failed: {e}")
    return apps


def scan_linux_packages():
    apps = []
    try:
        output = subprocess.check_output(["dpkg-query", "-W", "-f=${Package} ${Version}\n"]).decode()
        for line in output.strip().split("\n"):
            parts = line.split()
            if len(parts) == 2:
                apps.append({"name": parts[0], "version": parts[1]})
    except Exception:
        try:
            output = subprocess.check_output(["rpm", "-qa", "--qf", "%{NAME} %{VERSION}\n"]).decode()
            for line in output.strip().split("\n"):
                parts = line.split()
                if len(parts) == 2:
                    apps.append({"name": parts[0], "version": parts[1]})
        except Exception as e:
            print(f"⚠️ Linux scan failed: {e}")
    return apps
