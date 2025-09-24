# QuietPatch v0.4.0 Windows Build Script
# Run from repo root in PowerShell

param(
    [switch]$SkipBuild,
    [switch]$SkipPackage,
    [switch]$SkipSign,
    [string]$PythonVersion = "3.12"
)

Write-Host "🚀 QuietPatch v0.4.0 Windows Build Script" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python 3.12
try {
    $pythonVersion = & py -3.12 --version 2>&1
    if ($pythonVersion -match "Python 3\.12\.\d+") {
        Write-Host "✅ Python 3.12 found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python 3.12 not found"
    }
} catch {
    Write-Host "❌ Python 3.12 not found. Please install from python.org" -ForegroundColor Red
    exit 1
}

# Check Inno Setup
$innoSetup = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (Test-Path $innoSetup) {
    Write-Host "✅ Inno Setup 6 found" -ForegroundColor Green
} else {
    Write-Host "❌ Inno Setup 6 not found. Please install from jrsoftware.org" -ForegroundColor Red
    exit 1
}

# Check 7-Zip
try {
    & 7z -h | Out-Null
    Write-Host "✅ 7-Zip found" -ForegroundColor Green
} catch {
    Write-Host "❌ 7-Zip not found. Installing via Chocolatey..." -ForegroundColor Yellow
    choco install -y 7zip
}

# Check minisign
try {
    & minisign -V | Out-Null
    Write-Host "✅ minisign found" -ForegroundColor Green
} catch {
    Write-Host "❌ minisign not found. Installing via Chocolatey..." -ForegroundColor Yellow
    choco install -y minisign
}

# Clean and setup environment
Write-Host "`n🧹 Setting up build environment..." -ForegroundColor Yellow

if (Test-Path ".venv") {
    Remove-Item -Recurse -Force .venv
}

# Create virtual environment
py -3.12 -m venv .venv
& .\.venv\Scripts\Activate.ps1

# Verify Python version in venv
$venvVersion = & python --version
Write-Host "✅ Virtual environment Python: $venvVersion" -ForegroundColor Green

# Install dependencies with binary wheels only
Write-Host "`n📦 Installing dependencies (binary wheels only)..." -ForegroundColor Yellow

$env:PIP_ONLY_BINARY = ":all:"
pip install --upgrade pip wheel
pip install pyinstaller==6.6.0 cryptography==42.0.7

# Install runtime dependencies
pip install -r requirements.txt

if (-not $SkipBuild) {
    Write-Host "`n🔨 Building executables..." -ForegroundColor Yellow
    
    # Build GUI
    Write-Host "Building GUI wizard..." -ForegroundColor Cyan
    pyinstaller build\quietpatch_wizard_win.spec
    
    # Build CLI
    Write-Host "Building CLI..." -ForegroundColor Cyan
    pyinstaller build\quietpatch_cli_win.spec
    
    Write-Host "✅ Build complete!" -ForegroundColor Green
}

if (-not $SkipPackage) {
    Write-Host "`n📦 Packaging artifacts..." -ForegroundColor Yellow
    
    # Create release directory
    if (Test-Path "release") {
        Remove-Item -Recurse -Force release
    }
    New-Item -ItemType Directory -Path "release" | Out-Null
    
    # Build Inno Setup installer
    Write-Host "Creating Windows installer..." -ForegroundColor Cyan
    & $innoSetup installer\windows\QuietPatch.iss
    
    if (Test-Path "Output\QuietPatch-Setup-v0.4.0.exe") {
        Copy-Item "Output\QuietPatch-Setup-v0.4.0.exe" "release\"
        Write-Host "✅ Installer created: release\QuietPatch-Setup-v0.4.0.exe" -ForegroundColor Green
    } else {
        Write-Host "❌ Installer not found in Output\ directory" -ForegroundColor Red
        exit 1
    }
    
    # Create portable CLI ZIP
    Write-Host "Creating portable CLI..." -ForegroundColor Cyan
    if (Test-Path "dist\quietpatch") {
        7z a release\quietpatch-cli-v0.4.0-win64.zip .\dist\quietpatch\*
        Write-Host "✅ Portable CLI created: release\quietpatch-cli-v0.4.0-win64.zip" -ForegroundColor Green
    } else {
        Write-Host "❌ CLI build not found in dist\quietpatch" -ForegroundColor Red
        exit 1
    }
    
    # Copy documentation
    Copy-Item "README-QuickStart.md" "release\"
    Copy-Item "VERIFY.md" "release\"
    Write-Host "✅ Documentation copied" -ForegroundColor Green
}

if (-not $SkipSign) {
    Write-Host "`n🔐 Generating checksums and signing..." -ForegroundColor Yellow
    
    Set-Location release
    
    # Generate SHA256 checksums
    Write-Host "Generating SHA256 checksums..." -ForegroundColor Cyan
    Get-ChildItem -File | ForEach-Object {
        $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        "$hash *$($_.Name)" | Add-Content SHA256SUMS.txt
    }
    Write-Host "✅ SHA256SUMS.txt created" -ForegroundColor Green
    
    # Sign with minisign
    Write-Host "Signing checksums..." -ForegroundColor Cyan
    if (Test-Path "..\keys\quietpatch.key") {
        minisign -Sm SHA256SUMS.txt -s ..\keys\quietpatch.key
        Write-Host "✅ SHA256SUMS.txt.minisig created" -ForegroundColor Green
        
        # Verify signature
        Write-Host "Verifying signature..." -ForegroundColor Cyan
        minisign -Vm SHA256SUMS.txt -P "RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR"
        Write-Host "✅ Signature verified" -ForegroundColor Green
    } else {
        Write-Host "❌ Minisign key not found at ..\keys\quietpatch.key" -ForegroundColor Red
        Write-Host "Please copy your minisign key to the keys\ directory" -ForegroundColor Yellow
    }
    
    Set-Location ..
}

Write-Host "`n🎉 Windows build complete!" -ForegroundColor Green
Write-Host "Release artifacts in: release\" -ForegroundColor Cyan
Write-Host "`nFiles created:" -ForegroundColor Yellow
Get-ChildItem release | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }

Write-Host "`n📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the installer on a clean Windows VM" -ForegroundColor White
Write-Host "2. Upload artifacts to GitHub Release" -ForegroundColor White
Write-Host "3. Update landing page with download links" -ForegroundColor White
