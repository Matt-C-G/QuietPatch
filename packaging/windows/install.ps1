# QuietPatch Windows Production Installation Script
# This script sets up a production-ready QuietPatch installation with:
# - Embedded Python 3.13
# - Scheduled Task (daily at 03:00)
# - Secure file permissions
# - Offline database snapshot
# - Comprehensive logging

param(
    [string]$PexPath = "dist\quietpatch-windows-x64.pex",
    [string]$DbSnapshot = "dist\db-*.tar.zst",
    [string]$MinisignPath = "third_party\minisign\minisign.exe",
    [string]$PythonEmbedded = "$env:USERPROFILE\Downloads\python-3.13.*-embed-amd64.zip"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor $Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor $Yellow }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor $Red }

# Check preconditions
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    if (-not (Test-Path $PexPath)) {
        Write-Error "PEX file not found: $PexPath"
        Write-Error "Build the PEX first: .\tools\build_pex.ps1"
        exit 1
    }
    
    if (-not (Test-Path $MinisignPath)) {
        Write-Warn "Minisign not found at $MinisignPath"
        Write-Warn "Database signature verification will be skipped"
        $script:MinisignPath = $null
    }
    
    # Check if running as Administrator
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Error "This script must be run as Administrator"
        exit 1
    }
    
    Write-Info "Prerequisites check passed ✓"
}

# Setup filesystem and permissions
function Setup-Filesystem {
    Write-Info "Setting up filesystem and permissions..."
    
    $base = "C:\Program Files\QuietPatch"
    $data = "C:\ProgramData\QuietPatch"
    
    # Create directories
    New-Item -ItemType Directory -Force -Path $base | Out-Null
    New-Item -ItemType Directory -Force -Path "$base\logs" | Out-Null
    New-Item -ItemType Directory -Force -Path "$base\db" | Out-Null
    New-Item -ItemType Directory -Force -Path "$base\python" | Out-Null
    New-Item -ItemType Directory -Force -Path $data | Out-Null
    
    # Set permissions
    icacls $base /inheritance:r /grant:r "SYSTEM:(OI)(CI)(F)" "Administrators:(OI)(CI)(M)"
    icacls "$base\logs" /inheritance:r /grant:r "SYSTEM:(OI)(CI)(F)" "Administrators:(OI)(CI)(M)"
    icacls $data /inheritance:r /grant:r "SYSTEM:(OI)(CI)(F)" "Administrators:(OI)(CI)(M)"
    
    Write-Info "Filesystem setup completed ✓"
}

# Install embedded Python
function Install-EmbeddedPython {
    Write-Info "Installing embedded Python..."
    
    $base = "C:\Program Files\QuietPatch"
    
    # Find Python embedded zip
    $pythonZip = Get-ChildItem -Path $PythonEmbedded -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if (-not $pythonZip) {
        Write-Warn "Python embedded zip not found at $PythonEmbedded"
        Write-Warn "Download from: https://www.python.org/downloads/windows/"
        Write-Warn "Skipping embedded Python installation"
        return
    }
    
    # Extract Python
    Write-Info "Extracting Python from $($pythonZip.Name)..."
    Expand-Archive $pythonZip.FullName "$base\python" -Force
    
    # Enable site packages and zip imports
    $pthFile = "$base\python\python313._pth"
    if (Test-Path $pthFile) {
        $content = Get-Content $pthFile
        $content = $content -replace '^#import site', 'import site'
        $content | Set-Content $pthFile
        Write-Info "Python site packages enabled ✓"
    }
    
    Write-Info "Embedded Python installed ✓"
}

# Install PEX and configuration
function Install-Binary {
    Write-Info "Installing QuietPatch binary..."
    
    $base = "C:\Program Files\QuietPatch"
    
    # Copy PEX
    Copy-Item $PexPath "$base\quietpatch.pex" -Force
    
    # Copy policy if available
    if (Test-Path "config\policy.yml") {
        Copy-Item "config\policy.yml" "$base\policy.yml" -Force
        Write-Info "Policy configuration installed"
    } else {
        Write-Warn "Policy file not found, using defaults"
    }
    
    Write-Info "Binary installation completed ✓"
}

# Install and verify database snapshot
function Install-Database {
    Write-Info "Installing database snapshot..."
    
    $base = "C:\Program Files\QuietPatch"
    
    # Find the latest DB snapshot
    if (-not (Test-Path $DbSnapshot)) {
        $DbSnapshot = Get-ChildItem "dist\db-*.tar.zst" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    }
    
    if (-not $DbSnapshot -or -not (Test-Path $DbSnapshot)) {
        Write-Warn "No database snapshot found, skipping database installation"
        Write-Warn "Run: python3 tools\db_snapshot.py --out dist"
        return
    }
    
    $dbBasename = Split-Path $DbSnapshot -Leaf
    $dbDir = "$base\db"
    
    # Copy snapshot files
    Copy-Item $DbSnapshot "$dbDir\" -Force
    
    # Copy checksum if available
    $checksumFile = "$DbSnapshot.sha256"
    if (Test-Path $checksumFile) {
        Copy-Item $checksumFile "$dbDir\" -Force
    }
    
    # Copy signature if available
    $signatureFile = "$DbSnapshot.minisig"
    if (Test-Path $signatureFile) {
        Copy-Item $signatureFile "$dbDir\" -Force
    }
    
    # Copy minisign if available
    if ($MinisignPath -and (Test-Path $MinisignPath)) {
        Copy-Item $MinisignPath "$base\minisign.exe" -Force
    }
    
    # Verify and extract
    Set-Location $dbDir
    Write-Info "Verifying database snapshot..."
    
    # Verify checksum
    if (Test-Path "$dbBasename.sha256") {
        $expectedHash = Get-Content "$dbBasename.sha256" | ForEach-Object { $_.Split(' ')[0] }
        $actualHash = Get-FileHash $dbBasename -Algorithm SHA256 | Select-Object -ExpandProperty Hash
        if ($expectedHash -eq $actualHash) {
            Write-Info "Checksum verification passed ✓"
        } else {
            Write-Error "Checksum verification failed!"
            exit 1
        }
    }
    
    # Verify signature if available
    if ($MinisignPath -and (Test-Path "$dbBasename.minisig")) {
        $minisignPath = "$base\minisign.exe"
        if (Test-Path $minisignPath) {
            $result = & $minisignPath -Vm $dbBasename 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Info "Signature verification passed ✓"
            } else {
                Write-Error "Signature verification failed!"
                exit 1
            }
        }
    }
    
    # Extract database
    Write-Info "Extracting database..."
    try {
        # Try using tar if available (Git for Windows)
        if (Get-Command tar -ErrorAction SilentlyContinue) {
            tar -I zstd -xf $dbBasename -C $base
        } else {
            # Fallback to 7zip if available
            $7zip = Get-Command 7z -ErrorAction SilentlyContinue
            if ($7zip) {
                & $7zip x $dbBasename -o"$base" -y
            } else {
                Write-Error "Neither tar nor 7zip found. Install Git for Windows or 7zip."
                exit 1
            }
        }
        Write-Info "Database extracted successfully ✓"
    } catch {
        Write-Error "Failed to extract database: $_"
        exit 1
    }
}

# Setup environment variables
function Setup-Environment {
    Write-Info "Setting up environment variables..."
    
    # Set system environment variables
    [Environment]::SetEnvironmentVariable("QP_OFFLINE", "1", "Machine")
    [Environment]::SetEnvironmentVariable("QP_DISABLE_AUTO_SYNC", "1", "Machine")
    [Environment]::SetEnvironmentVariable("QP_DATA_DIR", "C:\ProgramData\QuietPatch", "Machine")
    
    # Apply immediately
    $env:QP_OFFLINE = "1"
    $env:QP_DISABLE_AUTO_SYNC = "1"
    $env:QP_DATA_DIR = "C:\ProgramData\QuietPatch"
    
    Write-Info "Environment variables set ✓"
}

# Create Scheduled Task
function Install-ScheduledTask {
    Write-Info "Creating Scheduled Task..."
    
    $base = "C:\Program Files\QuietPatch"
    
    # Determine Python path
    $pythonPath = "$base\python\python.exe"
    if (-not (Test-Path $pythonPath)) {
        $pythonPath = "python.exe"  # Use system Python
    }
    
    # Create task action
    $action = New-ScheduledTaskAction -Execute $pythonPath `
        -Argument "`"$base\quietpatch.pex`" scan --also-report" `
        -WorkingDirectory $base
    
    # Create task trigger (daily at 3:00 AM)
    $trigger = New-ScheduledTaskTrigger -Daily -At 3am
    
    # Create task settings
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
        -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
    
    # Create task principal (SYSTEM account)
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
    
    # Register the task
    try {
        Register-ScheduledTask -TaskName "QuietPatch\DailyScan" `
            -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
        
        Write-Info "Scheduled Task created successfully ✓"
    } catch {
        Write-Error "Failed to create Scheduled Task: $_"
        exit 1
    }
}

# Test the installation
function Test-Installation {
    Write-Info "Testing installation..."
    
    $base = "C:\Program Files\QuietPatch"
    
    # Determine Python path
    $pythonPath = "$base\python\python.exe"
    if (-not (Test-Path $pythonPath)) {
        $pythonPath = "python.exe"
    }
    
    # Test one-shot run
    try {
        Write-Info "Running test scan..."
        $result = & $pythonPath "$base\quietpatch.pex" scan --also-report 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Test scan completed successfully ✓"
            
            # Check if report was generated
            $reports = Get-ChildItem "C:\ProgramData\QuietPatch" -Filter "*.html" -Recurse -ErrorAction SilentlyContinue
            if ($reports) {
                Write-Info "Report generated successfully ✓"
                Write-Info "Report location: $($reports[0].FullName)"
            } else {
                Write-Warn "No report found - check for errors"
            }
        } else {
            Write-Error "Test scan failed with exit code $LASTEXITCODE"
            Write-Error "Output: $result"
            exit 1
        }
    } catch {
        Write-Error "Failed to run test scan: $_"
        exit 1
    }
}

# Main installation flow
function Main {
    Write-Info "Starting QuietPatch Windows production installation..."
    
    Test-Prerequisites
    Setup-Filesystem
    Install-EmbeddedPython
    Install-Binary
    Install-Database
    Setup-Environment
    Install-ScheduledTask
    Test-Installation
    
    Write-Info "Installation completed successfully! 🎉"
    Write-Info ""
    Write-Info "QuietPatch is now configured as a Scheduled Task:"
    Write-Info "  - Task: QuietPatch\DailyScan"
    Write-Info "  - Schedule: Daily at 03:00 AM"
    Write-Info "  - Account: SYSTEM"
    Write-Info "  - Binary: $base\quietpatch.pex"
    Write-Info "  - Data: C:\ProgramData\QuietPatch"
    Write-Info ""
    Write-Info "Manual test: Start the Scheduled Task manually"
    Write-Info "Check status: Get-ScheduledTask -TaskName 'QuietPatch\DailyScan'"
}

# Run main function
Main


