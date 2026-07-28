"""Career-coach responses with persistent history; ready to swap to an LLM provider."""

from beanie import PydanticObjectId

from app.models.coach import CoachMessage
from app.schemas.coach import CoachMessageResponse, CoachQuestion


def _answer(question: str) -> str:
    lower = question.lower()
    if "resume" in lower:
        return "Start with the role you want, then make each bullet show action, scope, and a measurable outcome. Use the Resume Center scorecard to prioritise missing keywords."
    if "interview" in lower:
        return "Choose one target role, practise three questions, and answer with Situation, Task, Action, Result. Review the score and improve one specific point in the next session."
    if "skill" in lower or "learn" in lower:
        return "Pick one skill gap connected to target jobs, build a small project around it, document the result, then add that evidence to your resume and portfolio."
    return "Break this into a one-week goal: define the target outcome, choose one measurable action each day, and review your progress at the end of the week."


def _response(message: CoachMessage) -> CoachMessageResponse:
    return CoachMessageResponse(id=str(message.id), question=message.question, answer=message.answer, created_at=message.created_at)


async def ask(candidate_id: str, data: CoachQuestion) -> CoachMessageResponse:
    message = CoachMessage(candidate_id=PydanticObjectId(candidate_id), question=data.question, answer=_answer(data.question))
    await message.insert()
    return _response(message)


async def history(candidate_id: str) -> list[CoachMessageResponse]:
    rows = await CoachMessage.find(CoachMessage.candidate_id == PydanticObjectId(candidate_id)).sort("-created_at").to_list()
    return [_response(row) for row in rows]
