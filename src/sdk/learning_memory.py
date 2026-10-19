"""
Persistent Learning Memory Engine for Hallwright
Part of the Hallwright Autonomous Craftsmanship Protocol.

Records AI agent mistakes, successes, conventions, and past scar tissue
in `.hallwright/memory.json`, dynamically retrieving relevant lessons
to prevent repeated errors across sessions.
"""

import os
import json
import re
import tempfile
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

try:
    from src.memory.store import SqliteMemoryStore
except ImportError:
    try:
        from memory.store import SqliteMemoryStore
    except ImportError:
        SqliteMemoryStore = None

DEFAULT_MEMORY_PATH = os.path.join(".hallwright", "memory.json")

# Semantic domain synonym expansion mapping
SYNONYM_MAP: Dict[str, List[str]] = {
    "login": ["auth", "authentication", "session", "credential"],
    "signup": ["auth", "registration", "user"],
    "password": ["auth", "hash", "secret", "credential"],
    "jwt": ["auth", "token", "signature", "bearer"],
    "payment": ["stripe", "billing", "charge", "checkout", "idempotency"],
    "stripe": ["payment", "billing", "charge", "idempotency"],
    "money": ["payment", "finance", "billing"],
    "db": ["database", "sql", "query", "migration"],
    "sql": ["database", "query", "injection", "orm"],
    "postgres": ["database", "sql", "pool"],
    "mysql": ["database", "sql", "pool"],
    "sqlite": ["database", "sql"],
    "rest": ["api", "endpoint", "http", "route"],
    "fastapi": ["api", "endpoint", "route"],
    "express": ["api", "endpoint", "route"],
    "speed": ["performance", "latency", "cache", "slow"],
    "slow": ["performance", "latency", "bottleneck", "optimization"],
    "css": ["ui", "design", "style", "layout"],
    "frontend": ["ui", "design", "component", "react"],
    "ui": ["design", "frontend", "layout", "contrast"]
}


class LearningMemory:
    """
    Persistent learning memory manager for Hallwright AI coding assistants.
    """

    def __init__(self, memory_path: str = DEFAULT_MEMORY_PATH):
        self.memory_path = memory_path
        self._ensure_storage()
        db_dir = os.path.dirname(self.memory_path) or ".hallwright"
        self.db_path = os.path.join(db_dir, "memory.db")
        if SqliteMemoryStore:
            self.store = SqliteMemoryStore(db_path=self.db_path)
            if os.path.exists(self.memory_path):
                self.store.sync_from_json(self.memory_path)
        else:
            self.store = None

    def _ensure_storage(self) -> None:
        """Ensures that the memory directory and json file exist with valid schema."""
        dir_name = os.path.dirname(self.memory_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        if not os.path.exists(self.memory_path):
            initial_data = {
                "version": "2.0.0",
                "project": "Hallwright Engineering Core",
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                "scarTissue": [
                    {
                        "id": "scar-001",
                        "category": "auth",
                        "pattern": "plain password comparison",
                        "lesson": "Never use plain password equality or plaintext storage; always use constant-time comparison and bcrypt/argon2id hashing.",
                        "severity": "critical"
                    },
                    {
                        "id": "scar-002",
                        "category": "payment",
                        "pattern": "non-idempotent payment charge",
                        "lesson": "Always require and verify idempotency keys on payment transactions to prevent double charges.",
                        "severity": "critical"
                    },
                    {
                        "id": "scar-003",
                        "category": "database",
                        "pattern": "unindexed foreign key joins / N+1 loops",
                        "lesson": "Always batch queries and ensure index coverage on foreign keys to prevent table scans and N+1 query cascades.",
                        "severity": "high"
                    }
                ],
                "mistakes": [],
                "successes": [],
                "conventions": [
                    {
                        "id": "conv-001",
                        "category": "quality",
                        "rule": "100% test pass rate and pre-commit gatekeeper 100/100 score required before commit."
                    }
                ],
                "anti_patterns": [
                    {
                        "id": "anti-001",
                        "pattern": "bare exception suppression / empty catch",
                        "reason": "Silently swallows catastrophic exceptions, making bugs impossible to debug."
                    }
                ],
                "lessons": []
            }
            self._write_atomic(initial_data)

    def load_data(self) -> Dict[str, Any]:
        """Loads memory data safely from JSON."""
        if not os.path.exists(self.memory_path):
            self._ensure_storage()

        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure essential keys exist
                for key in ["scarTissue", "mistakes", "successes", "conventions", "anti_patterns", "lessons"]:
                    if key not in data:
                        data[key] = []
                return data
        except (json.JSONDecodeError, OSError):
            return {
                "version": "2.0.0",
                "scarTissue": [],
                "mistakes": [],
                "successes": [],
                "conventions": [],
                "anti_patterns": [],
                "lessons": []
            }

    def _write_atomic(self, data: Dict[str, Any]) -> None:
        """Writes JSON data atomically to prevent corruption."""
        dir_name = os.path.dirname(self.memory_path) or "."
        fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="hallwright_mem_", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.memory_path)
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as cleanup_err:
                    import logging
                    logging.debug("Failed to remove temp memory file: %s", cleanup_err)
            raise

    def get_lessons(self, task: str = "", category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant lessons, mistakes, and scar tissue matching the task or category.
        """
        data = self.load_data()
        all_items: List[Dict[str, Any]] = []

        # Combine items from scarTissue, mistakes, lessons, and anti_patterns
        for item in data.get("scarTissue", []):
            all_items.append({**item, "source": "scarTissue"})
        for item in data.get("mistakes", []):
            all_items.append({**item, "source": "mistake"})
        for item in data.get("lessons", []):
            all_items.append({**item, "source": "lesson"})
        for item in data.get("anti_patterns", []):
            all_items.append({
                "id": item.get("id"),
                "category": item.get("category", "code"),
                "pattern": item.get("pattern", ""),
                "lesson": f"Avoid anti-pattern: {item.get('pattern')}. {item.get('reason', '')}",
                "severity": "high",
                "source": "anti_pattern"
            })

        if not task and not category:
            return all_items[:limit]

        raw_tokens = set(re.findall(r"\b[a-z0-9_\-\.]{2,}\b", (task or "").lower()))
        task_tokens = set(raw_tokens)
        for t in raw_tokens:
            if t in SYNONYM_MAP:
                task_tokens.update(SYNONYM_MAP[t])
        scored_items = []

        for item in all_items:
            score = 0
            item_cat = (item.get("category") or "").lower()
            item_pattern = (item.get("pattern") or "").lower()
            item_lesson = (item.get("lesson") or "").lower()

            # Category filter/boost
            if category:
                if category.lower() in item_cat:
                    score += 5.0
                else:
                    continue  # Strict category filter if specified

            # Token overlap scoring
            for token in task_tokens:
                if token in item_cat:
                    score += 3.0
                if token in item_pattern:
                    score += 2.5
                if token in item_lesson:
                    score += 1.5

            # Severity boost
            sev = (item.get("severity") or "").lower()
            if sev == "critical":
                score += 2.0
            elif sev == "high":
                score += 1.0

            if score > 0:
                scored_items.append((score, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_items[:limit]]

    def record_learning(
        self,
        record_type: str,
        category: str,
        pattern: str,
        lesson: str,
        severity: str = "high"
    ) -> Dict[str, Any]:
        """
        Records a new learning experience into memory.json.
        record_type: 'mistake' | 'success' | 'convention' | 'anti_pattern' | 'lesson'
        """
        data = self.load_data()
        now_iso = datetime.now(timezone.utc).isoformat()
        clean_type = record_type.lower().strip()
        cat_clean = category.lower().strip()

        # Mapping to target array
        target_map = {
            "mistake": "mistakes",
            "success": "successes",
            "convention": "conventions",
            "anti_pattern": "anti_patterns",
            "lesson": "lessons",
            "scartissue": "scarTissue"
        }
        target_key = target_map.get(clean_type, "lessons")
        records = data.setdefault(target_key, [])

        # Check for duplicate by pattern and category
        for existing in records:
            if existing.get("category") == cat_clean and existing.get("pattern") == pattern:
                existing["lesson"] = lesson
                existing["severity"] = severity
                existing["updatedAt"] = now_iso
                data["lastUpdated"] = now_iso
                self._write_atomic(data)
                if self.store:
                    existing_id = existing.get("id") or f"lsn_{int(datetime.now(timezone.utc).timestamp()*1000)}"
                    if clean_type == "convention":
                        self.store.record_convention(existing_id, cat_clean, lesson)
                    else:
                        self.store.record_lesson(existing_id, cat_clean, pattern, lesson, severity=severity)
                return {
                    "status": "updated",
                    "id": existing.get("id"),
                    "category": cat_clean,
                    "target": target_key
                }

        # Generate unique ID
        rec_id = f"{clean_type[:3]}-{len(records) + 1:04d}"
        new_entry = {
            "id": rec_id,
            "category": cat_clean,
            "pattern": pattern,
            "lesson": lesson,
            "severity": severity,
            "recordedAt": now_iso
        }
        records.append(new_entry)
        data["lastUpdated"] = now_iso
        self._write_atomic(data)
        if self.store:
            if clean_type == "convention":
                self.store.record_convention(rec_id, cat_clean, lesson)
            else:
                self.store.record_lesson(rec_id, cat_clean, pattern, lesson, severity=severity)

        return {
            "status": "recorded",
            "id": rec_id,
            "category": cat_clean,
            "target": target_key,
            "total_records": len(records)
        }

    def format_warning_snippet(self, task: str) -> str:
        """
        Returns a ready-to-inject warning markdown block based on matching lessons.
        """
        lessons = self.get_lessons(task=task, limit=4)
        if not lessons:
            return ""

        lines = ["## ⚠️ PAST LESSONS & SCAR TISSUE (DO NOT REPEAT):"]
        for item in lessons:
            cat = item.get("category", "code").upper()
            lesson = item.get("lesson", "")
            lines.append(f"- **[{cat}]**: {lesson}")
        return "\n".join(lines)
