import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.models.user import User
from app.services.compliance_service import ComplianceService
from app.schemas.compliance import (
    EstablishmentCreate, EstablishmentResponse,
    StatutoryRegistrationCreate, StatutoryRegistrationResponse,
    EmployeeStatutoryProfileUpdate, EmployeeStatutoryProfileResponse,
    ComplianceRuleCreate, ComplianceRuleResponse,
    PrePayrollPrecheckResponse,
    ComplianceTaskCreate, ComplianceTaskResponse,
    ComplianceViolationCreate, ComplianceViolationResponse,
    InternalAuditCreate, InternalAuditResponse,
    ConsentGrantRequest, PrivacyConsentResponse,
    DataSubjectRequestCreate, DataSubjectRequestResponse,
    LegalHoldCreate, LegalHoldResponse,
    ComplianceDashboardSummary
)

router = APIRouter(prefix="/compliance", tags=["Compliance & Governance"])

# Dashboard Summary Scorecard
@router.get("/dashboard", response_model=ComplianceDashboardSummary)
async def get_compliance_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_dashboard_summary(db, tenant_id)


# Establishments Hierarchy
@router.post("/establishments", response_model=EstablishmentResponse, status_code=status.HTTP_201_CREATED)
async def create_establishment(
    data: EstablishmentCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.create_establishment(db, tenant_id, data)

@router.get("/establishments", response_model=List[EstablishmentResponse])
async def get_establishments(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_establishments(db, tenant_id)


# Statutory Registrations
@router.post("/registrations", response_model=StatutoryRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    data: StatutoryRegistrationCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.create_registration(db, tenant_id, data)

@router.get("/registrations", response_model=List[StatutoryRegistrationResponse])
async def get_registrations(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_registrations(db, tenant_id)


# Employee Statutory Profiles
@router.get("/employee-statutory/{employee_id}", response_model=EmployeeStatutoryProfileResponse)
async def get_employee_statutory_profile(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_or_create_statutory_profile(db, tenant_id, employee_id)

@router.put("/employee-statutory/{employee_id}", response_model=EmployeeStatutoryProfileResponse)
async def update_employee_statutory_profile(
    employee_id: str,
    data: EmployeeStatutoryProfileUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.update_statutory_profile(db, tenant_id, employee_id, data)


# Compliance Rules Engine
@router.post("/rules", response_model=ComplianceRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_compliance_rule(
    data: ComplianceRuleCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.create_rule(db, tenant_id, data)

@router.get("/rules", response_model=List[ComplianceRuleResponse])
async def get_compliance_rules(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_rules(db, tenant_id)


# Pre-Payroll Compliance Pre-Check Engine
@router.post("/payroll/precheck", response_model=PrePayrollPrecheckResponse)
async def run_prepayroll_compliance_precheck(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.run_prepayroll_precheck(db, tenant_id)


# Compliance Tasks & Evidence
@router.post("/tasks", response_model=ComplianceTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_compliance_task(
    data: ComplianceTaskCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.create_task(db, tenant_id, data)

@router.get("/tasks", response_model=List[ComplianceTaskResponse])
async def get_compliance_tasks(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_tasks(db, tenant_id)


# Violations & CAPA
@router.post("/violations", response_model=ComplianceViolationResponse, status_code=status.HTTP_201_CREATED)
async def create_compliance_violation(
    data: ComplianceViolationCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.create_violation(db, tenant_id, data)

@router.get("/violations", response_model=List[ComplianceViolationResponse])
async def get_compliance_violations(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_violations(db, tenant_id)


# Internal Audits
@router.post("/audits", response_model=InternalAuditResponse, status_code=status.HTTP_201_CREATED)
async def create_internal_audit(
    data: InternalAuditCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.create_audit(db, tenant_id, data)

@router.get("/audits", response_model=List[InternalAuditResponse])
async def get_internal_audits(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_audits(db, tenant_id)


# Data Privacy & Legal Holds
@router.post("/privacy/consents", response_model=PrivacyConsentResponse)
async def grant_privacy_consent(
    data: ConsentGrantRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.grant_consent(db, tenant_id, str(current_user.id), data)

@router.post("/privacy/dsr", response_model=DataSubjectRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_dsr_request(
    data: DataSubjectRequestCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.create_dsr_request(db, tenant_id, str(current_user.id), data)

@router.get("/privacy/dsr", response_model=List[DataSubjectRequestResponse])
async def get_dsr_requests(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_dsr_requests(db, tenant_id)

@router.post("/privacy/legal-holds", response_model=LegalHoldResponse, status_code=status.HTTP_201_CREATED)
async def create_legal_hold(
    data: LegalHoldCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.create_legal_hold(db, tenant_id, data)

@router.get("/privacy/legal-holds", response_model=List[LegalHoldResponse])
async def get_legal_holds(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await ComplianceService.get_legal_holds(db, tenant_id)
