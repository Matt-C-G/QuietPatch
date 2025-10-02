param([string]$BundleRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) + "\..\..")
$ErrorActionPreference = 'Stop'
$manifest = Get-Content (Join-Path $BundleRoot 'manifest.json') -Raw | ConvertFrom-Json
$target = $manifest.targets | Where-Object { $_.os -eq 'windows' }
$logDir = $manifest.logging.dir_win; New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir "verify_$(Get-Date -Format yyyyMMdd_HHmmss).log"
Start-Transcript -Path $log -Append | Out-Null

$verify = $target.verify
if ($verify.type -eq 'file_version') {
  if (!(Test-Path $verify.path)) { Write-Error "Missing file: $($verify.path)"; Stop-Transcript; exit 2 }
  $v = (Get-Item $verify.path).VersionInfo.FileVersion
  Write-Host "File version: $v ; expect $($verify.version)"
  if ($v -like "$($verify.version)*") { Stop-Transcript; exit 0 } else { Stop-Transcript; exit 1 }
}
Write-Error "Unknown verify type: $($verify.type)"; Stop-Transcript; exit 2
