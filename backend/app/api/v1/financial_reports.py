from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.session import get_db
from app.models.user import User
from app.models.employee import Employee
from app.models.financial import (
    ExpenseClaim,
    ExpenseClaimStatus,
    Reimbursement,
    ReimbursementStatus,
    EmployeeLoan,
    LoanStatus,
    LoanInstallment,
    InstallmentStatus,
    SalaryAdvance,
    SalaryAdvanceStatus,
    AdvanceRecovery,
    RecoveryStatus,
    FinancialTransactionType,
    TransactionDirection
)
from app.api.deps import get_current_user, get_current_tenant_id
from app.schemas.financial import (
    FinancialTransactionResponse,
    FinancialDashboardSummaryResponse
)
from app.services.financial_transaction_service import FinancialTransactionService

router = APIRouter(prefix="/financial", tags=["Phase 8: Financial Ledger & Reports"])


@router.get("/transactions", response_model=List[FinancialTransactionResponse])
async def get_financial_transactions(
    transaction_type: Optional[FinancialTransactionType] = None,
    direction: Optional[TransactionDirection] = None,
    search: Optional[str] = None,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp_res = await db.execute(select(Employee).where(Employee.user_id == current_user.id))
    emp = emp_res.scalar_one_or_none()
    emp_id = emp.id if (emp and current_user.role not in ["COMPANY_ADMIN", "HR_ADMIN", "FINANCE_ADMIN"]) else None

    return await FinancialTransactionService.get_transactions(
        db=db,
        tenant_id=tenant_id,
        employee_id=emp_id,
        transaction_type=transaction_type,
        direction=direction,
        search=search
    )


@router.get("/dashboard", response_model=FinancialDashboardSummaryResponse)
async def get_financial_dashboard_summary(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Total claims count
    claim_cnt_res = await db.execute(
        select(func.count(ExpenseClaim.id)).where(ExpenseClaim.tenant_id == tenant_id)
    )
    total_claims = claim_cnt_res.scalar() or 0

    # Pending claims total
    pending_amt_res = await db.execute(
        select(func.coalesce(func.sum(ExpenseClaim.total_amount), Decimal("0.00")))
        .where(and_(ExpenseClaim.tenant_id == tenant_id, ExpenseClaim.status == ExpenseClaimStatus.SUBMITTED))
    )
    pending_claims_amt = Decimal(str(pending_amt_res.scalar_one()))

    # Approved reimbursements total
    approved_reimb_res = await db.execute(
        select(func.coalesce(func.sum(Reimbursement.amount), Decimal("0.00")))
        .where(and_(Reimbursement.tenant_id == tenant_id, Reimbursement.status == ReimbursementStatus.PENDING))
    )
    approved_reimb_amt = Decimal(str(approved_reimb_res.scalar_one()))

    # Active loans count & outstanding principal
    active_loans_res = await db.execute(
        select(func.count(EmployeeLoan.id)).where(
            and_(EmployeeLoan.tenant_id == tenant_id, EmployeeLoan.status == LoanStatus.ACTIVE)
        )
    )
    active_loans_cnt = active_loans_res.scalar() or 0

    outstanding_loans_res = await db.execute(
        select(func.coalesce(func.sum(LoanInstallment.remaining_amount), Decimal("0.00")))
        .where(and_(LoanInstallment.tenant_id == tenant_id, LoanInstallment.status == InstallmentStatus.PENDING))
    )
    outstanding_loans_amt = Decimal(str(outstanding_loans_res.scalar_one()))

    monthly_emi_res = await db.execute(
        select(func.coalesce(func.sum(EmployeeLoan.monthly_installment), Decimal("0.00")))
        .where(and_(EmployeeLoan.tenant_id == tenant_id, EmployeeLoan.status == LoanStatus.ACTIVE))
    )
    monthly_emi_amt = Decimal(str(monthly_emi_res.scalar_one()))

    # Active advances count & outstanding amount
    active_adv_res = await db.execute(
        select(func.count(SalaryAdvance.id)).where(
            and_(SalaryAdvance.tenant_id == tenant_id, SalaryAdvance.status == SalaryAdvanceStatus.DISBURSED)
        )
    )
    active_adv_cnt = active_adv_res.scalar() or 0

    outstanding_adv_res = await db.execute(
        select(func.coalesce(func.sum(AdvanceRecovery.amount - AdvanceRecovery.recovered_amount), Decimal("0.00")))
        .where(and_(AdvanceRecovery.tenant_id == tenant_id, AdvanceRecovery.status == RecoveryStatus.PENDING))
    )
    outstanding_adv_amt = Decimal(str(outstanding_adv_res.scalar_one()))

    return FinancialDashboardSummaryResponse(
        total_claims_count=total_claims,
        pending_claims_amount=pending_claims_amt,
        approved_reimbursements_amount=approved_reimb_amt,
        total_active_loans_count=active_loans_cnt,
        outstanding_loans_principal=outstanding_loans_amt,
        monthly_loan_recovery_expected=monthly_emi_amt,
        total_active_advances_count=active_adv_cnt,
        outstanding_advances_amount=outstanding_adv_amt
    )


@router.get("/reconciliation/{period_id}")
async def get_payroll_reconciliation(
    period_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await FinancialTransactionService.reconcile_payroll_period(db, tenant_id, period_id)
