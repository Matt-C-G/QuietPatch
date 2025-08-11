# cve_mapper.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import requests
import json
import time
from src.config.encryptor import get_or_create_key
from cryptography.fernet import Fernet
from src.config.encryptor import encrypt_file, decrypt_file
from difflib import get_close_matches
from src.core.scanner import scan_installed_apps

VULN_LOG_ENC = "data/vuln_log.json.enc"
SETTINGS_ENC = "src/config/settings.json.enc"
NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# Load API key from encrypted settings
try:
    settings = decrypt_file(SETTINGS_ENC)
    NVD_API_KEY = settings.get("nvd_api_key", "")
except Exception as e:
    print(f"❌ Failed to load API key: {e}")
    NVD_API_KEY = ""

if not NVD_API_KEY:
    print("🔒 No NVD API key found.")
    print("🧪 Launching QuietPatch Lite — limited mode with 5 lookups every 30 seconds.")

HEADERS = {
    "User-Agent": "QuietPatch/1.0"
}
if NVD_API_KEY:
    HEADERS["apiKey"] = NVD_API_KEY

# Efficient keyword normalization
def normalize_keyword(app_name):
    known_map = {
        "google chrome": "chrome",
        "microsoft word": "word",
        "visual studio code": "vscode",
        "adobe acrobat": "acrobat",
        "zoom": "zoom",
        "vlc": "vlc",
        "firefox": "firefox",
        "safari": "safari",
        "outlook": "outlook"
    }
    name = app_name.lower()
    if name in known_map:
        return known_map[name]
    match = get_close_matches(name, known_map.keys(), n=1, cutoff=0.6)
    if match:
        return known_map[match[0]]
    return name.split()[0]  # fallback

def is_common_keyword(keyword):
    return len(keyword) > 3 and keyword.isalpha()

def parse_cves(data):
    results = []
    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        summary = next((d.get("value", "") for d in cve.get("descriptions", []) if d.get("lang") == "en"), "")
        score = cve.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore", 0)
        results.append({
            "id": cve.get("id", ""),
            "summary": summary,
            "cvss": score
        })
    return results

def fetch_cves(keyword, max_results=20, retries=3):
    params = {
        "keywordSearch": keyword,
        "resultsPerPage": max_results,
        "cvssV3Severity": "HIGH"
    }
    for attempt in range(retries):
        response = requests.get(NVD_API, params=params, headers=HEADERS)

        if response.status_code == 200:
            try:
                return parse_cves(response.json())
            except Exception as e:
                print(f"❌ JSON error for '{keyword}': {e}")
                return []
        elif response.status_code == 429:
            print(f"⏳ Rate limited on '{keyword}' — retrying in 5s...")
            time.sleep(5)
        elif response.status_code == 403:
            print(f"❌ Forbidden (403) on '{keyword}' — possible bad or missing API key")
            break
        else:
            print(f"❌ Error {response.status_code} for '{keyword}'")
            break

    return []

def correlate(app_data, additional_apps=None):
    results = []
    count = 0
    last_reset = time.time()

    if additional_apps:
        app_data.extend(additional_apps)
    for app in app_data:
        if not NVD_API_KEY:
            # Allow 5 lookups every 30 seconds
            if count >= 5:
                elapsed = time.time() - last_reset
                if elapsed < 30:
                    wait_time = 30 - elapsed
                    print(f"⏳ Waiting {int(wait_time)}s to continue in demo mode...")
                    time.sleep(wait_time)
                count = 0
                last_reset = time.time()

        keyword = normalize_keyword(app["name"])
        print(f"🔑 Searching CVEs for '{app['name']}' using keyword: '{keyword}'")
        cves = fetch_cves(keyword)
        count += 1

        for cve in cves:
            results.append({
                "app": app["name"],
                "version": app["version"],
                "vulnerability": cve["summary"],
                "resolved": False
            })

    return results

def save_encrypted_vuln_log(vuln_data):
    key = get_or_create_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps(vuln_data).encode())
    with open(VULN_LOG_ENC, "wb") as f:
        f.write(encrypted)
    print(f"🔐 Encrypted vuln log saved to {VULN_LOG_ENC}")

def load_vuln_log():
    if not os.path.exists(VULN_LOG_ENC):
        return []
    try:
        return decrypt_file(VULN_LOG_ENC)
    except Exception as e:
        print(f"Failed to decrypt vuln log: {e}")
        return []

def purge_resolved(apps, vuln_log):
    current_versions = {app["name"]: app["version"] for app in apps}
    filtered = []
    for entry in vuln_log:
        app_name = entry["app"]
        if app_name not in current_versions:
            continue
        if current_versions[app_name] == entry["version"]:
            filtered.append(entry)
    return filtered

if __name__ == "__main__":
    print("🔍 Running CVE correlation...\n")

    apps = scan_installed_apps()
    if not apps:
        print("⚠️ No applications detected. Check OS-specific scanner logic.")

    old_vulns = load_vuln_log()
    new_vulns = correlate(apps)

    all_vulns = purge_resolved(apps, old_vulns + new_vulns)
    save_encrypted_vuln_log(all_vulns)

    for vuln in all_vulns:
        print(f"⚠️ {vuln['app']} {vuln['version']} is vulnerable to: {vuln['vulnerability']}")