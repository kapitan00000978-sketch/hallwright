import os
import sys
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from compressor import TokenCompressor, CompressionStats


def test_compress_python_basic_comments():
    compressor = TokenCompressor()
    code = (
        "#!/usr/bin/env python3\n"
        "# This is a redundant comment\n"
        "def calculate_total(price, tax):\n"
        "    # Another obvious comment\n"
        "    return price + tax\n"
    )
    compressed, stats = compressor.compress_code(code, "example.py")
    assert "#!/usr/bin/env python3" in compressed
    assert "redundant comment" not in compressed
    assert "obvious comment" not in compressed
    assert "def calculate_total(price, tax):" in compressed
    assert stats.comments_removed >= 2
    assert stats.tokens_saved > 0


def test_compress_preserves_pragmas():
    compressor = TokenCompressor()
    code = (
        "def run_eval():\n"
        "    eval('1 + 1')  # hallwright-ignore\n"
        "    x = 10  # type: ignore\n"
        "    # Regular useless comment\n"
        "    return x\n"
    )
    compressed, stats = compressor.compress_code(code, "pragma_test.py")
    assert "hallwright-ignore" in compressed
    assert "type: ignore" in compressed
    assert "Regular useless comment" not in compressed
    assert stats.comments_removed >= 1


def test_compress_c_style_comments():
    compressor = TokenCompressor()
    js_code = (
        "// Redundant top comment\n"
        "function greet(name) {\n"
        "  // Say hello\n"
        "  const msg = 'Hello ' + name; // inline comment\n"
        "  return msg;\n"
        "}\n"
    )
    compressed, stats = compressor.compress_code(js_code, "script.js")
    assert "Redundant top comment" not in compressed
    assert "Say hello" not in compressed
    assert "inline comment" not in compressed
    assert "function greet(name)" in compressed
    assert stats.comments_removed >= 3
    assert stats.tokens_saved > 0


def test_compress_file_and_directory():
    compressor = TokenCompressor()
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath1 = os.path.join(tmpdir, "module.py")
        with open(fpath1, "w", encoding="utf-8") as f:
            f.write("# Module comment\nx = 1\n# Another comment\n")

        # Check non in-place
        _, stats = compressor.compress_file(fpath1, in_place=False)
        assert stats.tokens_saved > 0
        with open(fpath1, "r", encoding="utf-8") as f:
            assert "# Module comment" in f.read()

        # Check in-place
        _, stats_ip = compressor.compress_file(fpath1, in_place=True)
        with open(fpath1, "r", encoding="utf-8") as f:
            content = f.read()
            assert "# Module comment" not in content
            assert "x = 1" in content
