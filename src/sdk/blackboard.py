"""
Hallwright SwarmBlackboard: Multi-Agent State Synchronization & Coordination Engine.
Part of Pillar III: Sub-Agent Mesh & Swarm Intelligence Architecture.

Solves multi-agent communication breakdown by providing:
1. Shared Blackboard State: Centralized, process-safe session memory (.hallwright/swarm_blackboard.json)
2. Contract-First Protocol: Explicit API schemas, model interfaces, and UI data-testids
3. Structured Handoff Ledger: Formal handover artifacts between sequential agent stages
4. Conflict Arbitration: Marcus Sterling Chief Arbiter resolving security vs design vs performance trade-offs
5. File-Lock Registry: Eliminates concurrent overwrite collisions between sub-agents
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("hallwright.swarm.blackboard")

DEFAULT_BLACKBOARD_PATH = os.path.join(".hallwright", "swarm_blackboard.json")


class SwarmBlackboard:
    """
    Centralized communication and agreement board for multi-agent swarms.
    Ensures sub-agents operate with unified contracts, seamless handoffs, and zero collisions.
    """

    def __init__(self, workspace_root: str = ".", board_path: Optional[str] = None):
        self.workspace_root = workspace_root
        self.board_path = board_path or os.path.join(workspace_root, DEFAULT_BLACKBOARD_PATH)
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Initializes empty blackboard structure if file does not exist."""
        board_dir = os.path.dirname(self.board_path)
        if board_dir and not os.path.exists(board_dir):
            os.makedirs(board_dir, exist_ok=True)

        if not os.path.exists(self.board_path):
            initial_state = {
                "version": "1.1.0",
                "initialized_at": datetime.now(timezone.utc).isoformat(),
                "contracts": {},
                "handoff_ledger": [],
                "arbitration_decisions": [],
                "file_locks": {},
                "active_task": "",
                "pipeline_status": "IDLE"
            }
            self._write_state(initial_state)

    def _read_state(self) -> Dict[str, Any]:
        """Reads blackboard state safely from disk."""
        if not os.path.exists(self.board_path):
            self._ensure_storage()
        try:
            with open(self.board_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {
                "version": "1.1.0",
                "contracts": {},
                "handoff_ledger": [],
                "arbitration_decisions": [],
                "file_locks": {},
                "active_task": "",
                "pipeline_status": "RECOVERED"
            }

    def _write_state(self, state: Dict[str, Any]) -> None:
        """Atomically persists blackboard state to disk."""
        tmp_path = f"{self.board_path}.tmp_{uuid.uuid4().hex[:6]}"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, self.board_path)

    # -------------------------------------------------------------------------
    # 1. Contract-First Protocol
    # -------------------------------------------------------------------------
    def register_contract(
        self,
        contract_id: str,
        author_agent: str,
        contract_type: str,
        spec: Dict[str, Any],
        affected_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Registers an explicit architectural contract (data schema, API endpoints, UI IDs).
        All downstream agents must strictly conform to this contract.
        """
        state = self._read_state()
        contract_entry = {
            "contract_id": contract_id,
            "author_agent": author_agent,
            "contract_type": contract_type,
            "spec": spec,
            "affected_files": affected_files or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "ACTIVE"
        }
        state["contracts"][contract_id] = contract_entry
        self._write_state(state)
        logger.info("Agent %s registered contract '%s' (%s)", author_agent, contract_id, contract_type)
        return contract_entry

    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific contract by ID."""
        state = self._read_state()
        return state.get("contracts", {}).get(contract_id)

    def list_contracts(self, status: str = "ACTIVE") -> List[Dict[str, Any]]:
        """Lists all registered contracts matching status."""
        state = self._read_state()
        contracts = list(state.get("contracts", {}).values())
        if status:
            return [c for c in contracts if c.get("status") == status]
        return contracts

    # -------------------------------------------------------------------------
    # 2. Structured Handoff Ledger
    # -------------------------------------------------------------------------
    def record_handoff(
        self,
        from_agent: str,
        to_agent: str,
        task_summary: str,
        files_modified: List[str],
        contract_ids: Optional[List[str]] = None,
        constraints_for_next: Optional[List[str]] = None,
        guarantees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Records a formal handoff ledger entry from one agent stage to the next.
        Eliminates guesswork and ping-pong regression between agents.
        """
        state = self._read_state()
        handoff_entry = {
            "handoff_id": f"ho_{uuid.uuid4().hex[:8]}",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task_summary": task_summary,
            "files_modified": files_modified,
            "contract_ids": contract_ids or [],
            "constraints_for_next": constraints_for_next or [],
            "guarantees": guarantees or [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        state["handoff_ledger"].append(handoff_entry)
        self._write_state(state)
        logger.info("Handoff recorded from %s -> %s for task '%s'", from_agent, to_agent, task_summary[:30])
        return handoff_entry

    def get_latest_handoff(self, for_agent: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves the most recent handoff entry, optionally addressed to a specific agent."""
        state = self._read_state()
        ledger = state.get("handoff_ledger", [])
        if not ledger:
            return None
        if for_agent:
            matches = [h for h in ledger if h.get("to_agent") in (for_agent, "all", "*")]
            return matches[-1] if matches else None
        return ledger[-1]

    # -------------------------------------------------------------------------
    # 3. Conflict Arbitration Engine (Marcus Sterling Protocol)
    # -------------------------------------------------------------------------
    def arbitrate_conflict(
        self,
        topic: str,
        agent_a: str,
        claim_a: str,
        agent_b: str,
        claim_b: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Marcus Sterling Chief Arbiter: Resolves conflicting agent requirements objectively.
        Precedence Rules:
        - Security wins on fundamental vulnerabilities (SQLi, XSS, Secret Leaks).
        - However, Security must offer safe implementation pathways (e.g. local vendor bundling, non-eval JS) rather than killing user features.
        - Architecture wins on systemic modularity, data contracts, and dependency trees.
        - Design wins on ergonomics, spatial grids, 60fps micro-interactions, and visual depth.
        - Performance wins on algorithmic latency and memory leaks, but cannot break contract correctness.
        """
        state = self._read_state()
        decision_id = f"arb_{uuid.uuid4().hex[:8]}"

        # Deterministic arbitration logic based on domain invariants
        resolution = ""
        ruling_authority = "Marcus 'The Vanguard' Sterling (Supreme Arbiter)"
        winner = ""

        lower_claim_a = claim_a.lower()
        lower_claim_b = claim_b.lower()

        # Security vs Design (e.g. Gabriel Frost vs Elena Rostova)
        if "security" in agent_a or "security" in agent_b:
            sec_agent = agent_a if "security" in agent_a else agent_b
            other_agent = agent_b if sec_agent == agent_a else agent_a
            other_claim = claim_b if sec_agent == agent_a else claim_a

            if any(k in (lower_claim_a + lower_claim_b) for k in ["xss", "innerhtml", "eval", "sqli", "secret", "token"]):
                winner = sec_agent
                resolution = (
                    f"Security Invariant Enforced: {other_agent}'s request is approved ONLY with secure primitives. "
                    "Zero innerHTML/eval permitted; use textContent, createElement, or pre-compiled safe templates."
                )
            else:
                winner = "COMPROMISE"
                resolution = (
                    f"Synergistic Synthesis: {other_agent} retains modern visual/functional capability, "
                    f"while {sec_agent} verifies CSP policies, sanitization, and zero remote CDN sinks."
                )
        # Architecture vs Database (e.g. Marcus Sterling vs Cassandra Thorne)
        elif "database" in agent_a or "database" in agent_b:
            db_agent = agent_a if "database" in agent_a else agent_b
            winner = db_agent
            resolution = (
                f"Data Integrity Mandate: {db_agent}'s ACID transaction boundaries and index coverage take precedence. "
                "Architectural layers must wrap mutations in atomic transactions."
            )
        else:
            winner = agent_a
            resolution = f"Architectural Standard: {agent_a}'s specification ratified with {agent_b}'s constraints integrated."

        decision_entry = {
            "decision_id": decision_id,
            "topic": topic,
            "parties": {agent_a: claim_a, agent_b: claim_b},
            "winner": winner,
            "resolution": resolution,
            "ruling_authority": ruling_authority,
            "context": context or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        state["arbitration_decisions"].append(decision_entry)
        self._write_state(state)
        logger.info("Conflict arbitrated on '%s': %s", topic, resolution)
        return decision_entry

    # -------------------------------------------------------------------------
    # 4. Context Synchronization for Sub-Agents
    # -------------------------------------------------------------------------
    def get_synchronized_context(self, agent_id: str, current_task: str) -> Dict[str, Any]:
        """
        Builds a comprehensive, zero-drift context packet for a sub-agent before it begins work.
        Includes active contracts, predecessor handoffs, and ruling decisions.
        """
        state = self._read_state()
        handoff = self.get_latest_handoff(for_agent=agent_id) or self.get_latest_handoff()
        active_contracts = self.list_contracts(status="ACTIVE")
        relevant_contracts = [
            c for c in active_contracts
            if not handoff or not handoff.get("contract_ids") or c["contract_id"] in handoff["contract_ids"]
        ]

        return {
            "agent_id": agent_id,
            "task": current_task,
            "blackboard_status": state.get("pipeline_status", "ACTIVE"),
            "predecessor_handoff": handoff,
            "active_contracts": relevant_contracts,
            "recent_arbitrations": state.get("arbitration_decisions", [])[-3:],
            "file_locks": list(state.get("file_locks", {}).keys())
        }

    # -------------------------------------------------------------------------
    # 5. File Lock Registry (Collision Prevention)
    # -------------------------------------------------------------------------
    def acquire_file_lock(self, agent_id: str, file_path: str, ttl_seconds: float = 60.0) -> bool:
        """Acquires an exclusive lock on a file for an agent to prevent race conditions."""
        state = self._read_state()
        now = time.time()
        current_lock = state.get("file_locks", {}).get(file_path)

        if current_lock and current_lock.get("expires_at", 0) > now:
            if current_lock.get("agent_id") == agent_id:
                current_lock["expires_at"] = now + ttl_seconds
                self._write_state(state)
                return True
            return False

        state["file_locks"][file_path] = {
            "agent_id": agent_id,
            "acquired_at": now,
            "expires_at": now + ttl_seconds
        }
        self._write_state(state)
        return True

    def release_file_lock(self, agent_id: str, file_path: str) -> bool:
        """Releases a file lock held by an agent."""
        state = self._read_state()
        current_lock = state.get("file_locks", {}).get(file_path)
        if current_lock and current_lock.get("agent_id") == agent_id:
            del state["file_locks"][file_path]
            self._write_state(state)
            return True
        return False

    def clear(self) -> None:
        """Resets the blackboard to fresh idle state."""
        self._ensure_storage()
        initial_state = {
            "version": "1.1.0",
            "initialized_at": datetime.now(timezone.utc).isoformat(),
            "contracts": {},
            "handoff_ledger": [],
            "arbitration_decisions": [],
            "file_locks": {},
            "active_task": "",
            "pipeline_status": "IDLE"
        }
        self._write_state(initial_state)
