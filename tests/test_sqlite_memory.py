"""
Unit tests for the SQLite WAL-mode memory store (src/memory/store.py).
"""

import os
import tempfile
from src.memory.store import SqliteMemoryStore


def test_sqlite_store_initialization():
    """Verify that SqliteMemoryStore creates necessary tables and index."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        store = SqliteMemoryStore(db_path=db_path)
        assert os.path.exists(db_path)

        # Record a lesson
        success = store.record_lesson(
            lesson_id="test-001",
            category="security",
            pattern="raw sql execution",
            lesson="Always use parameterized queries.",
            auditor="Gabriel Frost",
            severity="CRITICAL"
        )
        assert success is True

        lessons = store.get_lessons(category="security")
        assert len(lessons) == 1
        assert lessons[0]["pattern"] == "raw sql execution"
        assert lessons[0]["auditor"] == "Gabriel Frost"


def test_sqlite_store_checkpoint_and_export():
    """Verify checkpoint persistence and JSON export."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        json_path = os.path.join(tmpdir, "exported.json")
        store = SqliteMemoryStore(db_path=db_path)

        # Save a checkpoint
        store.save_checkpoint(
            checkpoint_id="chk-100",
            session_id="sess-xyz",
            agent_name="claude-code",
            task="Refactoring user authentication",
            stopped_at_file="src/auth.py",
            stopped_at_line=45,
            status="IN_PROGRESS",
            extra_data={"milestones_completed": ["login", "token_refresh"]}
        )

        chk = store.get_latest_checkpoint()
        assert chk is not None
        assert chk["id"] == "chk-100"
        assert chk["agent_name"] == "claude-code"
        assert chk["stopped_at_file"] == "src/auth.py"
        assert chk["stopped_at_line"] == 45
        assert chk["extra_data"]["milestones_completed"] == ["login", "token_refresh"]

        # Record convention and test JSON export
        store.record_convention(
            conv_id="conv-01",
            category="styling",
            rule="No inline CSS styles; utilize CSS variables."
        )
        export_success = store.export_to_json(json_path)
        assert export_success is True
        assert os.path.exists(json_path)

        # Re-import into new store
        db_path2 = os.path.join(tmpdir, "test_memory_2.db")
        store2 = SqliteMemoryStore(db_path=db_path2)
        count = store2.sync_from_json(json_path)
        assert count >= 1
        convs = store2.get_conventions()
        assert any(c["id"] == "conv-01" for c in convs)


def test_sqlite_store_search_lessons():
    """Verify that SqliteMemoryStore searches lessons across tokens with ranking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        store = SqliteMemoryStore(db_path=db_path)

        store.record_lesson("lsn-1", "security", "sql injection via string format", "Use parameterized queries.", severity="CRITICAL")
        store.record_lesson("lsn-2", "performance", "slow unindexed join query", "Add index on foreign key columns.", severity="HIGH")
        store.record_lesson("lsn-3", "auth", "plain text password storage", "Use bcrypt hashing.", severity="CRITICAL")

        # 1. Search by token 'parameterized'
        res1 = store.search_lessons("parameterized")
        assert len(res1) == 1
        assert res1[0]["id"] == "lsn-1"

        # 2. Search by multiple tokens with severity ranking
        res2 = store.search_lessons("query")
        assert len(res2) == 2
        # Critical severity should rank first
        assert res2[0]["id"] == "lsn-1"
        assert res2[1]["id"] == "lsn-2"

        # 3. Search with category filter
        res3 = store.search_lessons("query", category="performance")
        assert len(res3) == 1
        assert res3[0]["id"] == "lsn-2"


def test_sqlite_store_sync_from_immune_system():
    """Verify that SqliteMemoryStore imports evolved vaccines from immune_system.json."""
    import json
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        immune_path = os.path.join(tmpdir, "immune_system.json")
        store = SqliteMemoryStore(db_path=db_path)

        immune_payload = {
            "vaccines": [
                {
                    "id": "vac-999",
                    "category": "runtime",
                    "error_signature": "ZeroDivisionError in billing calculation",
                    "web_solution": "Guard divisor against zero before dividing",
                    "guardrail_rule": "GUARD_DIVISORS"
                }
            ]
        }
        with open(immune_path, "w", encoding="utf-8") as f:
            json.dump(immune_payload, f)

        imported = store.sync_from_immune_system(immune_path)
        assert imported == 1

        lessons = store.get_lessons(category="runtime")
        assert len(lessons) == 1
        assert lessons[0]["id"] == "vac-999"
        assert lessons[0]["auditor"] == "ImmuneSystem"
        assert lessons[0]["severity"] == "CRITICAL"
        assert "GUARD_DIVISORS" in lessons[0]["lesson"]

