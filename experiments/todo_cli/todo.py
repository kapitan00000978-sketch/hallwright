"""
Task management application built for hwmem A/B Benchmark.
Provides complete in-memory CRUD operations and JSON persistence.
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_DB_FILE = "todos.json"


class TodoItem:
    def __init__(self, item_id: int, title: str, completed: bool = False, created_at: Optional[str] = None):
        self.id = item_id
        self.title = title
        self.completed = completed
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TodoItem":
        return cls(
            item_id=data["id"],
            title=data["title"],
            completed=data.get("completed", False),
            created_at=data.get("created_at")
        )


class TodoList:
    def __init__(self):
        self.items: List[TodoItem] = []
        self._next_id = 1

    def add(self, title: str) -> TodoItem:
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")
        item = TodoItem(item_id=self._next_id, title=title.strip())
        self.items.append(item)
        self._next_id += 1
        return item

    def list_all(self, show_all: bool = False) -> List[TodoItem]:
        if show_all:
            return list(self.items)
        return [i for i in self.items if not i.completed]

    def complete(self, item_id: int) -> bool:
        for item in self.items:
            if item.id == item_id:
                item.completed = True
                return True
        return False

    def delete(self, item_id: int) -> bool:
        for idx, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(idx)
                return True
        return False

    def save_json(self, filepath: str = DEFAULT_DB_FILE) -> None:
        data = {
            "next_id": self._next_id,
            "todos": [i.to_dict() for i in self.items]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_json(self, filepath: str = DEFAULT_DB_FILE) -> None:
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._next_id = data.get("next_id", 1)
        self.items = [TodoItem.from_dict(d) for d in data.get("todos", [])]


    def export_csv(self, filepath: str = "todos.csv") -> int:
        import csv
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "completed", "created_at"])
            for item in self.items:
                writer.writerow([item.id, item.title, str(item.completed), item.created_at])
        return len(self.items)


def main() -> int:
    parser = argparse.ArgumentParser(description="Tiny Todo CLI")
    parser.add_argument("--file", "-f", default=DEFAULT_DB_FILE, help="Path to JSON storage file")
    subparsers = parser.add_subparsers(dest="subcommand")

    p_add = subparsers.add_parser("add", help="Add a new todo item")
    p_add.add_argument("title", help="Task title")

    p_list = subparsers.add_parser("list", help="List todo items")
    p_list.add_argument("--all", "-a", action="store_true", help="Include completed items")

    p_done = subparsers.add_parser("done", help="Mark item as completed")
    p_done.add_argument("id", type=int, help="Task ID")

    p_del = subparsers.add_parser("delete", help="Delete an item")
    p_del.add_argument("id", type=int, help="Task ID")

    p_exp = subparsers.add_parser("export", help="Export tasks to file")
    p_exp.add_argument("--format", choices=["csv"], default="csv", help="Export format (default: csv)")
    p_exp.add_argument("--output", "-o", default="todos.csv", help="Output file path (default: todos.csv)")

    args = parser.parse_args()

    todo_list = TodoList()
    todo_list.load_json(args.file)

    if args.subcommand == "add":
        item = todo_list.add(args.title)
        todo_list.save_json(args.file)
        print(f"Added task #{item.id}: {item.title}")
        return 0
    elif args.subcommand == "list":
        items = todo_list.list_all(show_all=getattr(args, "all", False))
        if not items:
            print("No tasks found.")
            return 0
        for i in items:
            status = "[x]" if i.completed else "[ ]"
            print(f"{i.id}. {status} {i.title} ({i.created_at})")
        return 0
    elif args.subcommand == "done":
        if todo_list.complete(args.id):
            todo_list.save_json(args.file)
            print(f"Completed task #{args.id}")
            return 0
        else:
            print(f"Error: Task #{args.id} not found", file=sys.stderr)
            return 1
    elif args.subcommand == "delete":
        if todo_list.delete(args.id):
            todo_list.save_json(args.file)
            print(f"Deleted task #{args.id}")
            return 0
        else:
            print(f"Error: Task #{args.id} not found", file=sys.stderr)
            return 1
    elif args.subcommand == "export":
        if args.format == "csv":
            count = todo_list.export_csv(args.output)
            print(f"Exported {count} tasks to {args.output}")
            return 0
        else:
            print(f"Unsupported format: {args.format}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
