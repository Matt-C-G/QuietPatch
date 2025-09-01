@echo off
setlocal
set PEX_ROOT=%~dp0.pexroot
set TMP=%~dp0.tmp
set TEMP=%~dp0.tmp
where py >nul 2>&1 || (echo Install Python 3.11 (64-bit) and retry.& exit /b 86)
py -3.11 "%~dp0quietpatch-win-py311.pex" %*
endlocal
