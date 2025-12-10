"""
MatchMyJD - Global Configuration Settings
-----------------------------------------
NO API KEYS ARE LOADED INSIDE THIS FILE.
Only constants, weights, and normalization rules.
"""
# ============================================================
# 🔧 GEMINI MODEL CONFIGURATION
# ============================================================

GEMINI_MODEL_JD = "gemini-2.5-flash"
GEMINI_MODEL_RESUME = "gemini-2.5-flash"
GEMINI_MODEL_EMBEDDINGS = "gemini-embedding-001"

MAX_TOKENS = 4096

# ============================================================
# 🔧 MATCHING WEIGHTS
# ============================================================

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
    "ds": "data science",
    "s2s": "speech-to-speech",
    "nn": "deep learning",
    "stats": "statistics",
}

STOPWORDS = {
    "and", "or", "the", "basic", "knowledge", "experience", "with"
}

# ============================================================
# 🔧 RESUME SECTIONS
# ============================================================

RESUME_SECTIONS = [
    "skills",
    "technical skills",
    "projects",
    "experience",
    "work experience",
    "education",
    "certifications",
    "publications",
]

# ============================================================
# 🔧 DEBUG LOGGING
# ============================================================

DEBUG = True

def debug_log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")
