from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# Establishments
class EstablishmentBase(BaseModel):
    name: str = Field(..., example="Bengaluru Tech Park Establishment")
    code: str = Field(..., example="EST-BLR-01")
    country_code: str = Field("IN", example="IN")
    state_code: str = Field("KA", example="KA")
    city: Optional[str] = Field("Bengaluru", example="Bengaluru")
    address: Optional[str] = Field(None, example="Outer Ring Road, Marathahalli")

class EstablishmentCreate(EstablishmentBase):
    pass

class EstablishmentResponse(EstablishmentBase):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Statutory Registrations
class StatutoryRegistrationBase(BaseModel):
    establishment_id: Optional[str] = None
    registration_type: str = Field(..., example="TAX_ID") # TAX_ID, PF_CODE, ESI_CODE, PT_REG, LABOR_PERMIT
    registration_number: str = Field(..., example="AAACX1234K")
    authority_name: str = Field(..., example="Income Tax Department India")
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None

class StatutoryRegistrationCreate(StatutoryRegistrationBase):
    pass

class StatutoryRegistrationResponse(BaseModel):
    id: str
    tenant_id: str
    establishment_id: Optional[str]
    registration_type: str
    masked_number: str
    authority_name: str
    issue_date: Optional[date]
    expiry_date: Optional[date]
    renewal_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Employee Statutory Profiles
class EmployeeStatutoryProfileUpdate(BaseModel):
    tax_identifier: Optional[str] = None
    social_security_number: Optional[str] = None
    pf_uan: Optional[str] = None
    esi_number: Optional[str] = None
    professional_tax_registered: Optional[bool] = True

class EmployeeStatutoryProfileResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    tax_identifier_masked: Optional[str]
    social_security_number_masked: Optional[str]
    pf_uan: Optional[str]
    esi_number: Optional[str]
    professional_tax_registered: bool
    verification_status: str
    verified_at: Optional[datetime]

    class Config:
        from_attributes = True


# Compliance Rules
class ComplianceRuleCreate(BaseModel):
    rule_code: str = Field(..., example="PF_CONTRIBUTION_2026")
    rule_name: str = Field(..., example="Provident Fund Statutory Rate 12%")
    category: str = Field(..., example="PF") # TAX, PF, ESI, MINIMUM_WAGE, OVERTIME, WORKING_HOURS
    country_code: str = Field("IN", example="IN")
    state_code: str = Field("ALL", example="ALL")
    effective_from: date
    effective_to: Optional[date] = None
    rule_config: Dict[str, Any] = Field(default_factory=dict)

class ComplianceRuleResponse(BaseModel):
    id: str
    tenant_id: str
    rule_code: str
    rule_name: str
    version: int
    category: str
    country_code: str
    state_code: str
    effective_from: date
    effective_to: Optional[date]
    rule_config_json: Dict[str, Any]
    status: str
    is_active: bool

    class Config:
        from_attributes = True


# Minimum Wage Rules
class MinimumWageRuleCreate(BaseModel):
    country_code: str = "IN"
    state_code: str = "KA"
    skill_category: str = Field(..., example="SKILLED") # UNSKILLED, SEMI_SKILLED, SKILLED, HIGHLY_SKILLED
    min_basic_wage: float = Field(..., example="24000.0")
    currency: str = "INR"
    effective_from: date

class MinimumWageRuleResponse(BaseModel):
    id: str
    tenant_id: str
    country_code: str
    state_code: str
    skill_category: str
    min_basic_wage: float
    currency: str
    effective_from: date
    effective_to: Optional[date]
    is_active: bool

    class Config:
        from_attributes = True


# Compliance Precheck (Pre-Payroll Engine)
class PrecheckIssueItem(BaseModel):
    employee_id: str
    employee_name: str
    rule_code: str
    severity: str # WARNING, HIGH, CRITICAL
    issue_description: str
    recommended_action: str

class PrePayrollPrecheckResponse(BaseModel):
    status: str # COMPLIANCE_CHECK_PASSED, COMPLIANCE_CHECK_WARNING, COMPLIANCE_CHECK_FAILED
    total_employees_checked: int
    issues_count: int
    issues_list: List[PrecheckIssueItem]


# Compliance Tasks & Evidence
class ComplianceTaskCreate(BaseModel):
    title: str = Field(..., example="File Q3 Tax Withholding Form 16")
    compliance_type: str = Field(..., example="TAX_FILING")
    description: Optional[str] = None
    assigned_to_id: Optional[str] = None
    due_date: date
    priority: str = Field("MEDIUM", example="HIGH") # LOW, MEDIUM, HIGH, CRITICAL

class ComplianceTaskResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    compliance_type: str
    description: Optional[str]
    assigned_to_id: Optional[str]
    reviewer_id: Optional[str]
    due_date: date
    priority: str
    status: str
    evidence_file_url: Optional[str]
    completion_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# Violations & CAPA
class ComplianceViolationCreate(BaseModel):
    violation_code: str = Field(..., example="VIOL-MIN-WAGE-001")
    category: str = Field(..., example="MINIMUM_WAGE")
    severity: str = Field("HIGH", example="HIGH")
    description: str = Field(..., example="Employee gross compensation falls below statutory minimum wage threshold.")
    employee_id: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None

class ComplianceViolationResponse(BaseModel):
    id: str
    tenant_id: str
    violation_code: str
    category: str
    severity: str
    description: str
    employee_id: Optional[str]
    detected_date: datetime
    status: str
    root_cause: Optional[str]
    corrective_action: Optional[str]
    preventive_action: Optional[str]
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# Internal Audits
class InternalAuditCreate(BaseModel):
    audit_title: str = Field(..., example="Annual ISO 27001 & Labour Law Audit")
    audit_type: str = Field(..., example="LABOUR_LAW")
    auditor_name: str = Field(..., example="Enterprise External Auditor")
    start_date: date
    end_date: date

class InternalAuditResponse(BaseModel):
    id: str
    tenant_id: str
    audit_title: str
    audit_type: str
    auditor_name: str
    start_date: date
    end_date: date
    status: str
    checklist_score: float
    findings_summary: Optional[str]

    class Config:
        from_attributes = True


# Data Privacy & Legal Holds
class ConsentGrantRequest(BaseModel):
    consent_type: str = Field(..., example="DATA_PROCESSING")
    version: str = "v1.0"
    is_granted: bool = True

class PrivacyConsentResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    consent_type: str
    version: str
    is_granted: bool
    granted_at: datetime

    class Config:
        from_attributes = True


class DataSubjectRequestCreate(BaseModel):
    request_type: str = Field(..., example="DATA_ACCESS") # DATA_ACCESS, DATA_CORRECTION, DATA_EXPORT, DATA_DELETION
    details: Optional[str] = Field(None, example="Request copy of personal data logs.")

class DataSubjectRequestResponse(BaseModel):
    id: str
    tenant_id: str
    request_number: str
    employee_id: str
    request_type: str
    status: str
    details: Optional[str]
    response_summary: Optional[str]
    submitted_at: datetime

    class Config:
        from_attributes = True


class LegalHoldCreate(BaseModel):
    hold_name: str = Field(..., example="Q3 Pending Tax Investigation Hold")
    reason: str = Field(..., example="Preserve all financial and attendance records for ongoing tax review.")
    start_date: date

class LegalHoldResponse(BaseModel):
    id: str
    tenant_id: str
    hold_name: str
    reason: str
    start_date: date
    release_date: Optional[date]
    is_active: bool

    class Config:
        from_attributes = True


# Compliance Dashboard Scorecard
class ComplianceDashboardSummary(BaseModel):
    compliance_score: float
    risk_level: str
    open_violations_count: int
    overdue_tasks_count: int
    active_legal_holds_count: int
    expiring_registrations_count: int
    mandatory_policy_ack_pct: float
    snapshot_date: date
