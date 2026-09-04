from typing import Optional
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.models.regularization import RegularizationRequestStatus


class RegularizationCreate(BaseModel):
    attendance_date: date
    requested_check_in: datetime
    requested_check_out: datetime
    reason: str = Field(..., min_length=3)


class RegularizationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    attendance_id: Optional[UUID] = None
    employee_id: UUID
    employee_name: str
    attendance_date: date
    original_check_in: Optional[datetime] = None
    original_check_out: Optional[datetime] = None
    requested_check_in: datetime
    requested_check_out: datetime
    reason: str
    status: RegularizationRequestStatus
    approval_instance_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
