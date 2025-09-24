#Requires -Version 5
$ErrorActionPreference = "Stop"

function Require-Python311 {
  $candidates = @("py -3.12","py -3.11","python","python3")
  foreach ($c in $candidates) {
    try {
      $ver = & $c -c "import sys;print('.'.join(map(str,sys.version_info[:3])))" 2>$null
      if ($LASTEXITCODE -eq 0) {
        $ok = & $c -c "import sys;exit(0 if sys.version_info[:2] >= (3,11) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { return $c }
      }
    } catch {}
  }
  throw "Python ≥3.11 not found. Install from https://www.python.org/downloads/windows/"
}

$PY = Require-Python311

# pipx
try { pipx --version *>$null } catch {
  & $PY -m pip install --user pipx
  & $PY -m pipx ensurepath
  $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

# Install package
$version = $env:QUIETPATCH_VERSION; if (-not $version) { $version = "0.3.0" }
pipx install --force "quietpatch==$version"

# Offline DB
$QP_HOME = if ($env:QUIETPATCH_HOME) { $env:QUIETPATCH_HOME } else { "$env:USERPROFILE\.quietpatch" }
New-Item -ItemType Directory -Force -Path "$QP_HOME\db" | Out-Null

$tag = if ($env:QUIETPATCH_DB_TAG) { $env:QUIETPATCH_DB_TAG } else { "db" }
$dbFile = if ($env:QUIETPATCH_DB_FILE) { $env:QUIETPATCH_DB_FILE } else { "qp_db-latest.tar.zst" }
$base = "https://github.com/Matt-C-G/QuietPatch/releases/download/$tag"
Invoke-WebRequest "$base/$dbFile" -OutFile "$QP_HOME\db\$dbFile"

# Extract
if ($dbFile -like "*.zst") {
  $zstd = Get-Command zstd -ErrorAction SilentlyContinue
  if (-not $zstd) { Write-Host "Install zstd or 7-Zip to extract .zst"; throw }
  & zstd -d -f "$QP_HOME\db\$dbFile"
} elseif ($dbFile -like "*.gz") {
  & $PY -c "import gzip,shutil,sys;shutil.copyfileobj(gzip.open(sys.argv[1],'rb'),open(sys.argv[1][:-3],'wb'))" "$QP_HOME\db\$dbFile"
} else {
  throw "Unknown db extension: $dbFile"
}

Write-Host "✅ QuietPatch installed. Run: quietpatch scan --offline"

