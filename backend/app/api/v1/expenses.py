from typing import List, Optional
from uuid import UUID
from datetime import date
import os
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.session import get_db
from app.models.user import User
from app.models.employee import Employee
from app.models.financial import ExpenseClaim, ExpenseReceipt, Reimbursement
from app.api.deps import get_current_user, get_current_tenant_id
from app.schemas.financial import (
    ExpenseCategoryCreate,
    ExpenseCategoryResponse,
    ExpensePolicyCreate,
    ExpensePolicyResponse,
    ExpenseClaimCreate,
    ExpenseClaimResponse,
    ReceiptUploadResponse,
    ReimbursementProcessRequest,
    ReimbursementResponse
)
from app.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["Phase 8: Expenses & Reimbursements"])


@router.post("/categories", response_model=ExpenseCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_category(
    data: ExpenseCategoryCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ExpenseService.create_category(db, tenant_id, data)


@router.get("/categories", response_model=List[ExpenseCategoryResponse])
async def get_expense_categories(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ExpenseService.get_categories(db, tenant_id)


@router.post("/policies", response_model=ExpensePolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_policy(
    data: ExpensePolicyCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ExpenseService.create_policy(db, tenant_id, data)


@router.post("/receipts/upload", response_model=ReceiptUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_expense_receipt(
    file: UploadFile = File(...),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    receipt = await ExpenseService.upload_receipt(db, tenant_id, current_user.id, file)
    return ReceiptUploadResponse(
        id=receipt.id,
        file_name=receipt.file_name,
        file_path=receipt.file_path,
        content_type=receipt.content_type,
        file_size=receipt.file_size
    )


@router.get("/receipts/{receipt_id}")
async def download_expense_receipt(
    receipt_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(ExpenseReceipt).where(
            and_(ExpenseReceipt.id == receipt_id, ExpenseReceipt.tenant_id == tenant_id)
        )
    )
    receipt = res.scalar_one_or_none()
    if not receipt or not os.path.exists(receipt.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt file not found.")

    return FileResponse(
        path=receipt.file_path,
        media_type=receipt.content_type,
        filename=receipt.file_name
    )


async def _get_or_create_employee(db: AsyncSession, tenant_id: UUID, user: User) -> Employee:
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


@router.post("/claims", response_model=ExpenseClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_claim(
    data: ExpenseClaimCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await _get_or_create_employee(db, tenant_id, current_user)
    return await ExpenseService.create_claim(db, tenant_id, emp.id, data)


@router.post("/claims/{claim_id}/submit", response_model=ExpenseClaimResponse)
async def submit_expense_claim(
    claim_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ExpenseService.submit_claim(db, tenant_id, claim_id)


@router.get("/claims", response_model=List[ExpenseClaimResponse])
async def get_expense_claims(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await _get_or_create_employee(db, tenant_id, current_user)

    query = select(ExpenseClaim).where(ExpenseClaim.tenant_id == tenant_id)
    if current_user.role not in ["COMPANY_ADMIN", "HR_ADMIN", "FINANCE_ADMIN"]:
        query = query.where(ExpenseClaim.employee_id == emp.id)

    res = await db.execute(query.order_by(ExpenseClaim.created_at.desc()))
    return list(res.scalars().all())


@router.get("/reimbursements", response_model=List[ReimbursementResponse])
async def get_reimbursements(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Reimbursement)
        .where(Reimbursement.tenant_id == tenant_id)
        .order_by(Reimbursement.created_at.desc())
    )
    return list(res.scalars().all())


@router.post("/reimbursements/{reimbursement_id}/process", response_model=ReimbursementResponse)
async def process_reimbursement(
    reimbursement_id: UUID,
    req: ReimbursementProcessRequest,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ExpenseService.process_reimbursement(db, tenant_id, reimbursement_id, req)
