"""
Embedding Service — Text representation builder & vector embedding generator
using Sentence Transformers (all-MiniLM-L6-v2).
"""

import hashlib
import logging
from typing import Any
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

import os

_MODEL_INSTANCE: Any = None


def _get_sentence_transformer_model() -> Any:
    """Lazy load SentenceTransformer model once on demand."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        if os.environ.get("USE_FALLBACK_EMBEDDINGS", "").lower() in ("1", "true", "yes"):
            logger.info("USE_FALLBACK_EMBEDDINGS active. Using deterministic fallback embedder.")
            _MODEL_INSTANCE = "FALLBACK"
            return _MODEL_INSTANCE

        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer model: %s", settings.EMBEDDING_MODEL_NAME)
            _MODEL_INSTANCE = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        except Exception as exc:
            logger.warning("Could not load SentenceTransformer (%s). Using fallback embedder.", exc)
            _MODEL_INSTANCE = "FALLBACK"
    return _MODEL_INSTANCE


def build_profile_text(profile_data: Any) -> str:
    """
    Combines structured candidate facts (skills, experience, summary, education)
    into a comprehensive, representative text block for vector encoding.
    """
    if hasattr(profile_data, "model_dump"):
        data = profile_data.model_dump(mode="json")
    elif isinstance(profile_data, dict):
        data = profile_data
    else:
        data = {}

    parts: list[str] = []

    # Title / Name
    full_name = data.get("full_name")
    if full_name:
        parts.append(f"Candidate: {full_name}")

    # Skills
    skills = data.get("skills", [])
    if skills:
        parts.append(f"Skills: {', '.join(skills)}")

    # Summary & Highlights
    prof_summary = data.get("professional_summary")
    if prof_summary:
        parts.append(f"Summary: {prof_summary}")

    career_snap = data.get("career_snapshot")
    if career_snap:
        parts.append(f"Career Snapshot: {career_snap}")

    key_highlights = data.get("key_highlights", [])
    if key_highlights:
        parts.append(f"Highlights: {' '.join(key_highlights)}")

    # Experience
    exp_list = data.get("experience", [])
    exp_texts = []
    for exp in exp_list:
        if isinstance(exp, dict):
            title = exp.get("title", "")
            company = exp.get("company", "")
            desc = exp.get("description", "")
            highlights = " ".join(exp.get("highlights", []))
            exp_texts.append(f"{title} at {company}. {desc} {highlights}".strip())
    if exp_texts:
        parts.append(f"Experience: {' | '.join(exp_texts)}")

    # Education
    edu_list = data.get("education", [])
    edu_texts = []
    for edu in edu_list:
        if isinstance(edu, dict):
            deg = edu.get("degree", "")
            inst = edu.get("institution", "")
            edu_texts.append(f"{deg} from {inst}".strip())
    if edu_texts:
        parts.append(f"Education: {', '.join(edu_texts)}")

    combined_text = "\n".join(parts).strip()
    return combined_text or "Candidate profile with unspecified technical skills."


def build_job_text(job_details: dict[str, Any]) -> str:
    """
    Combines job description fields into a representative text block for vector search.
    """
    parts: list[str] = []

    title = job_details.get("title")
    if title:
        parts.append(f"Job Title: {title}")

    req_skills = job_details.get("required_skills", [])
    if req_skills:
        parts.append(f"Required Skills: {', '.join(req_skills)}")

    opt_skills = job_details.get("optional_skills", [])
    if opt_skills:
        parts.append(f"Optional Skills: {', '.join(opt_skills)}")

    description = job_details.get("description")
    if description:
        parts.append(f"Description: {description}")

    combined_text = "\n".join(parts).strip()
    return combined_text or "Job description position seeking technical candidates."


def _generate_fallback_embedding(text: str, dimension: int = 384) -> list[float]:
    """
    Generates a deterministic L2-normalized 384-dimensional float vector
    from text tokens for testing environments without SentenceTransformers.
    """
    rng = np.random.RandomState(int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16))
    raw_vec = rng.randn(dimension).astype(np.float32)
    norm = np.linalg.norm(raw_vec)
    if norm > 0:
        raw_vec /= norm
    return raw_vec.tolist()


def generate_embedding(text: str) -> list[float]:
    """
    Encodes text into an L2-normalized 384-float vector.
    """
    model = _get_sentence_transformer_model()
    if model == "FALLBACK" or model is None:
        return _generate_fallback_embedding(text, dimension=settings.EMBEDDING_DIMENSION)

    try:
        vec = model.encode(text, normalize_embeddings=True)
        if isinstance(vec, np.ndarray):
            return vec.tolist()
        return list(vec)
    except Exception as exc:
        logger.warning("Error generating embedding with SentenceTransformers: %s. Using fallback.", exc)
        return _generate_fallback_embedding(text, dimension=settings.EMBEDDING_DIMENSION)
