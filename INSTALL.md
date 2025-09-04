# Installation Guide

QuietPatch can be installed in several ways across different platforms.

## 🚀 One-Command Installation (Recommended)

### macOS & Linux
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.sh)"
```

### Windows
```powershell
irm https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/install.ps1 | iex
```

These scripts will:
- Download the latest release for your platform
- Verify checksums for security
- Extract the PEX executable and launcher scripts
- Download the offline vulnerability database
- Set up PATH integration (where possible)
- Provide usage instructions

## 📦 Package Managers

### macOS (Homebrew)
```bash
# Add the tap and install
brew tap matt-c-g/quietpatch
brew install quietpatch

# Or in one command
brew tap matt-c-g/quietpatch && brew install quietpatch
```

### Windows (Scoop)
```powershell
# Add the bucket and install
scoop bucket add quietpatch https://github.com/Matt-C-G/scoop-quietpatch
scoop install quietpatch
```

### Linux (Linuxbrew)
```bash
# Same as macOS Homebrew
brew tap matt-c-g/quietpatch
brew install quietpatch
```

## 🔧 Manual Installation

### 1. Download Release
Visit the [latest release](https://github.com/Matt-C-G/QuietPatch/releases/latest) and download:
- **Windows**: `quietpatch-windows-x64.zip`
- **Linux**: `quietpatch-linux-x86_64.zip`
- **macOS**: `quietpatch-macos-arm64.zip`

### 2. Extract and Run
```bash
# Extract the archive
unzip quietpatch-*.zip

# Run the scanner
./run_quietpatch.sh scan --help  # Linux/macOS
# or
run_quietpatch.bat scan --help   # Windows
```

### 3. Download Database (Optional)
For offline operation, download the vulnerability database:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/scripts/install.sh)"
```

## 🔍 Verification

All releases include SHA256 checksums for verification:

```bash
# Download and verify checksums
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/SHA256SUMS
sha256sum -c SHA256SUMS
```

## 📋 Requirements

- **Python 3.11** (required for PEX execution)
- **Internet connection** (for initial download and database updates)
- **Offline operation** supported with local database

## 🛠️ Development Installation

For developers who want to build from source:

```bash
# Clone the repository
git clone https://github.com/Matt-C-G/QuietPatch.git
cd QuietPatch

# Install in development mode
make dev

# Build and test locally
make pre-release
```

## 🆘 Troubleshooting

### Python Not Found
Ensure Python 3.11 is installed and in your PATH:
- **macOS**: `brew install python@3.11`
- **Linux**: Use your distribution's package manager
- **Windows**: Download from [python.org](https://python.org)

### Permission Denied
On Unix systems, you may need to make scripts executable:
```bash
chmod +x run_quietpatch.sh
```

### PATH Issues
If the `quietpatch` command isn't found after installation:
- **Linux/macOS**: Add the installation directory to your PATH
- **Windows**: Restart your terminal or run `refreshenv`

## 🗑️ Uninstallation

### One-Command Uninstall

**macOS & Linux:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/uninstall.sh)"
```

**Windows:**
```powershell
irm https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/uninstall.ps1 | iex
```

### Package Manager Uninstall

**Homebrew:**
```bash
brew uninstall quietpatch
```

**Scoop:**
```powershell
scoop uninstall quietpatch
```

### Manual Uninstall

1. Remove the installation directory:
   - **macOS/Linux**: `~/.quietpatch/` or `$QUIETPATCH_PREFIX`
   - **Windows**: `%LOCALAPPDATA%\QuietPatch\` or `$env:QUIETPATCH_PREFIX`

2. Remove cache directories:
   - **macOS/Linux**: `~/.cache/quietpatch/`
   - **Windows**: `%LOCALAPPDATA%\quietpatch\`

3. Remove PATH entries if manually added

## 🔄 Updates

### Package Managers
```bash
# Homebrew
brew upgrade quietpatch

# Scoop
scoop update quietpatch
```

### Manual Updates
Re-run the installation script or download the latest release manually.

## 📞 Support

For installation issues or questions:
- [GitHub Issues](https://github.com/Matt-C-G/QuietPatch/issues)
- [Documentation](https://github.com/Matt-C-G/QuietPatch#readme)
