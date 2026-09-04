import enum
import uuid
from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApproverType(str, enum.Enum):
    REPORTING_MANAGER = "REPORTING_MANAGER"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    HR = "HR"
    ROLE = "ROLE"
    SPECIFIC_USER = "SPECIFIC_USER"
    ADMIN = "ADMIN"


class ApprovalActionType(str, enum.Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    RETURN = "RETURN"
    CANCEL = "CANCEL"
    DELEGATE = "DELEGATE"


class WorkflowStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ApprovalInstanceStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RETURNED = "RETURNED"
    CANCELLED = "CANCELLED"


class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False, index=True)  # LEAVE_REQUEST, REGULARIZATION, OVERTIME
    status = Column(Enum(WorkflowStatus, native_enum=False), nullable=False, default=WorkflowStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    steps = relationship("ApprovalWorkflowStep", back_populates="workflow", cascade="all, delete-orphan", order_by="ApprovalWorkflowStep.step_order")

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="idx_workflow_tenant_code"),
    )


class ApprovalWorkflowStep(Base):
    __tablename__ = "approval_workflow_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("approval_workflows.id", ondelete="CASCADE"), nullable=False, index=True)

    step_order = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    approver_type = Column(Enum(ApproverType, native_enum=False), nullable=False)
    approver_ref_id = Column(String(100), nullable=True)  # Role ID or User ID if SPECIFIC_USER/ROLE
    required = Column(Boolean, nullable=False, default=True)
    auto_approve_after_days = Column(Integer, nullable=True)

    workflow = relationship("ApprovalWorkflow", back_populates="steps")

    __table_args__ = (
        UniqueConstraint("workflow_id", "step_order", name="idx_wf_step_wf_order"),
    )


class ApprovalInstance(Base):
    __tablename__ = "approval_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("approval_workflows.id", ondelete="CASCADE"), nullable=False, index=True)

    entity_type = Column(String(50), nullable=False, index=True)  # LEAVE_REQUEST, REGULARIZATION
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)

    current_step_order = Column(Integer, nullable=False, default=1)
    status = Column(Enum(ApprovalInstanceStatus, native_enum=False), nullable=False, default=ApprovalInstanceStatus.PENDING, index=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workflow = relationship("ApprovalWorkflow")
    requester = relationship("Employee", foreign_keys=[requester_id])
    steps = relationship("ApprovalInstanceStep", back_populates="instance", cascade="all, delete-orphan", order_by="ApprovalInstanceStep.step_order")


class ApprovalInstanceStep(Base):
    __tablename__ = "approval_instance_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("approval_instances.id", ondelete="CASCADE"), nullable=False, index=True)

    step_order = Column(Integer, nullable=False)
    approver_type = Column(Enum(ApproverType, native_enum=False), nullable=False)
    assigned_approver_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Resolved specific User/Employee ID
    status = Column(Enum(ApprovalInstanceStatus, native_enum=False), nullable=False, default=ApprovalInstanceStatus.PENDING)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    instance = relationship("ApprovalInstance", back_populates="steps")


class ApprovalAction(Base):
    __tablename__ = "approval_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("approval_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(UUID(as_uuid=True), ForeignKey("approval_instance_steps.id", ondelete="SET NULL"), nullable=True)

    actor_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # User ID of approver
    action = Column(Enum(ApprovalActionType, native_enum=False), nullable=False)
    comments = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    instance = relationship("ApprovalInstance")


class ApprovalDelegation(Base):
    __tablename__ = "approval_delegations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    delegator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    delegate_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    scope = Column(String(50), nullable=False, default="ALL")  # ALL, LEAVE, REGULARIZATION
    status = Column(String(20), nullable=False, default="ACTIVE")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
