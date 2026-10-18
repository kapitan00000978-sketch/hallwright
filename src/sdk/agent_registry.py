"""
Hallwright Multi-Agent State Synchronization & Session Registry.
Part of the Hallwright Autonomous Craftsmanship Protocol (Phase 2).

Maintains a synchronized, conflict-free ledger of active AI agents
(Claude Code, Cursor, Copilot, Antigravity, Hermes) operating concurrently
in the repository, preventing write-collisions and stomped edits.
"""

import os
import json
import uuid
import tempfile
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

DEFAULT_SESSIONS_PATH = os.path.join(".hallwright", "agent_sessions.json")
DEFAULT_TIMEOUT_MINUTES = 15

logger = logging.getLogger("artisan.agent_registry")


class AgentRegistry:
    """
    Manages live AI agent sessions, active file locks, and cross-agent coordination.
    """

    def __init__(self, sessions_path: str = DEFAULT_SESSIONS_PATH):
        self.sessions_path = sessions_path
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensures that the sessions file and storage directory exist with valid schema."""
        dir_name = os.path.dirname(self.sessions_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        if not os.path.exists(self.sessions_path):
            initial_data = {
                "version": "1.0.0",
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                "active_sessions": []
            }
            self._write_atomic(initial_data)

    def _read_data(self) -> Dict[str, Any]:
        """Reads sessions data with fallback to a clean empty state."""
        if not os.path.exists(self.sessions_path):
            return {"version": "1.0.0", "active_sessions": []}
        try:
            with open(self.sessions_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as err:
            logger.warning("Could not parse sessions file (%s), reinitializing: %s", self.sessions_path, err)
            return {"version": "1.0.0", "active_sessions": []}

    def _write_atomic(self, data: Dict[str, Any]) -> None:
        """Atomically persists session data to prevent partial reads during concurrent agent access."""
        dir_name = os.path.dirname(self.sessions_path) or "."
        os.makedirs(dir_name, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="artisan_sess_", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.sessions_path)
        except OSError as write_err:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as cleanup_err:
                    logger.debug("Failed to clean up temp sessions file: %s", cleanup_err)
            raise write_err

    def register_session(
        self,
        agent_name: str,
        active_files: Optional[List[str]] = None,
        intent: str = "",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registers or refreshes an active agent session in the workspace.
        """
        data = self._read_data()
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        sid = session_id or f"sess_{agent_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

        files = [os.path.normpath(f) for f in (active_files or [])]
        sessions = data.get("active_sessions", [])

        # Update existing session if found
        for s in sessions:
            if s.get("session_id") == sid:
                s["last_heartbeat"] = now_iso
                s["active_files"] = files
                if intent:
                    s["intent"] = intent
                data["lastUpdated"] = now_iso
                self._write_atomic(data)
                return s

        new_session = {
            "session_id": sid,
            "agent_name": agent_name,
            "intent": intent,
            "active_files": files,
            "started_at": now_iso,
            "last_heartbeat": now_iso
        }
        sessions.append(new_session)
        data["active_sessions"] = sessions
        data["lastUpdated"] = now_iso
        self._write_atomic(data)
        return new_session

    def heartbeat(self, session_id: str) -> bool:
        """Refreshes the heartbeat timestamp of a running session."""
        data = self._read_data()
        now_iso = datetime.now(timezone.utc).isoformat()
        for s in data.get("active_sessions", []):
            if s.get("session_id") == session_id:
                s["last_heartbeat"] = now_iso
                data["lastUpdated"] = now_iso
                self._write_atomic(data)
                return True
        return False

    def release_session(self, session_id: str) -> bool:
        """Removes an agent session upon task completion."""
        data = self._read_data()
        initial_len = len(data.get("active_sessions", []))
        data["active_sessions"] = [s for s in data.get("active_sessions", []) if s.get("session_id") != session_id]
        if len(data["active_sessions"]) < initial_len:
            data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
            self._write_atomic(data)
            return True
        return False

    def get_active_sessions(self, timeout_minutes: int = DEFAULT_TIMEOUT_MINUTES) -> List[Dict[str, Any]]:
        """
        Returns all live sessions, filtering out and pruning stale sessions exceeding the timeout threshold.
        """
        data = self._read_data()
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=timeout_minutes)

        live_sessions = []
        has_pruned = False

        for s in data.get("active_sessions", []):
            hb_str = s.get("last_heartbeat")
            if not hb_str:
                continue
            try:
                hb = datetime.fromisoformat(hb_str)
                if hb.tzinfo is None:
                    hb = hb.replace(tzinfo=timezone.utc)
                if hb >= cutoff:
                    live_sessions.append(s)
                else:
                    has_pruned = True
            except ValueError:
                has_pruned = True

        if has_pruned:
            data["active_sessions"] = live_sessions
            data["lastUpdated"] = now.isoformat()
            try:
                self._write_atomic(data)
            except OSError as err:
                logger.debug("Failed to write pruned sessions: %s", err)

        return live_sessions

    def check_conflicts(self, target_file: str, current_session_id: str = "") -> List[Dict[str, Any]]:
        """
        Checks if any other active agent is currently working on or holding a lock on the target file.
        """
        norm_target = os.path.normpath(target_file)
        active = self.get_active_sessions()
        conflicts = []

        for s in active:
            if current_session_id and s.get("session_id") == current_session_id:
                continue
            held_files = [os.path.normpath(f) for f in s.get("active_files", [])]
            if norm_target in held_files:
                conflicts.append(s)

        return conflicts
