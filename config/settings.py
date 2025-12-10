"""
MatchMyJD - Global Configuration Settings
-----------------------------------------

Every module in the system reads from this file.
No hardcoded values anywhere else.
Easy to tune, experiment, and improve match quality.
"""

# ============================================================
# 🔧 GEMINI MODEL CONFIGURATION
# ============================================================

GEMINI_MODEL_JD = "gemini-2.5-flash"
GEMINI_MODEL_RESUME = "gemini-2.5-flash"
GEMINI_MODEL_EMBEDDINGS = "gemini-embedding-001"   # for semantic similarity

MAX_TOKENS = 4096  # safe limit for responses

# ============================================================
# 🔧 MATCHING WEIGHTS
# ============================================================
# These weights determine the hybrid score calculation

WEIGHTS = {
    "exact_match": 0.30,       # direct string match
    "fuzzy_match": 0.20,       # token overlap similarity
    "semantic_match": 0.50     # embedding similarity
}

# Thresholds for final classification
THRESHOLDS = {
    "excellent": 0.80,
    "good": 0.60,
    "fair": 0.40,
    "poor": 0.20
}

# ============================================================
# 🔧 TEXT NORMALIZATION RULES
# ============================================================

# Convert variants → canonical names
SKILL_SYNONYMS = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "asr": "speech recognition",
    "data science": "data science",
    "big data": "big data",
    "ds": "data science",
    "s2s": "speech-to-speech",
    "speech2speech": "speech-to-speech",
    "neural networks": "deep learning",
    "nn": "deep learning",
    "stats": "statistics",
    "probability and statistics": "statistics",
}

# These will be stripped from skills
STOPWORDS = {
    "and", "or", "the", "basic", "knowledge", "experience", "with"
}

# ============================================================
# 🔧 RESUME SECTION HEADERS
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
# 🔧 LOGGING SETTINGS
# ============================================================

DEBUG = True     # global debug switch

# Simple debug printer
def debug_log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")
