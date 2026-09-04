import uuid
import enum
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Enum, Text, Numeric
from sqlalchemy.orm import relationship
from app.models import Base

class RequisitionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    OPEN = "OPEN"
    ON_HOLD = "ON_HOLD"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

class CandidateStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW = "INTERVIEW"
    TECHNICAL_INTERVIEW = "TECHNICAL_INTERVIEW"
    MANAGER_INTERVIEW = "MANAGER_INTERVIEW"
    HR_INTERVIEW = "HR_INTERVIEW"
    OFFER = "OFFER"
    HIRED = "HIRED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class InterviewType(str, enum.Enum):
    PHONE = "PHONE"
    VIDEO = "VIDEO"
    TECHNICAL = "TECHNICAL"
    MANAGERIAL = "MANAGERIAL"
    HR = "HR"
    PANEL = "PANEL"
    FINAL = "FINAL"

class InterviewStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"

class RecommendationType(str, enum.Enum):
    STRONG_HIRE = "STRONG_HIRE"
    HIRE = "HIRE"
    HOLD = "HOLD"
    NO_HIRE = "NO_HIRE"
    STRONG_NO_HIRE = "STRONG_NO_HIRE"

class OfferStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SENT = "SENT"
    VIEWED = "VIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    WITHDRAWN = "WITHDRAWN"

class JobRequisition(Base):
    __tablename__ = "recruitment_job_requisitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    department_id = Column(String(36), nullable=True)
    designation_id = Column(String(36), nullable=True)
    hiring_manager_id = Column(String(36), nullable=True)
    positions_count = Column(Integer, default=1, nullable=False)
    employment_type = Column(String(50), default="FULL_TIME", nullable=False)
    location = Column(String(200), nullable=True)
    min_experience = Column(Integer, default=0, nullable=False)
    max_experience = Column(Integer, default=10, nullable=False)
    required_skills = Column(Text, nullable=True)
    education = Column(String(200), nullable=True)
    salary_min = Column(Numeric(12, 2), default=0.00, nullable=False)
    salary_max = Column(Numeric(12, 2), default=0.00, nullable=False)
    budget = Column(Numeric(12, 2), default=0.00, nullable=False)
    priority = Column(String(50), default="MEDIUM", nullable=False)
    reason_for_hiring = Column(Text, nullable=True)
    target_joining_date = Column(Date, nullable=True)
    status = Column(Enum(RequisitionStatus), default=RequisitionStatus.DRAFT, nullable=False, index=True)
    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), onupdate=lambda: datetime.now(), nullable=False)

class JobPosting(Base):
    __tablename__ = "recruitment_job_postings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    requisition_id = Column(String(36), ForeignKey("recruitment_job_requisitions.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    responsibilities = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    skills_list = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    location_type = Column(String(50), default="HYBRID", nullable=False)
    employment_type = Column(String(50), default="FULL_TIME", nullable=False)
    application_deadline = Column(Date, nullable=True)
    openings_count = Column(Integer, default=1, nullable=False)
    is_published = Column(Boolean, default=True, nullable=False, index=True)
    slug = Column(String(255), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class Candidate(Base):
    __tablename__ = "recruitment_candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    job_posting_id = Column(String(36), ForeignKey("recruitment_job_postings.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    current_company = Column(String(200), nullable=True)
    current_designation = Column(String(200), nullable=True)
    expected_salary = Column(Numeric(12, 2), default=0.00, nullable=False)
    notice_period_days = Column(Integer, default=30, nullable=False)
    source = Column(String(100), default="CAREER_PAGE", nullable=False)
    referral_by_id = Column(String(36), nullable=True)
    resume_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    skills_list = Column(Text, nullable=True)
    overall_score = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(CandidateStatus), default=CandidateStatus.APPLIED, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), onupdate=lambda: datetime.now(), nullable=False)

class CandidateStatusHistory(Base):
    __tablename__ = "recruitment_candidate_status_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    candidate_id = Column(String(36), ForeignKey("recruitment_candidates.id"), nullable=False, index=True)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by_id = Column(String(36), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class CandidateDocument(Base):
    __tablename__ = "recruitment_candidate_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    candidate_id = Column(String(36), ForeignKey("recruitment_candidates.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), default="PDF", nullable=False)
    file_size = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class Interview(Base):
    __tablename__ = "recruitment_interviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    candidate_id = Column(String(36), ForeignKey("recruitment_candidates.id"), nullable=False, index=True)
    job_posting_id = Column(String(36), nullable=True)
    interviewer_id = Column(String(36), nullable=True)
    interview_type = Column(Enum(InterviewType), default=InterviewType.TECHNICAL, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=45, nullable=False)
    meeting_url = Column(String(500), nullable=True)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.SCHEDULED, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class InterviewFeedback(Base):
    __tablename__ = "recruitment_interview_feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    interview_id = Column(String(36), ForeignKey("recruitment_interviews.id"), nullable=False, index=True)
    interviewer_id = Column(String(36), nullable=False)
    technical_score = Column(Float, default=0.0, nullable=False)
    communication_score = Column(Float, default=0.0, nullable=False)
    culture_fit_score = Column(Float, default=0.0, nullable=False)
    problem_solving_score = Column(Float, default=0.0, nullable=False)
    overall_rating = Column(Float, default=0.0, nullable=False)
    recommendation = Column(Enum(RecommendationType), default=RecommendationType.HIRE, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class Offer(Base):
    __tablename__ = "recruitment_offers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    candidate_id = Column(String(36), ForeignKey("recruitment_candidates.id"), nullable=False, index=True)
    job_posting_id = Column(String(36), nullable=True)
    offer_number = Column(String(100), nullable=False, unique=True)
    base_salary = Column(Numeric(12, 2), default=0.00, nullable=False)
    variable_pay = Column(Numeric(12, 2), default=0.00, nullable=False)
    joining_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    status = Column(Enum(OfferStatus), default=OfferStatus.DRAFT, nullable=False, index=True)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class TalentPool(Base):
    __tablename__ = "recruitment_talent_pools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class TalentPoolMember(Base):
    __tablename__ = "recruitment_talent_pool_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    talent_pool_id = Column(String(36), ForeignKey("recruitment_talent_pools.id"), nullable=False, index=True)
    candidate_id = Column(String(36), ForeignKey("recruitment_candidates.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
