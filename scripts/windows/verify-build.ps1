# QuietPatch Windows Build Verification Script
# Run this after .\Makefile.ps1 all to verify everything is correct

param(
    [string]$Version = '0.4.0'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Write-Host "🔍 QuietPatch Windows Build Verification" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Check release directory exists
if (-not (Test-Path "release")) {
    Write-Host "❌ Release directory not found. Run .\Makefile.ps1 all first." -ForegroundColor Red
    exit 1
}

Write-Host "`n📁 Checking release artifacts..." -ForegroundColor Yellow

# Expected files
$ExpectedFiles = @(
    "QuietPatch-Setup-v$Version.exe",
    "quietpatch-cli-v$Version-win64.zip",
    "SHA256SUMS.txt",
    "SHA256SUMS.txt.minisig",
    "README-QuickStart.txt",
    "VERIFY.md"
)

$MissingFiles = @()
foreach ($file in $ExpectedFiles) {
    $path = "release\$file"
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        Write-Host "✅ $file ($([math]::Round($size/1MB, 2)) MB)" -ForegroundColor Green
    } else {
        Write-Host "❌ $file (MISSING)" -ForegroundColor Red
        $MissingFiles += $file
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Host "`n❌ Missing files: $($MissingFiles -join ', ')" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔐 Verifying checksums..." -ForegroundColor Yellow

# Check SHA256SUMS.txt format
$ShaFile = "release\SHA256SUMS.txt"
$ShaContent = Get-Content $ShaFile
Write-Host "SHA256SUMS.txt contents:" -ForegroundColor Cyan
$ShaContent | ForEach-Object { Write-Host "  $_" -ForegroundColor White }

# Verify installer checksum
$InstallerFile = "release\QuietPatch-Setup-v$Version.exe"
if (Test-Path $InstallerFile) {
    $InstallerHash = (Get-FileHash $InstallerFile -Algorithm SHA256).Hash
    $ShaLine = $ShaContent | Where-Object { $_ -match "QuietPatch-Setup-v$Version\.exe" }
    if ($ShaLine -match $InstallerHash) {
        Write-Host "✅ Installer checksum verified" -ForegroundColor Green
    } else {
        Write-Host "❌ Installer checksum mismatch" -ForegroundColor Red
        Write-Host "  Expected: $InstallerHash" -ForegroundColor Yellow
        Write-Host "  Found: $ShaLine" -ForegroundColor Yellow
    }
}

Write-Host "`n🔑 Verifying minisign signature..." -ForegroundColor Yellow

# Check if minisign is available
if (Get-Command minisign -ErrorAction SilentlyContinue) {
    $PubKey = "RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR"
    try {
        Push-Location release
        $result = minisign -Vm SHA256SUMS.txt -P $PubKey 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Minisign signature verified" -ForegroundColor Green
        } else {
            Write-Host "❌ Minisign signature verification failed" -ForegroundColor Red
            Write-Host "  Output: $result" -ForegroundColor Yellow
        }
        Pop-Location
    } catch {
        Write-Host "❌ Minisign verification error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  Minisign not available - skipping signature verification" -ForegroundColor Yellow
}

Write-Host "`n📦 Checking portable CLI contents..." -ForegroundColor Yellow

# Check portable CLI ZIP contents
$ZipFile = "release\quietpatch-cli-v$Version-win64.zip"
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

Write-Host "`n📋 Checking Inno Setup installer..." -ForegroundColor Yellow

# Check installer file size and basic properties
if (Test-Path $InstallerFile) {
    $InstallerInfo = Get-Item $InstallerFile
    $SizeMB = [math]::Round($InstallerInfo.Length / 1MB, 2)
    Write-Host "Installer: $($InstallerInfo.Name) ($SizeMB MB)" -ForegroundColor Cyan
    Write-Host "Created: $($InstallerInfo.CreationTime)" -ForegroundColor Cyan
    
    if ($SizeMB -lt 5) {
        Write-Host "⚠️  Installer seems small - check if all files are included" -ForegroundColor Yellow
    } elseif ($SizeMB -gt 100) {
        Write-Host "⚠️  Installer seems large - check for unnecessary files" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Installer size looks reasonable" -ForegroundColor Green
    }
}

Write-Host "`n🎯 Build Verification Summary" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

if ($MissingFiles.Count -eq 0) {
    Write-Host "✅ All required files present" -ForegroundColor Green
} else {
    Write-Host "❌ Missing files: $($MissingFiles.Count)" -ForegroundColor Red
}

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test installer on clean Windows VM" -ForegroundColor White
Write-Host "2. Test portable CLI extraction and execution" -ForegroundColor White
Write-Host "3. Verify Start Menu shortcuts after installation" -ForegroundColor White
Write-Host "4. Upload to GitHub Release" -ForegroundColor White
Write-Host "5. Update landing page download links" -ForegroundColor White

Write-Host "`n🚀 Windows build verification complete!" -ForegroundColor Green
