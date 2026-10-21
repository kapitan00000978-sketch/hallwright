"""
Unit tests for hwmem - Tiny session-memory system for AI coding agents.
Python 3 standard library unittest only.
"""

import os
import sys
import shutil
import tempfile
import threading
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import memory


class TestHwmem(unittest.TestCase):
    def setUp(self):
        # Create an isolated temporary test directory
        self.test_dir = tempfile.mkdtemp(prefix="test_hwmem_env_")
        self.orig_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Redirect memory paths to this test directory
        memory.MEMORY_DIR = Path(".hallwright/memory")
        memory.SESSIONS_DIR = memory.MEMORY_DIR / "sessions"
        memory.ARCHIVE_DIR = memory.SESSIONS_DIR / "archive"
        memory.INDEX_FILE = memory.MEMORY_DIR / "INDEX.md"

    def tearDown(self):
        os.chdir(self.orig_cwd)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_start_note_finish_flow(self):
        """Tests standard start -> note -> finish lifecycle."""
        # 1. Start session
        code = memory.cmd_start("Initialize Core Feature")
        self.assertEqual(code, 0)
        self.assertTrue(memory.INDEX_FILE.exists())

        files = memory._list_session_files()
        self.assertEqual(len(files), 1)
        session_file = files[0]

        # Verify header marker
        with open(session_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(lines[0].strip(), ".hallwright.memory")

        # 2. Add notes
        self.assertEqual(memory.cmd_note("Done", "Implemented core data structures"), 0)
        self.assertEqual(memory.cmd_note("Decisions", "Used standard library only"), 0)
        self.assertEqual(memory.cmd_note("Next", "Write unit test suite"), 0)
        self.assertEqual(memory.cmd_note("Verify command", "python -m unittest tests/test_hwmem.py"), 0)

        with open(session_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Implemented core data structures", content)
        self.assertIn("Used standard library only", content)
        self.assertIn("Write unit test suite", content)

        # 3. Finish session with slug
        self.assertEqual(memory.cmd_finish("core-feature-done"), 0)
        updated_files = memory._list_session_files()
        self.assertEqual(len(updated_files), 1)
        self.assertTrue(updated_files[0].name.endswith("core-feature-done.md"))

        # Verify INDEX.md updated
        with open(memory.INDEX_FILE, "r", encoding="utf-8") as f:
            idx_text = f.read()
        self.assertIn("core-feature-done", idx_text)

    def test_secret_refusal(self):
        """Verifies that secrets are strictly rejected and not written to disk."""
        fake_sk = "sk-" + "1234567890abcdef1234567890"
        with self.assertRaises(ValueError):
            memory.cmd_start(f"Feature with secret {fake_sk}")

        # GitHub token
        memory.cmd_start("Legitimate Session")
        fake_ghp = "ghp_" + "1234567890abcdef1234567890"
        with self.assertRaises(ValueError):
            memory.cmd_note("Done", f"Added token {fake_ghp}")

        # Password
        fake_pw = "password=" + "'SuperSecretPassword123'"
        with self.assertRaises(ValueError):
            memory.cmd_note("Decisions", f"Set admin {fake_pw}")

        # Ensure secret was not written to file
        session_file = memory._get_latest_session_file()
        with open(session_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("SuperSecretPassword123", content)
        self.assertNotIn("ghp_", content)


    def test_index_cap_and_compact(self):
        """Verifies that when INDEX > 30 lines, the 10 oldest sessions are compacted and archived."""
        # Create 32 sessions
        for i in range(1, 33):
            code = memory.cmd_start(f"Session Item {i:02d}")
            self.assertEqual(code, 0)
            memory.cmd_note("Done", f"Finished milestone {i}")
            memory.cmd_finish(f"slug-{i:02d}")

        # INDEX lines (excluding header) must be <= 30
        with open(memory.INDEX_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

        self.assertLessEqual(len(lines), 30)

        # Check that archive directory exists and contains archived sessions
        self.assertTrue(memory.ARCHIVE_DIR.exists())
        archived_files = list(memory.ARCHIVE_DIR.glob("*.md"))
        self.assertGreaterEqual(len(archived_files), 10)

        # Check that INDEX contains an archive summary line
        with open(memory.INDEX_FILE, "r", encoding="utf-8") as f:
            idx_content = f.read()
        self.assertIn("archive-", idx_content)

    def test_corrupt_and_missing_file_resilience(self):
        """Verifies that missing or corrupt files do not crash the tool."""
        # Show with no files
        self.assertEqual(memory.cmd_show(), 0)

        # Start a session then write binary garbage into INDEX.md
        memory.cmd_start("Resilience Test")
        with open(memory.INDEX_FILE, "wb") as f:
            f.write(b"\xff\xfe\x00\x00\x80\x99\xff\xaa\xbb")

        # show must still succeed cleanly using errors='replace'
        self.assertEqual(memory.cmd_show(), 0)

    def test_verify_detects_missing_path_and_binary(self):
        """Verifies that verify reports missing paths and commands without crashing or altering files."""
        memory.cmd_start("Verify Diagnostic Test")
        memory.cmd_note("Done", "Created missing file docs/nonexistent_xyz_ghost.md")
        memory.cmd_note("Verify command", "fakebinary12345_nonexistent --check")

        # Run verify; should return 1 (reporting mismatches)
        exit_code = memory.cmd_verify()
        self.assertEqual(exit_code, 1)

        # Now test with a file that actually exists
        real_file = Path("real_file.txt")
        real_file.write_text("ok", encoding="utf-8")
        memory.cmd_start("Valid Verify Session")
        memory.cmd_note("Done", "Verified real_file.txt exists")
        memory.cmd_note("Verify command", "python --version")

        clean_code = memory.cmd_verify()
        self.assertEqual(clean_code, 0)

    def test_concurrent_writers(self):
        """Verifies that concurrent writers do not corrupt files under thread/process lock."""
        memory.cmd_start("Concurrency Benchmark")
        errors = []

        def worker(worker_id):
            try:
                for j in range(5):
                    code = memory.cmd_note("Done", f"Worker {worker_id} iteration {j}")
                    if code != 0:
                        errors.append(f"Worker {worker_id} failed with exit code {code}")
            except Exception as e:
                errors.append(f"Worker {worker_id} exception: {e}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        session_file = memory._get_latest_session_file()
        with open(session_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Verify entries from all workers are present
        for i in range(4):
            self.assertIn(f"Worker {i} iteration 0", content)


if __name__ == "__main__":
    unittest.main()
