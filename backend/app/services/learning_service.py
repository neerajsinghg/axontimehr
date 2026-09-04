import uuid
from typing import List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.learning import Course, TrainingEnrollment, EmployeeCertification, EmployeeSkill, EnrollmentStatus, CertificationStatus
from app.schemas.performance import CourseCreate, TrainingEnrollmentCreate, CertificationCreate, SkillUpdate


class LearningService:
    @staticmethod
    async def create_course(db: AsyncSession, tenant_id: uuid.UUID, data: CourseCreate) -> Course:
        course = Course(
            tenant_id=str(tenant_id),
            title=data.title,
            description=data.description,
            category=data.category,
            provider=data.provider,
            mode=data.mode,
            duration_hours=data.duration_hours,
            cost=data.cost,
            capacity=data.capacity,
            course_url=data.course_url,
        )
        db.add(course)
        await db.commit()
        await db.refresh(course)
        return course

    @staticmethod
    async def get_courses(db: AsyncSession, tenant_id: uuid.UUID) -> List[Course]:
        res = await db.execute(
            select(Course).where(Course.tenant_id == str(tenant_id)).order_by(Course.title)
        )
        courses = list(res.scalars().all())
        if not courses:
            # Seed standard default training courses
            defaults = [
                Course(
                    tenant_id=str(tenant_id),
                    title="Enterprise Cybersecurity & Data Privacy Standards",
                    description="Mandatory compliance course on SOC2, ISO27001, and workplace security best practices",
                    category="COMPLIANCE",
                    provider="INTERNAL",
                    mode="ONLINE",
                    duration_hours=4,
                    course_url="https://coursera.org/learn/cybersecurity-roles-processes-operating-system-security",
                ),
                Course(
                    tenant_id=str(tenant_id),
                    title="Agile Leadership & Cross-Functional Collaboration",
                    description="Professional workshop on team alignment, sprint execution, and managerial communication",
                    category="LEADERSHIP",
                    provider="HARVARD_EXECUTIVE",
                    mode="HYBRID",
                    duration_hours=16,
                    course_url="https://www.edx.org/learn/agile",
                ),
                Course(
                    tenant_id=str(tenant_id),
                    title="Full-Stack System Architecture & Cloud Microservices",
                    description="Hands-on technical boot camp covering scalable backend design and cloud infrastructure",
                    category="TECHNICAL",
                    provider="UDEMY_BUSINESS",
                    mode="SELF_PACED",
                    duration_hours=40,
                    course_url="https://aws.amazon.com/training/",
                )
            ]
            for c in defaults:
                db.add(c)
            await db.commit()

            res_new = await db.execute(
                select(Course).where(Course.tenant_id == str(tenant_id)).order_by(Course.title)
            )
            courses = list(res_new.scalars().all())

        return courses

    @staticmethod
    async def get_enrollments(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str) -> List[TrainingEnrollment]:
        res = await db.execute(
            select(TrainingEnrollment).where(
                TrainingEnrollment.tenant_id == str(tenant_id),
                TrainingEnrollment.employee_id == employee_id,
            )
        )
        return list(res.scalars().all())

    @staticmethod
    async def enroll_employee(db: AsyncSession, tenant_id: uuid.UUID, data: TrainingEnrollmentCreate) -> TrainingEnrollment:
        enrollment = TrainingEnrollment(
            tenant_id=str(tenant_id),
            course_id=data.course_id,
            employee_id=data.employee_id,
            status=EnrollmentStatus.ENROLLED,
        )
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def create_certification(db: AsyncSession, tenant_id: uuid.UUID, data: CertificationCreate) -> EmployeeCertification:
        cert = EmployeeCertification(
            tenant_id=str(tenant_id),
            employee_id=data.employee_id,
            name=data.name,
            issuing_organization=data.issuing_organization,
            issue_date=data.issue_date,
            expiry_date=data.expiry_date,
            credential_id=data.credential_id,
            status=CertificationStatus.ACTIVE,
        )
        db.add(cert)
        await db.commit()
        await db.refresh(cert)
        return cert

    @staticmethod
    async def get_certifications(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str) -> List[EmployeeCertification]:
        res = await db.execute(
            select(EmployeeCertification).where(
                EmployeeCertification.tenant_id == str(tenant_id),
                EmployeeCertification.employee_id == employee_id,
            )
        )
        return list(res.scalars().all())

    @staticmethod
    async def update_skill(db: AsyncSession, tenant_id: uuid.UUID, data: SkillUpdate) -> EmployeeSkill:
        gap = max(0, data.target_level - data.current_level)
        res = await db.execute(
            select(EmployeeSkill).where(
                EmployeeSkill.tenant_id == str(tenant_id),
                EmployeeSkill.employee_id == data.employee_id,
                EmployeeSkill.skill_name == data.skill_name,
            )
        )
        skill = res.scalar_one_or_none()
        if not skill:
            skill = EmployeeSkill(
                tenant_id=str(tenant_id),
                employee_id=data.employee_id,
                skill_name=data.skill_name,
                category=data.category,
                current_level=data.current_level,
                target_level=data.target_level,
                skill_gap=gap,
            )
            db.add(skill)
        else:
            skill.current_level = data.current_level
            skill.target_level = data.target_level
            skill.skill_gap = gap

        await db.commit()
        await db.refresh(skill)
        return skill

    @staticmethod
    async def get_skills_matrix(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str) -> List[EmployeeSkill]:
        res = await db.execute(
            select(EmployeeSkill).where(
                EmployeeSkill.tenant_id == str(tenant_id),
                EmployeeSkill.employee_id == employee_id,
            )
        )
        skills = list(res.scalars().all())
        if not skills:
            # Seed default skills for matrix demo
            defaults = [
                EmployeeSkill(tenant_id=str(tenant_id), employee_id=employee_id, skill_name="Python / FastAPI Backend", category="TECHNICAL", current_level=3, target_level=5, skill_gap=2),
                EmployeeSkill(tenant_id=str(tenant_id), employee_id=employee_id, skill_name="React / TypeScript Frontend", category="TECHNICAL", current_level=4, target_level=5, skill_gap=1),
                EmployeeSkill(tenant_id=str(tenant_id), employee_id=employee_id, skill_name="Agile Team Management", category="LEADERSHIP", current_level=2, target_level=4, skill_gap=2),
            ]
            for s in defaults:
                db.add(s)
            await db.commit()

            res_new = await db.execute(
                select(EmployeeSkill).where(
                    EmployeeSkill.tenant_id == str(tenant_id),
                    EmployeeSkill.employee_id == employee_id,
                )
            )
            skills = list(res_new.scalars().all())

        return skills
