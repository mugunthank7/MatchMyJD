"""
Skill Normalizer
-----------------------------
Purpose:
- Clean, unify, tokenize, normalize skill names
- Handle synonyms so matching becomes accurate
- Convert resume + JD skill lists into canonical form
"""

import re
from config.settings import debug_log


# -----------------------------------------------------------
# LEXICONS (expand over time)
# -----------------------------------------------------------

CANONICAL_SKILLS = {
    "data structures": ["ds", "data structures & algorithms", "dsa"],
    "algorithms": ["algo", "algorithmic thinking"],
    "machine learning": ["ml"],
    "deep learning": ["dl"],
    "nlp": ["natural language processing"],
    "speech": ["asr", "tts", "speech-to-speech translation"],
    "distributed systems": ["distributed computing"],
    "big data": ["big data analytics", "hadoop", "spark"],
}

PROGRAMMING_SYNONYMS = {
    "python": ["py"],
    "c++": ["cpp"],
    "r": [],
    "java": [],
    "scala": [],
    "sql": [],
}

# Merge into one dictionary
SYNONYMS = {**CANONICAL_SKILLS, **PROGRAMMING_SYNONYMS}


# -----------------------------------------------------------
# BASIC CLEANER
# -----------------------------------------------------------

def clean_skill(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9+]+", " ", s)     # keep alphanumerics & +
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# -----------------------------------------------------------
# MAP skill → canonical version
# -----------------------------------------------------------
def normalize_skill(skill: str) -> str:
    cleaned = clean_skill(skill)
    
    # --- SPECIAL RULES ---
    # Always treat Python as a tool, not a hard skill
    
    if cleaned == "python":
        return "python"   # normalized canonical form

    # Direct match
    if cleaned in SYNONYMS:
        return cleaned

    # Synonym lookup
    for canonical, variants in SYNONYMS.items():
        if cleaned == canonical:
            return canonical
        for v in variants:
            if cleaned == clean_skill(v):
                return canonical

    return cleaned  # fallback



# -----------------------------------------------------------
# Normalize a list
# -----------------------------------------------------------

def normalize_skill_list(skills: list[str]) -> list[str]:
    normalized = []
    for s in skills:
        ns = normalize_skill(s)
        normalized.append(ns)
        debug_log(f"Normalized: {s} → {ns}")
    return list(set(normalized))  # unique


# -----------------------------------------------------------
# DEMO (run as script)
# -----------------------------------------------------------

if __name__ == "__main__":
    sample = [
        "Data Structures & Algorithms",
        "DSA",
        "Python",
        "Py",
        "ASR",
        "Distributed Systems",
        "Distributed Computing"
    ]
    print(normalize_skill_list(sample))
