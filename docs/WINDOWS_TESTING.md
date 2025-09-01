# Windows Testing Guide

This guide covers comprehensive testing of QuietPatch on Windows systems, including edge cases and production scenarios.

## Prerequisites

- Windows 10/11 or Windows Server 2019/2022
- Python 3.11 (64-bit) installed and added to PATH
- PowerShell 5.1+ or PowerShell Core 7+
- Administrator access (for some tests)

## Test Environment Setup

### 1. Build the Windows PEX

```powershell
# From project root
py -3.11 -m pip install --upgrade pip wheel setuptools pex
py -3.11 -m pip install -e .
mkdir dist
py -3.11 -m pex quietpatch -c quietpatch `
  -o dist/quietpatch-win-py311.pex `
  --validate-entry-point --no-build --venv prepend --strip-pex-env
```

### 2. Set Environment Variables

```powershell
# Use short cache dirs to dodge MAX_PATH
$env:PEX_ROOT="C:\pex"
$env:TEMP="C:\t"
$env:TMP="C:\t"
```

## Test Scenarios

### Test 1: Basic Functionality

**Objective**: Verify the PEX runs and responds to basic commands.

```powershell
# Test help command
py -3.11 dist\quietpatch-win-py311.pex scan --help

# Test basic scan
py -3.11 dist\quietpatch-win-py311.pex scan
```

**Expected Results**:
- ✅ Help command displays usage information
- ✅ Scan runs without errors
- ✅ Report is generated (`report.html`)
- ✅ Exit code is 0

### Test 2: Report Generation

**Objective**: Verify scan reports are generated correctly.

```powershell
# Run scan with report generation
py -3.11 dist\quietpatch-win-py311.pex scan --also-report
```

**Expected Results**:
- ✅ `report.html` file is created
- ✅ File size > 0 bytes
- ✅ Report opens in default browser
- ✅ Report contains vulnerability data

### Test 3: Batch File Wrapper

**Objective**: Test the user-friendly batch file launcher.

**Steps**:
1. Copy `packaging/windows/run_quietpatch.bat` to the same directory as the PEX
2. Double-click `run_quietpatch.bat` in Windows Explorer
3. Verify the console opens and scan runs

**Expected Results**:
- ✅ Console window opens
- ✅ Scan runs automatically
- ✅ Report opens in browser
- ✅ Console shows success message

### Test 4: Non-Administrator Context

**Objective**: Verify functionality when running as a non-admin user.

**Steps**:
1. Open PowerShell as a non-administrator user
2. Navigate to the QuietPatch directory
3. Run the scan

```powershell
py -3.11 dist\quietpatch-win-py311.pex scan --also-report
```

**Expected Results**:
- ✅ Scan completes successfully
- ✅ Report is generated
- ⚠️ Some system-level findings may be limited
- ✅ No permission errors

### Test 5: Administrator Context

**Objective**: Verify full functionality when running as administrator.

**Steps**:
1. Open PowerShell as Administrator
2. Navigate to the QuietPatch directory
3. Run the scan

```powershell
py -3.11 dist\quietpatch-win-py311.pex scan --also-report
```

**Expected Results**:
- ✅ Scan completes successfully
- ✅ Report is generated
- ✅ Full system coverage (including system apps)
- ✅ No permission errors

### Test 6: Long Path Handling

**Objective**: Test PEX execution from deeply nested directories.

**Steps**:
1. Create a deeply nested directory structure
2. Copy the PEX to the deep location
3. Test execution with PEX_ROOT override

```powershell
# Create long path
$longPath = "C:\Users\$env:USERNAME\Documents\Deeply\Nested\QuietPatch\Test\Directory\Structure\That\Exceeds\Normal\Path\Limits\And\Tests\The\PEX\Root\Override\Functionality"

New-Item -ItemType Directory -Path $longPath -Force
Copy-Item "dist\quietpatch-win-py311.pex" $longPath

# Test execution
Push-Location $longPath
$env:PEX_ROOT = "C:\pex"
$env:TEMP = "C:\t"
$env:TMP = "C:\t"

python "quietpatch-win-py311.pex" --help

Pop-Location
```

**Expected Results**:
- ✅ Long path is created successfully
- ✅ PEX executes without WinError 206
- ✅ PEX_ROOT override works correctly
- ✅ No MAX_PATH issues

### Test 7: Missing Python Detection

**Objective**: Test error handling when Python is not available.

**Steps**:
1. Temporarily rename or move Python from PATH
2. Double-click `run_quietpatch.bat`
3. Verify error message

**Expected Results**:
- ✅ Clear error message displayed
- ✅ Instructions to install Python 3.11
- ✅ Link to python.org provided
- ✅ Batch file pauses for user input

### Test 8: Environment Variable Isolation

**Objective**: Verify PEX cache isolation and environment handling.

**Steps**:
1. Set custom environment variables
2. Run multiple scans
3. Verify cache isolation

```powershell
# Test with custom PEX_ROOT
$env:PEX_ROOT = "C:\custom\pex\cache"
$env:TEMP = "C:\custom\temp"
$env:TMP = "C:\custom\tmp"

py -3.11 dist\quietpatch-win-py311.pex scan

# Verify cache directory structure
Get-ChildItem "C:\custom\pex\cache" -Recurse
```

**Expected Results**:
- ✅ Custom cache directories are used
- ✅ No conflicts between different PEX_ROOT values
- ✅ Cache files are properly isolated

## Automated Testing

### Run the Complete Test Suite

```powershell
# Run all tests
.\tools\test_windows.ps1

# Run specific tests
.\tools\test_windows.ps1 -SkipAdminTests
.\tools\test_windows.ps1 -SkipLongPathTests
```

### CI Integration

The Windows build job in `.github/workflows/release.yml` automatically runs:
- PEX build with exact specifications
- Smoke test with environment variables
- Distribution packaging
- Basic functionality verification

## Troubleshooting

### Common Issues

1. **"python not found"**
   - Install Python 3.11 from python.org
   - Ensure "Add Python to PATH" is checked

2. **Permission errors**
   - Run PowerShell as Administrator
   - Check antivirus exclusions

3. **Path too long errors**
   - Use PEX_ROOT override
   - Run from shorter directory paths
   - Set TEMP and TMP to short paths

4. **PEX cache issues**
   - Clear PEX_ROOT directory
   - Use isolated cache directories
   - Check disk space

### Debug Mode

```powershell
# Enable verbose output
$env:QP_DEBUG = "1"
py -3.11 dist\quietpatch-win-py311.pex scan --also-report
```

## Performance Testing

### Scan Performance

```powershell
# Measure scan time
$startTime = Get-Date
py -3.11 dist\quietpatch-win-py311.pex scan --also-report
$endTime = Get-Date
$duration = $endTime - $startTime
Write-Host "Scan completed in $($duration.TotalSeconds) seconds"
```

### Memory Usage

```powershell
# Monitor memory usage during scan
Get-Process python | Select-Object ProcessName, WorkingSet, CPU
```

## Production Readiness Checklist

- [ ] PEX builds successfully with specified flags
- [ ] Basic scan functionality works
- [ ] Report generation works
- [ ] Batch file wrapper functions correctly
- [ ] Non-admin scans work (with limitations)
- [ ] Admin scans provide full coverage
- [ ] Long path handling works with PEX_ROOT
- [ ] Missing Python detection provides clear guidance
- [ ] Environment variable isolation works
- [ ] Performance is acceptable
- [ ] Error handling is user-friendly
- [ ] Distribution package includes all required files

## Next Steps

After completing all tests:

1. **Package the distribution** using `tools/package_windows.ps1`
2. **Test on fresh Windows VM** to verify deployment
3. **Validate user experience** with double-click functionality
4. **Document any issues** found during testing
5. **Update release notes** with Windows-specific information
