import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, String, Boolean, Float, DateTime, Date, Text, JSON, Integer
from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class ComplianceEstablishment(Base):
    __tablename__ = "compliance_establishments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, index=True)
    country_code = Column(String(10), nullable=False, default="IN")
    state_code = Column(String(50), nullable=False, default="KA")
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StatutoryRegistration(Base):
    __tablename__ = "statutory_registrations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    establishment_id = Column(String(36), nullable=True, index=True)
    registration_type = Column(String(100), nullable=False) # TAX_ID, PF_CODE, ESI_CODE, PT_REG, LABOR_PERMIT
    registration_number_encrypted = Column(Text, nullable=False)
    masked_number = Column(String(50), nullable=False) # e.g. ********1234
    authority_name = Column(String(255), nullable=False)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)
    renewal_status = Column(String(50), default="ACTIVE") # ACTIVE, RENEWAL_DUE, EXPIRED
    responsible_person_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmployeeStatutoryProfile(Base):
    __tablename__ = "employee_statutory_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    tax_identifier_masked = Column(String(50), nullable=True) # e.g. ********1234
    social_security_number_masked = Column(String(50), nullable=True) # e.g. ***-**-6789
    pf_uan = Column(String(50), nullable=True)
    esi_number = Column(String(50), nullable=True)
    professional_tax_registered = Column(Boolean, default=True)
    verification_status = Column(String(50), default="VERIFIED") # PENDING, VERIFIED, REJECTED
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    rule_code = Column(String(100), nullable=False, index=True)
    rule_name = Column(String(255), nullable=False)
    version = Column(Integer, default=1)
    category = Column(String(100), nullable=False) # TAX, PF, ESI, MINIMUM_WAGE, OVERTIME, WORKING_HOURS
    country_code = Column(String(10), default="IN")
    state_code = Column(String(50), default="ALL")
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    rule_config_json = Column(JSON, nullable=False)
    status = Column(String(50), default="ACTIVE") # DRAFT, PENDING_APPROVAL, ACTIVE, SUPERSEDED
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MinimumWageRule(Base):
    __tablename__ = "minimum_wage_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    country_code = Column(String(10), nullable=False, default="IN")
    state_code = Column(String(50), nullable=False, default="KA")
    skill_category = Column(String(100), nullable=False) # UNSKILLED, SEMI_SKILLED, SKILLED, HIGHLY_SKILLED
    min_basic_wage = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceTask(Base):
    __tablename__ = "compliance_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    compliance_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to_id = Column(String(36), nullable=True, index=True)
    reviewer_id = Column(String(36), nullable=True)
    due_date = Column(Date, nullable=False, index=True)
    priority = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), default="OPEN") # OPEN, IN_PROGRESS, PENDING_REVIEW, COMPLETED, OVERDUE
    evidence_file_url = Column(Text, nullable=True)
    completion_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ComplianceViolation(Base):
    __tablename__ = "compliance_violations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    violation_code = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    severity = Column(String(20), default="MEDIUM") # INFO, LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    employee_id = Column(String(36), nullable=True, index=True)
    establishment_id = Column(String(36), nullable=True)
    detected_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="OPEN") # OPEN, INVESTIGATING, ACTION_REQUIRED, RESOLVED, CLOSED
    root_cause = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    preventive_action = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class InternalAudit(Base):
    __tablename__ = "internal_audits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    audit_title = Column(String(255), nullable=False)
    audit_type = Column(String(100), nullable=False) # LABOUR_LAW, PAYROLL, PRIVACY, SAFETY
    auditor_name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), default="PLANNED") # PLANNED, IN_PROGRESS, COMPLETED, CLOSED
    checklist_score = Column(Float, default=100.0)
    findings_summary = Column(Text, nullable=True)
    findings_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PrivacyConsent(Base):
    __tablename__ = "privacy_consents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    consent_type = Column(String(100), nullable=False) # DATA_PROCESSING, BIOMETRIC, MARKETING
    version = Column(String(20), default="v1.0")
    is_granted = Column(Boolean, default=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    withdrawn_at = Column(DateTime, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataSubjectRequest(Base):
    __tablename__ = "data_subject_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    request_number = Column(String(50), nullable=False, unique=True)
    employee_id = Column(String(36), nullable=False, index=True)
    request_type = Column(String(50), nullable=False) # DATA_ACCESS, DATA_CORRECTION, DATA_EXPORT, DATA_DELETION
    status = Column(String(50), default="SUBMITTED") # SUBMITTED, UNDER_REVIEW, APPROVED, PROCESSING, COMPLETED
    details = Column(Text, nullable=True)
    response_summary = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class DataRetentionPolicy(Base):
    __tablename__ = "data_retention_policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    data_category = Column(String(100), nullable=False) # PAYROLL_RECORDS, ATTENDANCE_LOGS, CANDIDATE_CV
    retention_months = Column(Integer, nullable=False, default=84) # e.g. 7 years
    requires_legal_approval = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LegalHold(Base):
    __tablename__ = "legal_holds"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    hold_name = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    release_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceSnapshot(Base):
    __tablename__ = "compliance_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=False, index=True)
    snapshot_date = Column(Date, nullable=False, index=True)
    compliance_score = Column(Float, nullable=False, default=100.0)
    open_violations_count = Column(Integer, default=0)
    overdue_tasks_count = Column(Integer, default=0)
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow)
