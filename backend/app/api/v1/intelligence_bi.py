import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.models.user import User
from app.services.intelligence_bi_service import IntelligenceBiService
from app.schemas.intelligence_bi import (
    AnalyticsMetricResponse, AnalyticsQueryRequest, AnalyticsQueryResult,
    AICopilotChatRequest, AICopilotChatResponse,
    AnomalyRecordResponse, AnomalyReviewRequest,
    WorkforceForecastResponse, ScenarioCreateRequest, ScenarioResponse,
    DataQualityIssueResponse
)

router = APIRouter(prefix="", tags=["Phase 13: Intelligence & BI Platform"])

# Metric Catalog & Analytics Query Execution Engine
@router.get("/analytics/metrics", response_model=List[AnalyticsMetricResponse])
async def get_metrics_catalog(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.get_metrics(db, tenant_id)

@router.post("/analytics/query", response_model=AnalyticsQueryResult)
async def execute_analytics_query(
    data: AnalyticsQueryRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.execute_analytics_query(db, tenant_id, data)


# AxonTime AI Copilot Conversational Assistant
@router.post("/ai/copilot/chat", response_model=AICopilotChatResponse)
async def copilot_chat(
    data: AICopilotChatRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.process_copilot_chat(db, tenant_id, current_user.id, data)


# Anomaly Detection Center
@router.get("/anomalies", response_model=List[AnomalyRecordResponse])
async def get_anomalies(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.get_anomalies(db, tenant_id)

@router.patch("/anomalies/{anomaly_id}/review", response_model=AnomalyRecordResponse)
async def review_anomaly(
    anomaly_id: str,
    data: AnomalyReviewRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.review_anomaly(db, tenant_id, anomaly_id, data)


# Workforce Forecasts & Scenario Planning
@router.get("/forecasts", response_model=List[WorkforceForecastResponse])
async def get_workforce_forecasts(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.get_forecasts(db, tenant_id)

@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    data: ScenarioCreateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.create_scenario(db, tenant_id, current_user.id, data)

@router.get("/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.get_scenarios(db, tenant_id)


# Data Quality Auditor
@router.get("/data-quality/issues", response_model=List[DataQualityIssueResponse])
async def get_data_quality_issues(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    return await IntelligenceBiService.get_data_quality_issues(db, tenant_id)
