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

## Quickstart

```bash
quietpatch scan --db ./db-latest.tar.zst --also-report --open
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

