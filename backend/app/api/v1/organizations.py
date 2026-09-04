from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.models.user import User
from app.schemas.organization import (
    CompanyResponse, CompanyUpdate,
    BranchResponse, BranchCreate, BranchUpdate,
    DepartmentResponse, DepartmentCreate, DepartmentUpdate,
    DesignationResponse, DesignationCreate, DesignationUpdate
)
from app.services.organization_service import OrganizationService
from app.services.audit_service import AuditService

router = APIRouter()

# --- Organization ---
@router.get(
    "/organization",
    response_model=CompanyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tenant organization profile"
)
async def get_organization(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> CompanyResponse:
    company = await OrganizationService.get_company(db, tenant_id)
    return CompanyResponse.model_validate(company)

@router.put(
    "/organization",
    response_model=CompanyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update tenant organization profile"
)
async def update_organization(
    payload: CompanyUpdate,
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CompanyResponse:
    company = await OrganizationService.update_company(db, tenant_id, payload)
    await AuditService.log_event(
        db=db, action="ORGANIZATION_UPDATED", entity_type="Company",
        entity_id=str(tenant_id), tenant_id=tenant_id, actor_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    return CompanyResponse.model_validate(company)

# --- Branches ---
@router.get(
    "/branches",
    response_model=List[BranchResponse],
    status_code=status.HTTP_200_OK,
    summary="List organization branches"
)
async def get_branches(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> List[BranchResponse]:
    branches = await OrganizationService.get_branches(db, tenant_id)
    return [BranchResponse.model_validate(b) for b in branches]

@router.post(
    "/branches",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create branch"
)
async def create_branch(
    payload: BranchCreate,
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> BranchResponse:
    branch = await OrganizationService.create_branch(db, tenant_id, payload)
    await AuditService.log_event(
        db=db, action="BRANCH_CREATED", entity_type="Branch",
        entity_id=str(branch.id), tenant_id=tenant_id, actor_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    return BranchResponse.model_validate(branch)

@router.get(
    "/branches/{branch_id}",
    response_model=BranchResponse,
    status_code=status.HTTP_200_OK,
    summary="Get branch details"
)
async def get_branch(
    branch_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> BranchResponse:
    branch = await OrganizationService.get_branch(db, tenant_id, branch_id)
    return BranchResponse.model_validate(branch)

@router.put(
    "/branches/{branch_id}",
    response_model=BranchResponse,
    status_code=status.HTTP_200_OK,
    summary="Update branch"
)
async def update_branch(
    branch_id: UUID,
    payload: BranchUpdate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> BranchResponse:
    branch = await OrganizationService.update_branch(db, tenant_id, branch_id, payload)
    return BranchResponse.model_validate(branch)

@router.delete(
    "/branches/{branch_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete branch"
)
async def delete_branch(
    branch_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> dict:
    await OrganizationService.delete_branch(db, tenant_id, branch_id)
    return {"success": True, "message": "Branch deleted successfully"}

# --- Departments ---
@router.get(
    "/departments",
    response_model=List[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List organization departments"
)
async def get_departments(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> List[DepartmentResponse]:
    depts = await OrganizationService.get_departments(db, tenant_id)
    return [DepartmentResponse.model_validate(d) for d in depts]

@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create department"
)
async def create_department(
    payload: DepartmentCreate,
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DepartmentResponse:
    dept = await OrganizationService.create_department(db, tenant_id, payload)
    await AuditService.log_event(
        db=db, action="DEPARTMENT_CREATED", entity_type="Department",
        entity_id=str(dept.id), tenant_id=tenant_id, actor_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    return DepartmentResponse.model_validate(dept)

@router.get(
    "/departments/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get department details"
)
async def get_department(
    department_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> DepartmentResponse:
    dept = await OrganizationService.get_department(db, tenant_id, department_id)
    return DepartmentResponse.model_validate(dept)

@router.put(
    "/departments/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update department"
)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> DepartmentResponse:
    dept = await OrganizationService.update_department(db, tenant_id, department_id, payload)
    return DepartmentResponse.model_validate(dept)

@router.delete(
    "/departments/{department_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete department"
)
async def delete_department(
    department_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> dict:
    await OrganizationService.delete_department(db, tenant_id, department_id)
    return {"success": True, "message": "Department deleted successfully"}

# --- Designations ---
@router.get(
    "/designations",
    response_model=List[DesignationResponse],
    status_code=status.HTTP_200_OK,
    summary="List organization designations"
)
async def get_designations(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> List[DesignationResponse]:
    desigs = await OrganizationService.get_designations(db, tenant_id)
    return [DesignationResponse.model_validate(d) for d in desigs]

@router.post(
    "/designations",
    response_model=DesignationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create designation"
)
async def create_designation(
    payload: DesignationCreate,
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DesignationResponse:
    desig = await OrganizationService.create_designation(db, tenant_id, payload)
    await AuditService.log_event(
        db=db, action="DESIGNATION_CREATED", entity_type="Designation",
        entity_id=str(desig.id), tenant_id=tenant_id, actor_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    return DesignationResponse.model_validate(desig)

@router.get(
    "/designations/{designation_id}",
    response_model=DesignationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get designation details"
)
async def get_designation(
    designation_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> DesignationResponse:
    desig = await OrganizationService.get_designation(db, tenant_id, designation_id)
    return DesignationResponse.model_validate(desig)

@router.put(
    "/designations/{designation_id}",
    response_model=DesignationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update designation"
)
async def update_designation(
    designation_id: UUID,
    payload: DesignationUpdate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> DesignationResponse:
    desig = await OrganizationService.update_designation(db, tenant_id, designation_id, payload)
    return DesignationResponse.model_validate(desig)

@router.delete(
    "/designations/{designation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete designation"
)
async def delete_designation(
    designation_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> dict:
    await OrganizationService.delete_designation(db, tenant_id, designation_id)
    return {"success": True, "message": "Designation deleted successfully"}
