# 🚀 QuietPatch Production Deployment Guide

## Overview

This guide covers the complete production deployment of QuietPatch across Linux and Windows environments. The system is designed for enterprise-grade security with offline-first operation and comprehensive service integration.

## 🐧 **Linux (systemd) Production Deployment**

### Prerequisites

- **Build Artifact**: `dist/quietpatch-linux-x64.pex` (built on manylinux, Py3.11–3.13 compatible)
- **Interpreter**: `/usr/bin/python3` (3.11+)
- **System**: systemd-based Linux distribution
- **Permissions**: Root access required

### Quick Installation

```bash
# 1. Build the PEX (on Linux runner)
./tools/build_pex.sh

# 2. Build database snapshot
python3 tools/db_snapshot.py --out dist

# 3. Run production installer
sudo ./packaging/linux/install.sh
```

### Manual Installation Steps

#### 1. File Layout (Secure Service User)

```bash
# Create locked-down service user
sudo useradd --system --no-create-home --shell /usr/sbin/nologin quietpatch

# Create directory structure with proper ownership
sudo install -d -o root -g root -m 0755 /opt/quietpatch/bin
sudo install -d -o root -g root -m 0755 /opt/quietpatch/db
sudo install -d -o quietpatch -g quietpatch -m 0750 /var/lib/quietpatch
sudo install -d -o quietpatch -g quietpatch -m 0750 /var/log/quietpatch
sudo install -d -o root -g root -m 0755 /etc/quietpatch

# Install PEX and configuration
sudo install -m 0755 dist/quietpatch-linux-x64.pex /opt/quietpatch/bin/quietpatch.pex
sudo install -m 0644 config/policy.yml /etc/quietpatch/policy.yml
sudo ln -sf /opt/quietpatch/bin/quietpatch.pex /usr/local/bin/quietpatch
```

#### 2. Offline Database Snapshot

```bash
# Install database files
sudo install -m 0644 dist/db-*.tar.zst /opt/quietpatch/db/
sudo install -m 0644 dist/db-*.tar.zst.sha256 /opt/quietpatch/db/
sudo install -m 0644 dist/db-*.tar.zst.minisig /opt/quietpatch/db/

# Verify and extract
cd /opt/quietpatch/db
sha256sum -c db-*.tar.zst.sha256
minisign -Vm db-*.tar.zst  # must show "Signature verified"

# Extract database
sudo tar --use-compress-program=unzstd -xf db-*.tar.zst -C /var/lib/quietpatch
sudo chown -R quietpatch:quietpatch /var/lib/quietpatch/db
```

#### 3. Environment Configuration

```bash
# Create environment file
sudo tee /etc/quietpatch/env >/dev/null <<'ENV'
QP_OFFLINE=1
QP_DISABLE_AUTO_SYNC=1
QP_DATA_DIR=/var/lib/quietpatch
QP_DB_MAX_AGE_DAYS=7
ENV

sudo chmod 0644 /etc/quietpatch/env
```

#### 4. Systemd Service

```bash
# Service unit
sudo tee /etc/systemd/system/quietpatch.service >/dev/null <<'UNIT'
[Unit]
Description=QuietPatch vulnerability scan
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=quietpatch
Group=quietpatch
EnvironmentFile=/etc/quietpatch/env
ExecStart=/usr/bin/python3 /opt/quietpatch/bin/quietpatch.pex scan --also-report
WorkingDirectory=/var/lib/quietpatch
Nice=10
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/quietpatch /var/log/quietpatch
StandardOutput=append:/var/log/quietpatch/quietpatch.log
StandardError=append:/var/log/quietpatch/quietpatch.err

[Install]
WantedBy=multi-user.target
UNIT

# Timer unit
sudo tee /etc/systemd/system/quietpatch.timer >/dev/null <<'TMR'
[Unit]
Description=Run QuietPatch daily

[Timer]
OnCalendar=03:00
Persistent=true
RandomizedDelaySec=5m

[Install]
WantedBy=timers.target
TMR

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now quietpatch.timer
```

#### 5. SELinux Configuration (if enforcing)

```bash
sudo semanage fcontext -a -t var_lib_t "/var/lib/quietpatch(/.*)?"
sudo semanage fcontext -a -t var_log_t "/var/log/quietpatch(/.*)?"
sudo restorecon -Rv /var/lib/quietpatch /var/log/quietpatch
```

### Verification

```bash
# Check service status
sudo systemctl status quietpatch.timer

# Test one-shot run
sudo systemctl start quietpatch.service

# Check logs
sudo tail -n 100 /var/log/quietpatch/quietpatch.log
sudo tail -n 100 /var/log/quietpatch/quietpatch.err

# Verify report generation
sudo find /var/lib/quietpatch -name "*.html"
```

### Uninstallation

```bash
sudo ./packaging/linux/uninstall.sh
```

---

## 🪟 **Windows Production Deployment**

### Prerequisites

- **Build Artifact**: `dist\quietpatch-windows-x64.pex`
- **Python**: Embedded Python 3.13 (recommended) or system Python 3.11+
- **System**: Windows 10/11 or Windows Server 2019+
- **Permissions**: Administrator access required

### Quick Installation

```powershell
# 1. Build the PEX (on Windows runner)
.\tools\build_pex.ps1

# 2. Build database snapshot (on Linux)
python3 tools/db_snapshot.py --out dist

# 3. Run production installer (as Administrator)
.\packaging\windows\install.ps1
```

### Manual Installation Steps

#### 1. File Layout

```powershell
$base = "C:\Program Files\QuietPatch"
New-Item -ItemType Directory -Force "$base","$base\logs","$base\db","$base\python" | Out-Null

# Embedded Python 3.13 (download from python.org)
Expand-Archive "$env:USERPROFILE\Downloads\python-3.13.*-embed-amd64.zip" "$base\python" -Force

# Enable site packages
(Get-Content "$base\python\python313._pth") -replace '^#import site','import site' | Set-Content "$base\python\python313._pth"

# Install PEX and database
Copy-Item dist\quietpatch-windows-x64.pex "$base\quietpatch.pex" -Force
Copy-Item dist\db-*.tar.zst* "$base\db\" -Force
```

#### 2. Verify and Extract Database

```powershell
Set-Location "$base\db"

# Verify checksum
Get-FileHash db-*.tar.zst -Algorithm SHA256 | Format-List
type db-*.tar.zst.sha256

# Verify signature
& "$base\minisign.exe" -Vm db-*.tar.zst

# Extract database
tar -I zstd -xf db-*.tar.zst -C "$base"
```

#### 3. Scheduled Task Creation

```powershell
$base = "C:\Program Files\QuietPatch"
$pythonPath = "$base\python\python.exe"

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
Register-ScheduledTask -TaskName "QuietPatch\DailyScan" `
    -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
```

#### 4. Environment Variables

```powershell
# Set system environment variables
[Environment]::SetEnvironmentVariable("QP_OFFLINE", "1", "Machine")
[Environment]::SetEnvironmentVariable("QP_DISABLE_AUTO_SYNC", "1", "Machine")
[Environment]::SetEnvironmentVariable("QP_DATA_DIR", "C:\ProgramData\QuietPatch", "Machine")

# Apply immediately
$env:QP_OFFLINE = "1"
$env:QP_DISABLE_AUTO_SYNC = "1"
$env:QP_DATA_DIR = "C:\ProgramData\QuietPatch"
```

#### 5. Permissions and Logging

```powershell
# Set secure permissions
icacls "C:\Program Files\QuietPatch" /inheritance:r /grant:r "SYSTEM:(OI)(CI)(F)" "Administrators:(OI)(CI)(M)"
icacls "C:\ProgramData\QuietPatch" /inheritance:r /grant:r "SYSTEM:(OI)(CI)(F)" "Administrators:(OI)(CI)(M)"

# Create data directory
New-Item -ItemType Directory -Force "C:\ProgramData\QuietPatch" | Out-Null
```

### Verification

```powershell
# Check Scheduled Task
Get-ScheduledTask -TaskName "QuietPatch\DailyScan"

# Test one-shot run
& "$base\python\python.exe" "$base\quietpatch.pex" scan --also-report

# Check for reports
Get-ChildItem "C:\ProgramData\QuietPatch" -Filter "*.html" -Recurse
```

### Uninstallation

```powershell
# As Administrator
.\packaging\windows\uninstall.ps1

# Force uninstall (no prompts)
.\packaging\windows\uninstall.ps1 -Force
```

---

## 🔒 **Security Features**

### Linux Security Hardening

- **Service User**: Dedicated `quietpatch` user with no shell access
- **File Permissions**: Strict ownership and mode restrictions
- **Systemd Security**: `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=strict`
- **SELinux**: Proper context labeling for data and logs
- **Network Isolation**: `ProtectHome=true`, limited `ReadWritePaths`

### Windows Security Hardening

- **SYSTEM Account**: Runs with highest available privileges
- **File Permissions**: Restricted inheritance, explicit ACLs
- **Environment Isolation**: System-wide environment variables
- **Task Security**: SYSTEM principal with execution time limits

---

## 📊 **Monitoring and Maintenance**

### Health Checks

```bash
# Linux
sudo systemctl status quietpatch.timer
sudo journalctl -u quietpatch.service -f

# Windows
Get-ScheduledTask -TaskName "QuietPatch\DailyScan"
Get-ChildItem "C:\ProgramData\QuietPatch" -Recurse | Measure-Object
```

### Log Analysis

```bash
# Linux
sudo tail -f /var/log/quietpatch/quietpatch.log
sudo tail -f /var/log/quietpatch/quietpatch.err

# Windows
Get-Content "C:\ProgramData\QuietPatch\logs\quietpatch.log" -Tail 100 -Wait
```

### Database Updates

```bash
# Build new snapshot
python3 tools/db_snapshot.py --out dist

# Linux: Extract to /var/lib/quietpatch
sudo tar -xf dist/db-*.tar.zst -C /var/lib/quietpatch

# Windows: Extract to C:\ProgramData\QuietPatch
tar -xf dist\db-*.tar.zst -C "C:\ProgramData\QuietPatch"
```

---

## 🚨 **Troubleshooting**

### Common Issues

#### PEX Execution Failures

```bash
# Check Python version compatibility
python3 --version

# Verify PEX file integrity
file dist/quietpatch-*.pex
ls -lh dist/quietpatch-*.pex
```

#### Database Issues

```bash
# Verify database files
ls -la /var/lib/quietpatch/db/
ls -la /opt/quietpatch/db/

# Check database age
find /var/lib/quietpatch -name "*.json" -exec stat -c "%y %n" {} \;
```

#### Service Failures

```bash
# Linux: Check systemd logs
sudo journalctl -u quietpatch.service -n 50

# Windows: Check Task Scheduler history
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'; ID=200} | Select-Object -First 10
```

### Performance Tuning

```bash
# Linux: Adjust systemd limits
sudo systemctl edit quietpatch.service

# Add to override file:
[Service]
Nice=10
IOSchedulingClass=2
IOSchedulingPriority=4
```

---

## 📋 **Deployment Checklist**

### Pre-deployment

- [ ] PEX built for target platform
- [ ] Database snapshot created and verified
- [ ] Target system meets requirements
- [ ] Administrative access confirmed
- [ ] Network policies reviewed

### Installation

- [ ] Service user created (Linux)
- [ ] Directory structure established
- [ ] Binary and configuration installed
- [ ] Database extracted and verified
- [ ] Service/task configured
- [ ] Permissions set correctly

### Post-deployment

- [ ] Service starts successfully
- [ ] Test scan completes
- [ ] Report generated
- [ ] Logs accessible
- [ ] Scheduled execution confirmed
- [ ] Security settings verified

---

## 🎯 **Enterprise Integration**

### Configuration Management

- **Ansible**: Use provided scripts in playbooks
- **Puppet/Chef**: Integrate installation steps
- **SCCM/Intune**: Deploy via Windows management
- **Docker**: Containerized deployment available

### Monitoring Integration

- **Prometheus**: Export metrics via custom endpoints
- **Grafana**: Dashboard templates for vulnerability trends
- **ELK Stack**: Log aggregation and analysis
- **Splunk**: SIEM integration for security events

### Compliance

- **SOC 2**: Audit logging and access controls
- **PCI DSS**: Vulnerability scanning requirements
- **HIPAA**: Security assessment tools
- **ISO 27001**: Information security management

---

**QuietPatch is now ready for enterprise production deployment!** 🚀


