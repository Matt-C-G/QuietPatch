QuietPatch/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── scanner.py
│   │   ├── cve_mapper.py
│   │   └── notifier.py
│   ├── ui/
│   │   └── dashboard.py
│   └── config/
│       ├── encryptor.py
│       └── settings.json.enc
├── data/
│   ├── cve_cache.json
│   └── known_apps.json
├── scripts/
│   └── setup_admin_scan.py
├── tests/
│   └── test_scanner.py

# README.md

# QuietPatch 

**QuietPatch** is a lightweight, cross-platform security awareness tool that passively monitors your system for vulnerable applications and services. It scans your environment with minimal privileges and uses an encrypted configuration to protect its scan profile.

---

### 👋 Note to Recruiters & Employers

QuietPatch is a passive vulnerability scanner that maps system applications to known Common Vulnerabilities and Exposures (CVEs). The core scanning, encryption, and alert logic are fully implemented. A graphical interface (GUI) is currently in development, but is not required for core functionality.

Additionally, I’m exploring API integration workarounds to ensure users can run QuietPatch out of the box, without needing to obtain or manually apply their own API keys. Until then, this is the "lite" version.

If you’d like a walkthrough or have any feedback, please don’t hesitate to reach out.  
— MCG


## ✨ Features
- Passive vulnerability monitoring
- OS key vault encryption for configuration
- No auto-patching: provides secure, trusted vendor links
- Cross-platform: Windows, macOS, Linux
- Real-time notifications for known CVEs (NVD, CISA KEV)

## 🔧 Installation
```bash
git clone https://github.com/yourname/QuietPatch.git
cd QuietPatch
pip install -r requirements.txt
```

## 📜 License
MIT License. See LICENSE file for details.
📌 This project and its core concept are the intellectual property of Matthew Graham. Sharing access is intended for evaluation only. Any commercial use, replication, or derivative work requires written permission.

# requirements.txt
keyring
requests
cryptography
pywin32; platform_system == "Windows"
PyQt5  # Optional GUI

# .gitignore
__pycache__/
*.pyc
.env
*.log
settings.json.enc
*.sqlite3
.vscode/
.idea/
build/
dist/
