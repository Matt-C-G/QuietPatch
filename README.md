# QuietPatch 🔐

![version](https://img.shields.io/badge/version-v0.4.2-blue.svg)
[![CI](https://github.com/Matt-C-G/QuietPatch/actions/workflows/ci.yml/badge.svg)](https://github.com/Matt-C-G/QuietPatch/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Privacy-first vulnerability scanner.  
> Runs fully offline, cross-platform (macOS · Linux · Windows), produces a clean HTML report with clear remediation steps.  
> No telemetry · No auto-patching · Deterministic results.

---

## 🚀 Quick Start

**Supported Python:** 3.11–3.12 (3.13 not yet)

**Install:**
```bash
python -m pip install quietpatch==0.4.2
quietpatch env doctor
quietpatch db fetch
quietpatch scan --offline --html
```

**Verified install (security-conscious):**
```bash
# Download and verify checksums
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/SHA256SUMS
shasum -a 256 -c SHA256SUMS

# Install with binary-only mode
python -m pip install quietpatch==0.4.2 --only-binary :all:
```

> **⚠️ If install fails:** Use Python 3.12 (`brew install python@3.12` / Winget 'Python 3.12'). We do not support 3.13 yet.

## 📥 Downloads

Prebuilt wheels and source tarball are attached to the **[v0.4.2 release](../../releases/tag/v0.4.2)**.

Typical asset names:
- `quietpatch-0.4.2-py3-none-any.whl` (pure)
- `quietpatch-0.4.2-cp312-*-manylinux*.whl` (Linux)
- `quietpatch-0.4.2-cp312-*-macosx*.whl` (macOS)
- `quietpatch-0.4.2-cp312-*-win_amd64.whl` (Windows)
- `quietpatch-0.4.2.tar.gz` (sdist)

> Use `pip install <asset-url>` if you prefer installing directly from an asset.

---

## 📦 Alternative Install Methods

**One-command installers:**

macOS / Linux
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.sh)"
```

Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.ps1 | iex
```

**Package managers:**

macOS (Homebrew)
```bash
brew tap matt-c-g/quietpatch && brew install quietpatch
```

Windows (Scoop)
```powershell
scoop bucket add quietpatch https://github.com/Matt-C-G/scoop-quietpatch
scoop install quietpatch
```

**Standalone executables:**
Download from [Releases](https://github.com/Matt-C-G/QuietPatch/releases) - no Python required.

**Docker (Alpine/containerized):**
```bash
# Pull and run
docker run --rm -v "$HOME/.quietpatch:/root/.quietpatch" ghcr.io/matt-c-g/quietpatch:latest env doctor
docker run --rm -v "$HOME/.quietpatch:/root/.quietpatch" ghcr.io/matt-c-g/quietpatch:latest scan --offline --html

# Or build locally
docker build -t quietpatch .
docker run --rm -v "$HOME/.quietpatch:/root/.quietpatch" quietpatch scan --offline --html
```

---

## ✨ What You Get

* 📦 Inventory of apps & versions
* 🛡️ CVEs with severity badges (Critical/High/Medium/Low)
* 🚨 KEV + EPSS flagged clearly
* 🔧 Concrete remediation commands (copy-to-clipboard)
* 📑 Deterministic, reproducible report for audits

<p align="center">
  <img src="docs/assets/screenshot-report.svg" alt="QuietPatch Report Preview" width="820"/>
</p>

---

## 🔒 Why QuietPatch?

* **Privacy-first**: No telemetry. The app never sends data. Nightly jobs run on our infra against our test images only.
* **Offline-first**: signed CVE DB snapshot; nothing leaves your machine
* **No surprises**: never auto-patches, all fixes are suggestions
* **Cross-platform**: works the same on macOS, Linux, and Windows
* **Enterprise-ready**: systemd / launchd / Task Scheduler templates

---

## ⚙️ Advanced Options

* Policies: tune results with ready-made presets

  ```bash
  quietpatch scan --policy policies/policy-critical-only.yml
  ```
* JSON export: machine-readable for SIEM/ticketing

  ```bash
  quietpatch scan --json-out report.json
  ```
* Doctor: diagnose environment and provide fixes

  ```bash
  quietpatch doctor --open-check
  ```
* Recurring scans: use included service templates (systemd/launchd/Task Scheduler)

---

## 🛠️ For Developers

```bash
git clone https://github.com/Matt-C-G/QuietPatch.git
cd QuietPatch
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

---

## 📄 License & Data

* License: [MIT](LICENSE)
* Data sources: [NVD](https://nvd.nist.gov/), [CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog), [FIRST EPSS](https://www.first.org/epss/)

## 🔄 Version Support Policy

**We support exactly two CPython minor versions:**
- **Current**: Python 3.11, 3.12
- **Next**: Python 3.12, 3.13 (when 3.13 support is added)
- **Deprecated**: None currently
- **End of life**: Python 3.10 and below, 3.14 and above

**Policy:**
- New versions added only after thorough testing with wheels + constraints
- Old versions deprecated when new ones are added
- Python 3.13 support will be added in a future release
- See [SUPPORT_MATRIX.md](SUPPORT_MATRIX.md) for full details

## 🔐 Security & Integrity

**Database Security:**
- All catalogs are minisign-verified before extraction
- Path traversal protection prevents `../` attacks
- Downgrade protection blocks rollback attacks
- Epoch-based versioning ensures monotonic updates

**Platform Support:**
- Alpine not supported; use Docker image
- Two Python minors supported (3.11/3.12)
- No telemetry; diagnostics bundle is local-only and opt-in

**Supply Chain:**
- Cryptographic verification with Minisign signatures
- Binary-only installation option for security-conscious users
- Deterministic reports with content hashing
- Automated security testing in CI/CD

---

## 🔧 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "Requires Python ≥3.11" | Using 3.9/3.10/3.13 | Install 3.12; re-run install |
| "zstandard not found" | Env resolved wrong dep | `python -m pip install "zstandard>=0.22,<0.23"` |
| "DB not found (offline)" | No catalog downloaded | `quietpatch db fetch` |
| Gatekeeper blocks (macOS) | Unsigned | `xattr -dr com.apple.quarantine /path/to/python /usr/local/bin/quietpatch` |
| SARIF empty in CI | Wrong path | Ensure `--sarif out.sarif` and upload step |

**Quick diagnosis:**
```bash
quietpatch env doctor  # Shows exact fix commands
```

## 🔑 Verify Downloads

```bash
shasum -a 256 -c SHA256SUMS
```

Optional: verify Minisign signatures (VERIFY.md).

Windows Authenticode
```powershell
Get-AuthenticodeSignature .\quietpatch-windows-x64.exe | Format-List Status, StatusMessage, SignerCertificate, TimeStamperCertificate
# Expect Status: Valid
```

macOS notarization
```bash
spctl --assess -vv quietpatch-macos-arm64.zip   # Expect: accepted
xcrun stapler validate quietpatch-macos-arm64.zip  # Expect: The validate action worked!
```

---

## 🙏 Thanks

QuietPatch builds on the open-source security ecosystem.
Thanks to early testers and contributors for shaping the tool.
