import math
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.employee import Employee
from app.models.location import (
    AttendanceLocation,
    AttendanceLocationAssignment,
    AttendanceLocationPolicy,
    LocationStatus,
    OutsideGeofenceAction
)
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationPolicyCreate,
    LocationAssignmentCreate
)
from app.services.audit_service import AuditService

EARTH_RADIUS_METERS = 6371000.0  # Earth's mean radius in meters

@dataclass
class LocationValidationResult:
    is_valid: bool
    status_code: str  # INSIDE, OUTSIDE, LOW_ACCURACY, STALE_LOCATION, INVALID_COORDINATES, NOT_REQUIRED, GEOFENCE_NOT_CONFIGURED
    distance_meters: float
    allowed_radius: float
    message: str
    has_exception: bool
    location_id: Optional[UUID] = None
    location_name: Optional[str] = None


class LocationService:

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates the great-circle distance between two GPS points in meters
        using the Haversine formula.
        """
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return EARTH_RADIUS_METERS * c

    @staticmethod
    def validate_coordinates(latitude: Optional[float], longitude: Optional[float], accuracy: Optional[float] = None) -> bool:
        if latitude is None or longitude is None:
            return False
        if not (-90.0 <= latitude <= 90.0):
            return False
        if not (-180.0 <= longitude <= 180.0):
            return False
        if accuracy is not None and accuracy <= 0.0:
            return False
        return True

    @staticmethod
    async def get_or_create_policy(db: AsyncSession, tenant_id: UUID) -> AttendanceLocationPolicy:
        res = await db.execute(
            select(AttendanceLocationPolicy).where(AttendanceLocationPolicy.tenant_id == tenant_id)
        )
        policy = res.scalar_one_or_none()
        if not policy:
            policy = AttendanceLocationPolicy(
                tenant_id=tenant_id,
                location_required=False,
                geofence_enabled=False,
                allowed_radius=100,
                minimum_accuracy=50.0,
                location_freshness_seconds=300,
                allow_outside_geofence=False,
                outside_geofence_action=OutsideGeofenceAction.REJECT
            )
            db.add(policy)
            await db.commit()
            await db.refresh(policy)
        return policy

    @staticmethod
    async def update_policy(
        db: AsyncSession,
        tenant_id: UUID,
        data: LocationPolicyCreate,
        actor_id: Optional[UUID] = None
    ) -> AttendanceLocationPolicy:
        policy = await LocationService.get_or_create_policy(db, tenant_id)
        for key, value in data.model_dump().items():
            setattr(policy, key, value)
        
        db.add(policy)
        await db.commit()
        await db.refresh(policy)

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="LOCATION_POLICY_UPDATED",
            entity_type="AttendanceLocationPolicy",
            entity_id=policy.id,
            actor_id=actor_id,
            details=data.model_dump()
        )
        return policy

    @staticmethod
    async def create_location(
        db: AsyncSession,
        tenant_id: UUID,
        data: LocationCreate,
        actor_id: Optional[UUID] = None
    ) -> AttendanceLocation:
        # Check duplicate code
        res = await db.execute(
            select(AttendanceLocation).where(
                and_(AttendanceLocation.tenant_id == tenant_id, AttendanceLocation.code == data.code.upper())
            )
        )
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location code '{data.code}' already exists for this organization."
            )

        loc = AttendanceLocation(
            tenant_id=tenant_id,
            created_by_id=actor_id,
            code=data.code.upper(),
            **data.model_dump(exclude={"code"})
        )
        db.add(loc)
        await db.commit()
        await db.refresh(loc)

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="LOCATION_CREATED",
            entity_type="AttendanceLocation",
            entity_id=loc.id,
            actor_id=actor_id,
            details={"code": loc.code, "name": loc.name, "latitude": loc.latitude, "longitude": loc.longitude}
        )
        return loc

    @staticmethod
    async def get_locations(db: AsyncSession, tenant_id: UUID) -> List[AttendanceLocation]:
        res = await db.execute(
            select(AttendanceLocation)
            .where(AttendanceLocation.tenant_id == tenant_id)
            .order_by(AttendanceLocation.name.asc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def get_location_by_id(db: AsyncSession, tenant_id: UUID, location_id: UUID) -> AttendanceLocation:
        res = await db.execute(
            select(AttendanceLocation).where(
                and_(AttendanceLocation.tenant_id == tenant_id, AttendanceLocation.id == location_id)
            )
        )
        loc = res.scalar_one_or_none()
        if not loc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance location not found.")
        return loc

    @staticmethod
    async def update_location(
        db: AsyncSession,
        tenant_id: UUID,
        location_id: UUID,
        data: LocationUpdate,
        actor_id: Optional[UUID] = None
    ) -> AttendanceLocation:
        loc = await LocationService.get_location_by_id(db, tenant_id, location_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(loc, key, value)
        
        db.add(loc)
        await db.commit()
        await db.refresh(loc)

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="LOCATION_UPDATED",
            entity_type="AttendanceLocation",
            entity_id=loc.id,
            actor_id=actor_id,
            details={"updated_fields": list(update_data.keys())}
        )
        return loc

    @staticmethod
    async def delete_location(
        db: AsyncSession,
        tenant_id: UUID,
        location_id: UUID,
        actor_id: Optional[UUID] = None
    ) -> None:
        loc = await LocationService.get_location_by_id(db, tenant_id, location_id)
        loc.status = LocationStatus.ARCHIVED
        db.add(loc)
        await db.commit()

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="LOCATION_ARCHIVED",
            entity_type="AttendanceLocation",
            entity_id=loc.id,
            actor_id=actor_id,
            details={"name": loc.name}
        )

    @staticmethod
    async def assign_location(
        db: AsyncSession,
        tenant_id: UUID,
        data: LocationAssignmentCreate,
        actor_id: Optional[UUID] = None
    ) -> AttendanceLocationAssignment:
        await LocationService.get_location_by_id(db, tenant_id, data.location_id)
        
        priority = 4
        if data.employee_id:
            priority = 1
        elif data.department_id:
            priority = 2
        elif data.branch_id:
            priority = 3

        assignment = AttendanceLocationAssignment(
            tenant_id=tenant_id,
            location_id=data.location_id,
            branch_id=data.branch_id,
            department_id=data.department_id,
            employee_id=data.employee_id,
            priority=priority,
            status=LocationStatus.ACTIVE
        )
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="LOCATION_ASSIGNED",
            entity_type="AttendanceLocationAssignment",
            entity_id=assignment.id,
            actor_id=actor_id,
            details={"location_id": str(data.location_id), "priority": priority}
        )
        return assignment

    @staticmethod
    async def resolve_employee_location(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID
    ) -> Tuple[Optional[AttendanceLocation], AttendanceLocationPolicy]:
        policy = await LocationService.get_or_create_policy(db, tenant_id)
        
        # 1. Fetch Employee record for Branch/Department context
        emp_res = await db.execute(
            select(Employee).where(and_(Employee.organization_id == tenant_id, Employee.id == employee_id))
        )
        emp = emp_res.scalar_one_or_none()
        
        if not emp:
            return None, policy

        # 2. Check explicit assignments by precedence (Priority 1 -> 2 -> 3)
        conditions = [AttendanceLocationAssignment.employee_id == employee_id]
        if emp.department_id is not None:
            conditions.append(AttendanceLocationAssignment.department_id == emp.department_id)
        if emp.branch_id is not None:
            conditions.append(AttendanceLocationAssignment.branch_id == emp.branch_id)

        assign_query = (
            select(AttendanceLocationAssignment)
            .options(selectinload(AttendanceLocationAssignment.location))
            .where(
                and_(
                    AttendanceLocationAssignment.tenant_id == tenant_id,
                    AttendanceLocationAssignment.status == LocationStatus.ACTIVE,
                    or_(*conditions)
                )
            )
            .order_by(AttendanceLocationAssignment.priority.asc())
        )
        assign_res = await db.execute(assign_query)
        assignment = assign_res.scalars().first()
        
        if assignment and assignment.location and assignment.location.status == LocationStatus.ACTIVE:
            return assignment.location, policy

        # 3. Check Branch direct location if available
        if emp.branch_id:
            branch_loc_res = await db.execute(
                select(AttendanceLocation).where(
                    and_(
                        AttendanceLocation.tenant_id == tenant_id,
                        AttendanceLocation.branch_id == emp.branch_id,
                        AttendanceLocation.status == LocationStatus.ACTIVE
                    )
                )
            )
            branch_loc = branch_loc_res.scalars().first()
            if branch_loc:
                return branch_loc, policy

        # 4. Fallback to default active Tenant location
        default_loc_res = await db.execute(
            select(AttendanceLocation)
            .where(
                and_(
                    AttendanceLocation.tenant_id == tenant_id,
                    AttendanceLocation.status == LocationStatus.ACTIVE
                )
            )
            .order_by(AttendanceLocation.created_at.asc())
        )
        default_loc = default_loc_res.scalars().first()

        return default_loc, policy

    @staticmethod
    async def validate_location_punch(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID,
        latitude: Optional[float],
        longitude: Optional[float],
        accuracy: Optional[float],
        captured_at: Optional[datetime] = None
    ) -> LocationValidationResult:
        location, policy = await LocationService.resolve_employee_location(db, tenant_id, employee_id)

        # Rule A: If Location is NOT required by tenant policy
        if not policy.location_required and not policy.geofence_enabled:
            return LocationValidationResult(
                is_valid=True,
                status_code="NOT_REQUIRED",
                distance_meters=0.0,
                allowed_radius=0.0,
                message="Location validation is not required for this tenant.",
                has_exception=False,
                location_id=location.id if location else None,
                location_name=location.name if location else None
            )

        # Rule B: Coordinate validation check
        if not LocationService.validate_coordinates(latitude, longitude, accuracy):
            return LocationValidationResult(
                is_valid=False,
                status_code="INVALID_COORDINATES",
                distance_meters=0.0,
                allowed_radius=location.radius_meters if location else policy.allowed_radius,
                message="Invalid or missing GPS coordinates provided.",
                has_exception=True
            )

        # Rule C: Freshness check
        now_utc = datetime.now(timezone.utc)
        if captured_at:
            if captured_at.tzinfo is None:
                captured_at = captured_at.replace(tzinfo=timezone.utc)
            delta_seconds = abs((now_utc - captured_at).total_seconds())
            if delta_seconds > policy.location_freshness_seconds:
                return LocationValidationResult(
                    is_valid=False,
                    status_code="STALE_LOCATION",
                    distance_meters=0.0,
                    allowed_radius=location.radius_meters if location else policy.allowed_radius,
                    message=f"GPS location measurement is stale ({int(delta_seconds)}s old). Please capture live location.",
                    has_exception=True
                )

        # Rule D: Accuracy requirement check
        min_acc = location.accuracy_requirement if location else policy.minimum_accuracy
        if accuracy is not None and accuracy > min_acc:
            return LocationValidationResult(
                is_valid=False,
                status_code="LOW_ACCURACY",
                distance_meters=0.0,
                allowed_radius=location.radius_meters if location else policy.allowed_radius,
                message=f"GPS accuracy ({accuracy:.1f}m) exceeds the allowed limit ({min_acc:.1f}m). Move to an open area.",
                has_exception=True
            )

        # Rule E: No Geofence Configured
        if not location:
            return LocationValidationResult(
                is_valid=not policy.geofence_enabled,
                status_code="GEOFENCE_NOT_CONFIGURED" if policy.geofence_enabled else "NOT_REQUIRED",
                distance_meters=0.0,
                allowed_radius=policy.allowed_radius,
                message="No geofence location is configured for your branch/department.",
                has_exception=policy.geofence_enabled
            )

        # Rule F: Calculate Haversine Distance
        distance = LocationService.haversine_distance(latitude, longitude, location.latitude, location.longitude)
        allowed_r = location.radius_meters or policy.allowed_radius

        if distance <= allowed_r:
            return LocationValidationResult(
                is_valid=True,
                status_code="INSIDE",
                distance_meters=round(distance, 2),
                allowed_radius=allowed_r,
                message=f"You are inside the authorized geofence area ({round(distance, 1)}m from center).",
                has_exception=False,
                location_id=location.id,
                location_name=location.name
            )
        else:
            is_valid = policy.allow_outside_geofence or (policy.outside_geofence_action != OutsideGeofenceAction.REJECT)
            return LocationValidationResult(
                is_valid=is_valid,
                status_code="OUTSIDE",
                distance_meters=round(distance, 2),
                allowed_radius=allowed_r,
                message=f"You are outside the authorized geofence boundary ({round(distance, 1)}m away, allowed {allowed_r}m).",
                has_exception=True,
                location_id=location.id,
                location_name=location.name
            )
