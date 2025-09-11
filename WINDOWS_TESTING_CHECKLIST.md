# QuietPatch Windows Testing Checklist

## Pre-Build Verification

### ✅ Environment Setup
- [ ] Python 3.12 x64 installed from python.org
- [ ] Inno Setup 6 installed from jrsoftware.org
- [ ] Minisign installed (`choco install minisign`)
- [ ] 7-Zip installed (optional, falls back to PowerShell)
- [ ] Git repository cloned to Windows VM

### ✅ Build Files Present
- [ ] `Makefile.ps1` exists
- [ ] `README-QuickStart.txt` exists
- [ ] `installer/windows/QuietPatch.iss` exists
- [ ] `build/quietpatch_wizard_win.spec` exists
- [ ] `build/quietpatch_cli_win.spec` exists
- [ ] `keys/quietpatch.key` exists (secret key)

## Build Process

### ✅ One-Command Build
```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\Makefile.ps1 all
```

**Expected Output:**
- [ ] `release/QuietPatch-Setup-v0.4.0.exe` (installer)
- [ ] `release/quietpatch-cli-v0.4.0-win64.zip` (portable CLI)
- [ ] `release/SHA256SUMS.txt` (checksums)
- [ ] `release/SHA256SUMS.txt.minisig` (signature)
- [ ] `release/README-QuickStart.txt` (user guide)
- [ ] `release/VERIFY.md` (verification instructions)

### ✅ Build Verification
```powershell
.\scripts\windows\verify-build.ps1
```

**Expected Results:**
- [ ] All required files present
- [ ] File sizes reasonable (installer 10-50MB, CLI zip 5-20MB)
- [ ] Checksums verified
- [ ] Minisign signature verified
- [ ] Portable CLI contains `quietpatch.exe` and `README-QuickStart.txt`

## Installer Testing

### ✅ Clean Windows 11 VM Test
1. **Download & Run Installer**
   - [ ] Download `QuietPatch-Setup-v0.4.0.exe`
   - [ ] Right-click → Properties → Unblock (if needed)
   - [ ] Double-click to run
   - [ ] Expect SmartScreen warning → "More info" → "Run anyway"

2. **Installation Process**
   - [ ] Installer launches with proper UI
   - [ ] Default installation path is correct
   - [ ] Installation completes without errors
   - [ ] Post-install option to "Open QuickStart Guide" works

3. **Start Menu Verification**
   - [ ] "QuietPatch" shortcut exists (launches GUI)
   - [ ] "QuietPatch CLI" shortcut exists (launches CLI)
   - [ ] "QuickStart Guide" shortcut exists (opens in Notepad)
   - [ ] "Verify Download" shortcut exists (opens VERIFY.md)
   - [ ] "Uninstall QuietPatch" shortcut exists

4. **Application Testing**
   - [ ] Launch QuietPatch from Start Menu
   - [ ] GUI wizard opens correctly
   - [ ] Click "Start Scan" (read-only mode)
   - [ ] Scan completes successfully
   - [ ] Click "View Report" opens HTML report
   - [ ] Report displays correctly in browser

5. **CLI Testing**
   - [ ] Open Command Prompt
   - [ ] Run `quietpatch --help` (shows help)
   - [ ] Run `quietpatch scan --report .` (creates report)
   - [ ] Verify HTML report is generated

6. **Uninstall Testing**
   - [ ] Go to Apps & Features
   - [ ] Find "QuietPatch 0.4.0"
   - [ ] Click Uninstall
   - [ ] Uninstall completes successfully
   - [ ] Start Menu shortcuts removed
   - [ ] Program files removed

## Portable CLI Testing

### ✅ Portable CLI Test
1. **Extract ZIP**
   - [ ] Download `quietpatch-cli-v0.4.0-win64.zip`
   - [ ] Extract to a folder
   - [ ] Verify `README-QuickStart.txt` is at top level
   - [ ] Verify `quietpatch.exe` is present

2. **CLI Execution**
   - [ ] Open Command Prompt in extracted folder
   - [ ] Run `quietpatch.exe --help`
   - [ ] Run `quietpatch.exe scan --report .`
   - [ ] Verify scan completes and creates report

3. **QuickStart Guide**
   - [ ] Double-click `README-QuickStart.txt`
   - [ ] Opens in Notepad with correct content
   - [ ] Instructions are clear and helpful

## Verification Testing

### ✅ Checksum Verification
```powershell
cd release
Get-FileHash .\QuietPatch-Setup-v0.4.0.exe -Algorithm SHA256
Get-Content .\SHA256SUMS.txt | Select-String QuietPatch-Setup-v0.4.0.exe
```

**Expected:**
- [ ] Hash matches between file and SHA256SUMS.txt

### ✅ Minisign Verification
```powershell
cd release
minisign -Vm .\SHA256SUMS.txt -P "RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR"
```

**Expected:**
- [ ] "Signature and comment signature verified"

## Common Issues & Fixes

### ❌ Build Issues
- **PyInstaller fails**: Check Python 3.12, virtual environment, dependencies
- **Inno Setup fails**: Check installer script paths, file locations
- **7-Zip missing**: Script falls back to PowerShell compression
- **Minisign fails**: Check key file path, permissions

### ❌ Installer Issues
- **SmartScreen blocks**: Expected on first run, use "More info" → "Run anyway"
- **Missing files**: Check Inno Setup script source paths
- **Wrong shortcuts**: Check [Icons] section in installer script
- **Installation fails**: Check admin privileges, disk space

### ❌ Runtime Issues
- **GUI won't start**: Check PyInstaller build, dependencies
- **CLI won't run**: Check executable permissions, antivirus
- **Report won't open**: Check browser association, file permissions

## Release Readiness

### ✅ Pre-Release Checklist
- [ ] All tests pass on clean Windows 11 VM
- [ ] Installer works with SmartScreen bypass
- [ ] Portable CLI works without installation
- [ ] All Start Menu shortcuts functional
- [ ] Checksums and signatures verified
- [ ] QuickStart guide accessible and helpful

### ✅ Release Upload
- [ ] Upload all files from `release/` to GitHub Release
- [ ] Update landing page download links
- [ ] Test download links work correctly
- [ ] Verify public key in VERIFY.md

## Success Criteria

**✅ Windows Release is Ready When:**
- [ ] One-command build works: `.\Makefile.ps1 all`
- [ ] Installer works on clean Windows 11 VM
- [ ] Portable CLI works without installation
- [ ] All verification steps pass
- [ ] User experience is smooth and professional

**🎉 Ship it!** 🚀
