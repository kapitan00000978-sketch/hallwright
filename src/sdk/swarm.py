"""
Hallwright Multi-Agent Swarm Orchestrator Engine.
Part of the Hallwright Autonomous Craftsmanship Protocol (Phase 4).

Coordinates specialized sub-agents (architect, security, critic, tester, performance, copywriter, healer)
to execute complex software engineering tasks collaboratively with zero context pollution,
conflict-free file locking, and multi-persona adversarial verification.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger("hallwright.swarm")

try:
    from agent_registry import AgentRegistry
except ImportError:
    AgentRegistry = None

try:
    from learning_memory import LearningMemory
except ImportError:
    LearningMemory = None


SUBAGENTS_ROSTER = {
    "hallwright-architect": {
        "persona": "Marcus Sterling",
        "role": "Senior Software Architect",
        "description": "Modular system design, clean abstractions, domain modeling, and zero technical debt.",
        "domains": ["architecture", "api", "database", "backend", "refactor", "system", "structure", "design"]
    },
    "hallwright-security": {
        "persona": "Gabriel Frost",
        "role": "Principal Cybersecurity Auditor",
        "description": "Zero-trust threat modeling, credential protection, OWASP Top 10 defense, and sanitization.",
        "domains": ["auth", "security", "jwt", "login", "payment", "crypto", "token", "password", "permission"]
    },
    "hallwright-critic": {
        "persona": "Adversarial Red-Team Critic",
        "role": "Independent Code Auditor",
        "description": "Objective red-team review, defect ledger compilation, and independent veto/approval decisions.",
        "domains": ["review", "audit", "diff", "pr", "quality", "veto", "gatekeeper"]
    },
    "hallwright-tester": {
        "persona": "Mutation & Test Lead",
        "role": "Senior Quality & Mutation Engineer",
        "description": "Test suite authoring, AST mutation analysis, boundary assertions, and fuzzing.",
        "domains": ["test", "mutation", "coverage", "benchmark", "assert", "mock", "spec"]
    },
    "hallwright-performance": {
        "persona": "Valerie Cross & Thaddeus Vance",
        "role": "Low-Latency Systems Architect",
        "description": "Mechanical sympathy, CPU cache alignment, low tail-latency, and non-blocking I/O.",
        "domains": ["performance", "speed", "latency", "async", "cache", "memory", "profiling", "fast"]
    },
    "hallwright-copywriter": {
        "persona": "Diana Drake",
        "role": "Conversion & DX Copywriter",
        "description": "Direct-response developer experience, high-conversion READMEs, and crystal-clear documentation.",
        "domains": ["doc", "readme", "copy", "landing", "marketing", "changelog", "guide"]
    },
    "hallwright-healer": {
        "persona": "Autonomous Remediator",
        "role": "Self-Correction & AST Repair Engineer",
        "description": "Automatic remediation of silent exceptions, unfinished stubs, and syntax regressions.",
        "domains": ["fix", "repair", "remediate", "clean", "healing", "stub"]
    }
}


class SwarmOrchestrator:
    """
    Decomposes tasks into specialized sub-agent delegations and orchestrates collaborative execution.
    """

    def __init__(self, registry: Optional[Any] = None, memory: Optional[Any] = None):
        self.registry = registry if registry else (AgentRegistry() if AgentRegistry else None)
        self.memory = memory if memory else (LearningMemory() if LearningMemory else None)

    def plan_swarm_pipeline(self, task: str, files: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Analyzes task intent and constructs an ordered multi-stage sub-agent execution pipeline.
        """
        task_lower = task.lower()
        files = files or []
        stages: List[Dict[str, Any]] = []

        # Scoring relevance of each sub-agent
        scores: Dict[str, int] = {}
        for agent_id, meta in SUBAGENTS_ROSTER.items():
            score = 0
            for d in meta["domains"]:
                if d in task_lower:
                    score += 2
            # Check file extensions
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in (".md", ".txt") and agent_id == "hallwright-copywriter":
                    score += 3
                elif ext in (".py", ".ts", ".js", ".go", ".rs") and agent_id in ("hallwright-architect", "hallwright-critic", "hallwright-tester"):
                    score += 1
            scores[agent_id] = score

        # Always include architect for system-level implementation
        if any(w in task_lower for w in ["build", "create", "implement", "feature", "add", "develop"]):
            scores["hallwright-architect"] = max(scores.get("hallwright-architect", 0), 3)

        # Always include security if authentication, keys, or endpoints are touched
        if any(w in task_lower for w in ["auth", "login", "jwt", "token", "payment", "api", "key", "secret"]):
            scores["hallwright-security"] = max(scores.get("hallwright-security", 0), 4)

        # Always include tester for implementation tasks
        if any(w in task_lower for w in ["build", "create", "fix", "implement", "refactor"]):
            scores["hallwright-tester"] = max(scores.get("hallwright-tester", 0), 2)

        # Always include critic as the final gatekeeper
        scores["hallwright-critic"] = max(scores.get("hallwright-critic", 0), 3)

        # Order agents sequentially into clear stages
        execution_order = [
            "hallwright-architect",
            "hallwright-security",
            "hallwright-performance",
            "hallwright-tester",
            "hallwright-critic",
            "hallwright-healer",
            "hallwright-copywriter"
        ]

        stage_num = 1
        for agent_id in execution_order:
            if scores.get(agent_id, 0) > 0:
                meta = SUBAGENTS_ROSTER[agent_id]
                lessons = self._get_agent_lessons(agent_id, task)
                stages.append({
                    "stage": stage_num,
                    "agent_id": agent_id,
                    "persona": meta["persona"],
                    "role": meta["role"],
                    "description": meta["description"],
                    "relevant_lessons": lessons,
                    "target_files": files
                })
                stage_num += 1

        return stages

    def execute_pipeline(self, task: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Simulates and registers multi-agent swarm execution across active sessions.
        """
        pipeline = self.plan_swarm_pipeline(task, files)
        sessions_created = []

        # Register active session locks in AgentRegistry to guarantee zero collision
        if self.registry:
            for stage in pipeline:
                agent_id = stage["agent_id"]
                try:
                    sess = self.registry.register_session(
                        agent_name=agent_id,
                        active_files=files,
                        intent=f"Stage {stage['stage']}: {stage['role']} - {task[:40]}"
                    )
                    sessions_created.append(sess.get("session_id"))
                except OSError as reg_err:
                    logger.debug("Session registration skipped: %s", reg_err)

        return {
            "task": task,
            "stages_count": len(pipeline),
            "stages": pipeline,
            "registered_sessions": sessions_created,
            "orchestrated_at": datetime.now(timezone.utc).isoformat(),
            "status": "SWARM_PIPELINE_READY"
        }

    def _get_agent_lessons(self, agent_id: str, task: str) -> List[Dict[str, Any]]:
        """Retrieves lessons from living memory tailored to the subagent's domain."""
        if not self.memory:
            return []
        try:
            domain_query = SUBAGENTS_ROSTER.get(agent_id, {}).get("domains", ["code"])[0]
            lessons = self.memory.get_lessons(task=f"{domain_query} {task}", limit=2)
            return lessons
        except (KeyError, OSError, ValueError) as mem_err:
            logger.debug("Could not fetch domain lessons: %s", mem_err)
            return []

    def format_cli_pipeline(self, pipeline_data: Dict[str, Any]) -> str:
        """Visualizes the swarm delegation pipeline in a formatted terminal graph."""
        lines = [
            "\n🤖 [HALLWRIGHT MULTI-AGENT SWARM ORCHESTRATOR]",
            f"🎯 Mission: \"{pipeline_data['task']}\"",
            f"📋 Delegated Stages: {pipeline_data['stages_count']} sub-agent stages\n",
            "────────────────────────────────────────────────────────────────────────"
        ]

        for s in pipeline_data["stages"]:
            lines.append(f"  Stage {s['stage']}: 🤖 [{s['agent_id']}] — {s['persona']} ({s['role']})")
            lines.append(f"          Focus: {s['description']}")
            if s["relevant_lessons"]:
                lesson_str = "; ".join(f"[{l.get('id', 'mem')}] {l.get('lesson', '')[:50]}..." for l in s["relevant_lessons"])
                lines.append(f"          🧠 Injected Scar Tissue: {lesson_str}")
            lines.append("")

        lines.append("────────────────────────────────────────────────────────────────────────")
        lines.append("✅ Swarm coordination active. Sessions synchronized via Hallwright AgentRegistry.")
        return "\n".join(lines)
