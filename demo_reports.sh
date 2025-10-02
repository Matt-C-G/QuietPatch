#!/bin/bash
# Demo script for QuietPatch dual-report system
# Generates both Technical and Executive reports with sample data

set -euo pipefail

echo "🚀 QuietPatch Dual-Report Demo"
echo "=============================="

# Ensure output directory exists
mkdir -p out

# Generate Technical Report
echo "📊 Generating Technical Report..."
python3 qp_cli.py report tech \
  --scan data/scan.json \
  --policy data/policy.json \
  --approval data/approval.json \
  --assets data/assets.json \
  --out out/tech-report.html \
  --pdf out/tech-report.pdf \
  --watermark "APPROVED • CAB-2025-10-01"

echo "✅ Technical report generated: out/tech-report.html"

# Generate Executive Report  
echo "📈 Generating Executive Report..."
python3 qp_cli.py report exec \
  --scan data/scan.json \
  --kpi data/kpi.json \
  --business-units data/business_units.json \
  --actions data/actions.json \
  --approval data/approval.json \
  --out out/exec-report.html \
  --pdf out/exec-report.pdf \
  --watermark "APPROVED • CAB-2025-10-01"

echo "✅ Executive report generated: out/exec-report.html"

# Optional: Sign reports if minisign is available
if command -v minisign >/dev/null 2>&1; then
    echo "🔐 Signing reports with minisign..."
    if [ -f ~/.config/quietpatch/minisign.key ]; then
        minisign -S -s ~/.config/quietpatch/minisign.key -m out/tech-report.html
        minisign -S -s ~/.config/quietpatch/minisign.key -m out/exec-report.html
        echo "✅ Reports signed with minisign"
    else
        echo "⚠️  Minisign key not found at ~/.config/quietpatch/minisign.key"
        echo "   Run: minisign -G -s ~/.config/quietpatch/minisign.key -p ~/.config/quietpatch/minisign.pub"
    fi
else
    echo "ℹ️  Minisign not available - skipping signing"
fi

echo ""
echo "🎉 Demo complete! Reports available in out/ directory:"
echo "   Technical: out/tech-report.html"
echo "   Executive: out/exec-report.html"
echo ""
echo "📖 Open reports in browser:"
echo "   open out/tech-report.html"
echo "   open out/exec-report.html"
