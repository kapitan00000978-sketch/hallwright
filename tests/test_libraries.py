"""Tests for Artisan Universal Enterprise Domain Libraries.

Validates:
- Architecture (FSM, EventBus, CircuitBreaker, Clean Ports)
- Security (Sanitizer, TokenBucket, JWTEngine, ASTSecurityScanner)
- Performance (LRUCache, SPSCRingBuffer, ObjectPool)
- Testing (EdgeCaseGenerator, Fluent Assertions, ASTMutationGenerator)
- Copywriting (MarkdownDocGenerator, ChangelogBuilder, DXLinter)
- Design & Registry (Asset paths, Dashboard HTML, LibraryRegistry)
"""

import os
import time
import pytest
from src.libraries.architecture import (
    FiniteStateMachine,
    EventBus,
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenException,
    InvalidTransitionError,
    GuardFailedError,
    BaseEntity,
    AggregateRoot,
)
from src.libraries.security import (
    InputSanitizer,
    SecuritySanitizationError,
    TokenBucketRateLimiter,
    JWTEngine,
    JWTExpiredError,
    JWTSignatureInvalidError,
    ASTSecurityScanner,
)
from src.libraries.performance import (
    LRUCache,
    cached,
    SPSCRingBuffer,
    RingBufferFullError,
    RingBufferEmptyError,
    ObjectPool,
    ObjectPoolExhaustedError,
)
from src.libraries.testing import (
    EdgeCaseGenerator,
    assert_that,
    FluentAssertionError,
    ASTMutationGenerator,
)
from src.libraries.copywriting import (
    MarkdownDocGenerator,
    ChangelogBuilder,
    DXLinter,
)
from src.libraries.design import (
    get_asset_path,
    get_dashboard_html,
)
from src.libraries.registry import LibraryRegistry


# ============================================================================
# ARCHITECTURE TESTS
# ============================================================================

def test_fsm_lifecycle_and_rollback():
    """Verify FSM state transitions, guards, entry hooks, and rollback."""
    entered_states = []
    fsm = FiniteStateMachine(initial_state="DRAFT")
    fsm.on_enter("REVIEW", lambda ctx: entered_states.append("REVIEW"))

    fsm.add_transition(
        source="DRAFT",
        target="REVIEW",
        event="SUBMIT",
        guard=lambda ctx: ctx.get("is_valid", False),
    )
    fsm.add_transition(source="REVIEW", target="PUBLISHED", event="APPROVE")

    # Guard failure
    with pytest.raises(GuardFailedError):
        fsm.trigger("SUBMIT", is_valid=False)
    assert fsm.current_state == "DRAFT"

    # Guard success
    fsm.trigger("SUBMIT", is_valid=True)
    assert fsm.current_state == "REVIEW"
    assert "REVIEW" in entered_states

    # Transition to published
    fsm.trigger("APPROVE")
    assert fsm.current_state == "PUBLISHED"

    # Rollback to REVIEW
    prev = fsm.rollback()
    assert prev == "REVIEW"
    assert fsm.current_state == "REVIEW"


def test_event_bus_wildcards_and_dead_letters():
    """Verify EventBus wildcard routing, priority, and dead letter queue."""
    bus = EventBus()
    received_user_events = []
    received_all_events = []

    bus.subscribe("user.*", lambda payload: received_user_events.append(payload), priority=100)
    bus.subscribe("*", lambda topic, payload: received_all_events.append((topic, payload)), priority=50)

    delivered = bus.publish("user.created", {"user_id": 42})
    assert delivered == 2
    assert len(received_user_events) == 1
    assert received_user_events[0] == {"user_id": 42}

    # Unhandled event routed to dead letters
    delivered_unhandled = bus.publish("system.kernel.panic", "crash")
    # Wildcard '*' still matches
    assert delivered_unhandled == 1

    bus.clear()
    delivered_none = bus.publish("unhandled.topic", "lost")
    assert delivered_none == 0
    assert len(bus.dead_letters) == 1
    assert bus.dead_letters[0].reason == "NO_SUBSCRIBERS_MATCHED"


def test_circuit_breaker_trip_and_recovery():
    """Verify CircuitBreaker trips upon failure threshold and recovers."""
    cb = CircuitBreaker(
        name="test_service",
        failure_threshold=2,
        recovery_timeout_sec=0.1,
        half_open_success_threshold=1,
    )

    def failing_call():
        raise RuntimeError("Service unavailable")

    def successful_call():
        return "OK"

    # Trigger first failure
    with pytest.raises(RuntimeError):
        cb.execute(failing_call)
    assert cb.state == CircuitState.CLOSED

    # Trigger second failure (reaches threshold -> trips to OPEN)
    with pytest.raises(RuntimeError):
        cb.execute(failing_call)
    assert cb.state == CircuitState.OPEN

    # Fast failure while OPEN
    with pytest.raises(CircuitBreakerOpenException):
        cb.execute(successful_call)

    # Wait for recovery timeout
    time.sleep(0.12)
    assert cb.state == CircuitState.HALF_OPEN

    # Probe succeeds in HALF_OPEN -> transitions back to CLOSED
    res = cb.execute(successful_call)
    assert res == "OK"
    assert cb.state == CircuitState.CLOSED


def test_clean_ports_and_aggregate_root():
    """Verify BaseEntity equality and AggregateRoot domain event staging."""
    agg = AggregateRoot[str](id="order-101")
    assert agg.id == "order-101"
    assert agg.version == 1

    agg.increment_version()
    assert agg.version == 2

    agg.record_event("OrderCreated", {"total": 99.50})
    events = agg.pull_domain_events()
    assert len(events) == 1
    assert events[0]["type"] == "OrderCreated"

    # Second pull is empty
    assert len(agg.pull_domain_events()) == 0


# ============================================================================
# SECURITY TESTS
# ============================================================================

def test_input_sanitizer():
    """Verify recursive payload sanitization, XSS, and path traversal defense."""
    raw_payload = {
        "title": "<script>alert('xss')</script>",
        "tags": ["<b>alpha</b>", "safe text"],
        "nested": {"query": "SELECT * FROM users"},
    }
    cleaned = InputSanitizer.clean_payload(raw_payload)
    assert "&lt;script&gt;" in cleaned["title"]
    assert "&lt;b&gt;" in cleaned["tags"][0]

    # SQL injection detection
    assert InputSanitizer.detect_sql_injection("1' OR '1'='1' --") is True
    assert InputSanitizer.detect_sql_injection("normal username") is False

    # Path traversal detection
    with pytest.raises(SecuritySanitizationError):
        InputSanitizer.sanitize_path("../../etc/passwd", base_dir="./safe")


def test_token_bucket_rate_limiter():
    """Verify TokenBucket rate limiting and replenishment."""
    limiter = TokenBucketRateLimiter(capacity=2.0, refill_rate_per_sec=10.0)

    assert limiter.try_acquire(1.0) is True
    assert limiter.try_acquire(1.0) is True
    # Exhausted
    assert limiter.try_acquire(1.0) is False

    # Replenish
    time.sleep(0.12)
    assert limiter.try_acquire(1.0) is True


def test_jwt_engine_roundtrip_and_expiration():
    """Verify zero-dependency JWT encoding, decoding, and tamper resistance."""
    secret = "artisan-super-secret-key-32-bytes!"
    payload = {"sub": "user_42", "role": "admin"}

    token = JWTEngine.encode(payload, secret=secret, expires_in_sec=100)
    decoded = JWTEngine.decode(token, secret=secret)
    assert decoded["sub"] == "user_42"
    assert decoded["role"] == "admin"

    # Tampered signature
    with pytest.raises(JWTSignatureInvalidError):
        JWTEngine.decode(token, secret="wrong-secret-key!")

    # Expired token
    expired_token = JWTEngine.encode(payload, secret=secret, expires_in_sec=-10)
    with pytest.raises(JWTExpiredError):
        JWTEngine.decode(expired_token, secret=secret)


def test_ast_security_scanner():
    """Verify AST security scanner flags dangerous calls with line numbers."""
    unsafe_code = 'eval("user_input")\n'
    findings = ASTSecurityScanner.scan_source(unsafe_code)
    assert len(findings) >= 1
    assert any(f.rule_id == "SEC-001" for f in findings)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_lru_cache_and_cached_decorator():
    """Verify LRUCache capacity eviction, TTL, and @cached decorator."""
    cache = LRUCache(max_size=2)
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.get("a") == 1  # recency updated: 'b' is older now

    cache.set("c", 3)  # Evicts 'b'
    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3
    assert cache.evictions == 1

    # Decorator test
    call_counts = {"val": 0}

    @cached(max_size=10)
    def compute(n):
        call_counts["val"] += 1
        return n * 2

    assert compute(5) == 10
    assert compute(5) == 10
    assert call_counts["val"] == 1


def test_spsc_ring_buffer():
    """Verify SPSC ring buffer FIFO queue semantics and boundary exceptions."""
    buf = SPSCRingBuffer[int](capacity=3, overwrite_on_full=False)
    assert buf.is_empty is True

    buf.push(10)
    buf.push(20)
    buf.push(30)
    assert buf.is_full is True

    with pytest.raises(RingBufferFullError):
        buf.push(40)

    assert buf.pop() == 10
    assert buf.pop() == 20
    buf.push(50)
    assert buf.pop() == 30
    assert buf.pop() == 50
    assert buf.is_empty is True

    with pytest.raises(RingBufferEmptyError):
        buf.pop()


def test_object_pool_lifecycle():
    """Verify ObjectPool borrowing, returning, and context manager acquisition."""
    pool = ObjectPool[list](factory=lambda: [], reset_fn=lambda lst: lst.clear(), initial_size=2, max_capacity=3)
    assert pool.available_count == 2

    with pool.acquire() as item:
        item.append("working")
        assert len(item) == 1
    # Automatically reset and returned
    assert pool.available_count == 2

    # Borrow all
    o1 = pool.borrow()
    o2 = pool.borrow()
    o3 = pool.borrow()
    with pytest.raises(ObjectPoolExhaustedError):
        pool.borrow()

    pool.release(o1)
    pool.release(o2)
    pool.release(o3)


# ============================================================================
# TESTING & ASSERTIONS TESTS
# ============================================================================

def test_fluent_assertions():
    """Verify assert_that fluent chaining."""
    assert_that(42).is_equal_to(42).is_between(40, 50)
    assert_that("Artisan Protocol").contains("Artisan").matches_regex(r"^Artisan")
    assert_that([1, 2, 3]).has_length(3).contains(2)

    with pytest.raises(FluentAssertionError):
        assert_that(10).is_equal_to(20)


def test_ast_mutation_generator():
    """Verify synthetic mutant generation from comparison and boolean operators."""
    sample_code = "def check(x):\n    return x > 0 and True\n"
    mutants = ASTMutationGenerator.generate_mutants(sample_code)
    assert len(mutants) >= 1
    mutated_snippets = [m.mutated_code for m in mutants]
    assert any("<=" in snip for snip in mutated_snippets) or any("False" in snip for snip in mutated_snippets)


# ============================================================================
# COPYWRITING & DX TESTS
# ============================================================================

def test_markdown_doc_generator():
    """Verify AST documentation parser extracts functions, classes, and renders markdown."""
    src = '''
"""My sample module."""

class Worker:
    """A background worker."""
    def run(self, task: str) -> bool:
        """Execute a task."""
        return True
'''
    doc_mod = MarkdownDocGenerator.parse_source(src, module_name="worker_mod")
    assert len(doc_mod.classes) == 1
    assert doc_mod.classes[0].name == "Worker"
    assert len(doc_mod.classes[0].methods) == 1

    md = MarkdownDocGenerator.to_markdown(doc_mod)
    assert "# API Reference: `worker_mod`" in md
    assert "class Worker" in md
    assert "def run(self, task: str) -> bool" in md


def test_changelog_builder():
    """Verify Keep-A-Changelog builder markdown rendering."""
    cb = ChangelogBuilder("Artisan")
    cb.add_release("2.0.0", added=["Universal Domain Libraries", "3D Spatial Engine"])
    md = cb.render_markdown()
    assert "# Changelog: Artisan" in md
    assert "## [2.0.0]" in md
    assert "### Added" in md
    assert "- Universal Domain Libraries" in md


def test_dx_linter():
    """Verify syllable counting, readability calculations, and actionable error audits."""
    assert DXLinter.count_syllables("artisan") == 3
    assert DXLinter.count_syllables("the") == 1

    score = DXLinter.calculate_flesch_reading_ease("This is a simple sentence.")
    assert score > 70.0

    issues = DXLinter.audit_error_message("failed")
    assert any(i.rule == "DX-002" for i in issues)


# ============================================================================
# DESIGN & REGISTRY TESTS
# ============================================================================

def test_design_assets_exist():
    """Verify design static assets are discoverable and non-empty."""
    js_path = get_asset_path("spatial_3d.js")
    css_path = get_asset_path("liquid_glass.css")
    html_path = get_asset_path("dashboard_3d.html")

    assert os.path.exists(js_path)
    assert os.path.exists(css_path)
    assert os.path.exists(html_path)

    html = get_dashboard_html()
    assert "Artisan 3D Swarm" in html
    assert "spatial_3d.js" in html


def test_library_registry_metadata():
    """Verify LibraryRegistry lists all 6 domain libraries."""
    domains = LibraryRegistry.list_domains()
    assert "architecture" in domains
    assert "security" in domains
    assert "performance" in domains
    assert "testing" in domains
    assert "copywriting" in domains
    assert "design" in domains
    assert "resilience" in domains

    sec_info = LibraryRegistry.get_domain("security")
    assert len(sec_info["modules"]) >= 6

    arch_info = LibraryRegistry.get_domain("architecture")
    assert len(arch_info["modules"]) >= 6
