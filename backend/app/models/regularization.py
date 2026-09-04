import enum
import uuid
from datetime import datetime, timezone, date, time
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class RegularizationRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AttendanceRegularization(Base):
    __tablename__ = "attendance_regularizations_v2"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_id = Column(UUID(as_uuid=True), ForeignKey("attendances.id", ondelete="CASCADE"), nullable=True, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)

    original_check_in = Column(DateTime(timezone=True), nullable=True)
    original_check_out = Column(DateTime(timezone=True), nullable=True)
    requested_check_in = Column(DateTime(timezone=True), nullable=False)
    requested_check_out = Column(DateTime(timezone=True), nullable=False)

    reason = Column(Text, nullable=False)
    status = Column(Enum(RegularizationRequestStatus, native_enum=False), nullable=False, default=RegularizationRequestStatus.PENDING, index=True)
    approval_instance_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    attendance = relationship("Attendance", foreign_keys=[attendance_id])
