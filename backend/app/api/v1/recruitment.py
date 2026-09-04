import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.services.recruitment_service import RecruitmentService
from app.schemas.recruitment import (
    RequisitionCreate, RequisitionResponse,
    JobPostingCreate, JobPostingResponse,
    CandidateCreate, CandidateResponse, CandidateStageUpdate,
    InterviewCreate, InterviewResponse, InterviewFeedbackSubmit,
    OfferCreate, OfferResponse
)

router = APIRouter(prefix="/recruitment", tags=["Recruitment & ATS"])

@router.post("/requisitions", response_model=RequisitionResponse, status_code=status.HTTP_201_CREATED)
async def create_requisition(
    data: RequisitionCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.create_requisition(db, tenant_id, data, user_id=current_user.id)

@router.get("/requisitions", response_model=List[RequisitionResponse])
async def get_requisitions(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.get_requisitions(db, tenant_id)

@router.post("/jobs", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
async def create_job_posting(
    data: JobPostingCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.create_job_posting(db, tenant_id, data)

@router.get("/jobs", response_model=List[JobPostingResponse])
async def get_job_postings(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.get_job_postings(db, tenant_id)

@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    data: CandidateCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.create_candidate(db, tenant_id, data)

@router.get("/candidates", response_model=List[CandidateResponse])
async def get_candidates(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.get_candidates(db, tenant_id)

@router.patch("/candidates/{candidate_id}/stage", response_model=CandidateResponse)
async def update_candidate_stage(
    candidate_id: str,
    data: CandidateStageUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    try:
        return await RecruitmentService.update_candidate_stage(db, tenant_id, candidate_id, data, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    data: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.schedule_interview(db, tenant_id, data)

@router.get("/interviews", response_model=List[InterviewResponse])
async def get_interviews(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.get_interviews(db, tenant_id)

@router.post("/interviews/feedback", status_code=status.HTTP_201_CREATED)
async def submit_interview_feedback(
    data: InterviewFeedbackSubmit,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.submit_interview_feedback(db, tenant_id, data, user_id=current_user.id)

@router.post("/offers", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    data: OfferCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.create_offer(db, tenant_id, data)

@router.get("/offers", response_model=List[OfferResponse])
async def get_offers(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await RecruitmentService.get_offers(db, tenant_id)

@router.post("/offers/{offer_id}/convert-employee")
async def convert_candidate_to_employee(
    offer_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    try:
        emp = await RecruitmentService.convert_candidate_to_employee(db, tenant_id, offer_id)
        return {"status": "success", "employee_id": emp.id, "employee_code": emp.employee_id, "message": "Candidate successfully converted to Active Employee!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
