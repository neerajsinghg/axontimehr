import uuid
import enum
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models import Base

class ChangeRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class HRRequestType(str, enum.Enum):
    EMPLOYMENT_CERTIFICATE = "EMPLOYMENT_CERTIFICATE"
    EXPERIENCE_LETTER = "EXPERIENCE_LETTER"
    SALARY_CERTIFICATE = "SALARY_CERTIFICATE"
    BANK_INFO_CHANGE = "BANK_INFO_CHANGE"
    DEPARTMENT_TRANSFER = "DEPARTMENT_TRANSFER"
    OTHER = "OTHER"

class HRRequestStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class TicketCategory(str, enum.Enum):
    PAYROLL = "PAYROLL"
    LEAVE = "LEAVE"
    ATTENDANCE = "ATTENDANCE"
    BENEFITS = "BENEFITS"
    DOCUMENTS = "DOCUMENTS"
    PROFILE = "PROFILE"
    IT_HR = "IT_HR"
    POLICY = "POLICY"
    OTHER = "OTHER"

class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_EMPLOYEE = "WAITING_FOR_EMPLOYEE"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class AnnouncementPriority(str, enum.Enum):
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    URGENT = "URGENT"

class AnnouncementTargetType(str, enum.Enum):
    ALL = "ALL"
    DEPARTMENT = "DEPARTMENT"
    BRANCH = "BRANCH"
    LOCATION = "LOCATION"
    DESIGNATION = "DESIGNATION"

class RecognitionType(str, enum.Enum):
    GREAT_WORK = "GREAT_WORK"
    TEAM_PLAYER = "TEAM_PLAYER"
    CUSTOMER_CHAMPION = "CUSTOMER_CHAMPION"
    INNOVATION = "INNOVATION"
    LEADERSHIP = "LEADERSHIP"

class ProfileChangeRequest(Base):
    __tablename__ = "ee_profile_change_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(Enum(ChangeRequestStatus), default=ChangeRequestStatus.PENDING, nullable=False, index=True)
    reviewed_by_id = Column(String(36), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class HRDocumentTemplate(Base):
    __tablename__ = "ee_document_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    template_code = Column(String(100), nullable=False, index=True)
    category = Column(String(50), default="GENERAL", nullable=False)
    template_body = Column(Text, nullable=False)
    variables_json = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class GeneratedHRLetter(Base):
    __tablename__ = "ee_generated_hr_letters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    template_id = Column(String(36), ForeignKey("ee_document_templates.id"), nullable=True)
    title = Column(String(200), nullable=False)
    letter_number = Column(String(100), nullable=False, unique=True)
    snapshot_html = Column(Text, nullable=False)
    file_url = Column(String(500), nullable=True)
    generated_by_id = Column(String(36), nullable=True)
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class HRPolicy(Base):
    __tablename__ = "ee_hr_policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(100), default="GENERAL", nullable=False)
    current_version = Column(String(20), default="1.0", nullable=False)
    policy_body = Column(Text, nullable=False)
    file_url = Column(String(500), nullable=True)
    is_mandatory_ack = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), onupdate=lambda: datetime.now(), nullable=False)

class PolicyAcknowledgement(Base):
    __tablename__ = "ee_policy_acknowledgements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id = Column(String(36), ForeignKey("ee_hr_policies.id"), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    employee_id = Column(String(36), nullable=False, index=True)
    acknowledged_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    ip_address = Column(String(50), nullable=True)

class HRRequest(Base):
    __tablename__ = "ee_hr_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    request_type = Column(Enum(HRRequestType), default=HRRequestType.EMPLOYMENT_CERTIFICATE, nullable=False)
    subject = Column(String(200), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(Enum(HRRequestStatus), default=HRRequestStatus.SUBMITTED, nullable=False, index=True)
    assigned_to_id = Column(String(36), nullable=True)
    expected_completion_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class HRHelpdeskTicket(Base):
    __tablename__ = "ee_helpdesk_tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    ticket_number = Column(String(100), nullable=False, unique=True)
    category = Column(Enum(TicketCategory), default=TicketCategory.IT_HR, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False, index=True)
    assigned_agent_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), onupdate=lambda: datetime.now(), nullable=False)

class HRHelpdeskComment(Base):
    __tablename__ = "ee_helpdesk_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("ee_helpdesk_tickets.id"), nullable=False, index=True)
    sender_id = Column(String(36), nullable=False)
    comment_text = Column(Text, nullable=False)
    attachment_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class CompanyAnnouncement(Base):
    __tablename__ = "ee_company_announcements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="GENERAL", nullable=False)
    priority = Column(Enum(AnnouncementPriority), default=AnnouncementPriority.NORMAL, nullable=False)
    target_type = Column(Enum(AnnouncementTargetType), default=AnnouncementTargetType.ALL, nullable=False)
    target_id = Column(String(36), nullable=True)
    publish_date = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    is_mandatory_ack = Column(Boolean, default=False, nullable=False)
    created_by_id = Column(String(36), nullable=True)
    status = Column(String(50), default="PUBLISHED", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)

class AnnouncementRead(Base):
    __tablename__ = "ee_announcement_reads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    announcement_id = Column(String(36), ForeignKey("ee_company_announcements.id"), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

class EmployeeRecognition(Base):
    __tablename__ = "ee_employee_recognitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    sender_id = Column(String(36), nullable=False)
    recipient_id = Column(String(36), nullable=False, index=True)
    recognition_type = Column(Enum(RecognitionType), default=RecognitionType.GREAT_WORK, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
