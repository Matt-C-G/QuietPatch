# Verify QuietPatch Release

## 0) Get files
Download: `quietpatch.pyz` (and optional wrappers), `SHA256SUMS`, `SHA256SUMS.minisig`, and `minisign.pub`.

## 1) Verify checksums
macOS:
  shasum -a 256 -c SHA256SUMS
Linux:
  sha256sum -c SHA256SUMS
Windows (PowerShell):
  Get-FileHash .\quietpatch.pyz -Algorithm SHA256

## 2) Verify publisher signature (minisign)
minisign -Vm SHA256SUMS -P "$(cat minisign.pub)"

## 3) Run (no install)
macOS/Linux:
  python3 quietpatch.pyz -h
Windows:
  py quietpatch.pyz -h
