$ErrorActionPreference = "Stop"

$Prefix = if ($Env:QUIETPATCH_PREFIX) { $Env:QUIETPATCH_PREFIX } else { "$Env:LOCALAPPDATA\QuietPatch" }
$Bin = Join-Path $Prefix "bin"

Write-Host "🗑️  Uninstalling QuietPatch..." -ForegroundColor Yellow

# Check if installation exists
if (-not (Test-Path $Bin)) {
    Write-Host "❌ QuietPatch installation not found at $Bin" -ForegroundColor Red
    Write-Host "   Nothing to uninstall."
    exit 0
}

Write-Host "→ Removing QuietPatch from $Bin"
Remove-Item -Recurse -Force $Bin -ErrorAction SilentlyContinue

# Remove PATH entry if present
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -like "*$Bin*") {
    $NewPath = ($UserPath.Split(';') | Where-Object { $_ -ne $Bin }) -join ';'
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Write-Host "✓ Removed PATH entry"
}

# Cache cleanup
$Cache = Join-Path $Env:LOCALAPPDATA "quietpatch"
if (Test-Path $Cache) {
    Remove-Item -Recurse -Force $Cache
    Write-Host "✓ Removed cache $Cache"
}

# Remove the parent directory if it's empty
if ((Test-Path $Prefix) -and ((Get-ChildItem $Prefix -Force | Measure-Object).Count -eq 0)) {
    Remove-Item -Path $Prefix -Force
    Write-Host "✓ Removed empty parent directory: $Prefix"
}

Write-Host "✓ QuietPatch uninstalled" -ForegroundColor Green
