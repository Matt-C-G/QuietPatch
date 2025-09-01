#!/usr/bin/env bash
set -euo pipefail

# QuietPatch Linux Production Installation Script
# This script sets up a production-ready QuietPatch installation with:
# - Locked-down service user
# - Secure file permissions
# - Systemd service + timer
# - Offline database snapshot
# - SELinux context configuration

PEX_PATH="${1:-dist/quietpatch-linux-x64.pex}"
DB_SNAPSHOT="${2:-dist/db-*.tar.zst}"
MINISIGN_PATH="${3:-third_party/minisign/minisign}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check preconditions
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if [[ ! -f "$PEX_PATH" ]]; then
        log_error "PEX file not found: $PEX_PATH"
        log_error "Build the PEX first: ./tools/build_pex.sh"
        exit 1
    fi
    
    if [[ ! -f "$MINISIGN_PATH" ]]; then
        log_warn "Minisign not found at $MINISIGN_PATH"
        log_warn "Database signature verification will be skipped"
        MINISIGN_PATH=""
    fi
    
    if ! command -v systemctl >/dev/null 2>&1; then
        log_error "systemd not available on this system"
        exit 1
    fi
    
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "python3 not found. Install Python 3.11+ first"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 0 ]]; then
        log_error "Python $PYTHON_VERSION found, but 3.11+ is required"
        exit 1
    fi
    log_info "Python $PYTHON_VERSION found ✓"
}

# Create service user and directories
setup_filesystem() {
    log_info "Setting up filesystem and permissions..."
    
    # Create service user
    if ! id "quietpatch" &>/dev/null; then
        useradd --system --no-create-home --shell /usr/sbin/nologin quietpatch
        log_info "Created service user: quietpatch"
    else
        log_info "Service user quietpatch already exists"
    fi
    
    # Create directories with proper ownership
    install -d -o root -g root -m 0755 /opt/quietpatch/bin
    install -d -o root -g root -m 0755 /opt/quietpatch/db
    install -d -o quietpatch -g quietpatch -m 0750 /var/lib/quietpatch
    install -d -o quietpatch -g quietpatch -m 0750 /var/log/quietpatch
    install -d -o root -g root -m 0755 /etc/quietpatch
    
    log_info "Directory structure created ✓"
}

# Install PEX and configuration
install_binary() {
    log_info "Installing QuietPatch binary and configuration..."
    
    # Install PEX
    install -m 0755 "$PEX_PATH" /opt/quietpatch/bin/quietpatch.pex
    
    # Install policy
    if [[ -f "config/policy.yml" ]]; then
        install -m 0644 config/policy.yml /etc/quietpatch/policy.yml
        log_info "Policy configuration installed"
    else
        log_warn "Policy file not found, using defaults"
    fi
    
    # Create symlink for convenience
    ln -sf /opt/quietpatch/bin/quietpatch.pex /usr/local/bin/quietpatch
    
    log_info "Binary and configuration installed ✓"
}

# Install and verify database snapshot
install_database() {
    log_info "Installing database snapshot..."
    
    # Find the latest DB snapshot
    if [[ -z "$DB_SNAPSHOT" ]] || [[ ! -f "$DB_SNAPSHOT" ]]; then
        DB_SNAPSHOT=$(ls -t dist/db-*.tar.zst 2>/dev/null | head -n1 || true)
    fi
    
    if [[ -z "$DB_SNAPSHOT" ]] || [[ ! -f "$DB_SNAPSHOT" ]]; then
        log_warn "No database snapshot found, skipping database installation"
        log_warn "Run: python3 tools/db_snapshot.py --out dist"
        return 0
    fi
    
    DB_BASENAME=$(basename "$DB_SNAPSHOT")
    DB_DIR="/opt/quietpatch/db"
    
    # Copy snapshot files
    install -m 0644 "$DB_SNAPSHOT" "$DB_DIR/"
    
    # Copy checksum if available
    if [[ -f "${DB_SNAPSHOT}.sha256" ]]; then
        install -m 0644 "${DB_SNAPSHOT}.sha256" "$DB_DIR/"
    fi
    
    # Copy signature if available
    if [[ -f "${DB_SNAPSHOT}.minisig" ]]; then
        install -m 0644 "${DB_SNAPSHOT}.minisig" "$DB_DIR/"
    fi
    
    # Install minisign if available
    if [[ -n "$MINISIGN_PATH" ]] && [[ -f "$MINISIGN_PATH" ]]; then
        install -m 0755 "$MINISIGN_PATH" /usr/local/bin/minisign
    fi
    
    # Verify and extract
    cd "$DB_DIR"
    log_info "Verifying database snapshot..."
    
    # Verify checksum
    if [[ -f "${DB_BASENAME}.sha256" ]]; then
        if sha256sum -c "${DB_BASENAME}.sha256"; then
            log_info "Checksum verification passed ✓"
        else
            log_error "Checksum verification failed!"
            exit 1
        fi
    fi
    
    # Verify signature if available
    if [[ -n "$MINISIGN_PATH" ]] && [[ -f "${DB_BASENAME}.minisig" ]]; then
        if minisign -Vm "$DB_BASENAME"; then
            log_info "Signature verification passed ✓"
        else
            log_error "Signature verification failed!"
            exit 1
        fi
    fi
    
    # Extract database
    log_info "Extracting database to /var/lib/quietpatch..."
    tar --use-compress-program=unzstd -xf "$DB_BASENAME" -C /var/lib/quietpatch
    chown -R quietpatch:quietpatch /var/lib/quietpatch/db
    
    log_info "Database installed and verified ✓"
}

# Create environment configuration
setup_environment() {
    log_info "Setting up environment configuration..."
    
    cat > /etc/quietpatch/env <<'ENV'
QP_OFFLINE=1
QP_DISABLE_AUTO_SYNC=1
QP_DATA_DIR=/var/lib/quietpatch
QP_DB_MAX_AGE_DAYS=7
# HTTP_PROXY=  HTTPS_PROXY=  NO_PROXY=
ENV
    
    chmod 0644 /etc/quietpatch/env
    log_info "Environment configuration created ✓"
}

# Install systemd service
install_systemd() {
    log_info "Installing systemd service and timer..."
    
    # Service unit
    cat > /etc/systemd/system/quietpatch.service <<'UNIT'
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
    cat > /etc/systemd/system/quietpatch.timer <<'TMR'
[Unit]
Description=Run QuietPatch daily

[Timer]
OnCalendar=03:00
Persistent=true
RandomizedDelaySec=5m

[Install]
WantedBy=timers.target
TMR
    
    # Reload systemd and enable
    systemctl daemon-reload
    systemctl enable --now quietpatch.timer
    
    log_info "Systemd service and timer installed ✓"
}

# Configure SELinux contexts
setup_selinux() {
    log_info "Configuring SELinux contexts..."
    
    if command -v semanage >/dev/null 2>&1; then
        if semanage fcontext -a -t var_lib_t "/var/lib/quietpatch(/.*)?" 2>/dev/null; then
            log_info "SELinux context for /var/lib/quietpatch set"
        fi
        if semanage fcontext -a -t var_log_t "/var/log/quietpatch(/.*)?" 2>/dev/null; then
            log_info "SELinux context for /var/log/quietpatch set"
        fi
        restorecon -Rv /var/lib/quietpatch /var/log/quietpatch
        log_info "SELinux contexts applied ✓"
    else
        log_info "SELinux not available, skipping context configuration"
    fi
}

# Test the installation
test_installation() {
    log_info "Testing installation..."
    
    # Test one-shot run
    if systemctl start quietpatch.service; then
        log_info "Service started successfully ✓"
        sleep 3
        
        # Check logs
        if [[ -f /var/log/quietpatch/quietpatch.log ]]; then
            log_info "Recent log output:"
            tail -n 20 /var/log/quietpatch/quietpatch.log
        fi
        
        if [[ -f /var/log/quietpatch/quietpatch.err ]]; then
            log_info "Recent error output:"
            tail -n 10 /var/log/quietpatch/quietpatch.err
        fi
        
        # Check if report was generated
        if find /var/lib/quietpatch -name "*.html" | grep -q .; then
            log_info "Report generated successfully ✓"
        else
            log_warn "No report found - check logs for errors"
        fi
    else
        log_error "Service failed to start"
        systemctl status quietpatch.service
        exit 1
    fi
}

# Main installation flow
main() {
    log_info "Starting QuietPatch Linux production installation..."
    
    check_prerequisites
    setup_filesystem
    install_binary
    install_database
    setup_environment
    install_systemd
    setup_selinux
    test_installation
    
    log_info "Installation completed successfully! 🎉"
    log_info ""
    log_info "QuietPatch is now running as a systemd service:"
    log_info "  - Service: quietpatch.service"
    log_info "  - Timer: quietpatch.timer (daily at 03:00)"
    log_info "  - Logs: /var/log/quietpatch/"
    log_info "  - Data: /var/lib/quietpatch/"
    log_info "  - Binary: /opt/quietpatch/bin/quietpatch.pex"
    log_info ""
    log_info "Manual test: sudo systemctl start quietpatch.service"
    log_info "Check status: sudo systemctl status quietpatch.timer"
}

# Run main function
main "$@"


