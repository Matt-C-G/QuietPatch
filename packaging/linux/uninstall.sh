#!/usr/bin/env bash
set -euo pipefail

# QuietPatch Linux Uninstall Script
# This script completely removes QuietPatch from the system

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Stop and disable services
stop_services() {
    log_info "Stopping and disabling QuietPatch services..."
    
    # Stop and disable timer
    if systemctl is-active --quiet quietpatch.timer; then
        systemctl stop quietpatch.timer
        log_info "Stopped quietpatch.timer"
    fi
    
    if systemctl is-enabled --quiet quietpatch.timer; then
        systemctl disable quietpatch.timer
        log_info "Disabled quietpatch.timer"
    fi
    
    # Stop and disable service
    if systemctl is-active --quiet quietpatch.service; then
        systemctl stop quietpatch.service
        log_info "Stopped quietpatch.service"
    fi
    
    if systemctl is-enabled --quiet quietpatch.service; then
        systemctl disable quietpatch.service
        log_info "Disabled quietpatch.service"
    fi
    
    log_info "Services stopped and disabled ✓"
}

# Remove systemd units
remove_systemd() {
    log_info "Removing systemd units..."
    
    # Remove service and timer files
    rm -f /etc/systemd/system/quietpatch.service
    rm -f /etc/systemd/system/quietpatch.timer
    
    # Reload systemd
    systemctl daemon-reload
    
    log_info "Systemd units removed ✓"
}

# Remove files and directories
remove_files() {
    log_info "Removing QuietPatch files and directories..."
    
    # Remove binary and configuration
    rm -rf /opt/quietpatch
    
    # Remove configuration
    rm -rf /etc/quietpatch
    
    # Remove data and logs (ask user first)
    if [[ -d /var/lib/quietpatch ]] || [[ -d /var/log/quietpatch ]]; then
        echo
        read -p "Remove data and logs? This will delete all scan results and reports. (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf /var/lib/quietpatch
            rm -rf /var/log/quietpatch
            log_info "Data and logs removed"
        else
            log_info "Data and logs preserved"
        fi
    fi
    
    # Remove symlink
    rm -f /usr/local/bin/quietpatch
    
    log_info "Files and directories removed ✓"
}

# Remove service user
remove_user() {
    log_info "Removing service user..."
    
    if id "quietpatch" &>/dev/null; then
        userdel quietpatch
        log_info "Service user quietpatch removed ✓"
    else
        log_info "Service user quietpatch not found"
    fi
}

# Main uninstall flow
main() {
    log_info "Starting QuietPatch Linux uninstallation..."
    
    check_root
    stop_services
    remove_systemd
    remove_files
    remove_user
    
    log_info "Uninstallation completed successfully! 🎉"
    log_info ""
    log_info "QuietPatch has been completely removed from the system."
    log_info "If you preserved data/logs, they remain in:"
    log_info "  - /var/lib/quietpatch (if preserved)"
    log_info "  - /var/log/quietpatch (if preserved)"
}

# Run main function
main "$@"


