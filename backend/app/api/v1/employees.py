from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.models.user import User
from app.schemas.employee import (
    EmployeeListResponse, EmployeeStatsResponse, EmployeeSummary,
    EmployeeDetailResponse, EmployeeCreate, EmployeeUpdate, EmployeeStatusUpdate,
    EmployeeDocumentCreate, EmployeeDocumentResponse
)
from app.services.employee import EmployeeService
from app.services.audit_service import AuditService

router = APIRouter()

@router.get(
    "/employees",
    response_model=EmployeeListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get paginated list of employees",
    description="Returns searchable, filterable list of employees enforced by tenant scope."
)
async def get_employees(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    q: Optional[str] = Query(None, description="Search query (name, email, ID)"),
    department_id: Optional[UUID] = Query(None, description="Filter by department ID"),
    branch_id: Optional[UUID] = Query(None, description="Filter by branch ID"),
    designation_id: Optional[UUID] = Query(None, description="Filter by designation ID"),
    status_param: Optional[str] = Query(None, alias="status", description="Filter by status (ACTIVE, ON_LEAVE, INACTIVE, etc.)"),
    manager_id: Optional[UUID] = Query(None, description="Filter by reporting manager ID"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> EmployeeListResponse:
    request_id = getattr(request.state, "request_id", None)
    
    employees, total, total_pages = await EmployeeService.get_employees_paginated(
        db=db,
        tenant_id=tenant_id,
        page=page,
        limit=limit,
        search=q,
        department_id=department_id,
        branch_id=branch_id,
        designation_id=designation_id,
        status=status_param,
        manager_id=manager_id
    )

    data = [EmployeeSummary.model_validate(e) for e in employees]

    return EmployeeListResponse(
        success=True,
        data=data,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        request_id=request_id
    )

@router.post(
    "/employees",
    response_model=EmployeeDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee record",
    description="Creates an employee record within tenant and optionally creates linked user account."
)
async def create_employee(
    payload: EmployeeCreate,
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDetailResponse:
    emp = await EmployeeService.create_employee(db, tenant_id, payload)
    await AuditService.log_event(
        db=db, action="EMPLOYEE_CREATED", entity_type="Employee",
        entity_id=str(emp.id), tenant_id=tenant_id, actor_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    return EmployeeDetailResponse.model_validate(emp)

@router.get(
    "/employees/stats",
    response_model=EmployeeStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get employee database statistics"
)
async def get_employee_stats(
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> EmployeeStatsResponse:
    request_id = getattr(request.state, "request_id", None)
    stats = await EmployeeService.get_employee_stats(db, tenant_id)

    return EmployeeStatsResponse(
        success=True,
        total_employees=stats["total_employees"],
        active_employees=stats["active_employees"],
        on_leave_employees=stats["on_leave_employees"],
        inactive_employees=stats["inactive_employees"],
        departments_count=stats["departments_count"],
        by_department=stats["by_department"],
        request_id=request_id
    )

@router.get(
    "/employees/me",
    response_model=EmployeeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user's employee profile"
)
async def get_me_employee(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDetailResponse:
    from app.services.attendance_service import AttendanceService
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    return EmployeeDetailResponse.model_validate(emp)

@router.get(
    "/employees/{employee_id}",
    response_model=EmployeeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed employee profile"
)
async def get_employee(
    employee_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDetailResponse:
    emp = await EmployeeService.get_employee_by_id(db, employee_id, tenant_id)
    return EmployeeDetailResponse.model_validate(emp)

@router.put(
    "/employees/{employee_id}",
    response_model=EmployeeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update employee details"
)
async def update_employee(
    employee_id: UUID,
    payload: EmployeeUpdate,
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDetailResponse:
    emp = await EmployeeService.update_employee(db, tenant_id, employee_id, payload)
    await AuditService.log_event(
        db=db, action="EMPLOYEE_UPDATED", entity_type="Employee",
        entity_id=str(employee_id), tenant_id=tenant_id, actor_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    return EmployeeDetailResponse.model_validate(emp)

@router.patch(
    "/employees/{employee_id}/status",
    response_model=EmployeeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Change employee status lifecycle"
)
async def update_employee_status(
    employee_id: UUID,
    payload: EmployeeStatusUpdate,
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDetailResponse:
    emp = await EmployeeService.update_employee_status(db, tenant_id, employee_id, payload)
    await AuditService.log_event(
        db=db, action="EMPLOYEE_STATUS_CHANGED", entity_type="Employee",
        entity_id=str(employee_id), tenant_id=tenant_id, actor_id=current_user.id,
        details={"new_status": payload.status},
        ip_address=request.client.host if request.client else None
    )
    return EmployeeDetailResponse.model_validate(emp)

@router.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete / Terminate employee"
)
async def delete_employee(
    employee_id: UUID,
    request: Request,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    await EmployeeService.soft_delete_employee(db, tenant_id, employee_id)
    await AuditService.log_event(
        db=db, action="EMPLOYEE_TERMINATED", entity_type="Employee",
        entity_id=str(employee_id), tenant_id=tenant_id, actor_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    return {"success": True, "message": "Employee marked as terminated successfully"}

# --- Employee Documents ---
@router.get(
    "/employees/{employee_id}/documents",
    response_model=List[EmployeeDocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List employee document metadata records"
)
async def get_employee_documents(
    employee_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> List[EmployeeDocumentResponse]:
    docs = await EmployeeService.get_documents(db, tenant_id, employee_id)
    return [EmployeeDocumentResponse.model_validate(d) for d in docs]

@router.post(
    "/employees/{employee_id}/documents",
    response_model=EmployeeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add document metadata record for employee"
)
async def add_employee_document(
    employee_id: UUID,
    payload: EmployeeDocumentCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EmployeeDocumentResponse:
    doc = await EmployeeService.add_document(db, tenant_id, employee_id, payload, uploaded_by=current_user.id)
    return EmployeeDocumentResponse.model_validate(doc)

@router.delete(
    "/employees/{employee_id}/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete employee document metadata record"
)
async def delete_employee_document(
    employee_id: UUID,
    document_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> dict:
    await EmployeeService.delete_document(db, tenant_id, employee_id, document_id)
    return {"success": True, "message": "Document metadata removed successfully"}
