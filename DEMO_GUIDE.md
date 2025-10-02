# QuietPatch Demo & Documentation

## 🚀 Quick Start

### Try Reports (No Install Required)

**macOS/Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/scripts/qp-report.py -o qp-report
chmod +x qp-report
./qp-report exec \
  --scan data/scan.json \
  --kpi data/kpi.json \
  --business-units data/business_units.json \
  --actions data/actions.json \
  --approval data/approval.json \
  --watermark "APPROVED • CAB-2025-10-01" \
  --out out/exec-report.html --pdf out/exec-report.pdf
```

**Windows (PowerShell):**
```powershell
iwr https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/scripts/qp-report.ps1 -OutFile qp-report.ps1
.\qp-report.ps1 exec `
  --scan data\scan.json `
  --kpi data\kpi.json `
  --business-units data\business_units.json `
  --actions data\actions.json `
  --approval data\approval.json `
  --watermark "APPROVED • CAB-2025-10-01" `
  --out out\exec-report.html --pdf out\exec-report.pdf
```

### Complete Demo Setup
```bash
# Run the complete demo setup
./demo_complete.sh
```

### Generate Reports
```bash
# Generate both Technical and Executive reports
./demo_reports.sh
```

### Test Canary + Rollback
```bash
# Test the canary deployment system
./demo_canary_rollback.sh
```

## 📊 Dual-Report System

### Technical Report (Engineers/SRE/IT)
```bash
quietpatch report tech \
  --scan data/scan.json \
  --policy data/policy.json \
  --approval data/approval.json \
  --assets data/assets.json \
  --watermark "APPROVED • CAB-2025-10-01" \
  --out out/tech-report.html \
  --pdf out/tech-report.pdf
```

### Executive Report (CIO/CISO/Board)
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

### Optional: Sign Reports
```bash
# Sign reports with minisign (if available)
quietpatch report tech --scan data/scan.json --assets data/assets.json --out out/tech.html --sign --sign-key ~/.config/quietpatch/minisign.key
```

## 📦 Canary + Rollback System

### Build Bundle with SHA256 Hashes
```bash
cd canary-rollback/sample-bundle
python3 build-hashes.py
```

### Deploy with Orchestration Tools

#### Ansible
```bash
ansible-playbook -i inventory canary-rollback/examples/deploy_canary_waves.yml
```

#### Microsoft Intune
1. Package as Win32 app
2. Use detection script: `canary-rollback/scripts/win/detect.ps1`
3. Install command: `canary-rollback/scripts/win/apply.ps1`
4. Uninstall command: `canary-rollback/scripts/win/rollback.ps1`

#### SCCM/ConfigMgr
1. Create Application with detection method
2. Use scripts from `canary-rollback/scripts/win/`
3. Configure maintenance windows

#### Jamf Pro
1. Create Policy with Extension Attribute
2. Use scripts from `canary-rollback/scripts/mac/`
3. Configure Smart Groups

## 🔧 Sample Data Files

All sample data files are ready in the `data/` directory:

- `scan.json` - Scan totals and metadata
- `assets.json` - Asset inventory with CVEs and remediation
- `policy.json` - Policy configuration
- `approval.json` - Change approval metadata
- `kpi.json` - Executive KPIs
- `business_units.json` - Business unit breakdown
- `actions.json` - Action items and timelines

## 📋 Ring-Based Deployment

For ring-based deployments, use the enhanced manifest:

```bash
# Use ring-based manifest
cp canary-rollback/examples/manifest-rings.json canary-rollback/sample-bundle/manifest.json
python3 canary-rollback/sample-bundle/build-hashes.py
```

## 🎯 Features

### Dual-Report System
- ✅ **Technical Report**: Detailed HTML/PDF for engineers
- ✅ **Executive Report**: High-level HTML/PDF for leadership
- ✅ **Watermarks**: CAB approval status
- ✅ **Signing**: Optional minisign integration
- ✅ **Deterministic**: Same input = same output
- ✅ **Offline**: No network dependencies

### Canary + Rollback System
- ✅ **Cross-platform**: Windows/macOS/Linux scripts
- ✅ **Integrity**: SHA256 verification
- ✅ **Policy Gates**: Maintenance windows, success thresholds
- ✅ **Ring Deployment**: Gradual rollout with auto-rollback
- ✅ **Orchestration**: Ansible/Intune/SCCM/Jamf examples
- ✅ **Offline**: No telemetry, local operation

## 🔗 Integration Examples

### Microsoft Intune Integration
```powershell
# Detection script
.\canary-rollback\scripts\win\detect.ps1 -ManifestPath .\manifest.json

# Install script  
.\canary-rollback\scripts\win\apply.ps1 -ManifestPath .\manifest.json -ArtifactId openssl-3.0.14-win64

# Rollback script
.\canary-rollback\scripts\win\rollback.ps1 -ManifestPath .\manifest.json -ArtifactId openssl-3.0.14-win64
```

### Ansible Integration
```yaml
# Use the provided playbook
- name: Deploy QuietPatch bundle
  import_playbook: canary-rollback/examples/deploy_canary_waves.yml
  vars:
    bundle_path: "canary-rollback/sample-bundle"
    target_ring: "ring0-canary"
```

## 📖 Documentation

- **Canary + Rollback**: `canary-rollback/docs/README.md`
- **Dual Reports**: `quietpatch/report/README.md`
- **Sample Bundle**: `canary-rollback/sample-bundle/README.md`
- **Integration Examples**: `canary-rollback/examples/`

## 🎉 Ready for Production

QuietPatch is enterprise-ready with:
- Deterministic reporting
- Offline operation
- Cross-platform support
- Policy-driven deployment
- Audit trails
- Change approval workflows
- Optional digital signing

Perfect for SOC 2, ISO 27001, and enterprise security requirements.
