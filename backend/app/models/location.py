import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Index,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base

class GeofenceType(str, enum.Enum):
    CIRCULAR = "CIRCULAR"
    POLYGON = "POLYGON"

class LocationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"

class OutsideGeofenceAction(str, enum.Enum):
    REJECT = "REJECT"
    ALLOW_WITH_WARNING = "ALLOW_WITH_WARNING"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RECORD_EXCEPTION = "RECORD_EXCEPTION"

class VerificationFailureAction(str, enum.Enum):
    REJECT = "REJECT"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"
    RECORD_EXCEPTION = "RECORD_EXCEPTION"

class VerificationStatus(str, enum.Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ERROR = "ERROR"

class VerificationProviderType(str, enum.Enum):
    MOCK = "MOCK"
    INTERNAL_FACE = "INTERNAL_FACE"
    THIRD_PARTY = "THIRD_PARTY"


class AttendanceLocation(Base):
    __tablename__ = "attendance_locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    radius_meters: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    accuracy_requirement: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    
    geofence_type: Mapped[GeofenceType] = mapped_column(Enum(GeofenceType, native_enum=False), default=GeofenceType.CIRCULAR, nullable=False)
    coordinates: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Optional polygon vertices
    status: Mapped[LocationStatus] = mapped_column(Enum(LocationStatus, native_enum=False), default=LocationStatus.ACTIVE, nullable=False)
    
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    branch = relationship("Branch", foreign_keys=[branch_id])
    created_by = relationship("User", foreign_keys=[created_by_id])

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="idx_loc_tenant_code"),
        Index("idx_loc_tenant_status", "tenant_id", "status"),
    )


class AttendanceLocationAssignment(Base):
    __tablename__ = "attendance_location_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("attendance_locations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=True, index=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True, index=True)
    employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=True, index=True)
    
    priority: Mapped[int] = mapped_column(Integer, default=4, nullable=False) # 1=Emp, 2=Dept, 3=Branch, 4=Default
    status: Mapped[LocationStatus] = mapped_column(Enum(LocationStatus, native_enum=False), default=LocationStatus.ACTIVE, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    location = relationship("AttendanceLocation", foreign_keys=[location_id])
    branch = relationship("Branch", foreign_keys=[branch_id])
    department = relationship("Department", foreign_keys=[department_id])
    employee = relationship("Employee", foreign_keys=[employee_id])


class AttendanceLocationPolicy(Base):
    __tablename__ = "attendance_location_policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    location_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    geofence_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_radius: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    minimum_accuracy: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    location_freshness_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    allow_outside_geofence: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    outside_geofence_action: Mapped[OutsideGeofenceAction] = mapped_column(
        Enum(OutsideGeofenceAction, native_enum=False), default=OutsideGeofenceAction.REJECT, nullable=False
    )
    
    selfie_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_failure_action: Mapped[VerificationFailureAction] = mapped_column(
        Enum(VerificationFailureAction, native_enum=False), default=VerificationFailureAction.REJECT, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class AttendanceVerification(Base):
    __tablename__ = "attendance_verifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("attendance_events.id", ondelete="SET NULL"), nullable=True, index=True)
    
    provider: Mapped[str] = mapped_column(String(50), default="MOCK", nullable=False)
    status: Mapped[VerificationStatus] = mapped_column(Enum(VerificationStatus, native_enum=False), default=VerificationStatus.PENDING, nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), default="image/jpeg", nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    attendance_event = relationship("AttendanceEvent", foreign_keys=[attendance_event_id])
