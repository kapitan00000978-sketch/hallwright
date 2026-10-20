import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from web_healer import AutonomousWebHealer, HealingResult
from server import dispatch_request


@pytest.fixture
def healer():
    return AutonomousWebHealer(workspace_root=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_formulate_search_query_with_traceback(healer):
    raw_error = (
        'Traceback (most recent call last):\n'
        '  File "C:\\Users\\user\\app\\main.py", line 42, in <module>\n'
        '    import fastapi\n'
        'ModuleNotFoundError: No module named \'fastapi\''
    )
    query = healer.formulate_search_query(raw_error)
    assert "ModuleNotFoundError" in query
    assert "fastapi" in query
    assert "C:\\Users" not in query


def test_heal_defect_with_mocked_web(healer, monkeypatch):
    class MockSearchHit:
        def __init__(self, title, snippet, url):
            self.title = title
            self.snippet = snippet
            self.metadata = {"url": url}

    mock_hits = [
        MockSearchHit(
            title="FastAPI Installation Guide",
            snippet="Install fastapi via pip install fastapi uvicorn to resolve missing module.",
            url="https://fastapi.tiangolo.com/tutorial/"
        )
    ]

    monkeypatch.setattr(healer.search_engine, "search_web", lambda q, limit=3: mock_hits)

    res = healer.heal_defect("ModuleNotFoundError: No module named 'fastapi'", auto_record_memory=False)
    assert isinstance(res, HealingResult)
    assert "ModuleNotFoundError" in res.query
    assert len(res.web_references) == 1
    assert "FastAPI Installation Guide" in res.web_references[0]["title"]
    assert "https://fastapi.tiangolo.com/tutorial/" in res.web_references[0]["url"]
    assert "ModuleNotFoundError" in res.diagnosis


def test_heal_defect_records_to_memory(healer, monkeypatch):
    monkeypatch.setattr(healer.search_engine, "search_web", lambda q, limit=3: [])

    res = healer.heal_defect("ZeroDivisionError: division by zero", auto_record_memory=True)
    assert res.memory_recorded is True
    assert res.lesson_id is not None


def test_heal_from_traceback(healer, monkeypatch):
    monkeypatch.setattr(healer.search_engine, "search_web", lambda q, limit=3: [])

    tb = (
        'Traceback (most recent call last):\n'
        '  File "server.py", line 12, in handle\n'
        'ValueError: invalid literal for int() with base 10: \'abc\''
    )
    res = healer.heal_from_traceback(tb, auto_record=False)
    assert "ValueError" in res.query


def test_mcp_heal_error_tool():
    req = {
        "jsonrpc": "2.0",
        "id": 301,
        "method": "tools/call",
        "params": {
            "name": "hallwright_heal_error",
            "arguments": {
                "error": "TypeError: 'NoneType' object is not callable"
            }
        }
    }
    resp = dispatch_request(req)
    assert resp["id"] == 301
    assert "result" in resp
    content = resp["result"]["content"]
    parsed = json.loads(content[0]["text"])
    assert "query" in parsed
    assert "remediation_strategy" in parsed
