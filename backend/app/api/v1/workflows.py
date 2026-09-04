from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_current_tenant_id, require_permission
from app.schemas.workflow import (
    ApprovalWorkflowCreate,
    ApprovalWorkflowResponse,
    WorkflowStepResponse
)
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Approval Workflows"])


@router.post("/", response_model=ApprovalWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_workflow(
    data: ApprovalWorkflowCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(require_permission("workflow.create")),
    db: AsyncSession = Depends(get_db)
):
    wf = await WorkflowService.create_workflow(db, tenant_id, data)
    steps = [
        WorkflowStepResponse(
            id=s.id,
            workflow_id=s.workflow_id,
            step_order=s.step_order,
            name=s.name,
            approver_type=s.approver_type,
            approver_ref_id=s.approver_ref_id,
            required=s.required,
            auto_approve_after_days=s.auto_approve_after_days
        )
        for s in wf.steps
    ]
    return ApprovalWorkflowResponse(
        id=wf.id,
        tenant_id=wf.tenant_id,
        code=wf.code,
        name=wf.name,
        entity_type=wf.entity_type,
        status=wf.status,
        steps=steps,
        created_at=wf.created_at,
        updated_at=wf.updated_at
    )


@router.get("/", response_model=List[ApprovalWorkflowResponse])
async def get_approval_workflows(
    entity_type: Optional[str] = None,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workflows = await WorkflowService.get_workflows(db, tenant_id, entity_type)
    output = []
    for wf in workflows:
        steps = [
            WorkflowStepResponse(
                id=s.id,
                workflow_id=s.workflow_id,
                step_order=s.step_order,
                name=s.name,
                approver_type=s.approver_type,
                approver_ref_id=s.approver_ref_id,
                required=s.required,
                auto_approve_after_days=s.auto_approve_after_days
            )
            for s in wf.steps
        ]
        output.append(
            ApprovalWorkflowResponse(
                id=wf.id,
                tenant_id=wf.tenant_id,
                code=wf.code,
                name=wf.name,
                entity_type=wf.entity_type,
                status=wf.status,
                steps=steps,
                created_at=wf.created_at,
                updated_at=wf.updated_at
            )
        )
    return output
