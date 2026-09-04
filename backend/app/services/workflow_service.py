import uuid
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.workflow import (
    ApprovalWorkflow,
    ApprovalWorkflowStep,
    ApprovalInstance,
    ApprovalInstanceStep,
    ApprovalAction,
    ApprovalDelegation,
    ApproverType,
    ApprovalActionType,
    WorkflowStatus,
    ApprovalInstanceStatus
)
from app.models.employee import Employee
from app.models.organization import Department
from app.models.user import User
from app.schemas.workflow import ApprovalWorkflowCreate, ApprovalActionRequest


class WorkflowService:

    @staticmethod
    async def create_workflow(db: AsyncSession, tenant_id: uuid.UUID, data: ApprovalWorkflowCreate) -> ApprovalWorkflow:
        existing = await db.execute(
            select(ApprovalWorkflow).where(
                and_(
                    ApprovalWorkflow.tenant_id == tenant_id,
                    ApprovalWorkflow.code == data.code
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Approval workflow with code '{data.code}' already exists."
            )

        wf = ApprovalWorkflow(
            tenant_id=tenant_id,
            code=data.code,
            name=data.name,
            entity_type=data.entity_type,
            status=data.status
        )
        db.add(wf)
        await db.flush()

        for step_data in data.steps:
            step = ApprovalWorkflowStep(
                tenant_id=tenant_id,
                workflow_id=wf.id,
                step_order=step_data.step_order,
                name=step_data.name,
                approver_type=step_data.approver_type,
                approver_ref_id=step_data.approver_ref_id,
                required=step_data.required,
                auto_approve_after_days=step_data.auto_approve_after_days
            )
            db.add(step)

        await db.commit()
        await db.refresh(wf)
        return wf

    @staticmethod
    async def get_workflows(db: AsyncSession, tenant_id: uuid.UUID, entity_type: Optional[str] = None) -> List[ApprovalWorkflow]:
        query = select(ApprovalWorkflow).options(selectinload(ApprovalWorkflow.steps)).where(ApprovalWorkflow.tenant_id == tenant_id)
        if entity_type:
            query = query.where(ApprovalWorkflow.entity_type == entity_type)

        res = await db.execute(query.order_by(ApprovalWorkflow.name))
        return list(res.scalars().all())

    @staticmethod
    async def start_approval_instance(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        requester_id: uuid.UUID
    ) -> ApprovalInstance:
        # Find default or active workflow for entity_type
        wf_res = await db.execute(
            select(ApprovalWorkflow)
            .options(selectinload(ApprovalWorkflow.steps))
            .where(
                and_(
                    ApprovalWorkflow.tenant_id == tenant_id,
                    ApprovalWorkflow.entity_type == entity_type,
                    ApprovalWorkflow.status == WorkflowStatus.ACTIVE
                )
            )
        )
        wf = wf_res.scalars().first()

        if not wf or not wf.steps:
            # Fallback single-step manager approval: Create default workflow record first
            wf = ApprovalWorkflow(
                tenant_id=tenant_id,
                code=f"DEFAULT_{entity_type}",
                name=f"Default {entity_type} Workflow",
                entity_type=entity_type,
                status=WorkflowStatus.ACTIVE
            )
            db.add(wf)
            await db.flush()

            wf_step = ApprovalWorkflowStep(
                tenant_id=tenant_id,
                workflow_id=wf.id,
                step_order=1,
                name="Reporting Manager Approval",
                approver_type=ApproverType.REPORTING_MANAGER,
                required=True
            )
            db.add(wf_step)
            await db.flush()

            instance = ApprovalInstance(
                tenant_id=tenant_id,
                workflow_id=wf.id,
                entity_type=entity_type,
                entity_id=entity_id,
                requester_id=requester_id,
                current_step_order=1,
                status=ApprovalInstanceStatus.PENDING
            )
            db.add(instance)
            await db.flush()

            # Resolve manager
            emp_res = await db.execute(select(Employee).where(Employee.id == requester_id))
            emp = emp_res.scalar_one_or_none()
            manager_user_id = emp.manager_id if emp else None

            inst_step = ApprovalInstanceStep(
                tenant_id=tenant_id,
                instance_id=instance.id,
                step_order=1,
                approver_type=ApproverType.REPORTING_MANAGER,
                assigned_approver_id=manager_user_id,
                status=ApprovalInstanceStatus.PENDING
            )
            db.add(inst_step)
            await db.commit()
            await db.refresh(instance)
            return instance

        # Create instance from template steps
        instance = ApprovalInstance(
            tenant_id=tenant_id,
            workflow_id=wf.id,
            entity_type=entity_type,
            entity_id=entity_id,
            requester_id=requester_id,
            current_step_order=1,
            status=ApprovalInstanceStatus.PENDING
        )
        db.add(instance)
        await db.flush()

        emp_res = await db.execute(select(Employee).where(Employee.id == requester_id))
        emp = emp_res.scalar_one_or_none()

        for s in wf.steps:
            assigned_id = None
            if s.approver_type == ApproverType.REPORTING_MANAGER and emp:
                assigned_id = emp.manager_id
            elif s.approver_type == ApproverType.SPECIFIC_USER and s.approver_ref_id:
                try:
                    assigned_id = uuid.UUID(s.approver_ref_id)
                except ValueError:
                    pass

            inst_step = ApprovalInstanceStep(
                tenant_id=tenant_id,
                instance_id=instance.id,
                step_order=s.step_order,
                approver_type=s.approver_type,
                assigned_approver_id=assigned_id,
                status=ApprovalInstanceStatus.PENDING
            )
            db.add(inst_step)

        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def process_action(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        instance_id: uuid.UUID,
        actor_user: User,
        action_req: ApprovalActionRequest
    ) -> ApprovalInstance:
        inst_res = await db.execute(
            select(ApprovalInstance)
            .options(selectinload(ApprovalInstance.steps), selectinload(ApprovalInstance.requester))
            .where(
                and_(
                    ApprovalInstance.id == instance_id,
                    ApprovalInstance.tenant_id == tenant_id
                )
            )
        )
        instance = inst_res.scalar_one_or_none()
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval instance not found."
            )

        if instance.status != ApprovalInstanceStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Approval instance is already {instance.status.value}."
            )

        # Self-approval prevention check
        if instance.requester and instance.requester.user_id == actor_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Self-approval is prohibited. You cannot approve or modify your own request."
            )

        current_step = next((s for s in instance.steps if s.step_order == instance.current_step_order), None)
        
        # Log action
        action_log = ApprovalAction(
            tenant_id=tenant_id,
            instance_id=instance.id,
            step_id=current_step.id if current_step else None,
            actor_id=actor_user.id,
            action=action_req.action,
            comments=action_req.comments
        )
        db.add(action_log)

        if action_req.action == ApprovalActionType.REJECT:
            instance.status = ApprovalInstanceStatus.REJECTED
            if current_step:
                current_step.status = ApprovalInstanceStatus.REJECTED

        elif action_req.action == ApprovalActionType.APPROVE:
            if current_step:
                current_step.status = ApprovalInstanceStatus.APPROVED
            
            # Check if more steps exist
            next_step = next((s for s in instance.steps if s.step_order == instance.current_step_order + 1), None)
            if next_step:
                instance.current_step_order += 1
            else:
                instance.status = ApprovalInstanceStatus.APPROVED

        elif action_req.action == ApprovalActionType.RETURN:
            instance.status = ApprovalInstanceStatus.RETURNED

        elif action_req.action == ApprovalActionType.CANCEL:
            instance.status = ApprovalInstanceStatus.CANCELLED

        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def get_inbox(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        actor_user: User
    ) -> List[dict]:
        # Fetch pending approval instances for tenant
        res = await db.execute(
            select(ApprovalInstance)
            .options(
                selectinload(ApprovalInstance.steps),
                selectinload(ApprovalInstance.requester),
                selectinload(ApprovalInstance.workflow)
            )
            .where(
                and_(
                    ApprovalInstance.tenant_id == tenant_id,
                    ApprovalInstance.status == ApprovalInstanceStatus.PENDING,
                    ApprovalInstance.requester_id != actor_user.id  # exclude self requests
                )
            )
        )
        instances = res.scalars().all()

        inbox_items = []
        for inst in instances:
            current_step = next((s for s in inst.steps if s.step_order == inst.current_step_order), None)
            req_name = f"{inst.requester.first_name} {inst.requester.last_name}" if inst.requester else "Unknown"

            inbox_items.append({
                "instance_id": inst.id,
                "workflow_id": inst.workflow_id,
                "workflow_name": inst.workflow.name if inst.workflow else "Approval Workflow",
                "entity_type": inst.entity_type,
                "entity_id": inst.entity_id,
                "requester_id": inst.requester_id,
                "requester_name": req_name,
                "current_step_order": inst.current_step_order,
                "current_step_name": current_step.approver_type.value if current_step else "Manager Approval",
                "status": inst.status.value if hasattr(inst.status, 'value') else str(inst.status),
                "details": {
                    "entity_type": inst.entity_type,
                    "entity_id": str(inst.entity_id)
                },
                "created_at": inst.created_at,
                "updated_at": inst.updated_at
            })

        return inbox_items
