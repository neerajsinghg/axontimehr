from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# Metrics & Query Engine
class AnalyticsMetricResponse(BaseModel):
    id: str
    tenant_id: str
    metric_code: str
    metric_name: str
    category: str
    calculation_formula: str
    unit: str
    version: int

    class Config:
        from_attributes = True

class AnalyticsQueryRequest(BaseModel):
    metric_code: str = Field(..., example="HEADCOUNT_TOTAL")
    aggregation: str = Field("COUNT", example="COUNT") # COUNT, SUM, AVG, MIN, MAX, PERCENTAGE, GROWTH_RATE
    filters: Dict[str, Any] = Field(default_factory=dict)
    group_by: Optional[str] = Field(None, example="department")
    period: str = Field("current_month", example="current_month")

class AnalyticsQueryResult(BaseModel):
    metric_code: str
    metric_name: str
    unit: str
    calculated_value: float
    formatted_value: str
    group_breakdown: Optional[Dict[str, float]] = None
    trend_pct: Optional[float] = 4.2


# Dashboards
class AnalyticsDashboardCreate(BaseModel):
    title: str = Field(..., example="Executive Workforce Board")
    description: Optional[str] = None
    is_shared: bool = False
    widgets_config: List[Dict[str, Any]] = Field(default_factory=list)

class AnalyticsDashboardResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: Optional[str]
    owner_id: str
    is_shared: bool
    widgets_config_json: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# AI Copilot Chat
class AICopilotChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message_text: str = Field(..., example="What is our current monthly payroll cost and attrition rate?")

class AICopilotChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    reply_text: str
    kpi_cards: List[Dict[str, Any]] = Field(default_factory=list)
    chart_type: Optional[str] = Field("bar", example="bar")
    chart_data: Optional[Dict[str, Any]] = None
    suggested_questions: List[str] = Field(default_factory=list)
    created_at: datetime


# Anomalies
class AnomalyRecordResponse(BaseModel):
    id: str
    tenant_id: str
    module: str
    severity: str
    title: str
    description: str
    anomaly_score: float
    entity_type: Optional[str]
    entity_id: Optional[str]
    review_status: str
    resolution_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AnomalyReviewRequest(BaseModel):
    review_status: str = Field(..., example="CONFIRMED") # CONFIRMED, FALSE_POSITIVE, RESOLVED
    resolution_notes: Optional[str] = None


# Workforce Forecasts & Scenarios
class WorkforceForecastResponse(BaseModel):
    id: str
    tenant_id: str
    forecast_type: str
    horizon_days: int
    forecast_results_json: Dict[str, Any]
    accuracy_score: float
    run_date: date

    class Config:
        from_attributes = True

class ScenarioCreateRequest(BaseModel):
    scenario_name: str = Field(..., example="Q4 15% Engineering Expansion Scenario")
    input_parameters: Dict[str, Any] = Field(..., example={"additional_hires": 15, "average_salary_inr": 1800000})

class ScenarioResponse(BaseModel):
    id: str
    tenant_id: str
    scenario_name: str
    input_parameters_json: Dict[str, Any]
    projected_results_json: Dict[str, Any]
    created_by_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Data Quality
class DataQualityIssueResponse(BaseModel):
    id: str
    tenant_id: str
    issue_type: str
    severity: str
    description: str
    affected_entity_type: str
    affected_entity_id: str
    is_resolved: bool
    detected_at: datetime

    class Config:
        from_attributes = True
