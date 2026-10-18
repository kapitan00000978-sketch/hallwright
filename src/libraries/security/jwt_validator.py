"""Hallwright Enterprise Security Library: Zero-Dependency JWT Engine.

Provides cryptographically secure JSON Web Token (JWT) creation, decoding,
and signature verification using Python standard library HMAC-SHA256.
"""

import json
import base64
import hmac
import hashlib
import time
from typing import Dict, Any, Optional


class JWTError(Exception):
    """Base exception for JWT validation failures."""
    pass


class JWTExpiredError(JWTError):
    """Raised when the token's exp claim is in the past."""
    pass


class JWTSignatureInvalidError(JWTError):
    """Raised when token signature does not match secret."""
    pass


class JWTFormatError(JWTError):
    """Raised when token string is malformed."""
    pass


class JWTEngine:
    """Zero-dependency HS256 JWT signer and verifier.

    Features:
    - Base64URL encoding/decoding without padding issues
    - Timing-attack resistant signature comparison via hmac.compare_digest
    - Standard claim validation: 'exp', 'nbf', 'iat', 'iss', 'aud'
    - Custom claims preservation
    """

    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        """Encode bytes to base64url string without trailing '=' padding."""
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    @staticmethod
    def _b64url_decode(segment: str) -> bytes:
        """Decode base64url string with dynamic padding restoration."""
        rem = len(segment) % 4
        if rem > 0:
            segment += "=" * (4 - rem)
        try:
            return base64.urlsafe_b64decode(segment.encode("utf-8"))
        except Exception as exc:
            raise JWTFormatError(f"Invalid base64url encoding: {str(exc)}")

    @classmethod
    def encode(
        cls,
        payload: Dict[str, Any],
        secret: str,
        expires_in_sec: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Encode and sign a payload dictionary into a compact JWT token."""
        if not secret:
            raise ValueError("JWT secret must not be empty.")

        header_dict = dict(headers or {})
        header_dict.setdefault("typ", "JWT")
        header_dict["alg"] = "HS256"

        body = dict(payload)
        now = int(time.time())
        body.setdefault("iat", now)
        if expires_in_sec is not None:
            body["exp"] = now + int(expires_in_sec)

        header_json = json.dumps(header_dict, separators=(",", ":"), sort_keys=True).encode("utf-8")
        payload_json = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")

        encoded_header = cls._b64url_encode(header_json)
        encoded_payload = cls._b64url_encode(payload_json)

        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        encoded_signature = cls._b64url_encode(signature)

        return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

    @classmethod
    def decode(
        cls,
        token: str,
        secret: str,
        verify_exp: bool = True,
        leeway_sec: int = 0,
        expected_issuer: Optional[str] = None,
        expected_audience: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Decode and verify a signed JWT token."""
        if not isinstance(token, str) or not token:
            raise JWTFormatError("Token must be a non-empty string.")

        parts = token.split(".")
        if len(parts) != 3:
            raise JWTFormatError("JWT token must consist of exactly 3 parts separated by dots.")

        encoded_header, encoded_payload, encoded_signature = parts

        # Verify Signature
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = cls._b64url_decode(encoded_signature)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise JWTSignatureInvalidError("Token signature verification failed.")

        # Decode Header & Payload
        try:
            payload_data = json.loads(cls._b64url_decode(encoded_payload).decode("utf-8"))
        except Exception as exc:
            raise JWTFormatError(f"Malformed JSON payload: {str(exc)}")

        now = int(time.time())

        # Validate Expiration (exp)
        if verify_exp and "exp" in payload_data:
            exp_time = payload_data["exp"]
            if now > exp_time + leeway_sec:
                raise JWTExpiredError(f"Token expired at {exp_time} (current time {now}).")

        # Validate Not Before (nbf)
        if "nbf" in payload_data:
            nbf_time = payload_data["nbf"]
            if now < nbf_time - leeway_sec:
                raise JWTError(f"Token not valid before {nbf_time}.")

        # Validate Issuer (iss)
        if expected_issuer is not None:
            if payload_data.get("iss") != expected_issuer:
                raise JWTError(f"Issuer mismatch: expected '{expected_issuer}', got '{payload_data.get('iss')}'.")

        # Validate Audience (aud)
        if expected_audience is not None:
            if payload_data.get("aud") != expected_audience:
                raise JWTError(f"Audience mismatch: expected '{expected_audience}', got '{payload_data.get('aud')}'.")

        return payload_data
