"""
Unit tests for task manager CLI suite.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from todo import TodoList, TodoItem


class TestTodoCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.temp_dir, "test_todos.json")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_step1_core_crud(self):
        """Tests Step 1: Core in-memory add, list, complete, delete."""
        todos = TodoList()
        item1 = todos.add("Write unit tests")
        item2 = todos.add("Implement JSON save")

        self.assertEqual(item1.id, 1)
        self.assertEqual(item2.id, 2)
        self.assertEqual(len(todos.list_all()), 2)

        # Mark done
        self.assertTrue(todos.complete(1))
        # Active list should only show item 2
        active = todos.list_all(show_all=False)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, 2)

        # All list shows both
        all_items = todos.list_all(show_all=True)
        self.assertEqual(len(all_items), 2)

        # Delete
        self.assertTrue(todos.delete(2))
        self.assertEqual(len(todos.list_all(show_all=True)), 1)

    def test_step2_json_persistence(self):
        """Tests Step 2: JSON file persistence."""
        todos = TodoList()
        todos.add("Persisted task 1")
        todos.add("Persisted task 2")
        todos.complete(1)
        todos.save_json(self.db_file)

        self.assertTrue(os.path.exists(self.db_file))

        # Reload in a fresh instance
        reloaded = TodoList()
        reloaded.load_json(self.db_file)

        self.assertEqual(len(reloaded.items), 2)
        self.assertTrue(reloaded.items[0].completed)
        self.assertFalse(reloaded.items[1].completed)
        self.assertEqual(reloaded._next_id, 3)


if __name__ == "__main__":
    unittest.main()
