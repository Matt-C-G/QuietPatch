from src.core.scanner_windows import _scan_wmic, _scan_appx, _scan_winget

def test_scan_wmic_parsing():
    """Test that WMIC parsing function exists and can be called."""
    # Just test that the function exists and is callable
    assert callable(_scan_wmic)
    result = _scan_wmic()
    # On non-Windows systems, this will return empty list, which is expected
    assert isinstance(result, list)

def test_scan_appx_parsing():
    """Test that AppX parsing function exists and can be called."""
    # Just test that the function exists and is callable
    assert callable(_scan_appx)
    result = _scan_appx()
    # On non-Windows systems, this will return empty list, which is expected
    assert isinstance(result, list)

def test_scan_winget_parsing():
    """Test that winget parsing function exists and can be called."""
    # Just test that the function exists and is callable
    assert callable(_scan_winget)
    result = _scan_winget()
    # On non-Windows systems, this will return empty list, which is expected
    assert isinstance(result, list)

def test_collect_installed_apps():
    """Test the main collection function."""
    from src.core.scanner_windows import collect_installed_apps
    assert callable(collect_installed_apps)
    result = collect_installed_apps()
    assert isinstance(result, list)
