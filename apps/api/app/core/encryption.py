"""
AES-256 Symmetric Field-Level Encryption & Decryption Module.

Provides authenticated symmetric encryption (Fernet / AES-128-CBC + HMAC-SHA256) 
for sensitive candidate PII, resume text, and private evaluation fields.
"""

import base64
import hashlib
import logging
from typing import Optional
from cryptography.fernet import Fernet
from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_fernet_instance() -> Fernet:
    """Derive a valid 32-byte URL-safe base64 key from configured SecretStr."""
    secret_bytes = settings.FIELD_ENCRYPTION_KEY.get_secret_value().encode("utf-8")
    key_digest = hashlib.sha256(secret_bytes).digest()
    fernet_key = base64.urlsafe_b64encode(key_digest)
    return Fernet(fernet_key)


def encrypt_field(plaintext: Optional[str]) -> Optional[str]:
    """
    Encrypts a sensitive plaintext string field into an authenticated AES ciphertext token.
    Returns None if input plaintext is None.
    """
    if plaintext is None:
        return None
    if not isinstance(plaintext, str):
        plaintext = str(plaintext)
    if not plaintext:
        return ""

    try:
        fernet = _get_fernet_instance()
        encrypted_bytes = fernet.encrypt(plaintext.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Field encryption failed: {e}", exc_info=True)
        raise ValueError("Failed to encrypt sensitive field.") from e


def decrypt_field(ciphertext: Optional[str]) -> Optional[str]:
    """
    Decrypts an authenticated AES ciphertext token back into original plaintext.
    Returns None if input ciphertext is None.
    """
    if ciphertext is None:
        return None
    if not ciphertext:
        return ""

    try:
        fernet = _get_fernet_instance()
        decrypted_bytes = fernet.decrypt(ciphertext.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Field decryption failed: {e}", exc_info=True)
        raise ValueError("Failed to decrypt sensitive field — invalid ciphertext or key mismatch.") from e
