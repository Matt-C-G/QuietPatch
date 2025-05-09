from src.config.encryptor import decrypt_file

data = decrypt_file("data/vuln_log.json.enc")
for entry in data:
    print(f"⚠️ {entry['app']} {entry['version']} → {entry['vulnerability']}")
