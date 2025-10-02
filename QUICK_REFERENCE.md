# QuietPatch: Enterprise-Ready CVE Management

## 🎯 What This Proves

**Dual-Report System**: Generate both Technical (engineer) and Executive (C-suite) reports with watermarks, approval metadata, and optional digital signing.

**Canary + Rollback**: Cross-platform deployment with ring-based rollouts, integrity checks, and automated rollback on failure.

## 🚀 Quick Demo

```bash
# Complete demo setup
./demo_complete.sh

# Generate both reports
./demo_reports.sh

# Test canary deployment
./demo_canary_rollback.sh
```

## 📊 Reports

### Technical Report (Engineers/SRE/IT)
- Detailed asset inventory with CVEs
- Copyable remediation commands
- Policy decisions and gates
- Change approval metadata
- Deterministic SHA256 footer

### Executive Report (CIO/CISO/Board)
- KPI dashboard (Exposure Index, KEV backlog, SLA adherence)
- Business unit breakdown
- 30/60/90 day action items
- Risk trend visualization
- Audit proof with signatures

## 📦 Canary + Rollback

### Cross-Platform Scripts
- **Windows**: PowerShell with MSI/registry detection
- **macOS**: Bash with app bundle verification
- **Linux**: Bash with package manager integration

### Orchestration Ready
- **Ansible**: Playbook for ring-based deployment
- **Intune**: Win32 app packaging with detection
- **SCCM**: Application model with collections
- **Jamf**: Policies with Extension Attributes

### Policy Gates
- Maintenance windows
- Success rate thresholds
- Maximum failure limits
- Auto-rollback triggers

## 🔧 Sample Commands

### Generate Technical Report
```bash
quietpatch report tech \
  --scan data/scan.json \
  --assets data/assets.json \
  --policy data/policy.json \
  --approval data/approval.json \
  --watermark "APPROVED • CAB-2025-10-01" \
  --out out/tech-report.html \
  --pdf out/tech-report.pdf
```

### Generate Executive Report
```bash
quietpatch report exec \
  --scan data/scan.json \
  --kpi data/kpi.json \
  --business-units data/business_units.json \
  --actions data/actions.json \
  --approval data/approval.json \
  --watermark "APPROVED • CAB-2025-10-01" \
  --out out/exec-report.html \
  --pdf out/exec-report.pdf
```

### Build Bundle with Integrity
```bash
cd canary-rollback/sample-bundle
python3 build-hashes.py
```

### Deploy with Ansible
```bash
ansible-playbook -i inventory canary-rollback/examples/deploy_canary_waves.yml
```

## 🎯 Enterprise Features

- **Offline Operation**: No telemetry, no network dependencies
- **Deterministic Output**: Same input = identical output
- **Audit Trail**: SHA256 hashes, approval metadata, change tracking
- **Policy-Driven**: Configurable gates and thresholds
- **Cross-Platform**: Windows/macOS/Linux support
- **Integration Ready**: Works with existing orchestration tools
- **Optional Signing**: Minisign integration for report integrity

## 📋 Sample Data

Ready-to-use sample files in `data/`:
- `scan.json` - Scan totals and metadata
- `assets.json` - Asset inventory with CVEs
- `policy.json` - Policy configuration
- `approval.json` - Change approval
- `kpi.json` - Executive KPIs
- `business_units.json` - BU breakdown
- `actions.json` - Action items

## 🔗 Integration Examples

### Microsoft Intune
```powershell
# Detection
.\canary-rollback\scripts\win\detect.ps1 -ManifestPath .\manifest.json

# Install
.\canary-rollback\scripts\win\apply.ps1 -ManifestPath .\manifest.json -ArtifactId openssl-3.0.14-win64

# Rollback
.\canary-rollback\scripts\win\rollback.ps1 -ManifestPath .\manifest.json -ArtifactId openssl-3.0.14-win64
```

### SCCM/ConfigMgr
- Create Application with detection method
- Use scripts from `canary-rollback/scripts/win/`
- Configure maintenance windows and success thresholds

### Jamf Pro
- Create Policy with Extension Attribute
- Use scripts from `canary-rollback/scripts/mac/`
- Configure Smart Groups for ring deployment

## 🎉 Production Ready

Perfect for:
- SOC 2 compliance
- ISO 27001 requirements
- Enterprise security programs
- Change management workflows
- Audit and compliance reporting

**Zero telemetry, offline operation, deterministic output, enterprise integration.**
