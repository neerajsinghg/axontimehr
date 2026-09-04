from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.employee import Employee
from app.models.financial import SalaryAdvance
from app.api.deps import get_current_user, get_current_tenant_id
from app.schemas.financial import SalaryAdvanceCreate, SalaryAdvanceResponse
from app.services.advance_service import AdvanceService

router = APIRouter(prefix="/salary-advances", tags=["Phase 8: Salary Advances"])


async def _get_or_create_employee(db: AsyncSession, tenant_id: UUID, user: User) -> Employee:
    from datetime import date
    emp_res = await db.execute(select(Employee).where(Employee.user_id == user.id))
    emp = emp_res.scalar_one_or_none()
    if not emp:
        emp = Employee(
            organization_id=tenant_id,
            user_id=user.id,
            employee_id=f"EMP-{user.id.hex[:6].upper()}",
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            joining_date=date.today(),
            status="ACTIVE"
        )
        db.add(emp)
        await db.commit()
        await db.refresh(emp)
    return emp


@router.post("/", response_model=SalaryAdvanceResponse, status_code=status.HTTP_201_CREATED)
async def request_salary_advance(
    data: SalaryAdvanceCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await _get_or_create_employee(db, tenant_id, current_user)
    return await AdvanceService.request_advance(db, tenant_id, emp.id, data)


@router.get("/", response_model=List[SalaryAdvanceResponse])
async def get_salary_advances(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await _get_or_create_employee(db, tenant_id, current_user)

    query = select(SalaryAdvance).options(selectinload(SalaryAdvance.recoveries)).where(SalaryAdvance.tenant_id == tenant_id)
    if current_user.role not in ["COMPANY_ADMIN", "HR_ADMIN", "FINANCE_ADMIN"]:
        query = query.where(SalaryAdvance.employee_id == emp.id)

    res = await db.execute(query.order_by(SalaryAdvance.created_at.desc()))
    return list(res.scalars().all())


@router.post("/{advance_id}/disburse", response_model=SalaryAdvanceResponse)
async def disburse_salary_advance(
    advance_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await AdvanceService.disburse_advance(db, tenant_id, advance_id)
