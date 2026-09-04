from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id, require_permission
from app.models.user import User
from app.models.employee import Employee
from app.schemas.attendance import (
    PunchRequest,
    AttendanceResponse,
    AttendanceListResponse,
    DailyAttendanceStatusResponse,
    AttendanceDashboardResponse,
    ShiftCreate,
    ShiftUpdate,
    ShiftResponse,
    ShiftAssignmentCreate,
    ShiftAssignmentResponse,
    RegularizationCreate,
    RegularizationResponse,
    HolidayCreate,
    HolidayResponse
)
from app.services.attendance_service import AttendanceService
from app.services.shift_service import ShiftService

router = APIRouter()

# ----------------------------------------------------
# Attendance Punches (Check-In & Check-Out)
# ----------------------------------------------------
@router.post("/attendance/check-in", response_model=AttendanceResponse)
async def check_in(
    data: PunchRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    return await AttendanceService.check_in(db, tenant_id, emp.id, data)

@router.post("/attendance/check-out", response_model=AttendanceResponse)
async def check_out(
    data: PunchRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    return await AttendanceService.check_out(db, tenant_id, emp.id, data)

@router.get("/attendance/today", response_model=DailyAttendanceStatusResponse)
async def get_today_status(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    return await AttendanceService.get_today_status(db, tenant_id, emp.id)

@router.get("/attendance/my", response_model=AttendanceListResponse)
async def get_my_attendance_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    records, total = await AttendanceService.get_my_attendance_history(
        db, tenant_id, emp.id, page, limit, start_date, end_date
    )
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return AttendanceListResponse(
        success=True,
        data=[AttendanceResponse.model_validate(r) for r in records],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.get("/attendance/dashboard", response_model=AttendanceDashboardResponse)
async def get_attendance_dashboard(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await AttendanceService.get_dashboard_metrics(db, tenant_id)

# ----------------------------------------------------
# Regularization Workflows
# ----------------------------------------------------
@router.post("/attendance/regularization", response_model=RegularizationResponse)
async def request_regularization(
    data: RegularizationCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    return await AttendanceService.request_regularization(db, tenant_id, emp.id, data)

@router.post("/attendance/regularization/{id}/approve", response_model=RegularizationResponse)
async def approve_regularization(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await AttendanceService.approve_regularization(db, tenant_id, id, current_user.id)

# ----------------------------------------------------
# Shift Master CRUD & Roster Assignment
# ----------------------------------------------------
@router.get("/shifts", response_model=List[ShiftResponse])
async def get_shifts(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    shifts = await ShiftService.get_shifts(db, tenant_id)
    return [ShiftResponse.model_validate(s) for s in shifts]

@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(
    data: ShiftCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    shift = await ShiftService.create_shift(db, tenant_id, data, current_user.id)
    return ShiftResponse.model_validate(shift)

@router.get("/shifts/{id}", response_model=ShiftResponse)
async def get_shift_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    shift = await ShiftService.get_shift_by_id(db, tenant_id, id)
    return ShiftResponse.model_validate(shift)

@router.put("/shifts/{id}", response_model=ShiftResponse)
async def update_shift(
    id: UUID,
    data: ShiftUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    shift = await ShiftService.update_shift(db, tenant_id, id, data, current_user.id)
    return ShiftResponse.model_validate(shift)

@router.post("/employees/{employee_id}/shift", response_model=ShiftAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_employee_shift(
    employee_id: UUID,
    data: ShiftAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    assignment = await ShiftService.assign_employee_shift(db, tenant_id, employee_id, data, current_user.id)
    return ShiftAssignmentResponse.model_validate(assignment)

# ----------------------------------------------------
# Holiday Calendar Management
# ----------------------------------------------------
@router.get("/holidays", response_model=List[HolidayResponse])
async def get_holidays(
    branch_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    holidays = await ShiftService.get_holidays(db, tenant_id, branch_id)
    return [HolidayResponse.model_validate(h) for h in holidays]

@router.post("/holidays", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    data: HolidayCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    holiday = await ShiftService.create_holiday(db, tenant_id, data, current_user.id)
    return HolidayResponse.model_validate(holiday)
