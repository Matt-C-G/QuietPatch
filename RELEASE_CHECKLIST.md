# QuietPatch v0.4.0 Release Checklist

## Pre-Release Setup

### 1. Generate Minisign Keys
```bash
# On an offline-ish machine
./scripts/generate_keys.sh
```

**Next steps:**
- Add base64 private key to GitHub Secrets as `MINISIGN_SECRET_KEY_B64`
- Update `VERIFY.md` with the public key content
- Keep private key secure and never commit to git

### 2. GitHub Pages Setup
1. Go to Settings → Pages → Source: main (or gh-pages) → root /
2. If using custom domain:
   - Add CNAME in repo root
   - Set domain in Pages settings
   - Configure DNS:
     - Apex: A 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
     - www: CNAME → <user>.github.io
   - Wait for HTTPS to issue; re-save Domain if cert stalls

### 3. Update Repository URLs
Replace `OWNER/REPO` in:
- `docs/index.html` (GitHub Pages landing page)
- `VERIFY.md` (raw GitHub links)

## Release Process

### 1. Tag and Release
```bash
git add -A
git commit -m "v0.4.0: download-ready release kit"
git tag v0.4.0
git push origin main --tags
```

**GitHub Actions will automatically:**
- Build PyInstaller binaries for all platforms
- Create platform-specific packages
- Generate SHA256 checksums
- Sign with minisign
- Upload all artifacts to GitHub Release

## Post-Release Testing

### Manual Smoke Tests (15 minutes)

#### Windows 11
1. Download EXE from GitHub Release
2. Expect SmartScreen: click "More info" → "Run anyway"
3. App launches; run a read-only scan
4. Confirm report footer has hash + signature status
5. Test uninstall (removes Start Menu entry)

#### macOS (Sonoma/Sequoia, Intel + ARM)
1. Open DMG → drag app to Applications
2. First run: Right-click → "Open" → "Open"
3. Scan in read-only; confirm report
4. App quits/relaunches without quarantine prompts

#### Linux (Ubuntu LTS)
1. `chmod +x QuietPatch-*.AppImage && ./QuietPatch-*.AppImage`
2. Scan, open report
3. Desktop entry appears when integrated

### Verification Tests
```powershell
# Windows PowerShell
Get-FileHash .\QuietPatch-Setup-v0.4.0.exe -Algorithm SHA256
```

```bash
# macOS/Linux
shasum -a 256 QuietPatch-v0.4.0.dmg
```

```bash
# Minisign verification
minisign -Vm SHA256SUMS.txt -P "<PUBKEY>"
# Must show: "Signature and comment signature verified"
```

## User-Facing Messages

### SmartScreen & Gatekeeper Copy

**Windows:**
> "Windows protected your PC" → click "More info" then "Run anyway". We use open signing (minisign + checksums) instead of paid certs. Verify first if you prefer.

**macOS:**
> App is from an unidentified developer → Right-click the app → "Open" → "Open" once. Future launches open normally.

## Known Pitfalls (Fix Before Users Hit Them)

1. **Wrong asset paths in Actions** - Ensure dist names match PyInstaller outputs
2. **Minisign package missing on macOS runners** - Brew sometimes fails; verify minisign step runs
3. **Public key not in VERIFY.md** - Users can't verify without it
4. **Pages links still OWNER/REPO** - Replace with real org/repo

## Post-Ship QA (15 minutes)

- [ ] Download each OS artifact from the Release (not Actions artifacts)
- [ ] Run verification steps exactly as written in VERIFY.md
- [ ] Confirm landing page buttons resolve to v0.4.0 assets (no 404)
- [ ] Test robots.txt and sitemap.xml over HTTPS

## When to Invest in Code Signing

**Windows OV cert:** When users >20% bounce at SmartScreen
**Apple Developer ID + notarization:** When macOS audience complains or MDM blocks unidentified dev apps

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
