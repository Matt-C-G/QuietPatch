# QuietPatch Windows Build Guide

This guide walks you through building QuietPatch v0.4.0 on Windows.

## Prerequisites

### Required Software
- **Windows 11 x64** (or Windows 10 21H2+)
- **Python 3.12 x64** - Download from [python.org](https://www.python.org/downloads/)
- **Inno Setup 6** - Download from [jrsoftware.org](https://jrsoftware.org/isdl.php)
- **7-Zip** - For creating portable CLI archives
- **Minisign** - For signing release artifacts

### Quick Setup (Automated)
Run as Administrator:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\setup-prereqs.ps1
```

### Manual Setup
1. Install Python 3.12 from python.org (check "Add to PATH")
2. Install Inno Setup 6 from jrsoftware.org
3. Install 7-Zip from 7-zip.org
4. Install Minisign from [GitHub releases](https://github.com/jedisct1/minisign/releases)

## Building

### Option 1: Automated Build (Recommended)
```cmd
build-windows.bat
```

### Option 2: Manual PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\build-release.ps1
```

### Option 3: Step-by-Step Manual
```powershell
# 1. Setup environment
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:PIP_ONLY_BINARY=":all:"
pip install --upgrade pip wheel
pip install pyinstaller==6.6.0 cryptography==42.0.7
pip install -r requirements.txt

# 2. Build executables
pyinstaller build\quietpatch_wizard_win.spec
pyinstaller build\quietpatch_cli_win.spec

# 3. Create installer
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\windows\QuietPatch.iss

# 4. Create portable CLI
7z a release\quietpatch-cli-v0.4.0-win64.zip .\dist\quietpatch\*

# 5. Generate checksums
cd release
Get-ChildItem -File | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    "$hash *$($_.Name)" | Add-Content SHA256SUMS.txt
}

# 6. Sign checksums
minisign -Sm SHA256SUMS.txt -s ..\keys\quietpatch.key
```

## Output

The build process creates:
- `release\QuietPatch-Setup-v0.4.0.exe` - Windows installer
- `release\quietpatch-cli-v0.4.0-win64.zip` - Portable CLI
- `release\SHA256SUMS.txt` - Checksums
- `release\SHA256SUMS.txt.minisig` - Signature
- `release\README-QuickStart.md` - User guide
- `release\VERIFY.md` - Verification instructions

## Testing

### Installer Test
1. Run `QuietPatch-Setup-v0.4.0.exe`
2. Expect SmartScreen warning → "More info" → "Run anyway"
3. Complete installation
4. Launch QuietPatch from Start Menu
5. Run a scan, verify report opens

### Portable CLI Test
1. Extract `quietpatch-cli-v0.4.0-win64.zip`
2. Run `quietpatch.exe --help`
3. Run `quietpatch.exe scan --report .`
4. Verify HTML report is generated

## Troubleshooting

### Python Issues
- Ensure Python 3.12 is installed and in PATH
- Use `py -3.12` instead of `python` if needed
- Check virtual environment activation

### PyInstaller Issues
- Ensure all dependencies are installed
- Check for missing hidden imports
- Verify spec file paths are correct

### Inno Setup Issues
- Ensure Inno Setup 6 is installed
- Check installer script paths
- Verify output directory permissions

### Minisign Issues
- Ensure minisign is in PATH
- Check key file exists at `keys\quietpatch.key`
- Verify public key matches

## Publishing

1. Upload artifacts to GitHub Release
2. Update landing page download links
3. Test on clean Windows VM
4. Share with users

## Support

For issues:
1. Check this guide first
2. Review build logs
3. Test on clean Windows VM
4. Open GitHub issue with details
