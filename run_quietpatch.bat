@echo off
setlocal
set PEX_ROOT=%~dp0.pexroot
set TMP=%~dp0.tmp
set TEMP=%~dp0.tmp
where py >nul 2>&1 || (echo QuietPatch requires Python 3.11 (64-bit). Download from https://www.python.org/downloads/release/python-311/ & pause & exit /b 86)
if exist "%~dp0quietpatch.pex" (
  py -3.11 "%~dp0quietpatch.pex" %*
) else if exist "%~dp0quietpatch-win-py311.pex" (
  py -3.11 "%~dp0quietpatch-win-py311.pex" %*
) else if exist "%~dp0quietpatch-windows-x64.pex" (
  py -3.11 "%~dp0quietpatch-windows-x64.pex" %*
) else (
  echo Could not find quietpatch.pex in "%~dp0" & pause & exit /b 87)
endlocal
