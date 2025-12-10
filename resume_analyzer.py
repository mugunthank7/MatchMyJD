#!/usr/bin/env python3

import os
import json
import sys
import re
from dotenv import load_dotenv
import google.generativeai as genai
from resume_parser import extract_resume_text     # your PDF extractor

MODEL_NAME = "gemini-2.5-flash"


# ---------------------- CLEAN JSON ------------------------
def extract_json(text: str) -> dict:
    """Extract valid JSON from Gemini output."""
    if not text:
        raise RuntimeError("Gemini returned empty response.")

    # Remove markdown
    text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise RuntimeError(f"Could not find JSON in response:\n{text}")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except Exception:
        raise RuntimeError(f"Gemini returned invalid JSON:\n\n{json_str}")


# ---------------------- PROMPT ----------------------------
def build_prompt(resume_text: str) -> str:
    return f"""
Extract the following fields from this resume and return VALID JSON ONLY:

- technical_skills
- soft_skills
- programming_languages
- tools_and_libraries
- experience_summary
- education
- certifications

Format EXACTLY:

{{
  "technical_skills": [],
  "soft_skills": [],
  "programming_languages": [],
  "tools_and_libraries": [],
  "experience_summary": [],
  "education": [],
  "certifications": []
}}

NO comments.
NO markdown.
NO explanation.

Resume:
{resume_text}
"""


# ---------------------- CONFIG ----------------------------
def configure_gemini():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")
    genai.configure(api_key=api_key)


# ---------------------- MAIN ANALYSIS ----------------------
def analyze_resume(resume_path: str):
    resume_text = extract_resume_text(resume_path)
    prompt = build_prompt(resume_text)

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    # Extract text from response
    try:
        text = response.text
    except:
        text = response.candidates[0].content.parts[0].text

    return extract_json(text)


# ---------------------- CLI -------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 resume_analyzer.py resume.pdf")
        sys.exit(1)

    resume_path = sys.argv[1]

    configure_gemini()
    result = analyze_resume(resume_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
