"""Hallwright Token Compressor & AST Comment Stripper.

Removes redundant '#' and '//' comments and unnecessary blank lines to
dramatically reduce LLM prompt/completion token consumption while
preserving syntax validity and critical compiler/linter directives.
"""

import ast
import io
import os
import re
import tokenize
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger("hallwright.compressor")

PRESERVED_PRAGMAS = (
    "hallwright-ignore",
    "noqa",
    "type: ignore",
    "pylint:",
    "flake8:",
    "mypy:",
    "fmt: off",
    "fmt: on",
    "c8 ignore",
    "istanbul ignore",
    "eslint-disable",
    "eslint-enable",
    "@ts-ignore",
    "@ts-expect-error",
)


@dataclass
class CompressionStats:
    """Statistics detailing token and character savings."""
    file_path: str = ""
    original_chars: int = 0
    compressed_chars: int = 0
    original_lines: int = 0
    compressed_lines: int = 0
    original_tokens: int = 0
    compressed_tokens: int = 0
    tokens_saved: int = 0
    savings_pct: float = 0.0
    comments_removed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "original_chars": self.original_chars,
            "compressed_chars": self.compressed_chars,
            "original_lines": self.original_lines,
            "compressed_lines": self.compressed_lines,
            "original_tokens": self.original_tokens,
            "compressed_tokens": self.compressed_tokens,
            "tokens_saved": self.tokens_saved,
            "savings_pct": round(self.savings_pct, 2),
            "comments_removed": self.comments_removed,
        }


class TokenCompressor:
    """Safe, syntax-aware code minifier and token saver."""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimates token count using standard subword heuristic (~3.8 chars per token)."""
        if not text:
            return 0
        words = text.split()
        char_tokens = len(text) / 3.8
        word_tokens = len(words) * 1.3
        return max(1, int(round((char_tokens + word_tokens) / 2)))

    @classmethod
    def compress_python(cls, source_code: str) -> Tuple[str, int]:
        """Safely removes comments and excessive whitespace using Python tokenizer."""
        comments_removed = 0
        io_obj = io.StringIO(source_code)
        tokens_out: List[tokenize.TokenInfo] = []

        try:
            tokens = list(tokenize.generate_tokens(io_obj.readline))
        except (tokenize.TokenError, IndentationError) as tok_err:
            logger.debug("Tokenize parse error: %s, falling back to regex", tok_err)
            return cls._compress_generic_hash(source_code)

        for tok in tokens:
            if tok.type == tokenize.COMMENT:
                comment_text = tok.string.strip()
                if comment_text.startswith("#!"):
                    tokens_out.append(tok)
                    continue
                if any(pragma in comment_text for pragma in PRESERVED_PRAGMAS):
                    tokens_out.append(tok)
                    continue
                comments_removed += 1
                continue
            tokens_out.append(tok)

        try:
            untokenized = tokenize.untokenize(tokens_out)
        except Exception as untok_err:
            logger.debug("Untokenize error: %s, falling back to regex", untok_err)
            return cls._compress_generic_hash(source_code)

        cleaned_lines: List[str] = []
        blank_run = 0
        for line in untokenized.splitlines():
            stripped = line.strip()
            if not stripped:
                blank_run += 1
                if blank_run <= 1:
                    cleaned_lines.append("")
            else:
                blank_run = 0
                cleaned_lines.append(line.rstrip())

        result = "\n".join(cleaned_lines)
        if result and not result.endswith("\n"):
            result += "\n"

        try:
            ast.parse(result)
        except SyntaxError as syn_err:
            logger.debug("AST validation failed on compressed code: %s", syn_err)
            return source_code, 0

        return result, comments_removed

    @classmethod
    def _compress_generic_hash(cls, source_code: str) -> Tuple[str, int]:
        """Regex-based quote-aware fallback for python/bash/yaml hash comments."""
        comments_removed = 0
        pattern = re.compile(r"""('(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`)|(#.*)""")
        lines = source_code.splitlines()
        out_lines = []
        blank_run = 0

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                if stripped.startswith("#!") or any(p in stripped for p in PRESERVED_PRAGMAS):
                    out_lines.append(line)
                else:
                    comments_removed += 1
                continue

            def repl(m):
                nonlocal comments_removed
                if m.group(1):
                    return m.group(1)
                comment_text = m.group(2)
                if any(p in comment_text for p in PRESERVED_PRAGMAS):
                    return comment_text
                comments_removed += 1
                return ""

            processed_line = pattern.sub(repl, line).rstrip()
            if not processed_line.strip():
                blank_run += 1
                if blank_run <= 1:
                    out_lines.append("")
                continue
            blank_run = 0
            out_lines.append(processed_line)

        res = "\n".join(out_lines) + "\n"
        return res, comments_removed

    @classmethod
    def compress_c_style(cls, source_code: str) -> Tuple[str, int]:
        """Strips single-line '//' comments from JS, TS, Go, Rust, C++."""
        comments_removed = 0
        pattern = re.compile(r"""('(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`)|(//.*)""")
        lines = source_code.splitlines()
        out_lines = []
        blank_run = 0

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("//"):
                if any(p in stripped for p in PRESERVED_PRAGMAS):
                    out_lines.append(line)
                else:
                    comments_removed += 1
                continue

            def repl(m):
                nonlocal comments_removed
                if m.group(1):
                    return m.group(1)
                comment_text = m.group(2)
                if any(p in comment_text for p in PRESERVED_PRAGMAS):
                    return comment_text
                comments_removed += 1
                return ""

            processed_line = pattern.sub(repl, line).rstrip()
            if not processed_line.strip():
                blank_run += 1
                if blank_run <= 1:
                    out_lines.append("")
                continue
            blank_run = 0
            out_lines.append(processed_line)

        res = "\n".join(out_lines) + "\n"
        return res, comments_removed

    def compress_code(self, source_code: str, file_path: str = "") -> Tuple[str, CompressionStats]:
        """Compresses source code based on file extension or heuristic."""
        ext = os.path.splitext(file_path)[1].lower() if file_path else ".py"

        if ext in (".py", ".pyw"):
            compressed, comments = self.compress_python(source_code)
        elif ext in (".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".c", ".cpp"):
            compressed, comments = self.compress_c_style(source_code)
        else:
            compressed, comments = self._compress_generic_hash(source_code)

        orig_tokens = self.estimate_tokens(source_code)
        comp_tokens = self.estimate_tokens(compressed)
        saved = max(0, orig_tokens - comp_tokens)
        pct = (saved / orig_tokens * 100.0) if orig_tokens > 0 else 0.0

        stats = CompressionStats(
            file_path=file_path,
            original_chars=len(source_code),
            compressed_chars=len(compressed),
            original_lines=len(source_code.splitlines()),
            compressed_lines=len(compressed.splitlines()),
            original_tokens=orig_tokens,
            compressed_tokens=comp_tokens,
            tokens_saved=saved,
            savings_pct=pct,
            comments_removed=comments,
        )
        return compressed, stats

    def compress_file(self, file_path: str, in_place: bool = False) -> Tuple[str, CompressionStats]:
        """Reads file, compresses it, and optionally writes it back."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        compressed, stats = self.compress_code(content, file_path=file_path)

        if in_place and stats.tokens_saved > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(compressed)

        return compressed, stats

    def compress_directory(
        self,
        dir_path: str,
        extensions: Optional[List[str]] = None,
        in_place: bool = False
    ) -> List[CompressionStats]:
        """Scans directory and compresses matching source files."""
        target_exts = extensions or [".py", ".js", ".ts", ".go", ".rs"]
        results: List[CompressionStats] = []

        ignore_dirs = {".git", ".pytest_cache", "node_modules", "target", "venv", "__pycache__"}

        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in target_exts:
                    full_path = os.path.join(root, file)
                    try:
                        _, stats = self.compress_file(full_path, in_place=in_place)
                        if stats.tokens_saved > 0:
                            results.append(stats)
                    except Exception as err:
                        logger.debug("Failed to compress %s: %s", full_path, err)

        return results
