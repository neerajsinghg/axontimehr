import uuid
import enum
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Enum, Text, Numeric
from app.models import Base

class PlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class PositionStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

class HeadcountPlan(Base):
    __tablename__ = "workforce_headcount_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    planning_year = Column(Integer, default=2026, nullable=False)
    department_id = Column(String(36), nullable=True, index=True)
    designation_id = Column(String(36), nullable=True)
    current_headcount = Column(Integer, default=0, nullable=False)
    target_headcount = Column(Integer, default=0, nullable=False)
    planned_hiring = Column(Integer, default=0, nullable=False)
    expected_attrition = Column(Integer, default=0, nullable=False)
    allocated_budget = Column(Numeric(14, 2), default=0.00, nullable=False)
    status = Column(Enum(PlanStatus), default=PlanStatus.DRAFT, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class PositionPlan(Base):
    __tablename__ = "workforce_position_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    headcount_plan_id = Column(String(36), ForeignKey("workforce_headcount_plans.id"), nullable=True)
    position_title = Column(String(200), nullable=False)
    department_id = Column(String(36), nullable=True)
    designation_id = Column(String(36), nullable=True)
    location = Column(String(200), nullable=True)
    budget = Column(Numeric(12, 2), default=0.00, nullable=False)
    planned_start_date = Column(Date, nullable=True)
    status = Column(Enum(PositionStatus), default=PositionStatus.PLANNED, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class WorkforceDemand(Base):
    __tablename__ = "workforce_demands"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    department_id = Column(String(36), nullable=False)
    requested_positions = Column(Integer, default=1, nullable=False)
    justification = Column(Text, nullable=True)
    target_quarter = Column(String(20), default="Q1", nullable=False)
    status = Column(Enum(PlanStatus), default=PlanStatus.DRAFT, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class WorkforceForecast(Base):
    __tablename__ = "workforce_forecasts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    forecast_period = Column(String(50), default="2026-Q4", nullable=False)
    department_id = Column(String(36), nullable=True)
    expected_headcount = Column(Integer, default=0, nullable=False)
    expected_hiring_need = Column(Integer, default=0, nullable=False)
    expected_attrition = Column(Integer, default=0, nullable=False)
    expected_labor_cost = Column(Numeric(14, 2), default=0.00, nullable=False)
    confidence_level = Column(String(20), default="MEDIUM", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
