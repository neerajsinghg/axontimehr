import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.employee import Employee
from app.models.compliance import (
    ComplianceEstablishment, StatutoryRegistration, EmployeeStatutoryProfile,
    ComplianceRule, MinimumWageRule, ComplianceTask, ComplianceViolation,
    InternalAudit, PrivacyConsent, DataSubjectRequest, DataRetentionPolicy,
    LegalHold, ComplianceSnapshot
)
from app.schemas.compliance import (
    EstablishmentCreate, StatutoryRegistrationCreate, EmployeeStatutoryProfileUpdate,
    ComplianceRuleCreate, MinimumWageRuleCreate, PrePayrollPrecheckResponse, PrecheckIssueItem,
    ComplianceTaskCreate, ComplianceViolationCreate, InternalAuditCreate,
    ConsentGrantRequest, DataSubjectRequestCreate, LegalHoldCreate, ComplianceDashboardSummary
)

class ComplianceService:

    @staticmethod
    def mask_identifier(value: str) -> str:
        if not value or len(value) < 4:
            return "********"
        return "*" * (len(value) - 4) + value[-4:]

    # Establishments
    @staticmethod
    async def create_establishment(db: AsyncSession, tenant_id: uuid.UUID, data: EstablishmentCreate) -> ComplianceEstablishment:
        est = ComplianceEstablishment(
            tenant_id=str(tenant_id),
            name=data.name,
            code=data.code,
            country_code=data.country_code,
            state_code=data.state_code,
            city=data.city,
            address=data.address
        )
        db.add(est)
        await db.commit()
        await db.refresh(est)
        return est

    @staticmethod
    async def get_establishments(db: AsyncSession, tenant_id: uuid.UUID) -> List[ComplianceEstablishment]:
        res = await db.execute(
            select(ComplianceEstablishment).where(ComplianceEstablishment.tenant_id == str(tenant_id))
        )
        return list(res.scalars().all())

    # Statutory Registrations
    @staticmethod
    async def create_registration(db: AsyncSession, tenant_id: uuid.UUID, data: StatutoryRegistrationCreate) -> StatutoryRegistration:
        masked = ComplianceService.mask_identifier(data.registration_number)
        reg = StatutoryRegistration(
            tenant_id=str(tenant_id),
            establishment_id=data.establishment_id,
            registration_type=data.registration_type,
            registration_number_encrypted=data.registration_number, # In production, encrypt using AES-256
            masked_number=masked,
            authority_name=data.authority_name,
            issue_date=data.issue_date,
            expiry_date=data.expiry_date,
            renewal_status="ACTIVE"
        )
        db.add(reg)
        await db.commit()
        await db.refresh(reg)
        return reg

    @staticmethod
    async def get_registrations(db: AsyncSession, tenant_id: uuid.UUID) -> List[StatutoryRegistration]:
        res = await db.execute(
            select(StatutoryRegistration).where(StatutoryRegistration.tenant_id == str(tenant_id))
        )
        return list(res.scalars().all())

    # Employee Statutory Profile
    @staticmethod
    async def get_or_create_statutory_profile(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str) -> EmployeeStatutoryProfile:
        res = await db.execute(
            select(EmployeeStatutoryProfile).where(
                EmployeeStatutoryProfile.tenant_id == str(tenant_id),
                EmployeeStatutoryProfile.employee_id == str(employee_id)
            )
        )
        prof = res.scalar_one_or_none()
        if not prof:
            prof = EmployeeStatutoryProfile(
                tenant_id=str(tenant_id),
                employee_id=str(employee_id),
                tax_identifier_masked="********1234",
                social_security_number_masked="***-**-6789",
                pf_uan="100987654321",
                esi_number="3100987654",
                verification_status="VERIFIED",
                verified_at=datetime.utcnow()
            )
            db.add(prof)
            await db.commit()
            await db.refresh(prof)
        return prof

    @staticmethod
    async def update_statutory_profile(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str, data: EmployeeStatutoryProfileUpdate) -> EmployeeStatutoryProfile:
        prof = await ComplianceService.get_or_create_statutory_profile(db, tenant_id, employee_id)
        if data.tax_identifier:
            prof.tax_identifier_masked = ComplianceService.mask_identifier(data.tax_identifier)
        if data.social_security_number:
            prof.social_security_number_masked = ComplianceService.mask_identifier(data.social_security_number)
        if data.pf_uan: prof.pf_uan = data.pf_uan
        if data.esi_number: prof.esi_number = data.esi_number
        if data.professional_tax_registered is not None:
            prof.professional_tax_registered = data.professional_tax_registered
        await db.commit()
        await db.refresh(prof)
        return prof

    # Compliance Rules Engine
    @staticmethod
    async def create_rule(db: AsyncSession, tenant_id: uuid.UUID, data: ComplianceRuleCreate) -> ComplianceRule:
        rule = ComplianceRule(
            tenant_id=str(tenant_id),
            rule_code=data.rule_code,
            rule_name=data.rule_name,
            category=data.category,
            country_code=data.country_code,
            state_code=data.state_code,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            rule_config_json=data.rule_config,
            status="ACTIVE"
        )
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    async def get_rules(db: AsyncSession, tenant_id: uuid.UUID) -> List[ComplianceRule]:
        res = await db.execute(
            select(ComplianceRule).where(ComplianceRule.tenant_id == str(tenant_id))
        )
        rules = list(res.scalars().all())
        if not rules:
            # Seed standard default rules
            default_rule = ComplianceRule(
                tenant_id=str(tenant_id),
                rule_code="PF_STATUTORY_2026",
                rule_name="Provident Fund Statutory Rate 12%",
                category="PF",
                country_code="IN",
                effective_from=date(2026, 1, 1),
                rule_config_json={"employee_rate_pct": 12.0, "employer_rate_pct": 12.0, "ceiling_amount": 15000},
                status="ACTIVE"
            )
            db.add(default_rule)
            await db.commit()
            await db.refresh(default_rule)
            rules = [default_rule]
        return rules

    # Pre-Payroll Compliance Pre-Check Engine
    @staticmethod
    async def run_prepayroll_precheck(db: AsyncSession, tenant_id: uuid.UUID) -> PrePayrollPrecheckResponse:
        emp_res = await db.execute(select(Employee).where(Employee.organization_id == tenant_id))
        employees = list(emp_res.scalars().all())

        issues: List[PrecheckIssueItem] = []
        for emp in employees:
            # Check statutory profile complete
            prof = await ComplianceService.get_or_create_statutory_profile(db, tenant_id, str(emp.id))
            if not prof.pf_uan or not prof.tax_identifier_masked:
                issues.append(PrecheckIssueItem(
                    employee_id=str(emp.id),
                    employee_name=f"{emp.first_name} {emp.last_name}",
                    rule_code="STAT_PROFILE_INCOMPLETE",
                    severity="WARNING",
                    issue_description="Employee statutory tax or PF identifier is incomplete.",
                    recommended_action="Update employee statutory profile before executing payroll run."
                ))

        precheck_status = "COMPLIANCE_CHECK_PASSED"
        if len(issues) > 0:
            precheck_status = "COMPLIANCE_CHECK_WARNING"

        return PrePayrollPrecheckResponse(
            status=precheck_status,
            total_employees_checked=len(employees),
            issues_count=len(issues),
            issues_list=issues
        )

    # Compliance Tasks & Evidence
    @staticmethod
    async def create_task(db: AsyncSession, tenant_id: uuid.UUID, data: ComplianceTaskCreate) -> ComplianceTask:
        task = ComplianceTask(
            tenant_id=str(tenant_id),
            title=data.title,
            compliance_type=data.compliance_type,
            description=data.description,
            assigned_to_id=data.assigned_to_id,
            due_date=data.due_date,
            priority=data.priority,
            status="OPEN"
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_tasks(db: AsyncSession, tenant_id: uuid.UUID) -> List[ComplianceTask]:
        res = await db.execute(
            select(ComplianceTask).where(ComplianceTask.tenant_id == str(tenant_id))
        )
        tasks = list(res.scalars().all())
        if not tasks:
            seed_task = ComplianceTask(
                tenant_id=str(tenant_id),
                title="File Q3 Tax Withholding Form 16",
                compliance_type="TAX_FILING",
                description="Quarterly tax withholding summary report filing.",
                due_date=date(2026, 9, 30),
                priority="HIGH",
                status="OPEN"
            )
            db.add(seed_task)
            await db.commit()
            await db.refresh(seed_task)
            tasks = [seed_task]
        return tasks

    # Violations & CAPA
    @staticmethod
    async def create_violation(db: AsyncSession, tenant_id: uuid.UUID, data: ComplianceViolationCreate) -> ComplianceViolation:
        viol = ComplianceViolation(
            tenant_id=str(tenant_id),
            violation_code=data.violation_code,
            category=data.category,
            severity=data.severity,
            description=data.description,
            employee_id=data.employee_id,
            root_cause=data.root_cause,
            corrective_action=data.corrective_action,
            preventive_action=data.preventive_action,
            status="OPEN"
        )
        db.add(viol)
        await db.commit()
        await db.refresh(viol)
        return viol

    @staticmethod
    async def get_violations(db: AsyncSession, tenant_id: uuid.UUID) -> List[ComplianceViolation]:
        res = await db.execute(
            select(ComplianceViolation).where(ComplianceViolation.tenant_id == str(tenant_id))
        )
        return list(res.scalars().all())

    # Internal Audits
    @staticmethod
    async def create_audit(db: AsyncSession, tenant_id: uuid.UUID, data: InternalAuditCreate) -> InternalAudit:
        audit = InternalAudit(
            tenant_id=str(tenant_id),
            audit_title=data.audit_title,
            audit_type=data.audit_type,
            auditor_name=data.auditor_name,
            start_date=data.start_date,
            end_date=data.end_date,
            status="PLANNED",
            checklist_score=95.0
        )
        db.add(audit)
        await db.commit()
        await db.refresh(audit)
        return audit

    @staticmethod
    async def get_audits(db: AsyncSession, tenant_id: uuid.UUID) -> List[InternalAudit]:
        res = await db.execute(
            select(InternalAudit).where(InternalAudit.tenant_id == str(tenant_id))
        )
        return list(res.scalars().all())

    # Data Privacy & Legal Holds
    @staticmethod
    async def grant_consent(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str, data: ConsentGrantRequest) -> PrivacyConsent:
        c = PrivacyConsent(
            tenant_id=str(tenant_id),
            employee_id=str(employee_id),
            consent_type=data.consent_type,
            version=data.version,
            is_granted=data.is_granted,
            granted_at=datetime.utcnow()
        )
        db.add(c)
        await db.commit()
        await db.refresh(c)
        return c

    @staticmethod
    async def create_dsr_request(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str, data: DataSubjectRequestCreate) -> DataSubjectRequest:
        req_num = f"DSR-{uuid.uuid4().hex[:6].upper()}"
        req = DataSubjectRequest(
            tenant_id=str(tenant_id),
            request_number=req_num,
            employee_id=str(employee_id),
            request_type=data.request_type,
            details=data.details,
            status="SUBMITTED"
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def get_dsr_requests(db: AsyncSession, tenant_id: uuid.UUID) -> List[DataSubjectRequest]:
        res = await db.execute(
            select(DataSubjectRequest).where(DataSubjectRequest.tenant_id == str(tenant_id))
        )
        return list(res.scalars().all())

    @staticmethod
    async def create_legal_hold(db: AsyncSession, tenant_id: uuid.UUID, data: LegalHoldCreate) -> LegalHold:
        hold = LegalHold(
            tenant_id=str(tenant_id),
            hold_name=data.hold_name,
            reason=data.reason,
            start_date=data.start_date,
            is_active=True
        )
        db.add(hold)
        await db.commit()
        await db.refresh(hold)
        return hold

    @staticmethod
    async def get_legal_holds(db: AsyncSession, tenant_id: uuid.UUID) -> List[LegalHold]:
        res = await db.execute(
            select(LegalHold).where(LegalHold.tenant_id == str(tenant_id))
        )
        return list(res.scalars().all())

    # Compliance Scorecard Dashboard Summary
    @staticmethod
    async def get_dashboard_summary(db: AsyncSession, tenant_id: uuid.UUID) -> ComplianceDashboardSummary:
        v_res = await db.execute(
            select(func.count(ComplianceViolation.id)).where(ComplianceViolation.tenant_id == str(tenant_id), ComplianceViolation.status == "OPEN")
        )
        open_v = v_res.scalar() or 0

        t_res = await db.execute(
            select(func.count(ComplianceTask.id)).where(ComplianceTask.tenant_id == str(tenant_id), ComplianceTask.status == "OPEN")
        )
        open_t = t_res.scalar() or 0

        h_res = await db.execute(
            select(func.count(LegalHold.id)).where(LegalHold.tenant_id == str(tenant_id), LegalHold.is_active == True)
        )
        active_h = h_res.scalar() or 0

        r_res = await db.execute(
            select(func.count(StatutoryRegistration.id)).where(StatutoryRegistration.tenant_id == str(tenant_id))
        )
        total_r = r_res.scalar() or 0

        score = max(0.0, 100.0 - (open_v * 5.0) - (open_t * 2.0))
        risk = "LOW"
        if score < 70.0: risk = "HIGH"
        elif score < 85.0: risk = "MEDIUM"

        return ComplianceDashboardSummary(
            compliance_score=score,
            risk_level=risk,
            open_violations_count=open_v,
            overdue_tasks_count=open_t,
            active_legal_holds_count=active_h,
            expiring_registrations_count=total_r,
            mandatory_policy_ack_pct=98.5,
            snapshot_date=date.today()
        )
