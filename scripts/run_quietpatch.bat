@echo off
setlocal
REM Keep cache paths short to dodge WinError 206
set PEX_ROOT=%~dp0.pexroot
set TMP=%~dp0.tmp
set TEMP=%~dp0.tmp

REM Prefer system py launcher for py311
where py >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo Python launcher not found. Please install Python 3.11 (64-bit) and retry.
  exit /b 86
)

REM Run PEX with py311; pass through args
py -3.11 "%~dp0quietpatch-win-py311.pex" %*
endlocal