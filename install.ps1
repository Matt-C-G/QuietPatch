#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

# ---- Config ----
$Repo = 'matt-c-g/quietpatch'
$Api  = "https://api.github.com/repos/$Repo/releases/latest"
$Root = "$env:LOCALAPPDATA\QuietPatch"
$Bin  = "$Root\current"
$WithDb = $true   # set to $false to skip DB download

# ---- Helpers ----
function Note($msg){ Write-Host "==> $msg" -ForegroundColor Cyan }
function Fatal($msg){ Write-Error $msg; exit 1 }
function Get-Headers {
  if ($env:GH_TOKEN) { return @{ Authorization = "Bearer $($env:GH_TOKEN)" } }
  return $null
}
function Get-Json($url){
  $headers = Get-Headers
  try {
    if ($headers) { return Invoke-RestMethod -Uri $url -Headers $headers -UseBasicParsing }
    else { return Invoke-RestMethod -Uri $url -UseBasicParsing }
  } catch {
    if ($_.Exception.Response.StatusCode.Value__ -eq 403) {
      Fatal "GitHub API rate-limited. Set GH_TOKEN to increase limits."
    }
    throw
  }
}
function Get-File($url, $out){
  $headers = Get-Headers
  if ($headers) { Invoke-WebRequest -Uri $url -OutFile $out -Headers $headers -UseBasicParsing }
  else { Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing }
}

# GitHub API (no auth needed for public)
try {
  Note "Fetching latest release metadata…"
  $rel = Get-Json $Api
} catch {
  Fatal "GitHub API failed: $($_.Exception.Message)"
}

# Detect arch
$arch = if ($env:PROCESSOR_ARCHITECTURE -match 'ARM64') { 'arm64' } else { 'x64|amd64' }
$pattern = "windows.+($arch)"
Note "Pattern: $pattern"

# Select asset
$asset = $rel.assets | Where-Object { $_.name -match $pattern } | Select-Object -First 1
if (-not $asset) { Fatal "No asset matched: $pattern" }
$assetUrl = $asset.browser_download_url
Note "Asset: $($asset.name)"

# Optional: SHA256SUMS
$sum = $rel.assets | Where-Object { $_.name -match 'SHA256SUMS' } | Select-Object -First 1
$sumUrl = $sum.browser_download_url

# Optional: DB snapshot
$db = $null
if ($WithDb) {
  $db = $rel.assets | Where-Object { $_.name -match '^db-.*\.(tar\.(zst|gz))$' } | Select-Object -First 1
}

# Prep dirs
New-Item -Force -ItemType Directory -Path $Bin | Out-Null
Set-Location (New-Item -Force -ItemType Directory -Path ([System.IO.Path]::GetTempPath() + '\qp-inst') )

# Download asset
Note "Downloading asset…"
Get-File $assetUrl ".\asset"

# Optional verify
if ($sumUrl) {
  Note "Verifying SHA256…"
  Get-File $sumUrl ".\SHA256SUMS"
  $expected = (Get-Content .\SHA256SUMS | Select-String -SimpleMatch $asset.name | Select-Object -First 1).ToString().Split(' ')[0]
  if (-not $expected) { Note "No matching entry in SHA256SUMS; skipping verification." }
  else {
    $actual = (Get-FileHash .\asset -Algorithm SHA256).Hash.ToLower()
    if ($actual -ne $expected.ToLower()) { Fatal "Checksum mismatch! expected=$expected actual=$actual" }
  }
} else {
  Note "No SHA256SUMS found; skipping verification."
}

# Expand/install
Note "Installing to $Bin"
if ($asset.name -match '\.zip$') {
  Expand-Archive -Path .\asset -DestinationPath $Bin -Force
} elseif ($asset.name -match '\.pex$') {
  Copy-Item .\asset "$Bin\quietpatch-win-py311.pex"
} else {
  # fallback: try to treat it as zip
  try { Expand-Archive -Path .\asset -DestinationPath $Bin -Force } catch { Copy-Item .\asset "$Bin\$($asset.name)" }
}

# Optional DB
if ($db) {
  Note "Downloading offline DB: $($db.name)"
  New-Item -Force -ItemType Directory -Path "$Root\db" | Out-Null
  Get-File $db.browser_download_url "$Root\db\$($db.name)"
}

# Create shim on PATH
$UserBin = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"
$Shim = Join-Path $UserBin 'quietpatch.cmd'
Note "Creating launcher: $Shim"
@"
@echo off
set PEX_ROOT=$Root\.pexroot
if exist "$Bin\run_quietpatch.bat" (
  call "$Bin\run_quietpatch.bat" %*
  exit /b %ERRORLEVEL%
)
for %%F in ("$Bin\quietpatch*.pex") do (
  where py >nul 2>&1 || (echo Install Python 3.11+ and retry.& exit /b 86)
  py -3.11 "%%~fF" %*
  exit /b %ERRORLEVEL%
)
echo QuietPatch runtime not found in $Bin
exit /b 1
"@ | Out-File -Encoding ASCII -FilePath $Shim -Force

# Ensure Bin is on PATH for current user (in case WindowsApps is blocked)
$needPath = -not ($env:PATH -split ';' | Where-Object { $_ -eq $Bin })
if ($needPath) {
  Note "Adding $Bin to your user PATH"
  $newPath = ([Environment]::GetEnvironmentVariable('PATH','User') + ";$Bin").Trim(';')
  [Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')
}

Write-Host ""
Write-Host "✅ Installed. Open a NEW PowerShell and run:" -ForegroundColor Green
Write-Host "  quietpatch scan --also-report --open"
if ($db) { Write-Host "  (offline DB at $Root\db\$($db.name))" }
