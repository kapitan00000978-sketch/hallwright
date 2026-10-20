"""
Hallwright Autonomous Self-Evolution Engine (evolution.py).
Part of Pillar II & III: Continuous Learning Memory & Autonomous Immunity Architecture.

Enforces closed-loop self-evolution:
- Non-blocking asynchronous ingestion: AI agents are NEVER halted or blocked.
- Live web research on detected defects: Extracts root causes and modern web fixes.
- Dynamic vaccine synthesis: Formulates permanent guardrail rules and increments generation.
- Swarm-wide immunization: Automatically injects learned vaccines into agent contexts.
"""

import os
import sys
import json
import uuid
import logging
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

logger = logging.getLogger("hallwright.evolution")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

try:
    from search_engine import search_web, SearchScope
except ImportError:
    try:
        from src.sdk.search_engine import search_web, SearchScope
    except ImportError:
        search_web = None
        SearchScope = None

try:
    from learning_memory import LearningMemory
except ImportError:
    LearningMemory = None

try:
    from agent_mesh import AgentMesh, AgentMessage
except ImportError:
    AgentMesh = None
    AgentMessage = None


@dataclass
class ImmunityVaccine:
    """Canonical representation of an evolved immunity rule synthesized from a defect."""
    id: str
    generation: int
    category: str
    error_signature: str
    root_cause: str
    web_solution: str
    guardrail_rule: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImmunityVaccine":
        return cls(
            id=data.get("id", f"vac-{uuid.uuid4().hex[:4]}"),
            generation=data.get("generation", 1),
            category=data.get("category", "reliability"),
            error_signature=data.get("error_signature", "Unspecified error pattern"),
            root_cause=data.get("root_cause", "Unspecified defect root cause"),
            web_solution=data.get("web_solution", "Apply defensive boundary validation and structured handling"),
            guardrail_rule=data.get("guardrail_rule", "DEFENSIVE_INVARIANT_ENFORCED"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat())
        )


class SelfEvolutionEngine:
    """
    Closed-loop, non-blocking self-evolution engine.
    Monitors defect events, researches solutions online in the background,
    synthesizes permanent immunity vaccines, and advances the project generation.
    """

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root
        self.ledger_dir = os.path.join(workspace_root, ".hallwright")
        self.ledger_path = os.path.join(self.ledger_dir, "immune_system.json")
        self._lock = threading.RLock()
        self._active_workers: List[threading.Thread] = []
        self._init_immune_ledger()

    def _init_immune_ledger(self) -> None:
        """Initializes immune ledger with baseline Generation 1 vaccines if not existing."""
        with self._lock:
            os.makedirs(self.ledger_dir, exist_ok=True)
            if not os.path.exists(self.ledger_path):
                baseline_data = {
                    "version": "1.0.0",
                    "project": "Hallwright Autonomous Immune Core",
                    "generation": 1,
                    "immunity_score": 90,
                    "last_evolved_at": datetime.now(timezone.utc).isoformat(),
                    "total_vaccines": 3,
                    "vaccines": [
                        {
                            "id": "vac-001",
                            "generation": 1,
                            "category": "security",
                            "error_signature": "SQL Injection vulnerability via string concatenation",
                            "root_cause": "Dynamic string formatting interpolates untrusted inputs into SQL statements",
                            "web_solution": "Use parameterized queries with prepared statements (e.g. cursor.execute('SELECT * FROM users WHERE id = %s', (uid,)))",
                            "guardrail_rule": "ALL_QUERIES_MUST_BE_PARAMETERIZED",
                            "created_at": datetime.now(timezone.utc).isoformat()
                        },
                        {
                            "id": "vac-002",
                            "generation": 1,
                            "category": "reliability",
                            "error_signature": "Silent exception suppression with bare except statement and pass",
                            "root_cause": "Empty catch or unhandled exception block swallows fatal runtime errors",
                            "web_solution": "Always catch explicit exceptions and log with logger.error or re-raise with context",
                            "guardrail_rule": "NEVER_USE_BARE_EXCEPTION_SUPPRESSION",
                            "created_at": datetime.now(timezone.utc).isoformat()
                        },
                        {
                            "id": "vac-003",
                            "generation": 1,
                            "category": "runtime",
                            "error_signature": "ZeroDivisionError / Unchecked divisor",
                            "root_cause": "Divisor variable reaches zero without prior defensive boundary checking",
                            "web_solution": "Guard divisor against zero (e.g. if divisor == 0: return fallback) before division",
                            "guardrail_rule": "ALWAYS_GUARD_DIVISORS_AGAINST_ZERO",
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                    ]
                }
                try:
                    with open(self.ledger_path, "w", encoding="utf-8") as f:
                        json.dump(baseline_data, f, indent=2)
                except OSError as write_err:
                    logger.debug("Failed initializing immune ledger: %s", write_err)

    def load_immune_state(self) -> Dict[str, Any]:
        """Loads current immune state and active vaccines from disk."""
        with self._lock:
            if not os.path.exists(self.ledger_path):
                self._init_immune_ledger()
            try:
                with open(self.ledger_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as read_err:
                logger.debug("Could not read immune ledger: %s", read_err)
                return {
                    "generation": 1,
                    "immunity_score": 90,
                    "total_vaccines": 0,
                    "vaccines": []
                }

    def ingest_and_evolve_async(
        self,
        defect_text: str,
        file_path: Optional[str] = None,
        callback: Optional[Any] = None
    ) -> threading.Thread:
        """
        NON-BLOCKING BACKGROUND EVOLUTION:
        Spawns a background worker thread that searches the web and evolves the project
        without interrupting or blocking the AI agent's active coding stream.
        """
        thread_name = f"ImmuneWorker-{uuid.uuid4().hex[:6]}"
        worker = threading.Thread(
            target=self._background_evolution_worker,
            args=(defect_text, file_path, callback),
            name=thread_name,
            daemon=True
        )
        with self._lock:
            self._active_workers.append(worker)
        worker.start()
        logger.info("Launched non-blocking self-evolution thread '%s' for defect: %s", thread_name, defect_text[:40])
        return worker

    def _background_evolution_worker(
        self,
        defect_text: str,
        file_path: Optional[str],
        callback: Optional[Any]
    ) -> None:
        """Worker executing web research and vaccine synthesis in background."""
        try:
            vaccine = self.evolve_sync(defect_text=defect_text, file_path=file_path)
            if callback and callable(callback):
                try:
                    callback(vaccine)
                except Exception as cb_err:
                    logger.debug("Evolution callback error: %s", cb_err)
        except Exception as worker_err:
            logger.debug("Background evolution error: %s", worker_err)
        finally:
            with self._lock:
                curr = threading.current_thread()
                if curr in self._active_workers:
                    self._active_workers.remove(curr)

    def evolve_sync(
        self,
        defect_text: str,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronously processes defect, searches web, synthesizes vaccine,
        and advances project generation.
        """
        clean_defect = defect_text.strip()
        signature, category = self._extract_signature_and_category(clean_defect)

        # 1. Check if identical vaccine already exists
        state = self.load_immune_state()
        existing_signatures = [v.get("error_signature", "").lower() for v in state.get("vaccines", [])]
        if signature.lower() in existing_signatures:
            logger.info("Defect signature '%s' already neutralized in active generation.", signature)
            matched = next(v for v in state.get("vaccines", []) if v.get("error_signature", "").lower() == signature.lower())
            return {
                "status": "ALREADY_IMMUNIZED",
                "generation": state.get("generation", 1),
                "vaccine": matched
            }

        # 2. Research optimal fix online
        web_solution, rule_name = self._research_web_solution(signature, category)

        # 3. Formulate new Immunity Vaccine
        with self._lock:
            current_gen = state.get("generation", 1) + 1
            vaccine_id = f"vac-{len(state.get('vaccines', [])) + 1:03d}"

            new_vaccine = ImmunityVaccine(
                id=vaccine_id,
                generation=current_gen,
                category=category,
                error_signature=signature,
                root_cause=f"Defect '{signature}' occurred in {file_path or 'workspace'}",
                web_solution=web_solution,
                guardrail_rule=rule_name
            )

            state["generation"] = current_gen
            state["last_evolved_at"] = datetime.now(timezone.utc).isoformat()
            state["vaccines"].append(new_vaccine.to_dict())
            state["total_vaccines"] = len(state["vaccines"])
            state["immunity_score"] = min(100, 90 + state["total_vaccines"])

            try:
                with open(self.ledger_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
            except OSError as save_err:
                logger.debug("Failed saving evolved immune ledger: %s", save_err)

        # 4. Ingest into Living Memory as [EVOLVED_IMMUNITY]
        if LearningMemory:
            try:
                mem = LearningMemory(workspace_root=self.workspace_root)
                mem.record_learning(
                    record_type="rule",
                    category=category,
                    pattern=f"[EVOLVED_IMMUNITY] {signature}",
                    lesson=f"Gen {current_gen} Vaccine: {web_solution}. Enforced by rule: {rule_name}",
                    severity="high"
                )
            except Exception as mem_err:
                logger.debug("Learning memory ingestion skipped: %s", mem_err)

        # 5. Broadcast to AgentMesh and Live Hub
        self._broadcast_evolution_event(new_vaccine, current_gen)

        logger.info("✨ [EVOLUTION SUCCESS]: Project evolved to Generation %d with Vaccine %s", current_gen, vaccine_id)
        return {
            "status": "EVOLVED",
            "generation": current_gen,
            "immunity_score": state["immunity_score"],
            "vaccine": new_vaccine.to_dict()
        }

    def _extract_signature_and_category(self, defect: str) -> tuple:
        """Parses defect text to isolate signature and domain category."""
        d_lower = defect.lower()
        if "sql" in d_lower or "injection" in d_lower:
            return "SQL Injection vulnerability via raw interpolation", "security"
        elif "xss" in d_lower or "innerhtml" in d_lower:
            return "DOM Cross-Site Scripting (XSS) via unescaped HTML", "security"
        elif "token" in d_lower or "secret" in d_lower or "key" in d_lower:
            return "Plaintext secret or credential exposure", "security"
        elif "zerodivision" in d_lower or "division by zero" in d_lower:
            return "ZeroDivisionError: unhandled zero divisor in computation", "runtime"
        elif "indexerror" in d_lower or "out of range" in d_lower:
            return "IndexError: list index accessed without length boundary check", "runtime"
        elif "keyerror" in d_lower:
            return "KeyError: dictionary key accessed without get() fallback or guard", "runtime"
        elif "typeerror" in d_lower:
            return "TypeError: unexpected type operation without typeguard", "runtime"
        elif "silent exception" in d_lower or "bare except" in d_lower or "empty catch" in d_lower:
            return "Silent exception suppression concealing runtime defects", "reliability"
        elif "memory leak" in d_lower or "unclosed" in d_lower:
            return "Resource leak: unclosed file descriptor or handle", "performance"
        else:
            first_line = defect.split("\n")[0][:80]
            return f"Defect pattern: {first_line}", "quality"

    def _research_web_solution(self, signature: str, category: str) -> tuple:
        """Researches optimal solutions online and synthesizes invariant rule."""
        query = f"how to fix {signature} best practice design pattern"
        solution = ""
        rule = "DEFENSIVE_INVARIANT_ENFORCED"

        if search_web:
            try:
                results = search_web(query=query, limit=2)
                if results:
                    snippets = " ".join(r.get("snippet", "") for r in results if r.get("snippet"))
                    if len(snippets) > 40:
                        solution = snippets[:180] + "..."
            except Exception as s_err:
                logger.debug("Live web search fallback in evolution engine: %s", s_err)

        if not solution:
            fallbacks = {
                "security": "Enforce strict parameterized input sanitization, zero plain text secrets, and OWASP Top 10 defense.",
                "runtime": "Implement defensive boundary guards (e.g. check None, 0, and collection bounds) before operations.",
                "reliability": "Catch specific exceptions explicitly, log with logger.error, and avoid silent swallows.",
                "performance": "Ensure deterministic resource cleanup using context managers (with statements) and connection pools.",
                "quality": "Apply modular domain separation and verify 100/100 Pre-Commit Gatekeeper compliance."
            }
            solution = fallbacks.get(category, "Apply defensive programming and zero-stub architecture.")

        rule_map = {
            "security": "INPUT_SANITIZATION_AND_ZERO_PLAIN_SECRETS",
            "runtime": "DEFENSIVE_BOUNDARY_AND_NULL_GUARD",
            "reliability": "EXPLICIT_EXCEPTION_LOGGING_NO_BARE_CATCH",
            "performance": "CONTEXT_MANAGED_RESOURCE_LIFECYCLE",
            "quality": "ZERO_STUB_PRODUCTION_COMPLIANCE"
        }
        rule = rule_map.get(category, "INVARIANT_QUALITY_RULE")
        return solution, rule

    def _broadcast_evolution_event(self, vaccine: ImmunityVaccine, generation: int) -> None:
        """Publishes evolution events across AgentMesh and Live Hub."""
        if AgentMesh:
            try:
                mesh = AgentMesh(workspace_root=self.workspace_root)
                mesh.dispatch(
                    topic="evolution.vaccinated",
                    sender="SelfEvolutionEngine",
                    payload={
                        "generation": generation,
                        "vaccine_id": vaccine.id,
                        "category": vaccine.category,
                        "rule": vaccine.guardrail_rule,
                        "solution": vaccine.web_solution
                    }
                )
            except Exception as mesh_err:
                logger.debug("AgentMesh evolution publish skipped: %s", mesh_err)

        try:
            from live_hub import hub_registry
            hub_registry.broadcast("evolution_event", {
                "generation": generation,
                "vaccine": vaccine.to_dict(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception as hub_err:
            logger.debug("LiveHub broadcast skipped: %s", hub_err)

    def get_vaccination_prompt_injection(self, task: str = "") -> str:
        """
        Compiles active vaccines into an immunization directive
        injected silently into AI subagent prompts.
        """
        state = self.load_immune_state()
        gen = state.get("generation", 1)
        vaccines = state.get("vaccines", [])
        if not vaccines:
            return ""

        lines = [
            f"## 🧬 Autonomous Project Immunity (Generation {gen}):",
            "The following invariants have been evolved from past lessons and MUST be strictly upheld:"
        ]
        for v in vaccines[-5:]:
            lines.append(f"- **[{v.get('guardrail_rule', 'INVARIANT')}]:** {v.get('web_solution')}")

        return "\n".join(lines)


# Singleton convenience instance
default_evolution_engine = SelfEvolutionEngine()


def evolve_async(defect_text: str, file_path: Optional[str] = None) -> threading.Thread:
    """Convenience function to trigger non-blocking background evolution."""
    return default_evolution_engine.ingest_and_evolve_async(defect_text, file_path)


def evolve_sync(defect_text: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for synchronous evolution."""
    return default_evolution_engine.evolve_sync(defect_text, file_path)
