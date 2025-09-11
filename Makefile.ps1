<#  QuietPatch Windows Builder
    One-command local release for v0.4.0
    Requirements: Python 3.12 x64, Inno Setup 6, 7-Zip (optional), minisign
#>

param(
  [ValidateSet('all','setup','build','package','checksums','sign','release','clean')]
  [string]$Target = 'all',
  [string]$Version = '0.4.0'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ----- Config -----
$Iscc      = 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe'
$Py        = 'py'               # Python launcher
$PyVer     = '3.12'
$Venv      = ".venv$PyVer"
$RelDir    = 'release'
$DistDir   = 'dist'
$OutputDir = 'Output'
$BinCliDir = Join-Path $DistDir 'quietpatch'
$CliExe = Join-Path $DistDir 'quietpatch.exe'
$ExeSetup  = "QuietPatch-Setup-v$Version.exe"
$ZipCli    = "quietpatch-cli-v$Version-win64.zip"
$ShaFile   = 'SHA256SUMS.txt'
$KeyFile   = 'keys\quietpatch.key'   # local secret key file
$PubKey    = 'RWToYFmF4YgJS6OnTBHNCgRH59Fnx85WiQJF7jy9I3spZwdj/Ac+m8MR' # for verification

# ----- Helpers -----
function Say([string]$msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Check-Cmd([string]$cmd, [string]$hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing '$cmd'. $hint"
  }
}
function Ensure-Dir([string]$p) { if (-not (Test-Path $p)) { New-Item -ItemType Directory $p | Out-Null } }

function Ensure-QuickStartTxt {
  if (-not (Test-Path 'README-QuickStart.txt')) {
    if (Test-Path 'README-QuickStart.md') {
      Copy-Item 'README-QuickStart.md' 'README-QuickStart.txt' -Force
      Say "Created README-QuickStart.txt from .md version"
    } else {
      @'
QuietPatch QuickStart (v0.4.0)

1) Install or run QuietPatch.
2) Click "Start Scan" (Read-only by default).
3) Click "View Report". Done.

First launch:
- Windows SmartScreen: More info → Run anyway.
- macOS: Right-click the app → Open → Open (first time only).

Verify (optional): See VERIFY.md for SHA256 + minisign steps.
Support: Open a GitHub issue with the error text and OS version.
'@ | Out-File 'README-QuickStart.txt' -Encoding ascii
      Say "Created basic README-QuickStart.txt"
    }
  }
}

# ----- Tasks -----
function Task-Setup {
  Say "Verifying toolchain"
  Check-Cmd $Py "Install Python 3.12 x64 from python.org"
  Check-Cmd 'minisign' "Install via 'choco install minisign'"
  if (-not (Test-Path $Iscc)) { throw "Inno Setup not found at: $Iscc" }

  Say "Creating venv ($Venv) with Python $PyVer"
  & $Py -$PyVer -m venv $Venv
  & "$Venv\Scripts\Activate.ps1"
  $v = & python -V
  if ($v -notmatch '3\.12') { throw "Wrong Python: $v (need 3.12.x)" }

  Say "Installing wheel-only deps"
  $env:PIP_ONLY_BINARY=":all:"
  python -m pip install --upgrade pip wheel
  pip install pyinstaller==6.6.0 cryptography==42.0.7
  
  # Install runtime dependencies
  if (Test-Path 'requirements.txt') {
    pip install -r requirements.txt
  }
}

function Task-Build {
  & "$Venv\Scripts\Activate.ps1"
  $env:PIP_ONLY_BINARY=":all:"
  
  Say "Building GUI (PyInstaller)"
  if (Test-Path 'build\quietpatch_wizard_win.spec') {
    pyinstaller build\quietpatch_wizard_win.spec
  } elseif (Test-Path 'build\quietpatch.spec') {
    pyinstaller build\quietpatch.spec
  } else { 
    throw "Missing GUI spec file. Need build\quietpatch_wizard_win.spec or build\quietpatch.spec" 
  }

  Say "Building CLI (PyInstaller)"
  if (Test-Path 'build\quietpatch_cli_win.spec') {
    pyinstaller build\quietpatch_cli_win.spec
  } elseif (Test-Path 'build\quietpatch_cli.spec') {
    pyinstaller build\quietpatch_cli.spec
  } else { 
    throw "Missing CLI spec file. Need build\quietpatch_cli_win.spec or build\quietpatch_cli.spec" 
  }

  Say "Dist layout:"
  Get-ChildItem -Recurse $DistDir | Select-Object FullName,Length | Format-Table -AutoSize
}

function Task-Package {
  Ensure-Dir $RelDir
  Ensure-QuickStartTxt

  Say "Running Inno Setup"
  & $Iscc 'installer\windows\QuietPatch.iss'
  Copy-Item -Force "$OutputDir\$ExeSetup" $RelDir\

  Say "Creating portable CLI zip"
  if (Test-Path $BinCliDir) {
    # CLI built as folder - include QuickStart in the zip root
    Copy-Item -Force 'README-QuickStart.txt' $BinCliDir\
    Copy-Item -Force 'VERIFY.md' $BinCliDir\ -ErrorAction SilentlyContinue
    
    if (Get-Command 7z -ErrorAction SilentlyContinue) {
      7z a "$RelDir\$ZipCli" "$BinCliDir\*"
    } else {
      Compress-Archive -Path "$BinCliDir\*" -DestinationPath "$RelDir\$ZipCli" -Force
    }
    Say "Portable CLI created with QuickStart included"
  } elseif (Test-Path $CliExe) {
    # CLI built as single file - create temp folder for packaging
    $TempCliDir = Join-Path $DistDir 'quietpatch-portable'
    New-Item -ItemType Directory -Path $TempCliDir -Force | Out-Null
    Copy-Item -Force $CliExe $TempCliDir\
    Copy-Item -Force 'README-QuickStart.txt' $TempCliDir\
    Copy-Item -Force 'VERIFY.md' $TempCliDir\ -ErrorAction SilentlyContinue
    
    if (Get-Command 7z -ErrorAction SilentlyContinue) {
      7z a "$RelDir\$ZipCli" "$TempCliDir\*"
    } else {
      Compress-Archive -Path "$TempCliDir\*" -DestinationPath "$RelDir\$ZipCli" -Force
    }
    Remove-Item -Recurse -Force $TempCliDir
    Say "Portable CLI created with QuickStart included"
  } else {
    throw "CLI not found: $BinCliDir or $CliExe"
  }

  # Copy additional files to release directory
  Copy-Item -Force 'README-QuickStart.txt' $RelDir\ -ErrorAction SilentlyContinue
  Copy-Item -Force 'VERIFY.md' $RelDir\ -ErrorAction SilentlyContinue

  Say "Release artifacts so far:"
  Get-ChildItem $RelDir
}

function Task-Checksums {
  Say "Writing SHA256SUMS"
  Push-Location $RelDir
  # Consistent GNU coreutils format: HASH *filename
  Remove-Item -Force $ShaFile -ErrorAction SilentlyContinue
  Get-ChildItem | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
    $h = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    "{0} *{1}" -f $h, $_.Name | Out-File -FilePath $ShaFile -Append -Encoding ascii
  }
  Say "SHA256SUMS.txt contents:"
  Get-Content $ShaFile
  Pop-Location
}

function Task-Sign {
  if (-not (Test-Path $KeyFile)) { throw "Secret key not found: $KeyFile" }
  Say "Signing SHA256SUMS with minisign"
  Push-Location $RelDir
  minisign -Sm $ShaFile -s "..\$KeyFile"
  if ($PubKey) {
    Say "Verifying with provided public key"
    minisign -Vm $ShaFile -P $PubKey
  }
  Pop-Location
}

function Task-Release {
  Check-Cmd 'gh' "Install GitHub CLI from https://cli.github.com"
  Say "Creating GitHub release v$Version"
  $files = @(
    "$RelDir\$ExeSetup",
    "$RelDir\$ZipCli",
    "$RelDir\$ShaFile",
    "$RelDir\$ShaFile.minisig"
  ) | ForEach-Object { Resolve-Path $_ }
  
  # Include documentation files if they exist
  if (Test-Path "$RelDir\README-QuickStart.txt") { $files += (Resolve-Path "$RelDir\README-QuickStart.txt") }
  if (Test-Path "$RelDir\VERIFY.md") { $files += (Resolve-Path "$RelDir\VERIFY.md") }
  
  & gh release create "v$Version" $files `
     -t "QuietPatch v$Version" `
     -n "Download-ready Windows release (installer + portable CLI + signed checksums)"
}

function Task-Clean {
  Say "Cleaning"
  Remove-Item -Recurse -Force $DistDir,$RelDir,$OutputDir -ErrorAction SilentlyContinue
  Remove-Item -Force 'README-QuickStart.txt' -ErrorAction SilentlyContinue
  Say "Cleaned dist/, release/, Output/, and temp files"
  Get-ChildItem
}

# ----- Dispatcher -----
switch ($Target) {
  'setup'     { Task-Setup }
  'build'     { Task-Build }
  'package'   { Task-Package }
  'checksums' { Task-Checksums }
  'sign'      { Task-Sign }
  'release'   { Task-Release }
  'clean'     { Task-Clean }
  'all'       {
                Task-Setup
                Task-Build
                Task-Package
                Task-Checksums
                Task-Sign
              }
}
