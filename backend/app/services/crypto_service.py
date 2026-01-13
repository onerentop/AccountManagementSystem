"""Cryptographic utilities for password hashing and data encryption."""
import os
import secrets
from typing import Tuple

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CryptoService:
    """Service for cryptographic operations."""

    def __init__(self):
        self._hasher = PasswordHasher(
            time_cost=3,
            memory_cost=65536,  # 64MB
            parallelism=4,
            hash_len=32,
            salt_len=16,
            type=Type.ID,  # Argon2id
        )
        self._encryption_key: bytes | None = None

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2id."""
        return self._hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            self._hasher.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    def needs_rehash(self, password_hash: str) -> bool:
        """Check if the password hash needs to be rehashed."""
        return self._hasher.check_needs_rehash(password_hash)

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive an encryption key from password and salt."""
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
        return kdf.derive(password.encode())

    def generate_salt(self) -> bytes:
        """Generate a random salt for key derivation."""
        return os.urandom(16)

    def set_encryption_key(self, key: bytes) -> None:
        """Set the encryption key for data encryption/decryption."""
        if len(key) != 32:
            raise ValueError("Encryption key must be 32 bytes")
        self._encryption_key = key

    def clear_encryption_key(self) -> None:
        """Clear the encryption key from memory."""
        self._encryption_key = None

    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt plaintext using AES-256-GCM."""
        if not self._encryption_key:
            raise ValueError("Encryption key not set")
        if not plaintext:
            return b""

        aesgcm = AESGCM(self._encryption_key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return nonce + ciphertext

    def decrypt(self, encrypted: bytes) -> str:
        """Decrypt ciphertext using AES-256-GCM."""
        if not self._encryption_key:
            raise ValueError("Encryption key not set")
        if not encrypted:
            return ""

        aesgcm = AESGCM(self._encryption_key)
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    def generate_token(self, length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)


# Singleton instance
crypto_service = CryptoService()
