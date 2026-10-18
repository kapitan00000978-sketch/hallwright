"""
Hallwright Enterprise Architecture: Transactional Outbox Pattern Engine.
Part of Pillar IV: Enterprise Modular Domain Libraries (Bosqich 40).

Guarantees at-least-once reliable message delivery and event dispatch across
service boundaries, network failures, and abrupt process terminations without
relying on heavy distributed transactions (2PC).
"""

import time
import json
import uuid
import sqlite3
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class OutboxStatus(str, Enum):
    PENDING = "PENDING"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"


@dataclass
class OutboxRecord:
    id: str
    topic: str
    payload: Dict[str, Any]
    idempotency_key: str
    status: OutboxStatus = OutboxStatus.PENDING
    retry_count: int = 0
    max_retries: int = 5
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_attempt_at: Optional[str] = None
    error_message: Optional[str] = None


class TransactionalOutbox:
    """
    Guarantees that state changes and events are committed together atomically.
    Stores messages in an SQLite/in-memory table before background dispatching.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._in_memory_conn: Optional[sqlite3.Connection] = None
        if db_path == ":memory:" or "mode=memory" in db_path:
            self._in_memory_conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._in_memory_conn is not None:
            return self._in_memory_conn
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS outbox_events (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    max_retries INTEGER NOT NULL DEFAULT 5,
                    created_at TEXT NOT NULL,
                    last_attempt_at TEXT,
                    error_message TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_status ON outbox_events (status)")
            conn.commit()
            if self._in_memory_conn is None:
                conn.close()

    def _connection(self):
        from contextlib import contextmanager
        @contextmanager
        def _cm():
            conn = self._get_connection()
            try:
                yield conn
            finally:
                if self._in_memory_conn is None:
                    conn.close()
        return _cm()

    def record_event(
        self,
        topic: str,
        payload: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        max_retries: int = 5
    ) -> OutboxRecord:
        """Atomically inserts an event into the outbox ledger."""
        rec_id = f"out_{uuid.uuid4().hex[:12]}"
        idem_key = idempotency_key or f"idem_{uuid.uuid4().hex}"
        record = OutboxRecord(
            id=rec_id,
            topic=topic,
            payload=payload,
            idempotency_key=idem_key,
            max_retries=max_retries
        )

        with self._lock:
            with self._connection() as conn:
                conn.execute("""
                    INSERT INTO outbox_events (
                        id, topic, payload, idempotency_key, status, retry_count, max_retries, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.id,
                    record.topic,
                    json.dumps(record.payload),
                    record.idempotency_key,
                    record.status.value,
                    record.retry_count,
                    record.max_retries,
                    record.created_at
                ))
                conn.commit()

        return record

    def fetch_pending(self, limit: int = 20) -> List[OutboxRecord]:
        """Retrieves uncommitted or failed events eligible for retry."""
        records: List[OutboxRecord] = []
        with self._lock:
            with self._connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM outbox_events
                    WHERE status IN ('PENDING', 'FAILED') AND retry_count < max_retries
                    ORDER BY created_at ASC
                    LIMIT ?
                """, (limit,))
                for row in cursor.fetchall():
                    records.append(OutboxRecord(
                        id=row["id"],
                        topic=row["topic"],
                        payload=json.loads(row["payload"]),
                        idempotency_key=row["idempotency_key"],
                        status=OutboxStatus(row["status"]),
                        retry_count=row["retry_count"],
                        max_retries=row["max_retries"],
                        created_at=row["created_at"],
                        last_attempt_at=row["last_attempt_at"],
                        error_message=row["error_message"]
                    ))
        return records

    def process_pending(self, publisher: Callable[[str, Dict[str, Any]], bool], batch_size: int = 20) -> int:
        """
        Dispatches pending events through the given publisher callback.
        Marks records as PUBLISHED or increments retry counters on failure.
        """
        pending = self.fetch_pending(limit=batch_size)
        published_count = 0

        for rec in pending:
            now_iso = datetime.now(timezone.utc).isoformat()
            try:
                success = publisher(rec.topic, rec.payload)
                with self._lock:
                    with self._connection() as conn:
                        if success:
                            conn.execute("""
                                UPDATE outbox_events
                                SET status = 'PUBLISHED', last_attempt_at = ?
                                WHERE id = ?
                            """, (now_iso, rec.id))
                            published_count += 1
                        else:
                            new_count = rec.retry_count + 1
                            new_status = 'DEAD_LETTER' if new_count >= rec.max_retries else 'FAILED'
                            conn.execute("""
                                UPDATE outbox_events
                                SET status = ?, retry_count = ?, last_attempt_at = ?, error_message = ?
                                WHERE id = ?
                            """, (new_status, new_count, now_iso, "Publisher returned False", rec.id))
                        conn.commit()
            except Exception as err:
                with self._lock:
                    with self._connection() as conn:
                        new_count = rec.retry_count + 1
                        new_status = 'DEAD_LETTER' if new_count >= rec.max_retries else 'FAILED'
                        conn.execute("""
                            UPDATE outbox_events
                            SET status = ?, retry_count = ?, last_attempt_at = ?, error_message = ?
                            WHERE id = ?
                        """, (new_status, new_count, now_iso, str(err), rec.id))
                        conn.commit()

        return published_count
