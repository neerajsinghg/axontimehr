from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_current_tenant_id, require_permission
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationAssignmentCreate,
    LocationAssignmentResponse,
    LocationPolicyCreate,
    LocationPolicyResponse,
    LocationValidateRequest,
    LocationValidateResponse,
    SelfieUploadResponse,
    AttendanceExceptionResponse,
    AttendanceExceptionListResponse
)
from app.services.location_service import LocationService
from app.services.verification_service import VerificationService
from app.services.attendance_service import AttendanceService
from app.services.employee import EmployeeService

router = APIRouter(prefix="", tags=["Attendance Location & Verification"])

# ----------------------------------------------------
# 1. Attendance Location Policy Endpoints
# ----------------------------------------------------
@router.get(
    "/location-policies",
    response_model=LocationPolicyResponse,
    summary="Get tenant attendance location & verification policy"
)
async def get_location_policy(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> LocationPolicyResponse:
    policy = await LocationService.get_or_create_policy(db, tenant_id)
    return LocationPolicyResponse.model_validate(policy)

@router.put(
    "/location-policies",
    response_model=LocationPolicyResponse,
    summary="Update tenant attendance location & verification policy"
)
async def update_location_policy(
    data: LocationPolicyCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(require_permission("attendance.location_policy.update")),
    db: AsyncSession = Depends(get_db)
) -> LocationPolicyResponse:
    policy = await LocationService.update_policy(db, tenant_id, data, actor_id=current_user.id)
    return LocationPolicyResponse.model_validate(policy)


# ----------------------------------------------------
# 2. Location Master Management CRUD Endpoints
# ----------------------------------------------------
@router.get(
    "/locations",
    response_model=List[LocationResponse],
    summary="List all active attendance locations for organization"
)
async def get_locations(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> List[LocationResponse]:
    locations = await LocationService.get_locations(db, tenant_id)
    return [LocationResponse.model_validate(loc) for loc in locations]

@router.post(
    "/locations",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new attendance office/site location"
)
async def create_location(
    data: LocationCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(require_permission("attendance.location.create")),
    db: AsyncSession = Depends(get_db)
) -> LocationResponse:
    location = await LocationService.create_location(db, tenant_id, data, actor_id=current_user.id)
    return LocationResponse.model_validate(location)

@router.get(
    "/locations/{location_id}",
    response_model=LocationResponse,
    summary="Get location detail by ID"
)
async def get_location_by_id(
    location_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
) -> LocationResponse:
    location = await LocationService.get_location_by_id(db, tenant_id, location_id)
    return LocationResponse.model_validate(location)

@router.put(
    "/locations/{location_id}",
    response_model=LocationResponse,
    summary="Update attendance location details"
)
async def update_location(
    location_id: UUID,
    data: LocationUpdate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(require_permission("attendance.location.update")),
    db: AsyncSession = Depends(get_db)
) -> LocationResponse:
    location = await LocationService.update_location(db, tenant_id, location_id, data, actor_id=current_user.id)
    return LocationResponse.model_validate(location)

@router.delete(
    "/locations/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archive/Delete attendance location"
)
async def delete_location(
    location_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(require_permission("attendance.location.delete")),
    db: AsyncSession = Depends(get_db)
) -> None:
    await LocationService.delete_location(db, tenant_id, location_id, actor_id=current_user.id)


# ----------------------------------------------------
# 3. Location Roster Assignment Endpoints
# ----------------------------------------------------
@router.post(
    "/location-assignments",
    response_model=LocationAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign location to Branch, Department or Employee"
)
async def assign_location(
    data: LocationAssignmentCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(require_permission("attendance.location.create")),
    db: AsyncSession = Depends(get_db)
) -> LocationAssignmentResponse:
    assignment = await LocationService.assign_location(db, tenant_id, data, actor_id=current_user.id)
    return LocationAssignmentResponse.model_validate(assignment)


# ----------------------------------------------------
# 4. Geofence Validation Pre-check Endpoint
# ----------------------------------------------------
@router.post(
    "/location/validate",
    response_model=LocationValidateResponse,
    summary="Pre-validate client GPS coordinates against assigned geofence"
)
async def validate_location_precheck(
    payload: LocationValidateRequest,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> LocationValidateResponse:
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    res = await LocationService.validate_location_punch(
        db, tenant_id, emp.id, payload.latitude, payload.longitude, payload.accuracy, payload.captured_at
    )
    return LocationValidateResponse(
        is_valid=res.is_valid,
        status_code=res.status_code,
        distance_meters=res.distance_meters,
        allowed_radius=res.allowed_radius,
        message=res.message,
        location_id=res.location_id,
        location_name=res.location_name
    )


# ----------------------------------------------------
# 5. Selfie Upload & Streaming Endpoints
# ----------------------------------------------------
@router.post(
    "/verification/upload-selfie",
    response_model=SelfieUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload selfie image for attendance identity verification"
)
async def upload_selfie(
    file: UploadFile = File(...),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SelfieUploadResponse:
    emp = await AttendanceService.get_or_create_employee_for_user(db, tenant_id, current_user.id)
    ver = await VerificationService.process_selfie_upload(db, tenant_id, emp.id, file)
    return SelfieUploadResponse(
        verification_id=ver.id,
        status=ver.status,
        score=ver.score,
        message=f"Selfie processed successfully ({ver.status.value})."
    )

@router.get(
    "/verification/selfie/{verification_id}",
    summary="Stream selfie image for verified attendance preview"
)
async def get_selfie_image(
    verification_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    full_path, mime_type = await VerificationService.get_selfie_path(db, tenant_id, verification_id)
    return FileResponse(full_path, media_type=mime_type)


# ----------------------------------------------------
# 6. Admin Exception Dashboard Endpoint
# ----------------------------------------------------
@router.get(
    "/exceptions",
    response_model=AttendanceExceptionListResponse,
    summary="List attendance location & verification exceptions for admin review"
)
async def get_attendance_exceptions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(require_permission("attendance.exception.view")),
    db: AsyncSession = Depends(get_db)
):
    items, total = await AttendanceService.get_exceptions(db, tenant_id, page, limit, start_date, end_date)
    return {
        "success": True,
        "data": items,
        "total": total,
        "page": page,
        "limit": limit
    }
