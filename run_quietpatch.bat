@echo off
setlocal
set PEX_ROOT=%~dp0.pexroot
set TMP=%~dp0.tmp
set TEMP=%~dp0.tmp
rem Try newest first, then fall back.
for %%V in (3.13 3.12 3.11) do (
  py -%%V -c "import sys" >nul 2>&1
  if not errorlevel 1 (
    py -%%V "%~dp0quietpatch-win-py311.pex" %*
    goto :eof
  )
)

echo QuietPatch requires Python 3.11–3.13 (64-bit) on Windows.
echo Install from https://www.python.org/downloads/windows/ or via winget:
echo   winget install --id=Python.Python.3.13 -e
exit /b 86
endlocal
