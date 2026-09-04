import os
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from dataclasses import dataclass
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile

from app.models.location import (
    AttendanceVerification,
    AttendanceLocationPolicy,
    VerificationStatus,
    VerificationProviderType,
    VerificationFailureAction
)
from app.services.location_service import LocationService
from app.services.audit_service import AuditService

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "selfies")

@dataclass
class VerificationResult:
    is_valid: bool
    status: VerificationStatus
    score: float
    message: str
    verification_id: Optional[UUID] = None


class VerificationProvider(ABC):
    @abstractmethod
    async def verify(self, file_bytes: bytes, filename: str) -> Tuple[VerificationStatus, float, str]:
        pass


class MockVerificationProvider(VerificationProvider):
    async def verify(self, file_bytes: bytes, filename: str) -> Tuple[VerificationStatus, float, str]:
        # Deterministic testing rules
        if "test_fail" in filename.lower():
            return VerificationStatus.FAILED, 0.25, "Facial match score below confidence threshold."
        elif "test_review" in filename.lower():
            return VerificationStatus.PENDING, 0.65, "Verification score requires admin review."
        else:
            return VerificationStatus.VERIFIED, 0.98, "Identity verified successfully."


class VerificationService:

    @staticmethod
    def get_provider(provider_type: str = "MOCK") -> VerificationProvider:
        return MockVerificationProvider()

    @staticmethod
    async def process_selfie_upload(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID,
        file: UploadFile
    ) -> AttendanceVerification:
        # 1. Validate MIME type & file extension
        allowed_mimes = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{file.content_type}'. Allowed types: JPEG, PNG, WEBP."
            )

        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded."
            )
        if len(file_bytes) > 5 * 1024 * 1024:  # 5MB max
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds maximum limit of 5MB."
            )

        # 2. Save file to local storage directory
        verification_id = uuid.uuid4()
        tenant_upload_dir = os.path.join(UPLOAD_DIR, str(tenant_id))
        os.makedirs(tenant_upload_dir, exist_ok=True)
        
        ext = ".jpg"
        if "png" in file.content_type:
            ext = ".png"
        elif "webp" in file.content_type:
            ext = ".webp"

        file_filename = f"{verification_id}{ext}"
        full_path = os.path.join(tenant_upload_dir, file_filename)

        with open(full_path, "wb") as f:
            f.write(file_bytes)

        rel_storage_key = os.path.join("uploads", "selfies", str(tenant_id), file_filename)

        # 3. Execute Verification Provider
        provider = VerificationService.get_provider("MOCK")
        v_status, score, msg = await provider.verify(file_bytes, file.filename or file_filename)

        # 4. Create Database Record
        verification = AttendanceVerification(
            id=verification_id,
            tenant_id=tenant_id,
            employee_id=employee_id,
            provider="MOCK",
            status=v_status,
            score=score,
            storage_key=rel_storage_key,
            mime_type=file.content_type,
            file_size=len(file_bytes),
            verified_at=datetime.now(timezone.utc)
        )
        db.add(verification)
        await db.commit()
        await db.refresh(verification)

        await AuditService.log_event(
            db=db,
            tenant_id=tenant_id,
            action="SELFIE_VERIFICATION_PROCESSED",
            entity_type="AttendanceVerification",
            entity_id=verification.id,
            details={"status": v_status, "score": score, "file_size": len(file_bytes)}
        )
        return verification

    @staticmethod
    async def evaluate_verification_requirement(
        db: AsyncSession,
        tenant_id: UUID,
        employee_id: UUID,
        verification_id: Optional[UUID]
    ) -> VerificationResult:
        policy = await LocationService.get_or_create_policy(db, tenant_id)

        # Rule A: If Selfie is NOT required by policy
        if not policy.selfie_required:
            return VerificationResult(
                is_valid=True,
                status=VerificationStatus.NOT_REQUIRED,
                score=1.0,
                message="Selfie verification is not required for this organization."
            )

        # Rule B: Missing verification when required
        if not verification_id:
            return VerificationResult(
                is_valid=False,
                status=VerificationStatus.FAILED,
                score=0.0,
                message="Selfie verification is required by tenant policy."
            )

        # Rule C: Check verification record
        res = await db.execute(
            select(AttendanceVerification).where(
                and_(
                    AttendanceVerification.tenant_id == tenant_id,
                    AttendanceVerification.employee_id == employee_id,
                    AttendanceVerification.id == verification_id
                )
            )
        )
        ver = res.scalar_one_or_none()
        if not ver:
            return VerificationResult(
                is_valid=False,
                status=VerificationStatus.FAILED,
                score=0.0,
                message="Invalid or missing verification reference."
            )

        if ver.status == VerificationStatus.VERIFIED:
            return VerificationResult(
                is_valid=True,
                status=VerificationStatus.VERIFIED,
                score=ver.score,
                message="Identity verified successfully.",
                verification_id=ver.id
            )
        else:
            is_valid = policy.verification_failure_action != VerificationFailureAction.REJECT
            return VerificationResult(
                is_valid=is_valid,
                status=ver.status,
                score=ver.score,
                message=f"Selfie verification failed ({ver.status}).",
                verification_id=ver.id
            )

    @staticmethod
    async def get_selfie_path(
        db: AsyncSession,
        tenant_id: UUID,
        verification_id: UUID
    ) -> Tuple[str, str]:
        res = await db.execute(
            select(AttendanceVerification).where(
                and_(
                    AttendanceVerification.tenant_id == tenant_id,
                    AttendanceVerification.id == verification_id
                )
            )
        )
        ver = res.scalar_one_or_none()
        if not ver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification selfie not found.")

        full_path = os.path.join(os.getcwd(), ver.storage_key)
        if not os.path.exists(full_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selfie file storage key not found.")

        return full_path, ver.mime_type
