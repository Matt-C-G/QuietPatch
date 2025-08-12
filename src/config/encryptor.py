import keyring
import os
import json
from cryptography.fernet import Fernet

SERVICE_NAME = "QuietPatch"
KEY_NAME = "scan_encryption_key"

def get_or_create_key():
    key = keyring.get_password(SERVICE_NAME, KEY_NAME)
    if key is None:
        key = Fernet.generate_key().decode()
        keyring.set_password(SERVICE_NAME, KEY_NAME, key)
    return key.encode()

def encrypt_file(input_path, output_path):
    key = get_or_create_key()
    fernet = Fernet(key)

    with open(input_path, "rb") as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)

    with open(output_path, "wb") as f:
        f.write(encrypted_data)

    print(f"🔒 Encrypted output saved to {output_path}")

def decrypt_file(encrypted_path):
    key = get_or_create_key()
    fernet = Fernet(key)

    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = fernet.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())
