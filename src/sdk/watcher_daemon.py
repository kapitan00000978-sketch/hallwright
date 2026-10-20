"""Hallwright Autonomous Background Watcher Daemon.

Silently monitors the workspace directory for file changes:
- Runs AST token compressor on saved code to strip comment bloat.
- Audits files against the 5 Core Invariants using the Gatekeeper.
- On any defect detection, automatically triggers background self-evolution
  and in-place remediation without halting or interrupting the developer/agent.
"""

import os
import sys
import time
import logging
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any

logger = logging.getLogger("hallwright.watcher")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

try:
    from compressor import TokenCompressor
except ImportError:
    TokenCompressor = None

try:
    from evolution import evolve_async
except ImportError:
    evolve_async = None


@dataclass
class WatcherEvent:
    """Represents a file change event detected by the daemon."""
    file_path: str
    event_type: str
    timestamp: float = field(default_factory=time.time)
    tokens_saved: int = 0
    healed: bool = False
    flaws_found: int = 0


class WatcherDaemon:
    """Non-blocking zero-dependency file surveillance daemon."""

    IGNORE_DIRS = {
        ".git", ".pytest_cache", "__pycache__", "node_modules",
        "target", "venv", ".idea", ".vscode", "dist", "build"
    }
    WATCH_EXTENSIONS = {".py", ".js", ".ts", ".go", ".rs", ".html", ".json"}

    def __init__(self, workspace_root: str = ROOT_DIR, poll_interval: float = 1.5):
        self.workspace_root = workspace_root
        self.poll_interval = poll_interval
        self._file_snapshots: Dict[str, float] = {}
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.compressor = TokenCompressor() if TokenCompressor else None

    def snapshot(self) -> Dict[str, float]:
        """Scans workspace and records current modification times."""
        snaps: Dict[str, float] = {}
        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.WATCH_EXTENSIONS:
                    fpath = os.path.join(root, file)
                    try:
                        snaps[fpath] = os.path.getmtime(fpath)
                    except OSError:
                        continue
        return snaps

    def check_changes(self, auto_heal: bool = True) -> List[WatcherEvent]:
        """Compares current filesystem against last snapshot and processes modifications."""
        current_snaps = self.snapshot()
        events: List[WatcherEvent] = []

        with self._lock:
            if not self._file_snapshots:
                self._file_snapshots = current_snaps
                return []

            for fpath, mtime in current_snaps.items():
                old_mtime = self._file_snapshots.get(fpath)
                if old_mtime is not None and mtime > old_mtime + 0.05:
                    event = self._process_file_change(fpath, auto_heal=auto_heal)
                    events.append(event)
                    current_snaps[fpath] = os.path.getmtime(fpath)

            self._file_snapshots = current_snaps

        return events

    def _process_file_change(self, file_path: str, auto_heal: bool = True) -> WatcherEvent:
        """Compresses token bloat and inspects file for autonomous evolution."""
        tokens_saved = 0
        healed = False
        flaws_count = 0

        # 1. Compress comments if enabled
        if self.compressor and os.path.splitext(file_path)[1] in (".py", ".js", ".ts"):
            try:
                _, stats = self.compressor.compress_file(file_path, in_place=True)
                tokens_saved = stats.tokens_saved
            except Exception as comp_err:
                logger.debug("Compression skipped on %s: %s", file_path, comp_err)

        # 2. Gatekeeper scan
        try:
            from detector import scan_file
            findings = scan_file(file_path)
            flaws_count = len(findings)
            if findings:
                # Trigger background evolution
                if evolve_async:
                    err_signature = findings[0].get("message", "Detected code defect in file")
                    evolve_async(err_signature, file_path=file_path)

                # Attempt remediation
                if auto_heal:
                    from remediator import remediate_file
                    repaired = remediate_file(file_path)
                    if repaired > 0:
                        healed = True
        except Exception as scan_err:
            logger.debug("Gatekeeper scan skipped on %s: %s", file_path, scan_err)

        return WatcherEvent(
            file_path=file_path,
            event_type="MODIFIED",
            tokens_saved=tokens_saved,
            healed=healed,
            flaws_found=flaws_count
        )

    def start_background(self, auto_heal: bool = True) -> threading.Thread:
        """Starts the watcher loop in a non-blocking background daemon thread."""
        self._is_running = True
        self._file_snapshots = self.snapshot()

        def _loop():
            while self._is_running:
                try:
                    events = self.check_changes(auto_heal=auto_heal)
                    for ev in events:
                        logger.info("Watcher: %s (Saved %d tokens, Healed: %s)", ev.file_path, ev.tokens_saved, ev.healed)
                except Exception as loop_err:
                    logger.debug("Watcher iteration error: %s", loop_err)
                time.sleep(self.poll_interval)

        t = threading.Thread(target=_loop, daemon=True, name="HallwrightWatcherDaemon")
        t.start()
        self._thread = t
        return t

    def stop(self) -> None:
        """Stops the daemon thread gracefully."""
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
