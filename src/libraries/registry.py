"""Hallwright Enterprise Libraries: Central Registry & Scaffolding Engine.

Provides metadata enumeration, component inspection, and automated code scaffolding
for all enterprise domain libraries (Architecture, Security, Performance, Testing, Copywriting, Design).
"""

import os
import shutil
from typing import Dict, List, Any


DOMAIN_REGISTRY: Dict[str, Dict[str, Any]] = {
    "architecture": {
        "title": "Enterprise Architecture & Clean Patterns",
        "description": "Deterministic finite state machines, decoupled event buses, circuit breakers, and clean hexagonal ports.",
        "modules": [
            {"name": "fsm.py", "class": "FiniteStateMachine", "purpose": "Deterministic state machine with guards and rollback"},
            {"name": "event_bus.py", "class": "EventBus", "purpose": "Decoupled pub/sub with wildcard patterns and dead-letter queue"},
            {"name": "circuit_breaker.py", "class": "CircuitBreaker", "purpose": "Fault tolerance, trip limits, and automatic recovery"},
            {"name": "ports.py", "class": "RepositoryPort", "purpose": "Clean hexagonal architecture entity and port abstractions"},
            {"name": "outbox_pattern.py", "class": "TransactionalOutbox", "purpose": "Guaranteed transactional outbox event delivery"},
            {"name": "invariant_guard.py", "class": "InvariantGuard", "purpose": "Architectural boundary and domain invariant enforcement"},
            {"name": "saga_coordinator.py", "class": "SagaCoordinator", "purpose": "Multi-agent transactional saga with compensation chain"},
        ],
    },
    "security": {
        "title": "Defensive Security & Zero-Trust Guards",
        "description": "Deep recursive input sanitization, token bucket rate limiters, standalone HS256 JWT, and AST security auditor.",
        "modules": [
            {"name": "sanitizer.py", "class": "InputSanitizer", "purpose": "XSS, SQLi, and path traversal defense"},
            {"name": "token_bucket.py", "class": "TokenBucketRateLimiter", "purpose": "Thread-safe DoS rate limiter"},
            {"name": "jwt_validator.py", "class": "JWTEngine", "purpose": "Zero-dependency HS256 JWT signer and verifier"},
            {"name": "ast_scanner.py", "class": "ASTSecurityScanner", "purpose": "Static AST vulnerability and secret audit"},
            {"name": "crypto_vault.py", "class": "CryptoVault", "purpose": "PBKDF2 key derivation and SecretZeroizer memory wipe"},
            {"name": "redos_sanitizer.py", "class": "ReDoSSanitizer", "purpose": "Catastrophic regex backtracking denial-of-service detector"},
            {"name": "owasp_guard.py", "class": "OwaspGuard", "purpose": "OWASP Top 10 semantic AST analyzer for injections and insecure deserialization"},
        ],
    },
    "performance": {
        "title": "Low-Latency High-Throughput Systems",
        "description": "Zero-allocation SPSC ring buffers, high-concurrency LRU/TTL caching, and pre-warmed object pools.",
        "modules": [
            {"name": "cache.py", "class": "LRUCache", "purpose": "O(1) thread-safe LRU & TTL cache with hit metrics"},
            {"name": "ring_buffer.py", "class": "SPSCRingBuffer", "purpose": "Single-producer single-consumer circular buffer"},
            {"name": "object_pool.py", "class": "ObjectPool", "purpose": "Recyclable object pool with RAII context manager"},
            {"name": "work_queue.py", "class": "WorkQueue", "purpose": "Cache-aligned prioritized thread pool with cancellation"},
        ],
    },
    "testing": {
        "title": "Adversarial Testing & Mutation Verification",
        "description": "Property-based boundary fuzzing, synthetic AST code mutants, and fluent chainable assertions.",
        "modules": [
            {"name": "fuzzer.py", "class": "EdgeCaseGenerator", "purpose": "Boundary numbers, adversarial strings, and fuzzer"},
            {"name": "assertions.py", "class": "assert_that", "purpose": "Fluent diagnostic assertion chains"},
            {"name": "mutation_suite.py", "class": "ASTMutationGenerator", "purpose": "Synthetic code mutant generator for test kill rates"},
        ],
    },
    "copywriting": {
        "title": "Developer Experience & Documentation",
        "description": "AST-first markdown reference generator, Keep-A-Changelog builder, and Flesch readability linter.",
        "modules": [
            {"name": "doc_generator.py", "class": "MarkdownDocGenerator", "purpose": "AST API reference documentation generator"},
            {"name": "changelog.py", "class": "ChangelogBuilder", "purpose": "Keep-A-Changelog release note constructor"},
            {"name": "dx_linter.py", "class": "DXLinter", "purpose": "Flesch readability and actionable error auditor"},
        ],
    },
    "design": {
        "title": "3D Spatial Canvas & Glassmorphic UI",
        "description": "Standalone 3D vector canvas engine, liquid glass dark mode CSS, and 3D agent swarm dashboard.",
        "modules": [
            {"name": "spatial_3d.js", "class": "SpatialScene", "purpose": "Standalone 3D perspective particle engine"},
            {"name": "liquid_glass.css", "class": "DesignTokens", "purpose": "Apple-grade dark glassmorphism stylesheet"},
            {"name": "dashboard_3d.html", "class": "HTML5 View", "purpose": "Interactive 3D Swarm & Library Dashboard"},
        ],
    },
    "resilience": {
        "title": "Fault Tolerance & System Resilience",
        "description": "Token bucket rate limiting, leaky bucket traffic smoothing, and adaptive backpressure flow control.",
        "modules": [
            {"name": "backpressure.py", "class": "TokenBucketLimiter", "purpose": "Token & Leaky Bucket traffic smoothing and backpressure flow control"},
            {"name": "chaos_injector.py", "class": "ChaosInjector", "purpose": "Deterministic and probabilistic chaos fault and latency injection"},
        ],
    },
    "database": {
        "title": "Database Security & Query Protection",
        "description": "AST SQL injection neutralizer and query safety verification.",
        "modules": [
            {"name": "sqli_neutralizer.py", "class": "SqlInjectionDetector", "purpose": "AST SQL injection neutralizer for concatenated or interpolated queries"},
        ],
    },
}


class LibraryRegistry:
    """Registry and installer for universal domain libraries."""

    @classmethod
    def list_domains(cls) -> Dict[str, Dict[str, Any]]:
        """Return all registered domain toolkits."""
        return DOMAIN_REGISTRY

    @classmethod
    def get_domain(cls, domain: str) -> Dict[str, Any]:
        """Get details for a specific domain."""
        domain_key = domain.lower().strip()
        if domain_key not in DOMAIN_REGISTRY:
            raise KeyError(f"Domain '{domain}' not found. Available: {list(DOMAIN_REGISTRY.keys())}")
        return DOMAIN_REGISTRY[domain_key]

    @classmethod
    def scaffold_domain(cls, domain: str, target_dir: str) -> List[str]:
        """Copy a domain library into a target project directory."""
        domain_info = cls.get_domain(domain)
        src_domain_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), domain.lower())
        
        if not os.path.exists(src_domain_dir):
            raise FileNotFoundError(f"Source domain directory not found: {src_domain_dir}")

        dest_dir = os.path.join(os.path.abspath(target_dir), domain.lower())
        os.makedirs(dest_dir, exist_ok=True)

        copied_files = []
        for filename in os.listdir(src_domain_dir):
            if filename.startswith("__pycache__"):
                continue
            src_file = os.path.join(src_domain_dir, filename)
            dest_file = os.path.join(dest_dir, filename)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, dest_file)
                copied_files.append(dest_file)

        return copied_files
