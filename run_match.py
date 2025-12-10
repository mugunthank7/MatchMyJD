#!/usr/bin/env python3

"""
MatchMyJD Pipeline Runner
Loads API key from .env automatically.
Does NOT expose key at any point.
"""

import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

from config.settings import debug_log
from core.resume_analyzer import analyze_resume
from core.jd_analyzer import analyze_jd
from matching.hybrid_scorer import hybrid_match


# -----------------------------------------------
# PATHS
# -----------------------------------------------
RESUME_PATH = "data/samples/sample_resume.pdf"
JD_PATH = "data/samples/sample_jd.txt"


# -----------------------------------------------
# Load .env and configure Gemini
# -----------------------------------------------
def configure_gemini():
    # Load environment file
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY not found in .env")

    genai.configure(api_key=api_key)
    debug_log("Gemini client configured using key from .env")


# -----------------------------------------------
# Main Pipeline
# -----------------------------------------------
def run_pipeline():

    debug_log("🚀 Starting MatchMyJD pipeline...")

    configure_gemini()

    # Analyze Resume
    resume_data = analyze_resume(RESUME_PATH)

    # Analyze JD
    with open(JD_PATH, "r") as f:
        jd_text = f.read()

    jd_data = analyze_jd(jd_text)

    # Hybrid scoring
    result = hybrid_match(jd_data, resume_data)

    return result


if __name__ == "__main__":
    output = run_pipeline()

    print("\n==============================")
    print("📌 FINAL MATCH RESULT")
    print("==============================\n")
    print(json.dumps(output, indent=2, ensure_ascii=False))
