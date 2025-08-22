from src.core.scanner_linux import _scan_dpkg, _scan_rpm, _scan_usr_bin

def test_scan_dpkg_parsing():
    """Test that dpkg parsing function exists and can be called."""
    # Just test that the function exists and is callable
    assert callable(_scan_dpkg)
    result = _scan_dpkg()
    # On non-Linux systems, this will return empty list, which is expected
    assert isinstance(result, list)

def test_scan_rpm_parsing():
    """Test that rpm parsing function exists and can be called."""
    # Just test that the function exists and is callable
    assert callable(_scan_rpm)
    result = _scan_rpm()
    # On non-Linux systems, this will return empty list, which is expected
    assert isinstance(result, list)

def test_usr_bin_scan():
    """Test that usr_bin scanning function exists and can be called."""
    # Just test that the function exists and is callable
    assert callable(_scan_usr_bin)
    result = _scan_usr_bin()
    # On non-Linux systems, this will return empty list, which is expected
    assert isinstance(result, list)

def test_collect_installed_apps():
    """Test the main collection function."""
    from src.core.scanner_linux import collect_installed_apps
    assert callable(collect_installed_apps)
    result = collect_installed_apps()
    assert isinstance(result, list)
