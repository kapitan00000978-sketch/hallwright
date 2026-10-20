"""
Tests for Hallwright Multi-Agent Swarm Orchestrator Engine (src/sdk/swarm.py).
Verifies task decomposition, subagent delegation, session locking, and pipeline execution.
"""

import os
import sys
import tempfile
import json
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from swarm import SwarmOrchestrator, SUBAGENTS_ROSTER
from agent_registry import AgentRegistry


def test_subagents_roster():
    assert len(SUBAGENTS_ROSTER) == 11
    expected = [
        "hallwright-architect",
        "hallwright-security",
        "hallwright-critic",
        "hallwright-tester",
        "hallwright-performance",
        "hallwright-copywriter",
        "hallwright-healer",
        "hallwright-designer",
        "hallwright-database",
        "hallwright-devops",
        "hallwright-ai"
    ]
    for agent_id in expected:
        assert agent_id in SUBAGENTS_ROSTER
        assert "persona" in SUBAGENTS_ROSTER[agent_id]
        assert "role" in SUBAGENTS_ROSTER[agent_id]


def test_plan_swarm_pipeline_security_task():
    orchestrator = SwarmOrchestrator()
    task = "Build secure JWT login authentication with Stripe payments"
    pipeline = orchestrator.plan_swarm_pipeline(task)

    agent_ids = [s["agent_id"] for s in pipeline]
    assert "hallwright-architect" in agent_ids
    assert "hallwright-security" in agent_ids
    assert "hallwright-critic" in agent_ids
    assert "hallwright-tester" in agent_ids


def test_plan_swarm_pipeline_copywriting_task():
    orchestrator = SwarmOrchestrator()
    task = "Write comprehensive README and marketing landing page copy"
    pipeline = orchestrator.plan_swarm_pipeline(task, files=["README.md"])

    agent_ids = [s["agent_id"] for s in pipeline]
    assert "hallwright-copywriter" in agent_ids
    assert "hallwright-critic" in agent_ids


def test_execute_pipeline_registers_sessions():
    with tempfile.TemporaryDirectory() as tmpdir:
        sess_file = os.path.join(tmpdir, "sessions.json")
        reg = AgentRegistry(sessions_path=sess_file)
        orchestrator = SwarmOrchestrator(registry=reg)

        result = orchestrator.execute_pipeline("Implement low-latency cache for database queries", files=["cache.py"])
        assert result["status"] == "SWARM_PIPELINE_READY"
        assert result["stages_count"] >= 3
        assert len(result["registered_sessions"]) >= 3

        # Verify sessions in registry
        active = reg.get_active_sessions()
        assert len(active) >= 3


def test_format_cli_pipeline():
    orchestrator = SwarmOrchestrator()
    pipeline_data = orchestrator.execute_pipeline("Refactor payment gateway")
    formatted = orchestrator.format_cli_pipeline(pipeline_data)
    assert "HALLWRIGHT MULTI-AGENT SWARM ORCHESTRATOR" in formatted
    assert "Delegated Stages" in formatted
    assert "hallwright-critic" in formatted


def test_dispatch_swarm_mesh():
    orchestrator = SwarmOrchestrator()
    task = "Design high-throughput distributed database outbox and UI monitor"
    result = orchestrator.dispatch_swarm_mesh(task, files=["outbox.py"])

    assert result["status"] == "SWARM_MESH_COMPLETED"
    assert result["stages_executed"] >= 3
    assert result["trace_id"].startswith("swarm_")
    agent_ids = [s["agent_id"] for s in result["stages"]]
    assert "hallwright-architect" in agent_ids
    assert "hallwright-database" in agent_ids

