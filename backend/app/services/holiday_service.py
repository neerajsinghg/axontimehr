import uuid
from typing import List, Optional, Tuple, Set
from datetime import date, datetime, timezone
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.holiday import (
    HolidayCalendar,
    HolidayMaster as Phase6HolidayMaster,
    HolidayCalendarAssignment,
    Phase6HolidayType,
    CalendarStatus
)
from app.schemas.holiday import (
    HolidayCalendarCreate,
    HolidayCreate
)


class HolidayService:

    @staticmethod
    async def create_calendar(db: AsyncSession, tenant_id: uuid.UUID, data: HolidayCalendarCreate) -> HolidayCalendar:
        existing = await db.execute(
            select(HolidayCalendar).where(
                and_(
                    HolidayCalendar.tenant_id == tenant_id,
                    HolidayCalendar.code == data.code,
                    HolidayCalendar.year == data.year
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Holiday calendar with code '{data.code}' for year {data.year} already exists."
            )

        cal = HolidayCalendar(
            tenant_id=tenant_id,
            code=data.code,
            name=data.name,
            year=data.year,
            organization_id=data.organization_id,
            branch_id=data.branch_id,
            status=data.status
        )
        db.add(cal)
        await db.commit()
        await db.refresh(cal)
        return cal

    @staticmethod
    async def get_calendars(db: AsyncSession, tenant_id: uuid.UUID, year: Optional[int] = None) -> List[dict]:
        query = select(HolidayCalendar).options(selectinload(HolidayCalendar.holidays)).where(HolidayCalendar.tenant_id == tenant_id)
        if year:
            query = query.where(HolidayCalendar.year == year)

        res = await db.execute(query.order_by(HolidayCalendar.year.desc(), HolidayCalendar.name))
        cals = res.scalars().all()

        result = []
        for c in cals:
            result.append({
                "id": c.id,
                "tenant_id": c.tenant_id,
                "code": c.code,
                "name": c.name,
                "year": c.year,
                "organization_id": c.organization_id,
                "branch_id": c.branch_id,
                "status": c.status.value if hasattr(c.status, 'value') else str(c.status),
                "total_holidays": len(c.holidays),
                "created_at": c.created_at,
                "updated_at": c.updated_at
            })
        return result

    @staticmethod
    async def create_holiday(db: AsyncSession, tenant_id: uuid.UUID, data: HolidayCreate) -> Phase6HolidayMaster:
        cal_res = await db.execute(
            select(HolidayCalendar).where(
                and_(
                    HolidayCalendar.id == data.calendar_id,
                    HolidayCalendar.tenant_id == tenant_id
                )
            )
        )
        cal = cal_res.scalar_one_or_none()
        if not cal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Holiday calendar not found."
            )

        # Check conflict
        existing = await db.execute(
            select(Phase6HolidayMaster).where(
                and_(
                    Phase6HolidayMaster.calendar_id == data.calendar_id,
                    Phase6HolidayMaster.holiday_date == data.holiday_date
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A holiday on date '{data.holiday_date}' already exists in this calendar."
            )

        h = Phase6HolidayMaster(
            tenant_id=tenant_id,
            calendar_id=data.calendar_id,
            holiday_date=data.holiday_date,
            holiday_name=data.holiday_name,
            holiday_type=data.holiday_type,
            branch_id=data.branch_id,
            description=data.description,
            status=data.status
        )
        db.add(h)
        await db.commit()
        await db.refresh(h)
        return h

    @staticmethod
    async def get_holidays_for_range(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        start_date: date,
        end_date: date,
        branch_id: Optional[uuid.UUID] = None
    ) -> List[Phase6HolidayMaster]:
        query = (
            select(Phase6HolidayMaster)
            .join(HolidayCalendar, Phase6HolidayMaster.calendar_id == HolidayCalendar.id)
            .where(
                and_(
                    Phase6HolidayMaster.tenant_id == tenant_id,
                    Phase6HolidayMaster.holiday_date >= start_date,
                    Phase6HolidayMaster.holiday_date <= end_date,
                    Phase6HolidayMaster.status == CalendarStatus.ACTIVE,
                    HolidayCalendar.status == CalendarStatus.ACTIVE
                )
            )
        )
        if branch_id:
            query = query.where(
                or_(
                    Phase6HolidayMaster.branch_id == branch_id,
                    Phase6HolidayMaster.branch_id == None,
                    HolidayCalendar.branch_id == branch_id,
                    HolidayCalendar.branch_id == None
                )
            )

        res = await db.execute(query.order_by(Phase6HolidayMaster.holiday_date.asc()))
        return list(res.scalars().all())

    @staticmethod
    async def get_holiday_dates_set(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        start_date: date,
        end_date: date,
        branch_id: Optional[uuid.UUID] = None
    ) -> Set[date]:
        holidays = await HolidayService.get_holidays_for_range(db, tenant_id, start_date, end_date, branch_id)
        # Exclude optional holidays unless mandatory
        return {h.holiday_date for h in holidays if h.holiday_type == Phase6HolidayType.MANDATORY}
