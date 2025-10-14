# QuietPatch 

Privacy-first vulnerability scanner with deterministic reports.

##  Install

**macOS/Linux**
```bash
/bin/bash -c "$(curl -fsSL https://quietpatch.dev/install.sh)"
```

**Windows (PowerShell)**
```powershell
irm https://quietpatch.dev/install.ps1 | iex
```

[Read the docs →](https://github.com/Matt-C-G/QuietPatch)

##  Features

- ** Offline-First**: Works without internet after initial setup
- **️ Privacy-Focused**: No telemetry, no data collection
- ** Rich Reports**: Beautiful HTML reports with CVSS scores and remediation steps
- ** Cross-Platform**: Single-file executables for Windows, macOS, and Linux

##  Quick Start

```bash
# Install
curl -fsSL https://quietpatch.dev/install.sh | bash

# Scan
quietpatch scan --also-report --open

# Check version
quietpatch --version

# Clean cache
quietpatch clean --cache
```

##  Package Managers

**Homebrew (macOS/Linux)**
```bash
brew tap matt-c-g/quietpatch && brew install quietpatch
```

**Scoop (Windows)**
```powershell
scoop bucket add quietpatch https://github.com/Matt-C-G/scoop-quietpatch
scoop install quietpatch
```

##  Links

- [GitHub Repository](https://github.com/Matt-C-G/QuietPatch)
- [Latest Releases](https://github.com/Matt-C-G/QuietPatch/releases)
- [Installation Guide](https://github.com/Matt-C-G/QuietPatch/blob/main/INSTALL.md)
- [Report Issues](https://github.com/Matt-C-G/QuietPatch/issues)
