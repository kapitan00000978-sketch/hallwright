import os
import sys
import time
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from watcher_daemon import WatcherDaemon


def test_watcher_snapshot_and_no_change():
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, "service.py")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("def start():\n    return True\n")

        daemon = WatcherDaemon(workspace_root=tmpdir, poll_interval=0.1)
        snaps = daemon.snapshot()
        assert fpath in snaps

        # Initial check should register snapshots and return empty events
        events_initial = daemon.check_changes()
        assert len(events_initial) == 0

        # No changes
        events_none = daemon.check_changes()
        assert len(events_none) == 0


def test_watcher_detects_modification_and_compresses_tokens():
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, "calc.py")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("x = 1\n")

        daemon = WatcherDaemon(workspace_root=tmpdir, poll_interval=0.05)
        daemon.check_changes()

        # Modify file with redundant comments
        time.sleep(0.05)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("# Redundant calculation comment\nx = 2 + 2\n# Another useless comment\n")
        # Ensure mtime changes
        os.utime(fpath, (time.time() + 1, time.time() + 1))

        events = daemon.check_changes(auto_heal=False)
        assert len(events) == 1
        assert events[0].file_path == fpath
        assert events[0].tokens_saved > 0

        # Verify comments were stripped in-place
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Redundant calculation comment" not in content
            assert "x = 2 + 2" in content


def test_watcher_background_start_and_stop():
    with tempfile.TemporaryDirectory() as tmpdir:
        daemon = WatcherDaemon(workspace_root=tmpdir, poll_interval=0.1)
        thread = daemon.start_background()
        assert thread.is_alive()
        daemon.stop()
        assert not daemon._is_running
