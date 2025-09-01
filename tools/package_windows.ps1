# QuietPatch Windows Distribution Packager
# Creates the final Windows distribution package

param(
    [string]$Version = "0.2.2",
    [string]$OutputDir = "dist/windows"
)

Write-Host "Packaging QuietPatch for Windows v$Version" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check prerequisites
$pexPath = "dist/quietpatch-win-py311.pex"
$batchPath = "packaging/windows/run_quietpatch.bat"
$readmePath = "packaging/windows/README-Windows.txt"

if (!(Test-Path $pexPath)) {
    Write-Host "ERROR: PEX file not found at $pexPath" -ForegroundColor Red
    Write-Host "Please build the PEX first using tools/build_pex.ps1" -ForegroundColor Yellow
    exit 1
}

if (!(Test-Path $batchPath)) {
    Write-Host "ERROR: Batch file not found at $batchPath" -ForegroundColor Red
    exit 1
}

if (!(Test-Path $readmePath)) {
    Write-Host "ERROR: README file not found at $readmePath" -ForegroundColor Red
    exit 1
}

# Create output directory
if (Test-Path $OutputDir) {
    Remove-Item $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

# Create the distribution structure
$distName = "QuietPatch-Windows-v$Version"
$distPath = Join-Path $OutputDir $distName
New-Item -ItemType Directory -Path $distPath -Force | Out-Null

Write-Host "Creating distribution structure..." -ForegroundColor Yellow

# Copy main files
Copy-Item $pexPath (Join-Path $distPath "quietpatch-win-py311.pex")
Copy-Item $batchPath (Join-Path $distPath "run_quietpatch.bat")
Copy-Item $readmePath (Join-Path $distPath "README-Windows.txt")

# Create catalog directory
$catalogPath = Join-Path $distPath "catalog"
New-Item -ItemType Directory -Path $catalogPath -Force | Out-Null

# Copy database files if they exist
$dbFiles = @(
    "data/db/cpe_to_cves.json",
    "data/db/cve_meta.json", 
    "data/db/kev.json",
    "data/db/epss.csv",
    "data/db/aliases.json",
    "data/db/affects.json"
)

foreach ($dbFile in $dbFiles) {
    if (Test-Path $dbFile) {
        $fileName = Split-Path $dbFile -Leaf
        Copy-Item $dbFile (Join-Path $catalogPath $fileName)
        Write-Host "✓ Copied $fileName to catalog/" -ForegroundColor Green
    } else {
        Write-Host "⚠ Database file not found: $dbFile" -ForegroundColor Yellow
    }
}

# Create policies directory
$policiesPath = Join-Path $distPath "policies"
New-Item -ItemType Directory -Path $policiesPath -Force | Out-Null

# Copy policy files if they exist
$policyFiles = @(
    "config/policy.yml",
    "config/aliases.yml"
)

foreach ($policyFile in $policyFiles) {
    if (Test-Path $policyFile) {
        $fileName = Split-Path $policyFile -Leaf
        Copy-Item $policyFile (Join-Path $policiesPath $fileName)
        Write-Host "✓ Copied $fileName to policies/" -ForegroundColor Green
    } else {
        Write-Host "⚠ Policy file not found: $policyFile" -ForegroundColor Yellow
    }
}

# Create the ZIP archive
$zipPath = Join-Path $OutputDir "$distName.zip"
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow

try {
    Compress-Archive -Path $distPath -DestinationPath $zipPath -Force
    Write-Host "✓ ZIP archive created: $zipPath" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create ZIP archive: $_" -ForegroundColor Red
    exit 1
}

# Show distribution contents
Write-Host ""
Write-Host "Distribution Contents:" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Get-ChildItem -Path $distPath -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Replace($distPath, "").TrimStart("\")
    $size = if ($_.PSIsContainer) { "DIR" } else { "$([math]::Round($_.Length / 1KB, 2)) KB" }
    Write-Host "$relativePath`t$size" -ForegroundColor Cyan
}

# Show archive info
$zipInfo = Get-Item $zipPath
Write-Host ""
Write-Host "Archive Information:" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "File: $zipPath" -ForegroundColor Cyan
Write-Host "Size: $([math]::Round($zipInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host "Created: $($zipInfo.CreationTime)" -ForegroundColor Cyan

Write-Host ""
Write-Host "Distribution package created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the package on a fresh Windows VM" -ForegroundColor Green
Write-Host "2. Verify all files are accessible and functional" -ForegroundColor Green
Write-Host "3. Test the batch file by double-clicking in Explorer" -ForegroundColor Green
Write-Host "4. Verify the PEX runs from various locations and user contexts" -ForegroundColor Green
Write-Host ""
Write-Host "Distribution ready for release!" -ForegroundColor Green
