from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.models.leave import (
    LeaveTypeStatus,
    AccrualFrequency,
    LedgerTransactionType,
    LeaveDurationType,
    HalfDayPosition,
    LeaveRequestStatus
)


class LeaveTypeCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    color_code: str = Field("#10B981", max_length=20)
    paid: bool = True
    requires_document: bool = False
    allow_half_day: bool = True
    allow_partial_day: bool = False
    allow_backdated: bool = False
    allow_future: bool = True
    minimum_notice_days: int = 0
    maximum_consecutive_days: Optional[int] = None
    status: LeaveTypeStatus = LeaveTypeStatus.ACTIVE

    model_config = {"from_attributes": True, "use_enum_values": True}


class LeaveTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color_code: Optional[str] = None
    paid: Optional[bool] = None
    requires_document: Optional[bool] = None
    allow_half_day: Optional[bool] = None
    allow_partial_day: Optional[bool] = None
    allow_backdated: Optional[bool] = None
    allow_future: Optional[bool] = None
    minimum_notice_days: Optional[int] = None
    maximum_consecutive_days: Optional[int] = None
    status: Optional[LeaveTypeStatus] = None


class LeaveTypeResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    color_code: str
    paid: bool
    requires_document: bool
    allow_half_day: bool
    allow_partial_day: bool
    allow_backdated: bool
    allow_future: bool
    minimum_notice_days: int
    maximum_consecutive_days: Optional[int] = None
    status: LeaveTypeStatus
    created_at: datetime
    updated_at: datetime


class LeavePolicyCreate(BaseModel):
    leave_type_id: UUID
    name: str = Field(..., max_length=100)
    annual_entitlement: float = 12.0
    accrual_frequency: AccrualFrequency = AccrualFrequency.MONTHLY
    accrual_amount: float = 1.0
    carry_forward_allowed: bool = True
    carry_forward_limit: float = 5.0
    encashment_allowed: bool = False
    maximum_balance: Optional[float] = None
    negative_balance_allowed: bool = False
    max_negative_balance: float = 0.0
    probation_allowed: bool = True
    notice_period_days: int = 0


class LeavePolicyResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    leave_type_id: UUID
    name: str
    annual_entitlement: float
    accrual_frequency: AccrualFrequency
    accrual_amount: float
    carry_forward_allowed: bool
    carry_forward_limit: float
    encashment_allowed: bool
    maximum_balance: Optional[float] = None
    negative_balance_allowed: bool
    max_negative_balance: float
    probation_allowed: bool
    notice_period_days: int
    created_at: datetime
    updated_at: datetime


class LeaveBalanceResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    leave_type_id: UUID
    leave_type_code: str
    leave_type_name: str
    color_code: str
    year: int
    allocated: float
    accrued: float
    adjusted: float
    used: float
    pending: float
    expired: float
    carried_forward: float
    available: float
    updated_at: datetime


class LeaveLedgerResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    leave_type_id: UUID
    leave_type_name: str
    transaction_type: LedgerTransactionType
    amount: float
    balance_after: float
    reference_id: Optional[str] = None
    remarks: Optional[str] = None
    created_at: datetime


class LeaveRequestCreate(BaseModel):
    leave_type_id: UUID
    start_date: date
    end_date: date
    duration_type: LeaveDurationType = LeaveDurationType.FULL_DAY
    half_day_position: Optional[HalfDayPosition] = None
    reason: str
    document_url: Optional[str] = None


class LeaveRequestResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    employee_name: str
    leave_type_id: UUID
    leave_type_name: str
    leave_type_code: str
    color_code: str
    start_date: date
    end_date: date
    duration_type: LeaveDurationType
    half_day_position: Optional[HalfDayPosition] = None
    total_requested_days: float
    working_days_count: float
    holiday_days_count: float
    weekly_off_days_count: float
    reason: str
    document_url: Optional[str] = None
    status: LeaveRequestStatus
    approval_instance_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
