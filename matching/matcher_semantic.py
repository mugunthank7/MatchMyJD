"""
matching/matcher_semantic.py
----------------------------
Semantic matcher using sentence embeddings.

Outputs a semantic similarity score in [0, 1] between:
- JD responsibilities/skills
- Resume projects/evidence/skills
"""

from __future__ import annotations

from typing import List, Dict, Any
import math

from utils.logger import get_logger

logger = get_logger(__name__)

_MODEL = None


# ---------------------------------------------------------
# Lazy load sentence transformer
# ---------------------------------------------------------
def _lazy_load_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(model_name)
        logger.info(f"Loaded semantic model: {model_name}")
    return _MODEL


# ---------------------------------------------------------
# Cosine similarity (no numpy dependency)
# ---------------------------------------------------------
def _cosine(a: List[float], b: List[float]) -> float:
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


# ---------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------
def _embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    model = _lazy_load_model()

    # IMPORTANT: returns List[List[float]]
    return model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).tolist()


# ---------------------------------------------------------
# Resume evidence flattening
# ---------------------------------------------------------
def _flatten_resume_evidence(skills_with_evidence: Dict[str, List[str]]) -> List[str]:
    chunks: List[str] = []
    for skill, evidences in (skills_with_evidence or {}).items():
        if not skill:
            continue
        if evidences:
            for e in evidences:
                if e and isinstance(e, str):
                    chunks.append(f"{skill}: {e}")
        else:
            chunks.append(skill)
    return chunks


# ---------------------------------------------------------
# Pairwise similarity
# ---------------------------------------------------------
def _pairwise_max_similarity(A: List[str], B: List[str]) -> float:
    if not A or not B:
        return 0.0

    embA = _embed_texts(A)
    embB = _embed_texts(B)

    best = 0.0
    for va in embA:
        for vb in embB:
            s = _cosine(va, vb)
            if s > best:
                best = s

    return max(0.0, min(1.0, best))


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def semantic_match_structured(jd_struct: Dict[str, Any], resume_struct: Dict[str, Any]) -> float:
    jd_responsibilities = jd_struct.get("responsibilities", []) or []
    jd_must = jd_struct.get("must_have_skills", []) or []
    jd_nice = jd_struct.get("nice_to_have_skills", []) or []

    resume_projects = resume_struct.get("projects", []) or []
    resume_tools = resume_struct.get("tools", []) or []
    resume_evidence_map = resume_struct.get("skills_with_evidence", {}) or {}

    resume_evidence_chunks = _flatten_resume_evidence(resume_evidence_map)

    resp_vs_projects = _pairwise_max_similarity(
        jd_responsibilities,
        resume_projects + resume_evidence_chunks
    )

    skills_vs_resume = _pairwise_max_similarity(
        jd_must + jd_nice,
        list(resume_evidence_map.keys()) + resume_tools
    )

    semantic_score = 0.65 * resp_vs_projects + 0.35 * skills_vs_resume
    semantic_score = max(0.0, min(1.0, semantic_score))

    logger.info(
        f"Semantic score: {semantic_score:.3f} | "
        f"resp_vs_projects={resp_vs_projects:.3f} "
        f"skills_vs_resume={skills_vs_resume:.3f}"
    )

    return semantic_score
