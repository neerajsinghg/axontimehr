import uuid
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.recruitment import (
    JobRequisition, RequisitionStatus,
    JobPosting,
    Candidate, CandidateStatus, CandidateStatusHistory,
    Interview, InterviewStatus, InterviewFeedback,
    Offer, OfferStatus
)
from app.models.employee import Employee
from app.schemas.recruitment import (
    RequisitionCreate, JobPostingCreate, CandidateCreate,
    CandidateStageUpdate, InterviewCreate, InterviewFeedbackSubmit, OfferCreate
)

class RecruitmentService:
    @staticmethod
    async def create_requisition(db: AsyncSession, tenant_id: uuid.UUID, data: RequisitionCreate, user_id: Optional[str] = None) -> JobRequisition:
        req = JobRequisition(
            tenant_id=str(tenant_id),
            department_id=data.department_id,
            designation_id=data.designation_id,
            hiring_manager_id=data.hiring_manager_id,
            positions_count=data.positions_count,
            employment_type=data.employment_type,
            location=data.location,
            min_experience=data.min_experience,
            max_experience=data.max_experience,
            required_skills=data.required_skills,
            education=data.education,
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            budget=data.budget,
            priority=data.priority,
            reason_for_hiring=data.reason_for_hiring,
            target_joining_date=data.target_joining_date,
            status=RequisitionStatus.APPROVED,  # Auto-approve for demo
            created_by=str(user_id) if user_id else None
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def get_requisitions(db: AsyncSession, tenant_id: uuid.UUID) -> List[JobRequisition]:
        res = await db.execute(
            select(JobRequisition).where(JobRequisition.tenant_id == str(tenant_id)).order_by(JobRequisition.created_at.desc())
        )
        requisitions = list(res.scalars().all())
        if not requisitions:
            # Seed default job requisition
            seed = JobRequisition(
                tenant_id=str(tenant_id),
                positions_count=3,
                employment_type="FULL_TIME",
                location="Bengaluru HQ",
                min_experience=3,
                max_experience=7,
                required_skills="Python, FastAPI, React, PostgreSQL",
                education="B.Tech / MCA",
                salary_min=1200000,
                salary_max=1800000,
                budget=5400000,
                priority="HIGH",
                reason_for_hiring="Q3 Expansion of Core Platform Engineering Team",
                status=RequisitionStatus.APPROVED
            )
            db.add(seed)
            await db.commit()
            await db.refresh(seed)
            requisitions = [seed]
        return requisitions

    @staticmethod
    async def create_job_posting(db: AsyncSession, tenant_id: uuid.UUID, data: JobPostingCreate) -> JobPosting:
        slug = f"{data.title.lower().replace(' ', '-')}-{uuid.uuid4().hex[:6]}"
        job = JobPosting(
            tenant_id=str(tenant_id),
            requisition_id=data.requisition_id,
            title=data.title,
            description=data.description,
            responsibilities=data.responsibilities,
            requirements=data.requirements,
            skills_list=data.skills_list,
            location=data.location,
            location_type=data.location_type,
            employment_type=data.employment_type,
            openings_count=data.openings_count,
            is_published=True,
            slug=slug
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_job_postings(db: AsyncSession, tenant_id: uuid.UUID) -> List[JobPosting]:
        res = await db.execute(
            select(JobPosting).where(JobPosting.tenant_id == str(tenant_id)).order_by(JobPosting.created_at.desc())
        )
        jobs = list(res.scalars().all())
        if not jobs:
            # Seed default job postings
            defaults = [
                JobPosting(
                    tenant_id=str(tenant_id),
                    title="Senior Full-Stack Engineer (Python & React)",
                    description="Lead complex SaaS feature builds across FastAPI microservices and React frontends.",
                    requirements="5+ years Python/React experience, PostgreSQL optimization, RESTful API design",
                    location="Bengaluru / Remote",
                    location_type="HYBRID",
                    openings_count=2,
                    is_published=True,
                    slug="senior-fullstack-engineer"
                ),
                JobPosting(
                    tenant_id=str(tenant_id),
                    title="HR Operations & Recruitment Specialist",
                    description="Manage end-to-end talent acquisition, interview scheduling, and employee onboarding.",
                    requirements="3+ years HR experience in tech SaaS, strong communication, ATS proficiency",
                    location="Mumbai Office",
                    location_type="ON_SITE",
                    openings_count=1,
                    is_published=True,
                    slug="hr-operations-specialist"
                )
            ]
            for j in defaults:
                db.add(j)
            await db.commit()
            jobs = defaults
        return jobs

    @staticmethod
    async def create_candidate(db: AsyncSession, tenant_id: uuid.UUID, data: CandidateCreate) -> Candidate:
        candidate = Candidate(
            tenant_id=str(tenant_id),
            job_posting_id=data.job_posting_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            location=data.location,
            current_company=data.current_company,
            current_designation=data.current_designation,
            expected_salary=data.expected_salary,
            notice_period_days=data.notice_period_days,
            source=data.source,
            resume_url=data.resume_url,
            skills_list=data.skills_list,
            overall_score=85.0,
            status=CandidateStatus.APPLIED
        )
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)
        return candidate

    @staticmethod
    async def get_candidates(db: AsyncSession, tenant_id: uuid.UUID) -> List[Candidate]:
        res = await db.execute(
            select(Candidate).where(Candidate.tenant_id == str(tenant_id)).order_by(Candidate.created_at.desc())
        )
        candidates = list(res.scalars().all())
        if not candidates:
            # Seed default candidates
            defaults = [
                Candidate(
                    tenant_id=str(tenant_id),
                    first_name="Aarav",
                    last_name="Sharma",
                    email="aarav.sharma@example.com",
                    phone="+91 9876543210",
                    current_company="TechCorp Solutions",
                    current_designation="Senior Software Engineer",
                    expected_salary=1600000,
                    notice_period_days=30,
                    source="LINKEDIN",
                    skills_list="Python, FastAPI, PostgreSQL, Docker",
                    overall_score=92.0,
                    status=CandidateStatus.INTERVIEW
                ),
                Candidate(
                    tenant_id=str(tenant_id),
                    first_name="Priya",
                    last_name="Verma",
                    email="priya.verma@example.com",
                    phone="+91 9812345678",
                    current_company="Innovate HR",
                    current_designation="HR Executive",
                    expected_salary=900000,
                    notice_period_days=15,
                    source="CAREER_PAGE",
                    skills_list="Talent Acquisition, Screening, Interviewing",
                    overall_score=88.0,
                    status=CandidateStatus.SCREENING
                )
            ]
            for c in defaults:
                db.add(c)
            await db.commit()
            candidates = defaults
        return candidates

    @staticmethod
    async def update_candidate_stage(db: AsyncSession, tenant_id: uuid.UUID, candidate_id: str, data: CandidateStageUpdate, user_id: Optional[str] = None) -> Candidate:
        res = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id, Candidate.tenant_id == str(tenant_id))
        )
        candidate = res.scalar_one_or_none()
        if not candidate:
            raise ValueError("Candidate not found")
        
        prev_status = candidate.status.value if candidate.status else "UNKNOWN"
        candidate.status = data.new_status

        history = CandidateStatusHistory(
            tenant_id=str(tenant_id),
            candidate_id=candidate.id,
            previous_status=prev_status,
            new_status=data.new_status.value,
            changed_by_id=str(user_id) if user_id else None,
            reason=data.reason or "Stage updated via Recruitment Pipeline"
        )
        db.add(history)
        await db.commit()
        await db.refresh(candidate)
        return candidate

    @staticmethod
    async def schedule_interview(db: AsyncSession, tenant_id: uuid.UUID, data: InterviewCreate) -> Interview:
        interview = Interview(
            tenant_id=str(tenant_id),
            candidate_id=data.candidate_id,
            job_posting_id=data.job_posting_id,
            interviewer_id=data.interviewer_id,
            interview_type=data.interview_type,
            scheduled_at=data.scheduled_at,
            duration_minutes=data.duration_minutes,
            meeting_url=data.meeting_url or "https://meet.google.com/axon-interview",
            status=InterviewStatus.SCHEDULED
        )
        db.add(interview)
        await db.commit()
        await db.refresh(interview)
        return interview

    @staticmethod
    async def get_interviews(db: AsyncSession, tenant_id: uuid.UUID) -> List[Interview]:
        res = await db.execute(
            select(Interview).where(Interview.tenant_id == str(tenant_id)).order_by(Interview.scheduled_at.desc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def submit_interview_feedback(db: AsyncSession, tenant_id: uuid.UUID, data: InterviewFeedbackSubmit, user_id: str) -> InterviewFeedback:
        fb = InterviewFeedback(
            tenant_id=str(tenant_id),
            interview_id=data.interview_id,
            interviewer_id=str(user_id) if user_id else None,
            technical_score=data.technical_score,
            communication_score=data.communication_score,
            culture_fit_score=data.culture_fit_score,
            problem_solving_score=data.problem_solving_score,
            overall_rating=data.overall_rating,
            recommendation=data.recommendation,
            comments=data.comments
        )
        db.add(fb)
        # Update interview status to COMPLETED
        await db.execute(
            update(Interview).where(Interview.id == data.interview_id).values(status=InterviewStatus.COMPLETED)
        )
        await db.commit()
        await db.refresh(fb)
        return fb

    @staticmethod
    async def create_offer(db: AsyncSession, tenant_id: uuid.UUID, data: OfferCreate) -> Offer:
        offer = Offer(
            tenant_id=str(tenant_id),
            candidate_id=data.candidate_id,
            job_posting_id=data.job_posting_id,
            offer_number=data.offer_number,
            base_salary=data.base_salary,
            variable_pay=data.variable_pay,
            joining_date=data.joining_date,
            status=OfferStatus.SENT,
            issued_at=datetime.now()
        )
        db.add(offer)
        await db.commit()
        await db.refresh(offer)
        return offer

    @staticmethod
    async def get_offers(db: AsyncSession, tenant_id: uuid.UUID) -> List[Offer]:
        res = await db.execute(
            select(Offer).where(Offer.tenant_id == str(tenant_id)).order_by(Offer.created_at.desc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def convert_candidate_to_employee(db: AsyncSession, tenant_id: uuid.UUID, offer_id: str) -> Employee:
        res = await db.execute(
            select(Offer).where(Offer.id == offer_id, Offer.tenant_id == str(tenant_id))
        )
        offer = res.scalar_one_or_none()
        if not offer:
            raise ValueError("Offer not found")

        cand_res = await db.execute(
            select(Candidate).where(Candidate.id == offer.candidate_id)
        )
        candidate = cand_res.scalar_one_or_none()
        if not candidate:
            raise ValueError("Candidate associated with offer not found")

        # Mark offer ACCEPTED & candidate HIRED
        offer.status = OfferStatus.ACCEPTED
        offer.accepted_at = datetime.now()
        candidate.status = CandidateStatus.HIRED

        # Generate Employee Code
        emp_code = f"EMP-{uuid.uuid4().hex[:6].upper()}"

        joining = getattr(offer, "joining_date", None)
        if isinstance(joining, str):
            joining_date_val = datetime.strptime(joining, "%Y-%m-%d").date()
        elif isinstance(joining, (datetime, date)):
            joining_date_val = joining
        else:
            joining_date_val = date.today()

        emp = Employee(
            organization_id=tenant_id,
            employee_id=emp_code,
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            email=candidate.email,
            phone=candidate.phone,
            joining_date=joining_date_val,
            status="ACTIVE"
        )
        db.add(emp)
        await db.commit()
        await db.refresh(emp)
        return emp
