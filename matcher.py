#!/usr/bin/env python3

import re
from typing import Dict, List, Set


# ---------- NORMALIZATION HELPERS ----------

def _normalize_skill(s: str) -> str:
    """
    Normalize skill strings for matching:
    - lowercase
    - strip spaces
    - collapse internal whitespace
    """
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _build_set(items: List[str]) -> Set[str]:
    return {_normalize_skill(x) for x in items if isinstance(x, str) and x.strip()}


# ---------- CORE MATCHING FUNCTION ----------

def match_jd_and_resume(jd_data: Dict, resume_data: Dict) -> Dict:
    """
    Simple overlap-based matcher.

    Expects:
      jd_data = output of analyze_jd(...)
      resume_data = output of analyze_resume(...)

    Returns:
      {
        "match_score": int (0-100),
        "jd_required_skills": [...],
        "resume_skills": [...],
        "matched_skills": [...],
        "missing_skills": [...],
        "extra_resume_skills": [...]
      }
    """

    # --- 1. Collect JD-side skills ---

    jd_hard = jd_data.get("hard_skills", []) or []
    jd_tools = jd_data.get("tools_and_frameworks", []) or []
    jd_must = jd_data.get("must_have_keywords", []) or []

    # You can tune this: domains can be treated as required or just context.
    jd_domains = jd_data.get("domains", []) or []

    # For now, treat hard skills + tools + must-have keywords as required.
    jd_required_raw: List[str] = jd_hard + jd_tools + jd_must

    # OPTIONAL: include domains if you want them in matching
    # jd_required_raw += jd_domains

    jd_required_norm = _build_set(jd_required_raw)

    # --- 2. Collect Resume-side skills ---

    r_tech = resume_data.get("technical_skills", []) or []
    r_tools = resume_data.get("tools_and_libraries", []) or []
    r_langs = resume_data.get("programming_languages", []) or []

    resume_skills_raw: List[str] = r_tech + r_tools + r_langs
    resume_skills_norm = _build_set(resume_skills_raw)

    # --- 3. Compute intersections and differences ---

    matched = jd_required_norm & resume_skills_norm
    missing = jd_required_norm - resume_skills_norm
    extra = resume_skills_norm - jd_required_norm

    # Avoid division by zero
    denom = max(len(jd_required_norm), 1)
    match_score = int(round(100 * len(matched) / denom))

    # --- 4. Build nice readable output (keep original casing for display) ---

    # Map normalized → original for JD & resume for prettier output
    def build_original_map(items: List[str]):
        m = {}
        for x in items:
            nx = _normalize_skill(x)
            if nx not in m:
                m[nx] = x.strip()
        return m

    jd_map = build_original_map(jd_required_raw)
    resume_map = build_original_map(resume_skills_raw)

    def to_pretty_list(norm_set, pref_map, fallback_map):
        pretty = []
        for n in sorted(norm_set):
            if n in pref_map:
                pretty.append(pref_map[n])
            elif n in fallback_map:
                pretty.append(fallback_map[n])
            else:
                pretty.append(n)
        return pretty

    jd_required_pretty = to_pretty_list(jd_required_norm, jd_map, resume_map)
    resume_pretty = to_pretty_list(resume_skills_norm, resume_map, jd_map)
    matched_pretty = to_pretty_list(matched, jd_map, resume_map)
    missing_pretty = to_pretty_list(missing, jd_map, resume_map)
    extra_pretty = to_pretty_list(extra, resume_map, jd_map)

    return {
        "match_score": match_score,
        "jd_required_skills": jd_required_pretty,
        "resume_skills": resume_pretty,
        "matched_skills": matched_pretty,
        "missing_skills": missing_pretty,
        "extra_resume_skills": extra_pretty,
    }
