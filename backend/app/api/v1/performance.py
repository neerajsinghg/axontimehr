from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.employee import Employee
from app.api.deps import get_current_user
from app.services.performance_service import PerformanceService
from app.schemas.performance import (
    PerformanceCycleCreate,
    PerformanceCycleResponse,
    GoalCreate,
    GoalProgressUpdate,
    GoalResponse,
    SelfAssessmentSubmit,
    ManagerAssessmentSubmit,
    CalibrationSubmit,
    PerformanceReviewResponse,
)

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


@router.post("/cycles", response_model=PerformanceCycleResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_cycle(
    data: PerformanceCycleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await PerformanceService.create_cycle(db, tenant_id, data)


@router.get("/cycles", response_model=List[PerformanceCycleResponse])
async def get_performance_cycles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await PerformanceService.get_cycles(db, tenant_id)


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await PerformanceService.create_goal(db, tenant_id, data)


@router.get("/goals", response_model=List[GoalResponse])
async def get_goals(
    employee_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    emp_id = employee_id or await _get_employee_id(db, current_user)
    return await PerformanceService.get_goals(db, tenant_id, emp_id)


@router.post("/goals/{goal_id}/progress", response_model=GoalResponse)
async def update_goal_progress(
    goal_id: str,
    data: GoalProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await PerformanceService.update_goal_progress(db, goal_id, data)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.get("/reviews/my-review", response_model=PerformanceReviewResponse)
async def get_my_review(
    cycle_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    emp_id = await _get_employee_id(db, current_user)
    return await PerformanceService.get_or_create_review(db, tenant_id, cycle_id, emp_id)


@router.post("/reviews/{review_id}/self-assessment", response_model=PerformanceReviewResponse)
async def submit_self_assessment(
    review_id: str,
    data: SelfAssessmentSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await PerformanceService.submit_self_assessment(db, review_id, data)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/reviews/{review_id}/manager-assessment", response_model=PerformanceReviewResponse)
async def submit_manager_assessment(
    review_id: str,
    data: ManagerAssessmentSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await PerformanceService.submit_manager_assessment(db, review_id, data)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/calibration", response_model=PerformanceReviewResponse)
async def submit_calibration(
    data: CalibrationSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    calib_by = await _get_employee_id(db, current_user)
    try:
        return await PerformanceService.submit_calibration(db, tenant_id, calib_by, data)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
