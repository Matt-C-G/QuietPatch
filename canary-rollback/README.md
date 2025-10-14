# QuietPatch Canary + Rollback System

A comprehensive, enterprise-ready deployment system for vulnerability remediation across Windows, macOS, and Linux platforms.

##  Quick Start

1. **Copy the sample bundle**: `cp -r canary-rollback/sample-bundle/ my-remediation-bundle/`
2. **Replace placeholder artifacts** with real installers
3. **Generate SHA256 hashes**: `./build_bundle.sh`
4. **Deploy using your orchestration tool** (Ansible, Intune, SCCM, Jamf)

##  Directory Structure

```
canary-rollback/
├── examples/                    # Templates and examples
│   ├── manifest.json           # Bundle manifest template
│   ├── deploy_canary_waves.yml # Ansible playbook
│   ├── intune_integration.md   # Intune setup guide
│   ├── jamf_integration.md     # Jamf Pro setup guide
│   └── sccm_integration.md     # SCCM setup guide
├── scripts/                     # Cross-platform scripts
│   ├── win/                    # PowerShell scripts
│   │   ├── detect.ps1         # Version detection
│   │   ├── apply.ps1          # Install target version
│   │   ├── verify.ps1         # Verify installation
│   │   └── rollback.ps1       # Rollback to previous
│   ├── mac/                    # Bash scripts for macOS
│   └── linux/                  # Bash scripts for Linux
├── sample-bundle/              # Complete example bundle
│   ├── manifest.json          # Bundle configuration
│   ├── artifacts/            # Platform-specific installers
│   ├── scripts/              # Platform-specific scripts
│   └── build_bundle.sh       # SHA256 hash generator
├── policies/                  # Deployment policies
│   └── policy-critical-only.yml
└── docs/                      # Documentation
    └── README.md
```

##  Key Features

- ** Cross-Platform**: Windows (PowerShell), macOS (Bash), Linux (Bash)
- ** Canary Deployment**: Test on small subset before full rollout
- ** Automatic Rollback**: Revert failed deployments automatically
- ** Integrity Verification**: SHA256 validation of all artifacts
- ** Preflight Checks**: Disk space, power, active sessions
- ** Comprehensive Logging**: Detailed logs for audit and troubleshooting
- ** Zero Telemetry**: Completely offline operation
- ** Enterprise Integration**: Works with Ansible, Intune, SCCM, Jamf

##  Integration Options

### Ansible/AWX
```bash
ansible-playbook -i inventory deploy_canary_waves.yml
```

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

##  Exit Code Contract

- **0**: Success (up-to-date or successfully updated)
- **1**: Needs remediation or verification failed
- **2**: Not installed (treat as needs remediation)
- **3**: Integrity check failed (SHA256 mismatch)

##  Security Model

- **No Local Admin**: QuietPatch never requires local admin credentials
- **Orchestration Control**: MDM/SCCM tools run scripts as SYSTEM/root
- **Offline Operation**: No network calls from remediation scripts
- **Integrity Verification**: All artifacts SHA256 signed and validated

##  Policy Gates

- **Maintenance Windows**: Deploy only during approved windows
- **Success Thresholds**: Require ≥98% success before proceeding
- **Auto-Rollback**: Trigger rollback if failure rate >2%
- **Preflight Checks**: Disk space, power, active sessions

## ️ Example Usage

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

##  Documentation

- [Complete Documentation](docs/README.md)
- [Ansible Integration](examples/deploy_canary_waves.yml)
- [Intune Integration](examples/intune_integration.md)
- [Jamf Integration](examples/jamf_integration.md)
- [SCCM Integration](examples/sccm_integration.md)

##  Best Practices

- Always test in isolated environment first
- Use canary deployment for all production rollouts
- Monitor logs for any issues or failures
- Keep rollback artifacts readily available
- Document all customizations and policies
- Regular testing of rollback procedures

##  Support

For questions or issues with the Canary + Rollback system, refer to the QuietPatch documentation or create an issue in the repository.
