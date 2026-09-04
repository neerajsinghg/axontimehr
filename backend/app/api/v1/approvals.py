from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.workflow import ApprovalActionType, ApprovalInstanceStatus
from app.api.deps import get_current_user, get_current_tenant_id
from app.schemas.workflow import (
    ApprovalActionRequest,
    ApprovalActionResponse,
    ApprovalItemResponse
)
from app.services.workflow_service import WorkflowService
from app.services.leave_service import LeaveService
from app.services.regularization_service import RegularizationService
from app.services.expense_service import ExpenseService
from app.services.loan_service import LoanService
from app.services.advance_service import AdvanceService

router = APIRouter(prefix="/approvals", tags=["Manager & HR Approval Inbox"])


@router.get("/inbox", response_model=List[ApprovalItemResponse])
async def get_approval_inbox(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await WorkflowService.get_inbox(db, tenant_id, current_user)


@router.post("/{instance_id}/action")
async def process_approval_action(
    instance_id: UUID,
    action_req: ApprovalActionRequest,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    instance = await WorkflowService.process_action(db, tenant_id, instance_id, current_user, action_req)

    # Trigger entity status callbacks if final decision reached
    if instance.status == ApprovalInstanceStatus.APPROVED:
        if instance.entity_type == "LEAVE_REQUEST":
            await LeaveService.approve_leave_request(db, tenant_id, instance.entity_id)
        elif instance.entity_type == "REGULARIZATION":
            await RegularizationService.approve_request(db, tenant_id, instance.entity_id)
        elif instance.entity_type == "EXPENSE_CLAIM":
            await ExpenseService.approve_claim(db, tenant_id, instance.entity_id)
        elif instance.entity_type == "EMPLOYEE_LOAN":
            await LoanService.approve_loan(db, tenant_id, instance.entity_id)
        elif instance.entity_type == "SALARY_ADVANCE":
            await AdvanceService.approve_advance(db, tenant_id, instance.entity_id)
    elif instance.status == ApprovalInstanceStatus.REJECTED:
        if instance.entity_type == "LEAVE_REQUEST":
            # Unreserve pending leave balance
            req = await LeaveService.cancel_leave_request(db, tenant_id, instance.entity_id)

    return {
        "success": True,
        "instance_id": str(instance.id),
        "status": instance.status.value if hasattr(instance.status, 'value') else str(instance.status),
        "action_taken": action_req.action.value if hasattr(action_req.action, 'value') else str(action_req.action)
    }
