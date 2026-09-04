from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.employee import Employee
from app.models.financial import EmployeeLoan
from app.api.deps import get_current_user, get_current_tenant_id
from app.schemas.financial import (
    LoanTypeCreate,
    LoanTypeResponse,
    EmployeeLoanCreate,
    EmployeeLoanResponse,
    LoanInstallmentResponse,
    LoanPrepayRequest
)
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["Phase 8: Employee Loans"])


@router.post("/types", response_model=LoanTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_loan_type(
    data: LoanTypeCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await LoanService.create_loan_type(db, tenant_id, data)


@router.get("/types", response_model=List[LoanTypeResponse])
async def get_loan_types(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await LoanService.get_loan_types(db, tenant_id)


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


@router.post("/requests", response_model=EmployeeLoanResponse, status_code=status.HTTP_201_CREATED)
async def request_employee_loan(
    data: EmployeeLoanCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await _get_or_create_employee(db, tenant_id, current_user)
    return await LoanService.request_loan(db, tenant_id, emp.id, data)


@router.get("/requests", response_model=List[EmployeeLoanResponse])
async def get_employee_loans(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await _get_or_create_employee(db, tenant_id, current_user)

    query = select(EmployeeLoan).options(selectinload(EmployeeLoan.installments)).where(EmployeeLoan.tenant_id == tenant_id)
    if current_user.role not in ["COMPANY_ADMIN", "HR_ADMIN", "FINANCE_ADMIN"]:
        query = query.where(EmployeeLoan.employee_id == emp.id)

    res = await db.execute(query.order_by(EmployeeLoan.created_at.desc()))
    return list(res.scalars().all())


@router.post("/{loan_id}/disburse", response_model=EmployeeLoanResponse)
async def disburse_employee_loan(
    loan_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await LoanService.disburse_loan(db, tenant_id, loan_id)


@router.post("/{loan_id}/prepay", response_model=EmployeeLoanResponse)
async def prepay_employee_loan(
    loan_id: UUID,
    req: LoanPrepayRequest,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await LoanService.prepay_loan(db, tenant_id, loan_id, req.amount)
