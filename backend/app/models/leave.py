import enum
import uuid
from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Float,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class LeaveTypeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class AccrualFrequency(str, enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"


class LedgerTransactionType(str, enum.Enum):
    OPENING_BALANCE = "OPENING_BALANCE"
    ACCRUAL = "ACCRUAL"
    LEAVE_DEBIT = "LEAVE_DEBIT"
    LEAVE_REVERSAL = "LEAVE_REVERSAL"
    MANUAL_ADJUSTMENT = "MANUAL_ADJUSTMENT"
    CARRY_FORWARD = "CARRY_FORWARD"
    EXPIRY = "EXPIRY"
    ENCASHMENT = "ENCASHMENT"


class LeaveDurationType(str, enum.Enum):
    FULL_DAY = "FULL_DAY"
    HALF_DAY = "HALF_DAY"
    PARTIAL_DAY = "PARTIAL_DAY"


class HalfDayPosition(str, enum.Enum):
    FIRST_HALF = "FIRST_HALF"
    SECOND_HALF = "SECOND_HALF"


class LeaveRequestStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"


class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color_code = Column(String(20), nullable=False, default="#10B981")
    paid = Column(Boolean, nullable=False, default=True)
    requires_document = Column(Boolean, nullable=False, default=False)
    allow_half_day = Column(Boolean, nullable=False, default=True)
    allow_partial_day = Column(Boolean, nullable=False, default=False)
    allow_backdated = Column(Boolean, nullable=False, default=False)
    allow_future = Column(Boolean, nullable=False, default=True)
    minimum_notice_days = Column(Integer, nullable=False, default=0)
    maximum_consecutive_days = Column(Integer, nullable=True)
    status = Column(Enum(LeaveTypeStatus, native_enum=False), nullable=False, default=LeaveTypeStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="idx_leave_type_tenant_code"),
    )


class LeavePolicy(Base):
    __tablename__ = "leave_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    annual_entitlement = Column(Float, nullable=False, default=12.0)
    accrual_frequency = Column(Enum(AccrualFrequency, native_enum=False), nullable=False, default=AccrualFrequency.MONTHLY)
    accrual_amount = Column(Float, nullable=False, default=1.0)
    
    carry_forward_allowed = Column(Boolean, nullable=False, default=True)
    carry_forward_limit = Column(Float, nullable=False, default=5.0)
    encashment_allowed = Column(Boolean, nullable=False, default=False)
    maximum_balance = Column(Float, nullable=True)
    
    negative_balance_allowed = Column(Boolean, nullable=False, default=False)
    max_negative_balance = Column(Float, nullable=False, default=0.0)
    probation_allowed = Column(Boolean, nullable=False, default=True)
    notice_period_days = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    leave_type = relationship("LeaveType", foreign_keys=[leave_type_id])


class LeavePolicyAssignment(Base):
    __tablename__ = "leave_policy_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("leave_policies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=True)
    priority = Column(Integer, nullable=False, default=1)  # 1=Employee, 2=Dept, 3=Branch, 4=Org Default

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    policy = relationship("LeavePolicy", foreign_keys=[policy_id])


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False, default=lambda: datetime.now().year)

    allocated = Column(Float, nullable=False, default=0.0)
    accrued = Column(Float, nullable=False, default=0.0)
    adjusted = Column(Float, nullable=False, default=0.0)
    used = Column(Float, nullable=False, default=0.0)
    pending = Column(Float, nullable=False, default=0.0)
    expired = Column(Float, nullable=False, default=0.0)
    carried_forward = Column(Float, nullable=False, default=0.0)
    available = Column(Float, nullable=False, default=0.0)

    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    leave_type = relationship("LeaveType", foreign_keys=[leave_type_id])

    __table_args__ = (
        UniqueConstraint("tenant_id", "employee_id", "leave_type_id", "year", name="idx_leave_bal_tenant_emp_type_yr"),
    )


class LeaveLedger(Base):
    __tablename__ = "leave_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False, index=True)

    transaction_type = Column(Enum(LedgerTransactionType, native_enum=False), nullable=False)
    amount = Column(Float, nullable=False)  # positive for credit, negative for debit
    balance_after = Column(Float, nullable=False)
    reference_id = Column(String(100), nullable=True)  # Request ID or Task ID
    remarks = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    leave_type = relationship("LeaveType", foreign_keys=[leave_type_id])


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False, index=True)

    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    duration_type = Column(Enum(LeaveDurationType, native_enum=False), nullable=False, default=LeaveDurationType.FULL_DAY)
    half_day_position = Column(Enum(HalfDayPosition, native_enum=False), nullable=True)

    total_requested_days = Column(Float, nullable=False)
    working_days_count = Column(Float, nullable=False)
    holiday_days_count = Column(Float, nullable=False, default=0.0)
    weekly_off_days_count = Column(Float, nullable=False, default=0.0)

    reason = Column(Text, nullable=False)
    document_url = Column(String(500), nullable=True)
    status = Column(Enum(LeaveRequestStatus, native_enum=False), nullable=False, default=LeaveRequestStatus.PENDING, index=True)
    approval_instance_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    leave_type = relationship("LeaveType", foreign_keys=[leave_type_id])

    __table_args__ = (
        Index("idx_leave_req_tenant_emp_status", "tenant_id", "employee_id", "status"),
        Index("idx_leave_req_tenant_dates", "tenant_id", "start_date", "end_date"),
    )
