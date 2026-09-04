import uuid
from typing import List, Optional
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.financial import (
    SalaryAdvance,
    AdvanceRecovery,
    SalaryAdvanceStatus,
    RecoveryStatus,
    FinancialTransactionType,
    TransactionDirection
)
from app.schemas.financial import SalaryAdvanceCreate
from app.services.workflow_service import WorkflowService
from app.services.financial_transaction_service import FinancialTransactionService
from app.services.audit_service import AuditService


class AdvanceService:

    @staticmethod
    async def request_advance(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        data: SalaryAdvanceCreate
    ) -> SalaryAdvance:
        if data.amount <= Decimal("0.00"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Advance amount must be positive.")

        adv_num = f"ADV-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
        monthly_recovery = (data.amount / Decimal(data.recovery_months)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        adv = SalaryAdvance(
            tenant_id=tenant_id,
            advance_number=adv_num,
            employee_id=employee_id,
            amount=data.amount,
            approved_amount=data.amount,
            recovery_months=data.recovery_months,
            monthly_recovery_amount=monthly_recovery,
            status=SalaryAdvanceStatus.PENDING
        )
        db.add(adv)
        await db.flush()

        # Build recovery schedule
        start_date = date.today()
        rem_amount = data.amount
        for i in range(1, data.recovery_months + 1):
            rec_amt = monthly_recovery if i < data.recovery_months else rem_amount
            due_date = start_date + timedelta(days=30 * i)
            rem_amount -= rec_amt

            rec = AdvanceRecovery(
                tenant_id=tenant_id,
                advance_id=adv.id,
                installment_number=i,
                due_date=due_date,
                amount=rec_amt,
                recovered_amount=Decimal("0.00"),
                status=RecoveryStatus.PENDING
            )
            db.add(rec)

        instance = await WorkflowService.start_approval_instance(
            db, tenant_id, "SALARY_ADVANCE", adv.id, employee_id
        )
        adv.approval_instance_id = instance.id

        await db.commit()
        
        res_full = await db.execute(
            select(SalaryAdvance)
            .options(selectinload(SalaryAdvance.recoveries))
            .where(SalaryAdvance.id == adv.id)
        )
        return res_full.scalar_one()

    @staticmethod
    async def approve_advance(db: AsyncSession, tenant_id: uuid.UUID, advance_id: uuid.UUID) -> SalaryAdvance:
        res = await db.execute(
            select(SalaryAdvance).where(
                and_(SalaryAdvance.id == advance_id, SalaryAdvance.tenant_id == tenant_id)
            )
        )
        adv = res.scalar_one_or_none()
        if not adv or adv.status != SalaryAdvanceStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Salary advance not found or not pending.")

        adv.status = SalaryAdvanceStatus.APPROVED
        await db.commit()
        
        res_full = await db.execute(
            select(SalaryAdvance)
            .options(selectinload(SalaryAdvance.recoveries))
            .where(SalaryAdvance.id == adv.id)
        )
        return res_full.scalar_one()

    @staticmethod
    async def disburse_advance(db: AsyncSession, tenant_id: uuid.UUID, advance_id: uuid.UUID) -> SalaryAdvance:
        res = await db.execute(
            select(SalaryAdvance).where(
                and_(SalaryAdvance.id == advance_id, SalaryAdvance.tenant_id == tenant_id)
            )
        )
        adv = res.scalar_one_or_none()
        if not adv or adv.status != SalaryAdvanceStatus.APPROVED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Salary advance not approved or already disbursed.")

        adv.status = SalaryAdvanceStatus.DISBURSED
        adv.disbursed_at = datetime.now(timezone.utc)

        await FinancialTransactionService.record_transaction(
            db=db,
            tenant_id=tenant_id,
            employee_id=adv.employee_id,
            transaction_type=FinancialTransactionType.SALARY_ADVANCE,
            reference_id=str(adv.id),
            amount=adv.approved_amount,
            direction=TransactionDirection.CREDIT
        )

        await db.commit()
        
        res_full = await db.execute(
            select(SalaryAdvance)
            .options(selectinload(SalaryAdvance.recoveries))
            .where(SalaryAdvance.id == adv.id)
        )
        return res_full.scalar_one()
