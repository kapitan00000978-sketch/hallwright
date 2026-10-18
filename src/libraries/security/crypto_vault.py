"""
Hallwright Enterprise Security: Cryptographic Vault & Secret Zeroizer.
Part of Pillar IV: Enterprise Modular Domain Libraries (Bosqich 43 & 46).

Provides:
- Pure standard-library PBKDF2-HMAC key derivation
- HMAC-SHA256 authenticated payload signing & constant-time verification
- SecretZeroizer: Memory wipe & zeroing abstraction for sensitive credentials
"""

import os
import hmac
import hashlib
import secrets
import ctypes
from typing import Tuple, Dict, Any, Optional
import json


class CryptoVault:
    """Zero-dependency cryptographic operations utility based entirely on Python hashlib & hmac."""

    @staticmethod
    def derive_key(password: str, salt: Optional[bytes] = None, iterations: int = 200_000) -> Tuple[bytes, bytes]:
        """Derives a 256-bit key from a password using PBKDF2-HMAC-SHA256."""
        used_salt = salt or secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            used_salt,
            iterations,
            dklen=32
        )
        return key, used_salt

    @staticmethod
    def sign_payload(payload: Dict[str, Any], secret_key: bytes) -> str:
        """Generates an HMAC-SHA256 signature for a JSON dictionary."""
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        sig = hmac.new(secret_key, serialized, hashlib.sha256).hexdigest()
        return sig

    @staticmethod
    def verify_payload(payload: Dict[str, Any], signature: str, secret_key: bytes) -> bool:
        """Verifies an HMAC signature using constant-time comparison to prevent timing attacks."""
        expected_sig = CryptoVault.sign_payload(payload, secret_key)
        return hmac.compare_digest(expected_sig, signature)

    @staticmethod
    def generate_secure_token(nbytes: int = 32) -> str:
        """Generates a cryptographically secure URL-safe hex token."""
        return secrets.token_hex(nbytes)


class SecretZeroizer:
    """
    Context manager that attempts to overwrite byte buffers in memory upon exit.
    Reduces the exposure window for credentials held in heap memory.
    """

    def __init__(self, secret_bytes: bytearray):
        if not isinstance(secret_bytes, bytearray):
            raise TypeError("SecretZeroizer requires a mutable bytearray to safely zero memory.")
        self.secret_bytes = secret_bytes

    def __enter__(self) -> bytearray:
        return self.secret_bytes

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wipe()

    def wipe(self) -> None:
        """Overwrites every byte in the buffer with zeros."""
        for i in range(len(self.secret_bytes)):
            self.secret_bytes[i] = 0
