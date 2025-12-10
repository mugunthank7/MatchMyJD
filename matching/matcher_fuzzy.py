"""
Fuzzy Matcher
-------------
Computes similarity between JD skills and Resume skills
using token-based Jaccard similarity.

Used as a middle layer between EXACT matching
and SEMANTIC (LLM-based) matching.

Output: score between 0.0 → 1.0
"""

import re
from config.settings import STOPWORDS, debug_log
from core.normalizer import clean_skill


# ---------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------
def tokenize(text: str):
    """Convert text into normalized tokens."""
    cleaned = clean_skill(text)
    tokens = re.split(r"[ \-/_,]+", cleaned)

    return set(t for t in tokens if t and t not in STOPWORDS)


# ---------------------------------------------------------
# Jaccard similarity
# ---------------------------------------------------------
def jaccard_similarity(a: str, b: str) -> float:
    """Basic token-overlap similarity metric."""
    a_tokens = tokenize(a)
    b_tokens = tokenize(b)

    if not a_tokens or not b_tokens:
        return 0.0

    intersection = a_tokens & b_tokens
    union = a_tokens | b_tokens

    score = len(intersection) / len(union)
    return score


# ---------------------------------------------------------
# Public fuzzy matcher
# ---------------------------------------------------------
def fuzzy_match_skill(skill_from_jd: str, skill_from_resume: str) -> float:
    """
    Compute fuzzy similarity (0 → 1).
    Higher score = more similar.
    """
    score = jaccard_similarity(skill_from_jd, skill_from_resume)
    debug_log(f"Fuzzy score for '{skill_from_jd}' ↔ '{skill_from_resume}' = {score:.3f}")
    return score


# ---------------------------------------------------------
# Alias function used by hybrid_scorer
# ---------------------------------------------------------
def fuzzy_similarity(a: str, b: str) -> float:
    """
    Compatibility wrapper.
    hybrid_scorer expects this exact function name.
    """
    return fuzzy_match_skill(a, b)


# ---------------------------------------------------------
# Local test block
# ---------------------------------------------------------
if __name__ == "__main__":
    tests = [
        ("software engineering", "software engineer"),
        ("python scripting", "python development"),
        ("machine learning", "ml"),
        ("data structures", "data structure"),
        ("data pipelines", "big data pipelines"),
    ]

    for a, b in tests:
        print(a, "<->", b, "=", fuzzy_similarity(a, b))
