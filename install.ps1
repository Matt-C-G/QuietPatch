$ErrorActionPreference = 'Stop'
$Owner = 'Matt-C-G'
$Dist  = 'quietpatch-dist'
$Arch  = (Get-CimInstance Win32_Processor).AddressWidth
if ($Arch -ne 64) { Write-Error 'Only x64 supported'; exit 1 }

$Asset = 'quietpatch-windows-x64-latest.zip'
$Tmp   = Join-Path $env:TEMP ("qp_" + [guid]::NewGuid().ToString("n"))
$Dest  = Join-Path $env:USERPROFILE ".quietpatch\bin"
New-Item -ItemType Directory -Force -Path $Tmp,$Dest | Out-Null

$Url = "https://github.com/$Owner/$Dist/releases/latest/download/$Asset"
Write-Host "Downloading $Asset …"
try {
  Invoke-WebRequest -Uri $Url -OutFile (Join-Path $Tmp pkg.zip) -UseBasicParsing -ErrorAction Stop
} catch {
  Write-Warning "Public download failed. Trying 'gh' fallback…"
  if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh release download -R "$Owner/$Dist" -p $Asset -D $Tmp | Out-Null
    Rename-Item (Join-Path $Tmp $Asset) (Join-Path $Tmp pkg.zip) -Force
  } else {
    Write-Error 'Cannot download asset. Install GitHub CLI or make repo public.'; exit 1
  }
}

Expand-Archive (Join-Path $Tmp pkg.zip) -DestinationPath $Dest -Force
Write-Host "Installed to $Dest"

$bin = "$Dest\quietpatch-windows-x64.exe"
if (Test-Path $bin) { & $bin --version | Out-String | Write-Host }

$path = [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not $path.Split(';') -contains $Dest) {
  [Environment]::SetEnvironmentVariable('Path', "$path;$Dest", 'User')
  Write-Host "Added to PATH (User). Open a new PowerShell to use 'quietpatch'."
}
