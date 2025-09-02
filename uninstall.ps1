$ErrorActionPreference = "Stop"

$Owner = "Matt-C-G"
$Repo  = "QuietPatch"
$Prefix = if ($Env:QUIETPATCH_PREFIX) { $Env:QUIETPATCH_PREFIX } else { "$Env:LOCALAPPDATA\QuietPatch" }
$Bin = Join-Path $Prefix "bin"

Write-Host "🗑️  Uninstalling QuietPatch..." -ForegroundColor Yellow

# Check if installation exists
if (-not (Test-Path $Bin)) {
    Write-Host "❌ QuietPatch installation not found at $Bin" -ForegroundColor Red
    Write-Host "   Nothing to uninstall."
    exit 0
}

# Remove from PATH (User)
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -like "*$Bin*") {
    Write-Host "→ Removing from PATH..."
    $NewPath = ($UserPath -split ';' | Where-Object { $_ -ne $Bin }) -join ';'
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Write-Host "✓ Removed from PATH"
}

# Remove the installation directory
Write-Host "→ Removing installation directory: $Bin"
Remove-Item -Path $Bin -Recurse -Force

# Remove cache directory
$CacheDir = Join-Path $Env:LOCALAPPDATA "quietpatch"
if (Test-Path $CacheDir) {
    Write-Host "→ Removing cache directory: $CacheDir"
    Remove-Item -Path $CacheDir -Recurse -Force
}

# Remove the parent directory if it's empty
if ((Test-Path $Prefix) -and ((Get-ChildItem $Prefix -Force | Measure-Object).Count -eq 0)) {
    Write-Host "→ Removing empty parent directory: $Prefix"
    Remove-Item -Path $Prefix -Force
}

Write-Host ""
Write-Host "✓ QuietPatch uninstalled successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: You may need to restart your terminal or run 'refreshenv' to clear command cache."
