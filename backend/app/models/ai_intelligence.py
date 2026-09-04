import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean
from app.models import Base

class AIQueryAudit(Base):
    __tablename__ = "ai_query_audits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    response_summary = Column(Text, nullable=True)
    tools_invoked = Column(String(500), nullable=True)
    token_count = Column(Integer, default=0, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    provider = Column(String(50), default="MOCK_PROVIDER", nullable=False)
    model_name = Column(String(100), default="axon-hr-ai-v1", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class AIUsageQuota(Base):
    __tablename__ = "ai_usage_quotas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    month_year = Column(String(20), nullable=False, index=True)
    monthly_token_limit = Column(Integer, default=100000, nullable=False)
    tokens_used_this_month = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), onupdate=lambda: datetime.now(), nullable=False)

class AIPromptVersion(Base):
    __tablename__ = "ai_prompt_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_key = Column(String(100), nullable=False, index=True)
    template_text = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
