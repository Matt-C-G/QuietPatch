"""Diagnostics bundle generation for support"""

import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Dict, Any


def generate_diagnostics_bundle(output_path: str) -> str:
    """
    Generate a diagnostics bundle for support purposes.
    
    Args:
        output_path: Path to save the diagnostics bundle
        
    Returns:
        Path to the generated bundle
    """
    bundle_path = Path(output_path)
    if not bundle_path.suffix:
        bundle_path = bundle_path.with_suffix('.zip')
    
    # Create diagnostics data
    diagnostics: Dict[str, Any] = {
        "system": {
            "platform": sys.platform,
            "python_version": sys.version,
            "python_executable": sys.executable,
        },
        "environment": {
            "qp_offline": os.environ.get("QP_OFFLINE"),
            "qp_data_dir": os.environ.get("QP_DATA_DIR"),
            "pex_root": os.environ.get("PEX_ROOT"),
            "path": os.environ.get("PATH", "")[:500],  # Truncate long paths
        },
        "quietpatch": {
            "version": "unknown",
            "installation_path": "unknown",
        }
    }
    
    # Try to get QuietPatch version
    try:
        from quietpatch import __version__
        diagnostics["quietpatch"]["version"] = __version__
    except ImportError:
        try:
            import importlib.metadata
            diagnostics["quietpatch"]["version"] = importlib.metadata.version("quietpatch")
        except Exception:
            pass
    
    # Try to get installation path
    try:
        import quietpatch
        diagnostics["quietpatch"]["installation_path"] = str(Path(quietpatch.__file__).parent)
    except Exception:
        pass
    
    # Check for common issues
    issues = []
    
    # Check Python version
    if not (3, 11) <= sys.version_info[:2] < (3, 13):
        issues.append(f"Unsupported Python version: {sys.version_info[:2]}")
    
    # Check for Alpine/musl
    try:
        import platform
        libc = platform.libc_ver()[0]
        if libc == "musl":
            issues.append("Alpine/musl detected (not supported)")
    except Exception:
        pass
    
    # Check for PEP 668
    extern = Path(sys.base_prefix) / "lib" / f"python{sys.version_info[0]}.{sys.version_info[1]}" / "EXTERNALLY-MANAGED"
    if extern.exists():
        issues.append("PEP 668 externally managed Python detected")
    
    # Check for Windows launcher
    if sys.platform.startswith("win"):
        import shutil
        py = shutil.which("py")
        if not py:
            issues.append("Python Launcher not found on Windows")
    
    # Check for zstandard
    try:
        import zstandard
        diagnostics["dependencies"] = {"zstandard": zstandard.__version__}
    except ImportError:
        issues.append("zstandard not installed")
        diagnostics["dependencies"] = {"zstandard": "not installed"}
    
    # Check for database
    data_dir = Path(os.environ.get("QP_DATA_DIR", "data"))
    db_files = list(data_dir.glob("db-*.tar.*"))
    diagnostics["database"] = {
        "data_dir": str(data_dir),
        "files_found": [f.name for f in db_files],
        "count": len(db_files),
    }
    
    if not db_files:
        issues.append("No database files found")
    
    diagnostics["issues"] = issues
    
    # Create ZIP bundle
    with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add diagnostics JSON
        zf.writestr("diagnostics.json", json.dumps(diagnostics, indent=2))
        
        # Add environment info
        env_info = {
            "python_path": sys.executable,
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": str(Path.cwd()),
        }
        zf.writestr("environment.txt", json.dumps(env_info, indent=2))
        
        # Add recent logs if they exist
        log_files = [
            "data/vuln_log.json",
            "data/apps.json",
            "report.html",
        ]
        
        for log_file in log_files:
            if Path(log_file).exists():
                try:
                    zf.write(log_file, f"logs/{Path(log_file).name}")
                except Exception:
                    pass  # Skip files that can't be read
    
    return str(bundle_path)


def run(output_path: str = "quietpatch-diagnostics.zip") -> int:
    """CLI entry point for diagnostics bundle generation."""
    try:
        bundle_path = generate_diagnostics_bundle(output_path)
        print(f"✅ Diagnostics bundle created: {bundle_path}")
        print("📧 Attach this file to your support request")
        return 0
    except Exception as e:
        print(f"❌ Failed to create diagnostics bundle: {e}")
        return 1
