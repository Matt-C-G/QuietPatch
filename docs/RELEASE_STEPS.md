# QuietPatch Release Steps

## 1) Tag on main
```bash
git checkout main && git pull
git tag -a v0.2.2 -m "QuietPatch v0.2.2"
git push origin --tags
```

## 2) GitHub Actions builds PEX for macOS/Linux/Windows + DB snapshot

The CI will automatically:
- Build PEX executables for all platforms
- Create a signed DB snapshot (tar.zst)
- Run all tests and release gates
- Upload artifacts

## 3) Create GitHub Release

1. Go to GitHub Releases page
2. Click "Create a new release"
3. Tag: `v0.2.2`
4. Title: `QuietPatch v0.2.2`
5. Description: Include changelog and known issues
6. Attach artifacts:
   - `quietpatch-macos-latest.pex`
   - `quietpatch-ubuntu-latest.pex` 
   - `quietpatch-windows-latest.pex`
   - `db-YYYYMMDD.tar.zst` (+ `.sha256`)

## 4) Sanity Check

Test the release locally:
```bash
# Download and test PEX
curl -LO https://github.com/quietpatch/QuietPatch/releases/download/v0.2.2/quietpatch-macos-latest.pex
chmod +x quietpatch-macos-latest.pex

# Test with local DB
./quietpatch-macos-latest.pex scan --also-report --open

# Verify report shows:
# - Real CVE IDs (no test patterns)
# - Action column populated
# - Severity badges working
```

## 5) Platform-Specific Installation

### macOS
```bash
# Install via package
sudo installer -pkg quietpatch-0.2.2.pkg -target /

# Or manual install
sudo mkdir -p /usr/local/quietpatch
sudo cp quietpatch-macos-latest.pex /usr/local/quietpatch/quietpatch
sudo cp config/policy.yml /etc/quietpatch/
```

### Linux
```bash
# Install via package
sudo dpkg -i quietpatch_0.2.2_amd64.deb

# Or manual install
sudo mkdir -p /usr/local/quietpatch /var/lib/quietpatch/{db,logs}
sudo cp quietpatch-ubuntu-latest.pex /usr/local/quietpatch/quietpatch.pex
sudo cp config/policy.yml /etc/quietpatch/
sudo systemctl enable --now quietpatch.timer
```

### Windows
```powershell
# Install via package
msiexec /i QuietPatch-0.2.2.msi

# Or manual install
$root = "C:\Program Files\QuietPatch"
New-Item -ItemType Directory -Force -Path $root | Out-Null
Copy-Item .\quietpatch-windows-latest.pex "$root\quietpatch.pex" -Force
Copy-Item .\packaging\windows\quietpatch.ps1 "$root\quietpatch.ps1" -Force

# Register scheduled task
schtasks /Create /TN "QuietPatch Agent" /XML ".\packaging\windows\QuietPatch-Agent.xml" /F
```

## 6) Verify Installation

### macOS
```bash
sudo launchctl print system/com.quietpatch.agent | grep -E "Program|Environment|QP_"
sudo ls -lh /var/lib/quietpatch/db
```

### Linux
```bash
sudo systemctl status quietpatch.timer
sudo ls -lh /var/lib/quietpatch/db
```

### Windows
```powershell
schtasks /Query /TN "QuietPatch Agent"
Get-ChildItem "C:\ProgramData\QuietPatch\db" -ErrorAction SilentlyContinue
```

## 7) First Run Test

```bash
# macOS
sudo launchctl kickstart -k system/com.quietpatch.agent

# Linux  
sudo systemctl start quietpatch.service

# Windows
schtasks /Run /TN "QuietPatch Agent"
```

Check logs and verify:
- Report generated successfully
- Action column populated
- Real CVE data (no test patterns)
- No errors in logs


