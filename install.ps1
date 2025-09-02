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

# Shim: adds a 'quietpatch' command
$shim = @'
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Env:PEX_ROOT = Join-Path $Root ".pexroot"
if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3.11 (Join-Path $Root "quietpatch-win-py311.pex") @Args
} else {
  & python (Join-Path $Root "quietpatch-win-py311.pex") @Args
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

Write-Host "Done. New session: run `quietpatch scan --db $Db --also-report --open`"
