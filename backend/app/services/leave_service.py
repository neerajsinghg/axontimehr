import uuid
from typing import List, Optional, Tuple, Set, Dict, Any
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.leave import (
    LeaveType,
    LeavePolicy,
    LeavePolicyAssignment,
    LeaveBalance,
    LeaveLedger,
    LeaveRequest,
    LeaveTypeStatus,
    AccrualFrequency,
    LedgerTransactionType,
    LeaveDurationType,
    HalfDayPosition,
    LeaveRequestStatus
)
from app.models.employee import Employee
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.leave import (
    LeaveTypeCreate,
    LeaveTypeUpdate,
    LeavePolicyCreate,
    LeaveRequestCreate
)
from app.services.holiday_service import HolidayService
from app.services.workflow_service import WorkflowService


class LeaveService:

    @staticmethod
    async def create_leave_type(db: AsyncSession, tenant_id: uuid.UUID, data: LeaveTypeCreate) -> LeaveType:
        existing = await db.execute(
            select(LeaveType).where(
                and_(
                    LeaveType.tenant_id == tenant_id,
                    LeaveType.code == data.code
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Leave type with code '{data.code}' already exists."
            )

        lt = LeaveType(
            tenant_id=tenant_id,
            code=data.code,
            name=data.name,
            description=data.description,
            color_code=data.color_code,
            paid=data.paid,
            requires_document=data.requires_document,
            allow_half_day=data.allow_half_day,
            allow_partial_day=data.allow_partial_day,
            allow_backdated=data.allow_backdated,
            allow_future=data.allow_future,
            minimum_notice_days=data.minimum_notice_days,
            maximum_consecutive_days=data.maximum_consecutive_days,
            status=data.status
        )
        db.add(lt)
        await db.commit()
        await db.refresh(lt)
        return lt

    @staticmethod
    async def get_leave_types(db: AsyncSession, tenant_id: uuid.UUID) -> List[LeaveType]:
        res = await db.execute(
            select(LeaveType)
            .where(LeaveType.tenant_id == tenant_id)
            .order_by(LeaveType.name)
        )
        return list(res.scalars().all())

    @staticmethod
    async def create_leave_policy(db: AsyncSession, tenant_id: uuid.UUID, data: LeavePolicyCreate) -> LeavePolicy:
        policy = LeavePolicy(
            tenant_id=tenant_id,
            leave_type_id=data.leave_type_id,
            name=data.name,
            annual_entitlement=data.annual_entitlement,
            accrual_frequency=data.accrual_frequency,
            accrual_amount=data.accrual_amount,
            carry_forward_allowed=data.carry_forward_allowed,
            carry_forward_limit=data.carry_forward_limit,
            encashment_allowed=data.encashment_allowed,
            maximum_balance=data.maximum_balance,
            negative_balance_allowed=data.negative_balance_allowed,
            max_negative_balance=data.max_negative_balance,
            probation_allowed=data.probation_allowed,
            notice_period_days=data.notice_period_days
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy

    @staticmethod
    async def get_or_create_employee_balance(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        leave_type_id: uuid.UUID,
        year: int
    ) -> LeaveBalance:
        res = await db.execute(
            select(LeaveBalance).where(
                and_(
                    LeaveBalance.tenant_id == tenant_id,
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.leave_type_id == leave_type_id,
                    LeaveBalance.year == year
                )
            )
        )
        bal = res.scalar_one_or_none()
        if not bal:
            # Resolve policy entitlement if exists
            policy_res = await db.execute(
                select(LeavePolicy).where(
                    and_(
                        LeavePolicy.tenant_id == tenant_id,
                        LeavePolicy.leave_type_id == leave_type_id
                    )
                )
            )
            policy = policy_res.scalars().first()
            allocated = policy.annual_entitlement if policy else 12.0

            bal = LeaveBalance(
                tenant_id=tenant_id,
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                year=year,
                allocated=allocated,
                accrued=allocated,
                used=0.0,
                pending=0.0,
                available=allocated
            )
            db.add(bal)
            await db.flush()

            # Record initial ledger entry
            ledger = LeaveLedger(
                tenant_id=tenant_id,
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                transaction_type=LedgerTransactionType.OPENING_BALANCE,
                amount=allocated,
                balance_after=allocated,
                remarks="Initial opening leave balance allocation"
            )
            db.add(ledger)
            await db.commit()
            await db.refresh(bal)

        return bal

    @staticmethod
    async def get_employee_balances(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        year: Optional[int] = None
    ) -> List[dict]:
        target_year = year or datetime.now().year
        l_types = await LeaveService.get_leave_types(db, tenant_id)

        result = []
        for lt in l_types:
            bal = await LeaveService.get_or_create_employee_balance(db, tenant_id, employee_id, lt.id, target_year)
            result.append({
                "id": bal.id,
                "tenant_id": bal.tenant_id,
                "employee_id": bal.employee_id,
                "leave_type_id": lt.id,
                "leave_type_code": lt.code,
                "leave_type_name": lt.name,
                "color_code": lt.color_code,
                "year": bal.year,
                "allocated": bal.allocated,
                "accrued": bal.accrued,
                "adjusted": bal.adjusted,
                "used": bal.used,
                "pending": bal.pending,
                "expired": bal.expired,
                "carried_forward": bal.carried_forward,
                "available": bal.available,
                "updated_at": bal.updated_at
            })
        return result

    @staticmethod
    async def calculate_working_days(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        start_date: date,
        end_date: date,
        duration_type: LeaveDurationType,
        branch_id: Optional[uuid.UUID] = None
    ) -> Tuple[float, float, float, float]:
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after end date."
            )

        holiday_dates = await HolidayService.get_holiday_dates_set(db, tenant_id, start_date, end_date, branch_id)

        cur_date = start_date
        total_days = 0
        working_days = 0
        holiday_days = 0
        weekly_off_days = 0

        while cur_date <= end_date:
            total_days += 1
            # Check Sunday (6)
            if cur_date.weekday() == 6:
                weekly_off_days += 1
            elif cur_date in holiday_dates:
                holiday_days += 1
            else:
                working_days += 1

            cur_date += timedelta(days=1)

        if duration_type == LeaveDurationType.HALF_DAY:
            working_days_count = 0.5
            total_req_days = 0.5
        else:
            working_days_count = float(working_days)
            total_req_days = float(total_days)

        return total_req_days, working_days_count, float(holiday_days), float(weekly_off_days)

    @staticmethod
    async def create_leave_request(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        data: LeaveRequestCreate
    ) -> LeaveRequest:
        # Check leave type exists
        lt_res = await db.execute(
            select(LeaveType).where(
                and_(
                    LeaveType.id == data.leave_type_id,
                    LeaveType.tenant_id == tenant_id
                )
            )
        )
        lt = lt_res.scalar_one_or_none()
        if not lt or lt.status != LeaveTypeStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive leave type."
            )

        # Overlap check
        overlap_res = await db.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.tenant_id == tenant_id,
                    LeaveRequest.employee_id == employee_id,
                    LeaveRequest.status.in_([LeaveRequestStatus.PENDING, LeaveRequestStatus.APPROVED]),
                    or_(
                        and_(LeaveRequest.start_date <= data.start_date, LeaveRequest.end_date >= data.start_date),
                        and_(LeaveRequest.start_date <= data.end_date, LeaveRequest.end_date >= data.end_date),
                        and_(LeaveRequest.start_date >= data.start_date, LeaveRequest.end_date <= data.end_date)
                    )
                )
            )
        )
        if overlap_res.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request overlaps with an existing pending or approved leave."
            )

        # Calculate working days
        emp_res = await db.execute(select(Employee).where(Employee.id == employee_id))
        emp = emp_res.scalar_one_or_none()
        branch_id = emp.branch_id if emp else None

        total_req_days, working_days, holiday_days, weekly_off_days = await LeaveService.calculate_working_days(
            db, tenant_id, data.start_date, data.end_date, data.duration_type, branch_id
        )

        # Balance check
        year = data.start_date.year
        bal = await LeaveService.get_or_create_employee_balance(db, tenant_id, employee_id, data.leave_type_id, year)
        if bal.available < working_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient leave balance. Available: {bal.available} days, Requested: {working_days} days."
            )

        # Create leave request
        req = LeaveRequest(
            tenant_id=tenant_id,
            employee_id=employee_id,
            leave_type_id=data.leave_type_id,
            start_date=data.start_date,
            end_date=data.end_date,
            duration_type=data.duration_type,
            half_day_position=data.half_day_position,
            total_requested_days=total_req_days,
            working_days_count=working_days,
            holiday_days_count=holiday_days,
            weekly_off_days_count=weekly_off_days,
            reason=data.reason,
            document_url=data.document_url,
            status=LeaveRequestStatus.PENDING
        )
        db.add(req)
        await db.flush()

        # Update pending balance
        bal.pending += working_days
        bal.available -= working_days

        # Start workflow instance
        instance = await WorkflowService.start_approval_instance(
            db, tenant_id, "LEAVE_REQUEST", req.id, employee_id
        )
        req.approval_instance_id = instance.id

        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def approve_leave_request(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        request_id: uuid.UUID
    ) -> LeaveRequest:
        req_res = await db.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.id == request_id,
                    LeaveRequest.tenant_id == tenant_id
                )
            )
        )
        req = req_res.scalar_one_or_none()
        if not req or req.status != LeaveRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request not found or not in pending status."
            )

        req.status = LeaveRequestStatus.APPROVED
        year = req.start_date.year

        # Update balance
        bal = await LeaveService.get_or_create_employee_balance(db, tenant_id, req.employee_id, req.leave_type_id, year)
        bal.pending = max(0.0, bal.pending - req.working_days_count)
        bal.used += req.working_days_count

        # Write ledger debit
        ledger = LeaveLedger(
            tenant_id=tenant_id,
            employee_id=req.employee_id,
            leave_type_id=req.leave_type_id,
            transaction_type=LedgerTransactionType.LEAVE_DEBIT,
            amount=-req.working_days_count,
            balance_after=bal.available,
            reference_id=str(req.id),
            remarks=f"Leave approved for period {req.start_date} to {req.end_date}"
        )
        db.add(ledger)

        # Update attendance records to ON_LEAVE
        cur_date = req.start_date
        while cur_date <= req.end_date:
            att_res = await db.execute(
                select(Attendance).where(
                    and_(
                        Attendance.tenant_id == tenant_id,
                        Attendance.employee_id == req.employee_id,
                        Attendance.attendance_date == cur_date
                    )
                )
            )
            att = att_res.scalar_one_or_none()
            if not att:
                att = Attendance(
                    tenant_id=tenant_id,
                    employee_id=req.employee_id,
                    attendance_date=cur_date,
                    status=AttendanceStatus.ON_LEAVE,
                    remarks=f"Approved Leave: {req.reason}"
                )
                db.add(att)
            else:
                att.status = AttendanceStatus.ON_LEAVE
                att.remarks = f"Approved Leave: {req.reason}"

            cur_date += timedelta(days=1)

        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def cancel_leave_request(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        request_id: uuid.UUID
    ) -> LeaveRequest:
        req_res = await db.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.id == request_id,
                    LeaveRequest.tenant_id == tenant_id
                )
            )
        )
        req = req_res.scalar_one_or_none()
        if not req or req.status not in (LeaveRequestStatus.PENDING, LeaveRequestStatus.APPROVED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending or approved leave requests can be cancelled."
            )

        old_status = req.status
        req.status = LeaveRequestStatus.CANCELLED
        year = req.start_date.year
        bal = await LeaveService.get_or_create_employee_balance(db, tenant_id, req.employee_id, req.leave_type_id, year)

        if old_status == LeaveRequestStatus.PENDING:
            bal.pending = max(0.0, bal.pending - req.working_days_count)
            bal.available += req.working_days_count
        elif old_status == LeaveRequestStatus.APPROVED:
            bal.used = max(0.0, bal.used - req.working_days_count)
            bal.available += req.working_days_count

            # Write ledger reversal
            ledger = LeaveLedger(
                tenant_id=tenant_id,
                employee_id=req.employee_id,
                leave_type_id=req.leave_type_id,
                transaction_type=LedgerTransactionType.LEAVE_REVERSAL,
                amount=req.working_days_count,
                balance_after=bal.available,
                reference_id=str(req.id),
                remarks=f"Reversal for cancelled leave {req.start_date} to {req.end_date}"
            )
            db.add(ledger)

        await db.commit()
        await db.refresh(req)
        return req
