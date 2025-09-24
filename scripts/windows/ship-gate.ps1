param(
  [string]$Version = "0.4.0",
  [Parameter(Mandatory=$true)][string]$PublicKey,
  [switch]$DoInstallSmoke = $false,
  [switch]$GhUpload = $false
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Say([string]$m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Fail([string]$m) { Write-Host "XX  $m" -ForegroundColor Red; exit 1 }
function Require-Cmd([string]$cmd, [string]$hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { Fail "Missing '$cmd'. $hint" }
}

# ---- Env check ----
Say "Checking toolchain"
Require-Cmd "py" "Install Python 3.12 from python.org"
Require-Cmd "minisign" "Install: choco install minisign"
$Iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $Iscc)) { Fail "Inno Setup not found at '$Iscc'. Install Inno Setup 6." }

# Optional
$SevenZ = (Get-Command 7z -ErrorAction SilentlyContinue)
if (-not $SevenZ) { Write-Host "i  7-Zip not found; will fall back to Compress-Archive" -ForegroundColor Yellow }
if ($GhUpload) { Require-Cmd "gh" "Install GitHub CLI: https://cli.github.com" }

# Verify Python 3.12 available (Makefile.ps1 will create venv)
try {
  $pyver = & py -3.12 -V
} catch {
  Fail "Python 3.12 not found. Install from https://www.python.org/downloads/windows/"
}
Say "Python: $pyver"

# ---- Run local build (Makefile.ps1 handles setup/build/package/checksums/sign) ----
if (-not (Test-Path ".\Makefile.ps1")) { Fail "Makefile.ps1 not found at repo root." }
Say "Running locked build pipeline"
& .\Makefile.ps1 all -Version $Version

# ---- Verify artifacts ----
$Rel = Resolve-Path ".\release" | Select-Object -ExpandProperty Path
$Setup = Join-Path $Rel "QuietPatch-Setup-v$Version.exe"
$ZipCli = Join-Path $Rel "quietpatch-cli-v$Version-win64.zip"
$Sha = Join-Path $Rel "SHA256SUMS.txt"
$Sig = Join-Path $Rel "SHA256SUMS.txt.minisig"
$QS  = Join-Path $Rel "README-QuickStart.txt"

Say "Checking artifact presence"
$need = @($Setup, $ZipCli, $Sha, $Sig, $QS)
$missing = $need | Where-Object { -not (Test-Path $_) }
if ($missing) { $missing | ForEach-Object { Write-Host "missing: $_" -ForegroundColor Red }; Fail "Artifacts missing." }

# Size sanity
Say "Size sanity checks"
if ((Get-Item $Setup).Length -lt 15MB) { Fail "Installer looks too small (<15MB): $Setup" }
if ((Get-Item $ZipCli).Length -lt 5MB)  { Fail "CLI zip looks too small (<5MB): $ZipCli" }

# ---- Verify checksums & signature ----
Say "Verifying minisign signature"
Push-Location $Rel
& minisign -Vm $Sha -P $PublicKey | Out-Null
Say "Recomputing local SHA256 and matching"
$map = @{}
Get-Content $Sha | ForEach-Object {
  if ($_ -match '^(?<hash>[0-9a-fA-F]{64}) \*(?<file>.+)$') {
    $map[$matches.file] = $matches.hash.ToLower()
  }
}
foreach ($kv in $map.GetEnumerator()) {
  $f = $kv.Key; $h = $kv.Value
  if (-not (Test-Path $f)) { Fail "SHA256SUMS references missing file: $f" }
  $local = (Get-FileHash $f -Algorithm SHA256).Hash.ToLower()
  if ($local -ne $h) { Fail "SHA256 mismatch for $f" }
}
Pop-Location
Say "Signature and checksums OK"

# ---- Optional: silent install smoke test ----
if ($DoInstallSmoke) {
  $SmokeDir = "C:\QuietPatchTest"
  Say "Running silent install to $SmokeDir"
  & $Setup /SP- /VERYSILENT /NORESTART /DIR="$SmokeDir" | Out-Null

  $GuiPath = Join-Path $SmokeDir "QuietPatchWizard.exe"
  $CliPath = Join-Path $SmokeDir "quietpatch.exe"
  if (-not (Test-Path $GuiPath)) { Fail "GUI exe not found after install: $GuiPath" }
  if (-not (Test-Path $CliPath)) { Fail "CLI exe not found after install: $CliPath" }

  Say "CLI help smoke"
  & $CliPath --help | Select-Object -First 3 | Out-Null

  Say "Uninstalling silently"
  $Uninst = Get-ChildItem "$SmokeDir\unins*.exe" | Select-Object -First 1
  if ($null -eq $Uninst) { Fail "Uninstaller not found in $SmokeDir" }
  & $Uninst.FullName /VERYSILENT /NORESTART | Out-Null
  if (Test-Path $SmokeDir) { Write-Host "Note: $SmokeDir still exists (expected if files in use)." -ForegroundColor Yellow }
  Say "Silent install smoke OK"
}

# ---- Optional: upload to GitHub Release ----
if ($GhUpload) {
  $tag = "v$Version"
  Say "Ensuring release $tag exists"
  $rel = & gh release view $tag 2>$null
  if ($LASTEXITCODE -ne 0) {
    Say "Creating release $tag"
    & gh release create $tag -t "QuietPatch v$Version" -n "Windows release (installer + portable CLI + signed checksums)"
  }
  Say "Uploading artifacts"
  & gh release upload $tag $Setup $ZipCli $Sha $Sig --clobber
  Say "Uploaded to GitHub release $tag"
}

Say "Windows ship-gate PASSED for v$Version"
exit 0