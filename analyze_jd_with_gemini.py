#!/usr/bin/env python3

import os
import json
import sys
import re
from dotenv import load_dotenv
import google.generativeai as genai
from preprocess_JD import preprocess_jd

MODEL_NAME = "gemini-2.5-flash"


# ---------------------- CLEAN JSON ------------------------
def extract_json(text: str) -> dict:
    """
    Removes markdown fences and extracts valid JSON.
    Works for all Gemini SDK versions.
    """
    if not text:
        raise RuntimeError("Gemini returned empty response.")

    # Remove ```json ... ```
    text = text.replace("```json", "").replace("```", "").strip()

    # Find first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise RuntimeError(f"Could not find JSON in response:\n{text}")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except Exception:
        raise RuntimeError(f"Gemini returned invalid JSON:\n\n{json_str}")


# ---------------------- PROMPT ----------------------------
def build_prompt(cleaned_jd: str) -> str:
    return f"""
You are an expert ATS job description parser. 
Extract ONLY actual technical skills and competencies — nothing else.

STRICT RULES:
- DO NOT extract responsibilities (e.g., "apply engineering principles", "collaborate", "work with teams")
- DO NOT extract eligibility requirements (e.g., "currently pursuing a degree", "must have 1 semester remaining")
- DO NOT extract soft statements (e.g., "ability to demonstrate", "quickly learns new methods")
- DO NOT extract general phrases like "problem solving" unless explicitly listed under skills.
- DO NOT extract full sentences.
- DO NOT extract company values or mission statements.

EXTRACT ONLY:
1. hard_skills  
   → Pure technical competencies (e.g., Data Structures, Algorithms, Software Engineering, Operating Systems, Distributed Systems)

2. tools_and_frameworks  
   → Actual tools/frameworks explicitly mentioned (e.g., Git, Linux, Java, Python, Docker)

3. domains  
   → Technical specialty areas (e.g., Software Engineering, Backend Systems, Cloud Infrastructure)

4. must_have_keywords  
   → Key technical requirements from the JD (ONLY skills — not requirements)

5. nice_to_have_keywords  
   → Optional technical skills or preferred qualifications


OUTPUT FORMAT (NO extra text, NO markdown):

{{
  "role_title": "",
  "seniority_level": "",
  "hard_skills": [],
  "tools_and_frameworks": [],
  "domains": [],
  "soft_skills": [],
  "key_responsibility_phrases": [],
  "must_have_keywords": [],
  "nice_to_have_keywords": []
}}

Job Description:
{cleaned_jd}
"""



# ---------------------- CONFIG ----------------------------
def configure_gemini():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")
    genai.configure(api_key=api_key)


# ---------------------- MAIN ANALYSIS ----------------------
def analyze_jd(raw_jd: str):
    cleaned = preprocess_jd(raw_jd)
    prompt = build_prompt(cleaned)

    model = genai.GenerativeModel(MODEL_NAME)

    response = model.generate_content(prompt)

    # Extract safely
    text = ""
    try:
        text = response.text
    except:
        # older SDK fallback
        text = response.candidates[0].content.parts[0].text

    return extract_json(text)


# ---------------------- CLI -------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_JD_with_gemini.py jd.txt")
        sys.exit(1)

    jd_path = sys.argv[1]
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_raw = f.read()

    configure_gemini()
    result = analyze_jd(jd_raw)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
