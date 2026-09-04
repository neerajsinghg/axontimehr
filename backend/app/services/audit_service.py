import json
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from app.core.logging import logger

class AuditService:
    @staticmethod
    async def log_event(
        db: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        tenant_id: Optional[UUID] = None,
        actor_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        try:
            details_str = json.dumps(details) if details else None
            log_record = AuditLog(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id else None,
                details=details_str,
                ip_address=ip_address
            )
            db.add(log_record)
            await db.flush()
            logger.info(f"Audit log recorded: {action} on {entity_type} {entity_id}", extra={"tenant_id": str(tenant_id) if tenant_id else None})
            return log_record
        except Exception as e:
            logger.warning(f"Failed to record audit log: {e}")
            return None
