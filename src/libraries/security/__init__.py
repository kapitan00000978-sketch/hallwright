"""Hallwright Enterprise Security Library.

Exposes security hardening components:
- InputSanitizer: Deep recursive XSS, SQLi, and path traversal sanitizer
- TokenBucketRateLimiter: Thread-safe high-throughput rate limiter
- JWTEngine: Zero-dependency HS256 JWT builder and validator
- ASTSecurityScanner: Static AST security auditor
"""

from .sanitizer import (
    InputSanitizer,
    SecuritySanitizationError,
)
from .token_bucket import (
    TokenBucketRateLimiter,
    RateLimitExceededError,
)
from .jwt_validator import (
    JWTEngine,
    JWTError,
    JWTExpiredError,
    JWTSignatureInvalidError,
    JWTFormatError,
)
from .ast_scanner import (
    ASTSecurityScanner,
    SecurityFinding,
)
from .crypto_vault import (
    CryptoVault,
    SecretZeroizer,
)
from .redos_sanitizer import (
    ReDoSSanitizer,
    ReDoSFinding,
)
from .owasp_guard import (
    OwaspGuard,
    SecurityVulnerability,
    scan_source_for_owasp_risks,
)

__all__ = [
    "InputSanitizer",
    "SecuritySanitizationError",
    "TokenBucketRateLimiter",
    "RateLimitExceededError",
    "JWTEngine",
    "JWTError",
    "JWTExpiredError",
    "JWTSignatureInvalidError",
    "JWTFormatError",
    "ASTSecurityScanner",
    "SecurityFinding",
    "CryptoVault",
    "SecretZeroizer",
    "ReDoSSanitizer",
    "ReDoSFinding",
    "OwaspGuard",
    "SecurityVulnerability",
    "scan_source_for_owasp_risks",
]
