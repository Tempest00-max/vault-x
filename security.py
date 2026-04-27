import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_key(password: str):
    # Fixed salt for consistent key derivation across sessions
    salt = b'vault_x2_production_salt_2026' 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key)

def encrypt_file_data(data: bytes, password: str) -> bytes:
    """Encrypts raw binary data (images, videos, docs)."""
    f = get_key(password)
    return f.encrypt(data)

def decrypt_file_data(data: bytes, password: str) -> bytes:
    """Decrypts raw binary data back to its original state."""
    f = get_key(password)
    return f.decrypt(data)