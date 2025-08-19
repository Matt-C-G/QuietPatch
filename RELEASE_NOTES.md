# QuietPatch Release Notes

## Version 2.0.0 - Policy Engine & Action Engine

**Release Date**: August 13, 2025  
**Previous Version**: 1.x (Legacy scanner)

---

## 🚀 New Features

### Policy Engine
- **Configurable filtering**: Allow/deny lists, minimum severity gates, CVE limits
- **Smart severity handling**: Automatic severity derivation from CVSS scores
- **Policy-aware sorting**: Risk-based ordering with KEV (Known Exploited Vulnerabilities) promotion
- **Deterministic output**: Consistent results across multiple scans

### Action Engine
- **Remediation suggestions**: Specific commands for Homebrew, Microsoft AutoUpdate, Apple Software Update
- **Direct download links**: Vendor-specific upgrade URLs
- **Safety-first approach**: Copy buttons instead of auto-execution
- **Comprehensive coverage**: Generic fallbacks for unmapped applications

### Enhanced Reporting
- **HTML vulnerability reports**: Rich, interactive web interface
- **Action column**: Clear remediation steps for each vulnerable application
- **Severity filters**: Pill-based filtering by risk level
- **Search functionality**: Find specific apps or CVEs quickly

---

## ⚙️ Policy Configuration

### Default Policy (`config/policy.yml`)
```yaml
# QuietPatch policy
allow: []                    # Whitelist specific apps (optional)
deny: []                     # Blacklist specific apps (optional)
min_severity: low            # Minimum severity to include
treat_unknown_as: low        # How to handle unknown severity CVEs
only_with_cves: true         # Hide apps with no vulnerabilities
limit_per_app: 50            # Maximum CVEs per application
```

### Policy Options
- **min_severity**: `none`, `low`, `medium`, `high`, `critical`
- **treat_unknown_as**: How to handle CVEs with unknown severity
- **allow/deny**: Use glob patterns like `"microsoft:*"` or `"*:safari"`

---

## 🔐 AGE Encryption Setup

### 1. Generate AGE Key Pair
```bash
# Generate new key pair
age-keygen -o ~/.age/quietpatch.txt

# Extract public key for encryption
age-keygen -y ~/.age/quietpatch.txt > ~/.age/quietpatch.pub
```

### 2. Set Environment Variables
```bash
# For scanning (encryption)
export AGE_RECIPIENT="$(cat ~/.age/quietpatch.pub)"

# For reporting (decryption)
export AGE_IDENTITY="~/.age/quietpatch.txt"
```

### 3. Alternative: Direct Key Usage
```bash
# Scan with public key
python3 qp_cli.py scan -o data --age-recipient "age1..."

# Report with private key
python3 qp_cli.py report -i data/vuln_log.json.enc -o report.html --age-identity ~/.age/quietpatch.txt
```

---

## 📖 Usage Instructions

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set AGE recipient
export AGE_RECIPIENT="your_age_public_key"

# 3. Run vulnerability scan
PYTHONPATH=. python3 qp_cli.py scan -o data --age-recipient "$AGE_RECIPIENT"

# 4. Generate HTML report
PYTHONPATH=. python3 qp_cli.py report -i data/vuln_log.json.enc -o report.html --age-identity ~/.age/quietpatch.txt
```

### Makefile Targets
```bash
# Scan for vulnerabilities
make scan

# Generate HTML report
make report

# Sync CVE database
make db-sync

# Run tests
make verify
```

### Database Synchronization
```bash
# Refresh local CVE database (5 years back)
PYTHONPATH=. python3 qp_cli.py db-sync --years-back 5
```

---

## 🔒 Privacy & Security

### Data Storage
- **Local only**: All data stored locally in `data/` directory
- **No telemetry**: Zero external data transmission
- **Encrypted output**: Scan results encrypted with AGE encryption
- **Key management**: Users control their own encryption keys

### What's Stored Locally
- `data/db/`: CVE metadata and CPE mappings
- `data/cache/`: Temporary resolver cache
- `data/unknown_apps.log`: Unmapped applications (for alias building)

### What's NOT Stored
- Application contents or binaries
- Personal files or documents
- Network traffic or external connections
- User behavior or analytics

---

## 🗄️ Database Information

### CVE Database
- **Source**: NVD (National Vulnerability Database) feeds
- **Coverage**: 5+ years of historical vulnerability data
- **Format**: JSON with CVSS scores, severity labels, KEV status, EPSS scores
- **Size**: ~60MB compressed, ~200MB uncompressed

### Database Files
- `data/db/cve_meta.json`: CVE metadata and severity information
- `data/db/cpe_to_cves.json`: CPE to CVE mappings
- `data/db/affects.json`: Vendor/product version range rules

### Optional Database Tarball
For offline installations or air-gapped systems:
- **URL**: [Database tarball link]
- **SHA256**: [Tarball checksum]
- **Contents**: Complete CVE database snapshot
- **Update frequency**: Weekly

---

## 🧪 Testing & Validation

### Test Suite
```bash
# Run all tests
python3 -m pytest -v

# Test policy engine
python3 -m pytest tests/test_policy.py -v

# Security linting
bandit -r src/
```

### Validation Checks
- ✅ Policy engine determinism
- ✅ CVE sorting (severity + CVSS + KEV)
- ✅ Action generation
- ✅ HTML report generation
- ✅ AGE encryption/decryption

---

## 🔧 Troubleshooting

### Common Issues
1. **AGE encryption fails**: Verify recipient key format and permissions
2. **No vulnerabilities found**: Check database freshness with `make db-sync`
3. **Policy too restrictive**: Adjust `min_severity` in `config/policy.yml`
4. **Missing actions**: Ensure `src/core/actions.py` is present

### Debug Mode
```bash
# Enable debug output
export QP_DEBUG=1
python3 qp_cli.py scan -o data --age-recipient "$AGE_RECIPIENT"
```

---

## 📋 Migration from v1.x

### Breaking Changes
- **New policy system**: Replaces hardcoded filtering
- **AGE encryption**: Replaces legacy encryption
- **Action engine**: New remediation suggestions
- **HTML reports**: Enhanced reporting format

### Migration Steps
1. Backup existing `data/` directory
2. Update to new policy configuration
3. Set AGE encryption keys
4. Re-run database sync
5. Test new scan/report workflow

---

## 🤝 Contributing

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run linting and tests
make verify

# Submit pull request with tests
```

### Code Standards
- Type hints required
- Comprehensive test coverage
- Security-first approach
- No external dependencies without justification

---

## 📄 License & Support

**License**: [License information]  
**Support**: [Support channels]  
**Documentation**: [Documentation links]  
**Security**: [Security contact]

---

*For detailed technical documentation, see `README.md` and inline code comments.*

