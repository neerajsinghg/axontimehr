from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.location import (
    GeofenceType,
    LocationStatus,
    OutsideGeofenceAction,
    VerificationFailureAction,
    VerificationStatus
)

class LocationCreate(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    branch_id: Optional[UUID] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    radius_meters: int = Field(default=100, gt=0, le=50000)
    accuracy_requirement: float = Field(default=50.0, gt=0.0)
    geofence_type: GeofenceType = GeofenceType.CIRCULAR
    coordinates: Optional[Dict[str, Any]] = None
    status: LocationStatus = LocationStatus.ACTIVE

class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    branch_id: Optional[UUID] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    radius_meters: Optional[int] = Field(None, gt=0, le=50000)
    accuracy_requirement: Optional[float] = Field(None, gt=0.0)
    geofence_type: Optional[GeofenceType] = None
    coordinates: Optional[Dict[str, Any]] = None
    status: Optional[LocationStatus] = None

class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    branch_id: Optional[UUID] = None
    name: str
    code: str
    latitude: float
    longitude: float
    radius_meters: int
    accuracy_requirement: float
    geofence_type: GeofenceType
    coordinates: Optional[Dict[str, Any]] = None
    status: LocationStatus
    created_at: datetime
    updated_at: datetime

class LocationAssignmentCreate(BaseModel):
    location_id: UUID
    branch_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None

class LocationAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    location_id: UUID
    branch_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    priority: int
    status: LocationStatus
    location: Optional[LocationResponse] = None

class LocationPolicyCreate(BaseModel):
    location_required: bool = False
    geofence_enabled: bool = False
    allowed_radius: int = Field(default=100, gt=0)
    minimum_accuracy: float = Field(default=50.0, gt=0.0)
    location_freshness_seconds: int = Field(default=300, gt=0)
    allow_outside_geofence: bool = False
    outside_geofence_action: OutsideGeofenceAction = OutsideGeofenceAction.REJECT
    selfie_required: bool = False
    verification_failure_action: VerificationFailureAction = VerificationFailureAction.REJECT

class LocationPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    location_required: bool
    geofence_enabled: bool
    allowed_radius: int
    minimum_accuracy: float
    location_freshness_seconds: int
    allow_outside_geofence: bool
    outside_geofence_action: OutsideGeofenceAction
    selfie_required: bool
    verification_failure_action: VerificationFailureAction
    created_at: datetime
    updated_at: datetime

class LocationValidateRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    accuracy: float = Field(..., gt=0.0)
    captured_at: Optional[datetime] = None

class LocationValidateResponse(BaseModel):
    is_valid: bool
    status_code: str # INSIDE, OUTSIDE, LOW_ACCURACY, STALE_LOCATION, INVALID_COORDINATES
    distance_meters: float
    allowed_radius: float
    message: str
    location_id: Optional[UUID] = None
    location_name: Optional[str] = None

class SelfieUploadResponse(BaseModel):
    verification_id: UUID
    status: VerificationStatus
    score: float
    message: str

class AttendanceExceptionResponse(BaseModel):
    attendance_id: UUID
    employee_id: UUID
    employee_name: str
    attendance_date: str
    status: str
    location_status: Optional[str] = None
    verification_status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    distance_meters: Optional[float] = None
    verification_id: Optional[UUID] = None
    remarks: Optional[str] = None
    created_at: datetime

class AttendanceExceptionListResponse(BaseModel):
    success: bool = True
    data: List[AttendanceExceptionResponse]
    total: int
    page: int
    limit: int
