import platform

from src.core.scanner_helper import get_scanner


def test_get_scanner_mac(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    s = get_scanner()
    assert hasattr(s, "collect_installed_apps")


def test_get_scanner_linux(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    s = get_scanner()
    assert hasattr(s, "collect_installed_apps")


def test_get_scanner_windows(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    s = get_scanner()
    assert hasattr(s, "collect_installed_apps")
