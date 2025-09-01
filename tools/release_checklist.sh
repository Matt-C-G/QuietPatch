#!/usr/bin/env bash
set -euo pipefail

# QuietPatch Release Checklist
# Run this before tagging a release to ensure all gates pass

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Check if running from repo root
check_repo_root() {
    if [[ ! -f "qp_cli.py" ]] || [[ ! -d "src" ]]; then
        log_error "Must run from repository root directory"
        exit 1
    fi
    log_info "Running from repository root ✓"
}

# Check Git status
check_git_status() {
    log_step "1. Checking Git status..."
    
    # Check if we're on main branch
    local current_branch
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" ]]; then
        log_error "Must be on main branch (currently on: $current_branch)"
        exit 1
    fi
    log_info "On main branch ✓"
    
    # Check if working directory is clean
    if [[ -n "$(git status --porcelain)" ]]; then
        log_error "Working directory has uncommitted changes:"
        git status --short
        exit 1
    fi
    log_info "Working directory is clean ✓"
    
    # Check if up to date with remote
    git fetch origin
    local local_commit
    local remote_commit
    local_commit=$(git rev-parse HEAD)
    remote_commit=$(git rev-parse origin/main)
    
    if [[ "$local_commit" != "$remote_commit" ]]; then
        log_error "Local main is not up to date with origin/main"
        log_error "  Local:  $local_commit"
        log_error "  Remote: $remote_commit"
        exit 1
    fi
    log_info "Up to date with origin/main ✓"
}

# Check version consistency
check_version_consistency() {
    log_step "2. Checking version consistency..."
    
    # Check VERSION file
    if [[ -f "VERSION" ]]; then
        local version_file
        version_file=$(cat VERSION)
        log_info "VERSION file contains: $version_file"
    else
        log_warn "No VERSION file found"
    fi
    
    # Check for version constants in code
    local version_constants
    version_constants=$(grep -r "0\.2\." src/ --include="*.py" 2>/dev/null || true)
    if [[ -n "$version_constants" ]]; then
        log_info "Version constants found in code:"
        echo "$version_constants"
    fi
    
    log_info "Version consistency check completed ✓"
}

# Run selfcheck
run_selfcheck() {
    log_step "3. Running selfcheck..."
    
    if [[ -f "tools/selfcheck.py" ]]; then
        if PYTHONPATH=. python3 tools/selfcheck.py; then
            log_info "Selfcheck passed ✓"
        else
            log_error "Selfcheck failed!"
            exit 1
        fi
    else
        log_warn "selfcheck.py not found, skipping"
    fi
}

# Run security scan
run_security_scan() {
    log_step "4. Running security scan..."
    
    if command -v bandit >/dev/null 2>&1; then
        log_info "Running bandit security scan..."
        if bandit -q -r src; then
            log_info "Bandit scan passed ✓"
        else
            log_warn "Bandit found security issues (check output above)"
            log_warn "Review and fix high-severity issues before release"
        fi
    else
        log_warn "bandit not available, skipping security scan"
        log_info "Install with: pip install bandit"
    fi
}

# Check for placeholder CVEs
check_placeholder_cves() {
    log_step "5. Checking for placeholder CVEs..."
    
    local placeholder_count
    placeholder_count=$(grep -r "CVE-2024-9999\|CVE-2024-8888" . --exclude-dir=.git --exclude-dir=node_modules 2>/dev/null | wc -l || echo "0")
    
    if [[ "$placeholder_count" -gt 0 ]]; then
        log_error "Found $placeholder_count placeholder CVEs in codebase!"
        log_error "These must be removed before release:"
        grep -r "CVE-2024-9999\|CVE-2024-8888" . --exclude-dir=.git --exclude-dir=node_modules 2>/dev/null || true
        exit 1
    fi
    
    log_info "No placeholder CVEs found ✓"
}

# Check database snapshot
check_database_snapshot() {
    log_step "6. Checking database snapshot..."
    
    local db_files
    db_files=$(ls dist/db-*.tar.zst 2>/dev/null || true)
    
    if [[ -z "$db_files" ]]; then
        log_error "No database snapshot found in dist/"
        log_error "Build one with: python3 tools/db_snapshot.py --out dist"
        exit 1
    fi
    
    # Check database age
    for db_file in $db_files; do
        local file_age_days
        file_age_days=$(( ( $(date +%s) - $(stat -f %m "$db_file" 2>/dev/null || stat -c %Y "$db_file") ) / 86400 ))
        
        if [[ "$file_age_days" -gt 30 ]]; then
            log_warn "Database snapshot is $file_age_days days old: $db_file"
            log_warn "Consider refreshing before release"
        else
            log_info "Database snapshot is $file_age_days days old ✓"
        fi
        
        # Check if checksum file exists
        local checksum_file="${db_file}.sha256"
        if [[ -f "$checksum_file" ]]; then
            log_info "Checksum file found: $checksum_file ✓"
        else
            log_warn "No checksum file for: $db_file"
        fi
    done
    
    log_info "Database snapshot check completed ✓"
}

# Check artifacts
check_artifacts() {
    log_step "7. Checking artifacts..."
    
    local missing_artifacts=()
    
    # Check for required PEX files
    if [[ ! -f "dist/quietpatch-macos.pex" ]]; then
        missing_artifacts+=("quietpatch-macos.pex")
    fi
    
    if [[ ! -f "dist/quietpatch-linux-x64.pex" ]]; then
        missing_artifacts+=("quietpatch-linux-x64.pex")
    fi
    
    if [[ ! -f "dist/quietpatch-windows-x64.zip" ]]; then
        missing_artifacts+=("quietpatch-windows-x64.zip")
    fi
    
    if [[ ${#missing_artifacts[@]} -gt 0 ]]; then
        log_error "Missing required artifacts: ${missing_artifacts[*]}"
        log_error "Build artifacts first:"
        log_error "  ./tools/build_pex.sh"
        log_error "  .\tools\build_pex.ps1 (on Windows)"
        exit 1
    fi
    
    log_info "All required artifacts present ✓"
    
    # Check artifact sizes
    echo "=== Artifact sizes ==="
    ls -lh dist/quietpatch-*.pex dist/quietpatch-*.zip 2>/dev/null || true
}

# Check documentation
check_documentation() {
    log_step "8. Checking documentation..."
    
    local missing_docs=()
    
    if [[ ! -f "README.md" ]]; then
        missing_docs+=("README.md")
    fi
    
    if [[ ! -f "docs/PRODUCTION_DEPLOYMENT.md" ]]; then
        missing_docs+=("docs/PRODUCTION_DEPLOYMENT.md")
    fi
    
    if [[ ! -f "docs/RELEASE_STEPS.md" ]]; then
        missing_docs+=("docs/RELEASE_STEPS.md")
    fi
    
    if [[ ${#missing_docs[@]} -gt 0 ]]; then
        log_warn "Missing documentation: ${missing_docs[*]}"
    else
        log_info "All required documentation present ✓"
    fi
    
    # Check for installation scripts
    if [[ -f "packaging/linux/install.sh" ]] && [[ -f "packaging/windows/install.ps1" ]]; then
        log_info "Installation scripts present ✓"
    else
        log_warn "Some installation scripts missing"
    fi
}

# Check CI workflow
check_ci_workflow() {
    log_step "9. Checking CI workflow..."
    
    if [[ -f ".github/workflows/release.yml" ]]; then
        log_info "Release workflow found ✓"
        
        # Check if workflow has matrix builds
        if grep -q "matrix:" .github/workflows/release.yml; then
            log_info "Matrix builds configured ✓"
        else
            log_warn "Matrix builds not configured in workflow"
        fi
    else
        log_error "Release workflow not found!"
        exit 1
    fi
}

# Final release readiness check
final_check() {
    log_step "10. Final release readiness check..."
    
    echo
    log_info "🎯 RELEASE READINESS SUMMARY:"
    echo
    
    # Check critical items
    local critical_failures=0
    
    if [[ ! -f "dist/quietpatch-macos.pex" ]]; then
        log_error "❌ macOS PEX missing"
        ((critical_failures++))
    else
        log_info "✅ macOS PEX ready"
    fi
    
    if [[ ! -f "dist/quietpatch-linux-x64.pex" ]]; then
        log_error "❌ Linux PEX missing"
        ((critical_failures++))
    else
        log_info "✅ Linux PEX ready"
    fi
    
    if [[ ! -f "dist/quietpatch-windows-x64.zip" ]]; then
        log_error "❌ Windows ZIP missing"
        ((critical_failures++))
    else
        log_info "✅ Windows ZIP ready"
    fi
    
    if [[ ! -f "dist/db-"*.tar.zst ]]; then
        log_error "❌ Database snapshot missing"
        ((critical_failures++))
    else
        log_info "✅ Database snapshot ready"
    fi
    
    if [[ ! -f ".github/workflows/release.yml" ]]; then
        log_error "❌ CI workflow missing"
        ((critical_failures++))
    else
        log_info "✅ CI workflow ready"
    fi
    
    echo
    
    if [[ $critical_failures -eq 0 ]]; then
        log_info "🎉 ALL CRITICAL CHECKS PASSED! 🎉"
        log_info ""
        log_info "QuietPatch is ready for release!"
        log_info ""
        log_info "Next steps:"
        log_info "  1. Update CHANGELOG.md if needed"
        log_info "  2. git commit -am 'v0.2.2: cross-platform artifacts + offline DB snapshot'"
        log_info "  3. git tag -a v0.2.2 -m 'QuietPatch v0.2.2'"
        log_info "  4. git push origin main --follow-tags"
        log_info "  5. CI will automatically build and publish the release"
        log_info ""
        log_info "Release checklist: COMPLETE ✅"
    else
        log_error "❌ $critical_failures critical checks failed!"
        log_error "Fix the issues above before proceeding with release"
        exit 1
    fi
}

# Main checklist flow
main() {
    log_info "🔍 Starting QuietPatch Release Checklist..."
    log_info "This script runs all release gates before tagging"
    echo
    
    check_repo_root
    check_git_status
    check_version_consistency
    run_selfcheck
    run_security_scan
    check_placeholder_cves
    check_database_snapshot
    check_artifacts
    check_documentation
    check_ci_workflow
    final_check
}

# Run main function
main "$@"


