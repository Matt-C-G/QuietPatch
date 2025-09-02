# QuietPatch 🔐

QuietPatch is a lightweight, privacy-first vulnerability scanner with an **action engine** and **policy engine**.  
It maps the software on a host to known CVEs and produces a clean, searchable **HTML report with actionable remediation**.  

- **Offline-first** · Runs without internet access (signed CVE DB snapshots)  
- **Cross-platform** · Single-file runner for macOS, Linux, Windows  
- **Enterprise-friendly** · Systemd / launchd / Task Scheduler templates included  
- **Secure by design** · No telemetry, no auto-patching, deterministic output  

---

## 🚀 Quick Install

### macOS & Linux
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.sh)"
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.ps1 | iex
```

### Package Managers

* **Homebrew** (macOS/Linux)
  ```bash
  brew tap matt-c-g/quietpatch && brew install quietpatch
  ```
* **Scoop** (Windows)
  ```powershell
  scoop bucket add quietpatch https://github.com/Matt-C-G/scoop-quietpatch
  scoop install quietpatch
  ```

---

## ✨ Highlights

* **Offline-first**: Encrypted, signed CVE DB snapshot – zero network calls
* **Action engine**: Per-app remediation (brew, MAU, vendor links, package managers)
* **Policy engine**: Severity filters, treat-unknown-as, KEV/EPSS sorting
* **Cross-platform runners**: Single-file PEX builds
* **Security**: SBOM, encrypted config, no secrets in repo

---

## 🧪 Usage

Run a scan with the offline DB:

```bash
quietpatch scan --db ./db-20250902.tar.zst --also-report --open
```

The report (`report.html`) will open in your browser and includes:

* Apps + versions
* CVEs (KEV badge, CVSS, EPSS)
* Remediation commands
* Deterministic ordering for stable results

---

## ⚙️ Policy Example (`config/policy.yml`)

```yaml
allow: []
deny: []
min_severity: medium      # low | medium | high | critical
treat_unknown_as: low     # map "unknown" to this floor
only_with_cves: true      # drop apps with no CVEs
limit_per_app: 50
```

---

## 🔒 Security & Privacy

* Offline DB (recommended for production)
* No auto-patching; all remediation is human-approved
* Deterministic reports with reproducible builds
* SBOM (`sbom.spdx.json`) and third-party notices included

---

## 🖥️ Service Install (Optional)

Schedule recurring scans with provided templates:

* **macOS**: `/Library/LaunchDaemons/com.quietpatch.agent.plist`
* **Linux**: `/etc/systemd/system/quietpatch.service`
* **Windows**: Task Scheduler XML

---

## 🛠️ Development

```bash
git clone https://github.com/Matt-C-G/QuietPatch.git
cd QuietPatch
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

---

## 📄 License & Acknowledgments

* **License**: MIT
* **Data sources**: [NVD](https://nvd.nist.gov/), [CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog), [FIRST EPSS](https://www.first.org/epss/)

---

## 🔑 Verify

Always verify your downloads:

```bash
shasum -a 256 -c SHA256SUMS
```

Optional: verify signed checksums with Minisign (`VERIFY.md`).

---

## 🙏 Thanks

QuietPatch builds on the open-source security ecosystem.
Special thanks to contributors and early design partners for testing and feedback.