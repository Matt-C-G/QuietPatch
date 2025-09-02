$ErrorActionPreference = "Stop"

$Owner = "Matt-C-G"
$Repo  = "QuietPatch"
$Prefix = if ($Env:QUIETPATCH_PREFIX) { $Env:QUIETPATCH_PREFIX } else { "$Env:LOCALAPPDATA\QuietPatch" }
$Bin = Join-Path $Prefix "bin"
$Asset = "quietpatch-windows-x64.zip"
$Db = "db-latest.tar.zst"

New-Item -ItemType Directory -Force -Path $Bin | Out-Null
Set-Location $Bin

Write-Host "→ Downloading latest $Asset..."
Invoke-WebRequest "https://github.com/$Owner/$Repo/releases/latest/download/$Asset" -OutFile $Asset

Write-Host "→ Verifying checksum..."
Invoke-WebRequest "https://github.com/$Owner/$Repo/releases/latest/download/SHA256SUMS" -OutFile "SHA256SUMS"
$zipHash = (Get-FileHash $Asset -Algorithm SHA256).Hash.ToLower()
$refHash = (Select-String -Path "SHA256SUMS" -Pattern "$Asset").Line.Split()[0].ToLower()
if ($zipHash -ne $refHash) { throw "Checksum mismatch for $Asset" }

Write-Host "→ Extracting…"
Expand-Archive -Path $Asset -DestinationPath $Bin -Force

Write-Host "→ Downloading offline DB ($Db)…"
Invoke-WebRequest "https://github.com/$Owner/$Repo/releases/latest/download/$Db" -OutFile $Db
if (Select-String -Path "SHA256SUMS" -Pattern $Db -Quiet) {
  $dbHash = (Get-FileHash $Db -Algorithm SHA256).Hash.ToLower()
  $refDb  = (Select-String -Path "SHA256SUMS" -Pattern $Db).Line.Split()[0].ToLower()
  if ($dbHash -ne $refDb) { throw "Checksum mismatch for $Db" }
}

# Shim: adds a 'quietpatch' command (tolerant to legacy PEX names)
$shim = @'
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Env:PEX_ROOT = Join-Path $Root ".pexroot"
$pexCandidates = @("quietpatch.pex","quietpatch-win-py311.pex","quietpatch-windows-x64.pex")
$pex = $pexCandidates | Where-Object { Test-Path (Join-Path $Root $_) } | Select-Object -First 1
if (-not $pex) { throw "PEX not found in $Root. Expected one of: quietpatch.pex, quietpatch-win-py311.pex, quietpatch-windows-x64.pex" }
if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3.11 (Join-Path $Root $pex) @Args
} else {
  & python (Join-Path $Root $pex) @Args
}
'@
$shimPath = Join-Path $Bin "quietpatch.ps1"
$shim | Out-File -FilePath $shimPath -Encoding ASCII

# Add to PATH (User)
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$Bin*") {
  [Environment]::SetEnvironmentVariable("Path", "$UserPath;$Bin", "User")
  $Env:Path = "$Env:Path;$Bin"
  Write-Host "✓ Updated PATH for current user"
}

# Get version info for success message
$VersionInfo = "QuietPatch"
$__pex = $null
foreach ($c in @("quietpatch.pex","quietpatch-win-py311.pex","quietpatch-windows-x64.pex")) {
    $p = Join-Path $Bin $c
    if (Test-Path $p) { $__pex = $p; break }
}
if ($__pex) {
    try {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            $VersionInfo = & py -3.11 $__pex --version 2>$null | Select-Object -First 1
        } else {
            $VersionInfo = & python $__pex --version 2>$null | Select-Object -First 1
        }
    } catch {
        $VersionInfo = "QuietPatch"
    }
}

Write-Host ""
Write-Host "✓ $VersionInfo installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Try: quietpatch scan --also-report --open"
Write-Host "     (or: quietpatch scan --db $Db --also-report --open)"
Write-Host ""
Write-Host "For help: quietpatch scan --help"
