import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.regularization import AttendanceRegularization, RegularizationRequestStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.employee import Employee
from app.schemas.regularization import RegularizationCreate
from app.services.workflow_service import WorkflowService
from app.services.audit_service import AuditService


class RegularizationService:

    @staticmethod
    async def create_request(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        data: RegularizationCreate
    ) -> AttendanceRegularization:
        if data.requested_check_in >= data.requested_check_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested check-in time must be before requested check-out time."
            )

        # Check existing attendance
        att_res = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.tenant_id == tenant_id,
                    Attendance.employee_id == employee_id,
                    Attendance.attendance_date == data.attendance_date
                )
            )
        )
        att = att_res.scalar_one_or_none()

        orig_in = att.first_check_in if att else None
        orig_out = att.last_check_out if att else None

        reg = AttendanceRegularization(
            tenant_id=tenant_id,
            attendance_id=att.id if att else None,
            employee_id=employee_id,
            attendance_date=data.attendance_date,
            original_check_in=orig_in,
            original_check_out=orig_out,
            requested_check_in=data.requested_check_in,
            requested_check_out=data.requested_check_out,
            reason=data.reason,
            status=RegularizationRequestStatus.PENDING
        )
        db.add(reg)
        await db.flush()

        # Start approval instance
        instance = await WorkflowService.start_approval_instance(
            db, tenant_id, "REGULARIZATION", reg.id, employee_id
        )
        reg.approval_instance_id = instance.id

        await db.commit()
        await db.refresh(reg)
        return reg

    @staticmethod
    async def approve_request(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        request_id: uuid.UUID
    ) -> AttendanceRegularization:
        reg_res = await db.execute(
            select(AttendanceRegularization).where(
                and_(
                    AttendanceRegularization.id == request_id,
                    AttendanceRegularization.tenant_id == tenant_id
                )
            )
        )
        reg = reg_res.scalar_one_or_none()
        if not reg or reg.status != RegularizationRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Regularization request not found or not pending."
            )

        reg.status = RegularizationRequestStatus.APPROVED

        # Calculate worked minutes
        diff = reg.requested_check_out - reg.requested_check_in
        worked_mins = max(0, int(diff.total_seconds() // 60))

        # Update or create attendance
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
                first_check_in=reg.requested_check_in,
                last_check_out=reg.requested_check_out,
                worked_minutes=worked_mins,
                total_work_minutes=worked_mins,
                status=AttendanceStatus.PRESENT,
                remarks=f"Regularized: {reg.reason}"
            )
            db.add(att)
        else:
            att.first_check_in = reg.requested_check_in
            att.last_check_out = reg.requested_check_out
            att.worked_minutes = worked_mins
            att.total_work_minutes = worked_mins
            att.status = AttendanceStatus.PRESENT
            att.remarks = f"Regularized: {reg.reason}"

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            actor_id=None,
            action="ATTENDANCE_REGULARIZATION_APPROVED",
            entity_type="AttendanceRegularization",
            entity_id=str(reg.id),
            details={
                "employee_id": str(reg.employee_id),
                "attendance_date": str(reg.attendance_date),
                "requested_check_in": str(reg.requested_check_in),
                "requested_check_out": str(reg.requested_check_out)
            }
        )

        await db.commit()
        await db.refresh(reg)
        return reg

    @staticmethod
    async def get_requests(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: Optional[uuid.UUID] = None
    ) -> List[dict]:
        query = (
            select(AttendanceRegularization)
            .options(selectinload(AttendanceRegularization.employee))
            .where(AttendanceRegularization.tenant_id == tenant_id)
        )
        if employee_id:
            query = query.where(AttendanceRegularization.employee_id == employee_id)

        res = await db.execute(query.order_by(AttendanceRegularization.created_at.desc()))
        records = res.scalars().all()

        result = []
        for r in records:
            emp_name = f"{r.employee.first_name} {r.employee.last_name}" if r.employee else "Unknown Employee"
            result.append({
                "id": r.id,
                "tenant_id": r.tenant_id,
                "attendance_id": r.attendance_id,
                "employee_id": r.employee_id,
                "employee_name": emp_name,
                "attendance_date": r.attendance_date,
                "original_check_in": r.original_check_in,
                "original_check_out": r.original_check_out,
                "requested_check_in": r.requested_check_in,
                "requested_check_out": r.requested_check_out,
                "reason": r.reason,
                "status": r.status.value if hasattr(r.status, 'value') else str(r.status),
                "approval_instance_id": r.approval_instance_id,
                "created_at": r.created_at,
                "updated_at": r.updated_at
            })
        return result
