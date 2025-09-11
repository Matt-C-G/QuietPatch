# Verify your QuietPatch download (v0.4.0)

QuietPatch publishes SHA256 checksums and a Minisign signature for every release. Verification proves your download wasn't tampered with.

## Files you need
- Your downloaded installer/app
- `SHA256SUMS.txt`
- `SHA256SUMS.txt.minisig`

## 1) Verify the checksum
### Windows (PowerShell)
```powershell
Get-FileHash .\QuietPatch-Setup-v0.4.0.exe -Algorithm SHA256 | Format-List
# Compare the Hash value to the matching line in SHA256SUMS.txt
```

### macOS / Linux (Terminal)
```bash
shasum -a 256 QuietPatch-v0.4.0.dmg
# or
sha256sum QuietPatch-v0.4.0-x86_64.AppImage
# Compare to SHA256SUMS.txt
```

## 2) Verify the signed checksum list with Minisign
Install minisign:
- **Windows:** Scoop `scoop install minisign` or Chocolatey `choco install minisign`
- **macOS:** Homebrew `brew install minisign`
- **Linux:** `apt install minisign` (or your distro equivalent)

Then run:
```bash
minisign -Vm SHA256SUMS.txt -P "RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR"
# Output should include: "Signature and comment signature verified"
```

## 3) macOS first launch (unsigned for now)
Right‑click QuietPatch → **Open** → **Open**. You'll only need to do this once.

## 4) Trouble? Read this
- If verification fails, **do not run the file**. Re‑download from the official release and try again.
- Still stuck? Open an issue on the repo with your OS/version and the exact error text.

Replace `<PASTE_QUIETPATCH_PUBLIC_KEY_HERE>` with your minisign public key (not the secret). Example format: RWQ...=, ~56 chars.