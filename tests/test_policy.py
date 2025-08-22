"""Test policy engine functionality."""
import pytest
from src.core.policy import load_policy, apply_policy, Policy, _SEV_RANK

def test_severity_rollup_honors_treat_unknown_as():
    """Test that severity rollup honors treat_unknown_as policy setting."""
    # Mock policy with treat_unknown_as: low
    policy = Policy(
        allow=[],
        deny=[],
        min_severity="low",
        treat_unknown_as="low",
        only_with_cves=False,
        limit_per_app=50
    )
    
    # Test data with unknown severity CVEs
    test_data = [
        {
            "app": "TestApp1",
            "version": "1.0",
            "cves": [
                {"severity": "unknown", "cvss": 7.5},
                {"severity": "low", "cvss": 3.0}
            ]
        },
        {
            "app": "TestApp2", 
            "version": "2.0",
            "cves": [
                {"severity": "unknown", "cvss": 9.0},
                {"severity": "unknown", "cvss": 2.0}
            ]
        }
    ]
    
    # Apply policy filtering
    filtered = apply_policy(test_data, policy)
    
    # Should include apps with unknown severity treated as low
    assert len(filtered) == 2
    # TestApp2 should be first (higher severity: 9.0 -> high = 4, vs TestApp1: low = 2)
    assert filtered[0]["app"] == "TestApp2"  # Higher severity (9.0 -> high)
    assert filtered[1]["app"] == "TestApp1"  # Lower severity

def test_min_severity_filtering():
    """Test that min_severity properly filters results."""
    policy = Policy(
        allow=[],
        deny=[],
        min_severity="medium",
        treat_unknown_as="low",
        only_with_cves=False,
        limit_per_app=50
    )
    
    test_data = [
        {"app": "LowApp", "cves": [{"severity": "low"}]},
        {"app": "MedApp", "cves": [{"severity": "medium"}]},
        {"app": "HighApp", "cves": [{"severity": "high"}]},
        {"app": "UnknownApp", "cves": [{"severity": "unknown"}]}
    ]
    
    filtered = apply_policy(test_data, policy)
    
    # Should only include medium+ severity (unknown treated as low, so excluded)
    assert len(filtered) == 2
    assert "MedApp" in [f["app"] for f in filtered]
    assert "HighApp" in [f["app"] for f in filtered]
    assert "LowApp" not in [f["app"] for f in filtered]
    assert "UnknownApp" not in [f["app"] for f in filtered]

def test_severity_value_mapping():
    """Test severity value mapping with treat_unknown_as."""
    from src.core.policy import _sev_to_int
    
    # Test unknown severity with different treat_unknown_as values
    assert _sev_to_int("unknown", "low") == _SEV_RANK["low"]
    assert _sev_to_int("unknown", "medium") == _SEV_RANK["medium"]
    assert _sev_to_int("unknown", "high") == _SEV_RANK["high"]
    assert _sev_to_int("unknown", "critical") == _SEV_RANK["critical"]
    
    # Test known severities
    assert _sev_to_int("low", "low") == _SEV_RANK["low"]
    assert _sev_to_int("high", "low") == _SEV_RANK["high"]
    assert _sev_to_int("critical", "low") == _SEV_RANK["critical"]

def test_cve_sorting_and_kev_promotion():
    """Test that CVEs are sorted by (sev desc, cvss desc, id asc) and KEV promotes display."""
    policy = Policy(
        allow=[],
        deny=[],
        min_severity="low",
        treat_unknown_as="low",
        only_with_cves=False,
        limit_per_app=10
    )
    
    # Test data with CVEs that should test the sorting logic
    test_data = [
        {
            "app": "TestApp",
            "version": "1.0",
            "cves": [
                {"id": "CVE-2023-1001", "severity": "low", "cvss": 3.0, "kev": False, "epss": 0.1},
                {"id": "CVE-2023-1002", "severity": "high", "cvss": 8.0, "kev": False, "epss": 0.2},
                {"id": "CVE-2023-1003", "severity": "medium", "cvss": 5.0, "kev": True, "epss": 0.3},
                {"id": "CVE-2023-1004", "severity": "high", "cvss": 7.5, "kev": False, "epss": 0.4},
                {"id": "CVE-2023-1005", "severity": "critical", "cvss": 9.0, "kev": False, "epss": 0.5},
                {"id": "CVE-2023-1006", "severity": "high", "cvss": 8.0, "kev": True, "epss": 0.6},
            ]
        }
    ]
    
    # Apply policy
    filtered = apply_policy(test_data, policy)
    
    # Should have one app with sorted CVEs
    assert len(filtered) == 1
    app = filtered[0]
    cves = app["cves"]
    
    # Verify CVEs are sorted by (severity desc, cvss desc, id asc)
    # Expected order based on policy sorting:
    # 1. CVE-2023-1005: critical (5), cvss 9.0, id "CVE-2023-1005"
    # 2. CVE-2023-1006: high (4), cvss 8.0, id "CVE-2023-1006" (KEV)
    # 3. CVE-2023-1002: high (4), cvss 8.0, id "CVE-2023-1002"
    # 4. CVE-2023-1004: high (4), cvss 7.5, id "CVE-2023-1004"
    # 5. CVE-2023-1003: medium (3), cvss 5.0, id "CVE-2023-1003" (KEV)
    # 6. CVE-2023-1001: low (2), cvss 3.0, id "CVE-2023-1001"
    
    assert cves[0]["id"] == "CVE-2023-1005"  # critical, highest cvss
    assert cves[1]["id"] == "CVE-2023-1006"  # high, cvss 8.0, KEV
    assert cves[2]["id"] == "CVE-2023-1002"  # high, cvss 8.0
    assert cves[3]["id"] == "CVE-2023-1004"  # high, cvss 7.5
    assert cves[4]["id"] == "CVE-2023-1003"  # medium, KEV
    assert cves[5]["id"] == "CVE-2023-1001"  # low
    
    # Verify KEV CVEs are present and properly positioned
    kev_cves = [c for c in cves if c.get("kev")]
    assert len(kev_cves) == 2
    assert "CVE-2023-1006" in [c["id"] for c in kev_cves]
    assert "CVE-2023-1003" in [c["id"] for c in kev_cves]
    
    # Verify severity ordering is maintained
    severities = [c.get("severity") for c in cves]
    assert severities == ["critical", "high", "high", "high", "medium", "low"]
