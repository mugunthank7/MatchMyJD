#!/usr/bin/env python3
# preprocess_JD.py
"""
Utility to clean and normalize a raw Job Description (JD) string
before sending it to an LLM like Gemini 2.5 Flash.

Main entry point:
    preprocess_jd(raw_text: str) -> str

You can also use this as a small CLI:
    python preprocess_JD.py path/to/jd.txt > cleaned_jd.txt
"""

from __future__ import annotations

import re
import sys
from typing import Iterable

# --- Regexes & constants -----------------------------------------------------

# Very simple HTML tag stripper (good enough for job board copy-paste)
_HTML_TAG_RE = re.compile(r"<[^>]+>")

# Any run of whitespace characters (except newlines when we handle per-line)
_WHITESPACE_RE = re.compile(r"\s+")

# Bullet characters we commonly see in JDs
_BULLET_CHARS = "•·●○▪▶■‣-"

# Lines starting with these (case-insensitive) are often noise/boilerplate.
# You can tweak this list over time based on what you see.
_IGNORE_LINE_PREFIXES = (
    "about the company",
    "about us",
    "about this role",
    "about the job",
    "why join us",
    "equal opportunity",
    "eoe statement",
    "we are an equal opportunity employer",
    "notice to recruitment agencies",
    "application instructions",
)

# Lines containing these phrases are often footer/legal noise
_IGNORE_LINE_CONTAINS = (
    "click here to apply",
    "apply now",
    "no agencies please",
    "background check",
    "drug-free workplace",
)


# --- Core helpers ------------------------------------------------------------

def strip_html(text: str) -> str:
    """Remove simple HTML tags if the JD was copied from a website."""
    if "<" in text and ">" in text:
        text = _HTML_TAG_RE.sub(" ", text)
    return text


def normalize_bullets(text: str) -> str:
    """
    Normalize various bullet characters to a single "- " prefix.

    Example:
        "• Build ML models" -> "- Build ML models"
    """
    bullet_pattern = rf"[{re.escape(_BULLET_CHARS)}]\s*"
    return re.sub(bullet_pattern, "- ", text)


def is_boilerplate_line(line: str) -> bool:
    """
    Heuristic filter for lines that are likely boilerplate / legal / noise.
    You can safely adjust these rules for your data.
    """
    if not line:
        return False

    lower = line.strip().lower()

    for prefix in _IGNORE_LINE_PREFIXES:
        if lower.startswith(prefix):
            return True

    for phrase in _IGNORE_LINE_CONTAINS:
        if phrase in lower:
            return True

    # Very short lines with no letters (e.g., separators)
    if len(lower) <= 3 and not re.search(r"[a-z]", lower):
        return True

    return False


def normalize_whitespace_preserve_lines(text: str) -> str:
    """
    Collapse repeated spaces/tabs within lines, strip edges, and drop
    empty lines, but preserve one newline between logical lines.
    """
    cleaned_lines: list[str] = []

    for raw_line in text.splitlines():
        # Collapse whitespace within the line
        line = _WHITESPACE_RE.sub(" ", raw_line).strip()
        if line:
            cleaned_lines.append(line)

    # Join with a single newline between non-empty lines
    return "\n".join(cleaned_lines)


def drop_boilerplate_lines(text: str) -> str:
    """
    Remove lines that are likely boilerplate / legal footer / meta info.
    """
    kept: list[str] = []
    for line in text.splitlines():
        if not is_boilerplate_line(line):
            kept.append(line)
    return "\n".join(kept)


# --- Public API --------------------------------------------------------------

def preprocess_jd(raw_text: str, *, remove_boilerplate: bool = True) -> str:
    """
    Full preprocessing pipeline for a Job Description.

    Steps:
    1. Normalize newlines.
    2. Strip simple HTML tags.
    3. Normalize bullet characters to "- ".
    4. Optionally drop obvious boilerplate / legal lines.
    5. Normalize whitespace while preserving line structure.

    Returns:
        Clean JD text ready to send to an LLM prompt.
    """
    # 1. Normalize newline styles
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Strip HTML tags if present
    text = strip_html(text)

    # 3. Normalize bullets
    text = normalize_bullets(text)

    # 4. Optional: drop boilerplate/legal/footer lines
    if remove_boilerplate:
        text = drop_boilerplate_lines(text)

    # 5. Normalize whitespace but keep line breaks
    text = normalize_whitespace_preserve_lines(text)

    # Final trim
    return text.strip()


# --- CLI entrypoint ----------------------------------------------------------

def _read_from_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main(argv: Iterable[str] | None = None) -> None:
    """
    Simple CLI usage.

    Examples:
        python preprocess_JD.py raw_jd.txt
        cat raw_jd.txt | python preprocess_JD.py
    """
    args = list(argv) if argv is not None else sys.argv[1:]

    if args:
        raw = _read_from_file(args[0])
    else:
        # Read from stdin if no file provided
        raw = sys.stdin.read()

    cleaned = preprocess_jd(raw)
    sys.stdout.write(cleaned)


if __name__ == "__main__":
    main()
