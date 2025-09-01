# QuietPatch Windows Uninstall Script
# This script completely removes QuietPatch from the system

param(
    [switch]$Force,
    [switch]$PreserveData
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor $Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor $Yellow }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor $Red }

# Check if running as Administrator
function Test-Administrator {
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Error "This script must be run as Administrator"
        exit 1
    }
}

# Stop and remove Scheduled Task
function Remove-ScheduledTask {
    Write-Info "Removing Scheduled Task..."
    
    try {
        Unregister-ScheduledTask -TaskName "QuietPatch\DailyScan" -Confirm:$false -ErrorAction SilentlyContinue
        Write-Info "Scheduled Task removed ✓"
    } catch {
        Write-Warn "Failed to remove Scheduled Task: $_"
    }
}

# Stop and remove service (if exists)
function Remove-Service {
    Write-Info "Removing service (if exists)..."
    
    try {
        if (Get-Service -Name "QuietPatch" -ErrorAction SilentlyContinue) {
            Stop-Service -Name "QuietPatch" -Force -ErrorAction SilentlyContinue
            Remove-Service -Name "QuietPatch" -Force -ErrorAction SilentlyContinue
            Write-Info "Service removed ✓"
        } else {
            Write-Info "Service not found"
        }
    } catch {
        Write-Warn "Failed to remove service: $_"
    }
}

# Remove environment variables
function Remove-EnvironmentVariables {
    Write-Info "Removing environment variables..."
    
    try {
        [Environment]::SetEnvironmentVariable("QP_OFFLINE", $null, "Machine")
        [Environment]::SetEnvironmentVariable("QP_DISABLE_AUTO_SYNC", $null, "Machine")
        [Environment]::SetEnvironmentVariable("QP_DATA_DIR", $null, "Machine")
        
        # Clear from current session
        Remove-Item Env:QP_OFFLINE -ErrorAction SilentlyContinue
        Remove-Item Env:QP_DISABLE_AUTO_SYNC -ErrorAction SilentlyContinue
        Remove-Item Env:QP_DATA_DIR -ErrorAction SilentlyContinue
        
        Write-Info "Environment variables removed ✓"
    } catch {
        Write-Warn "Failed to remove environment variables: $_"
    }
}

# Remove files and directories
function Remove-Files {
    Write-Info "Removing QuietPatch files and directories..."
    
    $base = "C:\Program Files\QuietPatch"
    $data = "C:\ProgramData\QuietPatch"
    
    # Remove main installation
    if (Test-Path $base) {
        Remove-Item -Path $base -Recurse -Force
        Write-Info "Main installation removed ✓"
    }
    
    # Remove data directory (unless preserved)
    if (Test-Path $data) {
        if ($PreserveData) {
            Write-Info "Data directory preserved: $data"
        } else {
            if ($Force) {
                Remove-Item -Path $data -Recurse -Force
                Write-Info "Data directory removed ✓"
            } else {
                $response = Read-Host "Remove data directory? This will delete all scan results and reports. (y/N)"
                if ($response -eq "y" -or $response -eq "Y") {
                    Remove-Item -Path $data -Recurse -Force
                    Write-Info "Data directory removed ✓"
                } else {
                    Write-Info "Data directory preserved: $data"
                }
            }
        }
    }
    
    Write-Info "Files and directories removed ✓"
}

# Main uninstall flow
function Main {
    Write-Info "Starting QuietPatch Windows uninstallation..."
    
    Test-Administrator
    
    if (-not $Force) {
        Write-Warn "This will completely remove QuietPatch from the system."
        $response = Read-Host "Are you sure? (y/N)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Info "Uninstallation cancelled"
            return
        }
    }
    
    Remove-ScheduledTask
    Remove-Service
    Remove-EnvironmentVariables
    Remove-Files
    
    Write-Info "Uninstallation completed successfully! 🎉"
    Write-Info ""
    Write-Info "QuietPatch has been completely removed from the system."
    if ($PreserveData) {
        Write-Info "Data directory preserved: C:\ProgramData\QuietPatch"
    }
}

# Run main function
Main


