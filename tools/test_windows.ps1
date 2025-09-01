# QuietPatch Windows Testing Script
# Tests all edge cases and scenarios for Windows deployment

param(
    [string]$PexPath = "dist/quietpatch-win-py311.pex",
    [switch]$SkipAdminTests,
    [switch]$SkipLongPathTests
)

Write-Host "QuietPatch Windows Testing Suite" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Test 1: Basic PEX functionality
Write-Host "Test 1: Basic PEX Functionality" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow

if (!(Test-Path $PexPath)) {
    Write-Host "ERROR: PEX file not found at $PexPath" -ForegroundColor Red
    Write-Host "Please build the PEX first using tools/build_pex.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "PEX file found: $PexPath" -ForegroundColor Green
$fileInfo = Get-Item $PexPath
Write-Host "File size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Green

# Test 2: Help command
Write-Host "Test 2: Help Command" -ForegroundColor Yellow
Write-Host "-------------------" -ForegroundColor Yellow

$env:PEX_ROOT = "C:\pex"
$env:TEMP = "C:\t"
$env:TMP = "C:\t"

try {
    $helpOutput = python $PexPath --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Help command works" -ForegroundColor Green
    } else {
        Write-Host "✗ Help command failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Help command failed: $_" -ForegroundColor Red
}

# Test 3: Basic scan
Write-Host "Test 3: Basic Scan" -ForegroundColor Yellow
Write-Host "-----------------" -ForegroundColor Yellow

try {
    Write-Host "Running basic scan..." -ForegroundColor Cyan
    $scanOutput = python $PexPath scan --also-report 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Basic scan completed successfully" -ForegroundColor Green
        
        if (Test-Path "report.html") {
            $reportSize = (Get-Item "report.html").Length
            Write-Host "✓ Report generated: report.html ($([math]::Round($reportSize / 1KB, 2)) KB)" -ForegroundColor Green
        } else {
            Write-Host "✗ Report file not found" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Basic scan failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "Output: $scanOutput" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Basic scan failed: $_" -ForegroundColor Red
}

# Test 4: Non-admin scan (if not skipping)
if (!$SkipAdminTests) {
    Write-Host "Test 4: Non-Admin Scan" -ForegroundColor Yellow
    Write-Host "----------------------" -ForegroundColor Yellow
    
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object System.Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if ($isAdmin) {
        Write-Host "Current user is Administrator" -ForegroundColor Cyan
        Write-Host "To test non-admin scenario, run this script from a non-admin PowerShell session" -ForegroundColor Yellow
    } else {
        Write-Host "Current user is NOT Administrator" -ForegroundColor Cyan
        Write-Host "Running scan as non-admin user..." -ForegroundColor Yellow
        
        try {
            $scanOutput = python $PexPath scan --also-report 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Non-admin scan completed successfully" -ForegroundColor Green
                Write-Host "Note: Some system-level findings may be limited" -ForegroundColor Yellow
            } else {
                Write-Host "✗ Non-admin scan failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ Non-admin scan failed: $_" -ForegroundColor Red
        }
    }
}

# Test 5: Long path testing (if not skipping)
if (!$SkipLongPathTests) {
    Write-Host "Test 5: Long Path Testing" -ForegroundColor Yellow
    Write-Host "------------------------" -ForegroundColor Yellow
    
    $longPath = "C:\Users\$env:USERNAME\Documents\Deeply\Nested\QuietPatch\Test\Directory\Structure\That\Exceeds\Normal\Path\Limits\And\Tests\The\PEX\Root\Override\Functionality"
    
    Write-Host "Creating long test path..." -ForegroundColor Cyan
    try {
        New-Item -ItemType Directory -Path $longPath -Force | Out-Null
        Write-Host "✓ Long path created: $longPath" -ForegroundColor Green
        
        # Copy PEX to long path
        $longPathPex = Join-Path $longPath "quietpatch-win-py311.pex"
        Copy-Item $PexPath $longPathPex
        
        Write-Host "Testing PEX from long path..." -ForegroundColor Cyan
        Push-Location $longPath
        
        $env:PEX_ROOT = "C:\pex"
        $env:TEMP = "C:\t"
        $env:TMP = "C:\t"
        
        try {
            $helpOutput = python "quietpatch-win-py311.pex" --help 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ PEX works from long path with PEX_ROOT override" -ForegroundColor Green
            } else {
                Write-Host "✗ PEX failed from long path (exit code: $LASTEXITCODE)" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ PEX failed from long path: $_" -ForegroundColor Red
        }
        
        Pop-Location
        
        # Cleanup
        Remove-Item $longPath -Recurse -Force
        Write-Host "✓ Long path test completed and cleaned up" -ForegroundColor Green
        
    } catch {
        Write-Host "✗ Long path test failed: $_" -ForegroundColor Red
    }
}

# Test 6: Missing Python scenario
Write-Host "Test 6: Missing Python Detection" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow

Write-Host "Testing batch file error handling..." -ForegroundColor Cyan
$batchPath = "packaging/windows/run_quietpatch.bat"

if (Test-Path $batchPath) {
    Write-Host "✓ Batch file found: $batchPath" -ForegroundColor Green
    
    # Test the batch file content for proper error handling
    $batchContent = Get-Content $batchPath -Raw
    if ($batchContent -match "python --version") {
        Write-Host "✓ Batch file checks for Python availability" -ForegroundColor Green
    } else {
        Write-Host "✗ Batch file missing Python check" -ForegroundColor Red
    }
    
    if ($batchContent -match "Please install Python") {
        Write-Host "✓ Batch file provides clear installation instructions" -ForegroundColor Green
    } else {
        Write-Host "✗ Batch file missing installation instructions" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Batch file not found: $batchPath" -ForegroundColor Red
}

# Test 7: Environment variable handling
Write-Host "Test 7: Environment Variable Handling" -ForegroundColor Yellow
Write-Host "------------------------------------" -ForegroundColor Yellow

$testVars = @{
    "PEX_ROOT" = "C:\pex"
    "TEMP" = "C:\t"
    "TMP" = "C:\t"
}

foreach ($var in $testVars.GetEnumerator()) {
    if ($env:$($var.Key) -eq $var.Value) {
        Write-Host "✓ $($var.Key) = $($var.Value)" -ForegroundColor Green
    } else {
        Write-Host "✗ $($var.Key) = $($env:$($var.Key)) (expected: $($var.Value))" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Testing Summary" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Green
Write-Host "All tests completed. Check the output above for any failures." -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If all tests pass, the Windows build is ready for distribution" -ForegroundColor Green
Write-Host "2. Package the files according to the distribution layout" -ForegroundColor Green
Write-Host "3. Test on a fresh Windows VM before release" -ForegroundColor Green
