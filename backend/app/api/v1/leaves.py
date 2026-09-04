from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.leave import LeaveRequest, LeaveLedger
from app.api.deps import get_current_user, get_current_tenant_id, require_permission
from app.schemas.leave import (
    LeaveTypeCreate,
    LeaveTypeResponse,
    LeavePolicyCreate,
    LeavePolicyResponse,
    LeaveBalanceResponse,
    LeaveLedgerResponse,
    LeaveRequestCreate,
    LeaveRequestResponse
)
from app.services.leave_service import LeaveService
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/leaves", tags=["Leaves & Balance Engine"])


@router.post("/types", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_type(
    data: LeaveTypeCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await LeaveService.create_leave_type(db, tenant_id, data)


@router.get("/types", response_model=List[LeaveTypeResponse])
async def get_leave_types(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await LeaveService.get_leave_types(db, tenant_id)


@router.post("/policies", response_model=LeavePolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_policy(
    data: LeavePolicyCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await LeaveService.create_leave_policy(db, tenant_id, data)


@router.get("/balance", response_model=List[LeaveBalanceResponse])
async def get_my_leave_balances(
    year: Optional[int] = None,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    return await LeaveService.get_employee_balances(db, tenant_id, emp.id, year)


@router.get("/requests", response_model=List[LeaveRequestResponse])
async def get_my_leave_requests(
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    res = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.employee), selectinload(LeaveRequest.leave_type))
        .where(
            and_(
                LeaveRequest.tenant_id == tenant_id,
                LeaveRequest.employee_id == emp.id
            )
        )
        .order_by(LeaveRequest.created_at.desc())
    )
    requests = res.scalars().all()

    output = []
    for r in requests:
        emp_name = f"{r.employee.first_name} {r.employee.last_name}" if r.employee else "Unknown Employee"
        output.append(
            LeaveRequestResponse(
                id=r.id,
                tenant_id=r.tenant_id,
                employee_id=r.employee_id,
                employee_name=emp_name,
                leave_type_id=r.leave_type_id,
                leave_type_name=r.leave_type.name if r.leave_type else "Leave",
                leave_type_code=r.leave_type.code if r.leave_type else "LEAVE",
                color_code=r.leave_type.color_code if r.leave_type else "#10B981",
                start_date=r.start_date,
                end_date=r.end_date,
                duration_type=r.duration_type,
                half_day_position=r.half_day_position,
                total_requested_days=r.total_requested_days,
                working_days_count=r.working_days_count,
                holiday_days_count=r.holiday_days_count,
                weekly_off_days_count=r.weekly_off_days_count,
                reason=r.reason,
                document_url=r.document_url,
                status=r.status,
                approval_instance_id=r.approval_instance_id,
                created_at=r.created_at,
                updated_at=r.updated_at
            )
        )
    return output


@router.post("/requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(
    data: LeaveRequestCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    req = await LeaveService.create_leave_request(db, tenant_id, emp.id, data)
    
    # Reload details
    res = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.employee), selectinload(LeaveRequest.leave_type))
        .where(LeaveRequest.id == req.id)
    )
    r = res.scalar_one()
    emp_name = f"{r.employee.first_name} {r.employee.last_name}" if r.employee else "Unknown Employee"
    
    return LeaveRequestResponse(
        id=r.id,
        tenant_id=r.tenant_id,
        employee_id=r.employee_id,
        employee_name=emp_name,
        leave_type_id=r.leave_type_id,
        leave_type_name=r.leave_type.name if r.leave_type else "Leave",
        leave_type_code=r.leave_type.code if r.leave_type else "LEAVE",
        color_code=r.leave_type.color_code if r.leave_type else "#10B981",
        start_date=r.start_date,
        end_date=r.end_date,
        duration_type=r.duration_type,
        half_day_position=r.half_day_position,
        total_requested_days=r.total_requested_days,
        working_days_count=r.working_days_count,
        holiday_days_count=r.holiday_days_count,
        weekly_off_days_count=r.weekly_off_days_count,
        reason=r.reason,
        document_url=r.document_url,
        status=r.status,
        approval_instance_id=r.approval_instance_id,
        created_at=r.created_at,
        updated_at=r.updated_at
    )


@router.post("/requests/{id}/cancel", response_model=LeaveRequestResponse)
async def cancel_leave_request(
    id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    req = await LeaveService.cancel_leave_request(db, tenant_id, id)
    res = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.employee), selectinload(LeaveRequest.leave_type))
        .where(LeaveRequest.id == req.id)
    )
    r = res.scalar_one()
    emp_name = f"{r.employee.first_name} {r.employee.last_name}" if r.employee else "Unknown Employee"

    return LeaveRequestResponse(
        id=r.id,
        tenant_id=r.tenant_id,
        employee_id=r.employee_id,
        employee_name=emp_name,
        leave_type_id=r.leave_type_id,
        leave_type_name=r.leave_type.name if r.leave_type else "Leave",
        leave_type_code=r.leave_type.code if r.leave_type else "LEAVE",
        color_code=r.leave_type.color_code if r.leave_type else "#10B981",
        start_date=r.start_date,
        end_date=r.end_date,
        duration_type=r.duration_type,
        half_day_position=r.half_day_position,
        total_requested_days=r.total_requested_days,
        working_days_count=r.working_days_count,
        holiday_days_count=r.holiday_days_count,
        weekly_off_days_count=r.weekly_off_days_count,
        reason=r.reason,
        document_url=r.document_url,
        status=r.status,
        approval_instance_id=r.approval_instance_id,
        created_at=r.created_at,
        updated_at=r.updated_at
    )
