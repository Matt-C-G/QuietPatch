# QuietPatch 🔐

[![CI](https://github.com/Matt-C-G/QuietPatch/actions/workflows/ci.yml/badge.svg)](https://github.com/Matt-C-G/QuietPatch/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🚀 Latest Release: QuietPatch v0.3.0

> Privacy-first vulnerability scanner.  
> Runs fully offline, cross-platform (macOS · Linux · Windows), produces a clean HTML report with clear remediation steps.  
> No telemetry · No auto-patching · Deterministic results.

---

## 🚀 Quick Start (30 seconds)

1. Install

   macOS / Linux
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.sh)"
   ```

   Windows (PowerShell)
   ```powershell
   irm https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.ps1 | iex
   ```

   Manual download (latest):
   - macOS: https://github.com/Matt-C-G/quietpatch-dist/releases/latest/download/quietpatch-macos-arm64-latest.zip
   - Linux: https://github.com/Matt-C-G/quietpatch-dist/releases/latest/download/quietpatch-linux-x86_64-latest.zip
   - Windows: https://github.com/Matt-C-G/quietpatch-dist/releases/latest/download/quietpatch-windows-x64-latest.zip
   - Offline DB: https://github.com/Matt-C-G/quietpatch-dist/releases/latest/download/db-latest.tar.zst

   Or via package managers

   macOS (Homebrew)
   ```bash
   brew tap matt-c-g/quietpatch && brew install quietpatch
   ```

   Windows (Scoop)
   ```powershell
   scoop bucket add quietpatch https://github.com/Matt-C-G/scoop-quietpatch
   scoop install quietpatch
   ```

   Windows (no Python needed)
   ```powershell
   # Download quietpatch-windows-x64.exe from the latest Release
   # Then run a scan directly
   .\quietpatch-windows-x64.exe scan --also-report --open
   ```

2. Run a scan

   ```bash
   quietpatch scan --also-report --open
   ```

3. View results
   Report (report.html) opens automatically in your browser.

That’s it ✅

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

* Offline-first: signed CVE DB snapshot; nothing leaves your machine
* No surprises: never auto-patches, all fixes are suggestions
* Cross-platform: works the same on macOS, Linux, and Windows
* Enterprise-ready: systemd / launchd / Task Scheduler templates

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

---

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

## 🧰 Troubleshooting

**macOS**
- If the app is blocked by Gatekeeper, run: `xattr -cr ~/.quietpatch/bin/*`

**PATH**
- If `quietpatch` is not found, add: `export PATH="$HOME/.quietpatch/bin:$PATH"`

**Windows**
- Open a new PowerShell after install to pick up PATH changes.

**Offline DB**
- Provide `db-latest.tar.zst` alongside the binary; run with `--db <path>` or set `QP_OFFLINE=1`.

---

## 🙏 Thanks

QuietPatch builds on the open-source security ecosystem.
Thanks to early testers and contributors for shaping the tool.
