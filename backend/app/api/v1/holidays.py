from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_current_tenant_id, require_permission
from app.schemas.holiday import (
    HolidayCalendarCreate,
    HolidayCalendarResponse,
    HolidayCreate,
    HolidayResponse
)
from app.services.holiday_service import HolidayService

router = APIRouter(prefix="/holidays", tags=["Holiday Calendars"])


@router.post("/calendars", response_model=HolidayCalendarResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday_calendar(
    data: HolidayCalendarCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    cal = await HolidayService.create_calendar(db, tenant_id, data)
    return HolidayCalendarResponse(
        id=cal.id,
        tenant_id=cal.tenant_id,
        code=cal.code,
        name=cal.name,
        year=cal.year,
        organization_id=cal.organization_id,
        branch_id=cal.branch_id,
        status=cal.status,
        total_holidays=0,
        created_at=cal.created_at,
        updated_at=cal.updated_at
    )


@router.get("/calendars", response_model=List[HolidayCalendarResponse])
async def get_holiday_calendars(
    year: Optional[int] = None,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await HolidayService.get_calendars(db, tenant_id, year)


@router.post("/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    data: HolidayCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    h = await HolidayService.create_holiday(db, tenant_id, data)
    return HolidayResponse(
        id=h.id,
        tenant_id=h.tenant_id,
        calendar_id=h.calendar_id,
        holiday_date=h.holiday_date,
        holiday_name=h.holiday_name,
        holiday_type=h.holiday_type.value if hasattr(h.holiday_type, 'value') else str(h.holiday_type),
        branch_id=h.branch_id,
        description=h.description,
        status=h.status.value if hasattr(h.status, 'value') else str(h.status),
        created_at=h.created_at
    )
