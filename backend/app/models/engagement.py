import enum
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Text,
    Integer,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class SurveyType(str, enum.Enum):
    PULSE = "PULSE"
    ENPS = "ENPS"
    ONBOARDING = "ONBOARDING"
    EXIT = "EXIT"
    CUSTOM = "CUSTOM"


class QuestionType(str, enum.Enum):
    RATING_1_5 = "RATING_1_5"
    NPS_0_10 = "NPS_0_10"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"


class Survey(Base):
    __tablename__ = "engagement_surveys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    survey_type = Column(SQLEnum(SurveyType), default=SurveyType.PULSE, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_anonymous = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    questions = relationship("SurveyQuestion", back_populates="survey", cascade="all, delete-orphan")
    responses = relationship("SurveyResponse", back_populates="survey", cascade="all, delete-orphan")


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    survey_id = Column(String(36), ForeignKey("engagement_surveys.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(SQLEnum(QuestionType), default=QuestionType.RATING_1_5, nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=1, nullable=False)

    survey = relationship("Survey", back_populates="questions")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    survey_id = Column(String(36), ForeignKey("engagement_surveys.id"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("survey_questions.id"), nullable=False, index=True)
    employee_id = Column(String(36), nullable=True, index=True)  # Null if anonymous
    rating_value = Column(Integer, nullable=True)
    text_value = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    survey = relationship("Survey", back_populates="responses")


class EmployeeFeedback(Base):
    __tablename__ = "employee_feedbacks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=True, index=True)  # Null if anonymous
    category = Column(String(100), default="WORKPLACE", nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="SUBMITTED", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
