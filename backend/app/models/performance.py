import enum
import uuid
from datetime import datetime, timezone, date
from decimal import Decimal
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Numeric,
    Enum as SQLEnum,
    Text,
    Integer,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class CycleType(str, enum.Enum):
    ANNUAL = "ANNUAL"
    HALF_YEARLY = "HALF_YEARLY"
    QUARTERLY = "QUARTERLY"
    MONTHLY = "MONTHLY"
    PROBATION = "PROBATION"
    CUSTOM = "CUSTOM"


class CycleStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    GOAL_SETTING = "GOAL_SETTING"
    IN_PROGRESS = "IN_PROGRESS"
    SELF_REVIEW = "SELF_REVIEW"
    MANAGER_REVIEW = "MANAGER_REVIEW"
    PEER_REVIEW = "PEER_REVIEW"
    CALIBRATION = "CALIBRATION"
    FINAL_REVIEW = "FINAL_REVIEW"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class GoalType(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    TEAM = "TEAM"
    DEPARTMENT = "DEPARTMENT"
    ORGANIZATION = "ORGANIZATION"
    PROJECT = "PROJECT"
    KPI = "KPI"
    KRA = "KRA"
    OKR = "OKR"
    DEVELOPMENT = "DEVELOPMENT"
    BEHAVIORAL = "BEHAVIORAL"


class GoalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ReviewStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    SELF_ASSESSMENT_PENDING = "SELF_ASSESSMENT_PENDING"
    MANAGER_REVIEW_PENDING = "MANAGER_REVIEW_PENDING"
    PEER_REVIEW_PENDING = "PEER_REVIEW_PENDING"
    CALIBRATION_PENDING = "CALIBRATION_PENDING"
    FINAL_REVIEW_PENDING = "FINAL_REVIEW_PENDING"
    FINALIZED = "FINALIZED"


class PIPStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    UNDER_REVIEW = "UNDER_REVIEW"
    SUCCESSFUL = "SUCCESSFUL"
    EXTENDED = "EXTENDED"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    CANCELLED = "CANCELLED"


class PerformanceCycle(Base):
    __tablename__ = "performance_cycles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    cycle_type = Column(SQLEnum(CycleType), default=CycleType.ANNUAL, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    goal_start_date = Column(Date, nullable=True)
    goal_end_date = Column(Date, nullable=True)
    self_review_start = Column(Date, nullable=True)
    self_review_end = Column(Date, nullable=True)
    manager_review_start = Column(Date, nullable=True)
    manager_review_end = Column(Date, nullable=True)
    peer_review_start = Column(Date, nullable=True)
    peer_review_end = Column(Date, nullable=True)
    calibration_start = Column(Date, nullable=True)
    calibration_end = Column(Date, nullable=True)
    status = Column(SQLEnum(CycleStatus), default=CycleStatus.DRAFT, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    configs = relationship("PerformanceCycleConfig", back_populates="cycle", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="cycle", cascade="all, delete-orphan")
    reviews = relationship("PerformanceReview", back_populates="cycle", cascade="all, delete-orphan")


class PerformanceCycleConfig(Base):
    __tablename__ = "performance_cycle_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    cycle_id = Column(String(36), ForeignKey("performance_cycles.id"), nullable=False, index=True)
    goal_weightage = Column(Numeric(5, 2), default=Decimal("60.00"), nullable=False)
    competency_weightage = Column(Numeric(5, 2), default=Decimal("20.00"), nullable=False)
    manager_weightage = Column(Numeric(5, 2), default=Decimal("20.00"), nullable=False)
    self_weightage = Column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    peer_weightage = Column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    min_goals = Column(Integer, default=3, nullable=False)
    max_goals = Column(Integer, default=10, nullable=False)
    is_360_anonymous = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    cycle = relationship("PerformanceCycle", back_populates="configs")


class RatingScale(Base):
    __tablename__ = "rating_scales"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    min_score = Column(Numeric(4, 2), default=Decimal("1.00"), nullable=False)
    max_score = Column(Numeric(4, 2), default=Decimal("5.00"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    values = relationship("RatingScaleValue", back_populates="rating_scale", cascade="all, delete-orphan")


class RatingScaleValue(Base):
    __tablename__ = "rating_scale_values"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rating_scale_id = Column(String(36), ForeignKey("rating_scales.id"), nullable=False, index=True)
    score = Column(Numeric(4, 2), nullable=False)
    label = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color_code = Column(String(20), default="#10B981", nullable=False)

    rating_scale = relationship("RatingScale", back_populates="values")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    cycle_id = Column(String(36), ForeignKey("performance_cycles.id"), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    manager_id = Column(String(36), nullable=True, index=True)
    parent_goal_id = Column(String(36), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(SQLEnum(GoalType), default=GoalType.INDIVIDUAL, nullable=False)
    baseline_value = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    current_value = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    target_value = Column(Numeric(12, 2), default=Decimal("100.00"), nullable=False)
    unit = Column(String(50), default="PERCENT", nullable=False)
    weightage = Column(Numeric(5, 2), default=Decimal("20.00"), nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(SQLEnum(GoalStatus), default=GoalStatus.IN_PROGRESS, nullable=False)
    progress_pct = Column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    achievement_pct = Column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    cycle = relationship("PerformanceCycle", back_populates="goals")
    milestones = relationship("GoalMilestone", back_populates="goal", cascade="all, delete-orphan")
    history = relationship("GoalProgressHistory", back_populates="goal", cascade="all, delete-orphan")


class GoalMilestone(Base):
    __tablename__ = "goal_milestones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String(36), ForeignKey("goals.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(50), default="PENDING", nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    goal = relationship("Goal", back_populates="milestones")


class GoalProgressHistory(Base):
    __tablename__ = "goal_progress_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String(36), ForeignKey("goals.id"), nullable=False, index=True)
    previous_value = Column(Numeric(12, 2), nullable=False)
    new_value = Column(Numeric(12, 2), nullable=False)
    progress_pct = Column(Numeric(5, 2), nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    goal = relationship("Goal", back_populates="history")


class Competency(Base):
    __tablename__ = "competencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False)
    category = Column(String(100), default="CORE", nullable=False)
    description = Column(Text, nullable=True)
    expected_level = Column(Integer, default=3, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    cycle_id = Column(String(36), ForeignKey("performance_cycles.id"), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    manager_id = Column(String(36), nullable=True, index=True)
    self_score = Column(Numeric(4, 2), nullable=True)
    manager_score = Column(Numeric(4, 2), nullable=True)
    peer_score = Column(Numeric(4, 2), nullable=True)
    calculated_score = Column(Numeric(4, 2), nullable=True)
    calibrated_score = Column(Numeric(4, 2), nullable=True)
    final_score = Column(Numeric(4, 2), nullable=True)
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.NOT_STARTED, nullable=False)
    self_submitted_at = Column(DateTime(timezone=True), nullable=True)
    manager_submitted_at = Column(DateTime(timezone=True), nullable=True)
    calibrated_at = Column(DateTime(timezone=True), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    employee_comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    cycle = relationship("PerformanceCycle", back_populates="reviews")
    peer_reviews = relationship("PeerReview360", back_populates="review", cascade="all, delete-orphan")


class PeerReview360(Base):
    __tablename__ = "peer_reviews_360"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    review_id = Column(String(36), ForeignKey("performance_reviews.id"), nullable=False, index=True)
    reviewer_id = Column(String(36), nullable=False, index=True)
    score = Column(Numeric(4, 2), nullable=True)
    feedback_text = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    review = relationship("PerformanceReview", back_populates="peer_reviews")


class PerformanceCalibration(Base):
    __tablename__ = "performance_calibrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    review_id = Column(String(36), ForeignKey("performance_reviews.id"), nullable=False, index=True)
    original_score = Column(Numeric(4, 2), nullable=False)
    calibrated_score = Column(Numeric(4, 2), nullable=False)
    reason = Column(Text, nullable=False)
    calibrated_by_id = Column(String(36), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class PerformanceImprovementPlan(Base):
    __tablename__ = "performance_improvement_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    manager_id = Column(String(36), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    action_items = Column(Text, nullable=False)
    status = Column(SQLEnum(PIPStatus), default=PIPStatus.ACTIVE, nullable=False)
    outcome = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class PromotionRecommendation(Base):
    __tablename__ = "promotion_recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    review_id = Column(String(36), ForeignKey("performance_reviews.id"), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    current_designation = Column(String(100), nullable=False)
    proposed_designation = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="SUBMITTED", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
