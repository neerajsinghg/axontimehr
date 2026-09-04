import enum
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
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


class Phase6HolidayType(str, enum.Enum):
    MANDATORY = "MANDATORY"
    OPTIONAL = "OPTIONAL"
    RESTRICTED = "RESTRICTED"


class CalendarStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class HolidayCalendar(Base):
    __tablename__ = "holiday_calendars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False, default=lambda: datetime.now().year)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=True)
    status = Column(Enum(CalendarStatus, native_enum=False), nullable=False, default=CalendarStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    holidays = relationship("HolidayMaster", back_populates="calendar", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", "year", name="idx_holiday_cal_tenant_code_yr"),
    )


class HolidayMaster(Base):
    __tablename__ = "holidays_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    calendar_id = Column(UUID(as_uuid=True), ForeignKey("holiday_calendars.id", ondelete="CASCADE"), nullable=False, index=True)
    
    holiday_date = Column(Date, nullable=False, index=True)
    holiday_name = Column(String(100), nullable=False)
    holiday_type = Column(Enum(Phase6HolidayType, native_enum=False), nullable=False, default=Phase6HolidayType.MANDATORY)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(CalendarStatus, native_enum=False), nullable=False, default=CalendarStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    calendar = relationship("HolidayCalendar", back_populates="holidays")

    __table_args__ = (
        UniqueConstraint("calendar_id", "holiday_date", name="idx_holiday_cal_date"),
    )


class HolidayCalendarAssignment(Base):
    __tablename__ = "holiday_calendar_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    calendar_id = Column(UUID(as_uuid=True), ForeignKey("holiday_calendars.id", ondelete="CASCADE"), nullable=False, index=True)

    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    calendar = relationship("HolidayCalendar")
