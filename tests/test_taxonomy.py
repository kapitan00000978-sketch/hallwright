"""
Test Suite for Hallwright Master Taxonomy & Tasnif Protocol
Validates taxonomy CLI command, alias (tasnif), JSON output serialization,
and cross-consistency with docs/TAXONOMY.md, docs/TASNIF.md, and scripts/detector.py.
"""

import os
import sys
import json
import subprocess
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_taxonomy_cli_command():
    """Verifies that 'hallwright taxonomy' outputs structured taxonomy."""
    cli_path = os.path.join(ROOT_DIR, "hallwright_cli.py")
    proc = subprocess.run(
        [sys.executable, cli_path, "taxonomy"],
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert proc.returncode == 0
    assert "HALLWRIGHT MASTER TAXONOMY & CLASSIFICATION MATRIX" in proc.stdout
    assert "DEFECT CLASSIFICATION & QUALITY PENALTIES" in proc.stdout
    assert "ENTERPRISE DOMAIN LIBRARIES" in proc.stdout
    assert "POLYGLOT RUNTIME SPECTRUM" in proc.stdout
    assert "THE 5 CORE INVARIANTS" in proc.stdout


def test_tasnif_alias_cli_command():
    """Verifies that 'hallwright tasnif' works identically as an alias."""
    cli_path = os.path.join(ROOT_DIR, "hallwright_cli.py")
    proc = subprocess.run(
        [sys.executable, cli_path, "tasnif"],
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert proc.returncode == 0
    assert "TASNIF" in proc.stdout
    assert "STUB_BARE_EXCEPT" in proc.stdout


def test_taxonomy_json_output():
    """Verifies that 'hallwright taxonomy --json' produces valid machine-readable JSON."""
    cli_path = os.path.join(ROOT_DIR, "hallwright_cli.py")
    proc = subprocess.run(
        [sys.executable, cli_path, "taxonomy", "--json"],
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert "title" in data
    assert "defects" in data
    assert "libraries" in data
    assert "runtimes" in data
    assert "invariants" in data
    assert len(data["defects"]) >= 15
    assert len(data["libraries"]) == 8
    assert len(data["runtimes"]) == 5
    assert len(data["invariants"]) == 5


def test_taxonomy_markdown_files_exist():
    """Verifies docs/TAXONOMY.md and docs/TASNIF.md exist and contain official content."""
    tax_path = os.path.join(ROOT_DIR, "docs", "TAXONOMY.md")
    tasnif_path = os.path.join(ROOT_DIR, "docs", "TASNIF.md")

    assert os.path.isfile(tax_path), "docs/TAXONOMY.md must exist"
    assert os.path.isfile(tasnif_path), "docs/TASNIF.md must exist"

    with open(tax_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "DEFEKTLAR VA XAVFSIZLIK XATOLIKLARI TASNIFI" in content
        assert "KORPORATIV DOMEN KUTUBXONALARI TASNIFI" in content
        assert "KO‘P TILLI YADRO VA RUNTIME TASNIFI" in content
        assert "ARXITEKTURA VA SIFAT INVARIANTLARI" in content
