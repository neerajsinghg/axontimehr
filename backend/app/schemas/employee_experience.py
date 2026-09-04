import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from app.models.employee_experience import (
    ChangeRequestStatus, HRRequestType, HRRequestStatus, TicketCategory, TicketPriority,
    TicketStatus, AnnouncementPriority, AnnouncementTargetType, RecognitionType
)

# --- ESS Dashboard & Profile ---
class EmployeeDashboardSummary(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    designation_name: Optional[str] = None
    department_name: Optional[str] = None
    today_status: str
    check_in_time: Optional[str] = None
    leave_balance_days: float
    latest_payslip_month: Optional[str] = None
    latest_net_pay_inr: Optional[float] = None
    pending_tasks_count: int
    active_goals_count: int
    assigned_trainings_count: int
    unread_announcements_count: int

class ProfileUpdateRequest(BaseModel):
    personal_email: Optional[str] = None
    personal_phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

class ProfileChangeRequestCreate(BaseModel):
    field_name: str
    new_value: str
    reason: str

class ProfileChangeRequestResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    field_name: str
    old_value: Optional[str] = None
    new_value: str
    reason: Optional[str] = None
    status: ChangeRequestStatus
    reviewed_by_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    comments: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Documents & Letters ---
class HRDocumentTemplateCreate(BaseModel):
    title: str
    template_code: str
    category: str = "GENERAL"
    template_body: str
    variables_json: Optional[str] = None

class HRDocumentTemplateResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    template_code: str
    category: str
    template_body: str
    variables_json: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class GenerateLetterRequest(BaseModel):
    template_id: str
    employee_id: str
    custom_variables: Optional[Dict[str, Any]] = None

class GeneratedHRLetterResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    template_id: Optional[str] = None
    title: str
    letter_number: str
    snapshot_html: str
    file_url: Optional[str] = None
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Policies ---
class HRPolicyCreate(BaseModel):
    title: str
    category: str = "GENERAL"
    current_version: str = "1.0"
    policy_body: str
    file_url: Optional[str] = None
    is_mandatory_ack: bool = True

class HRPolicyResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    category: str
    current_version: str
    policy_body: str
    file_url: Optional[str] = None
    is_mandatory_ack: bool
    created_at: datetime
    is_acknowledged_by_me: bool = False

    class Config:
        from_attributes = True

# --- HR Requests & Helpdesk ---
class HRRequestCreate(BaseModel):
    request_type: HRRequestType
    subject: str
    details: Optional[str] = None

class HRRequestResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    request_type: HRRequestType
    subject: str
    details: Optional[str] = None
    status: HRRequestStatus
    assigned_to_id: Optional[str] = None
    expected_completion_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HRHelpdeskTicketCreate(BaseModel):
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    subject: str
    description: str

class HRHelpdeskCommentSubmit(BaseModel):
    comment_text: str
    attachment_url: Optional[str] = None

class HRHelpdeskCommentResponse(BaseModel):
    id: str
    ticket_id: str
    sender_id: str
    comment_text: str
    attachment_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HRHelpdeskTicketResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    ticket_number: str
    category: TicketCategory
    priority: TicketPriority
    subject: str
    description: str
    status: TicketStatus
    assigned_agent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    comments: List[HRHelpdeskCommentResponse] = []

    class Config:
        from_attributes = True

# --- Announcements & Recognition ---
class CompanyAnnouncementCreate(BaseModel):
    title: str
    content: str
    category: str = "GENERAL"
    priority: AnnouncementPriority = AnnouncementPriority.NORMAL
    target_type: AnnouncementTargetType = AnnouncementTargetType.ALL
    target_id: Optional[str] = None
    is_mandatory_ack: bool = False

class CompanyAnnouncementResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    content: str
    category: str
    priority: AnnouncementPriority
    target_type: AnnouncementTargetType
    target_id: Optional[str] = None
    publish_date: datetime
    is_mandatory_ack: bool
    status: str
    is_read_by_me: bool = False
    is_acknowledged_by_me: bool = False

    class Config:
        from_attributes = True

class EmployeeRecognitionCreate(BaseModel):
    recipient_id: str
    recognition_type: RecognitionType
    message: str

class EmployeeRecognitionResponse(BaseModel):
    id: str
    tenant_id: str
    sender_id: str
    recipient_id: str
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None
    recognition_type: RecognitionType
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Unified Tasks & Approvals ---
class UnifiedTaskItem(BaseModel):
    id: str
    module: str  # LEAVE, EXPENSE, PERFORMANCE, POLICY, HR_REQUEST, HELPDESK
    title: str
    description: str
    created_at: datetime
    priority: str = "MEDIUM"
    action_url: str
