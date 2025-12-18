import json
from pathlib import Path
from utils.json_extractor import extract_json_block
from utils.logger import get_logger

logger = get_logger(__name__)

SCHEMA_DIR = Path("schemas")


def load_schema(schema_name: str) -> dict:
    with open(SCHEMA_DIR / schema_name, "r") as f:
        return json.load(f)


def call_llm(prompt: str) -> str:
    """
    TEMP implementation.
    Replace this with OpenAI / Ollama / Together / Groq call.
    """
    raise NotImplementedError("LLM call not wired yet")


def extract_with_schema(text: str, schema_file: str, system_prompt: str) -> dict:
    schema = load_schema(schema_file)

    prompt = f"""
{system_prompt}

TEXT:
{text}

Return ONLY valid JSON that strictly follows this schema:
{json.dumps(schema, indent=2)}
"""

    raw_response = call_llm(prompt)

    json_data = extract_json_block(raw_response)
    if not json_data:
        raise ValueError("Failed to extract JSON from LLM response")

    return json_data
def extract_jd_structured(jd_text: str) -> dict:
    system_prompt = """
You are an expert technical recruiter.
Extract job requirements clearly.
Classify skills strictly as must-have or nice-to-have.
Infer seniority conservatively.
"""
    return extract_with_schema(
        jd_text,
        "jd_schema.json",
        system_prompt
    )
def extract_resume_structured(resume_text: str) -> dict:
    system_prompt = """
You are an expert resume reviewer.
Extract skills ONLY if evidence is present.
Map each skill to where it appears (project, internship, coursework).
"""
    return extract_with_schema(
        resume_text,
        "resume_schema.json",
        system_prompt
    )
