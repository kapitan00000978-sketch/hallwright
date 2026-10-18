"""Tests for Hallwright Universal Cross-Agent Continuity & Checkpoint Memory Engine.

Validates:
- Checkpoint persistence (.artisan/checkpoints.json)
- Markdown handoff generation (.artisan/agent_handoff.md)
- Resumption prompt formatting for incoming AI agents
- Optional bypass (enabled=False, --no-continuity, env var override)
- Milestone progression and merging
"""

import os
import shutil
import tempfile
import time
import pytest
from src.sdk.continuity import ContinuityManager, CheckpointData


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for test isolation."""
    temp_dir = tempfile.mkdtemp(prefix="artisan_continuity_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_continuity_save_and_load(temp_workspace):
    """Verify saving and retrieving atomic checkpoints."""
    mgr = ContinuityManager(workspace_root=temp_workspace)
    assert mgr.is_enabled is True

    # Initial state should be None
    assert mgr.load_checkpoint() is None

    # Save checkpoint
    saved = mgr.save_checkpoint(
        last_task="Implemented high-throughput ring buffer",
        last_agent="claude-3-7-sonnet",
        stopped_at_file="src/libraries/performance/ring_buffer.py",
        stopped_at_line=42,
        completed_milestones=["Architecture FSM", "Ring Buffer"],
        pending_milestones=["Write unit tests", "Run gatekeeper"],
        architectural_decisions=["Use SPSC circular buffer with zero allocations"],
        status="IN_PROGRESS",
    )
    assert saved is True

    cp = mgr.load_checkpoint()
    assert cp is not None
    assert cp.last_agent == "claude-3-7-sonnet"
    assert cp.last_task == "Implemented high-throughput ring buffer"
    assert cp.stopped_at_file == "src/libraries/performance/ring_buffer.py"
    assert cp.stopped_at_line == 42
    assert "Ring Buffer" in cp.completed_milestones
    assert "Write unit tests" in cp.pending_milestones


def test_continuity_milestone_progression(temp_workspace):
    """Verify that completing a pending milestone removes it from pending list."""
    mgr = ContinuityManager(workspace_root=temp_workspace)

    # First session
    mgr.save_checkpoint(
        last_task="Start work on security sanitizer",
        last_agent="cursor-agent",
        completed_milestones=[],
        pending_milestones=["Sanitizer", "JWT Validator"],
    )

    # Second session completing "Sanitizer"
    mgr.save_checkpoint(
        last_task="Finish security sanitizer",
        last_agent="hermes-agent",
        completed_milestones=["Sanitizer"],
        pending_milestones=["JWT Validator"],
    )

    cp = mgr.load_checkpoint()
    assert cp is not None
    assert "Sanitizer" in cp.completed_milestones
    # Sanitizer must not be in pending milestones
    assert "Sanitizer" not in cp.pending_milestones
    assert "JWT Validator" in cp.pending_milestones


def test_continuity_markdown_and_resumption_prompt(temp_workspace):
    """Verify generated handoff markdown and LLM resumption prompt."""
    mgr = ContinuityManager(workspace_root=temp_workspace)
    mgr.save_checkpoint(
        last_task="Created 3D spatial dashboard",
        last_agent="antigravity",
        stopped_at_file="src/libraries/design/dashboard_3d.html",
        stopped_at_line=100,
        completed_milestones=["3D Engine"],
        pending_milestones=["Add sound effects"],
        architectural_decisions=["Canvas 2D projection with zero external dependencies"],
    )

    # Verify agent_handoff.md was created
    handoff_path = os.path.join(temp_workspace, ".hallwright", "agent_handoff.md")
    assert os.path.exists(handoff_path)
    with open(handoff_path, "r", encoding="utf-8") as f:
        md = f.read()
    assert "Hallwright Universal Agent Handoff" in md
    assert "antigravity" in md
    assert "dashboard_3d.html" in md

    # Verify resumption prompt
    prompt = mgr.generate_resumption_prompt()
    assert "HALLWRIGHT CONTINUITY HANDOFF" in prompt
    assert "PREVIOUS AGENT: antigravity" in prompt
    assert "STOPPED AT FILE: src/libraries/design/dashboard_3d.html:100" in prompt
    assert "3D Engine" in prompt


def test_continuity_optional_bypass(temp_workspace, monkeypatch):
    """Verify that continuity can be completely disabled and bypassed."""
    # 1. Explicitly disabled manager
    disabled_mgr = ContinuityManager(workspace_root=temp_workspace, enabled=False)
    assert disabled_mgr.is_enabled is False
    assert disabled_mgr.load_checkpoint() is None
    assert disabled_mgr.save_checkpoint("Should not save") is False

    # 2. Environment variable override
    monkeypatch.setenv("ARTISAN_NO_CONTINUITY", "1")
    env_mgr = ContinuityManager(workspace_root=temp_workspace)
    assert env_mgr.is_enabled is False


def test_continuity_clear(temp_workspace):
    """Verify clearing checkpoints removes files cleanly."""
    mgr = ContinuityManager(workspace_root=temp_workspace)
    mgr.save_checkpoint(last_task="Temporary test")
    assert os.path.exists(mgr.checkpoint_file)

    cleared = mgr.clear()
    assert cleared is True
    assert not os.path.exists(mgr.checkpoint_file)
    assert not os.path.exists(mgr.handoff_file)
