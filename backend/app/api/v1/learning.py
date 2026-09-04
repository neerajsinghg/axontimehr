from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.employee import Employee
from app.api.deps import get_current_user
from app.services.learning_service import LearningService
from app.schemas.performance import (
    CourseCreate,
    CourseResponse,
    TrainingEnrollmentCreate,
    TrainingEnrollmentResponse,
    CertificationCreate,
    CertificationResponse,
    SkillUpdate,
    SkillResponse,
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


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await LearningService.create_course(db, tenant_id, data)


@router.get("/courses", response_model=List[CourseResponse])
async def get_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await LearningService.get_courses(db, tenant_id)


@router.get("/enrollments", response_model=List[TrainingEnrollmentResponse])
async def get_enrollments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    emp_id = await _get_employee_id(db, current_user)
    return await LearningService.get_enrollments(db, tenant_id, emp_id)


@router.post("/enrollments", response_model=TrainingEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_employee(
    data: TrainingEnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await LearningService.enroll_employee(db, tenant_id, data)


@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
async def create_certification(
    data: CertificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await LearningService.create_certification(db, tenant_id, data)


@router.get("/certifications", response_model=List[CertificationResponse])
async def get_certifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    emp_id = await _get_employee_id(db, current_user)
    return await LearningService.get_certifications(db, tenant_id, emp_id)


@router.post("/skills/update", response_model=SkillResponse)
async def update_skill(
    data: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    return await LearningService.update_skill(db, tenant_id, data)


@router.get("/skills/matrix", response_model=List[SkillResponse])
async def get_skills_matrix(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _get_tenant_id(current_user)
    emp_id = await _get_employee_id(db, current_user)
    return await LearningService.get_skills_matrix(db, tenant_id, emp_id)
