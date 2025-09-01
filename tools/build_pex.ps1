# QuietPatch Windows PEX Builder
# Run this script to build the Windows PEX executable

param(
    [string]$Output = "dist/quietpatch-win-py311.pex",
    [string]$PythonVersion = "3.11"
)

Write-Host "Building QuietPatch PEX for Windows..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python $PythonVersion and add it to PATH" -ForegroundColor Yellow
    exit 1
}

# Check if pex is installed
try {
    $pexVersion = python -m pex --version 2>&1
    Write-Host "Found PEX: $pexVersion" -ForegroundColor Green
} catch {
    Write-Host "Installing PEX..." -ForegroundColor Yellow
    python -m pip install pex
}

# Create output directory
$outputDir = Split-Path $Output -Parent
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "Created output directory: $outputDir" -ForegroundColor Green
}

# Build the PEX
Write-Host "Building PEX executable..." -ForegroundColor Yellow
$buildCmd = @(
    "python", "-m", "pex", "quietpatch", "-c", "quietpatch",
    "-o", $Output,
    "--validate-entry-point", "--no-build", "--venv", "prepend", "--strip-pex-env"
)

Write-Host "Running: $($buildCmd -join ' ')" -ForegroundColor Cyan
& $buildCmd[0] $buildCmd[1..($buildCmd.Length-1)]

if ($LASTEXITCODE -eq 0) {
    Write-Host "PEX built successfully!" -ForegroundColor Green
    Write-Host "Output: $Output" -ForegroundColor Green
    
    # Show file info
    if (Test-Path $Output) {
        $fileInfo = Get-Item $Output
        Write-Host "File size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Green
        Write-Host "Created: $($fileInfo.CreationTime)" -ForegroundColor Green
    }
    
    # Test the PEX
    Write-Host "Testing PEX..." -ForegroundColor Yellow
    $env:PEX_ROOT = "C:\pex"
    $env:TEMP = "C:\t"
    $env:TMP = "C:\t"
    
    try {
        $helpOutput = python $Output --help 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PEX test passed!" -ForegroundColor Green
        } else {
            Write-Host "PEX test failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        }
    } catch {
        Write-Host "PEX test failed: $_" -ForegroundColor Red
    }
    
} else {
    Write-Host "PEX build failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}


