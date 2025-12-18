"""
MatchMyJD - Global Configuration Settings
-----------------------------------------
NO API KEYS ARE LOADED INSIDE THIS FILE.
Only constants, weights, thresholds, and normalization rules.
"""

# ============================================================
# 🔧 GEMINI MODEL CONFIGURATION
# ============================================================

# LLMs
GEMINI_MODEL_JD = "gemini-2.5-flash"
GEMINI_MODEL_RESUME = "gemini-2.5-flash"

# (Kept for future use; not used in current pipeline)
GEMINI_MODEL_EMBEDDINGS = "gemini-embedding-001"

# Token limits
MAX_TOKENS_JD = 2048
MAX_TOKENS_RESUME = 4096

# ============================================================
# 🔧 SCORING CONFIGURATION (CURRENT PIPELINE)
# ============================================================

# These are used INSIDE hybrid_scorer (human-aligned)
HYBRID_SCORING = {
    "must_have_weight": 0.55,
    "semantic_weight": 0.30,
    "base_floor": 0.15,
    "nice_to_have_max_bonus": 0.15,
    "min_final_score": 35
}

# ============================================================
# 🔧 LEGACY MATCHING CONFIG (KEPT FOR BACKWARD COMPAT)
# ============================================================

# ⚠️ Not used in current pipeline, but retained so old imports don’t break
WEIGHTS = {
    "exact_match": 0.30,
    "fuzzy_match": 0.20,
    "semantic_match": 0.50,
}

CATEGORY_WEIGHTS = {
    "hard": 0.40,
    "tools": 0.20,
    "soft": 0.10,
    "domains": 0.30,
}

THRESHOLDS = {
    "excellent": 0.80,
    "good": 0.60,
    "fair": 0.40,
    "poor": 0.20,
}

# ============================================================
# 🔧 TEXT NORMALIZATION RULES
# ============================================================

SKILL_SYNONYMS = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "asr": "speech recognition",
    "s2s": "speech-to-speech",
    "nn": "deep learning",
    "stats": "statistics",
    "ds": "data science",
}

STOPWORDS = {
    "and", "or", "the", "basic", "knowledge", "experience", "with"
}

# ============================================================
# 🔧 RESUME SECTION HEADERS
# ============================================================

RESUME_SECTIONS = [
    "summary",
    "skills",
    "technical skills",
    "projects",
    "experience",
    "work experience",
    "education",
    "certifications",
    "publications",
    "leadership",
    "activities",
]

# ============================================================
# 🔧 DEBUG LOGGING
# ============================================================

DEBUG = True

def debug_log(msg: str):
    if DEBUG:
        print(f"[DEBUG] {msg}")
