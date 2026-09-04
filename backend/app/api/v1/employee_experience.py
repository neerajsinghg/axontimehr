import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.schemas.employee_experience import (
    EmployeeDashboardSummary, ProfileUpdateRequest, ProfileChangeRequestCreate, ProfileChangeRequestResponse,
    HRDocumentTemplateCreate, HRDocumentTemplateResponse, GenerateLetterRequest, GeneratedHRLetterResponse,
    HRPolicyCreate, HRPolicyResponse, HRRequestCreate, HRRequestResponse,
    HRHelpdeskTicketCreate, HRHelpdeskTicketResponse, HRHelpdeskCommentSubmit, HRHelpdeskCommentResponse,
    CompanyAnnouncementCreate, CompanyAnnouncementResponse, EmployeeRecognitionCreate, EmployeeRecognitionResponse,
    UnifiedTaskItem
)
from app.services.employee_experience_service import EmployeeExperienceService

router = APIRouter(prefix="/employee-experience", tags=["Employee Experience (Phase 11)"])

@router.get("/me/dashboard", response_model=EmployeeDashboardSummary)
async def get_my_dashboard(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    user_id = uuid.UUID(str(current_user.id))
    return await EmployeeExperienceService.get_employee_dashboard_summary(db, tenant_id, user_id)

@router.put("/me/profile")
async def update_my_profile(
    data: ProfileUpdateRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    user_id = uuid.UUID(str(current_user.id))
    emp = await EmployeeExperienceService.update_self_profile(db, tenant_id, user_id, data)
    return {"status": "success", "message": "Self profile updated successfully", "employee_id": str(emp.id)}

@router.post("/me/profile/change-requests", response_model=ProfileChangeRequestResponse)
async def create_profile_change_request(
    data: ProfileChangeRequestCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    user_id = uuid.UUID(str(current_user.id))
    return await EmployeeExperienceService.create_profile_change_request(db, tenant_id, user_id, data)

@router.get("/me/profile/change-requests", response_model=List[ProfileChangeRequestResponse])
async def list_profile_change_requests(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.get_profile_change_requests(db, tenant_id)

# --- Documents & Letters ---
@router.post("/me/document-templates", response_model=HRDocumentTemplateResponse)
async def create_document_template(
    data: HRDocumentTemplateCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.create_document_template(db, tenant_id, data)

@router.get("/me/document-templates", response_model=List[HRDocumentTemplateResponse])
async def list_document_templates(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.get_document_templates(db, tenant_id)

@router.post("/me/documents/letters/generate", response_model=GeneratedHRLetterResponse)
async def generate_hr_letter(
    data: GenerateLetterRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    user_id = uuid.UUID(str(current_user.id))
    return await EmployeeExperienceService.generate_hr_letter(db, tenant_id, data, user_id)

@router.get("/me/documents/letters", response_model=List[GeneratedHRLetterResponse])
async def list_my_letters(
    employee_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    emp_id = employee_id or str(current_user.id)
    return await EmployeeExperienceService.get_employee_letters(db, tenant_id, emp_id)

# --- Policies ---
@router.post("/me/policies", response_model=HRPolicyResponse)
async def create_hr_policy(
    data: HRPolicyCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.create_hr_policy(db, tenant_id, data)

@router.get("/me/policies", response_model=List[HRPolicyResponse])
async def list_hr_policies(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.get_hr_policies(db, tenant_id)

@router.post("/me/policies/{policy_id}/acknowledge")
async def acknowledge_policy(
    policy_id: str,
    req: Request,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp_id = str(current_user.id)
    client_ip = req.client.host if req.client else "127.0.0.1"
    ack = await EmployeeExperienceService.acknowledge_hr_policy(db, policy_id, emp_id, client_ip)
    return {"status": "success", "message": "Policy acknowledged successfully", "acknowledged_at": ack.acknowledged_at}

# --- HR Requests & Helpdesk ---
@router.post("/me/requests", response_model=HRRequestResponse)
async def create_hr_request(
    data: HRRequestCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    user_id = uuid.UUID(str(current_user.id))
    return await EmployeeExperienceService.create_hr_request(db, tenant_id, user_id, data)

@router.get("/me/requests", response_model=List[HRRequestResponse])
async def list_hr_requests(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.get_hr_requests(db, tenant_id)

@router.post("/me/helpdesk/tickets", response_model=HRHelpdeskTicketResponse)
async def create_helpdesk_ticket(
    data: HRHelpdeskTicketCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    user_id = uuid.UUID(str(current_user.id))
    return await EmployeeExperienceService.create_helpdesk_ticket(db, tenant_id, user_id, data)

@router.get("/me/helpdesk/tickets", response_model=List[HRHelpdeskTicketResponse])
async def list_helpdesk_tickets(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.get_helpdesk_tickets(db, tenant_id)

@router.post("/me/helpdesk/tickets/{ticket_id}/comments", response_model=HRHelpdeskCommentResponse)
async def add_helpdesk_comment(
    ticket_id: str,
    data: HRHelpdeskCommentSubmit,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    sender_id = str(current_user.id)
    return await EmployeeExperienceService.add_helpdesk_comment(db, ticket_id, sender_id, data)

# --- Announcements & Recognition ---
@router.post("/me/announcements", response_model=CompanyAnnouncementResponse)
async def create_announcement(
    data: CompanyAnnouncementCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    user_id = uuid.UUID(str(current_user.id))
    return await EmployeeExperienceService.create_announcement(db, tenant_id, user_id, data)

@router.get("/me/announcements", response_model=List[CompanyAnnouncementResponse])
async def list_announcements(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.get_announcements(db, tenant_id)

@router.post("/me/recognitions", response_model=EmployeeRecognitionResponse)
async def create_recognition(
    data: EmployeeRecognitionCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    sender_id = str(current_user.id)
    return await EmployeeExperienceService.create_recognition(db, tenant_id, sender_id, data)

@router.get("/me/recognitions", response_model=List[EmployeeRecognitionResponse])
async def list_recognitions(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    return await EmployeeExperienceService.get_recognitions(db, tenant_id)

@router.get("/me/tasks", response_model=List[UnifiedTaskItem])
async def get_unified_tasks(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = uuid.UUID(str(current_user.tenant_id)) if hasattr(current_user, 'tenant_id') and current_user.tenant_id else uuid.uuid4()
    user_id = uuid.UUID(str(current_user.id))
    return await EmployeeExperienceService.get_unified_tasks_for_user(db, tenant_id, user_id)
