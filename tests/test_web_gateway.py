"""Tests for Hallwright Universal Internet Gateway & Live Web Research Engine.
Verifies web search, page fetching, agent research queries, and caching.
"""

import os
import sys
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from web_gateway import InternetGateway


def test_internet_gateway_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = InternetGateway(workspace_root=tmpdir)
        hits = gateway.search("Python asyncio event loop", limit=2)
        assert len(hits) >= 1
        assert "title" in hits[0]
        assert "url" in hits[0]
        assert "snippet" in hits[0]


def test_internet_gateway_fetch_invalid_url():
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = InternetGateway(workspace_root=tmpdir)
        res = gateway.fetch_page("ftp://invalid-scheme.org")
        assert res["status"] == "ERROR"


def test_internet_gateway_research_for_agent():
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = InternetGateway(workspace_root=tmpdir)
        res = gateway.research_for_agent(
            agent_id="hallwright-security",
            task="Build JWT authentication and password hashing"
        )
        assert res["connected"] is True
        assert res["agent_id"] == "hallwright-security"
        assert "security" in res["query"].lower() or "jwt" in res["query"].lower()
        assert res["references_count"] >= 1


def test_internet_gateway_docs_query():
    with tempfile.TemporaryDirectory() as tmpdir:
        gateway = InternetGateway(workspace_root=tmpdir)
        hits = gateway.query_docs(tech="sqlite", topic="parameterized queries", limit=2)
        assert len(hits) >= 1
