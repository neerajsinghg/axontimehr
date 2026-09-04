import enum
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Text,
    Integer,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class CourseMode(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    HYBRID = "HYBRID"
    SELF_PACED = "SELF_PACED"


class EnrollmentStatus(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    ENROLLED = "ENROLLED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"
    FAILED = "FAILED"


class CertificationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class Course(Base):
    __tablename__ = "learning_courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="TECHNICAL", nullable=False)
    provider = Column(String(150), default="INTERNAL", nullable=False)
    mode = Column(SQLEnum(CourseMode), default=CourseMode.ONLINE, nullable=False)
    duration_hours = Column(Integer, default=10, nullable=False)
    cost = Column(Integer, default=0, nullable=False)
    capacity = Column(Integer, default=50, nullable=False)
    course_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    enrollments = relationship("TrainingEnrollment", back_populates="course", cascade="all, delete-orphan")


class TrainingEnrollment(Base):
    __tablename__ = "training_enrollments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    course_id = Column(String(36), ForeignKey("learning_courses.id"), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    status = Column(SQLEnum(EnrollmentStatus), default=EnrollmentStatus.ASSIGNED, nullable=False)
    completion_percentage = Column(Integer, default=0, nullable=False)
    enrolled_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    certificate_url = Column(String(500), nullable=True)

    course = relationship("Course", back_populates="enrollments")


class EmployeeCertification(Base):
    __tablename__ = "employee_certifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    issuing_organization = Column(String(150), nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    credential_id = Column(String(100), nullable=True)
    credential_url = Column(String(500), nullable=True)
    status = Column(SQLEnum(CertificationStatus), default=CertificationStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    category = Column(String(100), default="TECHNICAL", nullable=False)
    current_level = Column(Integer, default=1, nullable=False)  # 1-5
    target_level = Column(Integer, default=5, nullable=False)   # 1-5
    skill_gap = Column(Integer, default=4, nullable=False)      # target - current
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
