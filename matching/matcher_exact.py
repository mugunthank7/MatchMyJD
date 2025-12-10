"""
Exact Matcher
-------------
Performs direct exact string comparison between individual skills.
This version is designed for hybrid scoring (string → string),
NOT dictionary → dictionary.
"""

from config.settings import debug_log
from core.normalizer import normalize_skill


# ---------------------------------------------------------
# Normalize and check exact match
# ---------------------------------------------------------

def exact_match_score(jd_skill: str, resume_skill: str) -> float:
    """
    Returns:
    1.0 if normalized strings match exactly
    0.0 otherwise
    """

    if not jd_skill or not resume_skill:
        return 0.0

    a = normalize_skill(jd_skill)
    b = normalize_skill(resume_skill)

    score = 1.0 if a == b else 0.0

    debug_log(f"[EXACT] '{a}' ↔ '{b}' = {score}")

    return score
