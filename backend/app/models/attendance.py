import enum
import uuid
from datetime import datetime, timezone, time, date
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Float,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Index,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class ShiftType(str, enum.Enum):
    FIXED = "FIXED"
    EVENING = "EVENING"
    NIGHT = "NIGHT"
    FLEXIBLE = "FLEXIBLE"
    SPLIT = "SPLIT"

class ShiftStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LATE = "LATE"
    EARLY_EXIT = "EARLY_EXIT"
    ON_LEAVE = "ON_LEAVE"
    HOLIDAY = "HOLIDAY"
    WEEK_OFF = "WEEK_OFF"
    WORK_FROM_HOME = "WORK_FROM_HOME"
    REGULARIZED = "REGULARIZED"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"

class AttendanceSource(str, enum.Enum):
    WEB = "WEB"
    MOBILE = "MOBILE"
    ADMIN = "ADMIN"
    API = "API"
    BIOMETRIC = "BIOMETRIC"
    IMPORT = "IMPORT"
    SYSTEM = "SYSTEM"

class AttendanceEventType(str, enum.Enum):
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"

class RegularizationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class HolidayType(str, enum.Enum):
    NATIONAL = "NATIONAL"
    REGIONAL = "REGIONAL"
    COMPANY = "COMPANY"
    OPTIONAL = "OPTIONAL"


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    shift_type = Column(Enum(ShiftType, native_enum=False), nullable=False, default=ShiftType.FIXED)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    grace_period_minutes = Column(Integer, nullable=False, default=15)
    late_threshold_minutes = Column(Integer, nullable=False, default=30)
    early_exit_threshold_minutes = Column(Integer, nullable=False, default=15)
    minimum_work_minutes = Column(Integer, nullable=False, default=480)
    break_duration_minutes = Column(Integer, nullable=False, default=60)
    is_overnight = Column(Boolean, nullable=False, default=False)
    status = Column(Enum(ShiftStatus, native_enum=False), nullable=False, default=ShiftStatus.ACTIVE)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="idx_shift_tenant_code"),
    )


class EmployeeShiftAssignment(Base):
    __tablename__ = "employee_shift_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_id = Column(UUID(as_uuid=True), ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False, index=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    weekly_offs = Column(JSON, nullable=False, default=lambda: ["SUNDAY"])
    status = Column(Enum(ShiftStatus, native_enum=False), nullable=False, default=ShiftStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    shift = relationship("Shift", foreign_keys=[shift_id])


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_id = Column(UUID(as_uuid=True), ForeignKey("shifts.id", ondelete="SET NULL"), nullable=True, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    status = Column(Enum(AttendanceStatus, native_enum=False), nullable=False, default=AttendanceStatus.PENDING, index=True)
    
    first_check_in = Column(DateTime(timezone=True), nullable=True)
    last_check_out = Column(DateTime(timezone=True), nullable=True)
    total_work_minutes = Column(Integer, nullable=False, default=0)
    total_break_minutes = Column(Integer, nullable=False, default=0)
    overtime_minutes = Column(Integer, nullable=False, default=0)
    late_minutes = Column(Integer, nullable=False, default=0)
    early_exit_minutes = Column(Integer, nullable=False, default=0)
    worked_minutes = Column(Integer, nullable=False, default=0)
    
    # Phase 5 GPS & Verification Extensions
    location_status = Column(String(50), nullable=False, default="NOT_REQUIRED")
    verification_status = Column(String(50), nullable=False, default="NOT_REQUIRED")
    has_exception = Column(Boolean, nullable=False, default=False)

    attendance_source = Column(Enum(AttendanceSource, native_enum=False), nullable=False, default=AttendanceSource.WEB)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    shift = relationship("Shift", foreign_keys=[shift_id])
    events = relationship("AttendanceEvent", back_populates="attendance", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "employee_id", "attendance_date", name="idx_att_tenant_emp_date"),
        Index("idx_att_tenant_date", "tenant_id", "attendance_date"),
        Index("idx_att_tenant_status_date", "tenant_id", "status", "attendance_date"),
        Index("idx_att_tenant_exception", "tenant_id", "has_exception"),
    )


class AttendanceEvent(Base):
    __tablename__ = "attendance_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_id = Column(UUID(as_uuid=True), ForeignKey("attendances.id", ondelete="CASCADE"), nullable=False, index=True)
    
    event_type = Column(Enum(AttendanceEventType, native_enum=False), nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    source = Column(Enum(AttendanceSource, native_enum=False), nullable=False, default=AttendanceSource.WEB)
    
    # Phase 5 Metadata Extensions
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    distance_meters = Column(Float, nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=True)
    geofence_status = Column(String(50), nullable=True)
    verification_status = Column(String(50), nullable=True)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("attendance_verifications.id", ondelete="SET NULL"), nullable=True, index=True)

    device_reference = Column(String(255), nullable=True)
    location_reference = Column(String(255), nullable=True)
    verification_reference = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    attendance = relationship("Attendance", back_populates="events")


class AttendanceRegularization(Base):
    __tablename__ = "attendance_regularizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    
    requested_check_in = Column(DateTime(timezone=True), nullable=True)
    requested_check_out = Column(DateTime(timezone=True), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(Enum(RegularizationStatus, native_enum=False), nullable=False, default=RegularizationStatus.PENDING, index=True)
    
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=True, index=True)
    
    holiday_name = Column(String(150), nullable=False)
    holiday_date = Column(Date, nullable=False, index=True)
    holiday_type = Column(Enum(HolidayType, native_enum=False), nullable=False, default=HolidayType.COMPANY)
    description = Column(Text, nullable=True)
    status = Column(Enum(ShiftStatus, native_enum=False), nullable=False, default=ShiftStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    branch = relationship("Branch", foreign_keys=[branch_id])

    __table_args__ = (
        UniqueConstraint("tenant_id", "branch_id", "holiday_date", name="idx_holiday_tenant_branch_date"),
    )
