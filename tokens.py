#!/usr/bin/env python3
"""
tokens.py - Token measurement utility for AI coding agents.
Uses tiktoken if installed, otherwise heuristic chars/4.
Always labels results as ESTIMATE per hwmem rules.
"""

import sys
import os
import math
import logging

logger = logging.getLogger("hwmem.tokens")

try:
    import tiktoken
    _TIKTOKEN_ENCODER = tiktoken.get_encoding("cl100k_base")
except ImportError:
    _TIKTOKEN_ENCODER = None


def count_tokens(text: str) -> tuple:
    """
    Counts tokens in a string.
    Returns (token_count, method_label).
    """
    if _TIKTOKEN_ENCODER is not None:
        try:
            tokens = _TIKTOKEN_ENCODER.encode(text)
            return len(tokens), "tiktoken (cl100k_base) [ESTIMATE]"
        except Exception as enc_err:
            logger.debug("tiktoken encoding failed, falling back to chars/4: %s", enc_err)

    # Heuristic chars / 4 fallback
    estimate = max(1, math.ceil(len(text) / 4.0)) if text else 0
    return estimate, "heuristic (chars/4) [ESTIMATE]"


def count_file_tokens(file_path: str) -> tuple:
    """Reads a file and returns (token_count, method_label)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as read_err:
        logger.debug("Failed reading file %s: %s", file_path, read_err)
        raise

    return count_tokens(content)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tokens.py <path_to_text_file>", file=sys.stderr)
        return 1

    target = sys.argv[1]
    try:
        count, method = count_file_tokens(target)
        print(f"{count} tokens | Method: {method} | File: {target}")
        return 0
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
