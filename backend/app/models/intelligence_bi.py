import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, String, Boolean, Float, DateTime, Date, Text, JSON, Integer
from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class BIMetricDefinition(Base):
    __tablename__ = "bi_metric_definitions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    metric_code = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False) # WORKFORCE, ATTENDANCE, PAYROLL, LEAVE, EXPENSE, RECRUITMENT, COMPLIANCE
    calculation_formula = Column(Text, nullable=False)
    unit = Column(String(20), default="COUNT") # COUNT, PERCENTAGE, CURRENCY, HOURS, DAYS
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalyticsDashboard(Base):
    __tablename__ = "analytics_dashboards"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), nullable=False, index=True)
    is_shared = Column(Boolean, default=False)
    widgets_config_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New AI Copilot Session")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), nullable=False, index=True)
    sender_role = Column(String(20), nullable=False) # USER, ASSISTANT, SYSTEM
    content = Column(Text, nullable=False)
    query_spec_json = Column(JSON, nullable=True)
    response_data_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnomalyRecord(Base):
    __tablename__ = "anomaly_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    module = Column(String(100), nullable=False, index=True) # ATTENDANCE, PAYROLL, EXPENSE, LOCATION
    severity = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    anomaly_score = Column(Float, nullable=False, default=0.85)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(String(36), nullable=True, index=True)
    review_status = Column(String(50), default="NEW") # NEW, UNDER_REVIEW, CONFIRMED, FALSE_POSITIVE, RESOLVED
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkforceForecastRun(Base):
    __tablename__ = "workforce_forecast_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    forecast_type = Column(String(100), nullable=False) # HEADCOUNT, ATTRITION, PAYROLL_COST, OVERTIME
    horizon_days = Column(Integer, default=90) # 30, 60, 90, 180, 365
    forecast_results_json = Column(JSON, nullable=False)
    accuracy_score = Column(Float, default=0.92)
    run_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScenarioModel(Base):
    __tablename__ = "scenario_models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    scenario_name = Column(String(255), nullable=False)
    input_parameters_json = Column(JSON, nullable=False)
    projected_results_json = Column(JSON, nullable=False)
    created_by_id = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    issue_type = Column(String(100), nullable=False) # ORPHAN_RECORD, MISSING_MANAGER, INCOMPLETE_STATUTORY, SALARY_MISMATCH
    severity = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    affected_entity_type = Column(String(100), nullable=False)
    affected_entity_id = Column(String(36), nullable=False)
    is_resolved = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
