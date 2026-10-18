"""
Tests for Hallwright Titan Modular Enterprise Libraries & AgentMesh.
Verifies:
- AgentMesh event-bus and cross-agent communication
- TransactionalOutbox at-least-once reliable delivery
- InvariantGuard rule assertions and decorator contracts
- CryptoVault key derivation and SecretZeroizer memory wiping
- ReDoSSanitizer catastrophic backtracking detection
- TokenBucketLimiter and LeakyBucketQueue backpressure controllers
"""

import time
import pytest
from src.sdk.agent_mesh import AgentMesh, AgentContract, AgentMessage
from src.libraries.architecture.outbox_pattern import TransactionalOutbox, OutboxStatus
from src.libraries.architecture.invariant_guard import InvariantGuard, InvariantViolation, invariant_required
from src.libraries.security.crypto_vault import CryptoVault, SecretZeroizer
from src.libraries.security.redos_sanitizer import ReDoSSanitizer
from src.libraries.resilience.backpressure import TokenBucketLimiter, LeakyBucketQueue


def test_agent_mesh_publish_subscribe():
    mesh = AgentMesh(workspace_root=".")
    received = []

    def mock_security_auditor(msg: AgentMessage):
        received.append(msg.payload)
        return AgentMessage(
            topic="mesh:security:verdict",
            sender="artisan-security",
            payload={"status": "CLEAN", "scanned_keys": list(msg.payload.keys())}
        )

    mesh.subscribe("mesh:code:analyze", mock_security_auditor)

    responses = mesh.dispatch(
        topic="mesh:code:analyze",
        sender="artisan-architect",
        payload={"file": "auth.py", "lines": 42}
    )

    assert len(received) == 1
    assert received[0]["file"] == "auth.py"
    assert len(responses) == 1
    assert responses[0].sender == "artisan-security"
    assert responses[0].payload["status"] == "CLEAN"
    assert responses[0].parent_id is not None


def test_agent_mesh_history_and_ledger():
    mesh = AgentMesh(workspace_root=".")
    mesh.dispatch("topic:a", "agent_1", {"key": "val1"})
    mesh.dispatch("topic:b", "agent_2", {"key": "val2"})

    history = mesh.get_history(limit=5)
    assert len(history) >= 2
    assert any(h["sender"] == "agent_1" for h in history)
    assert any(h["sender"] == "agent_2" for h in history)


def test_transactional_outbox_publish_success():
    outbox = TransactionalOutbox(db_path=":memory:")
    rec = outbox.record_event(topic="user.registered", payload={"email": "dev@hallwright.org"})
    assert rec.status == OutboxStatus.PENDING

    pending = outbox.fetch_pending()
    assert len(pending) == 1
    assert pending[0].payload["email"] == "dev@hallwright.org"

    # Publisher that always succeeds
    def mock_publisher(topic: str, payload: dict) -> bool:
        return True

    published = outbox.process_pending(mock_publisher)
    assert published == 1
    assert len(outbox.fetch_pending()) == 0


def test_transactional_outbox_retry_and_dead_letter():
    outbox = TransactionalOutbox(db_path=":memory:")
    outbox.record_event(topic="invoice.generated", payload={"id": 101}, max_retries=2)

    # Publisher that fails
    def failing_publisher(topic: str, payload: dict) -> bool:
        return False

    # Attempt 1 -> FAILED
    outbox.process_pending(failing_publisher)
    pending = outbox.fetch_pending()
    assert len(pending) == 1
    assert pending[0].retry_count == 1
    assert pending[0].status == OutboxStatus.FAILED

    # Attempt 2 -> DEAD_LETTER
    outbox.process_pending(failing_publisher)
    assert len(outbox.fetch_pending()) == 0  # No longer pending


def test_invariant_guard_check_and_decorator():
    guard = InvariantGuard(strict_mode=True)
    guard.register("non_empty_string", lambda val: isinstance(val, str) and len(val.strip()) > 0)

    # Valid check
    res = guard.check("non_empty_string", "Valid input")
    assert res.passed is True

    # Violation triggers exception in strict mode
    with pytest.raises(InvariantViolation):
        guard.check("non_empty_string", "   ")

    # Decorator test
    @invariant_required("positive_number", lambda x: isinstance(x, (int, float)) and x > 0)
    def compute_discount(price: float) -> float:
        return price * 0.9

    assert compute_discount(100.0) == 90.0

    @invariant_required("positive_number", lambda x: isinstance(x, (int, float)) and x > 0)
    def bad_compute() -> float:
        return -5.0

    with pytest.raises(InvariantViolation):
        bad_compute()


def test_crypto_vault_pbkdf2_and_hmac():
    password = "MasterKeyP@ssw0rd!"
    key, salt = CryptoVault.derive_key(password)
    assert len(key) == 32
    assert len(salt) == 16

    # Verify same password + salt produces identical key
    key2, _ = CryptoVault.derive_key(password, salt=salt)
    assert key == key2

    # HMAC Signing and verification
    data = {"account_id": "acc_123", "amount": 5000}
    sig = CryptoVault.sign_payload(data, key)
    assert len(sig) == 64
    assert CryptoVault.verify_payload(data, sig, key) is True

    # Tampered payload fails
    tampered = {"account_id": "acc_123", "amount": 999999}
    assert CryptoVault.verify_payload(tampered, sig, key) is False


def test_secret_zeroizer_memory_wipe():
    buf = bytearray(b"super_sensitive_api_key_12345")
    assert any(b != 0 for b in buf)

    with SecretZeroizer(buf) as sec:
        assert sec[0] == ord("s")

    # After with block, all bytes must be 0
    assert all(b == 0 for b in buf)


def test_redos_sanitizer_catastrophic_backtracking():
    # Dangerous nested quantifier
    vulnerable_1 = r"^(a+)+$"
    findings = ReDoSSanitizer.audit_pattern(vulnerable_1)
    assert len(findings) > 0
    assert findings[0].vulnerability_type == "NESTED_QUANTIFIER"
    assert ReDoSSanitizer.is_safe(vulnerable_1) is False

    # Dangerous overlapping alternation inside repetition
    vulnerable_2 = r"^(foo|foobar)+$"
    findings_2 = ReDoSSanitizer.audit_pattern(vulnerable_2)
    assert len(findings_2) > 0
    assert findings_2[0].vulnerability_type == "OVERLAPPING_ALTERNATION"

    # Safe regex
    safe_regex = r"^[a-zA-Z0-9_-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
    assert ReDoSSanitizer.is_safe(safe_regex) is True


def test_backpressure_token_bucket():
    bucket = TokenBucketLimiter(capacity=3.0, refill_rate=10.0)
    assert bucket.acquire(1.0) is True
    assert bucket.acquire(1.0) is True
    assert bucket.acquire(1.0) is True
    # Capacity exhausted
    assert bucket.acquire(1.0, blocking=False) is False


def test_backpressure_leaky_bucket():
    queue = LeakyBucketQueue(capacity=2, leak_rate=10.0)
    assert queue.add(1.0) is True
    assert queue.add(1.0) is True
    # Capacity exceeded
    assert queue.add(1.0) is False
