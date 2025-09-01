"""Test HTML report generation."""

import json
import tempfile
from pathlib import Path

from quietpatch.report.html import _action_cell, _first_cve, generate_report


def test_html_contains_action_cell():
    """Test that HTML contains Action cell and non-empty for known apps."""
    # Create test data with actions
    test_data = [
        {
            "app": "TestApp",
            "version": "1.0",
            "actions": [
                {"type": "upgrade", "cmd": "brew upgrade testapp", "note": "Requires Homebrew"}
            ],
            "cves": [{"id": "CVE-2023-1234", "severity": "medium"}],
        }
    ]

    # Write test data to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_data, f)
        input_path = f.name

    try:
        # Generate HTML report
        output_path = input_path.replace(".json", ".html")
        generate_report(input_path, output_path)

        # Read generated HTML
        with open(output_path) as f:
            html_content = f.read()

        # Verify action cell exists and contains expected content
        assert "Action" in html_content
        assert "brew upgrade testapp" in html_content
        assert "Requires Homebrew" in html_content
        assert "copy-btn" in html_content  # Copy button should be present

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_action_cell_generation():
    """Test _action_cell function generates proper HTML."""
    # Test with command
    rec_with_cmd = {"actions": [{"cmd": "test command", "note": "test note"}]}
    cell_html = _action_cell(rec_with_cmd)

    assert "test command" in cell_html
    assert "test note" in cell_html
    assert "copy-btn" in cell_html
    assert "onclick=" in cell_html

    # Test with URL
    rec_with_url = {"actions": [{"url": "https://example.com", "note": "test url"}]}
    cell_html = _action_cell(rec_with_url)

    assert "https://example.com" in cell_html
    assert "href=" in cell_html
    assert 'target="_blank"' in cell_html

    # Test with no actions
    rec_no_actions = {"actions": []}
    cell_html = _action_cell(rec_no_actions)

    assert "—" in cell_html


def test_first_cve_extraction():
    """Test _first_cve function extracts CVE data correctly."""
    rec = {
        "cves": [{"id": "CVE-2023-1234", "cvss": 7.5, "severity": "high", "summary": "Test CVE"}]
    }

    cve_id, cvss, sev, summary = _first_cve(rec)

    assert cve_id == "CVE-2023-1234"
    assert cvss == "7.5"
    assert sev == "high"
    assert summary == "Test CVE"

    # Test with no CVEs
    rec_no_cves = {"cves": []}
    cve_id, cvss, sev, summary = _first_cve(rec_no_cves)

    assert cve_id == ""
    assert cvss == ""
    assert sev == ""
    assert summary == ""
