import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import ExecutiveSummaryResponse, AttritionAnalyticsResponse, LaborCostAnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Advanced HR Analytics"])

@router.get("/executive-summary", response_model=ExecutiveSummaryResponse)
async def get_executive_summary(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await AnalyticsService.get_executive_summary(db, tenant_id)

@router.get("/attrition", response_model=AttritionAnalyticsResponse)
async def get_attrition_analytics(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await AnalyticsService.get_attrition_analytics(db, tenant_id)

@router.get("/labor-cost", response_model=LaborCostAnalyticsResponse)
async def get_labor_cost_analytics(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await AnalyticsService.get_labor_cost_analytics(db, tenant_id)
