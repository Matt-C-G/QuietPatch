# Requires: PowerShell 5+; runs as SYSTEM via SCCM/Intune/PDQ/etc.
param(
  [string]$BundleRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) + "\..\.."
)
$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $BundleRoot 'manifest.json'
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

$logDir = $manifest.logging.dir_win
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir "detect_$(Get-Date -Format yyyyMMdd_HHmmss).log"
Start-Transcript -Path $log -Append | Out-Null

function Get-ProductVersion {
  param([string[]]$ProductCodes)
  foreach ($code in $ProductCodes) {
    $key = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$code"
    if (Test-Path $key) {
      $v = (Get-ItemProperty $key).DisplayVersion
      if ($v) { return $v }
    }
    $keyWow = "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$code"
    if (Test-Path $keyWow) {
      $v = (Get-ItemProperty $keyWow).DisplayVersion
      if ($v) { return $v }
    }
  }
  return $null
}

function Get-FileVersion {
  param([string]$FilePath)
  if (Test-Path $FilePath) {
    return (Get-Item $FilePath).VersionInfo.FileVersion
  }
  return $null
}

$target = $manifest.targets | Where-Object { $_.os -eq 'windows' }
if (-not $target) { Write-Host "No Windows target in manifest"; Stop-Transcript; exit 0 }

# Try file-based detection first (more reliable)
$current = Get-FileVersion -FilePath $target.detect.file
if (-not $current -and $target.detect.registry_uninstall_displayname_prefix) {
  # Fallback to registry detection
  $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
  $regPathWow = "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
  
  $match = Get-ItemProperty $regPath -ErrorAction SilentlyContinue | 
    Where-Object { $_.DisplayName -like "$($target.detect.registry_uninstall_displayname_prefix)*" } |
    Select-Object -First 1
  
  if (-not $match) {
    $match = Get-ItemProperty $regPathWow -ErrorAction SilentlyContinue | 
      Where-Object { $_.DisplayName -like "$($target.detect.registry_uninstall_displayname_prefix)*" } |
      Select-Object -First 1
  }
  
  if ($match) {
    $current = $match.DisplayVersion
  }
}

Write-Host "Detected: $($target.display_name) version [$current] ; target [$($target.target_version)]"

# Exit code contract:
# 0 => up-to-date, 1 => needs remediation, 2 => not installed (treat as needs remediation)
if ($current -eq $target.target_version) { Stop-Transcript; exit 0 }
elseif ($current) { Stop-Transcript; exit 1 }
else { Stop-Transcript; exit 2 }
