#!/bin/bash
# Demo script for QuietPatch Canary + Rollback system
# Demonstrates cross-platform deployment with sample artifacts

set -euo pipefail

echo "🚀 QuietPatch Canary + Rollback Demo"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "canary-rollback/sample-bundle/manifest.json" ]; then
    echo "❌ Error: Run this script from the QuietPatch root directory"
    echo "   Expected: canary-rollback/sample-bundle/manifest.json"
    exit 1
fi

cd canary-rollback/sample-bundle

echo "📦 Building bundle with SHA256 hashes..."
python3 build-hashes.py

echo ""
echo "🔍 Testing detection scripts..."

# Test detection (should show current state)
echo "Windows detection:"
if [ -f "../scripts/win/detect.ps1" ]; then
    powershell.exe -ExecutionPolicy Bypass -File "../scripts/win/detect.ps1" 2>/dev/null || echo "  (Windows detection script available)"
else
    echo "  Windows detection script not found"
fi

echo "macOS detection:"
if [ -f "../scripts/mac/detect.sh" ]; then
    bash "../scripts/mac/detect.sh" 2>/dev/null || echo "  (macOS detection script available)"
else
    echo "  macOS detection script not found"
fi

echo "Linux detection:"
if [ -f "../scripts/linux/detect.sh" ]; then
    bash "../scripts/linux/detect.sh" 2>/dev/null || echo "  (Linux detection script available)"
else
    echo "  Linux detection script not found"
fi

echo ""
echo "📋 Bundle contents:"
echo "  Manifest: manifest.json"
echo "  Artifacts: artifacts/"
echo "  Scripts: ../scripts/"
echo ""
echo "🎯 Ready for deployment! Use your orchestration tool:"
echo ""
echo "Ansible:"
echo "  ansible-playbook -i inventory ../examples/deploy_canary_waves.yml"
echo ""
echo "Intune:"
echo "  Package as Win32 app with detection script"
echo ""
echo "SCCM:"
echo "  Create Application with detection method"
echo ""
echo "Jamf:"
echo "  Create Policy with Extension Attribute"
echo ""
echo "✅ Demo complete!"
