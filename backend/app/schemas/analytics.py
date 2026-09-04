from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class ExecutiveSummaryResponse(BaseModel):
    total_employees: int
    active_employees: int
    new_hires_this_month: int
    exits_this_month: int
    attrition_rate_pct: float
    open_positions: int
    candidates_in_pipeline: int
    total_payroll_cost_inr: Decimal
    avg_attendance_rate_pct: float
    avg_performance_rating: float
    training_completion_rate_pct: float

class DepartmentMetric(BaseModel):
    department_name: str
    headcount: int
    payroll_cost_inr: Decimal
    attrition_rate_pct: float
    avg_performance: float

class AttritionAnalyticsResponse(BaseModel):
    overall_attrition_rate_pct: float
    voluntary_count: int
    involuntary_count: int
    avg_tenure_months: float
    department_breakdown: List[DepartmentMetric]
    monthly_trend: List[Dict[str, Any]]

class LaborCostAnalyticsResponse(BaseModel):
    gross_payroll_inr: Decimal
    net_payroll_inr: Decimal
    total_tax_inr: Decimal
    overtime_cost_inr: Decimal
    reimbursements_cost_inr: Decimal
    cost_per_employee_inr: Decimal
