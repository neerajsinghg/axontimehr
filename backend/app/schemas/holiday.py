from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.models.holiday import Phase6HolidayType, CalendarStatus


class HolidayCalendarCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    year: int = Field(default_factory=lambda: datetime.now().year)
    organization_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    status: str = "ACTIVE"


class HolidayCalendarResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    year: int
    organization_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    status: str
    total_holidays: int = 0
    created_at: datetime
    updated_at: datetime


class HolidayCreate(BaseModel):
    calendar_id: UUID
    holiday_date: date
    holiday_name: str = Field(..., max_length=100)
    holiday_type: str = "MANDATORY"
    branch_id: Optional[UUID] = None
    description: Optional[str] = None
    status: str = "ACTIVE"

    model_config = {"from_attributes": True}


class HolidayResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    calendar_id: UUID
    holiday_date: date
    holiday_name: str
    holiday_type: str
    branch_id: Optional[UUID] = None
    branch_name: Optional[str] = None
    description: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
