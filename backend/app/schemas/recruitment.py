from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.models.recruitment import (
    RequisitionStatus,
    CandidateStatus,
    InterviewType,
    InterviewStatus,
    RecommendationType,
    OfferStatus
)

class RequisitionCreate(BaseModel):
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    hiring_manager_id: Optional[str] = None
    positions_count: int = 1
    employment_type: str = "FULL_TIME"
    location: Optional[str] = "Main Campus"
    min_experience: int = 0
    max_experience: int = 10
    required_skills: Optional[str] = None
    education: Optional[str] = "Bachelor's Degree"
    salary_min: Decimal = Decimal("0.00")
    salary_max: Decimal = Decimal("0.00")
    budget: Decimal = Decimal("0.00")
    priority: str = "MEDIUM"
    reason_for_hiring: Optional[str] = None
    target_joining_date: Optional[date] = None

class RequisitionResponse(RequisitionCreate):
    id: str
    tenant_id: str
    status: RequisitionStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class JobPostingCreate(BaseModel):
    requisition_id: Optional[str] = None
    title: str
    description: str
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    skills_list: Optional[str] = None
    location: Optional[str] = "Hybrid"
    location_type: str = "HYBRID"
    employment_type: str = "FULL_TIME"
    openings_count: int = 1

class JobPostingResponse(JobPostingCreate):
    id: str
    tenant_id: str
    is_published: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CandidateCreate(BaseModel):
    job_posting_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    current_company: Optional[str] = None
    current_designation: Optional[str] = None
    expected_salary: Decimal = Decimal("0.00")
    notice_period_days: int = 30
    source: str = "CAREER_PAGE"
    resume_url: Optional[str] = None
    skills_list: Optional[str] = None

class CandidateStageUpdate(BaseModel):
    new_status: CandidateStatus
    reason: Optional[str] = None

class CandidateResponse(CandidateCreate):
    id: str
    tenant_id: str
    overall_score: float
    status: CandidateStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InterviewCreate(BaseModel):
    candidate_id: str
    job_posting_id: Optional[str] = None
    interviewer_id: Optional[str] = None
    interview_type: InterviewType = InterviewType.TECHNICAL
    scheduled_at: datetime
    duration_minutes: int = 45
    meeting_url: Optional[str] = None

class InterviewFeedbackSubmit(BaseModel):
    interview_id: str
    technical_score: float = 4.0
    communication_score: float = 4.0
    culture_fit_score: float = 4.0
    problem_solving_score: float = 4.0
    overall_rating: float = 4.0
    recommendation: RecommendationType = RecommendationType.HIRE
    comments: Optional[str] = None

class InterviewResponse(InterviewCreate):
    id: str
    tenant_id: str
    status: InterviewStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OfferCreate(BaseModel):
    candidate_id: str
    job_posting_id: Optional[str] = None
    offer_number: str
    base_salary: Decimal
    variable_pay: Decimal = Decimal("0.00")
    joining_date: date

class OfferResponse(OfferCreate):
    id: str
    tenant_id: str
    status: OfferStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
