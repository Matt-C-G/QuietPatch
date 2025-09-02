$ErrorActionPreference = 'Stop'

$Owner = $env:OWNER; if (-not $Owner) { $Owner = 'Matt-C-G' }
$Repo  = $env:REPO;   if (-not $Repo)   { $Repo  = 'QuietPatch' }
$Token = $env:GITHUB_TOKEN; if (-not $Token) { $Token = $env:GH_TOKEN }
$Api   = "https://api.github.com/repos/$Owner/$Repo"
$UA    = "curl/quietpatch-installer"

# Asset per platform
$ASSET = 'quietpatch-windows-x64.zip'

$OutDir = "$env:USERPROFILE\.local\bin"
$PkgDir = "$env:TEMP\quietpatch_pkg"
New-Item -Force -ItemType Directory -Path $OutDir | Out-Null
New-Item -Force -ItemType Directory -Path $PkgDir | Out-Null

function Get-Asset {
  param([string]$OutPath)
  if ($Token) {
    $latest = Invoke-RestMethod -Headers @{ Authorization = "Bearer $Token"; 'User-Agent' = $UA } `
               -Uri "$Api/releases/latest" -Method GET
    $asset  = $latest.assets | Where-Object { $_.name -eq $ASSET } | Select-Object -First 1
    if (-not $asset) { throw "Asset $ASSET not found in latest release." }
    $url = "$Api/releases/assets/$($asset.id)"
    Invoke-WebRequest -Headers @{ Authorization="Bearer $Token"; Accept="application/octet-stream"; 'User-Agent'=$UA } `
      -Uri $url -OutFile $OutPath
  } else {
    $url = "https://github.com/$Owner/$Repo/releases/latest/download/$ASSET"
    Invoke-WebRequest -Uri $url -OutFile $OutPath
  }
}

$zip = Join-Path $env:TEMP $ASSET
Write-Host "Downloading $ASSET..."
Get-Asset -OutPath $zip

Write-Host 'Installing...'
Expand-Archive -Path $zip -DestinationPath $PkgDir -Force
if (Test-Path (Join-Path $PkgDir 'quietpatch.exe')) {
  Copy-Item -Force (Join-Path $PkgDir 'quietpatch.exe') (Join-Path $OutDir 'quietpatch.exe')
} elseif (Test-Path (Join-Path $PkgDir 'run_quietpatch.bat')) {
  Copy-Item -Force (Join-Path $PkgDir 'run_quietpatch.bat') (Join-Path $OutDir 'quietpatch.bat')
} else {
  throw 'No launcher found in package'
}

Write-Host "Installed to $OutDir"
& (Join-Path $OutDir 'quietpatch.exe') --version | Write-Host
