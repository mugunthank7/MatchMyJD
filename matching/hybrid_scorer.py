"""
Hybrid Scorer
-------------
This module combines:
- Exact matching
- Fuzzy token similarity
- Semantic similarity (LLM)
into one weighted scoring function.

Final Output:
{
    "overall_score": float,
    "category_scores": {...},
    "matched": [...],
    "missing": [...],
    "extra": [...],
    "details": { ... per skill explanation ... }
}

This is the heart of MatchMyJD.
"""

from matching.matcher_exact import exact_match_score
from matching.matcher_fuzzy import fuzzy_similarity
from matching.matcher_semantic import semantic_similarity
from config.settings import CATEGORY_WEIGHTS, debug_log


# ---------------------------------------------------------
# Score one pair of skills (JD skill vs resume skill)
# ---------------------------------------------------------
def score_skill(jd_skill: str, resume_skill: str) -> dict:
    """
    Returns dict:
    {
        "exact": 0 or 1,
        "fuzzy": float,
        "semantic": float,
        "combined": float
    }
    """

    e = exact_match_score(jd_skill, resume_skill)
    f = fuzzy_similarity(jd_skill, resume_skill)
    s = semantic_similarity(jd_skill, resume_skill)

    # Weighted blending inside skill-level scoring
    combined = (0.5 * e) + (0.3 * f) + (0.2 * s)

    debug_log(f"[SCORE] {jd_skill} ↔ {resume_skill} = exact={e}, fuzzy={f:.3f}, semantic={s:.3f}, combined={combined:.3f}")

    return {
        "exact": e,
        "fuzzy": f,
        "semantic": s,
        "combined": combined
    }


# ---------------------------------------------------------
# Score an entire category (hard skills, soft skills, tools, domains)
# ---------------------------------------------------------
def score_category(category_name: str, jd_list: list, resume_list: list) -> dict:
    """
    Returns category-level:
    {
        "coverage": float,
        "matched": [...],
        "missing": [...],
        "extra": [...],
        "score": float,
        "details": {...}
    }
    """

    jd_set = set(jd_list)
    resume_set = set(resume_list)

    matched = []
    missing = []
    extra = list(resume_set - jd_set)

    details = {}
    total_combined = 0
    match_count = 0

    for jd_skill in jd_set:

        # Best matching resume skill for this JD skill
        best_resume = None
        best_score = 0
        best_detail = None

        for rs in resume_set:
            sc = score_skill(jd_skill, rs)
            if sc["combined"] > best_score:
                best_score = sc["combined"]
                best_resume = rs
                best_detail = sc

        if best_score >= 0.5:  # threshold for calling it a match
            matched.append(jd_skill)
            total_combined += best_score
            match_count += 1

        else:
            missing.append(jd_skill)

        details[jd_skill] = {
            "matched_with": best_resume,
            "scores": best_detail
        }

    coverage = match_count / max(len(jd_set), 1)
    weighted_score = CATEGORY_WEIGHTS.get(category_name, 1.0) * coverage

    debug_log(f"[CATEGORY] {category_name}: coverage={coverage:.3f}, weighted={weighted_score:.3f}")

    return {
        "coverage": coverage,
        "score": weighted_score,
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "details": details
    }


# ---------------------------------------------------------
# FINAL HYBRID SCORER (JD analysis + resume analysis)
# ---------------------------------------------------------
def hybrid_match(jd_data: dict, resume_data: dict) -> dict:
    """
    Main entry point.
    Expects normalized jd_data + resume_data:
    {
        "hard_skills": [...],
        "soft_skills": [...],
        "tools": [...],
        "domains": [...]
    }
    """

    debug_log("[HYBRID] Starting hybrid matching...")

    categories = ["hard_skills", "soft_skills", "tools_and_frameworks", "domains"]

    results = {}
    final_score = 0

    for cat in categories:
        jd_list = jd_data.get(cat, [])
        resume_list = resume_data.get(cat.replace("tools_and_frameworks", "tools"), resume_data.get(cat, []))

        res = score_category(cat, jd_list, resume_list)
        results[cat] = res
        final_score += res["score"]

    final_score = round(final_score * 100, 2)  # convert to percentage

    debug_log(f"[HYBRID] Final score = {final_score}")

    return {
        "overall_score": final_score,
        "categories": results
    }


# ---------------------------------------------------------
# Local test block
# ---------------------------------------------------------
if __name__ == "__main__":
    jd = {
        "hard_skills": ["python", "data structures", "algorithms"],
        "soft_skills": ["teamwork"],
        "tools": ["git", "docker"],
        "domains": ["software engineering"]
    }

    resume = {
        "hard_skills": ["python", "machine learning", "data structures"],
        "soft_skills": ["teamwork", "communication"],
        "tools": ["git", "docker"],
        "domains": ["software engineering", "data science"]
    }

    print(hybrid_match(jd, resume))
