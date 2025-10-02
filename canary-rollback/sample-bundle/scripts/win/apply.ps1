param([string]$BundleRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) + "\..\..")
$ErrorActionPreference = 'Stop'
$manifest = Get-Content (Join-Path $BundleRoot 'manifest.json') -Raw | ConvertFrom-Json
$target = $manifest.targets | Where-Object { $_.os -eq 'windows' }
$logDir = $manifest.logging.dir_win; New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir "apply_$(Get-Date -Format yyyyMMdd_HHmmss).log"
Start-Transcript -Path $log -Append | Out-Null

function Expand-Cmd($cmd, $artifact){
  return ($cmd -replace '{{artifact}}', [Regex]::Escape($artifact))
}

function Get-SHA256($path){
  if (Test-Path $path) {
    return (Get-FileHash -Algorithm SHA256 -Path $path).Hash.ToLower()
  }
  return $null
}

# Preflight checks
if ($manifest.gates.preflight -contains 'ac_power') {
  $onAC = (Get-WmiObject -Class Win32_Battery | ForEach-Object { $_.BatteryStatus }) -contains 2
  if (-not $onAC -and (Get-WmiObject -Class Win32_Battery)) {
    Write-Error "AC power required."
  }
}

if ($manifest.gates.preflight -contains 'disk_space_mb>=500') {
  $freeSpace = [math]::Round((Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1MB)
  if ($freeSpace -lt 500) {
    Write-Error "Insufficient disk space: $freeSpace MB available, need 500 MB"
  }
}

# Verify artifact integrity if SHA256 provided
$artifact = Join-Path $BundleRoot $target.artifact
if (!(Test-Path $artifact)) { Write-Error "Artifact not found: $artifact" }

if ($target.sha256.artifact -and $target.sha256.artifact -ne "<FILL_AT_BUILD>") {
  $actualHash = Get-SHA256 $artifact
  if ($actualHash -ne $target.sha256.artifact.ToLower()) {
    Write-Error "SHA256 mismatch for $artifact. Expected: $($target.sha256.artifact), Got: $actualHash"
  }
}

$cmd = Expand-Cmd $target.install_cmd $artifact
Write-Host "Executing: $cmd"
$proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c $cmd" -PassThru -Wait
if ($proc.ExitCode -ne 0) { Write-Error "Installer exit code $($proc.ExitCode)" }

Stop-Transcript; exit 0
