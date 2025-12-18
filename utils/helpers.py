def split_resume_into_sections(text: str) -> dict:
    sections = {}
    current = "general"
    sections[current] = []

    for line in text.splitlines():
        l = line.strip().lower()
        if l in {
            "summary", "education", "experience", "projects",
            "technical skills", "skills", "publications",
            "leadership", "activities"
        }:
            current = l
            sections[current] = []
        else:
            sections[current].append(line)

    return {k: "\n".join(v) for k, v in sections.items()}
