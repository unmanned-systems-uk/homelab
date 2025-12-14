"""
Fernet-based credential encryption for HomeLab Infrastructure Database.
SECURITY CRITICAL - Handle with care.
"""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CredentialEncryption:
    """Manages encryption/decryption of credentials using Fernet."""

    KEY_FILE = Path.home() / '.homelab' / '.db_key'

    def __init__(self, key: bytes = None):
        """Initialize encryption with provided key or load from secure storage."""
        if key:
            self._fernet = Fernet(key)
        else:
            self._fernet = Fernet(self._load_or_create_key())

    def _load_or_create_key(self) -> bytes:
        """Load existing key or create new one securely."""
        # Check environment variable first
        env_key = os.environ.get('HOMELAB_DB_KEY')
        if env_key:
            return env_key.encode() if isinstance(env_key, str) else env_key

        # Check key file
        if self.KEY_FILE.exists():
            return self.KEY_FILE.read_bytes()

        # Generate new key
        key = Fernet.generate_key()
        self._save_key(key)
        return key

    def _save_key(self, key: bytes) -> None:
        """Save key to secure file with restricted permissions."""
        self.KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.KEY_FILE.write_bytes(key)
        os.chmod(self.KEY_FILE, 0o600)
        os.chmod(self.KEY_FILE.parent, 0o700)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64-encoded ciphertext."""
        if not plaintext:
            return None
        encrypted = self._fernet.encrypt(plaintext.encode())
        return encrypted.decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt base64-encoded ciphertext and return plaintext."""
        if not ciphertext:
            return None
        decrypted = self._fernet.decrypt(ciphertext.encode())
        return decrypted.decode('utf-8')

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new Fernet key."""
        return Fernet.generate_key()

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """Derive a Fernet key from a password using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
