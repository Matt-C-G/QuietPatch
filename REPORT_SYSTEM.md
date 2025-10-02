# QuietPatch Dual-Report System

## Overview

The QuietPatch Dual-Report System provides enterprise-grade reporting capabilities with two distinct report types:

- **Technical Report**: Detailed engineer runbook with actionable remediation steps
- **Executive Report**: Concise CISO/Board summary with KPIs and trends

## Key Features

- **✅ Offline Generation**: No network calls, completely air-gapped
- **✅ Deterministic Output**: Same input always produces identical reports
- **✅ Watermark Support**: Add approval status banners (DRAFT, APPROVED, etc.)
- **✅ Dual-Approval Metadata**: Embed change approval information
- **✅ Optional Signing**: Minisign integration for document integrity
- **✅ Cross-Platform**: Works on Windows, macOS, and Linux
- **✅ PDF + HTML**: Generate both formats simultaneously

## Quick Start

### 1. Generate Sample Data

```bash
python3 test_dual_reports.py
```

### 2. Create Technical Report

```bash
python3 qp_cli.py report tech \
  --scan test-reports/scan.json \
  --policy test-reports/policy.json \
  --out test-reports/tech-report.html \
  --pdf test-reports/tech-report.pdf \
  --approval test-reports/approval.json \
  --watermark "APPROVED • CAB-2025-10-01"
```

### 3. Create Executive Report

```bash
python3 qp_cli.py report exec \
  --scan test-reports/scan.json \
  --kpi test-reports/kpi.json \
  --out test-reports/exec-report.pdf \
  --html test-reports/exec-report.html \
  --approval test-reports/approval.json \
  --watermark "APPROVED • CAB-2025-10-01"
```

## Command Reference

### Technical Report (`report tech`)

**Purpose**: Detailed engineer runbook with remediation steps

**Required Arguments**:
- `--scan`: Path to scan.json file
- `--out`: HTML output path

**Optional Arguments**:
- `--pdf`: PDF output path (requires wkhtmltopdf)
- `--policy`: Policy decision log JSON
- `--bundle`: Remediation bundle ZIP file
- `--prev`: Previous scan for diff analysis
- `--watermark`: Watermark banner text
- `--approval`: Approval metadata JSON
- `--sign`: Sign outputs with minisign
- `--sign-key`: Path to minisign secret key

**Output**: HTML report with:
- Asset inventory and vulnerability details
- Remediation commands and rollback procedures
- Policy decisions and deployment rings
- Severity distribution charts
- Business unit heatmaps
- Change approval metadata

### Executive Report (`report exec`)

**Purpose**: CISO/Board summary with KPIs

**Required Arguments**:
- `--scan`: Path to scan.json file
- `--out`: PDF output path

**Optional Arguments**:
- `--html`: HTML output path
- `--kpi`: Pre-aggregated KPI JSON
- `--trend-dir`: Directory with historical scans
- `--watermark`: Watermark banner text
- `--approval`: Approval metadata JSON
- `--sign`: Sign outputs with minisign
- `--sign-key`: Path to minisign secret key

**Output**: PDF report with:
- Key performance indicators (KPIs)
- Exposure trend sparklines
- Severity distribution summary
- Next action items
- Audit proof with document hashes

## Data Formats

### Scan JSON Format

```json
{
  "run_id": "RUN-2025-10-01-001",
  "catalog": {
    "nvd_sha256": "abc123...",
    "kev_sha256": "def456...",
    "epss_sha256": "ghi789...",
    "signed": true
  },
  "assets": [
    {
      "asset_id": "WIN-001",
      "hostname": "web-server-01", 
      "os": "Windows Server 2022",
      "bu": "Finance",
      "vulns": [
        {
          "cve": "CVE-2023-12345",
          "severity": "critical",
          "cvss": 9.8,
          "kev": true,
          "epss": 0.83,
          "fix_available": true,
          "fix": {
            "target_version": "23.01",
            "install_cmd": "msiexec /i package.msi /qn",
            "verify_cmd": "package.exe --version",
            "rollback_cmd": "msiexec /i old-package.msi /qn"
          }
        }
      ]
    }
  ]
}
```

### Approval JSON Format

```json
{
  "change_id": "CAB-2025-10-01-042",
  "submitted_by": "Matthew Graham",
  "submitted_at": "2025-10-01T13:05:00Z",
  "approver_1": {"name": "C. Romero", "role": "Ops Manager", "date": "2025-10-01"},
  "approver_2": {"name": "J. Patel", "role": "CISO", "date": "2025-10-01"},
  "scope": "Ring-0 canary on 25 endpoints",
  "notes": "Rollback rehearsed on QA image"
}
```

### KPI JSON Format

```json
{
  "assets_total": 1200,
  "assets_scanned": 1187,
  "exposure_index": 3.4,
  "kev_backlog": 27,
  "sla": {"critical_7d": 0.92, "high_30d": 0.88}
}
```

## Dependencies

### Required
- Python 3.8+
- Jinja2 (templating)
- matplotlib (charts)

### Optional
- wkhtmltopdf (for PDF generation)
- minisign (for document signing)

### Installation

```bash
# Install Python dependencies
pip install jinja2 matplotlib

# Install PDF generation (macOS)
brew install wkhtmltopdf

# Install PDF generation (Ubuntu/Debian)
sudo apt-get install wkhtmltopdf

# Install signing (macOS)
brew install minisign

# Install signing (Ubuntu/Debian)
sudo apt-get install minisign
```

## Security Features

### Document Integrity
- SHA256 hash embedded in every report footer
- Deterministic generation ensures reproducible outputs
- Optional minisign signatures for tamper detection

### Offline Operation
- No network calls during report generation
- All charts generated as static SVG
- Templates use embedded CSS (no external resources)

### Approval Workflow
- Dual-approval metadata embedded in reports
- Watermark banners for approval status
- Change tracking with CAB numbers and scope

## Best Practices

1. **Always use watermarks** to indicate report status (DRAFT, APPROVED, etc.)
2. **Include approval metadata** for audit trails
3. **Sign critical reports** with minisign for integrity
4. **Store historical scans** for trend analysis
5. **Use consistent naming** for report files and CAB numbers

## Troubleshooting

### PDF Generation Fails
- Install wkhtmltopdf: `brew install wkhtmltopdf` (macOS) or `sudo apt-get install wkhtmltopdf` (Linux)
- Check file permissions on output directory
- Verify HTML template renders correctly in browser first

### Signing Fails
- Install minisign: `brew install minisign` (macOS) or `sudo apt-get install minisign` (Linux)
- Ensure secret key file exists and is readable
- Check minisign key format (should be private key)

### Charts Not Rendering
- Install matplotlib: `pip install matplotlib`
- Check Python environment and dependencies
- Verify SVG output in browser developer tools

## Integration Examples

### CI/CD Pipeline
```bash
# Generate reports in CI
quietpatch report tech --scan scan.json --out tech-report.html --pdf tech-report.pdf
quietpatch report exec --scan scan.json --out exec-report.pdf --watermark "CI-GENERATED"
```

### Change Management
```bash
# Generate approved reports
quietpatch report tech --scan scan.json --out tech-report.html \
  --approval approval.json --watermark "APPROVED • CAB-2025-10-01" \
  --sign --sign-key ~/.config/quietpatch/minisign.key
```

### Audit Preparation
```bash
# Generate signed reports for audit
quietpatch report exec --scan scan.json --out audit-report.pdf \
  --approval approval.json --watermark "AUDIT-READY" \
  --sign --sign-key ~/.config/quietpatch/minisign.key
```
