@echo off
echo QuietPatch v0.4.0 Windows Build
echo ================================

powershell -ExecutionPolicy Bypass -File scripts\windows\build-release.ps1

pause
