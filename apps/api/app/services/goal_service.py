"""Goal planner and career-progress aggregation."""

from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.core.exceptions import EntityNotFoundError
from app.models.goal import CareerGoal, GoalStatus
from app.models.interview import InterviewSession
from app.schemas.goal import CareerProgressResponse, GoalCreate, GoalProgressUpdate, GoalResponse


def _response(goal: CareerGoal) -> GoalResponse:
    return GoalResponse(id=str(goal.id), title=goal.title, category=goal.category, target_value=goal.target_value,
        current_value=goal.current_value, unit=goal.unit, due_date=goal.due_date, status=goal.status,
        created_at=goal.created_at, updated_at=goal.updated_at)


async def create_goal(candidate_id: str, data: GoalCreate) -> GoalResponse:
    goal = CareerGoal(candidate_id=PydanticObjectId(candidate_id), **data.model_dump())
    await goal.insert()
    return _response(goal)


async def list_goals(candidate_id: str) -> list[GoalResponse]:
    goals = await CareerGoal.find(CareerGoal.candidate_id == PydanticObjectId(candidate_id)).sort("-updated_at").to_list()
    return [_response(goal) for goal in goals]


async def update_goal_progress(candidate_id: str, goal_id: str, data: GoalProgressUpdate) -> GoalResponse:
    goal = await CareerGoal.find_one(CareerGoal.id == PydanticObjectId(goal_id), CareerGoal.candidate_id == PydanticObjectId(candidate_id))
    if not goal:
        raise EntityNotFoundError(entity="Goal", identifier=goal_id)
    goal.current_value = data.current_value
    goal.status = data.status or (GoalStatus.COMPLETED if data.current_value >= goal.target_value else goal.status)
    goal.updated_at = datetime.now(timezone.utc)
    await goal.save()
    return _response(goal)


async def get_progress(candidate_id: str) -> CareerProgressResponse:
    candidate_oid = PydanticObjectId(candidate_id)
    goals = await CareerGoal.find(CareerGoal.candidate_id == candidate_oid).to_list()
    interviews = await InterviewSession.find(InterviewSession.candidate_id == candidate_oid).to_list()
    completed = [session for session in interviews if session.overall_score is not None]
    average_score = round(sum(session.overall_score or 0 for session in completed) / len(completed), 1) if completed else None
    achievements: list[str] = []
    if completed:
        achievements.append("First mock interview completed")
    if len(completed) >= 10:
        achievements.append("10 mock interviews completed")
    if any(goal.status == GoalStatus.COMPLETED for goal in goals):
        achievements.append("Career goal achieved")
    return CareerProgressResponse(active_goals=sum(goal.status == GoalStatus.ACTIVE for goal in goals),
        completed_goals=sum(goal.status == GoalStatus.COMPLETED for goal in goals),
        completed_interviews=len(completed), interview_average_score=average_score, achievements=achievements)
