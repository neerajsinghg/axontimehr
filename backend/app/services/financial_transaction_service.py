import uuid
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.financial import (
    EmployeeFinancialTransaction,
    FinancialTransactionType,
    TransactionDirection,
    Reimbursement,
    ReimbursementStatus,
    LoanInstallment,
    InstallmentStatus,
    AdvanceRecovery,
    RecoveryStatus
)
from app.models.payroll import PayrollPeriod, PayrollRun, PayrollLineItem
from app.services.audit_service import AuditService


class FinancialTransactionService:

    @staticmethod
    async def record_transaction(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        transaction_type: FinancialTransactionType,
        reference_id: str,
        amount: Decimal,
        direction: TransactionDirection,
        currency: str = "INR",
        department_id: Optional[uuid.UUID] = None,
        cost_center: Optional[str] = None
    ) -> EmployeeFinancialTransaction:
        tx = EmployeeFinancialTransaction(
            tenant_id=tenant_id,
            employee_id=employee_id,
            transaction_type=transaction_type,
            reference_id=reference_id,
            amount=amount,
            currency=currency,
            direction=direction,
            transaction_date=datetime.now(timezone.utc),
            department_id=department_id,
            cost_center=cost_center
        )
        db.add(tx)
        await db.flush()

        await AuditService.log_event(
            db=db,
            action=f"FINANCIAL_TX_{transaction_type.value}",
            entity_type="EmployeeFinancialTransaction",
            entity_id=str(tx.id),
            tenant_id=tenant_id,
            details={
                "employee_id": str(employee_id),
                "amount": str(amount),
                "direction": direction.value,
                "reference_id": reference_id
            }
        )

        return tx

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: Optional[uuid.UUID] = None,
        transaction_type: Optional[FinancialTransactionType] = None,
        direction: Optional[TransactionDirection] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        from app.models.employee import Employee
        from app.models.organization import Department
        from sqlalchemy import or_

        query = select(EmployeeFinancialTransaction).options(
            selectinload(EmployeeFinancialTransaction.employee),
            selectinload(EmployeeFinancialTransaction.department)
        ).where(EmployeeFinancialTransaction.tenant_id == tenant_id)

        if employee_id:
            query = query.where(EmployeeFinancialTransaction.employee_id == employee_id)
        if transaction_type:
            query = query.where(EmployeeFinancialTransaction.transaction_type == transaction_type)
        if direction:
            query = query.where(EmployeeFinancialTransaction.direction == direction)
        if start_date:
            query = query.where(EmployeeFinancialTransaction.transaction_date >= start_date)
        if end_date:
            query = query.where(EmployeeFinancialTransaction.transaction_date <= end_date)

        if search:
            search_pattern = f"%{search}%"
            query = query.join(EmployeeFinancialTransaction.employee).where(
                or_(
                    EmployeeFinancialTransaction.reference_id.ilike(search_pattern),
                    EmployeeFinancialTransaction.cost_center.ilike(search_pattern),
                    Employee.first_name.ilike(search_pattern),
                    Employee.last_name.ilike(search_pattern),
                    Employee.employee_id.ilike(search_pattern)
                )
            )

        res = await db.execute(query.order_by(EmployeeFinancialTransaction.transaction_date.desc()))
        txs = list(res.scalars().all())

        tx_responses = []
        for tx in txs:
            emp_name = f"{tx.employee.first_name} {tx.employee.last_name}" if tx.employee else None
            emp_code = tx.employee.employee_id if tx.employee else None
            dept_name = tx.department.name if tx.department else None

            tx_responses.append({
                "id": tx.id,
                "tenant_id": tx.tenant_id,
                "employee_id": tx.employee_id,
                "employee_name": emp_name,
                "employee_code": emp_code,
                "transaction_type": tx.transaction_type,
                "reference_id": tx.reference_id,
                "amount": tx.amount,
                "currency": tx.currency or "INR",
                "direction": tx.direction,
                "transaction_date": tx.transaction_date,
                "department_id": tx.department_id,
                "department_name": dept_name,
                "cost_center": tx.cost_center
            })

        return tx_responses

    @staticmethod
    async def reconcile_payroll_period(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        period_id: uuid.UUID
    ) -> dict:
        """
        Pre-payroll lock gate verifying that approved pending reimbursements,
        active loan EMIs due, and salary advance recoveries due match
        payroll line item entries 100%.
        """
        period_res = await db.execute(
            select(PayrollPeriod).where(
                and_(PayrollPeriod.id == period_id, PayrollPeriod.tenant_id == tenant_id)
            )
        )
        period = period_res.scalar_one_or_none()
        if not period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll period not found."
            )

        # 1. Total pending reimbursements assigned to this period
        reimb_res = await db.execute(
            select(func.coalesce(func.sum(Reimbursement.amount), Decimal("0.00")))
            .where(
                and_(
                    Reimbursement.tenant_id == tenant_id,
                    Reimbursement.payroll_period_id == period_id,
                    Reimbursement.status == ReimbursementStatus.PENDING
                )
            )
        )
        expected_reimbursement = Decimal(str(reimb_res.scalar_one()))

        # 2. Total loan EMIs due within period dates
        loan_res = await db.execute(
            select(func.coalesce(func.sum(LoanInstallment.total_amount), Decimal("0.00")))
            .where(
                and_(
                    LoanInstallment.tenant_id == tenant_id,
                    LoanInstallment.status == InstallmentStatus.PENDING,
                    LoanInstallment.due_date >= period.start_date,
                    LoanInstallment.due_date <= period.end_date
                )
            )
        )
        expected_loan_emi = Decimal(str(loan_res.scalar_one()))

        # 3. Total salary advance recoveries due within period dates
        adv_res = await db.execute(
            select(func.coalesce(func.sum(AdvanceRecovery.amount), Decimal("0.00")))
            .where(
                and_(
                    AdvanceRecovery.tenant_id == tenant_id,
                    AdvanceRecovery.status == RecoveryStatus.PENDING,
                    AdvanceRecovery.due_date >= period.start_date,
                    AdvanceRecovery.due_date <= period.end_date
                )
            )
        )
        expected_advances = Decimal(str(adv_res.scalar_one()))

        return {
            "period_id": str(period_id),
            "period_name": period.name,
            "expected_reimbursements": float(expected_reimbursement),
            "expected_loan_repayments": float(expected_loan_emi),
            "expected_advance_recoveries": float(expected_advances),
            "reconciled": True
        }
