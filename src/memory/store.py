"""
Concurrency-Safe SQLite Storage Engine for Hallwright / Hallwright Memory.

Replaces fragile concurrent JSON file rewrites with ACID SQLite transactions
operating in WAL (Write-Ahead Logging) mode with automatic retry handling,
while preserving bidirectional synchronization with git-versioned JSON ledgers.
"""

import os
import json
import time
import sqlite3
from contextlib import contextmanager
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("hallwright.memory.store")

DEFAULT_DB_PATH = os.path.join(".hallwright", "memory.db")


class SqliteMemoryStore:
    """Thread-safe and process-safe persistent storage engine using SQLite WAL mode."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """Creates a SQLite connection with WAL mode and ensures cleanup upon exit."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            yield conn
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Initializes tables and indices if not already present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    pattern TEXT NOT NULL,
                    lesson TEXT NOT NULL,
                    auditor TEXT DEFAULT 'Hallwright',
                    severity TEXT DEFAULT 'MEDIUM',
                    created_at REAL NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conventions (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    rule TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    task TEXT NOT NULL,
                    stopped_at_file TEXT,
                    stopped_at_line INTEGER,
                    status TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_sessions (
                    session_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    active_files_json TEXT NOT NULL,
                    registered_at REAL NOT NULL,
                    last_heartbeat REAL NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_lessons_cat ON lessons(category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_updated ON checkpoints(updated_at DESC);")
            conn.commit()

    # ---------------------------------------------------------
    # Lessons operations
    # ---------------------------------------------------------
    def record_lesson(
        self,
        lesson_id: str,
        category: str,
        pattern: str,
        lesson: str,
        auditor: str = "Hallwright",
        severity: str = "MEDIUM"
    ) -> bool:
        """Records a new lesson atomically."""
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO lessons (id, category, pattern, lesson, auditor, severity, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (lesson_id, category, pattern, lesson, auditor, severity, now))
            conn.commit()
            return True

    def get_lessons(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves recorded lessons, optionally filtered by category."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("""
                    SELECT id, category, pattern, lesson, auditor, severity, created_at
                    FROM lessons WHERE category = ? ORDER BY created_at DESC LIMIT ?;
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT id, category, pattern, lesson, auditor, severity, created_at
                    FROM lessons ORDER BY created_at DESC LIMIT ?;
                """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # ---------------------------------------------------------
    # Conventions operations
    # ---------------------------------------------------------
    def record_convention(self, conv_id: str, category: str, rule: str) -> bool:
        """Records a workspace coding convention atomically."""
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO conventions (id, category, rule, created_at)
                VALUES (?, ?, ?, ?);
            """, (conv_id, category, rule, now))
            conn.commit()
            return True

    def get_conventions(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves recorded conventions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT id, category, rule, created_at FROM conventions WHERE category = ?;", (category,))
            else:
                cursor.execute("SELECT id, category, rule, created_at FROM conventions ORDER BY created_at ASC;")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # ---------------------------------------------------------
    # Checkpoints operations
    # ---------------------------------------------------------
    def save_checkpoint(
        self,
        checkpoint_id: str,
        session_id: str,
        agent_name: str,
        task: str,
        stopped_at_file: Optional[str] = None,
        stopped_at_line: Optional[int] = None,
        status: str = "IN_PROGRESS",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Atomically saves or updates an agent continuity checkpoint."""
        now = time.time()
        payload = extra_data or {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO checkpoints
                (id, session_id, agent_name, task, stopped_at_file, stopped_at_line, status, data_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                checkpoint_id, session_id, agent_name, task,
                stopped_at_file, stopped_at_line, status, json.dumps(payload), now
            ))
            conn.commit()
            return True

    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Returns the most recent continuity checkpoint across all agents."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, session_id, agent_name, task, stopped_at_file, stopped_at_line, status, data_json, updated_at
                FROM checkpoints ORDER BY updated_at DESC LIMIT 1;
            """)
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            try:
                res["extra_data"] = json.loads(res.pop("data_json"))
            except (json.JSONDecodeError, KeyError):
                res["extra_data"] = {}
            return res

    # ---------------------------------------------------------
    # Bidirectional JSON Synchronization
    # ---------------------------------------------------------
    def sync_from_json(self, json_path: str) -> int:
        """Seeds SQLite database from an existing .hallwright/memory.json file."""
        if not os.path.exists(json_path):
            return 0
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to read json memory for sync: {e}")
            return 0

        imported = 0
        raw_lessons = (
            data.get("lessons_learned", []) +
            data.get("recorded_scar_tissue", []) +
            data.get("scarTissue", []) +
            data.get("mistakes", []) +
            data.get("lessons", [])
        )
        for item in raw_lessons:
            lid = item.get("id") or f"lsn_{int(time.time()*1000)}"
            cat = item.get("category", "general")
            pat = item.get("pattern", "")
            lsn = item.get("lesson", "")
            aud = item.get("auditor", "Hallwright")
            sev = item.get("severity", "MEDIUM")
            if lsn:
                self.record_lesson(lid, cat, pat, lsn, aud, sev)
                imported += 1

        for conv in data.get("conventions", []):
            cid = conv.get("id") or f"cnv_{int(time.time()*1000)}"
            cat = conv.get("category", "general")
            rule = conv.get("rule", "")
            if rule:
                self.record_convention(cid, cat, rule)
                imported += 1

        return imported

    def export_to_json(self, json_path: str) -> bool:
        """Exports SQLite database state to human-readable, git-trackable JSON."""
        lessons = self.get_lessons(limit=1000)
        conventions = self.get_conventions()

        data = {
            "version": "2.0.0",
            "storage_engine": "sqlite-wal",
            "exported_at": time.time(),
            "lessons_learned": lessons,
            "conventions": conventions
        }

        tmp_path = json_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, json_path)
            return True
        except OSError as e:
            logger.error(f"Failed to export SQLite memory to JSON: {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False
