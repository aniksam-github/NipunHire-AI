"""
Unit tests for AES-256 Fernet symmetric field-level encryption and decryption (encrypt_field, decrypt_field).
"""

import pytest
from app.core.encryption import encrypt_field, decrypt_field


def test_field_encryption_and_decryption_roundtrip():
    original_text = "Sensitive Candidate PII Data: Phone +1-555-0199, SSN/ID 98765"

    ciphertext = encrypt_field(original_text)
    assert ciphertext is not None
    assert ciphertext != original_text
    assert len(ciphertext) > 20

    decrypted_text = decrypt_field(ciphertext)
    assert decrypted_text == original_text


def test_field_encryption_none_and_empty_handling():
    assert encrypt_field(None) is None
    assert decrypt_field(None) is None
    assert encrypt_field("") == ""
    assert decrypt_field("") == ""


def test_field_decryption_invalid_token_error():
    invalid_token = "gAAAAABm_invalid_corrupted_token_string_sample=="
    with pytest.raises(ValueError, match="Failed to decrypt sensitive field"):
        decrypt_field(invalid_token)
