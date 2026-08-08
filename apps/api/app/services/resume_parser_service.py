"""
Resume Parser Service — Regex & NLP extraction for candidate contact info,
skill matrix matching, and ATS quality score calculation.
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Standard Tech Skills Dictionary for Matching
TECH_SKILLS_DICTIONARY = [
    "Python", "FastAPI", "Django", "Flask", "React", "TypeScript", "JavaScript",
    "Node.js", "Express", "MongoDB", "PostgreSQL", "MySQL", "Redis", "Docker",
    "Kubernetes", "AWS", "GCP", "Azure", "PyTorch", "TensorFlow", "scikit-learn",
    "OpenCV", "PyMuPDF", "Beanie", "Pydantic", "Tailwind CSS", "HTML5", "CSS3",
    "Git", "GitHub", "CI/CD", "REST API", "GraphQL", "Java", "C++", "C#", "Go",
    "Rust", "SQL", "Pandas", "NumPy", "NLP", "Machine Learning", "Deep Learning",
    "System Design", "Microservices", "Linux", "Bash", "Terraform", "Ansible", "Figma"
]

# High-impact Action Verbs for ATS Feedback
ACTION_VERBS = [
    "Architected", "Engineered", "Developed", "Implemented", "Optimized",
    "Deployed", "Scaled", "Automated", "Orchestrated", "Led", "Streamlined"
]


def extract_email(text: str) -> str | None:
    """Extracts email address using regex."""
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Extracts phone number using regex."""
    pattern = r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_skills(text: str) -> list[str]:
    """Matches text against tech skills dictionary (case-insensitive word boundary)."""
    text_lower = text.lower()
    found_skills: list[str] = []

    for skill in TECH_SKILLS_DICTIONARY:
        skill_lower = skill.lower()
        if skill_lower in ["c++", "c#"]:
            pattern = r"(?:\b|_)" + re.escape(skill_lower) + r"(?:\b|_|\s|,|\.|$)"
        else:
            pattern = r"\b" + re.escape(skill_lower) + r"\b"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def calculate_ats_metrics(
    text: str,
    extracted_email: str | None,
    extracted_phone: str | None,
    skills: list[str],
    page_count: int,
) -> tuple[int, dict[str, int], dict[str, Any]]:
    """
    Calculates ATS Score (0 - 100) and AI quality feedback.
    """
    completeness_score = 0
    if extracted_email:
        completeness_score += 40
    if extracted_phone:
        completeness_score += 20
    if len(text) > 300:
        completeness_score += 40
    completeness_score = min(100, completeness_score)

    # Keyword Density Score (based on tech skills found)
    skill_count = len(skills)
    keyword_score = min(100, int((skill_count / 8.0) * 100))

    # Formatting Score (length, page count, structure)
    formatting_score = 90
    if page_count > 3:
        formatting_score -= 20
    if len(text) < 150:
        formatting_score -= 40

    # Overall Weighted ATS Score
    overall_ats_score = int(
        (completeness_score * 0.35) + (keyword_score * 0.45) + (formatting_score * 0.20)
    )
    overall_ats_score = max(10, min(99, overall_ats_score))

    quality_breakdown = {
        "completeness_score": completeness_score,
        "keyword_density_score": keyword_score,
        "formatting_score": formatting_score,
    }

    # AI Suggestions
    missing_elements: list[str] = []
    if not extracted_email:
        missing_elements.append("Email address not clearly formatted for ATS scanners.")
    if not extracted_phone:
        missing_elements.append("Phone number missing or unrecognized format.")
    if skill_count < 5:
        missing_elements.append("Add more explicit technical skill keywords (e.g. FastAPI, React, SQL).")

    action_verb_suggestions = [
        verb for verb in ACTION_VERBS if verb.lower() not in text.lower()
    ][:4]

    formatting_tips = []
    if page_count > 2:
        formatting_tips.append("Consider condensing resume to 1-2 pages for maximum recruiter retention.")
    if len(text) < 300:
        formatting_tips.append("Expand section bullet points with quantifiable metrics and impact numbers.")

    ai_feedback = {
        "missing_elements": missing_elements,
        "action_verb_suggestions": action_verb_suggestions,
        "formatting_tips": formatting_tips,
    }

    return overall_ats_score, quality_breakdown, ai_feedback
