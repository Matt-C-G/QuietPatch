---
title: QuietPatch
layout: default
---

<h1>QuietPatch 🔐</h1>
<p>Privacy-first vulnerability scanner with deterministic HTML reports and actionable remediation. Runs fully offline.</p>

## Install

**macOS / Linux**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.sh)"
```

**Windows (PowerShell)**

```powershell
irm https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.ps1 | iex
```

Or via package managers:

* **Homebrew**

```bash
brew tap matt-c-g/quietpatch && brew install quietpatch
```

* **Scoop**

```powershell
scoop bucket add quietpatch https://github.com/Matt-C-G/scoop-quietpatch
scoop install quietpatch
```

<section id="downloads" style="margin:2rem 0;">
  <h2>Download QuietPatch v0.4.0</h2>
  <p>Private, offline scan. No telemetry. First run on macOS: <b>Right-click → Open → Open</b>.</p>

  <div style="display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));align-items:start">

    <!-- macOS -->
    <div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;">
      <h3 style="margin:0 0 8px;">macOS</h3>
      <a href="https://github.com/Matt-C-G/QuietPatch/releases/download/v0.4.0/QuietPatch-v0.4.0.zip"
         style="display:inline-block;padding:10px 14px;border-radius:10px;background:#111;color:#fff;text-decoration:none;">
        Download for macOS (.zip)
      </a>
      <div style="margin-top:8px;font-size:14px;line-height:1.5;">
        <a href="https://github.com/Matt-C-G/QuietPatch/releases/download/v0.4.0/quietpatch-cli-v0.4.0-macos-universal.tar.gz">
          Portable CLI (tar.gz)
        </a>
      </div>
    </div>

    <!-- Windows -->
    <div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;">
      <h3 style="margin:0 0 8px;">Windows</h3>
      <a href="https://github.com/Matt-C-G/QuietPatch/releases/download/v0.4.0/QuietPatch-Setup-v0.4.0.exe"
         style="display:inline-block;padding:10px 14px;border-radius:10px;background:#111;color:#fff;text-decoration:none;">
        Download for Windows (.exe)
      </a>
      <div style="margin-top:8px;font-size:14px;line-height:1.5;">
        <a href="https://github.com/Matt-C-G/QuietPatch/releases/download/v0.4.0/quietpatch-cli-v0.4.0-win64.zip">
          Portable CLI (zip)
        </a>
      </div>
    </div>

    <!-- Linux -->
    <div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;">
      <h3 style="margin:0 0 8px;">Linux</h3>
      <a href="https://github.com/Matt-C-G/QuietPatch/releases/download/v0.4.0/QuietPatch-v0.4.0-x86_64.AppImage"
         style="display:inline-block;padding:10px 14px;border-radius:10px;background:#111;color:#fff;text-decoration:none;">
        Download for Linux (AppImage)
      </a>
      <div style="margin-top:8px;font-size:14px;line-height:1.5;">
        <a href="https://github.com/Matt-C-G/QuietPatch/releases/download/v0.4.0/quietpatch-cli-v0.4.0-linux-x86_64.tar.gz">
          Portable CLI (tar.gz)
        </a>
      </div>
    </div>
  </div>

  <!-- Verify -->
  <div style="margin-top:18px;padding:12px;border:1px solid #e5e7eb;border-radius:12px;background:#fafafa;">
    <strong>Verify your download</strong> —
    <a href="https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/VERIFY.md">Read VERIFY.md</a> ·
    <a href="https://github.com/Matt-C-G/QuietPatch/releases/download/v0.4.0/SHA256SUMS.txt">SHA256SUMS.txt</a> ·
    <a href="https://github.com/Matt-C-G/QuietPatch/releases/download/v0.4.0/SHA256SUMS.txt.minisig">SHA256SUMS.txt.minisig</a>
    <pre style="margin:10px 0 0;white-space:pre-wrap;font-size:12px;background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:10px;">
# Verify signature (replace with your public key from VERIFY.md)
minisign -Vm SHA256SUMS.txt -P "RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR"
# Verify checksums
shasum -a 256 -c SHA256SUMS.txt
    </pre>
  </div>

  <!-- Privacy blurb -->
  <p style="margin-top:12px;color:#475569;font-size:14px;">
    100% offline by default. No telemetry. Signed catalog. Deterministic report.
  </p>
</section>

## Quickstart

```bash
quietpatch scan --db ./qp_db-latest.tar.zst --also-report --open
```

The report opens in your browser with app inventory, CVEs (KEV, CVSS, EPSS), and concrete remediation steps.

## Verify

Always verify downloads:

```bash
shasum -a 256 -c SHA256SUMS
```

See <code>VERIFY.md</code> for minisign signature verification.

---

<p align="center">
  <img src="assets/screenshot-report.png" alt="QuietPatch Report" width="820" />
  </p>

