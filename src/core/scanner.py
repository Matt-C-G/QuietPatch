import os
import sys
import subprocess
import json


# Add project root to sys.path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def scan_mac_applications():
    """
    Scans the /Applications directory on macOS for installed apps
    and retrieves their version information using 'mdls'.
    """
    apps_dir = "/Applications"
    apps = []

    for entry in os.listdir(apps_dir):
        if entry.endswith(".app"):
            app_path = os.path.join(apps_dir, entry)
            version = get_app_version(app_path)
            apps.append({
                "name": entry.replace(".app", ""),
                "path": app_path,
                "version": version or "Unknown"
            })

    return apps

def get_app_version(app_path):
    """
    Uses macOS 'mdls' command to get app version metadata.
    """
    try:
        result = subprocess.run(
            ["mdls", "-name", "kMDItemVersion", app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        output = result.stdout.strip()
        if "=" in output:
            return output.split("=")[1].strip().strip('"')
    except Exception:
        return None
    return None

if __name__ == "__main__":
    print("🔍 Scanning installed applications...\n")
    apps = scan_mac_applications()

    for app in apps:
        print(f"{app['name']} - {app['version']}")

    # Output JSON
    output_path = "data/scan_results.json"
    try:
        with open(output_path, "w") as f:
            json.dump(apps, f, indent=2)
        print(f"\n✅ Scan results saved to {output_path}")
    except Exception as e:
        print(f"\n❌ Failed to write scan results: {e}")
    # Encrypt JSON file
    from src.config.encryptor import encrypt_file

    encrypted_path = "data/scan_results.json.enc"
    encrypt_file(output_path, encrypted_path)
