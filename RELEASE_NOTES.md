# QuietPatch v0.3.0 Release Notes

## Downloads
- **Windows (Python 3.11 required)**: `quietpatch-windows-x64.zip`
- **Linux x86_64 (Python 3.11 required)**: `quietpatch-linux-x86_64.zip`
- **macOS arm64 (Python 3.11 required)**: `quietpatch-macos-arm64.zip`

## Verify
See `VERIFY.md`, `SHA256SUMS`, and `SHA256SUMS.minisig`. Public key: `<YOUR_PUBLIC_KEY>`.

## What's New
- Enhanced HTML report UI with severity badges, stats banner, accessibility
- New `doctor` command to diagnose environment and provide fixes
- Package manager install paths (Homebrew, Scoop)
- Refactored README and docs site with improved design and content
- Policies presets and JSON export module docs

## Installation & Usage

### Windows
1. Install Python 3.11 (64-bit)
2. Extract the Windows ZIP
3. Double-click `run_quietpatch.bat`
4. View report at `.\nreports\quietpatch_report.html`

### Linux
1. Install Python 3.11
2. Extract the Linux ZIP
3. Run: `chmod +x run_quietpatch.sh && ./run_quietpatch.sh scan`
4. View report at `./reports/quietpatch_report.html`

### macOS
1. Install Python 3.11 (`brew install python@3.11`)
2. Extract the macOS ZIP
3. Double-click `run_quietpatch.command`
4. View report at `./reports/quietpatch_report.html`

## Notes
- Offline by default. No telemetry or network communication required.
- Report location: `./reports/quietpatch_report.html`
- Windows path-length errors: Always launch via `run_quietpatch.bat` to avoid WinError 206.
- Security: All builds are reproducible and include SHA256 checksums for verification.

## Technical Details
- Built with Python 3.11 and PEX for maximum compatibility
- Uses local CVE database for offline operation
- Includes comprehensive vulnerability metadata (CVSS, KEV, EPSS)
- Deterministic builds ensure reproducible results

## Support
For issues, feature requests, or questions, please visit the [GitHub repository](https://github.com/Matt-C-G/QuietPatch).

