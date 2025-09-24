# Endpoint Proof Pack

**What this proves** — Sensor health ≥98% (7-day), ASR FP <1/100 devices, BitLocker On with escrow present, recovery drill passed.

**Quick Start**
1) Run scripts: `.\scripts\check_sensor.ps1 -Simulate` and `.\scripts\check_bitlocker.ps1 -Simulate`
2) Review SOPs in `sops/` for operational procedures
3) Check evidence screenshots in `evidence/` for portal views
4) Export one-pager from `onepager/` for executive summary

## 🔗 Quick Links
- **[Scripts](scripts/)** — PowerShell automation for sensor and BitLocker checks
- **[SOPs](sops/)** — 3 one-page standard operating procedures
- **[Evidence](evidence/)** — Redacted portal screenshots
- **[JSON Artifacts](examples/sample_outputs/)** — Generated data for tickets
- **[One-pager](onepager/)** — Executive summary documentation
- **[Live Demo](https://matt-c-g.github.io/endpoint-labs/)** — GitHub Pages portfolio

## 📁 What's Inside
- `scripts/` — PowerShell checks (sensor + BitLocker) with exit codes and hash artifacts
- `sops/` — three 1-page SOPs (Defender, ASR, BitLocker)
- `examples/sample_outputs/` — JSON outputs from scripts
- `evidence/` — redacted screenshots (Defender portal, ASR hits, BitLocker recovery)
- `onepager/` — recruiter-friendly summary

## 🎯 Key Metrics Achieved
- **Sensor Health:** ≥98% (7-day average)
- **ASR False Positives:** <1/100 devices
- **BitLocker Coverage:** 80-90% of pilot group
- **Recovery Drill:** PASSED with key rotation

## 🧪 Quick Test
```powershell
pwsh
cd endpoint-labs
.\scripts\check_sensor.ps1 -Simulate
.\scripts\check_bitlocker.ps1 -Simulate
```

Artifacts land in `examples/sample_outputs/` (attach to tickets).

## 📄 License
MIT License - see [LICENSE](LICENSE) file for details.