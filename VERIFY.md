# Verify QuietPatch Release

This document explains how to verify the integrity and authenticity of QuietPatch releases.

## Quick Verification

```bash
# Download checksums and verify
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/SHA256SUMS
shasum -a 256 -c SHA256SUMS
```

## Cryptographic Verification (Recommended)

### 1. Install Minisign

**macOS:**
```bash
brew install minisign
```

**Ubuntu/Debian:**
```bash
sudo apt install minisign
```

**Windows:**
Download from [minisign releases](https://github.com/jedisct1/minisign/releases)

### 2. Verify Checksums

```bash
# Download checksums and signature
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/SHA256SUMS
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/SHA256SUMS.minisig

# Verify signature (replace with actual public key)
minisign -Vm SHA256SUMS -P <YOUR_PUBKEY>

# Verify artifacts match checksums
shasum -a 256 -c SHA256SUMS
```

### 3. Windows Verification

```powershell
# Download checksums
Invoke-WebRequest -Uri "https://github.com/Matt-C-G/QuietPatch/releases/latest/download/SHA256SUMS" -OutFile "SHA256SUMS"

# Verify each file
Get-ChildItem quietpatch-*.whl | ForEach-Object {
    $expected = (Select-String -Path "SHA256SUMS" -Pattern $_.Name).Line.Split()[0]
    $actual = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    if ($expected -eq $actual) {
        Write-Host "✅ $($_.Name) - OK"
    } else {
        Write-Host "❌ $($_.Name) - MISMATCH"
    }
}
```

## Verified Installation

For maximum security, install from verified sources:

```bash
# 1. Download and verify checksums
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/SHA256SUMS
minisign -Vm SHA256SUMS -P <YOUR_PUBKEY>

# 2. Install with binary-only mode (no source builds)
python -m pip install quietpatch==0.3.0 --only-binary :all:

# 3. Verify installation
quietpatch --version
quietpatch env doctor
```

## Release Assets

Each release includes:

- **Wheels**: `quietpatch-*.whl` (Python packages)
- **Source**: `quietpatch-*.tar.gz` (source distribution)
- **Database**: `qp_db-YYYYMMDD.tar.zst` (compressed CVE data)
- **Checksums**: `SHA256SUMS` (integrity verification)
- **Signature**: `SHA256SUMS.minisig` (authenticity verification)

## Security Model

- **Integrity**: SHA256 checksums prevent tampering
- **Authenticity**: Minisign signatures verify source
- **Reproducibility**: Deterministic builds from source
- **Transparency**: All code and build processes are public

## Troubleshooting

**Checksum mismatch:**
- Re-download the file
- Check for network issues
- Verify you're using the correct release

**Signature verification fails:**
- Ensure you have the correct public key
- Check that the signature file is not corrupted
- Verify the release is from the official repository

**Installation fails:**
- Run `quietpatch env doctor` for environment issues
- Check Python version compatibility (3.11-3.12)
- Use `--only-binary :all:` to avoid source builds

## Public Key

The public key for signature verification will be published in the repository root as `minisign.pub` and in the release notes.

## Reporting Issues

If you find any verification issues:

1. Check the [troubleshooting guide](README.md#troubleshooting)
2. Run `quietpatch env doctor` for diagnostics
3. Open an issue with the verification output
4. Include your platform and Python version