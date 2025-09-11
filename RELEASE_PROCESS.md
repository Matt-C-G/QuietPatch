# QuietPatch v0.4.0 Release Process

This document outlines the complete process for creating a download-ready release of QuietPatch v0.4.0.

## Overview

The release process creates user-friendly installers for all platforms:
- **Windows**: Inno Setup installer (.exe) + portable CLI
- **macOS**: DMG package (.dmg) + portable CLI  
- **Linux**: AppImage (.AppImage) + portable CLI

All releases are signed with minisign and include verification instructions.

## Prerequisites

### Required Tools
- Python 3.12+
- PyInstaller
- Platform-specific packaging tools:
  - **Windows**: Inno Setup 6
  - **macOS**: create-dmg (via Homebrew)
  - **Linux**: appimagetool

### GitHub Setup
1. Generate minisign key pair: `./scripts/generate_keys.sh`
2. Add private key to GitHub secrets as `MINISIGN_SECRET_KEY_B64`
3. Update `VERIFY.md` with the public key

## Build Process

### 1. Local Testing
```bash
# Test the build process
python build_all.py

# Test the GUI
python gui/wizard.py

# Test the CLI
python qp_cli.py --help
```

### 2. Platform-Specific Packaging

#### Windows
```bash
# Install Inno Setup (via Chocolatey)
choco install innosetup

# Build installer
"C:/Program Files (x86)/Inno Setup 6/ISCC.exe" installer/windows/QuietPatch.iss
```

#### macOS
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
./packaging/macos/create_dmg.sh
```

#### Linux
```bash
# Install dependencies
sudo apt-get install libfuse2 wget

# Create AppImage
./packaging/linux/create_appimage.sh
```

### 3. Automated Release (GitHub Actions)

The `.github/workflows/release.yml` workflow automatically:
1. Builds PyInstaller binaries for all platforms
2. Creates platform-specific packages
3. Generates SHA256 checksums
4. Signs checksums with minisign
5. Uploads all artifacts to GitHub Releases

#### Triggering a Release
```bash
# Create and push a tag
git tag v0.4.0
git push origin v0.4.0

# Or use the manual workflow dispatch
# Go to Actions → Build & Release QuietPatch v0.4.0 → Run workflow
```

## Release Artifacts

Each release includes:

### Common Files
- `SHA256SUMS.txt` - SHA256 checksums of all files
- `SHA256SUMS.txt.minisig` - Minisign signature of checksums
- `VERIFY.md` - Verification instructions
- `LICENSE.txt` - Software license
- `README-QuickStart.md` - End-user quick start guide

### Platform-Specific Files

#### Windows
- `QuietPatch-Setup-v0.4.0.exe` - Inno Setup installer
- `quietpatch-cli-v0.4.0-win64.zip` - Portable CLI

#### macOS
- `QuietPatch-v0.4.0.dmg` - DMG package
- `quietpatch-cli-v0.4.0-macos-universal.tar.gz` - Portable CLI

#### Linux
- `QuietPatch-v0.4.0-x86_64.AppImage` - AppImage package
- `quietpatch-cli-v0.4.0-linux-x86_64.tar.gz` - Portable CLI

## Verification Process

Users can verify downloads using:

1. **SHA256 Checksum**: Compare file hash with `SHA256SUMS.txt`
2. **Minisign Signature**: Verify `SHA256SUMS.txt` is authentic
3. **Platform-specific**: Handle unsigned binary warnings

See `VERIFY.md` for detailed instructions.

## GitHub Pages

The `docs/index.html` provides a landing page with:
- Three prominent download buttons
- Feature highlights
- Privacy guarantees
- Links to verification and documentation

## Troubleshooting

### Common Issues

1. **PyInstaller fails**: Check dependencies and hidden imports
2. **Packaging fails**: Verify platform-specific tools are installed
3. **Signing fails**: Check minisign key is properly configured
4. **Upload fails**: Verify GitHub token permissions

### Testing Checklist

- [ ] GUI launches and shows wizard interface
- [ ] CLI responds to --help
- [ ] Scan process works end-to-end
- [ ] Report generation works
- [ ] Installers work on target platforms
- [ ] Verification process works for users

## Security Notes

- Private keys are stored in GitHub secrets
- All releases are signed with minisign
- No telemetry or data collection
- Offline operation by default
- Reproducible builds

## Future Improvements

- Code signing certificates for Windows/macOS
- Notarization for macOS
- Auto-update mechanism
- Additional Linux package formats (deb, rpm)
- Windows Store submission
