import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.services.workforce_service import WorkforceService
from app.schemas.workforce import HeadcountPlanCreate, HeadcountPlanResponse, GapAnalysisResponse, WorkforceForecastResponse

router = APIRouter(prefix="/workforce", tags=["Workforce Planning"])

@router.post("/headcount-plans", response_model=HeadcountPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_headcount_plan(
    data: HeadcountPlanCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await WorkforceService.create_headcount_plan(db, tenant_id, data)

@router.get("/headcount-plans", response_model=List[HeadcountPlanResponse])
async def get_headcount_plans(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await WorkforceService.get_headcount_plans(db, tenant_id)

@router.get("/gap-analysis", response_model=List[GapAnalysisResponse])
async def get_gap_analysis(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await WorkforceService.get_gap_analysis(db, tenant_id)

@router.get("/forecast", response_model=WorkforceForecastResponse)
async def get_workforce_forecast(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user)
):
    return await WorkforceService.get_workforce_forecast(db, tenant_id)
