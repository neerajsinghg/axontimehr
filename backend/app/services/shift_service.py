from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, timezone
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.attendance import (
    Shift,
    EmployeeShiftAssignment,
    Holiday,
    ShiftStatus
)
from app.schemas.attendance import (
    ShiftCreate,
    ShiftUpdate,
    ShiftAssignmentCreate,
    HolidayCreate
)
from app.services.audit_service import AuditService

class ShiftService:
    @staticmethod
    async def create_shift(db: AsyncSession, tenant_id: UUID, data: ShiftCreate, actor_id: Optional[UUID] = None) -> Shift:
        # Check duplicate shift code per tenant
        res = await db.execute(select(Shift).where(and_(Shift.tenant_id == tenant_id, Shift.code == data.code)))
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Shift code '{data.code}' already exists for this tenant."
            )

        shift = Shift(
            tenant_id=tenant_id,
            **data.model_dump()
        )
        db.add(shift)
        await db.commit()
        await db.refresh(shift)

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="SHIFT_CREATED",
            entity_type="Shift",
            entity_id=shift.id,
            actor_id=actor_id,
            details={"code": shift.code, "name": shift.name}
        )
        return shift

    @staticmethod
    async def get_shifts(db: AsyncSession, tenant_id: UUID) -> List[Shift]:
        res = await db.execute(select(Shift).where(Shift.tenant_id == tenant_id).order_by(Shift.created_at.desc()))
        return list(res.scalars().all())

    @staticmethod
    async def get_shift_by_id(db: AsyncSession, tenant_id: UUID, shift_id: UUID) -> Shift:
        res = await db.execute(select(Shift).where(and_(Shift.tenant_id == tenant_id, Shift.id == shift_id)))
        shift = res.scalar_one_or_none()
        if not shift:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found.")
        return shift

    @staticmethod
    async def update_shift(db: AsyncSession, tenant_id: UUID, shift_id: UUID, data: ShiftUpdate, actor_id: Optional[UUID] = None) -> Shift:
        shift = await ShiftService.get_shift_by_id(db, tenant_id, shift_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(shift, key, value)

        db.add(shift)
        await db.commit()
        await db.refresh(shift)

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="SHIFT_UPDATED",
            entity_type="Shift",
            entity_id=shift.id,
            actor_id=actor_id,
            details={"updated_fields": list(update_data.keys())}
        )
        return shift

    # ------------------ Shift Assignment / Roster ------------------
    @staticmethod
    async def assign_employee_shift(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID,
        data: ShiftAssignmentCreate,
        actor_id: Optional[UUID] = None
    ) -> EmployeeShiftAssignment:
        # Validate Shift exists
        await ShiftService.get_shift_by_id(db, tenant_id, data.shift_id)

        # Expire any current active assignment that overlaps
        existing_res = await db.execute(
            select(EmployeeShiftAssignment).where(
                and_(
                    EmployeeShiftAssignment.tenant_id == tenant_id,
                    EmployeeShiftAssignment.employee_id == employee_id,
                    EmployeeShiftAssignment.status == ShiftStatus.ACTIVE,
                    EmployeeShiftAssignment.effective_to.is_(None)
                )
            )
        )
        existing_assignment = existing_res.scalar_one_or_none()
        if existing_assignment:
            existing_assignment.effective_to = data.effective_from
            existing_assignment.status = ShiftStatus.INACTIVE
            db.add(existing_assignment)

        new_assignment = EmployeeShiftAssignment(
            tenant_id=tenant_id,
            employee_id=employee_id,
            shift_id=data.shift_id,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            weekly_offs=data.weekly_offs,
            status=ShiftStatus.ACTIVE
        )
        db.add(new_assignment)
        await db.commit()

        # Re-query with shift relationship pre-loaded
        assignment_res = await db.execute(
            select(EmployeeShiftAssignment)
            .options(selectinload(EmployeeShiftAssignment.shift))
            .where(EmployeeShiftAssignment.id == new_assignment.id)
        )
        assignment_loaded = assignment_res.scalar_one()

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="SHIFT_ROSTER_ASSIGNED",
            entity_type="EmployeeShiftAssignment",
            entity_id=assignment_loaded.id,
            actor_id=actor_id,
            details={"employee_id": str(employee_id), "shift_id": str(data.shift_id), "effective_from": str(data.effective_from)}
        )
        return assignment_loaded

    @staticmethod
    async def get_active_shift_assignment(db: AsyncSession, tenant_id: UUID, employee_id: UUID, target_date: date) -> Optional[EmployeeShiftAssignment]:
        res = await db.execute(
            select(EmployeeShiftAssignment)
            .options(selectinload(EmployeeShiftAssignment.shift))
            .where(
                and_(
                    EmployeeShiftAssignment.tenant_id == tenant_id,
                    EmployeeShiftAssignment.employee_id == employee_id,
                    EmployeeShiftAssignment.status == ShiftStatus.ACTIVE,
                    EmployeeShiftAssignment.effective_from <= target_date,
                    or_(EmployeeShiftAssignment.effective_to.is_(None), EmployeeShiftAssignment.effective_to >= target_date)
                )
            )
            .order_by(EmployeeShiftAssignment.effective_from.desc())
        )
        return res.scalars().first()

    # ------------------
    # Holiday Calendar
    # ------------------
    @staticmethod
    async def create_holiday(db: AsyncSession, tenant_id: UUID, data: HolidayCreate, actor_id: Optional[UUID] = None) -> Holiday:
        holiday = Holiday(
            tenant_id=tenant_id,
            branch_id=data.branch_id,
            holiday_name=data.holiday_name,
            holiday_date=data.holiday_date,
            holiday_type=data.holiday_type,
            description=data.description,
            status=data.status
        )
        db.add(holiday)
        await db.commit()
        await db.refresh(holiday)
        return holiday

    @staticmethod
    async def get_holidays(db: AsyncSession, tenant_id: UUID, branch_id: Optional[UUID] = None) -> List[Holiday]:
        query = select(Holiday).where(and_(Holiday.tenant_id == tenant_id, Holiday.status == ShiftStatus.ACTIVE))
        if branch_id:
            query = query.where(or_(Holiday.branch_id == branch_id, Holiday.branch_id.is_(None)))
        res = await db.execute(query.order_by(Holiday.holiday_date))
        return list(res.scalars().all())
