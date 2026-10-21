import sys
import os
import json
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk")))
from learning_memory import LearningMemory


def test_learning_memory_initialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_path = os.path.join(tmpdir, "test_memory.json")
        mem = LearningMemory(mem_path)
        data = mem.load_data()
        assert data["version"] == "2.0.0"
        assert len(data["scarTissue"]) >= 3
        assert len(data["conventions"]) >= 1


def test_learning_memory_get_lessons_matching():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_path = os.path.join(tmpdir, "test_memory.json")
        mem = LearningMemory(mem_path)
        # Search for auth lessons
        lessons = mem.get_lessons(task="Create password auth endpoint", limit=3)
        assert len(lessons) > 0
        categories = [l["category"] for l in lessons]
        assert "auth" in categories
        assert any("bcrypt" in l["lesson"] or "password" in l["lesson"] for l in lessons)


def test_learning_memory_record_and_retrieve():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_path = os.path.join(tmpdir, "test_memory.json")
        mem = LearningMemory(mem_path)
        
        # Record a new mistake
        rec = mem.record_learning(
            record_type="mistake",
            category="api",
            pattern="unbounded pagination query",
            lesson="Always limit query to max 100 items per page.",
            severity="high"
        )
        assert rec["status"] == "recorded"
        assert rec["category"] == "api"

        # Query it back
        results = mem.get_lessons(task="API pagination handler", limit=2)
        assert len(results) > 0
        matched = [r for r in results if "pagination" in r.get("pattern", "")]
        assert len(matched) == 1
        assert "100 items" in matched[0]["lesson"]


def test_learning_memory_deduplication():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_path = os.path.join(tmpdir, "test_memory.json")
        mem = LearningMemory(mem_path)

        # Record first time
        rec1 = mem.record_learning(
            record_type="mistake",
            category="payment",
            pattern="duplicate charge without idempotency",
            lesson="Always verify idempotency key.",
            severity="critical"
        )
        assert rec1["status"] == "recorded"

        # Record second time with updated lesson
        rec2 = mem.record_learning(
            record_type="mistake",
            category="payment",
            pattern="duplicate charge without idempotency",
            lesson="Updated: Always verify and lock idempotency key with Redis mutex.",
            severity="critical"
        )
        assert rec2["status"] == "updated"

        data = mem.load_data()
        payment_mistakes = [m for m in data["mistakes"] if m.get("category") == "payment"]
        assert len(payment_mistakes) == 1
        assert "Redis mutex" in payment_mistakes[0]["lesson"]


def test_learning_memory_warning_snippet():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_path = os.path.join(tmpdir, "test_memory.json")
        mem = LearningMemory(mem_path)
        snippet = mem.format_warning_snippet("payment transaction charge")
        assert "PAST LESSONS & SCAR TISSUE" in snippet
        assert "idempotency" in snippet.lower()


def test_learning_memory_synonym_expansion():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_path = os.path.join(tmpdir, "test_memory.json")
        mem = LearningMemory(mem_path)
        # Search using synonym 'login' which maps to 'auth'
        lessons = mem.get_lessons(task="User login flow", limit=3)
        assert len(lessons) > 0
        assert any(l["category"] == "auth" for l in lessons)


def test_learning_memory_uzbek_and_multilingual_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_path = os.path.join(tmpdir, "test_memory.json")
        mem = LearningMemory(mem_path)
        
        # 1. Uzbek query for password/auth
        auth_lessons = mem.get_lessons(task="parol tekshirish va kirish tizimi", limit=3)
        assert len(auth_lessons) > 0
        assert any(l["category"] == "auth" for l in auth_lessons)

        # 2. Uzbek query for payment/cart
        payment_lessons = mem.get_lessons(task="to'lov savat billing", limit=3)
        assert len(payment_lessons) > 0
        assert any(l["category"] == "payment" for l in payment_lessons)

        # 3. Uzbek query for database
        db_lessons = mem.get_lessons(task="baza jadval so'rovlar", limit=3)
        assert len(db_lessons) > 0
        assert any(l["category"] == "database" for l in db_lessons)


def test_learning_memory_immune_system_vaccine_sync():
    with tempfile.TemporaryDirectory() as tmpdir:
        hallwright_dir = os.path.join(tmpdir, ".hallwright")
        os.makedirs(hallwright_dir, exist_ok=True)
        mem_path = os.path.join(hallwright_dir, "memory.json")
        immune_path = os.path.join(hallwright_dir, "immune_system.json")

        immune_data = {
            "version": "1.0.0",
            "generation": 3,
            "vaccines": [
                {
                    "id": "vac-006",
                    "generation": 3,
                    "category": "runtime",
                    "error_signature": "TypeError: unexpected NoneType operation without typeguard",
                    "root_cause": "Unchecked None value passed to string method",
                    "web_solution": "Apply defensive None checking before invoking string operations",
                    "guardrail_rule": "ALWAYS_CHECK_NONE_BEFORE_METHOD_CALL"
                }
            ]
        }
        with open(immune_path, "w", encoding="utf-8") as f:
            json.dump(immune_data, f)

        mem = LearningMemory(mem_path)
        lessons = mem.get_lessons(task="TypeError NoneType typeguard", limit=3)
        assert len(lessons) > 0
        vaccine_entry = next((l for l in lessons if l.get("id") == "vac-006"), None)
        assert vaccine_entry is not None
        assert vaccine_entry["source"] == "vaccine"
        assert vaccine_entry["severity"] == "critical"
        assert "ALWAYS_CHECK_NONE_BEFORE_METHOD_CALL" in vaccine_entry["lesson"]


def test_learning_memory_workspace_root_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = LearningMemory(workspace_root=tmpdir)
        assert os.path.normpath(mem.memory_path) == os.path.normpath(os.path.join(tmpdir, ".hallwright", "memory.json"))
        data = mem.load_data()
        assert data["version"] == "2.0.0"
