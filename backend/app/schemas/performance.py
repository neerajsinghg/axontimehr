from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.performance import CycleType, CycleStatus, GoalType, GoalStatus, ReviewStatus, PIPStatus
from app.models.learning import CourseMode, EnrollmentStatus, CertificationStatus
from app.models.engagement import SurveyType, QuestionType


# --- Performance Cycle Schemas ---
class PerformanceCycleBase(BaseModel):
    name: str
    description: Optional[str] = None
    cycle_type: CycleType = CycleType.ANNUAL
    start_date: date
    end_date: date
    self_review_end: Optional[date] = None
    manager_review_end: Optional[date] = None
    peer_review_end: Optional[date] = None
    calibration_end: Optional[date] = None


class PerformanceCycleCreate(PerformanceCycleBase):
    pass


class PerformanceCycleResponse(PerformanceCycleBase):
    id: str
    tenant_id: str
    status: CycleStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Goal Schemas ---
class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    goal_type: GoalType = GoalType.INDIVIDUAL
    baseline_value: Decimal = Decimal("0.00")
    target_value: Decimal = Decimal("100.00")
    current_value: Decimal = Decimal("0.00")
    unit: str = "PERCENT"
    weightage: Decimal = Decimal("20.00")
    due_date: Optional[date] = None


class GoalCreate(GoalBase):
    cycle_id: str
    employee_id: str
    parent_goal_id: Optional[str] = None


class GoalProgressUpdate(BaseModel):
    current_value: Decimal
    comments: Optional[str] = None


class GoalResponse(GoalBase):
    id: str
    tenant_id: str
    cycle_id: str
    employee_id: str
    status: GoalStatus
    progress_pct: Decimal
    achievement_pct: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Performance Review Schemas ---
class SelfAssessmentSubmit(BaseModel):
    self_score: Decimal
    employee_comments: Optional[str] = None


class ManagerAssessmentSubmit(BaseModel):
    manager_score: Decimal
    manager_comments: Optional[str] = None


class PeerReviewSubmit(BaseModel):
    score: Decimal
    feedback_text: Optional[str] = None
    is_anonymous: bool = True


class CalibrationSubmit(BaseModel):
    review_id: str
    calibrated_score: Decimal
    reason: str


class PerformanceReviewResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_id: str
    employee_id: str
    manager_id: Optional[str] = None
    self_score: Optional[Decimal] = None
    manager_score: Optional[Decimal] = None
    peer_score: Optional[Decimal] = None
    calculated_score: Optional[Decimal] = None
    calibrated_score: Optional[Decimal] = None
    final_score: Optional[Decimal] = None
    status: ReviewStatus
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    employee_comments: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Learning & Development Schemas ---
class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "TECHNICAL"
    provider: str = "INTERNAL"
    mode: CourseMode = CourseMode.ONLINE
    duration_hours: int = 10
    cost: Decimal = Decimal("0.00")
    capacity: int = 50
    course_url: Optional[str] = None


class CourseResponse(CourseCreate):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TrainingEnrollmentCreate(BaseModel):
    course_id: str
    employee_id: str


class TrainingEnrollmentResponse(BaseModel):
    id: str
    tenant_id: str
    course_id: str
    employee_id: str
    status: EnrollmentStatus
    enrollment_date: date
    completion_date: Optional[date] = None
    score_pct: Optional[Decimal] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CertificationCreate(BaseModel):
    employee_id: str
    name: str
    issuing_organization: str
    issue_date: date
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None


class CertificationResponse(CertificationCreate):
    id: str
    tenant_id: str
    status: CertificationStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SkillUpdate(BaseModel):
    employee_id: str
    skill_name: str
    category: str = "TECHNICAL"
    current_level: int
    target_level: int


class SkillResponse(SkillUpdate):
    id: str
    tenant_id: str
    skill_gap: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Engagement & Survey Schemas ---
class SurveyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    survey_type: SurveyType = SurveyType.PULSE
    start_date: date
    end_date: date
    is_anonymous: bool = True


class SurveyResponse(SurveyCreate):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SurveySubmitAnswer(BaseModel):
    question_id: str
    answer_rating: Optional[int] = None
    answer_text: Optional[str] = None


class EmployeeFeedbackCreate(BaseModel):
    category: str = "WORKPLACE"
    subject: str
    message: str
    is_anonymous: bool = True
