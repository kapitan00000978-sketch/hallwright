import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from search_engine import SearchEngine, SearchHit, SearchResultSet, SearchScope
from server import dispatch_request


@pytest.fixture
def engine():
    return SearchEngine(workspace_root=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_search_council_by_name(engine):
    results = engine.search_council("Marcus", limit=5)
    assert len(results) > 0
    assert any("Marcus" in r.title for r in results)
    assert results[0].category == "council"
    assert results[0].score >= 80.0


def test_search_council_by_keyword(engine):
    results = engine.search_council("database", limit=5)
    assert len(results) > 0
    assert any("Cassandra" in r.title for r in results)


def test_search_libraries(engine):
    results = engine.search_libraries("jwt", limit=5)
    assert len(results) > 0
    jwt_hit = next((r for r in results if "jwt" in r.metadata.get("module", "").lower()), None)
    assert jwt_hit is not None
    assert jwt_hit.category == "libraries"
    assert "src/libraries/security/jwt_validator.py" in jwt_hit.metadata["path"]


def test_search_memory(engine):
    results = engine.search_memory("expiration", limit=5)
    assert len(results) > 0
    assert results[0].category == "memory"
    assert "exp" in results[0].snippet.lower() or "expiration" in results[0].title.lower()


def test_search_plugins(engine):
    results = engine.search_plugins("database", limit=5)
    assert len(results) > 0
    assert any("database" in r.title.lower() for r in results)


def test_search_code(engine):
    results = engine.search_code("detect_tech_stack", limit=5)
    assert len(results) > 0
    assert results[0].category == "code"
    assert "hallwright_cli.py" in results[0].metadata["path"]
    assert results[0].metadata["line"] > 0


def test_search_unified_all(engine):
    results = engine.search("database", scope="all", limit=5)
    assert results.total_hits > 0
    assert "council" in results.by_category
    assert "libraries" in results.by_category
    assert results.query == "database"
    assert results.scope == "all"

    # Terminal format should render without error
    terminal_output = results.format_terminal()
    assert "HALLWRIGHT UNIFIED SEARCH ENGINE" in terminal_output
    assert "database" in terminal_output


def test_search_empty_query(engine):
    results = engine.search("", scope="all")
    assert results.total_hits == 0
    assert len(results.hits) == 0


def test_search_scope_filter(engine):
    results = engine.search("database", scope="council", limit=5)
    assert results.total_hits > 0
    assert "council" in results.by_category
    assert "libraries" not in results.by_category
    assert "code" not in results.by_category


def test_mcp_search_tool():
    req = {
        "jsonrpc": "2.0",
        "id": 101,
        "method": "tools/call",
        "params": {
            "name": "hallwright_search",
            "arguments": {
                "query": "jwt",
                "scope": "libraries",
                "limit": 3
            }
        }
    }
    resp = dispatch_request(req)
    assert resp["id"] == 101
    assert "result" in resp
    content = resp["result"]["content"]
    assert len(content) > 0
    parsed = json.loads(content[0]["text"])
    assert parsed["query"] == "jwt"
    assert parsed["total_hits"] > 0
    assert "libraries" in parsed["by_category"]


def test_search_web_offline_resilience(engine, monkeypatch):
    import urllib.request
    def mock_urlopen(*args, **kwargs):
        raise urllib.error.URLError("Simulated offline network failure")
    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    results = engine.search_web("FastAPI async", limit=5)
    assert isinstance(results, list)
    assert len(results) == 0  # Gracefully returned empty list without crashing


def test_search_web_html_extraction(engine, monkeypatch):
    import io
    sample_html = (
        '<div>'
        '<a class="result__a" href="/l/?kh=-1&uddg=https%3A%2F%2Ffastapi.tiangolo.com%2Fasync%2F">'
        'Concurrency and <b>async</b> / await - FastAPI</a>'
        '<a class="result__snippet">Modern versions of <b>Python</b> have intuitive async.</a>'
        '</div>'
    )
    class MockResponse:
        def read(self):
            return sample_html.encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: MockResponse())

    results = engine.search_web("FastAPI async", limit=1)
    assert len(results) == 1
    hit = results[0]
    assert hit.category == "web"
    assert "Concurrency and async / await - FastAPI" in hit.title
    assert "https://fastapi.tiangolo.com/async/" in hit.metadata["url"]
    assert "Modern versions of Python have intuitive async." in hit.snippet
    assert hit.score >= 80.0


def test_search_scope_web(engine, monkeypatch):
    import io
    sample_html = (
        '<a class="result__a" href="https://example.com/docs">Example Docs</a>'
        '<a class="result__snippet">Example technical documentation snippet.</a>'
    )
    class MockResponse:
        def read(self):
            return sample_html.encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: MockResponse())

    res = engine.search("FastAPI", scope="web", limit=3)
    assert res.scope == "web"
    assert res.total_hits == 1
    assert "web" in res.by_category
    assert "council" not in res.by_category

