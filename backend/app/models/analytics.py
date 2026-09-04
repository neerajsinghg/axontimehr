import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Numeric, Text
from app.models import Base

class AnalyticsMetricDefinition(Base):
    __tablename__ = "analytics_metric_definitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    metric_key = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), default="WORKFORCE", nullable=False)
    unit = Column(String(50), default="COUNT", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class AnalyticsMetricSnapshot(Base):
    __tablename__ = "analytics_metric_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    metric_key = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, default=0.0, nullable=False)
    dimensions_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class AttritionSnapshot(Base):
    __tablename__ = "analytics_attrition_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    department_id = Column(String(36), nullable=True)
    total_employees = Column(Integer, default=0, nullable=False)
    exits_count = Column(Integer, default=0, nullable=False)
    attrition_rate_pct = Column(Float, default=0.0, nullable=False)
    voluntary_count = Column(Integer, default=0, nullable=False)
    involuntary_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
