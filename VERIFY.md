# Verify QuietPatch Release

## 1) Verify checksums
- **Linux/macOS**
  ```sh
  sha256sum -c SHA256SUMS
  ```
- **Windows (PowerShell)**
  ```powershell
  Get-Content .\SHA256SUMS
  # For a single file:
  Get-FileHash .\quietpatch-<ver>-windows.zip -Algorithm SHA256
  ```

## 2) Verify signature (if provided)
Install minisign:
- **macOS**: `brew install minisign`
- **Linux**: `sudo apt install minisign` or equivalent
- **Windows**: Download `minisign.exe`

Verify:
```sh
minisign -Vm SHA256SUMS -P <YOUR_PUBLIC_KEY>
```

**Public Key**: `RWRtBE/9+6QQXihyB4b0MeRcOspjz7pVr0Ui/V1b9gU=`

**If checksum or signature fails: do not run the binaries—re-download from the Release page.**

## 3) Quick verification
```bash
# Download and verify in one go
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/quietpatch-linux-x86_64.zip
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/SHA256SUMS
sha256sum -c SHA256SUMS
```