# QuietPatch Windows Build & Release

## Quick Start

```powershell
# One-command build (Windows 11 x64)
.\Makefile.ps1 all
```

## Prerequisites

- **Python 3.12 x64** from [python.org](https://www.python.org/downloads/)
- **Inno Setup 6** from [jrsoftware.org](https://jrsoftware.org/isdl.php)
- **Minisign** (`choco install minisign`)
- **7-Zip** (optional, falls back to PowerShell)

## Build Commands

```powershell
.\Makefile.ps1 all           # Full build: setup → build → package → sign
.\Makefile.ps1 setup         # Just environment setup
.\Makefile.ps1 build         # Just PyInstaller builds
.\Makefile.ps1 package       # Just Inno Setup + portable ZIP
.\Makefile.ps1 checksums     # Generate SHA256SUMS.txt
.\Makefile.ps1 sign          # Sign with minisign
.\Makefile.ps1 release       # Create GitHub release (needs gh CLI)
.\Makefile.ps1 clean         # Clean all build artifacts
```

## Output

After `.\Makefile.ps1 all`:

```
release/
├── QuietPatch-Setup-v0.4.0.exe          # Windows installer
├── quietpatch-cli-v0.4.0-win64.zip      # Portable CLI
├── SHA256SUMS.txt                        # Checksums
├── SHA256SUMS.txt.minisig               # Minisign signature
├── README-QuickStart.txt                 # User guide
└── VERIFY.md                            # Verification instructions
```

## Testing

### Installer Test
1. Run `QuietPatch-Setup-v0.4.0.exe`
2. Expect SmartScreen → "More info" → "Run anyway"
3. Complete installation
4. Check Start Menu for shortcuts:
   - **QuietPatch** (main app)
   - **QuietPatch CLI** (command line)
   - **QuickStart Guide** (opens in Notepad)
   - **Verify Download** (opens VERIFY.md)

### Portable CLI Test
1. Extract `quietpatch-cli-v0.4.0-win64.zip`
2. Run `quietpatch.exe --help`
3. Run `quietpatch.exe scan --report .`
4. Check `README-QuickStart.txt` is included

## Publishing

### Option 1: GitHub CLI
```powershell
.\Makefile.ps1 release
```

### Option 2: Manual Upload
1. Go to GitHub → Releases → Draft new release
2. Tag: `v0.4.0`
3. Upload all files from `release/`
4. Publish

## Troubleshooting

### Python Issues
- Ensure Python 3.12 is installed and in PATH
- Use `py -3.12` if `python` doesn't work
- Check virtual environment activation

### PyInstaller Issues
- Ensure all dependencies are installed
- Check spec file paths are correct
- Verify no missing hidden imports

### Inno Setup Issues
- Ensure Inno Setup 6 is installed
- Check installer script paths
- Verify output directory permissions

### Minisign Issues
- Ensure minisign is in PATH
- Check key file exists at `keys\quietpatch.key`
- Verify public key matches

## File Structure

```
QuietPatch/
├── Makefile.ps1                    # Main build script
├── README-QuickStart.txt           # User guide
├── installer/windows/QuietPatch.iss # Inno Setup script
├── build/
│   ├── quietpatch_wizard_win.spec  # GUI PyInstaller spec
│   └── quietpatch_cli_win.spec     # CLI PyInstaller spec
├── keys/
│   └── quietpatch.key              # Minisign secret key
└── release/                        # Build output
```

## Notes

- The script uses `PIP_ONLY_BINARY=":all:"` to avoid compilation issues
- PyInstaller specs are Windows-optimized with proper icons
- Inno Setup creates a full Windows installer with Start Menu shortcuts
- Portable CLI includes QuickStart guide and verification instructions
- All artifacts are signed with minisign for verification
