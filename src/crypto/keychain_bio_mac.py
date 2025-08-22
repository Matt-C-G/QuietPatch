from __future__ import annotations
import secrets
from Foundation import NSData
import Security

SERVICE = "quietpatch"
ACCOUNT = "kek"

def _nsdata(b: bytes):
    return NSData.dataWithBytes_length_(b, len(b))

def _bytes(nsdata):
    # PyObjC bridges CFData/NSData to a bytes-like; this works across macOS versions
    try:
        return bytes(nsdata)
    except Exception:
        return bytes(memoryview(nsdata))

class BiometricKeychain:
    name = "biometric"

    def _access_control(self):
        flags = (Security.kSecAccessControlBiometryCurrentSet |
                 Security.kSecAccessControlUserPresence)
        sac, err = Security.SecAccessControlCreateWithFlags(
            None,
            Security.kSecAttrAccessibleWhenUnlocked,
            flags,
            None
        )
        if err is not None or sac is None:
            raise RuntimeError(f"SecAccessControlCreateWithFlags failed: {err}")
        return sac

    def get_or_create_kek(self) -> bytes:
        # Try read (prompts Touch ID/Watch)
        query = {
            Security.kSecClass: Security.kSecClassGenericPassword,
            Security.kSecAttrService: SERVICE,
            Security.kSecAttrAccount: ACCOUNT,
            Security.kSecReturnData: True,
            Security.kSecUseOperationPrompt: "Unlock QuietPatch key",
        }
        status, result = Security.SecItemCopyMatching(query, None)
        if status == Security.errSecSuccess and result is not None:
            return _bytes(result)

        # Remove any broken record
        Security.SecItemDelete({
            Security.kSecClass: Security.kSecClassGenericPassword,
            Security.kSecAttrService: SERVICE,
            Security.kSecAttrAccount: ACCOUNT
        })

        # Create new key—use access control ONLY (no kSecAttrAccessible alongside it)
        kek = secrets.token_bytes(32)
        sac = self._access_control()
        add_query = {
            Security.kSecClass: Security.kSecClassGenericPassword,
            Security.kSecAttrService: SERVICE,
            Security.kSecAttrAccount: ACCOUNT,
            Security.kSecValueData: _nsdata(kek),
            Security.kSecAttrAccessControl: sac,
        }
        status = Security.SecItemAdd(add_query, None)
        if status != Security.errSecSuccess:
            raise RuntimeError(f"Keychain add failed: {status}")
        return kek

    def label(self) -> str:
        return "macOS Keychain (biometric)"
