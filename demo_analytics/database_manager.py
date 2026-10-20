"""Database Access and Query Manager.
Generated for task: SaaS Analitika va Savdo Monitoring Paneli
Provides parameterized query execution, SQLite storage, migrations, and transactions.
"""

import sqlite3
import os
import contextlib
from typing import Dict, Any, List, Optional


class DatabaseManager:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._shared_conn = sqlite3.connect(self.db_path) if self.db_path == ":memory:" else None
        if self._shared_conn:
            self._shared_conn.row_factory = sqlite3.Row
        self._init_schema()

    @contextlib.contextmanager
    def get_connection(self):
        if self._shared_conn is not None:
            try:
                yield self._shared_conn
                self._shared_conn.commit()
            except Exception:
                self._shared_conn.rollback()
                raise
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _init_schema(self) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'default',
                    is_deleted INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_records_key ON records(key);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_records_category ON records(category);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_records_deleted ON records(is_deleted);")

    def insert_record(self, key: str, value: str, category: str = "default") -> int:
        if not key or not key.strip():
            raise ValueError("Record key cannot be empty")
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO records (key, value, category) VALUES (?, ?, ?);",
                (key.strip(), value, category.strip())
            )
            return cursor.lastrowid

    def get_record(self, key: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM records WHERE key = ? AND is_deleted = 0;",
                (key.strip(),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_records(self, category: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            if category:
                cursor = conn.execute(
                    "SELECT * FROM records WHERE category = ? AND is_deleted = 0 ORDER BY id DESC LIMIT ? OFFSET ?;",
                    (category.strip(), limit, offset)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM records WHERE is_deleted = 0 ORDER BY id DESC LIMIT ? OFFSET ?;",
                    (limit, offset)
                )
            return [dict(r) for r in cursor.fetchall()]

    def delete_record(self, key: str, soft: bool = True) -> bool:
        with self.get_connection() as conn:
            if soft:
                cursor = conn.execute(
                    "UPDATE records SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP WHERE key = ?;",
                    (key.strip(),)
                )
            else:
                cursor = conn.execute("DELETE FROM records WHERE key = ?;", (key.strip(),))
            return cursor.rowcount > 0

    def count_records(self, category: Optional[str] = None) -> int:
        with self.get_connection() as conn:
            if category:
                cursor = conn.execute(
                    "SELECT COUNT(*) as cnt FROM records WHERE category = ? AND is_deleted = 0;",
                    (category.strip(),)
                )
            else:
                cursor = conn.execute("SELECT COUNT(*) as cnt FROM records WHERE is_deleted = 0;")
            row = cursor.fetchone()
            return int(row["cnt"]) if row else 0
