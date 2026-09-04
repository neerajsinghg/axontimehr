import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.services.ai_orchestrator_service import AIOrchestratorService
from app.schemas.ai import AIQueryRequest, AIQueryResponse

router = APIRouter(prefix="/ai", tags=["AI HR Intelligence Assistant"])

@router.post("/query", response_model=AIQueryResponse)
async def query_ai_assistant(
    request: AIQueryRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await AIOrchestratorService.process_query(db, tenant_id, current_user.id, request)
