#!/usr/bin/env python3

"""
MatchMyJD Pipeline Runner
------------------------
End-to-end execution using:
- PDF → text resume parser
- Chunked LLM resume analyzer
- LLM JD analyzer
- Semantic matcher (embeddings)
- Human-aligned hybrid scorer
"""

import json
from utils.logger import get_logger

from core.resume_parser import parse_resume   # PDF → dict
from core.resume_analyzer import analyze_resume
from core.jd_analyzer import analyze_jd
from matching.matcher_semantic import semantic_match_structured
from matching.hybrid_scorer import compute_hybrid_score

logger = get_logger(__name__)

# -----------------------------------------------
# PATHS
# -----------------------------------------------
RESUME_PATH = "data/samples/sample_resume.pdf"
JD_PATH = "data/samples/sample_jd.txt"


# -----------------------------------------------
# Main Pipeline
# -----------------------------------------------
def run_pipeline():
    logger.info("🚀 Starting MatchMyJD pipeline...")

    # --- Resume ---
    resume_data = parse_resume(RESUME_PATH)

    # ✅ FIX: parser returns "raw_text", not "text"
    if isinstance(resume_data, dict):
        resume_text = resume_data.get("raw_text", "")
    else:
        resume_text = resume_data

    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("❌ Failed to extract resume text")

    resume_struct = analyze_resume(resume_text)

    # --- JD ---
    with open(JD_PATH, "r", encoding="utf-8") as f:
        jd_text = f.read()

    jd_struct = analyze_jd(jd_text)

    # --- Semantic Matching ---
    semantic_score = semantic_match_structured(jd_struct, resume_struct)

    # --- Hybrid Scoring ---
    final_result = compute_hybrid_score(
        jd_struct=jd_struct,
        resume_struct=resume_struct,
        semantic_score=semantic_score
    )

    return {
        "semantic_score": round(float(semantic_score), 3),
        **final_result
    }


# -----------------------------------------------
# CLI Entry
# -----------------------------------------------
if __name__ == "__main__":
    output = run_pipeline()

    print("\n==============================")
    print("📌 FINAL MATCH RESULT")
    print("==============================\n")
    print(json.dumps(output, indent=2, ensure_ascii=False))
