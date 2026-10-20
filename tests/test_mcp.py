import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp")))
import server

def test_mcp_list_council():
    res = server.handle_list_council({})
    assert "masters" in res
    assert res["council_size"] == 64
    names = [m["name"] for m in res["masters"]]
    assert any("Marcus" in n for n in names)
    assert any("Diana" in n for n in names)
    assert any("Elena" in n for n in names)
    assert any("Gabriel" in n for n in names)

def test_mcp_get_persona():
    marcus = server.handle_get_persona({"profession": "software_architect"})
    assert "Marcus" in marcus["name"]
    assert "Systems Sovereign" in marcus["archetype"]
    assert len(marcus["criteria"]) > 0

def test_mcp_inspect_code_clean():
    clean_code = "def calculate_total(price, tax):\n    return price + (price * tax)\n"
    res = server.handle_inspect_code({"code": clean_code})
    assert res["status"] == "CERTIFIED"
    assert res["score"] == 100
    assert len(res["flaws"]) == 0

def test_mcp_inspect_code_flawed():
    flawed_code = "try:\n    pass\nexcept:\n    pass\n"
    res = server.handle_inspect_code({"code": flawed_code})
    assert res["status"] == "REJECTED"
    assert len(res["flaws"]) > 0

def test_mcp_initialize_schema():
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    res = server.dispatch_request(req)
    assert res["result"]["protocolVersion"] == "2024-11-05"
    assert res["result"]["serverInfo"]["name"] in ("hallwright-mcp", "hallwright-mcp")

def test_mcp_tools_list_distilled_canonical_tools():
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    res = server.dispatch_request(req)
    tool_names = [t["name"] for t in res["result"]["tools"]]
    assert len(tool_names) == 15
    assert "hallwright_inspect_code" in tool_names
    assert "hallwright_get_persona" in tool_names
    assert "hallwright_list_council" in tool_names
    assert "hallwright_recall_memory" in tool_names
    assert "hallwright_select_masters" in tool_names
    assert "hallwright_get_lessons" in tool_names
    assert "hallwright_record_learning" in tool_names
    assert "hallwright_inject_prompt" in tool_names
    assert "hallwright_list_guilds" in tool_names
    assert "hallwright_resume_continuity" in tool_names
    assert "hallwright_save_checkpoint" in tool_names
    assert "hallwright_get_library" in tool_names
    assert "hallwright_review_code" in tool_names
    assert "hallwright_search" in tool_names
    assert "hallwright_optimize_prompt" in tool_names
    # Verify legacy artisan_* tools are NOT duplicated in tools/list
    assert not any(t.startswith("artisan_") for t in tool_names)

def test_mcp_canonical_hallwright_tools_dispatch():
    # Direct invocation using canonical hallwright_ prefix
    req = {
        "jsonrpc": "2.0",
        "id": 15,
        "method": "tools/call",
        "params": {
            "name": "hallwright_inspect_code",
            "arguments": {"code": "def valid(): return 42\n"}
        }
    }
    res = server.dispatch_request(req)
    assert "result" in res
    content = json.loads(res["result"]["content"][0]["text"])
    assert content["status"] == "CERTIFIED"
    assert content["score"] == 100

def test_mcp_list_guilds_via_dispatch():
    req = {
        "jsonrpc": "2.0",
        "id": 14,
        "method": "tools/call",
        "params": {
            "name": "artisan_list_guilds",
            "arguments": {}
        }
    }
    res = server.dispatch_request(req)
    assert "result" in res
    content = json.loads(res["result"]["content"][0]["text"])
    assert content["guilds_count"] == 8
    assert len(content["guilds"]) == 8
    names = [g["name"] for g in content["guilds"]]
    assert any("Software" in n for n in names)
    assert any("Cybersecurity" in n for n in names)

def test_mcp_select_masters_via_dispatch():
    req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "artisan_select_masters",
            "arguments": {"task": "Build FastAPI auth endpoint with bcrypt", "limit": 2}
        }
    }
    res = server.dispatch_request(req)
    assert "result" in res
    content = json.loads(res["result"]["content"][0]["text"])
    assert content["count"] == 2
    keys = [m["master_key"] for m in content["selected_masters"]]
    assert "cyber_security_auditor" in keys

def test_mcp_get_lessons_via_dispatch():
    req = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "artisan_get_lessons",
            "arguments": {"task": "auth password login", "limit": 3}
        }
    }
    res = server.dispatch_request(req)
    assert "result" in res
    content = json.loads(res["result"]["content"][0]["text"])
    assert "lessons" in content
    assert len(content["lessons"]) > 0

def test_mcp_record_learning_via_dispatch():
    req = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "artisan_record_learning",
            "arguments": {
                "type": "mistake",
                "category": "api",
                "pattern": "unbounded result payload",
                "lesson": "Always enforce pagination limits.",
                "severity": "high"
            }
        }
    }
    res = server.dispatch_request(req)
    assert "result" in res
    content = json.loads(res["result"]["content"][0]["text"])
    assert content["status"] in ["recorded", "updated"]

def test_mcp_inject_prompt_via_dispatch():
    req = {
        "jsonrpc": "2.0",
        "id": 13,
        "method": "tools/call",
        "params": {
            "name": "artisan_inject_prompt",
            "arguments": {"task": "Create Stripe checkout subscription endpoint", "files": ["checkout.py"]}
        }
    }
    res = server.dispatch_request(req)
    assert "result" in res
    content = json.loads(res["result"]["content"][0]["text"])
    assert "prompt" in content
    assert content["approx_tokens"] < 2000
    assert "ZERO STUBS" in content["prompt"]

def test_mcp_inspect_code_catches_secrets_and_fixme():
    dangerous_code = """
    # FIXME: implement this later
    password = "hunter2"
    anthropic_key = "sk-ant-api03-abcdef123456789012345678"
    """
    res = server.handle_inspect_code({"code": dangerous_code})
    assert res["status"] == "REJECTED"
    assert len(res["flaws"]) >= 2
    flaw_text = " ".join(res["flaws"])
    assert "stub" in flaw_text.lower() or "todo" in flaw_text.lower() or "fixme" in flaw_text.lower()
    assert "secret" in flaw_text.lower() or "password" in flaw_text.lower() or "key" in flaw_text.lower()

def test_mcp_unknown_tool_returns_jsonrpc_32601_error():
    req = {
        "jsonrpc": "2.0",
        "id": 42,
        "method": "tools/call",
        "params": {
            "name": "non_existent_tool",
            "arguments": {}
        }
    }
    res = server.dispatch_request(req)
    assert "error" in res
    assert res["error"]["code"] == -32601
    assert "Tool not found" in res["error"]["message"]
    assert "result" not in res

def test_mcp_unknown_method_returns_jsonrpc_32601_error():
    req = {
        "jsonrpc": "2.0",
        "id": 43,
        "method": "unknown/method",
        "params": {}
    }
    res = server.dispatch_request(req)
    assert "error" in res
    assert res["error"]["code"] == -32601
    assert "Method not found" in res["error"]["message"]


def test_mcp_missing_required_argument_returns_32602_error():
    # artisan_inspect_code requires 'code' parameter
    req = {
        "jsonrpc": "2.0",
        "id": 50,
        "method": "tools/call",
        "params": {
            "name": "artisan_inspect_code",
            "arguments": {}
        }
    }
    res = server.dispatch_request(req)
    assert "error" in res
    assert res["error"]["code"] == -32602
    assert "Missing required parameter 'code'" in res["error"]["message"]


def test_mcp_invalid_argument_type_returns_32602_error():
    # 'limit' in artisan_select_masters must be an integer, not a string or boolean
    req = {
        "jsonrpc": "2.0",
        "id": 51,
        "method": "tools/call",
        "params": {
            "name": "artisan_select_masters",
            "arguments": {"task": "Build auth", "limit": "not_an_int"}
        }
    }
    res = server.dispatch_request(req)
    assert "error" in res
    assert res["error"]["code"] == -32602
    assert "must be an integer" in res["error"]["message"]


def test_mcp_invalid_enum_argument_returns_32602_error():
    # 'type' in artisan_record_learning has strict enum: ["mistake", "success", "convention", "anti_pattern", "lesson"]
    req = {
        "jsonrpc": "2.0",
        "id": 52,
        "method": "tools/call",
        "params": {
            "name": "artisan_record_learning",
            "arguments": {
                "type": "invalid_junk_type",
                "category": "api",
                "pattern": "something",
                "lesson": "something else"
            }
        }
    }
    res = server.dispatch_request(req)
    assert "error" in res
    assert res["error"]["code"] == -32602
    assert "has invalid value" in res["error"]["message"]


def test_mcp_continuity_tools():
    # 1. Save checkpoint via MCP
    req_save = {
        "jsonrpc": "2.0",
        "id": 60,
        "method": "tools/call",
        "params": {
            "name": "artisan_save_checkpoint",
            "arguments": {
                "task": "MCP Integration task",
                "agent": "mcp-claude",
                "stopped_at_file": "server.py",
                "stopped_at_line": 50,
                "completed_milestones": ["MCP Handlers"],
                "pending_milestones": ["Verification"]
            }
        }
    }
    res_save = server.dispatch_request(req_save)
    assert "result" in res_save
    content_save = json.loads(res_save["result"]["content"][0]["text"])
    assert content_save["saved"] is True
    assert content_save["task"] == "MCP Integration task"

    # 2. Resume continuity via MCP
    req_res = {
        "jsonrpc": "2.0",
        "id": 61,
        "method": "tools/call",
        "params": {
            "name": "artisan_resume_continuity",
            "arguments": {}
        }
    }
    res_resume = server.dispatch_request(req_res)
    assert "result" in res_resume
    content_resume = json.loads(res_resume["result"]["content"][0]["text"])
    assert content_resume["status"] == "ACTIVE"
    assert "mcp-claude" in content_resume["resumption_prompt"]


def test_mcp_get_library_tool():
    # 1. List all domains
    req_all = {
        "jsonrpc": "2.0",
        "id": 62,
        "method": "tools/call",
        "params": {
            "name": "artisan_get_library",
            "arguments": {}
        }
    }
    res_all = server.dispatch_request(req_all)
    assert "result" in res_all
    content_all = json.loads(res_all["result"]["content"][0]["text"])
    assert "architecture" in content_all
    assert "security" in content_all

    # 2. Get specific domain
    req_sec = {
        "jsonrpc": "2.0",
        "id": 63,
        "method": "tools/call",
        "params": {
            "name": "artisan_get_library",
            "arguments": {"domain": "security"}
        }
    }
    res_sec = server.dispatch_request(req_sec)
    assert "result" in res_sec
    content_sec = json.loads(res_sec["result"]["content"][0]["text"])
    assert "Defensive Security" in content_sec["title"]


def test_mcp_review_code_tool():
    clean_code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    req_rev = {
        "jsonrpc": "2.0",
        "id": 64,
        "method": "tools/call",
        "params": {
            "name": "artisan_review_code",
            "arguments": {
                "code": clean_code,
                "filename": "math_lib.py"
            }
        }
    }
    res_rev = server.dispatch_request(req_rev)
    assert "result" in res_rev
    content_rev = json.loads(res_rev["result"]["content"][0]["text"])
    assert "score" in content_rev
    assert content_rev["passed"] is True



