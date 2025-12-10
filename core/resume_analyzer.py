import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from utils.json_extractor import extract_json_from_text as extract_json
from core.resume_parser import parse_resume as extract_resume_text

from config.settings import GEMINI_MODEL_RESUME, debug_log

# -----------------------------
# BUILD RESUME PROMPT (1 CALL)
# -----------------------------
def build_resume_prompt(raw_text: str) -> str:
    return f"""
Extract the following structured information from this resume.
Return STRICT JSON ONLY. No markdown, no commentary.

Fields to extract:

{{
  "technical_skills": [],
  "tools_and_frameworks": [],
  "programming_languages": [],
  "domains": [],
  "soft_skills": [],
  "experience_summary": [],
  "education": [],
  "certifications": []
}}

Resume Text:
{raw_text}
"""


# -----------------------------
# CONFIGURE GEMINI
# -----------------------------
def configure_gemini():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")
    genai.configure(api_key=api_key)
    debug_log("Configured Gemini client for resume analyzer.")


# -----------------------------
# MAIN ANALYZER (1 CALL)
# -----------------------------
def analyze_resume(pdf_path: str):
    debug_log(f"Starting single-shot resume analysis for: {pdf_path}")

    # 1) Extract raw resume text (PDF → text)
    raw_text = extract_resume_text(pdf_path)

    # 2) Build prompt
    prompt = build_resume_prompt(raw_text)

    # 3) Call Gemini once
    model = genai.GenerativeModel(GEMINI_MODEL_RESUME)
    response = model.generate_content(prompt)

    # 4) Extract TEXT safely
    try:
        text = response.text
    except:
        text = response.candidates[0].content.parts[0].text

    debug_log("Raw LLM output (truncated): " + text[:300])

    # 5) Convert to JSON
    result = extract_json(text)

    debug_log("Resume analysis complete.")
    return result


# -----------------------------
# CLI Usage
# -----------------------------
if __name__ == "__main__":
    configure_gemini()
    pdf = "data/samples/sample_resume.pdf"
    result = analyze_resume(pdf)
    print(json.dumps(result, indent=2))
