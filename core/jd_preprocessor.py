"""
JD Preprocessor
---------------
Cleaning and normalization module used by the MatchMyJD pipeline.

This converts raw noisy job descriptions from any website
into a clean, structured, machine-readable format.
"""

import re
from config.settings import STOPWORDS, debug_log


class JDPreprocessor:

    def __init__(self):
        # Regex patterns for cleaning
        self.bullet_pattern = re.compile(r"^[•\-▪–·\*]\s*")
        self.whitespace_pattern = re.compile(r"\s+")
        self.section_header_pattern = re.compile(
            r"(?i)^(responsibilities|requirements|qualifications|about the job|overview)\b"
        )

        # We treat Python specially inside JD to avoid misclassification later
        self.force_tool_terms = {"python"}

    # ---------------------------------------------------------
    # Main public method
    # ---------------------------------------------------------
    def preprocess(self, text: str) -> str:
        debug_log("Starting JD preprocessing...")

        if not text or len(text.strip()) == 0:
            return ""

        lines = text.split("\n")
        cleaned_lines = []
        seen = set()  # avoid duplicates

        for line in lines:
            original = line
            line = line.strip()

            if not line:
                continue

            # Remove bullets
            line = self.bullet_pattern.sub("", line)

            # Normalize whitespace
            line = self.whitespace_pattern.sub(" ", line)

            # Noise filtering
            if self._is_noise(line):
                continue

            # Normalize section headers
            if self.section_header_pattern.match(line.lower()):
                line = line.title()

            # Enforce skill normalization in-place (Python always treated as tool)
            lowered = line.lower()
            for term in self.force_tool_terms:
                if f"{term}" in lowered:
                    debug_log(f"Found special skill '{term}' in JD → normalized")
                    # does NOT replace the line, just logs the skill
                    # actual categorization happens in jd_analyzer
                    break

            # Deduplicate
            if line.lower() in seen:
                continue

            seen.add(line.lower())
            cleaned_lines.append(line)
            debug_log(f"Processed line: {original} → {line}")

        cleaned_text = "\n".join(cleaned_lines)
        debug_log("JD preprocessing complete.")
        return cleaned_text

    # ---------------------------------------------------------
    # Noise filtering logic
    # ---------------------------------------------------------
    def _is_noise(self, line: str) -> bool:

        noise_patterns = [
            r"^apply now",
            r"^click here",
            r"equal opportunity employer",
            r"drug free workplace",
            r"terms and conditions",
            r"privacy policy",
            r"job id[: ]",
            r"salary[: ]",
        ]

        for pattern in noise_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                debug_log(f"Removed noise line: {line}")
                return True

        # Remove lines that are only stopwords
        tokens = [t for t in line.lower().split() if t not in STOPWORDS]
        if len(tokens) == 0:
            debug_log(f"Removed stopword-only line: {line}")
            return True

        # Remove extremely short lines (<3 chars)
        if len(line) < 3:
            debug_log(f"Removed very short line: {line}")
            return True

        return False


# ---------------------------------------------------------
# Utility wrapper
# ---------------------------------------------------------

def preprocess_jd(text: str) -> str:
    processor = JDPreprocessor()
    return processor.preprocess(text)


# ---------------------------------------------------------
# Local test block
# ---------------------------------------------------------
if __name__ == "__main__":
    sample = """
    • Responsibilities
    - Write clean code
    • Apply strong problem solving skills
    Apply now
    Click here to apply
    Equal Opportunity Employer statement
    Python and Git required
    """

    print(preprocess_jd(sample))
