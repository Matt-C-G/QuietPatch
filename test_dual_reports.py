#!/usr/bin/env python3
"""
Test script for QuietPatch dual-report system
Generates sample data and demonstrates tech/exec reports
"""

import json
import os
from pathlib import Path

def create_sample_scan():
    """Create a sample scan.json file for testing"""
    sample_data = {
        "run_id": "RUN-2025-10-01-001",
        "catalog": {
            "nvd_sha256": "abc123def456",
            "kev_sha256": "def456ghi789", 
            "epss_sha256": "ghi789jkl012",
            "signed": True
        },
        "assets": [
            {
                "asset_id": "WIN-001",
                "hostname": "web-server-01",
                "os": "Windows Server 2022",
                "bu": "Finance",
                "packages": [{"name": "7zip", "version": "22.01"}],
                "vulns": [
                    {
                        "cve": "CVE-2023-12345",
                        "severity": "critical",
                        "cvss": 9.8,
                        "kev": True,
                        "epss": 0.83,
                        "fix_available": True,
                        "package": "7zip",
                        "current_version": "22.01",
                        "fix": {
                            "target_version": "23.01",
                            "install_cmd": "msiexec /i 7zip-23.01-x64.msi /qn",
                            "verify_cmd": "7z.exe --version",
                            "rollback_cmd": "msiexec /i 7zip-22.01-x64.msi /qn"
                        }
                    }
                ]
            },
            {
                "asset_id": "MAC-002", 
                "hostname": "dev-mac-01",
                "os": "macOS 14.0",
                "bu": "Engineering",
                "packages": [{"name": "iTerm2", "version": "3.5.10"}],
                "vulns": [
                    {
                        "cve": "CVE-2024-56789",
                        "severity": "high",
                        "cvss": 7.5,
                        "kev": False,
                        "epss": 0.45,
                        "fix_available": True,
                        "package": "iTerm2",
                        "current_version": "3.5.10",
                        "fix": {
                            "target_version": "3.5.12",
                            "install_cmd": "sudo installer -pkg iterm2-3.5.12.pkg -target /",
                            "verify_cmd": "defaults read /Applications/iTerm.app/Contents/Info.plist CFBundleShortVersionString",
                            "rollback_cmd": "sudo installer -pkg iterm2-3.5.10.pkg -target /"
                        }
                    }
                ]
            }
        ]
    }
    
    with open("test-reports/scan.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    print("✅ Created sample scan.json")

def create_sample_policy():
    """Create a sample policy.json file"""
    policy_data = {
        "policy_version": "2025-09-30",
        "rules": [
            {"match": "severity>=high", "window": "sat-02:00-04:00"},
            {"match": "kev=true", "window": "any"}
        ],
        "decisions": [
            {"cve": "CVE-2023-12345", "asset_id": "WIN-001", "action": "remediate", "ring": "canary"},
            {"cve": "CVE-2024-56789", "asset_id": "MAC-002", "action": "remediate", "ring": "wave1"}
        ]
    }
    
    with open("test-reports/policy.json", "w") as f:
        json.dump(policy_data, f, indent=2)
    print("✅ Created sample policy.json")

def create_sample_approval():
    """Create a sample approval.json file"""
    approval_data = {
        "change_id": "CAB-2025-10-01-042",
        "submitted_by": "Matthew Graham",
        "submitted_at": "2025-10-01T13:05:00Z",
        "approver_1": {"name": "C. Romero", "role": "Ops Manager", "date": "2025-10-01"},
        "approver_2": {"name": "J. Patel", "role": "CISO", "date": "2025-10-01"},
        "scope": "Ring-0 canary on 25 endpoints; 7-Zip/iTerm2 point upgrades",
        "notes": "Rollback rehearsed on QA image; see bundle SHA and commands in tech report."
    }
    
    with open("test-reports/approval.json", "w") as f:
        json.dump(approval_data, f, indent=2)
    print("✅ Created sample approval.json")

def create_sample_kpi():
    """Create a sample kpi.json file"""
    kpi_data = {
        "assets_total": 1200,
        "assets_scanned": 1187,
        "exposure_index": 3.4,
        "kev_backlog": 27,
        "sla": {"critical_7d": 0.92, "high_30d": 0.88}
    }
    
    with open("test-reports/kpi.json", "w") as f:
        json.dump(kpi_data, f, indent=2)
    print("✅ Created sample kpi.json")

def main():
    print("🚀 QuietPatch Dual-Report Test Script")
    print("=" * 50)
    
    # Create test directory
    os.makedirs("test-reports", exist_ok=True)
    
    # Generate sample data
    create_sample_scan()
    create_sample_policy()
    create_sample_approval()
    create_sample_kpi()
    
    print("\n📊 Sample data created in test-reports/")
    print("\n🔧 Test commands:")
    print("\n# Technical Report:")
    print("python3 qp_cli.py report tech \\")
    print("  --scan test-reports/scan.json \\")
    print("  --policy test-reports/policy.json \\")
    print("  --out test-reports/tech-report.html \\")
    print("  --pdf test-reports/tech-report.pdf \\")
    print("  --approval test-reports/approval.json \\")
    print("  --watermark 'APPROVED • CAB-2025-10-01'")
    
    print("\n# Executive Report:")
    print("python3 qp_cli.py report exec \\")
    print("  --scan test-reports/scan.json \\")
    print("  --kpi test-reports/kpi.json \\")
    print("  --out test-reports/exec-report.pdf \\")
    print("  --html test-reports/exec-report.html \\")
    print("  --approval test-reports/approval.json \\")
    print("  --watermark 'APPROVED • CAB-2025-10-01'")
    
    print("\n# With optional signing (requires minisign):")
    print("python3 qp_cli.py report exec \\")
    print("  --scan test-reports/scan.json \\")
    print("  --out test-reports/exec-report.pdf \\")
    print("  --sign --sign-key ~/.config/quietpatch/minisign.key")
    
    print("\n✨ Ready to test the dual-report system!")

if __name__ == "__main__":
    main()
