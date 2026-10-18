"""Hallwright Universal Enterprise Libraries.

Comprehensive, production-ready toolkits across key software craftsmanship domains:
- architecture: FSM, EventBus, CircuitBreaker, Clean Ports
- security: InputSanitizer, TokenBucketRateLimiter, JWTEngine, ASTSecurityScanner
- performance: LRUCache, SPSCRingBuffer, ObjectPool
- testing: EdgeCaseGenerator, FuzzRunner, assert_that, ASTMutationGenerator
- copywriting: MarkdownDocGenerator, ChangelogBuilder, DXLinter
- design: Standalone 3D Spatial Canvas Engine, Liquid Glass CSS
- registry: LibraryRegistry for dynamic inspection and project scaffolding
"""

from .registry import LibraryRegistry, DOMAIN_REGISTRY

__all__ = [
    "LibraryRegistry",
    "DOMAIN_REGISTRY",
]
