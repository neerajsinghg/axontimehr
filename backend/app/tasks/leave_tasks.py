import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leave import LeavePolicy, LeaveBalance, LeaveLedger, LedgerTransactionType
from app.models.employee import Employee, EmployeeStatus

logger = logging.getLogger("axontime.leave_tasks")


async def process_monthly_accruals(db: AsyncSession, tenant_id: uuid.UUID, year: int, month: int) -> dict:
    """Idempotent monthly leave accrual background task."""
    logger.info(f"Processing monthly accruals for tenant {tenant_id}, year={year}, month={month}")

    # Fetch active policies
    policies_res = await db.execute(
        select(LeavePolicy).where(LeavePolicy.tenant_id == tenant_id)
    )
    policies = policies_res.scalars().all()

    # Fetch active employees
    emp_res = await db.execute(
        select(Employee).where(
            and_(
                Employee.tenant_id == tenant_id,
                Employee.status == EmployeeStatus.ACTIVE
            )
        )
    )
    employees = emp_res.scalars().all()

    accrued_count = 0
    ref_id = f"ACCRUAL_{year}_{month:02d}"

    for emp in employees:
        for pol in policies:
            # Check idempotency (skip if ledger transaction for this ref_id already exists)
            existing = await db.execute(
                select(LeaveLedger).where(
                    and_(
                        LeaveLedger.tenant_id == tenant_id,
                        LeaveLedger.employee_id == emp.id,
                        LeaveLedger.leave_type_id == pol.leave_type_id,
                        LeaveLedger.reference_id == ref_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Fetch balance
            bal_res = await db.execute(
                select(LeaveBalance).where(
                    and_(
                        LeaveBalance.tenant_id == tenant_id,
                        LeaveBalance.employee_id == emp.id,
                        LeaveBalance.leave_type_id == pol.leave_type_id,
                        LeaveBalance.year == year
                    )
                )
            )
            bal = bal_res.scalar_one_or_none()
            if not bal:
                bal = LeaveBalance(
                    tenant_id=tenant_id,
                    employee_id=emp.id,
                    leave_type_id=pol.leave_type_id,
                    year=year,
                    allocated=pol.annual_entitlement,
                    accrued=0.0,
                    available=0.0
                )
                db.add(bal)
                await db.flush()

            accrual_amount = pol.accrual_amount
            bal.accrued += accrual_amount
            bal.available += accrual_amount

            ledger = LeaveLedger(
                tenant_id=tenant_id,
                employee_id=emp.id,
                leave_type_id=pol.leave_type_id,
                transaction_type=LedgerTransactionType.ACCRUAL,
                amount=accrual_amount,
                balance_after=bal.available,
                reference_id=ref_id,
                remarks=f"Monthly leave accrual for {year}-{month:02d}"
            )
            db.add(ledger)
            accrued_count += 1

    await db.commit()
    logger.info(f"Accrual processing completed. Granted {accrued_count} ledger accruals.")
    return {"status": "SUCCESS", "accrued_records": accrued_count}
