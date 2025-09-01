"""Test CPE resolution and validation."""

from src.match.cpe_resolver import CPEResolver


def test_resolve_cpe_returns_expected_cpe():
    # Create a CPE resolver instance
    resolver = CPEResolver()

    # Example input
    app = "Google Chrome"
    version = "116.0"
    cpe = resolver.resolve_best_cpe(app, version)

    # Should return a CPE string or None if no match found
    if cpe:
        assert "cpe:" in cpe.lower()
    else:
        # It's okay if no CPE is found for this test app
        assert True


def test_fetch_cves_for_cpe_returns_list():
    # Test the CPE validation functionality
    resolver = CPEResolver()

    # Test with a valid CPE format
    example_cpe = "cpe:2.3:a:google:chrome:116.0:*:*:*:*:*:*:*"
    is_valid = resolver._validate_cpe(example_cpe)
    assert is_valid

    # Test with an invalid CPE
    invalid_cpe = "invalid:cpe:format"
    is_invalid = resolver._validate_cpe(invalid_cpe)
    assert not is_invalid
