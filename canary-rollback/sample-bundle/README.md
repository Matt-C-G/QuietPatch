# Sample Bundle - Placeholder Artifacts

This directory contains placeholder files to demonstrate the bundle structure. In a real deployment, these would be replaced with actual installer packages.

## Windows Artifacts
- `7zip-23.01-x64.msi` - 7-Zip 23.01 installer (placeholder)
- `7zip-22.01-x64.msi` - 7-Zip 22.01 installer for rollback (placeholder)

## macOS Artifacts  
- `iterm2-3.5.12.pkg` - iTerm2 3.5.12 installer (placeholder)
- `iterm2-3.5.10.pkg` - iTerm2 3.5.10 installer for rollback (placeholder)

## Linux Artifacts
- `vscode_1.93.1_amd64.deb` - VS Code 1.93.1 Debian package (placeholder)
- `vscode_1.91.0_amd64.deb` - VS Code 1.91.0 Debian package for rollback (placeholder)

## Usage

1. Replace placeholder files with actual installer packages
2. Update SHA256 hashes in `manifest.json`
3. Test detection scripts to verify current versions
4. Deploy using your chosen orchestration tool

## Security Note

All artifacts should be:
- Downloaded from official vendor sources
- Verified against published checksums
- Signed with your organization's code signing certificate
- SHA256 hashed and recorded in the manifest
