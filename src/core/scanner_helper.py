import platform
from . import scanner_new as mac_scanner
from . import scanner_linux
from . import scanner_windows


def get_scanner():
    os_name = platform.system().lower()
    if os_name == "darwin":
        return mac_scanner
    if os_name == "linux":
        return scanner_linux
    if os_name == "windows":
        return scanner_windows
    raise RuntimeError(f"Unsupported OS: {os_name}")
