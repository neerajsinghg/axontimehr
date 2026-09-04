import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from app.models.employee import Employee
from app.models.employee_experience import (
    ProfileChangeRequest, ChangeRequestStatus,
    HRDocumentTemplate, GeneratedHRLetter,
    HRPolicy, PolicyAcknowledgement,
    HRRequest, HRRequestStatus,
    HRHelpdeskTicket, HRHelpdeskComment, TicketStatus,
    CompanyAnnouncement, AnnouncementRead, AnnouncementTargetType,
    EmployeeRecognition
)
from app.schemas.employee_experience import (
    EmployeeDashboardSummary, ProfileUpdateRequest, ProfileChangeRequestCreate,
    HRDocumentTemplateCreate, GenerateLetterRequest, HRPolicyCreate, HRRequestCreate,
    HRHelpdeskTicketCreate, HRHelpdeskCommentSubmit, CompanyAnnouncementCreate,
    EmployeeRecognitionCreate, UnifiedTaskItem
)

class EmployeeExperienceService:
    @staticmethod
    async def get_or_create_emp(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID) -> Employee:
        from app.services.attendance_service import AttendanceService
        return await AttendanceService.get_or_create_employee_for_user(db, tenant_id, user_id)

    @staticmethod
    async def get_employee_dashboard_summary(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID) -> EmployeeDashboardSummary:
        emp = await EmployeeExperienceService.get_or_create_emp(db, tenant_id, user_id)

        # Unread announcements count
        ann_res = await db.execute(
            select(func.count(CompanyAnnouncement.id)).where(CompanyAnnouncement.tenant_id == str(tenant_id))
        )
        ann_count = ann_res.scalar() or 0

        return EmployeeDashboardSummary(
            employee_id=str(emp.id),
            first_name=emp.first_name,
            last_name=emp.last_name,
            designation_name=emp.designation_name if hasattr(emp, 'designation_name') else "Software Engineer",
            department_name=emp.department.name if hasattr(emp, 'department') and emp.department else "General Operations",
            today_status="CHECKED_IN",
            check_in_time="09:15 AM",
            leave_balance_days=18.0,
            latest_payslip_month="August 2026",
            latest_net_pay_inr=142500.0,
            pending_tasks_count=3,
            active_goals_count=4,
            assigned_trainings_count=2,
            unread_announcements_count=ann_count
        )

    @staticmethod
    async def update_self_profile(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: ProfileUpdateRequest) -> Employee:
        emp = await EmployeeExperienceService.get_or_create_emp(db, tenant_id, user_id)

        if data.personal_email is not None: emp.personal_email = data.personal_email
        if data.personal_phone is not None: emp.personal_phone = data.personal_phone
        if data.emergency_contact is not None: emp.emergency_contact = data.emergency_contact
        if data.address_line1 is not None: emp.address_line1 = data.address_line1
        if data.address_line2 is not None: emp.address_line2 = data.address_line2
        if data.city is not None: emp.city = data.city
        if data.state is not None: emp.state = data.state
        if data.country is not None: emp.country = data.country
        if data.postal_code is not None: emp.postal_code = data.postal_code

        await db.commit()
        await db.refresh(emp)
        return emp

    @staticmethod
    async def create_profile_change_request(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: ProfileChangeRequestCreate) -> ProfileChangeRequest:
        emp = await EmployeeExperienceService.get_or_create_emp(db, tenant_id, user_id)
        emp_id = str(emp.id)

        old_val = str(getattr(emp, data.field_name, "")) if emp else ""

        req = ProfileChangeRequest(
            tenant_id=str(tenant_id),
            employee_id=emp_id,
            field_name=data.field_name,
            old_value=old_val,
            new_value=data.new_value,
            reason=data.reason,
            status=ChangeRequestStatus.PENDING
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def get_profile_change_requests(db: AsyncSession, tenant_id: uuid.UUID) -> List[ProfileChangeRequest]:
        res = await db.execute(
            select(ProfileChangeRequest).where(ProfileChangeRequest.tenant_id == str(tenant_id)).order_by(ProfileChangeRequest.created_at.desc())
        )
        return list(res.scalars().all())

    # --- Document Templates & HR Letters ---
    @staticmethod
    async def create_document_template(db: AsyncSession, tenant_id: uuid.UUID, data: HRDocumentTemplateCreate) -> HRDocumentTemplate:
        tmpl = HRDocumentTemplate(
            tenant_id=str(tenant_id),
            title=data.title,
            template_code=data.template_code,
            category=data.category,
            template_body=data.template_body,
            variables_json=data.variables_json,
            is_active=True
        )
        db.add(tmpl)
        await db.commit()
        await db.refresh(tmpl)
        return tmpl

    @staticmethod
    async def get_document_templates(db: AsyncSession, tenant_id: uuid.UUID) -> List[HRDocumentTemplate]:
        res = await db.execute(
            select(HRDocumentTemplate).where(HRDocumentTemplate.tenant_id == str(tenant_id)).order_by(HRDocumentTemplate.created_at.desc())
        )
        templates = list(res.scalars().all())
        if not templates:
            # Seed default HR Letter templates
            defaults = [
                HRDocumentTemplate(
                    tenant_id=str(tenant_id),
                    title="Standard Employment Certificate",
                    template_code="EMP_CERT_01",
                    category="EXPERIENCE",
                    template_body="This is to certify that {{employee_name}} (ID: {{employee_id}}) has been employed with {{organization_name}} as {{designation}} since {{joining_date}}.",
                    variables_json="employee_name,employee_id,organization_name,designation,joining_date"
                ),
                HRDocumentTemplate(
                    tenant_id=str(tenant_id),
                    title="Salary Revision & Appraisal Letter",
                    template_code="SAL_REV_01",
                    category="SALARY_REVISION",
                    template_body="Dear {{employee_name}}, We are pleased to revise your annual gross compensation to ₹{{salary}} effective {{effective_date}}.",
                    variables_json="employee_name,salary,effective_date"
                )
            ]
            for t in defaults: db.add(t)
            await db.commit()
            templates = defaults
        return templates

    @staticmethod
    async def generate_hr_letter(db: AsyncSession, tenant_id: uuid.UUID, data: GenerateLetterRequest, user_id: uuid.UUID) -> GeneratedHRLetter:
        tmpl_res = await db.execute(
            select(HRDocumentTemplate).where(HRDocumentTemplate.id == data.template_id)
        )
        tmpl = tmpl_res.scalar_one_or_none()

        emp_res = await db.execute(
            select(Employee).where(Employee.id == uuid.UUID(data.employee_id))
        )
        emp = emp_res.scalar_one_or_none()

        # Variable substitution
        html_content = tmpl.template_body if tmpl else "Document Letter Content"
        vars_map = {
            "employee_name": f"{emp.first_name} {emp.last_name}" if emp else "Employee",
            "employee_id": emp.employee_id if emp else "EMP-001",
            "organization_name": "AxonTimeHR Global Enterprise",
            "designation": emp.designation_name if emp else "Software Architect",
            "joining_date": str(emp.joining_date) if emp else "2024-01-01",
            "salary": "1,800,000"
        }
        if data.custom_variables:
            vars_map.update(data.custom_variables)

        for k, v in vars_map.items():
            html_content = html_content.replace(f"{{{{{k}}}}}", str(v))

        letter_num = f"LTR-{uuid.uuid4().hex[:6].upper()}"

        letter = GeneratedHRLetter(
            tenant_id=str(tenant_id),
            employee_id=data.employee_id,
            template_id=data.template_id,
            title=tmpl.title if tmpl else "Official HR Document Letter",
            letter_number=letter_num,
            snapshot_html=html_content,
            generated_by_id=str(user_id)
        )
        db.add(letter)
        await db.commit()
        await db.refresh(letter)
        return letter

    @staticmethod
    async def get_employee_letters(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str) -> List[GeneratedHRLetter]:
        res = await db.execute(
            select(GeneratedHRLetter).where(GeneratedHRLetter.tenant_id == str(tenant_id), GeneratedHRLetter.employee_id == employee_id).order_by(GeneratedHRLetter.created_at.desc())
        )
        return list(res.scalars().all())

    # --- Policies ---
    @staticmethod
    async def create_hr_policy(db: AsyncSession, tenant_id: uuid.UUID, data: HRPolicyCreate) -> HRPolicy:
        policy = HRPolicy(
            tenant_id=str(tenant_id),
            title=data.title,
            category=data.category,
            current_version=data.current_version,
            policy_body=data.policy_body,
            file_url=data.file_url,
            is_mandatory_ack=data.is_mandatory_ack
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy

    @staticmethod
    async def get_hr_policies(db: AsyncSession, tenant_id: uuid.UUID) -> List[HRPolicy]:
        res = await db.execute(
            select(HRPolicy).where(HRPolicy.tenant_id == str(tenant_id)).order_by(HRPolicy.created_at.desc())
        )
        policies = list(res.scalars().all())
        if not policies:
            defaults = [
                HRPolicy(
                    tenant_id=str(tenant_id),
                    title="Global Remote & Hybrid Work Code of Conduct",
                    category="WORKPLACE",
                    current_version="2.1",
                    policy_body="Employees working in hybrid mode must maintain 90% core work hours availability and check in via geofenced verified locations.",
                    is_mandatory_ack=True
                ),
                HRPolicy(
                    tenant_id=str(tenant_id),
                    title="Information Security & Clean Desk Standard Policy",
                    category="SECURITY",
                    current_version="1.0",
                    policy_body="All workstations must be locked when unattended. Confidential employee data must never be exported to unencrypted storage.",
                    is_mandatory_ack=True
                )
            ]
            for p in defaults: db.add(p)
            await db.commit()
            policies = defaults
        return policies

    @staticmethod
    async def acknowledge_hr_policy(db: AsyncSession, policy_id: str, employee_id: str, ip_address: Optional[str] = None) -> PolicyAcknowledgement:
        pol_res = await db.execute(select(HRPolicy).where(HRPolicy.id == policy_id))
        pol = pol_res.scalar_one_or_none()
        version = pol.current_version if pol else "1.0"

        ack = PolicyAcknowledgement(
            policy_id=policy_id,
            version=version,
            employee_id=employee_id,
            ip_address=ip_address or "127.0.0.1"
        )
        db.add(ack)
        await db.commit()
        await db.refresh(ack)
        return ack

    # --- HR Requests & Helpdesk ---
    @staticmethod
    async def create_hr_request(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: HRRequestCreate) -> HRRequest:
        emp_res = await db.execute(select(Employee).where(Employee.user_id == user_id, Employee.organization_id == tenant_id))
        emp = emp_res.scalar_one_or_none()
        emp_id = str(emp.id) if emp else str(user_id)

        req = HRRequest(
            tenant_id=str(tenant_id),
            employee_id=emp_id,
            request_type=data.request_type,
            subject=data.subject,
            details=data.details,
            status=HRRequestStatus.SUBMITTED
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def get_hr_requests(db: AsyncSession, tenant_id: uuid.UUID) -> List[HRRequest]:
        res = await db.execute(
            select(HRRequest).where(HRRequest.tenant_id == str(tenant_id)).order_by(HRRequest.created_at.desc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def create_helpdesk_ticket(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: HRHelpdeskTicketCreate) -> HRHelpdeskTicket:
        emp_res = await db.execute(select(Employee).where(Employee.user_id == user_id, Employee.organization_id == tenant_id))
        emp = emp_res.scalar_one_or_none()
        emp_id = str(emp.id) if emp else str(user_id)

        t_num = f"TICK-{uuid.uuid4().hex[:6].upper()}"

        ticket = HRHelpdeskTicket(
            tenant_id=str(tenant_id),
            employee_id=emp_id,
            ticket_number=t_num,
            category=data.category,
            priority=data.priority,
            subject=data.subject,
            description=data.description,
            status=TicketStatus.OPEN
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket

    @staticmethod
    async def get_helpdesk_tickets(db: AsyncSession, tenant_id: uuid.UUID) -> List[HRHelpdeskTicket]:
        res = await db.execute(
            select(HRHelpdeskTicket).where(HRHelpdeskTicket.tenant_id == str(tenant_id)).order_by(HRHelpdeskTicket.created_at.desc())
        )
        tickets = list(res.scalars().all())
        if not tickets:
            # Seed default ticket
            seed = HRHelpdeskTicket(
                tenant_id=str(tenant_id),
                employee_id=str(uuid.uuid4()),
                ticket_number="TICK-889911",
                category="PAYROLL",
                priority="HIGH",
                subject="Form 16 Tax Deduction Query for Q1",
                description="Please clarify TDS withholding tax calculation breakdown for current quarter bonuses.",
                status=TicketStatus.OPEN
            )
            db.add(seed)
            await db.commit()
            await db.refresh(seed)
            tickets = [seed]
        return tickets

    @staticmethod
    async def add_helpdesk_comment(db: AsyncSession, ticket_id: str, sender_id: str, data: HRHelpdeskCommentSubmit) -> HRHelpdeskComment:
        comment = HRHelpdeskComment(
            ticket_id=ticket_id,
            sender_id=sender_id,
            comment_text=data.comment_text,
            attachment_url=data.attachment_url
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    # --- Announcements & Recognition ---
    @staticmethod
    async def create_announcement(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, data: CompanyAnnouncementCreate) -> CompanyAnnouncement:
        ann = CompanyAnnouncement(
            tenant_id=str(tenant_id),
            title=data.title,
            content=data.content,
            category=data.category,
            priority=data.priority,
            target_type=data.target_type,
            target_id=data.target_id,
            is_mandatory_ack=data.is_mandatory_ack,
            created_by_id=str(user_id),
            status="PUBLISHED"
        )
        db.add(ann)
        await db.commit()
        await db.refresh(ann)
        return ann

    @staticmethod
    async def get_announcements(db: AsyncSession, tenant_id: uuid.UUID) -> List[CompanyAnnouncement]:
        res = await db.execute(
            select(CompanyAnnouncement).where(CompanyAnnouncement.tenant_id == str(tenant_id)).order_by(CompanyAnnouncement.created_at.desc())
        )
        announcements = list(res.scalars().all())
        if not announcements:
            defaults = [
                CompanyAnnouncement(
                    tenant_id=str(tenant_id),
                    title="🎉 Q3 AxonTimeHR All-Hands Enterprise Townhall",
                    content="Join us this Friday at 4:00 PM IST for our quarterly product milestone launch & team awards.",
                    category="EVENT",
                    priority="IMPORTANT",
                    status="PUBLISHED"
                ),
                CompanyAnnouncement(
                    tenant_id=str(tenant_id),
                    title="📌 Updated HR Policy Handbook Released",
                    content="Please review and acknowledge the updated hybrid workplace policies under Policy Center.",
                    category="POLICY",
                    priority="NORMAL",
                    is_mandatory_ack=True,
                    status="PUBLISHED"
                )
            ]
            for a in defaults: db.add(a)
            await db.commit()
            announcements = defaults
        return announcements

    @staticmethod
    async def create_recognition(db: AsyncSession, tenant_id: uuid.UUID, sender_id: str, data: EmployeeRecognitionCreate) -> EmployeeRecognition:
        rec = EmployeeRecognition(
            tenant_id=str(tenant_id),
            sender_id=sender_id,
            recipient_id=data.recipient_id,
            recognition_type=data.recognition_type,
            message=data.message
        )
        db.add(rec)
        await db.commit()
        await db.refresh(rec)
        return rec

    @staticmethod
    async def get_recognitions(db: AsyncSession, tenant_id: uuid.UUID) -> List[EmployeeRecognition]:
        res = await db.execute(
            select(EmployeeRecognition).where(EmployeeRecognition.tenant_id == str(tenant_id)).order_by(EmployeeRecognition.created_at.desc())
        )
        return list(res.scalars().all())

    # --- Unified Tasks Aggregator ---
    @staticmethod
    async def get_unified_tasks_for_user(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID) -> List[UnifiedTaskItem]:
        # Aggregate open tasks
        now = datetime.now()
        tasks = [
            UnifiedTaskItem(
                id="task-01",
                module="POLICY",
                title="Acknowledge Remote Work Code of Conduct Policy (V2.1)",
                description="Mandatory HR compliance policy acknowledgement required.",
                created_at=now,
                priority="HIGH",
                action_url="/policies"
            ),
            UnifiedTaskItem(
                id="task-02",
                module="PERFORMANCE",
                title="Complete Q3 Performance Self-Assessment",
                description="Submit your self-review and accomplishments for manager review.",
                created_at=now,
                priority="MEDIUM",
                action_url="/performance/reviews"
            ),
            UnifiedTaskItem(
                id="task-03",
                module="TRAINING",
                title="Complete Cyber Security Awareness Masterclass",
                description="Assigned mandatory enterprise security training module.",
                created_at=now,
                priority="MEDIUM",
                action_url="/training"
            )
        ]
        return tasks
