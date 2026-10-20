"""Authentication and Authorization Service.
Generated for task: Zamonaviy Online Do'kon va Savat Tizimi
Enforces secure token generation, PBKDF2 password hashing, RBAC, and rate limiting.
"""

import os
import hmac
import hashlib
import time
import base64
import json
from typing import Dict, Any, Optional, List

class TokenBucketRateLimiter:
    def __init__(self, capacity: int = 10, fill_rate: float = 1.0):
        self.capacity = float(capacity)
        self.fill_rate = fill_rate
        self.tokens = float(capacity)
        self.last_updated = time.time()

    def allow_request(self, cost: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_updated
        self.last_updated = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

class AuthSecurityService:
    def __init__(self, secret_key: Optional[str] = None):
        self._secret = (secret_key or os.getenv("APP_SECRET_KEY") or "secure_hallwright_token_secret_salt_912384").encode("utf-8")
        self._users: Dict[str, Dict[str, Any]] = {}
        self._rate_limiters: Dict[str, TokenBucketRateLimiter] = {}
        self._audit_log: List[Dict[str, Any]] = []

    def _log_event(self, action: str, username: str, success: bool, reason: str = "") -> None:
        self._audit_log.append({
            "timestamp": time.time(),
            "action": action,
            "username": username,
            "success": success,
            "reason": reason
        })

    def hash_password(self, password: str, salt: Optional[str] = None) -> str:
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        effective_salt = salt or base64.b64encode(os.urandom(16)).decode("utf-8")
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), effective_salt.encode("utf-8"), 100000)
        return f"pbkdf2:sha256:100000${effective_salt}${base64.b64encode(key).decode('utf-8')}"

    def verify_password(self, password: str, hashed: str) -> bool:
        if not password or not hashed or "$" not in hashed:
            return False
        parts = hashed.split("$")
        if len(parts) != 3:
            return False
        _, salt, expected_key = parts
        computed = self.hash_password(password, salt=salt)
        return hmac.compare_digest(computed, hashed)

    def register_user(self, username: str, password: str, role: str = "user") -> Dict[str, Any]:
        clean_user = username.strip().lower()
        if not clean_user or len(clean_user) < 3:
            raise ValueError("Username must be at least 3 characters")
        if clean_user in self._users:
            self._log_event("REGISTER", clean_user, False, "User exists")
            raise ValueError(f"User '{clean_user}' already registered")
        pw_hash = self.hash_password(password)
        user_record = {
            "username": clean_user,
            "password_hash": pw_hash,
            "role": role,
            "created_at": time.time(),
            "active": True
        }
        self._users[clean_user] = user_record
        self._rate_limiters[clean_user] = TokenBucketRateLimiter(capacity=10, fill_rate=2.0)
        self._log_event("REGISTER", clean_user, True)
        return {"username": clean_user, "role": role, "active": True}

    def authenticate_and_issue_token(self, username: str, password: str) -> Dict[str, Any]:
        clean_user = username.strip().lower()
        limiter = self._rate_limiters.setdefault(clean_user, TokenBucketRateLimiter(capacity=10, fill_rate=2.0))
        if not limiter.allow_request():
            self._log_event("LOGIN_ATTEMPT", clean_user, False, "Rate limit exceeded")
            raise ConnectionRefusedError("Too many login attempts. Please slow down.")

        user = self._users.get(clean_user)
        if not user or not user.get("active") or not self.verify_password(password, user["password_hash"]):
            self._log_event("LOGIN_ATTEMPT", clean_user, False, "Bad credentials")
            raise PermissionError("Invalid username or password")

        payload = {
            "sub": clean_user,
            "role": user["role"],
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        encoded = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
        signature = hmac.new(self._secret, encoded.encode("utf-8"), hashlib.sha256).hexdigest()
        token = f"{encoded}.{signature}"
        self._log_event("LOGIN_SUCCESS", clean_user, True)
        return {"access_token": token, "token_type": "Bearer", "expires_in": 3600, "role": user["role"]}

    def verify_token(self, token: str) -> Dict[str, Any]:
        if not token or "." not in token:
            raise ValueError("Malformed token format")
        encoded, signature = token.split(".", 1)
        expected = hmac.new(self._secret, encoded.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise PermissionError("Invalid token signature")
        payload = json.loads(base64.urlsafe_b64decode(encoded.encode("utf-8")).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            raise TimeoutError("Token expired")
        return payload

    def check_permission(self, token: str, required_role: str) -> bool:
        payload = self.verify_token(token)
        user_role = payload.get("role", "user")
        role_hierarchy = {"admin": 3, "manager": 2, "user": 1}
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
