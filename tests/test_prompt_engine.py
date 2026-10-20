import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompt_engine import PromptEngine, PromptQualityScore, OptimizationResult
from server import dispatch_request


@pytest.fixture
def engine():
    return PromptEngine()


def test_vague_prompt_elevation(engine):
    """Short and underspecified prompts must be elevated with Council invariants."""
    vague_prompt = "build authentication system"
    result = engine.optimize_prompt(vague_prompt)

    assert isinstance(result, OptimizationResult)
    assert result.status == "ELEVATION_APPLIED"
    assert result.score.is_complete is False
    assert result.score.total_score < 75.0
    assert len(result.enhancements_applied) > 0

    # Elevated prompt must contain defensive criteria and zero-stub invariants
    assert "Invariants" in result.final_prompt or "Defense" in result.final_prompt
    assert "vague or underspecified" in result.reason.lower()


def test_complete_prompt_passthrough(engine):
    """Comprehensive, detailed prompts must pass through 100% untouched without bloat."""
    detailed_prompt = (
        "Implement a resilient JWT token authentication service using Python and FastAPI. "
        "The service must store tokens in PostgreSQL with parameterized queries to prevent SQL injection. "
        "Ensure Argon2 password hashing with strict salt rounds. "
        "Include unit tests and integration tests verifying expired token rejection, replay attacks, "
        "and boundary validation. Return a clean API module in src/services/auth.py with zero stubs, "
        "comprehensive error handling, and structured logging."
    )

    result = engine.optimize_prompt(detailed_prompt)

    assert isinstance(result, OptimizationResult)
    assert result.status == "PASSTHROUGH_OPTIMAL"
    assert result.score.is_complete is True
    assert result.score.total_score >= 75.0
    # Core Invariant: final_prompt must exactly equal original_prompt
    assert result.final_prompt == detailed_prompt
    assert result.enhancements_applied == []
    assert "comprehensive" in result.reason.lower()


def test_score_dimensions(engine):
    """Verifies that all 5 quality dimensions are calculated accurately."""
    score = engine.analyze_quality("Quick fix")
    assert isinstance(score, PromptQualityScore)
    assert score.length_score <= 10.0
    assert score.edge_case_score == 0.0
    assert score.deliverable_score == 0.0
    assert score.total_score < 50.0

    score_dict = score.to_dict()
    assert "total_score" in score_dict
    assert "dimensions" in score_dict
    assert "is_complete" in score_dict


def test_domain_heuristics_injection(engine):
    """Ensures domain-specific Council Master heuristics are selected when appropriate."""
    db_prompt = "Create user profile storage table"
    result = engine.optimize_prompt(db_prompt, domain="database")
    assert result.domain == "database"
    assert any("database" in h.lower() or "sql" in h.lower() or "transaction" in h.lower() for h in result.enhancements_applied)

    sec_prompt = "Add password reset endpoint"
    result_sec = engine.optimize_prompt(sec_prompt, domain="security")
    assert result_sec.domain == "security"
    assert any("security" in h.lower() or "owasp" in h.lower() for h in result_sec.enhancements_applied)


def test_mcp_optimize_prompt_tool():
    """Verifies the MCP hallwright_optimize_prompt tool endpoint."""
    # 1. Underspecified prompt test
    req_vague = {
        "jsonrpc": "2.0",
        "id": 201,
        "method": "tools/call",
        "params": {
            "name": "hallwright_optimize_prompt",
            "arguments": {
                "prompt": "write a python script to parse csv"
            }
        }
    }
    resp = dispatch_request(req_vague)
    assert resp["id"] == 201
    assert "result" in resp
    content = resp["result"]["content"]
    parsed = json.loads(content[0]["text"])
    assert parsed["status"] == "ELEVATION_APPLIED"
    assert "final_prompt" in parsed

    # 2. Comprehensive prompt test
    req_complete = {
        "jsonrpc": "2.0",
        "id": 202,
        "method": "tools/call",
        "params": {
            "name": "hallwright_optimize_prompt",
            "arguments": {
                "prompt": (
                    "Build a streaming CSV parser in Python with pandas and asyncio. "
                    "Handle MalformedCSVError and EmptyFileError gracefully with custom exception classes. "
                    "Validate column headers against an explicit Pydantic schema. "
                    "Write unit tests with pytest covering empty files, corrupt rows, and large 1GB streams. "
                    "Deliver production code in src/parsers/csv_stream.py with zero TODO stubs."
                )
            }
        }
    }
    resp_complete = dispatch_request(req_complete)
    assert resp_complete["id"] == 202
    parsed_complete = json.loads(resp_complete["result"]["content"][0]["text"])
    assert parsed_complete["status"] == "PASSTHROUGH_OPTIMAL"
    assert parsed_complete["is_complete"] is True
    assert parsed_complete["analysis"]["is_complete"] is True
