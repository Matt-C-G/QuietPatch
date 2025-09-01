# 🚀 Quick Release Guide

## Pre-Release Validation (Run from macOS)

### 1. **Run Pre-Publish Checks**
```bash
# Comprehensive validation of all artifacts
./tools/pre_publish_checks.sh
```

This script validates:
- ✅ All platform artifacts (macOS, Linux, Windows)
- ✅ Database snapshot integrity and signatures
- ✅ macOS artifact functionality
- ✅ Linux artifact via Docker
- ✅ Windows artifact structure
- ✅ Security checks (selfcheck, bandit)
- ✅ Deterministic operation
- ✅ Offline operation

### 2. **Run Release Checklist**
```bash
# Final release gates
./tools/release_checklist.sh
```

This script checks:
- ✅ Git status (clean, on main, up-to-date)
- ✅ Version consistency
- ✅ Selfcheck passing
- ✅ Security scan results
- ✅ No placeholder CVEs
- ✅ Database snapshot ready
- ✅ All artifacts present
- ✅ Documentation complete
- ✅ CI workflow configured

## Release Process

### 3. **Tag and Push Release**
```bash
# Ensure you're on main and up-to-date
git checkout main
git pull --rebase

# Commit any final changes
git commit -am "v0.2.2: cross-platform artifacts + offline DB snapshot"

# Create annotated tag
git tag -a v0.2.2 -m "QuietPatch v0.2.2"

# Push to trigger CI
git push origin main --follow-tags
```

### 4. **CI Automatically:**
- 🐧 **Builds Linux PEX** on Ubuntu runner
- 🍎 **Builds macOS PEX** on macOS runner  
- 🪟 **Builds Windows PEX** on Windows runner
- 🗄️ **Creates DB snapshot** with checksums
- 📦 **Uploads all artifacts** to GitHub Release
- 🏷️ **Tags releases** with OS-specific labels

## What Gets Released

### **Platform Artifacts**
- `quietpatch-macos.pex` - macOS executable
- `quietpatch-linux-x64.pex` - Linux executable  
- `quietpatch-windows-x64.zip` - Windows package

### **Database Snapshot**
- `db-YYYYMMDD.tar.zst` - Offline vulnerability database
- `db-YYYYMMDD.tar.zst.sha256` - SHA256 checksum
- `db-YYYYMMDD.tar.zst.minisig` - Cryptographic signature

### **Installation Scripts**
- `packaging/linux/install.sh` - Linux production installer
- `packaging/windows/install.ps1` - Windows production installer

## Post-Release Verification

### 5. **Verify GitHub Release**
- Check [GitHub Releases](https://github.com/your-repo/releases)
- Confirm all platform artifacts uploaded
- Verify database snapshot included
- Check SHA256 checksums

### 6. **Test Installation Scripts**
```bash
# Linux (on target system)
sudo ./packaging/linux/install.sh

# Windows (as Administrator)
.\packaging\windows\install.ps1
```

## Troubleshooting

### **Common Issues**

#### **Pre-Publish Checks Fail**
```bash
# Rebuild artifacts
./tools/build_pex.sh
python3 tools/db_snapshot.py --out dist

# Re-run validation
./tools/pre_publish_checks.sh
```

#### **Release Checklist Fails**
```bash
# Check what failed
./tools/release_checklist.sh

# Fix issues (usually missing artifacts or failed tests)
# Re-run until all checks pass
```

#### **CI Build Fails**
- Check GitHub Actions logs
- Verify matrix builds are configured
- Ensure all runners have required dependencies

### **Emergency Rollback**
```bash
# Delete tag locally and remotely
git tag -d v0.2.2
git push origin :refs/tags/v0.2.2

# Fix issues and re-tag
git tag -a v0.2.2 -m "QuietPatch v0.2.2 (fixed)"
git push origin main --follow-tags
```

## Release Notes Template

When editing the GitHub Release:

```markdown
## Downloads
- **macOS**: quietpatch-macos.pex (SHA256: `...`)
- **Linux x64**: quietpatch-linux-x64.pex (SHA256: `...`)
- **Windows x64**: quietpatch-windows-x64.zip (SHA256: `...`)

## Offline DB Snapshot
- db-YYYYMMDD.tar.zst (SHA256: `...`, minisign pubkey: `...`)

## Installation
- **Linux**: Run `sudo ./packaging/linux/install.sh`
- **Windows**: Run `.\packaging\windows\install.ps1` as Administrator

## What's New
- Cross-platform PEX executables for macOS, Linux, and Windows
- Offline database snapshot with cryptographic verification
- Production installation scripts with systemd/Scheduled Task integration
- Comprehensive security hardening and enterprise deployment support

See [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md) for full details.
```

---

**🎯 Quick Release Summary:**
1. `./tools/pre_publish_checks.sh` ✅
2. `./tools/release_checklist.sh` ✅  
3. `git tag -a v0.2.2 -m "QuietPatch v0.2.2"` 🏷️
4. `git push origin main --follow-tags` 🚀
5. **CI builds and publishes automatically!** 🎉

**QuietPatch v0.2.2 will be released with full cross-platform support!** 🎊


