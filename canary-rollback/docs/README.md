# QuietPatch Canary + Rollback System

## Overview

The QuietPatch Canary + Rollback system provides enterprise-grade deployment automation for vulnerability remediation across Windows, macOS, and Linux platforms. It implements a safe, staged rollout pattern with automatic rollback capabilities.

## Key Features

- **Cross-Platform Support**: Windows (PowerShell), macOS (Bash), Linux (Bash)
- **Canary Deployment**: Test on small subset before full rollout
- **Automatic Rollback**: Revert failed deployments automatically
- **Integrity Verification**: SHA256 validation of all artifacts
- **Preflight Checks**: Disk space, power, active sessions
- **Comprehensive Logging**: Detailed logs for audit and troubleshooting
- **Zero Telemetry**: Completely offline operation

## Architecture

```
quietpatch_bundle/
├── manifest.json              # Single source of truth
├── artifacts/                 # Platform-specific installers
│   ├── win/                  # Windows MSI packages
│   ├── mac/                  # macOS PKG packages
│   └── linux/                # Linux DEB/RPM packages
├── scripts/                  # Platform-specific scripts
│   ├── win/                  # PowerShell scripts
│   ├── mac/                  # Bash scripts
│   └── linux/                # Bash scripts
├── signatures/               # Minisign signatures
└── policies/                 # Deployment policies
```

## Deployment Flow

1. **Detect**: Check current version vs target version
2. **Apply**: Install target version with integrity verification
3. **Verify**: Confirm successful installation
4. **Rollback**: Revert to previous version if needed

## Exit Code Contract

- **0**: Success (up-to-date or successfully updated)
- **1**: Needs remediation or verification failed
- **2**: Not installed (treat as needs remediation)
- **3**: Integrity check failed (SHA256 mismatch)

## Integration Options

### Ansible/AWX
- Use `deploy_canary_waves.yml` playbook
- Supports serial deployment with approval gates
- Automatic rollback for failed canaries

### Microsoft Intune
- Package as Win32 app
- Use PowerShell detection scripts
- Dynamic groups for canary/wave assignment

### Jamf Pro
- Extension Attributes for version detection
- Smart Groups for targeting
- Policies for apply/rollback operations

### SCCM/ConfigMgr
- Application model with detection scripts
- Collections for canary deployment
- Uninstall program for rollback

## Security Model

- **No Local Admin**: QuietPatch never requires local admin credentials
- **Orchestration Control**: MDM/SCCM tools run scripts as SYSTEM/root
- **Offline Operation**: No network calls from remediation scripts
- **Integrity Verification**: All artifacts SHA256 signed and validated

## Policy Gates

- **Maintenance Windows**: Deploy only during approved windows
- **Success Thresholds**: Require ≥98% success before proceeding
- **Auto-Rollback**: Trigger rollback if failure rate >2%
- **Preflight Checks**: Disk space, power, active sessions

## Getting Started

1. **Create Bundle**: Use `examples/manifest.json` as template
2. **Add Artifacts**: Place installers in appropriate platform directories
3. **Generate SHA256**: Update manifest with artifact hashes
4. **Test Detection**: Run detect scripts to verify current state
5. **Deploy Canary**: Start with small test group
6. **Monitor Success**: Check logs and success rates
7. **Rollout Waves**: Deploy to larger groups based on success

## Example Usage

```bash
# Test detection
./scripts/win/detect.ps1

# Apply remediation
./scripts/win/apply.ps1

# Verify installation
./scripts/win/verify.ps1

# Rollback if needed
./scripts/win/rollback.ps1
```

## Best Practices

- Always test in isolated environment first
- Use canary deployment for all production rollouts
- Monitor logs for any issues or failures
- Keep rollback artifacts readily available
- Document all customizations and policies
- Regular testing of rollback procedures

## Support

For questions or issues with the Canary + Rollback system, refer to the QuietPatch documentation or create an issue in the repository.
