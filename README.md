# QuietPatch 🔐

**QuietPatch** is a lightweight, cross-platform security awareness tool that passively monitors your system for vulnerable applications and services. It maps running applications to real-time known vulnerabilities using NVD CVE data—securely and without privilege escalation.

---

## ✨ Features

- ✅ Passive vulnerability scanning — no auto-patching or intrusive edits
- 🔐 Secure encrypted configuration (uses system key vault)
- 🧠 Real-time CVE mapping using [NVD API](https://nvd.nist.gov/)
- 💻 Cross-platform (Windows, macOS, Linux)
- 🔔 Optional notifications (planned in notifier module)

---

## 🔧 Installation

```bash
git clone https://github.com/yourname/QuietPatch.git
cd QuietPatch
pip install -r requirements.txt
```

---

## 🔐 API Key Setup

QuietPatch uses the National Vulnerability Database (NVD) API to retrieve vulnerability data for applications.

### 1️⃣ Get Your Free API Key

Visit [NVD Developer Portal](https://nvd.nist.gov/developers/request-an-api-key) and request an API key (it’s instant and free).

### 2️⃣ Create `settings.json`

Inside `src/config/`, create a file named `settings.json`:

```json
{
  "nvd_api_key": "YOUR_API_KEY_HERE"
}
```

### 3️⃣ Encrypt the Configuration

Run this one-liner to encrypt your key for secure use:

```bash
python3 -c 'from src.config.encryptor import encrypt_file; encrypt_file("src/config/settings.json", "src/config/settings.json.enc")'
```

Then **delete the plaintext version**:

```bash
rm src/config/settings.json
```

Now QuietPatch will automatically load and decrypt your API key when scanning.

---

## 🚀 Usage

To scan your system (macOS by default):

```bash
python src/core/cve_mapper.py
```

🛡️ The app list is scanned, correlated to known CVEs, and results are encrypted to `data/vuln_log.json.enc`.

---

## 📂 Project Structure

```
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
```

---

## 📜 License

MIT License — see `LICENSE` file.

---

## ✅ Requirements

```
keyring
requests
cryptography
pywin32 ; platform_system == "Windows"
PyQt5    # Optional GUI
```

---

## 🙏 Acknowledgments

- [NIST NVD API](https://nvd.nist.gov/)
- [CISA KEV Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
