from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.employee import Employee
from app.api.deps import get_current_user
from app.services.engagement_service import EngagementService
from app.schemas.performance import SurveyCreate, SurveyResponse as SurveySchemaResponse, SurveySubmitAnswer, EmployeeFeedbackCreate

router = APIRouter()


def _get_tenant_id(current_user: User):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an active organization tenant"
        )
    return current_user.tenant_id


async def _get_employee_id(db: AsyncSession, current_user: User) -> str:
    res = await db.execute(select(Employee).where(Employee.user_id == current_user.id))
    emp = res.scalar_one_or_none()
    return str(emp.id) if emp else str(current_user.id)


@router.post("/surveys", response_model=SurveySchemaResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(
    data: SurveyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await EngagementService.create_survey(db, tenant_id, data)


@router.get("/surveys", response_model=List[SurveySchemaResponse])
async def get_surveys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await EngagementService.get_surveys(db, tenant_id)


@router.post("/surveys/{survey_id}/respond", status_code=status.HTTP_200_OK)
async def submit_survey_response(
    survey_id: str,
    answers: List[SurveySubmitAnswer],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    emp_id = await _get_employee_id(db, current_user)
    try:
        await EngagementService.submit_response(db, tenant_id, survey_id, emp_id, answers)
        return {"success": True, "message": "Survey response submitted successfully"}
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    data: EmployeeFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    emp_id = await _get_employee_id(db, current_user)
    await EngagementService.create_feedback(db, tenant_id, emp_id, data)
    return {"success": True, "message": "Workplace feedback submitted successfully"}
