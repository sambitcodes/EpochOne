"""
Security utilities: encryption, hashing, token handling.
"""
from cryptography.fernet import Fernet
import os
import logging

logger = logging.getLogger(__name__)

def get_cipher():
    """Get Fernet cipher for encryption."""
    # In production, load from secure key management (AWS KMS, HashiCorp Vault, etc.)
    key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    return Fernet(key.encode() if isinstance(key, str) else key)

def encrypt_token(plaintext: str) -> str:
    """Encrypt a token (e.g., refresh token)."""
    cipher = get_cipher()
    encrypted = cipher.encrypt(plaintext.encode())
    return encrypted.decode()

def decrypt_token(ciphertext: str) -> str:
    """Decrypt a token."""
    cipher = get_cipher()
    decrypted = cipher.decrypt(ciphertext.encode())
    return decrypted.decode()