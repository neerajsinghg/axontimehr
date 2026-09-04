from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.models.workforce import PlanStatus, PositionStatus

class HeadcountPlanCreate(BaseModel):
    planning_year: int = 2026
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    current_headcount: int = 0
    target_headcount: int = 10
    planned_hiring: int = 10
    expected_attrition: int = 1
    allocated_budget: Decimal = Decimal("5000000.00")

class HeadcountPlanResponse(HeadcountPlanCreate):
    id: str
    tenant_id: str
    status: PlanStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class GapAnalysisResponse(BaseModel):
    department_id: Optional[str] = None
    department_name: str
    current_headcount: int
    required_headcount: int
    headcount_gap: int
    planned_hiring: int
    skill_gap_count: int
    advisory_recommendation: str

class WorkforceForecastResponse(BaseModel):
    forecast_period: str
    expected_headcount: int
    expected_hiring_need: int
    expected_attrition: int
    expected_labor_cost: Decimal
    confidence_level: str
