from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_current_tenant_id, require_permission
from app.schemas.regularization import (
    RegularizationCreate,
    RegularizationResponse
)
from app.services.regularization_service import RegularizationService
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/regularizations", tags=["Attendance Regularization"])


@router.post("/", response_model=RegularizationResponse, status_code=status.HTTP_201_CREATED)
async def create_regularization_request(
    data: RegularizationCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    reg = await RegularizationService.create_request(db, tenant_id, emp.id, data)
    emp_name = f"{emp.first_name} {emp.last_name}"

    return RegularizationResponse(
        id=reg.id,
        tenant_id=reg.tenant_id,
        attendance_id=reg.attendance_id,
        employee_id=reg.employee_id,
        employee_name=emp_name,
        attendance_date=reg.attendance_date,
        original_check_in=reg.original_check_in,
        original_check_out=reg.original_check_out,
        requested_check_in=reg.requested_check_in,
        requested_check_out=reg.requested_check_out,
        reason=reg.reason,
        status=reg.status,
        approval_instance_id=reg.approval_instance_id,
        created_at=reg.created_at,
        updated_at=reg.updated_at
    )


@router.get("/", response_model=List[RegularizationResponse])
async def get_regularization_requests(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    return await RegularizationService.get_requests(db, tenant_id, emp.id)
