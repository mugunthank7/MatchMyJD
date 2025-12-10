"""
Semantic Matcher (Embeddings)
-----------------------------
Uses Gemini embedding model to compute cosine similarity
between JD skills and Resume skills.

- No prompting
- No hallucinations
- Very fast and inexpensive
- Returns a score from 0.0 to 1.0
"""

import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai
from config.settings import debug_log

# ============================================================
# Load API key from .env
# ============================================================

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file.")

genai.configure(api_key=API_KEY)

# Official Gemini Embedding Model
EMBED_MODEL = "models/text-embedding-004"


# ============================================================
# Helper: Generate embedding for text
# ============================================================

def get_embedding(text: str):
    try:
        res = genai.embed_content(
            model=EMBED_MODEL,
            content=text
        )
        return np.array(res["embedding"], dtype=float)

    except Exception as e:
        debug_log(f"[EMBED ERROR] {e}")
        return np.zeros(768)  # safe fallback to avoid crashes


# ============================================================
# Helper: Cosine similarity
# ============================================================

def cosine_similarity(a, b):
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ============================================================
# Public API: semantic similarity score
# ============================================================

def semantic_similarity(skill_a: str, skill_b: str) -> float:
    emb_a = get_embedding(skill_a)
    emb_b = get_embedding(skill_b)

    score = cosine_similarity(emb_a, emb_b)

    # Clamp between 0 and 1
    score = max(0.0, min(1.0, score))

    debug_log(f"[SEMANTIC] '{skill_a}' ↔ '{skill_b}' = {score:.3f}")

    return score


# ============================================================
# Local testing
# ============================================================

if __name__ == "__main__":
    tests = [
        ("machine learning", "ML engineering"),
        ("python programming", "software development"),
        ("docker", "containerization"),
        ("data structures", "algorithms"),
        ("spark", "hadoop"),
        ("excel", "deep learning"),
    ]

    for a, b in tests:
        print(a, "<->", b, "=", semantic_similarity(a, b))
