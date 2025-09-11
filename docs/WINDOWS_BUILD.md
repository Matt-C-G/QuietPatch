# Windows Build Guide

## Overview

This guide covers building QuietPatch v0.4.0 for Windows using the automated ship-gate system.

## Prerequisites

### Required Tools
- **Python 3.12**: Install from [python.org](https://www.python.org/downloads/windows/)
- **Inno Setup 6**: Install from [jrsoftware.org](https://jrsoftware.org/isinfo.php)
- **Minisign**: Install via `choco install minisign` or download from [jedisct1/minisign](https://github.com/jedisct1/minisign)

### Optional Tools
- **7-Zip**: For better compression (falls back to PowerShell if missing)
- **GitHub CLI**: For uploading to releases (`gh` command)

## Quick Build

```powershell
# Set execution policy (one-time)
Set-ExecutionPolicy -Scope Process RemoteSigned

# Run complete build pipeline
.\scripts\windows\ship-gate.ps1 -Version 0.4.0 -PublicKey 'RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR' -DoInstallSmoke:$true
```

## What the Ship-Gate Does

1. **Environment Check**: Verifies Python 3.12, Inno Setup, minisign
2. **Build Pipeline**: Runs `Makefile.ps1 all` to build everything
3. **Artifact Verification**: Checks file presence and sizes
4. **Signature Verification**: Validates minisign signature and SHA256 checksums
5. **Smoke Test**: (Optional) Silent install/uninstall test
6. **Upload**: (Optional) Uploads to GitHub release

## Build Artifacts

The build produces:
- `QuietPatch-Setup-v0.4.0.exe` - Windows installer (Inno Setup)
- `quietpatch-cli-v0.4.0-win64.zip` - Portable CLI binary
- `SHA256SUMS.txt` - File checksums
- `SHA256SUMS.txt.minisig` - Minisign signature
- `README-QuickStart.txt` - User instructions

## Troubleshooting

### Python 3.12 Not Found
```powershell
# Verify Python installation
py -3.12 -V
# Should show: Python 3.12.x
```

### Inno Setup Path Issues
Update the path in `ship-gate.ps1`:
```powershell
$Iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

### Minisign Key Mismatch
Ensure the public key matches your signing key:
```powershell
# Check your public key
cat keys\quietpatch.pub
```

### SHA256 Mismatch
Re-run the checksum generation:
```powershell
.\Makefile.ps1 checksums -Version 0.4.0
.\Makefile.ps1 sign -Version 0.4.0
```

## Manual Build Steps

If you need to run individual steps:

```powershell
# 1. Setup environment
.\Makefile.ps1 setup -Version 0.4.0

# 2. Build binaries
.\Makefile.ps1 build -Version 0.4.0

# 3. Package installer
.\Makefile.ps1 package -Version 0.4.0

# 4. Generate checksums
.\Makefile.ps1 checksums -Version 0.4.0

# 5. Sign checksums
.\Makefile.ps1 sign -Version 0.4.0
```

## Testing

### Silent Install Test
```powershell
# Test installer silently
.\scripts\windows\ship-gate.ps1 -Version 0.4.0 -PublicKey 'RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR' -DoInstallSmoke:$true
```

### Manual Testing
1. Run installer normally
2. Verify GUI launches: `C:\Program Files\QuietPatch\QuietPatchWizard.exe`
3. Verify CLI works: `C:\Program Files\QuietPatch\quietpatch.exe --help`
4. Test scan functionality
5. Uninstall via Control Panel

## Release Process

1. **Build**: Run ship-gate with smoke test
2. **Upload**: Add `-GhUpload` flag to upload to GitHub
3. **Verify**: Download from release and verify signatures
4. **Test**: Test on clean Windows VM

## Security Notes

- All artifacts are signed with minisign
- SHA256 checksums prevent tampering
- Installer includes uninstaller
- No telemetry or data collection
- Runs completely offline

## Support

For build issues:
1. Check prerequisites are installed
2. Verify Python 3.12 is available
3. Check Inno Setup path
4. Verify minisign key matches
5. Open GitHub issue with error details
