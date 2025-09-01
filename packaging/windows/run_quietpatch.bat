@echo off
REM QuietPatch Windows Wrapper
REM This batch file runs QuietPatch from a double-click in Explorer

echo QuietPatch Vulnerability Scanner
echo ================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11 (64-bit) from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Set environment variables to avoid path issues
set PEX_ROOT=C:\pex
set TEMP=C:\t
set TMP=C:\t

REM Create cache directories if they don't exist
if not exist "%PEX_ROOT%" mkdir "%PEX_ROOT%"
if not exist "%TEMP%" mkdir "%TEMP%"

echo Running vulnerability scan...
echo.

REM Run the scan
python quietpatch-win-py311.pex scan --also-report

if %errorlevel% equ 0 (
    echo.
    echo Scan completed successfully!
    echo Report saved as: report.html
    echo.
    echo Opening report in default browser...
    start report.html
) else (
    echo.
    echo Scan completed with errors (exit code: %errorlevel%)
    echo Check the output above for details
)

echo.
pause
