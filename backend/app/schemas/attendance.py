from typing import Optional, List
from datetime import datetime, date, time
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.attendance import (
    ShiftType,
    ShiftStatus,
    AttendanceStatus,
    AttendanceSource,
    AttendanceEventType,
    RegularizationStatus,
    HolidayType
)

# ----------------------------
# Shift Schemas
# ----------------------------
class ShiftCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    shift_type: ShiftType = ShiftType.FIXED
    start_time: time
    end_time: time
    grace_period_minutes: int = 15
    late_threshold_minutes: int = 30
    early_exit_threshold_minutes: int = 15
    minimum_work_minutes: int = 480
    break_duration_minutes: int = 60
    is_overnight: bool = False
    status: ShiftStatus = ShiftStatus.ACTIVE

class ShiftUpdate(BaseModel):
    name: Optional[str] = None
    shift_type: Optional[ShiftType] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    grace_period_minutes: Optional[int] = None
    late_threshold_minutes: Optional[int] = None
    early_exit_threshold_minutes: Optional[int] = None
    minimum_work_minutes: Optional[int] = None
    break_duration_minutes: Optional[int] = None
    is_overnight: Optional[bool] = None
    status: Optional[ShiftStatus] = None

class ShiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    shift_type: ShiftType
    start_time: time
    end_time: time
    grace_period_minutes: int
    late_threshold_minutes: int
    early_exit_threshold_minutes: int
    minimum_work_minutes: int
    break_duration_minutes: int
    is_overnight: bool
    status: ShiftStatus
    created_at: datetime
    updated_at: datetime


# ----------------------------
# Employee Shift Roster Schemas
# ----------------------------
class ShiftAssignmentCreate(BaseModel):
    shift_id: UUID
    effective_from: date
    effective_to: Optional[date] = None
    weekly_offs: List[str] = Field(default_factory=lambda: ["SUNDAY"])

class ShiftAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    shift_id: UUID
    effective_from: date
    effective_to: Optional[date] = None
    weekly_offs: List[str]
    status: ShiftStatus
    created_at: datetime
    shift: Optional[ShiftResponse] = None


# ----------------------------
# Punch / Event Schemas
# ----------------------------
class PunchRequest(BaseModel):
    source: AttendanceSource = AttendanceSource.WEB
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    accuracy: Optional[float] = Field(None, gt=0.0)
    captured_at: Optional[datetime] = None
    verification_id: Optional[UUID] = None
    device_id: Optional[str] = None
    platform: Optional[str] = None
    app_version: Optional[str] = None
    device_reference: Optional[str] = None
    location_reference: Optional[str] = None
    verification_reference: Optional[str] = None
    remarks: Optional[str] = None

class AttendanceEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_type: AttendanceEventType
    event_time: datetime
    source: AttendanceSource
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    distance_meters: Optional[float] = None
    captured_at: Optional[datetime] = None
    geofence_status: Optional[str] = None
    verification_status: Optional[str] = None
    verification_id: Optional[UUID] = None
    device_reference: Optional[str] = None
    location_reference: Optional[str] = None
    verification_reference: Optional[str] = None
    remarks: Optional[str] = None


# ----------------------------
# Attendance Record Schemas
# ----------------------------
class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    shift_id: Optional[UUID] = None
    attendance_date: date
    status: AttendanceStatus
    first_check_in: Optional[datetime] = None
    last_check_out: Optional[datetime] = None
    total_work_minutes: int
    total_break_minutes: int
    overtime_minutes: int
    late_minutes: int
    early_exit_minutes: int
    worked_minutes: int
    location_status: str = "NOT_REQUIRED"
    verification_status: str = "NOT_REQUIRED"
    has_exception: bool = False
    attendance_source: AttendanceSource
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    shift: Optional[ShiftResponse] = None
    events: Optional[List[AttendanceEventResponse]] = None

class AttendanceListResponse(BaseModel):
    success: bool = True
    data: List[AttendanceResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class DailyAttendanceStatusResponse(BaseModel):
    today_date: date
    is_checked_in: bool
    is_checked_out: bool
    current_status: AttendanceStatus
    first_check_in: Optional[datetime] = None
    last_check_out: Optional[datetime] = None
    worked_minutes: int
    shift: Optional[ShiftResponse] = None


# ----------------------------
# Regularization Schemas
# ----------------------------
class RegularizationCreate(BaseModel):
    attendance_date: date
    requested_check_in: Optional[datetime] = None
    requested_check_out: Optional[datetime] = None
    reason: str

class RegularizationActionRequest(BaseModel):
    rejection_reason: Optional[str] = None

class RegularizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    attendance_date: date
    requested_check_in: Optional[datetime] = None
    requested_check_out: Optional[datetime] = None
    reason: str
    status: RegularizationStatus
    approved_by_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime


# ----------------------------
# Holiday Schemas
# ----------------------------
class HolidayCreate(BaseModel):
    holiday_name: str
    holiday_date: date
    branch_id: Optional[UUID] = None
    holiday_type: HolidayType = HolidayType.COMPANY
    description: Optional[str] = None
    status: ShiftStatus = ShiftStatus.ACTIVE

class HolidayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    branch_id: Optional[UUID] = None
    holiday_name: str
    holiday_date: date
    holiday_type: HolidayType
    description: Optional[str] = None
    status: ShiftStatus
    created_at: datetime


# ----------------------------
# Dashboard Metrics Schema
# ----------------------------
class AttendanceDashboardResponse(BaseModel):
    success: bool = True
    today_date: date
    total_employees: int
    present_count: int
    absent_count: int
    late_count: int
    on_leave_count: int
    wfh_count: int
    half_day_count: int
    week_off_count: int
    holiday_count: int
