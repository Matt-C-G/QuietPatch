# QuietPatch v0.3.2 Release Notes

## 🎯 Complete Supply-Chain Integrity and Safe Catalog Updates

This release closes all remaining attack surface and edge-case gaps, providing bulletproof supply-chain integrity and safe catalog updates.

## 🔐 Key Security Features

### Database Verification & Protection
- **Minisign Signatures**: All database catalogs cryptographically verified before extraction
- **Path Traversal Protection**: Prevents `../` attacks during archive extraction
- **Rollback Protection**: Epoch-based versioning blocks downgrade attacks
- **Multi-Key Rotation**: Support for trusted key rotation and management

### Catalog Management
- **Versioned Manifest**: Signed `manifest.json` with epoch and client version requirements
- **Dual Format Support**: Both `.tar.zst` (primary) and `.tar.gz` (fallback) database formats
- **Safe Extraction**: Protected tar extraction with comprehensive validation
- **Automated Updates**: Ready-to-use scheduler templates for all platforms

### CLI Enhancements
- **New Commands**:
  - `quietpatch catalog-update` - Update vulnerability catalog with rollback protection
  - `quietpatch db-apply <archive> <signature>` - Verify and extract database archives
  - `quietpatch trust list/add/remove` - Manage trusted signing keys
  - `quietpatch verify <report>` - Verify HTML report integrity
  - `quietpatch diagnostics` - Generate support bundle for troubleshooting

### Security Gates & Testing
- **Hard Release Gates**: Comprehensive testing catches security regressions
- **Deterministic Reports**: Fixed timestamps and content hashing for reproducibility
- **Mock Scanning**: Fast, deterministic CI checks with `--mock` flag
- **Platform-Specific Constraints**: Hermetic installations work across all platforms

## 🛠️ Technical Improvements

### Platform Support
- **macOS**: Native ARM64 support with proper PEX handling
- **Linux**: Full glibc/musl compatibility with platform-specific dependencies
- **Windows**: PowerShell integration and Windows Store Python support

### Installation & Distribution
- **One-Command Installers**: `install.sh` and `install.ps1` for easy setup
- **Package Managers**: Homebrew and Scoop integration ready
- **Docker Support**: Official container image with offline-first design
- **Hermetic Builds**: Platform-specific constraint files ensure reproducible installs

### Documentation & Support
- **Security Policies**: Clear documentation of all security guarantees
- **Support Matrix**: Comprehensive compatibility and requirement documentation
- **Issue Templates**: Structured templates for bug reports and feature requests
- **Troubleshooting Guide**: Step-by-step solutions for common issues

## 🔧 Breaking Changes

- **Python Version**: Now requires Python 3.11+ (previously 3.9+)
- **CLI Changes**: New subcommands for catalog and trust management
- **Database Format**: New epoch-based versioning system

## 📦 Installation

### Quick Install
```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.sh | bash

# Windows (PowerShell)
irm https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.ps1 | iex
```

### Manual Install
```bash
pip install quietpatch==0.3.2
```

### Verify Installation
```bash
quietpatch --version
quietpatch doctor
```

## 🔍 Verification

All release artifacts are cryptographically signed with minisign:

```bash
# Verify checksums
minisign -Vm SHA256SUMS -P <PUBLIC_KEY>
shasum -a 256 -c SHA256SUMS

# Verify individual files
minisign -Vm <file> -P <PUBLIC_KEY>
```

## 🚀 What's Next

- **Automated Catalog Updates**: Daily vulnerability database updates
- **Enhanced Reporting**: More detailed vulnerability analysis and reporting
- **Integration APIs**: REST API for CI/CD integration
- **Enterprise Features**: Advanced policy management and compliance reporting

## 📋 Full Changelog

### Security
- Implemented comprehensive database verification with minisign signatures
- Added path traversal protection for all archive extractions
- Enforced epoch-based rollback protection
- Created multi-key rotation support for trusted keys
- Added hard security gates for release testing

### CLI
- Added `catalog-update` command with downgrade protection
- Added `db-apply` command for safe database extraction
- Added `trust` management commands for key rotation
- Added `verify` command for report integrity checking
- Added `diagnostics` command for support bundle generation

### Infrastructure
- Created platform-specific constraint files for hermetic installs
- Added scheduler templates for macOS/Linux/Windows
- Implemented catalog updater scaffolds in Python and Go
- Added comprehensive error handling and validation
- Created automated regression detection with GitHub issues

### Documentation
- Updated README with security policies and installation instructions
- Added support matrix with compatibility requirements
- Created issue templates for structured bug reporting
- Added troubleshooting guide with common solutions
- Documented all security guarantees and limitations

---

**This release makes QuietPatch production-ready without surprises!** 🎉