"""
Hallwright Prompt Quality & Elevation Engine
Part of the Hallwright Autonomous Quality Protocol.

Evaluates user prompt completeness and specificity:
1. If prompt is already comprehensive, detailed, and fully specified:
   -> Passes through directly untouched ("shundoq berilsin tekshiruvdan o'tmasdan").
2. If prompt is vague, underspecified, or ambiguous:
   -> Enriches it with Council Master domain invariants, edge-case defenses,
      typed contracts, and production-ready acceptance criteria.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("hallwright.prompt_engine")


@dataclass
class PromptQualityScore:
    total_score: float
    is_complete: bool
    status: str
    dimensions: Dict[str, float]
    detected_intent: str
    missing_elements: List[str]
    matched_masters: List[str]

    @property
    def length_score(self) -> float:
        return self.dimensions.get("length_depth", 0.0)

    @property
    def intent_score(self) -> float:
        return self.dimensions.get("intent_clarity", 0.0)

    @property
    def technical_score(self) -> float:
        return self.dimensions.get("technical_context", 0.0)

    @property
    def edge_case_score(self) -> float:
        return self.dimensions.get("constraints_edge_cases", 0.0)

    @property
    def deliverable_score(self) -> float:
        return self.dimensions.get("deliverables_criteria", 0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": round(self.total_score, 1),
            "is_complete": self.is_complete,
            "status": self.status,
            "dimensions": {k: round(v, 1) for k, v in self.dimensions.items()},
            "detected_intent": self.detected_intent,
            "missing_elements": self.missing_elements,
            "matched_masters": self.matched_masters,
        }


@dataclass
class OptimizationResult:
    original_prompt: str
    status: str
    is_complete: bool
    completeness_score: float
    final_prompt: str
    message: str
    analysis: Dict[str, Any]
    masters: List[str]
    missing_elements: List[str] = field(default_factory=list)
    enhancements_applied: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    _score_obj: Optional[PromptQualityScore] = None

    @property
    def score(self) -> Optional[PromptQualityScore]:
        return self._score_obj

    @property
    def reason(self) -> str:
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_prompt": self.original_prompt,
            "status": self.status,
            "is_complete": self.is_complete,
            "completeness_score": round(self.completeness_score, 1),
            "final_prompt": self.final_prompt,
            "message": self.message,
            "analysis": self.analysis,
            "masters": self.masters,
            "missing_elements": self.missing_elements,
            "enhancements_applied": self.enhancements_applied,
            "domain": self.domain,
        }


class PromptEngine:
    """Intelligent prompt evaluation and autonomous elevation engine."""

    ACTION_VERBS = {
        "create", "build", "implement", "develop", "refactor", "fix", "repair",
        "audit", "optimize", "benchmark", "deploy", "generate", "write", "migrate",
        "integrate", "test", "design", "configure", "setup", "qil", "tuzat", "yoz", "qur"
    }

    TECHNICAL_INDICATORS = {
        # Languages & frameworks
        "python", "javascript", "typescript", "rust", "go", "react", "next.js", "nextjs",
        "vue", "angular", "fastapi", "flask", "django", "express", "node", "html", "css",
        # Databases & storage
        "postgres", "postgresql", "mysql", "sqlite", "redis", "mongodb", "database", "sql", "orm",
        # Protocols & architecture
        "jwt", "oauth", "rest", "graphql", "grpc", "websocket", "api", "docker", "k8s",
        "kubernetes", "sre", "ci/cd", "microservice", "outbox", "eventbus", "fsm",
        # Design & UI
        "ui", "ux", "tailwind", "grid", "flexbox", "wcag", "contrast", "dark mode", "animation"
    }

    CONSTRAINTS_INDICATORS = {
        "rate limit", "timeout", "latency", "security", "zero-trust", "sanitiz",
        "validation", "error handling", "exception", "rollback", "idempotent",
        "concurrency", "thread-safe", "memory leak", "index", "pagination", "atomic",
        "p99", "64-byte", "non-blocking", "xss", "sqli", "csrf", "ssrf"
    }

    DELIVERABLE_INDICATORS = {
        "test", "tests", "unit test", "integration test", "documentation", "readme",
        "pydantic", "dataclass", "interface", "schema", "type", "return", "status code",
        "json", "endpoint", "migration"
    }

    def __init__(self, completeness_threshold: float = 75.0):
        self.completeness_threshold = completeness_threshold

    def analyze_prompt(self, prompt: str) -> PromptQualityScore:
        clean_text = (prompt or "").strip()
        words = re.findall(r"\b[\w'-]+\b", clean_text.lower())
        word_count = len(words)

        if word_count == 0:
            return PromptQualityScore(
                total_score=0.0,
                is_complete=False,
                status="EMPTY_PROMPT",
                dimensions={"length": 0.0, "intent": 0.0, "technical": 0.0, "constraints": 0.0, "deliverables": 0.0},
                detected_intent="None",
                missing_elements=["Prompt cannot be empty."],
                matched_masters=[]
            )

        # 1. Dimension: Length & Depth (max 20 pts)
        # Very short prompts (<10 words) get penalized; descriptive prompts (>25 words) get high scores
        if word_count < 6:
            length_score = 4.0
        elif word_count < 12:
            length_score = 9.0
        elif word_count < 20:
            length_score = 15.0
        else:
            length_score = 20.0

        # 2. Dimension: Intent & Action Clarity (max 20 pts)
        has_action = any(v in words for v in self.ACTION_VERBS)
        intent_score = 20.0 if has_action else 8.0
        detected_intent = next((v for v in self.ACTION_VERBS if v in words), "General Engineering")

        # 3. Dimension: Technical Context & Stack (max 25 pts)
        tech_hits = [t for t in self.TECHNICAL_INDICATORS if t in clean_text.lower()]
        if len(tech_hits) >= 3:
            tech_score = 25.0
        elif len(tech_hits) == 2:
            tech_score = 18.0
        elif len(tech_hits) == 1:
            tech_score = 10.0
        else:
            tech_score = 2.0

        # 4. Dimension: Constraints & Edge Cases (max 20 pts)
        constraint_hits = [c for c in self.CONSTRAINTS_INDICATORS if c in clean_text.lower()]
        if len(constraint_hits) >= 2:
            constraint_score = 20.0
        elif len(constraint_hits) == 1:
            constraint_score = 12.0
        else:
            constraint_score = 0.0

        # 5. Dimension: Deliverables & Acceptance Criteria (max 15 pts)
        deliverable_hits = [d for d in self.DELIVERABLE_INDICATORS if d in clean_text.lower()]
        if len(deliverable_hits) >= 2:
            deliverable_score = 15.0
        elif len(deliverable_hits) == 1:
            deliverable_score = 8.0
        else:
            deliverable_score = 0.0

        total_score = length_score + intent_score + tech_score + constraint_score + deliverable_score

        # Identify missing elements
        missing = []
        if tech_score < 15.0:
            missing.append("Specific technology stack, frameworks, or libraries not clearly stated.")
        if constraint_score < 10.0:
            missing.append("Non-functional constraints, security defenses, or edge cases missing.")
        if deliverable_score < 8.0:
            missing.append("Clear deliverables, data schemas, or test coverage requirements omitted.")
        if word_count < 12:
            missing.append("Prompt is very brief/vague, leaving architectural decisions to chance.")

        # Determine matched Council Masters
        matched_masters = []
        if any(w in words for w in ("security", "auth", "jwt", "token", "password", "hash", "secret")):
            matched_masters.append("Gabriel Frost (Cybersecurity)")
        if any(w in words for w in ("database", "sql", "postgres", "sqlite", "query", "migration", "index")):
            matched_masters.append("Cassandra Thorne (Database)")
        if any(w in words for w in ("ui", "ux", "design", "css", "html", "color", "animation", "grid", "responsive")):
            matched_masters.append("Elena Rostova (UI/UX)")
        if any(w in words for w in ("docker", "deploy", "devops", "container", "k8s", "sre", "ci/cd")):
            matched_masters.append("Gareth Drake (DevOps)")
        if any(w in words for w in ("performance", "latency", "cache", "alloc", "fast", "speed", "simd")):
            matched_masters.append("Valerie Cross (Systems Performance)")
        if not matched_masters or any(w in words for w in ("architecture", "refactor", "solid", "module", "service")):
            matched_masters.append("Marcus Sterling (Software Architect)")

        is_complete = (total_score >= self.completeness_threshold) and (len(missing) <= 1)
        status = "PASSTHROUGH_OPTIMAL" if is_complete else "ELEVATION_REQUIRED"

        return PromptQualityScore(
            total_score=total_score,
            is_complete=is_complete,
            status=status,
            dimensions={
                "length_depth": length_score,
                "intent_clarity": intent_score,
                "technical_context": tech_score,
                "constraints_edge_cases": constraint_score,
                "deliverables_criteria": deliverable_score,
            },
            detected_intent=detected_intent.title(),
            missing_elements=missing,
            matched_masters=matched_masters,
        )

    def analyze_quality(self, prompt: str) -> PromptQualityScore:
        """Alias for analyze_prompt."""
        return self.analyze_prompt(prompt)

    def optimize_prompt(
        self,
        prompt: str,
        force_elevate: bool = False,
        domain: Optional[str] = None
    ) -> OptimizationResult:
        """
        Evaluates prompt.
        If prompt is complete and not force_elevate:
          -> Passes through directly untouched.
        If prompt is underspecified:
          -> Elevates into an actionable, world-class engineered specification.
        """
        analysis = self.analyze_prompt(prompt)

        # 1. Optimal Passthrough Mode: User gave a thorough, complete prompt
        if analysis.is_complete and not force_elevate:
            return OptimizationResult(
                original_prompt=prompt,
                status="PASSTHROUGH_OPTIMAL",
                is_complete=True,
                completeness_score=analysis.total_score,
                final_prompt=prompt,  # Exact original prompt! Untouched!
                message="Prompt is comprehensive and well-specified. Passed through directly without modification.",
                analysis=analysis.to_dict(),
                masters=analysis.matched_masters,
                missing_elements=[],
                enhancements_applied=[],
                domain=domain,
                _score_obj=analysis,
            )

        # 2. Elevation Mode: Prompt is vague, lazy, or incomplete
        enhancements = [
            "Zero-Stub & Zero-Placeholders Invariant",
            "Defensive Architecture & Input Sanitization",
            "Boundary Condition & Timeout Defense",
            "Explicit Verification & Test Suite Criteria",
        ]

        if domain:
            dom_lower = domain.lower()
            if "data" in dom_lower or "sql" in dom_lower:
                enhancements.append("Database Transaction Isolation & Parameterized SQL")
            elif "sec" in dom_lower or "auth" in dom_lower:
                enhancements.append("OWASP Top 10 Security & Credential Protection")
            elif "ui" in dom_lower or "front" in dom_lower or "design" in dom_lower:
                enhancements.append("WCAG 2.1 AAA Accessibility & 8pt Spatial Grid")
            elif "devops" in dom_lower or "infra" in dom_lower:
                enhancements.append("Immutable Containerization & Healthcheck Probes")

        elevated_spec = self._synthesize_elevated_prompt(prompt, analysis, domain=domain, extra_enhancements=enhancements)
        return OptimizationResult(
            original_prompt=prompt,
            status="ELEVATION_APPLIED",
            is_complete=False,
            completeness_score=analysis.total_score,
            final_prompt=elevated_spec,
            message=f"Prompt scored {analysis.total_score:.0f}/100 (vague or underspecified). Enriched with Council of Masters invariants.",
            analysis=analysis.to_dict(),
            missing_elements=analysis.missing_elements,
            enhancements_applied=enhancements,
            masters=analysis.matched_masters,
            domain=domain,
            _score_obj=analysis,
        )

    def _synthesize_elevated_prompt(
        self,
        raw_prompt: str,
        analysis: PromptQualityScore,
        domain: Optional[str] = None,
        extra_enhancements: Optional[List[str]] = None,
    ) -> str:
        masters_str = ", ".join(analysis.matched_masters)
        domain_badge = f" [{domain.upper()}]" if domain else ""
        lines = [
            f"# 🎯 ELEVATED ENGINEERING DIRECTIVE{domain_badge}: {analysis.detected_intent}",
            f"> **Original Prompt:** \"{raw_prompt}\"",
            f"> **Council Masters Engaged:** {masters_str}",
            "",
            "## 1. Primary Objective & Architectural Scope",
            f"Implement a production-grade, complete solution addressing: {raw_prompt}.",
            "All components must be modular, strongly typed, and decoupled from external side-effects.",
            "",
            "## 2. Inviolable Quality Invariants (Zero-Defect Protocol)",
            "- **Zero Placeholders:** Never emit unfinished markers (TODO/FIXME), empty pass, or mock return dictionaries.",  # hallwright-ignore
            "- **Zero Silent Catches:** Bare except or empty catch blocks are prohibited. Log context with logger.error or re-raise.",  # hallwright-ignore
            "- **Zero Plaintext Secrets:** Hardcoded passwords, JWT tokens, or credentials are strictly outlawed.",
            "- **Defensive Architecture:** Enforce input sanitization against SQLi, command injection, and SSRF.",
            "",
            "## 3. Edge-Case & Boundary Defense",
            "- Validate boundary inputs (empty states, nulls, zeroes, negative values, and maximum boundary thresholds).",
            "- Implement graceful fallback and structured error responses on unexpected timeouts or service disconnects.",
            "- Ensure deterministic, idempotent execution across repeat invocations.",
            "",
            "## 4. Deliverables & Verification Criteria",
            "- Fully functional, complete implementation with explicit type hints and parameter docstrings.",
            "- Accompanying unit/integration test suite covering both nominal success and adversarial failure paths.",
            "- Quality verification: Verify code achieves 100/100 score on Hallwright Pre-Commit Gatekeeper."
        ]
        return "\n".join(lines)
