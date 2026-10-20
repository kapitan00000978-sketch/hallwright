"""
Tests for Hallwright Unified CLI (hallwright_cli.py).
Verifies stack detection, 1-click initialization, audit, fix, status, doctor, and memory.
"""

import os
import sys
import json
import tempfile
import shutil
import argparse
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import hallwright_cli


def test_detect_tech_stack_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "pyproject.toml"), "w", encoding="utf-8") as f:
            f.write("[project]\nname = 'test'\n")
        stacks = hallwright_cli.detect_tech_stack(tmpdir)
        assert "Python" in stacks


def test_detect_tech_stack_node_and_next():
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_data = {
            "name": "web-app",
            "dependencies": {"next": "^14.0.0", "react": "^18.0.0"}
        }
        with open(os.path.join(tmpdir, "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg_data, f)
        with open(os.path.join(tmpdir, "tsconfig.json"), "w", encoding="utf-8") as f:
            f.write("{}")

        stacks = hallwright_cli.detect_tech_stack(tmpdir)
        assert "Node.js / JavaScript" in stacks
        assert "Next.js" in stacks
        assert "TypeScript" in stacks


def test_detect_tech_stack_go_rust_java():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "go.mod"), "w", encoding="utf-8") as f:
            f.write("module test\n")
        with open(os.path.join(tmpdir, "Cargo.toml"), "w", encoding="utf-8") as f:
            f.write("[package]\nname = 'test'\n")
        with open(os.path.join(tmpdir, "pom.xml"), "w", encoding="utf-8") as f:
            f.write("<project></project>\n")

        stacks = hallwright_cli.detect_tech_stack(tmpdir)
        assert "Go" in stacks
        assert "Rust" in stacks
        assert "Java" in stacks


def test_detect_tech_stack_universal():
    with tempfile.TemporaryDirectory() as tmpdir:
        stacks = hallwright_cli.detect_tech_stack(tmpdir)
        assert "Universal / Multi-Language" in stacks


def test_copy_safe_files_and_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "src.txt")
        dst_file = os.path.join(tmpdir, "subdir", "dst.txt")
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("hallwright")

        assert hallwright_cli.copy_safe(src_file, dst_file)
        assert os.path.exists(dst_file)

        # Test non-existent src
        assert not hallwright_cli.copy_safe(os.path.join(tmpdir, "none.txt"), dst_file)

        # Test preserve existing
        with open(dst_file, "w", encoding="utf-8") as f:
            f.write("original")
        assert not hallwright_cli.copy_safe(src_file, dst_file, preserve_existing=True)
        with open(dst_file, "r", encoding="utf-8") as f:
            assert f.read() == "original"


def test_cmd_init_in_clean_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        args = argparse.Namespace(dir=tmpdir, no_hook=True)
        ret = hallwright_cli.cmd_init(args)
        assert ret == 0

        # Memory ledger initialized
        mem_file = os.path.join(tmpdir, ".hallwright", "memory.json")
        assert os.path.exists(mem_file)
        with open(mem_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["version"] == "2.0.0"

        # Protocol and canonical agent rule files copied
        assert os.path.exists(os.path.join(tmpdir, "AGENTS.md"))
        assert os.path.exists(os.path.join(tmpdir, "CLAUDE.md"))
        assert os.path.exists(os.path.join(tmpdir, ".cursorrules"))
        assert os.path.exists(os.path.join(tmpdir, ".windsurfrules"))
        assert os.path.exists(os.path.join(tmpdir, ".clinerules"))
        assert os.path.exists(os.path.join(tmpdir, ".github", "copilot-instructions.md"))

        # Root directory is clean (zero unnecessary markdown clutter by default)
        assert not os.path.exists(os.path.join(tmpdir, "HERMES.md"))
        assert not os.path.exists(os.path.join(tmpdir, "CODEX.md"))
        assert not os.path.exists(os.path.join(tmpdir, "OPENCLAW.md"))
        assert not os.path.exists(os.path.join(tmpdir, "OPENCODE.md"))
        assert not os.path.exists(os.path.join(tmpdir, "PIE.md"))
        assert not os.path.exists(os.path.join(tmpdir, "KIMI.md"))
        assert not os.path.exists(os.path.join(tmpdir, "KILO.md"))


def test_cmd_init_with_all_agents():
    with tempfile.TemporaryDirectory() as tmpdir:
        args = argparse.Namespace(dir=tmpdir, no_hook=True, all_agents=True)
        ret = hallwright_cli.cmd_init(args)
        assert ret == 0
        assert os.path.exists(os.path.join(tmpdir, "AGENTS.md"))
        assert os.path.exists(os.path.join(tmpdir, "HERMES.md"))
        assert os.path.exists(os.path.join(tmpdir, "CODEX.md"))
        assert os.path.exists(os.path.join(tmpdir, "KIMI.md"))


def test_cmd_init_preserves_existing_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_agents = os.path.join(tmpdir, "AGENTS.md")
        custom_claude = os.path.join(tmpdir, "CLAUDE.md")
        with open(custom_agents, "w", encoding="utf-8") as f:
            f.write("# MY CUSTOM AGENTS RULES")
        with open(custom_claude, "w", encoding="utf-8") as f:
            f.write("# MY CUSTOM CLAUDE RULES")

        args = argparse.Namespace(dir=tmpdir, no_hook=True, force=False, backup=False)
        ret = hallwright_cli.cmd_init(args)
        assert ret == 0

        # Existing files must be preserved by default
        with open(custom_agents, "r", encoding="utf-8") as f:
            assert f.read() == "# MY CUSTOM AGENTS RULES"
        with open(custom_claude, "r", encoding="utf-8") as f:
            assert f.read() == "# MY CUSTOM CLAUDE RULES"
        assert not os.path.exists(custom_agents + ".bak")


def test_cmd_init_backup_creates_bak():
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_agents = os.path.join(tmpdir, "AGENTS.md")
        with open(custom_agents, "w", encoding="utf-8") as f:
            f.write("# MY PREVIOUS INSTRUCTIONS")

        args = argparse.Namespace(dir=tmpdir, no_hook=True, force=False, backup=True)
        ret = hallwright_cli.cmd_init(args)
        assert ret == 0

        # .bak file must be created with original contents
        assert os.path.exists(custom_agents + ".bak")
        with open(custom_agents + ".bak", "r", encoding="utf-8") as f:
            assert f.read() == "# MY PREVIOUS INSTRUCTIONS"
        with open(custom_agents, "r", encoding="utf-8") as f:
            assert "# MY PREVIOUS INSTRUCTIONS" not in f.read()


def test_cmd_init_force_overwrites():
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_agents = os.path.join(tmpdir, "AGENTS.md")
        with open(custom_agents, "w", encoding="utf-8") as f:
            f.write("# TO BE OVERWRITTEN")

        args = argparse.Namespace(dir=tmpdir, no_hook=True, force=True, backup=False)
        ret = hallwright_cli.cmd_init(args)
        assert ret == 0

        with open(custom_agents, "r", encoding="utf-8") as f:
            content = f.read()
            assert "# TO BE OVERWRITTEN" not in content
            assert "HALLWRIGHT" in content or "AGENT" in content



def test_cmd_status():
    args = argparse.Namespace()
    ret = hallwright_cli.cmd_status(args)
    assert ret == 0


def test_cmd_doctor():
    args = argparse.Namespace(strict=False)
    ret = hallwright_cli.cmd_doctor(args)
    assert ret == 0


def test_cmd_doctor_isolated_environment():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize project in tmpdir to test fully configured state
        args_init = argparse.Namespace(dir=tmpdir, no_hook=True, force=True, backup=False)
        hallwright_cli.cmd_init(args_init)

        args = argparse.Namespace(dir=tmpdir, strict=False)
        ret = hallwright_cli.cmd_doctor(args)
        assert ret == 0


def test_cmd_memory_list_and_record():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_file = os.path.join(tmpdir, ".hallwright", "memory.json")
        os.makedirs(os.path.dirname(mem_file), exist_ok=True)
        with open(mem_file, "w", encoding="utf-8") as f:
            json.dump({
                "version": "2.0.0",
                "lessons_learned": [],
                "conventions": [],
                "recorded_scar_tissue": []
            }, f)

        with patch("learning_memory.DEFAULT_MEMORY_PATH", mem_file):
            # Record a new lesson
            args_record = argparse.Namespace(
                record="mistake:auth:jwt_none_alg:Always verify algorithm is HS256/RS256",
                search=None,
                limit=10
            )
            ret_record = hallwright_cli.cmd_memory(args_record)
            assert ret_record == 0

            # List and verify it appears
            args_search = argparse.Namespace(record=None, search="jwt", limit=10)
            ret_search = hallwright_cli.cmd_memory(args_search)
            assert ret_search == 0


def test_cmd_audit_json_output(capsys):
    args = argparse.Namespace(staged=False, vibe=True, json=True)
    ret = hallwright_cli.cmd_audit(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "score" in data
    assert "passed" in data
    assert ret == 0


def test_cmd_context_output(capsys):
    args = argparse.Namespace(task="Build secure user login with JWT", files=[], json=False)
    ret = hallwright_cli.cmd_context(args)
    captured = capsys.readouterr()
    assert ret == 0
    assert "DYNAMIC CONTEXT" in captured.out
    assert "Context Optimization" in captured.out


def test_cmd_context_json(capsys):
    args = argparse.Namespace(task="Database connection pooling", files=[], json=True)
    ret = hallwright_cli.cmd_context(args)
    captured = capsys.readouterr()
    assert ret == 0
    data = json.loads(captured.out)
    assert "prompt" in data
    assert "selected_masters" in data


def test_cmd_metrics():
    args = argparse.Namespace()
    ret = hallwright_cli.cmd_metrics(args)
    assert ret == 0


def test_cmd_agents():
    args = argparse.Namespace(register=None, release=None, files=[])
    ret = hallwright_cli.cmd_agents(args)
    assert ret == 0


def test_cmd_mutate_json_output(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        target_py = os.path.join(tmpdir, "calc.py")
        test_py = os.path.join(tmpdir, "test_calc.py")
        with open(target_py, "w", encoding="utf-8") as f:
            f.write("def add(a, b):\n    return a + b\n")
        with open(test_py, "w", encoding="utf-8") as f:
            f.write("from calc import add\ndef test_add():\n    assert add(1, 2) == 3\n")

        args = argparse.Namespace(
            target=target_py,
            test=test_py,
            limit=2,
            json=True
        )
        ret = hallwright_cli.cmd_mutate(args)
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "target_file" in data
        assert "mutation_score" in data
        assert "total_mutants" in data


def test_cmd_review_clean_files(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        sample = os.path.join(tmpdir, "clean.py")
        with open(sample, "w", encoding="utf-8") as f:
            f.write("def hello():\n    return 'world'\n")

        args = argparse.Namespace(
            files=[sample],
            diff=False,
            staged=False,
            commit=None,
            markdown=False,
            json=False,
            threshold=85.0
        )
        ret = hallwright_cli.cmd_review(args)
        assert ret == 0
        captured = capsys.readouterr()
        assert "APPROVED_FOR_PRODUCTION" in captured.out


def test_cmd_review_json_output(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        sample = os.path.join(tmpdir, "vuln.py")
        with open(sample, "w", encoding="utf-8") as f:
            f.write("import os\ndef run(c):\n    os.system(c)\n")

        args = argparse.Namespace(
            files=[sample],
            diff=False,
            staged=False,
            commit=None,
            markdown=False,
            json=True,
            threshold=85.0
        )
        ret = hallwright_cli.cmd_review(args)
        assert ret == 1
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["passed"] is False
        assert data["verdict"] == "VETO_REVISION_REQUIRED"
        assert len(data["findings"]) >= 1


def test_cmd_swarm_plan_output(capsys):
    args = argparse.Namespace(
        task="Build high-performance database caching layer",
        files=["cache.py"],
        plan=True,
        json=False
    )
    ret = hallwright_cli.cmd_swarm(args)
    assert ret == 0
    captured = capsys.readouterr()
    assert "MULTI-AGENT SWARM ORCHESTRATOR" in captured.out
    assert "hallwright-architect" in captured.out


def test_cmd_swarm_json_output(capsys):
    args = argparse.Namespace(
        task="Write documentation and README for payment API",
        files=["README.md"],
        plan=False,
        json=True
    )
    ret = hallwright_cli.cmd_swarm(args)
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "stages_count" in data
    assert "stages" in data
    assert data["status"] == "SWARM_PIPELINE_READY"


def test_cmd_checkpoint_and_resume(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            # 1. Record checkpoint
            cp_args = argparse.Namespace(
                task="Test task execution",
                agent="claude-agent",
                file="main.py",
                line=25,
                completed="Setup complete",
                next="Add tests",
                decision="Use SQLite",
                status="IN_PROGRESS",
                no_continuity=False,
            )
            ret_cp = hallwright_cli.cmd_checkpoint(cp_args)
            assert ret_cp == 0
            captured = capsys.readouterr()
            assert "Checkpoint saved successfully" in captured.out

            # 2. Resume session
            res_args = argparse.Namespace(
                no_continuity=False,
                json=True,
            )
            ret_res = hallwright_cli.cmd_resume(res_args)
            assert ret_res == 0
            captured_res = capsys.readouterr()
            data = json.loads(captured_res.out)
            assert data["last_agent"] == "claude-agent"
            assert data["last_task"] == "Test task execution"
            assert data["stopped_at_file"] == "main.py"
        finally:
            os.chdir(orig_cwd)


def test_cmd_lib_list_and_info(capsys):
    # 1. List
    list_args = argparse.Namespace(
        action="list",
        json=True,
    )
    ret_list = hallwright_cli.cmd_lib(list_args)
    assert ret_list == 0
    captured = capsys.readouterr()
    domains = json.loads(captured.out)
    assert "architecture" in domains
    assert "security" in domains

    # 2. Info
    info_args = argparse.Namespace(
        action="info",
        domain="security",
        json=True,
    )
    ret_info = hallwright_cli.cmd_lib(info_args)
    assert ret_info == 0
    captured_info = capsys.readouterr()
    sec_info = json.loads(captured_info.out)
    assert sec_info["title"] == "Defensive Security & Zero-Trust Guards"


def test_cmd_3d(capsys, monkeypatch):
    import webbrowser
    opened_urls = []
    monkeypatch.setattr(webbrowser, "open", lambda url: opened_urls.append(url))
    args = argparse.Namespace()
    ret = hallwright_cli.cmd_3d(args)
    assert ret == 0
    captured = capsys.readouterr()
    assert "3D SPATIAL DASHBOARD" in captured.out
    assert len(opened_urls) == 1
    assert "dashboard_3d.html" in opened_urls[0] or "127.0.0.1" in opened_urls[0]


def test_cmd_compress(capsys, tmp_path):
    f = tmp_path / "test_file.py"
    f.write_text("# Redundant comment\nx = 10\n# Another comment\n", encoding="utf-8")
    args = argparse.Namespace(
        path=str(f),
        in_place=False,
        json=True,
        ext="",
    )
    ret = hallwright_cli.cmd_compress(args)
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["files_processed"] == 1
    assert data["total_tokens_saved"] > 0
    assert data["total_comments_removed"] >= 2


def test_cmd_arena(capsys):
    args = argparse.Namespace(
        json=True,
        no_evolve=False,
    )
    ret = hallwright_cli.cmd_arena(args)
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "defense_score" in data
    assert data["defense_score"] >= 90
    assert len(data["rounds"]) >= 4


def test_cmd_daemon_once(capsys):
    args = argparse.Namespace(
        once=True,
        interval=1.0,
        no_heal=False,
    )
    ret = hallwright_cli.cmd_daemon(args)
    assert ret == 0
    captured = capsys.readouterr()
    assert "HALLWRIGHT WATCHER DAEMON" in captured.out


def test_cmd_tier_status_and_switch(capsys):
    # Test status json
    args_status = argparse.Namespace(
        level=None,
        status=True,
        json=True,
    )
    ret_status = hallwright_cli.cmd_tier(args_status)
    assert ret_status == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "active_tier" in data
    assert len(data["available_tiers"]) == 3

    # Test switch to tier 3
    args_switch = argparse.Namespace(
        level=3,
        status=False,
        json=True,
    )
    ret_switch = hallwright_cli.cmd_tier(args_switch)
    assert ret_switch == 0
    captured_sw = capsys.readouterr()
    data_sw = json.loads(captured_sw.out)
    assert data_sw["tier"] == 3
    assert data_sw["full_access"] is True


def test_cmd_skill_list_and_run(capsys):
    # Test skill list
    args_list = argparse.Namespace(
        action="list",
        name=None,
        target=None,
        json=True
    )
    ret_list = hallwright_cli.cmd_skill(args_list)
    assert ret_list == 0
    captured = capsys.readouterr()
    skills = json.loads(captured.out)
    assert "craftsman-evaluator" in skills
    assert "tier-3-sovereign" in skills

    # Test skill run tier-3-sovereign
    args_run = argparse.Namespace(
        action="run",
        name="tier-3-sovereign",
        target=None,
        json=True
    )
    ret_run = hallwright_cli.cmd_skill(args_run)
    assert ret_run == 0
    captured_run = capsys.readouterr()
    data_run = json.loads(captured_run.out)
    assert data_run["status"] == "ACTIVATED"
    assert data_run["tier"] == 3


def test_cmd_web_search_and_docs(capsys):
    # Test web search
    args_search = argparse.Namespace(
        action="search",
        query="fastapi uvicorn",
        limit=2,
        json=True
    )
    ret_s = hallwright_cli.cmd_web(args_search)
    assert ret_s == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["query"] == "fastapi uvicorn"
    assert len(data["hits"]) >= 1

    # Test web docs
    args_docs = argparse.Namespace(
        action="docs",
        query="python",
        topic="sqlite3",
        limit=2,
        json=True
    )
    ret_d = hallwright_cli.cmd_web(args_docs)
    assert ret_d == 0
    captured_d = capsys.readouterr()
    data_d = json.loads(captured_d.out)
    assert data_d["technology"] == "python"
    assert len(data_d["hits"]) >= 1


def test_cmd_sovereign_loop(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        args = argparse.Namespace(
            task="Build fast session token manager",
            output_dir=tmpdir,
            skip_web=True,
            json=True
        )
        ret = hallwright_cli.cmd_sovereign(args)
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "SOVEREIGN_EXECUTION_COMPLETED"
        assert len(data["steps"]) >= 5
        assert any(s["name"] == "11-Titan Swarm AgentMesh Generation" for s in data["steps"])
        assert os.path.exists(os.path.join(tmpdir, "core_service.py"))
        assert os.path.exists(os.path.join(tmpdir, "index.html"))
