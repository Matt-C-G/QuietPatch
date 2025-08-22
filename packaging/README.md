# QuietPatch Packaging

This directory contains platform-specific packaging scripts and configurations for QuietPatch.

## macOS (.pkg + launchd)

### Quick Start

1. **Build the package:**
   ```bash
   # Ensure you have a built zipapp
   bash tools/build_pyz.sh
   
   # Copy to payload
   cp dist/quietpatch.pyz packaging/macos/payload/usr/local/quietpatch/
   
   # Build package
   cd packaging/macos && ./mkpkg.sh 0.2.1
   ```

2. **Install locally:**
   ```bash
   sudo installer -pkg packaging/macos/quietpatch-0.2.1.pkg -target /
   ```

3. **Test the service:**
   ```bash
   # Check status
   sudo launchctl list | grep quietpatch
   
   # Force a run
   sudo launchctl kickstart -k system/com.quietpatch.agent
   
   # View logs
   sudo tail -f /var/log/quietpatch.out /var/log/quietpatch.err
   ```

### Package Structure

- **Payload**: `/usr/local/quietpatch/quietpatch.pyz`
- **Service**: `com.quietpatch.agent` (LaunchDaemon)
- **Schedule**: Daily at 3:30 AM
- **Logs**: `/var/log/quietpatch.out` and `/var/log/quietpatch.err`

### Uninstall

```bash
sudo launchctl unload /Library/LaunchDaemons/com.quietpatch.agent.plist
sudo rm -f /Library/LaunchDaemons/com.quietpatch.agent.plist
sudo rm -f /usr/local/quietpatch/quietpatch.pyz
```

## Windows (.msi + Scheduled Task)

*Coming soon*

## Linux (.deb/.rpm + systemd)

*Coming soon*

## CI/CD Integration

The `.github/workflows/release.yml` workflow automatically builds packages when tags are pushed.

### Required Secrets

- `INSTALLER_ID`: Developer ID for code signing (optional)
- `NOTARY_PROFILE`: Keychain profile for notarization (optional)

### Manual Build

```bash
# Build all platforms
bash tools/build_all_platforms.sh 0.2.1

# Build specific platform
bash tools/build_all_platforms.sh 0.2.1 macos
```

