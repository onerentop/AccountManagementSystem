"""Tests for crypto service."""
import pytest

from app.services.crypto_service import CryptoService


class TestCryptoServicePasswordHashing:
    """Test cases for password hashing."""

    def test_hash_password(self):
        """Test password hashing produces hash."""
        crypto = CryptoService()
        password = "TestPassword123!"

        hash_result = crypto.hash_password(password)

        assert hash_result is not None
        assert hash_result != password
        assert len(hash_result) > 0

    def test_hash_password_different_each_time(self):
        """Test password hashing produces different hashes."""
        crypto = CryptoService()
        password = "TestPassword123!"

        hash1 = crypto.hash_password(password)
        hash2 = crypto.hash_password(password)

        # Argon2 uses random salt, so hashes should differ
        assert hash1 != hash2

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        crypto = CryptoService()
        password = "TestPassword123!"

        hash_result = crypto.hash_password(password)

        assert crypto.verify_password(password, hash_result) is True

    def test_verify_password_failure(self):
        """Test password verification with wrong password."""
        crypto = CryptoService()

        hash_result = crypto.hash_password("CorrectPassword!")

        assert crypto.verify_password("WrongPassword!", hash_result) is False


class TestCryptoServiceSalt:
    """Test cases for salt generation."""

    def test_generate_salt(self):
        """Test salt generation."""
        crypto = CryptoService()

        salt = crypto.generate_salt()

        assert salt is not None
        assert len(salt) == 16  # Default salt length

    def test_generate_salt_unique(self):
        """Test salt generation produces unique values."""
        crypto = CryptoService()

        salt1 = crypto.generate_salt()
        salt2 = crypto.generate_salt()

        assert salt1 != salt2


class TestCryptoServiceKeyDerivation:
    """Test cases for key derivation."""

    def test_derive_key(self):
        """Test key derivation from password and salt."""
        crypto = CryptoService()
        password = "TestPassword123!"
        salt = crypto.generate_salt()

        key = crypto.derive_key(password, salt)

        assert key is not None
        assert len(key) == 32  # 256-bit key

    def test_derive_key_deterministic(self):
        """Test key derivation is deterministic."""
        crypto = CryptoService()
        password = "TestPassword123!"
        salt = crypto.generate_salt()

        key1 = crypto.derive_key(password, salt)
        key2 = crypto.derive_key(password, salt)

        assert key1 == key2

    def test_derive_key_different_salt(self):
        """Test key derivation with different salt produces different keys."""
        crypto = CryptoService()
        password = "TestPassword123!"

        salt1 = crypto.generate_salt()
        salt2 = crypto.generate_salt()

        key1 = crypto.derive_key(password, salt1)
        key2 = crypto.derive_key(password, salt2)

        assert key1 != key2


class TestCryptoServiceEncryption:
    """Test cases for encryption/decryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption roundtrip."""
        crypto = CryptoService()
        password = "TestPassword123!"
        salt = crypto.generate_salt()
        key = crypto.derive_key(password, salt)
        crypto.set_encryption_key(key)

        plaintext = "Secret message to encrypt"

        encrypted = crypto.encrypt(plaintext)
        decrypted = crypto.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_produces_bytes(self):
        """Test encryption produces bytes."""
        crypto = CryptoService()
        password = "TestPassword123!"
        salt = crypto.generate_salt()
        key = crypto.derive_key(password, salt)
        crypto.set_encryption_key(key)

        encrypted = crypto.encrypt("Test message")

        assert isinstance(encrypted, bytes)
        assert len(encrypted) > 0

    def test_encrypt_different_each_time(self):
        """Test encryption produces different ciphertext each time."""
        crypto = CryptoService()
        password = "TestPassword123!"
        salt = crypto.generate_salt()
        key = crypto.derive_key(password, salt)
        crypto.set_encryption_key(key)

        plaintext = "Same message"

        encrypted1 = crypto.encrypt(plaintext)
        encrypted2 = crypto.encrypt(plaintext)

        # Due to random IV, ciphertext should differ
        assert encrypted1 != encrypted2

    def test_decrypt_requires_key(self):
        """Test decryption fails without key."""
        crypto = CryptoService()
        password = "TestPassword123!"
        salt = crypto.generate_salt()
        key = crypto.derive_key(password, salt)
        crypto.set_encryption_key(key)

        encrypted = crypto.encrypt("Test message")

        # Clear key
        crypto.clear_encryption_key()

        with pytest.raises(ValueError):
            crypto.decrypt(encrypted)


class TestCryptoServiceKeyManagement:
    """Test cases for encryption key management."""

    def test_set_encryption_key(self):
        """Test setting encryption key."""
        crypto = CryptoService()
        key = b"0" * 32  # 256-bit key

        crypto.set_encryption_key(key)

        assert crypto._encryption_key == key

    def test_clear_encryption_key(self):
        """Test clearing encryption key."""
        crypto = CryptoService()
        key = b"0" * 32
        crypto.set_encryption_key(key)

        crypto.clear_encryption_key()

        assert crypto._encryption_key is None

    def test_encrypt_without_key_raises(self):
        """Test encryption without key raises ValueError."""
        crypto = CryptoService()
        crypto.clear_encryption_key()

        with pytest.raises(ValueError) as exc_info:
            crypto.encrypt("Test")

        assert "not set" in str(exc_info.value).lower() or "locked" in str(exc_info.value).lower()
