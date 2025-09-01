QuietPatch for Windows
======================

Quick Start:
1. Double-click "run_quietpatch.bat" to run a vulnerability scan
2. The scan will run automatically and open the report in your browser
3. Review the HTML report for security findings

Requirements:
- Python 3.11 (64-bit) installed and added to PATH
- Windows 10/11 or Windows Server 2019/2022
- Administrator privileges for full system scan

Files:
- quietpatch-win-py311.pex - Main executable (Python PEX)
- run_quietpatch.bat - User-friendly launcher
- catalog/ - Vulnerability database files
- policies/ - Security policy configurations

Manual Usage:
From Command Prompt or PowerShell:
  python quietpatch-win-py311.pex scan --help
  python quietpatch-win-py311.pex scan --also-report

Environment Variables:
- PEX_ROOT=C:\pex - PEX cache directory
- TEMP=C:\t - Temporary files directory
- TMP=C:\t - Alternative temp directory

Troubleshooting:
- If you get "python not found", install Python 3.11 from python.org
- If you get path errors, run from a shorter directory path
- For permission issues, run as Administrator
- Check that antivirus isn't blocking the .pex file

For more information, see the main README.md file.
