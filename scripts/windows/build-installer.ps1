$ErrorActionPreference = 'Stop'
$Inno = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (!(Test-Path $Inno)) { throw "Inno Setup not found at $Inno" }
& $Inno "installer\windows\QuietPatch.iss"
New-Item -Force -ItemType Directory release | Out-Null
Copy-Item -Force .\Output\QuietPatch-Setup-v0.4.0.exe .\release\
