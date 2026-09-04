import math
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import date, datetime, time, timedelta, timezone
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.employee import Employee
from app.models.attendance import (
    Attendance,
    AttendanceEvent,
    AttendanceRegularization,
    Shift,
    EmployeeShiftAssignment,
    Holiday,
    AttendanceStatus,
    AttendanceSource,
    AttendanceEventType,
    RegularizationStatus,
    ShiftStatus
)
from app.schemas.attendance import (
    PunchRequest,
    RegularizationCreate,
    DailyAttendanceStatusResponse,
    AttendanceDashboardResponse
)
from app.services.shift_service import ShiftService
from app.services.audit_service import AuditService
from app.schemas.location import AttendanceExceptionResponse


class AttendanceService:

    @staticmethod
    async def get_or_create_employee_for_user(db: AsyncSession, tenant_id: UUID, user_id: UUID) -> Employee:
        res = await db.execute(
            select(Employee).where(and_(Employee.organization_id == tenant_id, Employee.user_id == user_id))
        )
        emp = res.scalar_one_or_none()
        if not emp:
            from app.models.user import User
            user_res = await db.execute(select(User).where(User.id == user_id))
            user = user_res.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No user account found."
                )
            emp = Employee(
                organization_id=tenant_id,
                user_id=user.id,
                employee_id=f"EMP-{user.id.hex[:6].upper()}",
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                joining_date=datetime.now(timezone.utc).date()
            )
            db.add(emp)
            await db.commit()
            await db.refresh(emp)
        return emp

    @staticmethod
    def calculate_shift_date_and_times(now_dt: datetime, shift: Optional[Shift]) -> Tuple[date, Optional[datetime], Optional[datetime]]:
        """
        Determines the shift date and theoretical shift start/end datetimes in UTC.
        For overnight shifts (e.g. 22:00 -> 06:00), if check-in is early morning (e.g. 02:00 AM),
        the Shift Date is bound to the previous calendar day.
        """
        target_date = now_dt.date()
        if not shift:
            return target_date, None, None

        shift_start_dt = datetime.combine(target_date, shift.start_time).replace(tzinfo=timezone.utc)
        shift_end_dt = datetime.combine(target_date, shift.end_time).replace(tzinfo=timezone.utc)

        if shift.is_overnight or shift.end_time < shift.start_time:
            # Shift spans overnight
            if now_dt.time() < shift.end_time:
                # Early morning punch for overnight shift started yesterday
                target_date = target_date - timedelta(days=1)
                shift_start_dt = datetime.combine(target_date, shift.start_time).replace(tzinfo=timezone.utc)
                shift_end_dt = datetime.combine(target_date + timedelta(days=1), shift.end_time).replace(tzinfo=timezone.utc)
            else:
                shift_end_dt = datetime.combine(target_date + timedelta(days=1), shift.end_time).replace(tzinfo=timezone.utc)

        return target_date, shift_start_dt, shift_end_dt

    @staticmethod
    async def check_in(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID,
        data: PunchRequest
    ) -> Attendance:
        now_dt = datetime.now(timezone.utc)
        
        # 1. Resolve Active Shift Roster for Employee
        assignment = await ShiftService.get_active_shift_assignment(db, tenant_id, employee_id, now_dt.date())
        shift = assignment.shift if assignment else None
        
        # 2. Determine Shift Date (Handles overnight shifts)
        shift_date, shift_start_dt, shift_end_dt = AttendanceService.calculate_shift_date_and_times(now_dt, shift)

        # 3. Check for existing daily attendance record
        res = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.tenant_id == tenant_id,
                    Attendance.employee_id == employee_id,
                    Attendance.attendance_date == shift_date
                )
            )
        )
        att = res.scalar_one_or_none()

        # Idempotency / Duplicate Check-in Protection
        if att and att.first_check_in is not None and att.last_check_out is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "ALREADY_CHECKED_IN", "message": "Employee is already checked in."}
            )

        # --- Phase 5 Location & Verification Policy Evaluation ---
        from app.services.location_service import LocationService
        from app.services.verification_service import VerificationService

        loc_val = await LocationService.validate_location_punch(
            db, tenant_id, employee_id, data.latitude, data.longitude, data.accuracy, data.captured_at
        )
        if not loc_val.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": f"LOCATION_{loc_val.status_code}", "message": loc_val.message}
            )

        ver_val = await VerificationService.evaluate_verification_requirement(
            db, tenant_id, employee_id, data.verification_id
        )
        if not ver_val.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": f"VERIFICATION_{ver_val.status.value}", "message": ver_val.message}
            )

        has_exception = loc_val.has_exception or (ver_val.status.value not in ("NOT_REQUIRED", "VERIFIED"))

        # 4. Calculate Late Minutes & Initial Status
        late_minutes = 0
        initial_status = AttendanceStatus.PRESENT

        if shift and shift_start_dt:
            grace_cutoff = shift_start_dt + timedelta(minutes=shift.grace_period_minutes)
            if now_dt > grace_cutoff:
                late_delta = now_dt - shift_start_dt
                late_minutes = max(0, int(late_delta.total_seconds() // 60))
                initial_status = AttendanceStatus.LATE

        # Check Weekly Off / Holiday
        weekday_name = shift_date.strftime("%A").upper()
        if assignment and weekday_name in (assignment.weekly_offs or []):
            initial_status = AttendanceStatus.WEEK_OFF

        if not att:
            att = Attendance(
                tenant_id=tenant_id,
                employee_id=employee_id,
                attendance_date=shift_date,
                shift_id=shift.id if shift else None,
                first_check_in=now_dt,
                status=initial_status,
                late_minutes=late_minutes,
                location_status=loc_val.status_code,
                verification_status=ver_val.status.value,
                has_exception=has_exception,
                attendance_source=data.source,
                remarks=data.remarks
            )
            db.add(att)
            await db.flush()
        else:
            if att.first_check_in is None:
                att.first_check_in = now_dt
                att.late_minutes = late_minutes
                att.status = initial_status
            att.location_status = loc_val.status_code
            att.verification_status = ver_val.status.value
            att.has_exception = has_exception
            att.last_check_out = None # Re-open active session if re-checking in after break

        # 5. Create Raw Punch Event
        event = AttendanceEvent(
            tenant_id=tenant_id,
            employee_id=employee_id,
            attendance_id=att.id,
            event_type=AttendanceEventType.CHECK_IN,
            event_time=now_dt,
            source=data.source,
            latitude=data.latitude,
            longitude=data.longitude,
            accuracy=data.accuracy,
            distance_meters=loc_val.distance_meters,
            captured_at=data.captured_at or now_dt,
            geofence_status=loc_val.status_code,
            verification_status=ver_val.status.value,
            verification_id=data.verification_id,
            device_reference=data.device_reference or data.device_id,
            location_reference=data.location_reference or loc_val.location_name,
            verification_reference=data.verification_reference or ver_val.message,
            remarks=data.remarks
        )
        db.add(event)
        await db.commit()

        # Eagerly load relationships before returning
        res_loaded = await db.execute(
            select(Attendance)
            .options(selectinload(Attendance.shift), selectinload(Attendance.events))
            .where(Attendance.id == att.id)
        )
        att_loaded = res_loaded.scalar_one()

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="ATTENDANCE_CHECK_IN",
            entity_type="Attendance",
            entity_id=att_loaded.id,
            details={"employee_id": str(employee_id), "check_in_time": str(now_dt), "late_minutes": late_minutes, "location_status": loc_val.status_code}
        )
        return att_loaded

    @staticmethod
    async def check_out(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID,
        data: PunchRequest
    ) -> Attendance:
        now_dt = datetime.now(timezone.utc)
        
        # 1. Resolve Active Attendance Record
        # Search today or yesterday for overnight active check-ins
        res = await db.execute(
            select(Attendance)
            .options(selectinload(Attendance.shift))
            .where(
                and_(
                    Attendance.tenant_id == tenant_id,
                    Attendance.employee_id == employee_id,
                    Attendance.first_check_in.isnot(None),
                    Attendance.last_check_out.is_(None)
                )
            ).order_by(Attendance.first_check_in.desc())
        )
        att = res.scalar_one_or_none()

        if not att:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_ATTENDANCE_STATE", "message": "Employee cannot check out before checking in."}
            )

        # --- Phase 5 Location & Verification Policy Evaluation ---
        from app.services.location_service import LocationService
        from app.services.verification_service import VerificationService

        loc_val = await LocationService.validate_location_punch(
            db, tenant_id, employee_id, data.latitude, data.longitude, data.accuracy, data.captured_at
        )
        if not loc_val.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": f"LOCATION_{loc_val.status_code}", "message": loc_val.message}
            )

        ver_val = await VerificationService.evaluate_verification_requirement(
            db, tenant_id, employee_id, data.verification_id
        )
        if not ver_val.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": f"VERIFICATION_{ver_val.status.value}", "message": ver_val.message}
            )

        # Fetch Shift details
        shift = att.shift

        # 2. Update Check-out Time & Calculate Durations
        att.last_check_out = now_dt
        att.location_status = loc_val.status_code
        att.verification_status = ver_val.status.value
        if loc_val.status_code == 'OUTSIDE':
            att.has_exception = True
        gross_seconds = (now_dt - att.first_check_in).total_seconds()
        gross_minutes = max(0, int(gross_seconds // 60))
        
        break_mins = shift.break_duration_minutes if shift else 0
        att.total_break_minutes = break_mins
        att.worked_minutes = max(0, gross_minutes - break_mins)
        att.total_work_minutes = att.worked_minutes

        # 3. Calculate Early Exit & Overtime
        early_exit_mins = 0
        if shift:
            shift_start_dt = datetime.combine(att.attendance_date, shift.start_time).replace(tzinfo=timezone.utc)
            if shift.is_overnight or shift.end_time < shift.start_time:
                shift_end_dt = datetime.combine(att.attendance_date + timedelta(days=1), shift.end_time).replace(tzinfo=timezone.utc)
            else:
                shift_end_dt = datetime.combine(att.attendance_date, shift.end_time).replace(tzinfo=timezone.utc)

            early_cutoff = shift_end_dt - timedelta(minutes=shift.early_exit_threshold_minutes)
            if now_dt < early_cutoff:
                early_exit_delta = shift_end_dt - now_dt
                early_exit_mins = max(0, int(early_exit_delta.total_seconds() // 60))
                att.early_exit_minutes = early_exit_mins

            # Determine Final Daily Status
            if att.worked_minutes < (shift.minimum_work_minutes // 2):
                att.status = AttendanceStatus.ABSENT
            elif att.worked_minutes < shift.minimum_work_minutes:
                att.status = AttendanceStatus.HALF_DAY
            elif early_exit_mins > 0 and att.late_minutes > 0:
                att.status = AttendanceStatus.PARTIAL
            elif early_exit_mins > 0:
                att.status = AttendanceStatus.EARLY_EXIT
            elif att.late_minutes > 0:
                att.status = AttendanceStatus.LATE
            else:
                att.status = AttendanceStatus.PRESENT

        # 4. Create Raw Punch Event
        event = AttendanceEvent(
            tenant_id=tenant_id,
            employee_id=employee_id,
            attendance_id=att.id,
            event_type=AttendanceEventType.CHECK_OUT,
            event_time=now_dt,
            source=data.source,
            latitude=data.latitude,
            longitude=data.longitude,
            accuracy=data.accuracy,
            distance_meters=loc_val.distance_meters,
            captured_at=data.captured_at or now_dt,
            geofence_status=loc_val.status_code,
            verification_status=ver_val.status.value,
            verification_id=data.verification_id,
            device_reference=data.device_reference or data.device_id,
            location_reference=data.location_reference or loc_val.location_name,
            verification_reference=data.verification_reference or ver_val.message,
            remarks=data.remarks
        )
        db.add(event)
        await db.commit()

        # Eagerly load relationships before returning
        res_loaded = await db.execute(
            select(Attendance)
            .options(selectinload(Attendance.shift), selectinload(Attendance.events))
            .where(Attendance.id == att.id)
        )
        att_loaded = res_loaded.scalar_one()

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="ATTENDANCE_CHECK_OUT",
            entity_type="Attendance",
            entity_id=att_loaded.id,
            details={"employee_id": str(employee_id), "check_out_time": str(now_dt), "worked_minutes": att_loaded.worked_minutes}
        )
        return att_loaded

    @staticmethod
    async def get_today_status(db: AsyncSession, tenant_id: UUID, employee_id: UUID) -> DailyAttendanceStatusResponse:
        today_date = datetime.now(timezone.utc).date()
        assignment = await ShiftService.get_active_shift_assignment(db, tenant_id, employee_id, today_date)
        shift = assignment.shift if assignment else None

        res = await db.execute(
            select(Attendance)
            .options(selectinload(Attendance.shift), selectinload(Attendance.events))
            .where(
                and_(
                    Attendance.tenant_id == tenant_id,
                    Attendance.employee_id == employee_id,
                    Attendance.attendance_date == today_date
                )
            )
        )
        att = res.scalar_one_or_none()

        is_checked_in = att is not None and att.first_check_in is not None and att.last_check_out is None
        is_checked_out = att is not None and att.last_check_out is not None

        return DailyAttendanceStatusResponse(
            today_date=today_date,
            is_checked_in=is_checked_in,
            is_checked_out=is_checked_out,
            current_status=att.status if att else AttendanceStatus.PENDING,
            first_check_in=att.first_check_in if att else None,
            last_check_out=att.last_check_out if att else None,
            worked_minutes=att.worked_minutes if att else 0,
            shift=shift
        )

    @staticmethod
    async def get_my_attendance_history(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID,
        page: int = 1,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Tuple[List[Attendance], int]:
        query = select(Attendance).options(selectinload(Attendance.shift), selectinload(Attendance.events)).where(
            and_(Attendance.tenant_id == tenant_id, Attendance.employee_id == employee_id)
        )
        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)

        total_res = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_res.scalar_one()

        offset = (page - 1) * limit
        res = await db.execute(
            query.order_by(Attendance.attendance_date.desc()).offset(offset).limit(limit)
        )
        records = list(res.scalars().all())
        return records, total

    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession, tenant_id: UUID) -> AttendanceDashboardResponse:
        today_date = datetime.now(timezone.utc).date()

        # Count total employees
        tot_emp_res = await db.execute(
            select(func.count(Employee.id)).where(and_(Employee.organization_id == tenant_id, Employee.status == "ACTIVE"))
        )
        total_employees = tot_emp_res.scalar_one()

        # Count today's statuses using DB aggregation
        status_res = await db.execute(
            select(Attendance.status, func.count(Attendance.id))
            .where(and_(Attendance.tenant_id == tenant_id, Attendance.attendance_date == today_date))
            .group_by(Attendance.status)
        )
        status_counts = dict(status_res.all())

        present = status_counts.get(AttendanceStatus.PRESENT, 0)
        late = status_counts.get(AttendanceStatus.LATE, 0)
        half_day = status_counts.get(AttendanceStatus.HALF_DAY, 0)
        on_leave = status_counts.get(AttendanceStatus.ON_LEAVE, 0)
        wfh = status_counts.get(AttendanceStatus.WORK_FROM_HOME, 0)
        week_off = status_counts.get(AttendanceStatus.WEEK_OFF, 0)
        holiday = status_counts.get(AttendanceStatus.HOLIDAY, 0)

        recorded_count = sum(status_counts.values())
        absent = max(0, total_employees - recorded_count)

        return AttendanceDashboardResponse(
            today_date=today_date,
            total_employees=total_employees,
            present_count=present,
            absent_count=absent,
            late_count=late,
            on_leave_count=on_leave,
            wfh_count=wfh,
            half_day_count=half_day,
            week_off_count=week_off,
            holiday_count=holiday
        )

    # ---------------------------
    # Regularization Workflow
    # ---------------------------
    @staticmethod
    async def request_regularization(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID,
        data: RegularizationCreate
    ) -> AttendanceRegularization:
        # Check duplicate pending regularization request for same date
        existing = await db.execute(
            select(AttendanceRegularization).where(
                and_(
                    AttendanceRegularization.tenant_id == tenant_id,
                    AttendanceRegularization.employee_id == employee_id,
                    AttendanceRegularization.attendance_date == data.attendance_date,
                    AttendanceRegularization.status == RegularizationStatus.PENDING
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A pending regularization request already exists for this date."
            )

        reg = AttendanceRegularization(
            tenant_id=tenant_id,
            employee_id=employee_id,
            attendance_date=data.attendance_date,
            requested_check_in=data.requested_check_in,
            requested_check_out=data.requested_check_out,
            reason=data.reason,
            status=RegularizationStatus.PENDING
        )
        db.add(reg)
        await db.commit()
        await db.refresh(reg)
        return reg

    @staticmethod
    async def approve_regularization(
        db: AsyncSession,
        tenant_id: UUID,
        reg_id: UUID,
        approver_user_id: UUID
    ) -> AttendanceRegularization:
        res = await db.execute(
            select(AttendanceRegularization).where(
                and_(AttendanceRegularization.id == reg_id, AttendanceRegularization.tenant_id == tenant_id)
            )
        )
        reg = res.scalar_one_or_none()
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regularization request not found")

        reg.status = RegularizationStatus.APPROVED
        reg.approved_by_id = approver_user_id
        reg.approved_at = datetime.now(timezone.utc)

        # Update or create Attendance Record
        att_res = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.tenant_id == tenant_id,
                    Attendance.employee_id == reg.employee_id,
                    Attendance.attendance_date == reg.attendance_date
                )
            )
        )
        att = att_res.scalar_one_or_none()

        if not att:
            att = Attendance(
                tenant_id=tenant_id,
                employee_id=reg.employee_id,
                attendance_date=reg.attendance_date,
                status=AttendanceStatus.REGULARIZED,
                first_check_in=reg.requested_check_in,
                last_check_out=reg.requested_check_out,
                attendance_source=AttendanceSource.ADMIN,
                remarks=f"Regularized: {reg.reason}"
            )
            db.add(att)
        else:
            att.status = AttendanceStatus.REGULARIZED
            if reg.requested_check_in:
                att.first_check_in = reg.requested_check_in
            if reg.requested_check_out:
                att.last_check_out = reg.requested_check_out
            att.remarks = f"Regularized: {reg.reason}"

        await db.commit()
        await db.refresh(reg)

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="ATTENDANCE_REGULARIZATION_APPROVED",
            entity_type="AttendanceRegularization",
            entity_id=reg.id,
            actor_id=approver_user_id,
            details={"employee_id": str(reg.employee_id), "status": "APPROVED"}
        )
        return reg

    @staticmethod
    async def get_exceptions(
        db: AsyncSession,
        tenant_id: UUID,
        page: int = 1,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Tuple[List[Any], int]:
        where_clause = and_(
            Attendance.tenant_id == tenant_id,
            or_(
                Attendance.has_exception == True,
                Attendance.location_status == "OUTSIDE",
                Attendance.location_status == "LOW_ACCURACY",
                Attendance.location_status == "STALE_LOCATION",
                Attendance.verification_status == "FAILED"
            )
        )

        count_query = select(func.count(Attendance.id)).where(where_clause)
        if start_date:
            count_query = count_query.where(Attendance.attendance_date >= start_date)
        if end_date:
            count_query = count_query.where(Attendance.attendance_date <= end_date)

        total_res = await db.execute(count_query)
        total = total_res.scalar_one()

        query = (
            select(Attendance)
            .options(selectinload(Attendance.employee), selectinload(Attendance.events))
            .where(where_clause)
        )
        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)

        offset = (page - 1) * limit
        res = await db.execute(
            query.order_by(Attendance.attendance_date.desc()).offset(offset).limit(limit)
        )
        records = list(res.scalars().all())

        exceptions = []
        for att in records:
            emp = att.employee
            emp_name = f"{emp.first_name} {emp.last_name}" if emp else "Unknown Employee"
            latest_event = att.events[0] if att.events else None

            exceptions.append({
                "attendance_id": att.id,
                "employee_id": att.employee_id,
                "employee_name": emp_name,
                "attendance_date": str(att.attendance_date),
                "status": att.status.value if hasattr(att.status, 'value') else str(att.status),
                "location_status": att.location_status.value if hasattr(att.location_status, 'value') else (str(att.location_status) if att.location_status else None),
                "verification_status": att.verification_status.value if hasattr(att.verification_status, 'value') else (str(att.verification_status) if att.verification_status else None),
                "latitude": latest_event.latitude if latest_event else None,
                "longitude": latest_event.longitude if latest_event else None,
                "accuracy": latest_event.accuracy if latest_event else None,
                "distance_meters": latest_event.distance_meters if latest_event else None,
                "verification_id": latest_event.verification_id if latest_event else None,
                "remarks": att.remarks,
                "created_at": att.created_at
            })

        return exceptions, total
