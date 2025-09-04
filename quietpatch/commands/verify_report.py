"""Report verification utilities"""

import hashlib
import re
from pathlib import Path


def verify_report(report_path: str) -> tuple[bool, str]:
    """
    Verify a QuietPatch HTML report for integrity.
    
    Args:
        report_path: Path to the HTML report file
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        report_file = Path(report_path)
        if not report_file.exists():
            return False, f"Report file not found: {report_path}"
        
        content = report_file.read_text(encoding='utf-8')
        
        # Extract hash from footer
        hash_match = re.search(r'Report-Hash: SHA256-([a-f0-9]+)', content)
        if not hash_match:
            return False, "No hash found in report footer"
        
        reported_hash = hash_match.group(1)
        
        # Compute actual hash
        actual_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        
        if reported_hash == actual_hash:
            return True, f"Report integrity verified (SHA256-{actual_hash})"
        else:
            return False, f"Hash mismatch: reported {reported_hash}, actual {actual_hash}"
            
    except Exception as e:
        return False, f"Verification failed: {e}"


def run(report_path: str) -> int:
    """CLI entry point for report verification."""
    is_valid, message = verify_report(report_path)
    
    if is_valid:
        print(f"✅ {message}")
        return 0
    else:
        print(f"❌ {message}")
        return 1
