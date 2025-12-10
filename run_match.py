#!/usr/bin/env python3

import json
from analyze_jd_with_gemini import analyze_jd, configure_gemini  # your JD file
from resume_analyzer import analyze_resume                       # our working one
from matcher import match_jd_and_resume


def main():
    jd_path = "jd.txt"                      # or take from CLI if you prefer
    resume_path = "Mugunthan_Kesavan-2.pdf"

    # 1) Load JD text
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_raw = f.read()

    # 2) Configure Gemini once
    configure_gemini()

    # 3) Analyze JD & Resume
    print("🔍 Analyzing JD with Gemini...")
    jd_data = analyze_jd(jd_raw)

    print("📄 Analyzing Resume with Gemini...")
    resume_data = analyze_resume(resume_path)

    # 4) Match
    print("🤝 Matching JD & Resume...")
    match_result = match_jd_and_resume(jd_data, resume_data)

    # 5) Pretty print
    print("\n========== MATCH RESULT ==========\n")
    print(json.dumps(match_result, indent=2, ensure_ascii=False))

    print(f"\n✅ Match Score: {match_result['match_score']}%")


if __name__ == "__main__":
    main()
