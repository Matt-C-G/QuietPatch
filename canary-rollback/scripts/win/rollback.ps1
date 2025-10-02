param([string]$BundleRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) + "\..\..")
$ErrorActionPreference = 'Stop'
$manifest = Get-Content (Join-Path $BundleRoot 'manifest.json') -Raw | ConvertFrom-Json
$target = $manifest.targets | Where-Object { $_.os -eq 'windows' }
$logDir = $manifest.logging.dir_win; New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir "rollback_$(Get-Date -Format yyyyMMdd_HHmmss).log"
Start-Transcript -Path $log -Append | Out-Null

function Get-SHA256($path){
  if (Test-Path $path) {
    return (Get-FileHash -Algorithm SHA256 -Path $path).Hash.ToLower()
  }
  return $null
}

$artifact = Join-Path $BundleRoot $target.rollback_artifact
if (!(Test-Path $artifact)) { Write-Error "Rollback artifact not found: $artifact" }

# Verify rollback artifact integrity if SHA256 provided
if ($target.sha256.rollback_artifact -and $target.sha256.rollback_artifact -ne "<FILL_AT_BUILD>") {
  $actualHash = Get-SHA256 $artifact
  if ($actualHash -ne $target.sha256.rollback_artifact.ToLower()) {
    Write-Error "SHA256 mismatch for rollback artifact $artifact. Expected: $($target.sha256.rollback_artifact), Got: $actualHash"
  }
}

$cmd = ($target.rollback_cmd -replace '{{rollback_artifact}}', [Regex]::Escape($artifact))
Write-Host "Executing rollback: $cmd"
$proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c $cmd" -PassThru -Wait
if ($proc.ExitCode -ne 0) { Write-Error "Rollback exit code $($proc.ExitCode)" }

Stop-Transcript; exit 0
