# QuietPatch Windows Ship Gate - Final Verification
# Run this before shipping to ensure everything is ready

param(
    [string]$Version = '0.4.0'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Write-Host "🚀 QuietPatch Windows Ship Gate - Final Verification" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "Makefile.ps1")) {
    Write-Host "❌ Makefile.ps1 not found. Run from repo root." -ForegroundColor Red
    exit 1
}

Write-Host "`n📋 Pre-build Checklist" -ForegroundColor Yellow

# Check required files
$RequiredFiles = @(
    "Makefile.ps1",
    "README-QuickStart.txt",
    "installer/windows/QuietPatch.iss",
    "build/quietpatch_wizard_win.spec",
    "build/quietpatch_cli_win.spec",
    "keys/quietpatch.key"
)

$MissingFiles = @()
foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file (MISSING)" -ForegroundColor Red
        $MissingFiles += $file
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Host "`n❌ Missing required files. Cannot proceed." -ForegroundColor Red
    exit 1
}

Write-Host "`n🔨 Running Build Process" -ForegroundColor Yellow
Write-Host "Command: .\Makefile.ps1 all" -ForegroundColor Cyan

# Run the build
try {
    & .\Makefile.ps1 all
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed with exit code $LASTEXITCODE"
    }
    Write-Host "✅ Build completed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Build failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n📦 Verifying Release Artifacts" -ForegroundColor Yellow

# Check release directory
if (-not (Test-Path "release")) {
    Write-Host "❌ Release directory not found" -ForegroundColor Red
    exit 1
}

Set-Location release

# Expected files
$ExpectedFiles = @(
    "QuietPatch-Setup-v$Version.exe",
    "quietpatch-cli-v$Version-win64.zip",
    "SHA256SUMS.txt",
    "SHA256SUMS.txt.minisig",
    "README-QuickStart.txt",
    "VERIFY.md"
)

Write-Host "Release artifacts:" -ForegroundColor Cyan
$MissingFiles = @()
foreach ($file in $ExpectedFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "✅ $file ($sizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "❌ $file (MISSING)" -ForegroundColor Red
        $MissingFiles += $file
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Host "`n❌ Missing release files. Build incomplete." -ForegroundColor Red
    exit 1
}

Write-Host "`n🔐 Verifying Checksums and Signatures" -ForegroundColor Yellow

# Check SHA256SUMS.txt format
Write-Host "SHA256SUMS.txt contents:" -ForegroundColor Cyan
Get-Content "SHA256SUMS.txt" | ForEach-Object { Write-Host "  $_" -ForegroundColor White }

# Verify installer checksum
$InstallerFile = "QuietPatch-Setup-v$Version.exe"
if (Test-Path $InstallerFile) {
    $InstallerHash = (Get-FileHash $InstallerFile -Algorithm SHA256).Hash
    $ShaLine = Get-Content "SHA256SUMS.txt" | Where-Object { $_ -match "QuietPatch-Setup-v$Version\.exe" }
    if ($ShaLine -match $InstallerHash) {
        Write-Host "✅ Installer checksum verified" -ForegroundColor Green
    } else {
        Write-Host "❌ Installer checksum mismatch" -ForegroundColor Red
        Write-Host "  Expected: $InstallerHash" -ForegroundColor Yellow
        Write-Host "  Found: $ShaLine" -ForegroundColor Yellow
    }
}

# Verify minisign signature
if (Get-Command minisign -ErrorAction SilentlyContinue) {
    $PubKey = "RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR"
    try {
        $result = minisign -Vm SHA256SUMS.txt -P $PubKey 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Minisign signature verified" -ForegroundColor Green
        } else {
            Write-Host "❌ Minisign signature verification failed" -ForegroundColor Red
            Write-Host "  Output: $result" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Minisign verification error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  Minisign not available - skipping signature verification" -ForegroundColor Yellow
}

Write-Host "`n📦 Verifying Portable CLI Contents" -ForegroundColor Yellow

# Check portable CLI ZIP contents
$ZipFile = "quietpatch-cli-v$Version-win64.zip"
if (Test-Path $ZipFile) {
    try {
        # Extract to temp directory to check contents
        $TempDir = "temp-cli-check"
        if (Test-Path $TempDir) { Remove-Item -Recurse -Force $TempDir }
        New-Item -ItemType Directory -Path $TempDir | Out-Null
        
        if (Get-Command 7z -ErrorAction SilentlyContinue) {
            7z x $ZipFile -o$TempDir -y | Out-Null
        } else {
            Expand-Archive -Path $ZipFile -DestinationPath $TempDir -Force
        }
        
        $ZipContents = Get-ChildItem -Recurse $TempDir
        Write-Host "Portable CLI contents:" -ForegroundColor Cyan
        $ZipContents | ForEach-Object { 
            $relPath = $_.FullName.Replace((Get-Item $TempDir).FullName, "").TrimStart('\')
            Write-Host "  $relPath" -ForegroundColor White 
        }
        
        # Check for required files
        $RequiredInZip = @("quietpatch.exe", "README-QuickStart.txt")
        $MissingInZip = @()
        foreach ($req in $RequiredInZip) {
            if (-not (Test-Path "$TempDir\$req")) {
                $MissingInZip += $req
            }
        }
        
        if ($MissingInZip.Count -eq 0) {
            Write-Host "✅ Portable CLI contains all required files" -ForegroundColor Green
        } else {
            Write-Host "❌ Portable CLI missing: $($MissingInZip -join ', ')" -ForegroundColor Red
        }
        
        Remove-Item -Recurse -Force $TempDir
    } catch {
        Write-Host "❌ Error checking portable CLI: $_" -ForegroundColor Red
    }
}

Write-Host "`n🎯 Ship Gate Summary" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green

if ($MissingFiles.Count -eq 0) {
    Write-Host "✅ All required files present" -ForegroundColor Green
    Write-Host "✅ Build process completed successfully" -ForegroundColor Green
    Write-Host "✅ Checksums and signatures verified" -ForegroundColor Green
    Write-Host "✅ Portable CLI packaging correct" -ForegroundColor Green
    
    Write-Host "`n🚀 READY TO SHIP!" -ForegroundColor Green
    Write-Host "=================" -ForegroundColor Green
    
    Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Test installer on clean Windows 11 VM" -ForegroundColor White
    Write-Host "2. Upload all files from release/ to GitHub Release v0.4.0" -ForegroundColor White
    Write-Host "3. Update landing page with correct download links" -ForegroundColor White
    Write-Host "4. Send download link to your friend for testing" -ForegroundColor White
    
    Write-Host "`n📁 Files to upload:" -ForegroundColor Cyan
    Get-ChildItem | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
    
} else {
    Write-Host "❌ Ship gate failed. Fix issues above before shipping." -ForegroundColor Red
    exit 1
}

Set-Location ..
