"""
Resume Parser 
--------------------------------
Extracts clean, structured text from PDF resumes.

Why this matters:
- Raw PDF text is messy, unstructured, noisy.
- Clean structured text → LLM outputs become stable + deterministic.

Outputs:
{
    "skills_section": "...",
    "experience_section": "...",
    "education_section": "...",
    "raw_text": "..."
}
"""

import re
import fitz  # PyMuPDF
from config.settings import RESUME_SECTIONS, debug_log


class ResumeParser:

    def __init__(self):
        # Normalize bullet patterns
        self.bullet_pattern = re.compile(r"^[•\-▪–·\*]\s*")
        self.whitespace_pattern = re.compile(r"\s+")

    # ---------------------------------------------------------
    # Public method: PDF → structured text
    # ---------------------------------------------------------

    def parse(self, pdf_path: str) -> dict:
        debug_log(f"Parsing resume: {pdf_path}")

        raw_text = self._extract_pdf_text(pdf_path)
        cleaned_text = self._clean_text(raw_text)
        sections = self._split_into_sections(cleaned_text)

        debug_log("Resume parsing complete.")
        return {
            "raw_text": cleaned_text,
            "sections": sections
        }

    # ---------------------------------------------------------
    # Extract text from PDF
    # ---------------------------------------------------------

    def _extract_pdf_text(self, pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        text = ""

        for page_num, page in enumerate(doc, start=1):
            extracted = page.get_text("text")
            text += extracted + "\n"
            debug_log(f"Extracted page {page_num}")

        doc.close()
        return text

    # ---------------------------------------------------------
    # Clean & normalize extracted text
    # ---------------------------------------------------------

    def _clean_text(self, text: str) -> str:
        lines = text.split("\n")
        cleaned = []

        for line in lines:
            original = line
            line = line.strip()

            if not line:
                continue

            # Remove bullets
            line = self.bullet_pattern.sub("", line)

            # Normalize whitespace
            line = self.whitespace_pattern.sub(" ", line)

            cleaned.append(line)
            debug_log(f"Line cleaned: {original} → {line}")

        return "\n".join(cleaned)

    # ---------------------------------------------------------
    # Extract logical sections using headings
    # ---------------------------------------------------------

    def _split_into_sections(self, text: str) -> dict:
        lines = text.split("\n")

        current_section = "other"
        sections = {sec: "" for sec in RESUME_SECTIONS}
        sections["other"] = ""

        for line in lines:
            lower = line.lower()

            # Detect section headers
            for section in RESUME_SECTIONS:
                if lower.startswith(section):
                    current_section = section
                    debug_log(f"Detected resume section: {section}")
                    break
            else:
                # Add content into the active section
                sections[current_section] += line + "\n"

        return sections


# ---------------------------------------------------------
# Wrapper function for external modules
# ---------------------------------------------------------

def parse_resume(pdf_path: str) -> dict:
    parser = ResumeParser()
    return parser.parse(pdf_path)


# ---------------------------------------------------------
# Local test block
# ---------------------------------------------------------

if __name__ == "__main__":
    sample_pdf = "data/samples/sample_resume.pdf"
    print(parse_resume(sample_pdf))
