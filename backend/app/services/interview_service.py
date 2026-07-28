"""Question generation and lightweight feedback for practice interviews."""

from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.models.interview import InterviewSession
from app.schemas.interview import InterviewCreate, InterviewResponse, InterviewSubmit


def _questions_for(data: InterviewCreate) -> list[str]:
    context = f" for a {data.position}" if data.position else ""
    bank = {
        "technical": [
            f"Explain a core {data.topic} concept and when you would use it{context}.",
            f"Describe a production problem you would solve with {data.topic}.",
            f"What trade-offs would you consider when working with {data.topic}?",
        ],
        "hr": [
            "Tell me about yourself and the direction you want your career to take.",
            "Describe a strength that makes you effective in a team.",
            "What kind of role and environment help you do your best work?",
        ],
        "behavioral": [
            "Tell me about a difficult situation and the action you took.",
            "Describe a conflict in a team and how you resolved it.",
            "Share an example of a decision you made with incomplete information.",
        ],
        "company_specific": [
            f"Why do you want to work at {data.company or 'this company'}?",
            f"How would your {data.topic} experience help this team?",
            "What would you aim to learn in your first 90 days?",
        ],
    }
    return bank[data.interview_type.value][: data.question_count]


def _response(session: InterviewSession) -> InterviewResponse:
    return InterviewResponse(
        id=str(session.id), interview_type=session.interview_type, topic=session.topic,
        company=session.company, position=session.position, questions=session.questions,
        answers=session.answers, feedback=session.feedback, overall_score=session.overall_score,
        completed_at=session.completed_at, created_at=session.created_at,
    )


async def start_interview(candidate_id: str, data: InterviewCreate) -> InterviewResponse:
    session = InterviewSession(
        candidate_id=PydanticObjectId(candidate_id), interview_type=data.interview_type,
        topic=data.topic, company=data.company, position=data.position, questions=_questions_for(data),
    )
    await session.insert()
    return _response(session)


async def list_interviews(candidate_id: str) -> list[InterviewResponse]:
    candidate_oid = PydanticObjectId(candidate_id)
    sessions = await InterviewSession.find(InterviewSession.candidate_id == candidate_oid).sort("-created_at").to_list()
    return [_response(session) for session in sessions]


async def submit_interview(candidate_id: str, interview_id: str, data: InterviewSubmit) -> InterviewResponse:
    candidate_oid = PydanticObjectId(candidate_id)
    session = await InterviewSession.find_one(
        InterviewSession.id == PydanticObjectId(interview_id), InterviewSession.candidate_id == candidate_oid
    )
    if not session:
        from app.core.exceptions import EntityNotFoundError
        raise EntityNotFoundError(entity="Interview session", identifier=interview_id)

    answer_lengths = [len(answer.split()) for answer in data.answers]
    average_length = sum(answer_lengths) / len(answer_lengths)
    session.overall_score = min(100, max(35, int(45 + average_length * 1.5)))
    session.answers = data.answers
    session.feedback = [
        "Use the STAR structure to make behavioural answers easier to follow.",
        "Add a concrete result or metric to strengthen each answer.",
    ] if average_length < 60 else [
        "Your answers have useful detail. Lead with the outcome, then explain your approach.",
        "Keep using concrete outcomes and role-specific terminology.",
    ]
    session.completed_at = datetime.now(timezone.utc)
    await session.save()
    return _response(session)
