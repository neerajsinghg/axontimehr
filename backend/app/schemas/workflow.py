from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.models.workflow import (
    ApproverType,
    ApprovalActionType,
    WorkflowStatus,
    ApprovalInstanceStatus
)


class WorkflowStepCreate(BaseModel):
    step_order: int
    name: str = Field(..., max_length=100)
    approver_type: ApproverType
    approver_ref_id: Optional[str] = None
    required: bool = True
    auto_approve_after_days: Optional[int] = None


class WorkflowStepResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    step_order: int
    name: str
    approver_type: ApproverType
    approver_ref_id: Optional[str] = None
    required: bool
    auto_approve_after_days: Optional[int] = None


class ApprovalWorkflowCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    entity_type: str = Field(..., max_length=50)  # LEAVE_REQUEST, REGULARIZATION
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    steps: List[WorkflowStepCreate]


class ApprovalWorkflowResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    entity_type: str
    status: WorkflowStatus
    steps: List[WorkflowStepResponse]
    created_at: datetime
    updated_at: datetime


class ApprovalActionRequest(BaseModel):
    action: ApprovalActionType
    comments: Optional[str] = None
    delegate_to_user_id: Optional[UUID] = None


class ApprovalActionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    instance_id: UUID
    actor_id: UUID
    actor_name: str
    action: ApprovalActionType
    comments: Optional[str] = None
    created_at: datetime


class ApprovalItemResponse(BaseModel):
    instance_id: UUID
    workflow_id: UUID
    workflow_name: str
    entity_type: str
    entity_id: UUID
    requester_id: UUID
    requester_name: str
    department_name: Optional[str] = None
    current_step_order: int
    current_step_name: str
    status: ApprovalInstanceStatus
    details: dict  # Entity preview (e.g. Leave dates, reason)
    created_at: datetime
    updated_at: datetime
