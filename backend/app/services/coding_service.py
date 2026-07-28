"""Coding practice bank and static code-quality feedback.

Code is never executed on the API server. Runtime sandboxing is a separate
production concern; this MVP evaluates structure and language-specific cues.
"""

from beanie import PydanticObjectId

from app.models.coding import CodingDifficulty, CodingLanguage, CodingSubmission
from app.schemas.coding import CodingQuestion, CodingSubmissionCreate, CodingSubmissionResponse


QUESTIONS = [
    CodingQuestion(id="two-sum-python", title="Two Sum", language=CodingLanguage.PYTHON, difficulty=CodingDifficulty.EASY,
        prompt="Return the indices of two numbers whose values add up to target.", starter_code="def two_sum(nums, target):\n    # write your solution\n    pass"),
    CodingQuestion(id="sql-active-users", title="Active Users", language=CodingLanguage.SQL, difficulty=CodingDifficulty.EASY,
        prompt="Write a query that returns users who have logged in during the last 30 days.", starter_code="SELECT\nFROM users\nWHERE"),
    CodingQuestion(id="api-cache-js", title="API Response Cache", language=CodingLanguage.JAVASCRIPT, difficulty=CodingDifficulty.MEDIUM,
        prompt="Implement an in-memory cache with a TTL for an async API call.", starter_code="async function getCached(key, fetcher) {\n  // write your solution\n}"),
]


def _question(question_id: str) -> CodingQuestion:
    for question in QUESTIONS:
        if question.id == question_id:
            return question
    raise ValueError("Unknown coding question")


def _response(submission: CodingSubmission) -> CodingSubmissionResponse:
    return CodingSubmissionResponse(id=str(submission.id), language=submission.language, difficulty=submission.difficulty,
        question_id=submission.question_id, question_title=submission.question_title, correctness_score=submission.correctness_score,
        code_quality_score=submission.code_quality_score, overall_score=submission.overall_score, feedback=submission.feedback,
        submitted_at=submission.submitted_at)


async def list_questions(language: CodingLanguage | None = None) -> list[CodingQuestion]:
    return [question for question in QUESTIONS if language is None or question.language == language]


async def submit(candidate_id: str, data: CodingSubmissionCreate) -> CodingSubmissionResponse:
    question = _question(data.question_id)
    if question.language != data.language:
        raise ValueError("The selected language does not match this question")
    code = data.code.strip()
    has_logic = any(marker in code.lower() for marker in ("return", "select", "for", "while", "map", "join"))
    correctness = 70 if has_logic else 25
    quality = 55
    feedback = ["Add a short explanation of your approach and complexity."]
    if len(code.splitlines()) >= 4:
        quality += 15
        feedback.append("The solution has a clear implementation structure.")
    if "#" in code or "//" in code or "--" in code:
        quality += 10
        feedback.append("Helpful comments improve maintainability.")
    if not has_logic:
        feedback.append("Implement the core algorithm or query before submitting.")
    submission = CodingSubmission(candidate_id=PydanticObjectId(candidate_id), language=data.language,
        difficulty=question.difficulty, question_id=question.id, question_title=question.title, code=code,
        correctness_score=correctness, code_quality_score=min(100, quality),
        overall_score=round((correctness * 0.7) + (min(100, quality) * 0.3)), feedback=feedback)
    await submission.insert()
    return _response(submission)


async def list_submissions(candidate_id: str) -> list[CodingSubmissionResponse]:
    rows = await CodingSubmission.find(CodingSubmission.candidate_id == PydanticObjectId(candidate_id)).sort("-submitted_at").to_list()
    return [_response(row) for row in rows]
