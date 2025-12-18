"""
matching/hybrid_scorer.py
-------------------------
Human-aligned Hybrid Scorer

Inputs:
- Structured JD (LLM-extracted)
- Structured Resume (LLM-extracted)
- Semantic similarity score (embedding-based)

Design goals:
- Must-have skills dominate
- Nice-to-have only boosts
- Semantic similarity rescues good resumes
- Evidence increases confidence
- No single miss can nuke the score
"""

from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def _normalize_list(xs: List[str]) -> List[str]:
    return [x.lower().strip() for x in xs if isinstance(x, str)]


def _must_have_coverage(must_have: List[str], resume_pool: set) -> float:
    if not must_have:
        return 1.0
    matched = sum(1 for s in must_have if s.lower() in resume_pool)
    return matched / len(must_have)


def _nice_to_have_bonus(nice: List[str], resume_pool: set) -> float:
    if not nice:
        return 0.0
    matched = sum(1 for s in nice if s.lower() in resume_pool)
    # max +15%
    return min(0.15, matched * 0.05)


def _evidence_multiplier(skills_with_evidence: Dict[str, List[str]]) -> float:
    """
    Boost score if multiple skills have strong evidence.
    """
    if not skills_with_evidence:
        return 1.0

    strong = sum(1 for ev in skills_with_evidence.values() if len(ev) >= 2)
    if strong >= 4:
        return 1.12
    if strong >= 2:
        return 1.07
    return 1.0


# ---------------------------------------------------------
# MAIN SCORER
# ---------------------------------------------------------

def compute_hybrid_score(
    jd_struct: Dict[str, Any],
    resume_struct: Dict[str, Any],
    semantic_score: float
) -> Dict[str, Any]:
    """
    Returns:
    {
      "overall_score": int,
      "strengths": [...],
      "gaps": [...],
      "suggestions": [...]
    }
    """

    # --- JD ---
    must_have = _normalize_list(jd_struct.get("must_have_skills", []))
    nice_to_have = _normalize_list(jd_struct.get("nice_to_have_skills", []))

    # --- Resume ---
    skills_with_evidence = resume_struct.get("skills_with_evidence", {})
    resume_skills = _normalize_list(list(skills_with_evidence.keys()))
    resume_tools = _normalize_list(resume_struct.get("tools", []))

    resume_pool = set(resume_skills + resume_tools)

    # --- Core scores ---
    must_cov = _must_have_coverage(must_have, resume_pool)
    nice_bonus = _nice_to_have_bonus(nice_to_have, resume_pool)
    evidence_boost = _evidence_multiplier(skills_with_evidence)

    # Semantic safety net
    semantic_safe = max(semantic_score, 0.35)

    # --- Final score composition ---
    raw = (
        0.55 * must_cov +
        0.30 * semantic_safe +
        0.15          # baseline fairness
    )

    raw += nice_bonus
    raw *= evidence_boost

    final_score = int(max(35, min(100, raw * 100)))

    # -------------------------------------------------
    # EXPLANATION (HR-readable)
    # -------------------------------------------------

    strengths = []
    gaps = []
    suggestions = []

    for s in must_have:
        if s in resume_pool:
            strengths.append(f"Strong evidence for required skill: {s}")
        else:
            gaps.append(s)
            suggestions.append(f"Build hands-on experience with {s}")

    if semantic_score >= 0.6:
        strengths.append("Projects align well with job responsibilities")

    if skills_with_evidence:
        strengths.append("Skills are backed by concrete project or work evidence")

    logger.info(
        f"[HYBRID] score={final_score} | must_cov={must_cov:.2f} "
        f"semantic={semantic_score:.2f} evidence_boost={evidence_boost}"
    )

    return {
        "overall_score": final_score,
        "strengths": strengths,
        "gaps": gaps,
        "suggestions": suggestions
    }
