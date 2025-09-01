# QuietPatch agent wrapper (offline-first)
# Logs to C:\ProgramData\QuietPatch\logs

$ErrorActionPreference = 'Stop'
$Root = 'C:\Program Files\QuietPatch'
$Data = 'C:\ProgramData\QuietPatch'
$Logs = Join-Path $Data 'logs'
New-Item -ItemType Directory -Force -Path $Logs | Out-Null

$Log = Join-Path $Logs 'quietpatch.log'
$Err = Join-Path $Logs 'quietpatch.err'

function Write-Log($msg) { "$(Get-Date -Format o) $msg" | Tee-Object -FilePath $Log -Append }

Write-Log "Starting QuietPatch scan"

# Prefer system Python 3.13, else an embedded runtime at $Root\python\python.exe
$PyCandidates = @(
  'C:\Program Files\Python313\python.exe',
  'C:\Python313\python.exe',
  (Join-Path $Root 'python\python.exe')
) | Where-Object { Test-Path $_ }

if ($PyCandidates.Count -eq 0) {
  "No Python 3.13 found" | Out-File -FilePath $Err -Append
  exit 1
}

$Py = $PyCandidates[0]
$Pex = Join-Path $Root 'quietpatch.pex'

$env:QP_OFFLINE = '1'
$env:QP_DISABLE_AUTO_SYNC = '1'
$env:QP_DATA_DIR = $Data

# Ensure data dirs exist
New-Item -ItemType Directory -Force -Path $Data | Out-Null

# If a DB snapshot exists under $Root\db-*.tar.*, unpack to $Data\db once
$dbDir = Join-Path $Data 'db'
if (!(Test-Path $dbDir)) {
  New-Item -ItemType Directory -Force -Path $dbDir | Out-Null
  $Snapshot = Get-ChildItem -Path $Root -Filter 'db-*.tar.*' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($Snapshot) {
    Write-Log "Unpacking DB snapshot $($Snapshot.Name)"
    try {
      if ($Snapshot.Name -like '*.zst') {
        # Needs zstandard on host; if not available, ship a tiny zstd.exe with the package.
        & (Join-Path $Root 'zstd.exe') -d -c $Snapshot.FullName | tar -x -C $dbDir
      } else {
        tar -xf $Snapshot.FullName -C $dbDir
      }
    } catch {
      $_ | Out-File -FilePath $Err -Append
    }
  }
}

# Run scan
$cmd = @($Py, $Pex, 'scan', '--also-report')
Write-Log "Exec: $($cmd -join ' ')"
try {
  & $Py $Pex scan --also-report 1>> $Log 2>> $Err
} catch {
  $_ | Out-File -FilePath $Err -Append
  exit 2
}

Write-Log "QuietPatch scan finished"


