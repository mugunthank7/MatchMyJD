"""
JD Preprocessor
---------------
cleaning and normalization module
used by the MatchMyJD pipeline.

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

            # Normalize bullets
            line = self.bullet_pattern.sub("", line)

            # Normalize whitespace
            line = self.whitespace_pattern.sub(" ", line)

            # Remove lines that are pure noise
            if self._is_noise(line):
                continue

            # Keep section headers but normalized
            if self.section_header_pattern.match(line.lower()):
                line = line.title()

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

        # Generic trash patterns
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

        # Remove lines that are only stopwords or nearly empty
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
# Utility function for external modules
# ---------------------------------------------------------

def preprocess_jd(text: str) -> str:
    """
    Simple wrapper used by jd_analyzer.
    """
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
    Click here to apply
    Equal Opportunity Employer statement
    """

    print(preprocess_jd(sample))
