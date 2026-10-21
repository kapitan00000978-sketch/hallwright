"""
Unit tests for Hallwright SwarmBlackboard & Multi-Agent Coordination Protocol.
Verifies contract-first agreements, structured handoff ledgers, conflict arbitration,
and SwarmOrchestrator integration.
"""

import os
import sys
import tempfile
import pytest

SDK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk"))
sys.path.insert(0, SDK_DIR)

from blackboard import SwarmBlackboard
from swarm import SwarmOrchestrator


@pytest.fixture
def temp_blackboard():
    with tempfile.TemporaryDirectory() as tmp_dir:
        board_file = os.path.join(tmp_dir, "test_blackboard.json")
        board = SwarmBlackboard(workspace_root=tmp_dir, board_path=board_file)
        yield board


def test_blackboard_contract_lifecycle(temp_blackboard):
    contract = temp_blackboard.register_contract(
        contract_id="contract_auth_v1",
        author_agent="hallwright-architect",
        contract_type="API_INTERFACE",
        spec={"endpoint": "/api/v1/auth", "method": "POST", "fields": ["username", "password"]},
        affected_files=["src/api/auth.py"]
    )
    assert contract["contract_id"] == "contract_auth_v1"
    assert contract["status"] == "ACTIVE"

    retrieved = temp_blackboard.get_contract("contract_auth_v1")
    assert retrieved is not None
    assert retrieved["spec"]["endpoint"] == "/api/v1/auth"

    all_active = temp_blackboard.list_contracts(status="ACTIVE")
    assert len(all_active) == 1


def test_blackboard_handoff_ledger(temp_blackboard):
    handoff = temp_blackboard.record_handoff(
        from_agent="hallwright-architect",
        to_agent="hallwright-designer",
        task_summary="Design tokens and dashboard layout",
        files_modified=["index.html", "src/styles.css"],
        contract_ids=["contract_auth_v1"],
        constraints_for_next=["Must use Plus Jakarta Sans and 8pt grid"],
        guarantees=["DOM elements conform to contract"]
    )
    assert handoff["from_agent"] == "hallwright-architect"
    assert handoff["to_agent"] == "hallwright-designer"
    assert "index.html" in handoff["files_modified"]

    latest = temp_blackboard.get_latest_handoff(for_agent="hallwright-designer")
    assert latest is not None
    assert latest["handoff_id"] == handoff["handoff_id"]


def test_blackboard_arbitration_security_vs_design(temp_blackboard):
    decision = temp_blackboard.arbitrate_conflict(
        topic="Dynamic Canvas vs Input Sanitization",
        agent_a="hallwright-designer",
        claim_a="Needs 3D canvas rendering and glowing buttons with innerHTML template.",
        agent_b="hallwright-security",
        claim_b="innerHTML is an XSS vulnerability vector, strictly ban it.",
        context={"target": "landing_page"}
    )
    assert decision["winner"] == "hallwright-security"
    assert "Security Invariant Enforced" in decision["resolution"]
    assert "Zero innerHTML" in decision["resolution"]


def test_blackboard_file_locking(temp_blackboard):
    locked = temp_blackboard.acquire_file_lock("hallwright-architect", "src/core.py", ttl_seconds=10.0)
    assert locked is True

    # Second agent cannot lock the same file
    locked_again = temp_blackboard.acquire_file_lock("hallwright-designer", "src/core.py", ttl_seconds=10.0)
    assert locked_again is False

    # First agent can re-lock or release
    released = temp_blackboard.release_file_lock("hallwright-architect", "src/core.py")
    assert released is True

    # Now second agent can acquire
    locked_after = temp_blackboard.acquire_file_lock("hallwright-designer", "src/core.py", ttl_seconds=10.0)
    assert locked_after is True


def test_swarm_orchestrator_blackboard_integration():
    with tempfile.TemporaryDirectory() as tmp_dir:
        orchestrator = SwarmOrchestrator(workspace_root=tmp_dir)
        res = orchestrator.execute_pipeline(
            task="Build secure ecommerce store with luxury UI and database persistence",
            files=["store.html", "store.py"]
        )
        assert res["status"] == "SWARM_PIPELINE_READY"
        assert res["stages_count"] >= 3
        assert len(res["contracts_registered"]) >= 1
        assert len(res["handoffs_recorded"]) >= 1

        # Check synchronized context inside stages
        first_stage = res["stages"][0]
        assert "synchronized_context" in first_stage
        assert first_stage["synchronized_context"]["task"] == "Build secure ecommerce store with luxury UI and database persistence"

        # Check arbitration triggered between designer and security
        agent_ids = [s["agent_id"] for s in res["stages"]]
        if "hallwright-security" in agent_ids and "hallwright-designer" in agent_ids:
            assert len(res["arbitrations"]) >= 1
