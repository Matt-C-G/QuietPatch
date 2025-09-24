# QuietPatch Windows Prerequisites Setup
# Run as Administrator

Write-Host "🔧 Setting up QuietPatch Windows prerequisites..." -ForegroundColor Green

# Install Chocolatey if not present
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Install prerequisites
Write-Host "Installing prerequisites..." -ForegroundColor Yellow
choco install -y python312 --version=3.12.11
choco install -y innosetup
choco install -y 7zip
choco install -y minisign

# Refresh PATH
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

Write-Host "`n✅ Prerequisites installed!" -ForegroundColor Green
Write-Host "Please restart PowerShell and run build-windows.bat" -ForegroundColor Yellow
