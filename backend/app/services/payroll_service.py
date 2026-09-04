from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payroll import (
    PayrollPeriod,
    PayrollRun,
    PayrollEmployee,
    PayrollPeriodStatus,
    PayrollRunStatus,
    PayrollAdjustment,
    AdjustmentStatus,
)
from app.models.employee import Employee
from app.schemas.payroll import PayrollPeriodCreate, PayrollRunCreate, PayrollAdjustmentCreate
from app.services.payroll_calculation_service import PayrollCalculationService
from app.services.payslip_service import PayslipService
from app.services.workflow_service import WorkflowService


class PayrollService:
    """
    Main payroll orchestration and lifecycle management service.
    Integrates with Phase 6 Workflow Engine and maintains immutable snapshots.
    """

    @staticmethod
    async def create_period(db: AsyncSession, tenant_id: UUID, data: PayrollPeriodCreate) -> PayrollPeriod:
        period = PayrollPeriod(
            tenant_id=tenant_id,
            name=data.name,
            year=data.year,
            month=data.month,
            start_date=data.start_date,
            end_date=data.end_date,
            pay_date=data.pay_date,
            status=PayrollPeriodStatus.OPEN
        )
        db.add(period)
        await db.commit()
        await db.refresh(period)
        return period

    @staticmethod
    async def get_periods(db: AsyncSession, tenant_id: UUID) -> List[PayrollPeriod]:
        res = await db.execute(
            select(PayrollPeriod)
            .where(PayrollPeriod.tenant_id == tenant_id)
            .order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def create_payroll_run(db: AsyncSession, tenant_id: UUID, data: PayrollRunCreate) -> PayrollRun:
        res = await db.execute(
            select(PayrollPeriod).where(
                PayrollPeriod.id == data.period_id,
                PayrollPeriod.tenant_id == tenant_id
            )
        )
        period = res.scalar_one_or_none()

        if not period:
            raise ValueError("Payroll period not found")

        payroll_run = PayrollRun(
            tenant_id=tenant_id,
            period_id=data.period_id,
            organization_id=data.organization_id,
            branch_id=data.branch_id,
            status=PayrollRunStatus.PROCESSING
        )
        db.add(payroll_run)
        await db.commit()
        
        res_created = await db.execute(
            select(PayrollRun)
            .options(
                selectinload(PayrollRun.period),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.employee),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.line_items)
            )
            .where(PayrollRun.id == payroll_run.id)
        )
        return res_created.scalar_one()

    @staticmethod
    async def calculate_payroll_run(db: AsyncSession, tenant_id: UUID, payroll_run_id: UUID) -> PayrollRun:
        res = await db.execute(
            select(PayrollRun)
            .options(selectinload(PayrollRun.period), selectinload(PayrollRun.payroll_employees))
            .where(
                PayrollRun.id == payroll_run_id,
                PayrollRun.tenant_id == tenant_id
            )
        )
        payroll_run = res.scalar_one_or_none()

        if not payroll_run:
            raise ValueError("Payroll run not found")

        if payroll_run.status in (PayrollRunStatus.LOCKED, PayrollRunStatus.PAID):
            raise ValueError("Cannot recalculate locked or paid payroll run")

        period_res = await db.execute(select(PayrollPeriod).where(PayrollPeriod.id == payroll_run.period_id))
        period = period_res.scalar_one_or_none()

        # Query active employees in tenant
        emp_res = await db.execute(
            select(Employee).where(
                Employee.organization_id == tenant_id,
                Employee.status == "ACTIVE"
            )
        )
        employees = list(emp_res.scalars().all())

        # Clear existing calculations for this run
        await db.execute(delete(PayrollEmployee).where(PayrollEmployee.payroll_run_id == payroll_run_id))
        await db.flush()

        total_gross = Decimal("0.00")
        total_deductions = Decimal("0.00")
        total_net = Decimal("0.00")
        processed_count = 0

        for emp in employees:
            pe = await PayrollCalculationService.calculate_employee_payroll(
                db=db,
                tenant_id=tenant_id,
                payroll_run_id=payroll_run_id,
                period=period,
                employee=emp
            )
            total_gross += pe.gross_salary
            total_deductions += pe.total_deductions
            total_net += pe.net_salary
            processed_count += 1

        payroll_run.total_employees = processed_count
        payroll_run.total_gross = total_gross
        payroll_run.total_deductions = total_deductions
        payroll_run.total_net = total_net
        payroll_run.status = PayrollRunStatus.PROCESSED

        await db.commit()
        
        # Re-fetch populated payroll run
        res_updated = await db.execute(
            select(PayrollRun)
            .options(
                selectinload(PayrollRun.period),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.employee),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.line_items)
            )
            .where(PayrollRun.id == payroll_run_id)
        )
        return res_updated.scalar_one()

    @staticmethod
    async def submit_for_approval(db: AsyncSession, tenant_id: UUID, payroll_run_id: UUID, requester_id: UUID) -> PayrollRun:
        res = await db.execute(
            select(PayrollRun).where(
                PayrollRun.id == payroll_run_id,
                PayrollRun.tenant_id == tenant_id
            )
        )
        payroll_run = res.scalar_one_or_none()

        if not payroll_run:
            raise ValueError("Payroll run not found")

        # Integration with WorkflowService
        instance = await WorkflowService.start_approval_instance(
            db=db,
            tenant_id=tenant_id,
            entity_type="PAYROLL_RUN",
            entity_id=payroll_run.id,
            requester_id=requester_id
        )

        payroll_run.approval_instance_id = instance.id
        payroll_run.status = PayrollRunStatus.PENDING_APPROVAL
        await db.commit()
        
        res_submitted = await db.execute(
            select(PayrollRun)
            .options(
                selectinload(PayrollRun.period),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.employee),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.line_items)
            )
            .where(PayrollRun.id == payroll_run_id)
        )
        return res_submitted.scalar_one()

    @staticmethod
    async def lock_payroll_run(db: AsyncSession, tenant_id: UUID, payroll_run_id: UUID) -> PayrollRun:
        res = await db.execute(
            select(PayrollRun)
            .options(
                selectinload(PayrollRun.period),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.employee),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.line_items)
            )
            .where(
                PayrollRun.id == payroll_run_id,
                PayrollRun.tenant_id == tenant_id
            )
        )
        payroll_run = res.scalar_one_or_none()

        if not payroll_run:
            raise ValueError("Payroll run not found")

        payroll_run.status = PayrollRunStatus.LOCKED
        payroll_run.locked_at = datetime.now(timezone.utc)

        p_res = await db.execute(select(PayrollPeriod).where(PayrollPeriod.id == payroll_run.period_id))
        period = p_res.scalar_one_or_none()
        if period:
            period.status = PayrollPeriodStatus.LOCKED

        for pe in payroll_run.payroll_employees:
            await PayslipService.generate_payslip_record(
                db=db,
                tenant_id=tenant_id,
                payroll_employee_id=pe.id,
                employee_id=pe.employee_id,
                period_id=payroll_run.period_id
            )

        await db.commit()
        await db.refresh(payroll_run)
        return payroll_run

    @staticmethod
    async def mark_payroll_paid(db: AsyncSession, tenant_id: UUID, payroll_run_id: UUID) -> PayrollRun:
        res = await db.execute(
            select(PayrollRun)
            .options(
                selectinload(PayrollRun.period),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.employee),
                selectinload(PayrollRun.payroll_employees).selectinload(PayrollEmployee.line_items)
            )
            .where(
                PayrollRun.id == payroll_run_id,
                PayrollRun.tenant_id == tenant_id
            )
        )
        payroll_run = res.scalar_one_or_none()

        if not payroll_run:
            raise ValueError("Payroll run not found")

        payroll_run.status = PayrollRunStatus.PAID
        payroll_run.paid_at = datetime.now(timezone.utc)

        p_res = await db.execute(select(PayrollPeriod).where(PayrollPeriod.id == payroll_run.period_id))
        period = p_res.scalar_one_or_none()
        if period:
            period.status = PayrollPeriodStatus.PAID

        await db.commit()
        await db.refresh(payroll_run)
        return payroll_run

    @staticmethod
    async def create_adjustment(db: AsyncSession, tenant_id: UUID, user_id: UUID, data: PayrollAdjustmentCreate) -> PayrollAdjustment:
        adjustment = PayrollAdjustment(
            tenant_id=tenant_id,
            employee_id=data.employee_id,
            adjustment_type=data.adjustment_type,
            amount=Decimal(str(data.amount)),
            reason=data.reason,
            payroll_period_id=data.payroll_period_id,
            status=AdjustmentStatus.APPROVED,
            created_by=user_id
        )
        db.add(adjustment)
        await db.commit()
        await db.refresh(adjustment)
        return adjustment

    @staticmethod
    async def get_adjustments(db: AsyncSession, tenant_id: UUID) -> List[PayrollAdjustment]:
        res = await db.execute(
            select(PayrollAdjustment)
            .options(selectinload(PayrollAdjustment.employee))
            .where(PayrollAdjustment.tenant_id == tenant_id)
            .order_by(PayrollAdjustment.created_at.desc())
        )
        return list(res.scalars().all())
