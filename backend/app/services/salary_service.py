from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payroll import (
    SalaryComponent,
    SalaryStructure,
    SalaryStructureComponent,
    EmployeeSalaryAssignment,
    ComponentType,
    CalculationType,
    SalaryAssignmentStatus,
)
from app.schemas.payroll import (
    SalaryComponentCreate,
    SalaryStructureCreate,
    EmployeeSalaryAssignmentCreate,
)


class SalaryService:

    @staticmethod
    async def seed_default_components(db: AsyncSession, tenant_id: UUID) -> List[SalaryComponent]:
        res = await db.execute(
            select(SalaryComponent).where(SalaryComponent.tenant_id == tenant_id)
        )
        existing = list(res.scalars().all())
        if existing:
            return existing

        defaults = [
            {
                "code": "BASIC",
                "name": "Basic Salary",
                "description": "Primary base earnings component (typically 50% of Gross)",
                "component_type": ComponentType.EARNING,
                "calculation_type": CalculationType.FIXED,
                "taxable": True,
                "included_in_ctc": True,
                "affects_gross": True,
                "affects_net": True,
            },
            {
                "code": "HRA",
                "name": "House Rent Allowance (HRA)",
                "description": "Housing allowance (40-50% of Basic)",
                "component_type": ComponentType.EARNING,
                "calculation_type": CalculationType.FORMULA,
                "formula": "BASIC * 0.40",
                "taxable": True,
                "included_in_ctc": True,
                "affects_gross": True,
                "affects_net": True,
            },
            {
                "code": "SPECIAL_ALLOWANCE",
                "name": "Special Allowance",
                "description": "Flexible balancing earnings component",
                "component_type": ComponentType.EARNING,
                "calculation_type": CalculationType.FIXED,
                "taxable": True,
                "included_in_ctc": True,
                "affects_gross": True,
                "affects_net": True,
            },
            {
                "code": "CONVEYANCE",
                "name": "Conveyance Allowance",
                "description": "Travel and commute allowance",
                "component_type": ComponentType.EARNING,
                "calculation_type": CalculationType.FIXED,
                "fixed_amount": Decimal("1600.00"),
                "taxable": True,
                "included_in_ctc": True,
                "affects_gross": True,
                "affects_net": True,
            },
            {
                "code": "PF",
                "name": "Provident Fund (Employee)",
                "description": "Statutory employee PF deduction (12% of Basic)",
                "component_type": ComponentType.DEDUCTION,
                "calculation_type": CalculationType.FORMULA,
                "formula": "min(BASIC * 0.12, 1800)",
                "taxable": False,
                "included_in_ctc": False,
                "affects_gross": False,
                "affects_net": True,
            },
            {
                "code": "ESI",
                "name": "Employee State Insurance (ESI)",
                "description": "Statutory employee ESI deduction (0.75% of Gross)",
                "component_type": ComponentType.DEDUCTION,
                "calculation_type": CalculationType.FORMULA,
                "formula": "GROSS * 0.0075",
                "taxable": False,
                "included_in_ctc": False,
                "affects_gross": False,
                "affects_net": True,
            },
            {
                "code": "PT",
                "name": "Professional Tax (PT)",
                "description": "Statutory state professional tax deduction",
                "component_type": ComponentType.DEDUCTION,
                "calculation_type": CalculationType.FIXED,
                "fixed_amount": Decimal("200.00"),
                "taxable": False,
                "included_in_ctc": False,
                "affects_gross": False,
                "affects_net": True,
            },
            {
                "code": "TDS",
                "name": "Tax Deducted at Source (TDS)",
                "description": "Estimated income tax deduction",
                "component_type": ComponentType.TAX,
                "calculation_type": CalculationType.FIXED,
                "fixed_amount": Decimal("0.00"),
                "taxable": False,
                "included_in_ctc": False,
                "affects_gross": False,
                "affects_net": True,
            },
        ]

        created = []
        for item in defaults:
            comp = SalaryComponent(tenant_id=tenant_id, **item)
            db.add(comp)
            created.append(comp)

        await db.commit()
        for c in created:
            await db.refresh(c)
        return created

    @staticmethod
    async def get_components(db: AsyncSession, tenant_id: UUID) -> List[SalaryComponent]:
        res = await db.execute(
            select(SalaryComponent).where(SalaryComponent.tenant_id == tenant_id)
        )
        return list(res.scalars().all())

    @staticmethod
    async def create_component(db: AsyncSession, tenant_id: UUID, data: SalaryComponentCreate) -> SalaryComponent:
        comp = SalaryComponent(tenant_id=tenant_id, **data.model_dump())
        db.add(comp)
        await db.commit()
        await db.refresh(comp)
        return comp

    @staticmethod
    async def create_structure(db: AsyncSession, tenant_id: UUID, data: SalaryStructureCreate) -> SalaryStructure:
        struct = SalaryStructure(
            tenant_id=tenant_id,
            code=data.code,
            name=data.name,
            description=data.description,
            status="ACTIVE"
        )
        db.add(struct)
        await db.flush()

        for item in data.components:
            st_comp = SalaryStructureComponent(
                tenant_id=tenant_id,
                structure_id=struct.id,
                component_id=item.component_id,
                calculation_type=item.calculation_type,
                amount=Decimal(str(item.amount)) if item.amount is not None else None,
                percentage=Decimal(str(item.percentage)) if item.percentage is not None else None,
                formula=item.formula
            )
            db.add(st_comp)

        await db.commit()
        
        res = await db.execute(
            select(SalaryStructure)
            .options(selectinload(SalaryStructure.components))
            .where(SalaryStructure.id == struct.id)
        )
        return res.scalar_one()

    @staticmethod
    async def get_structures(db: AsyncSession, tenant_id: UUID) -> List[SalaryStructure]:
        res = await db.execute(
            select(SalaryStructure)
            .options(selectinload(SalaryStructure.components))
            .where(SalaryStructure.tenant_id == tenant_id)
        )
        return list(res.scalars().all())

    @staticmethod
    async def assign_employee_salary(db: AsyncSession, tenant_id: UUID, data: EmployeeSalaryAssignmentCreate) -> EmployeeSalaryAssignment:
        # Supersede existing active assignments
        res = await db.execute(
            select(EmployeeSalaryAssignment).where(
                EmployeeSalaryAssignment.tenant_id == tenant_id,
                EmployeeSalaryAssignment.employee_id == data.employee_id,
                EmployeeSalaryAssignment.status == SalaryAssignmentStatus.ACTIVE
            )
        )
        active_assignments = list(res.scalars().all())

        max_version = 0
        for assign in active_assignments:
            assign.status = SalaryAssignmentStatus.SUPERSEDED
            assign.effective_to = data.effective_from
            if assign.version > max_version:
                max_version = assign.version

        annual_ctc = Decimal(str(data.annual_ctc))
        monthly_ctc = (annual_ctc / Decimal("12.00")).quantize(Decimal("0.01"))
        gross_salary = monthly_ctc  # Base gross estimation

        new_assignment = EmployeeSalaryAssignment(
            tenant_id=tenant_id,
            employee_id=data.employee_id,
            salary_structure_id=data.salary_structure_id,
            annual_ctc=annual_ctc,
            monthly_ctc=monthly_ctc,
            gross_salary=gross_salary,
            effective_from=data.effective_from,
            version=max_version + 1,
            status=SalaryAssignmentStatus.ACTIVE
        )
        db.add(new_assignment)
        await db.commit()
        
        res = await db.execute(
            select(EmployeeSalaryAssignment)
            .options(selectinload(EmployeeSalaryAssignment.structure))
            .where(EmployeeSalaryAssignment.id == new_assignment.id)
        )
        return res.scalar_one()

    @staticmethod
    async def get_active_assignment(db: AsyncSession, tenant_id: UUID, employee_id: UUID, target_date: Optional[date] = None) -> Optional[EmployeeSalaryAssignment]:
        if target_date is None:
            target_date = date.today()

        res = await db.execute(
            select(EmployeeSalaryAssignment)
            .options(selectinload(EmployeeSalaryAssignment.structure))
            .where(
                EmployeeSalaryAssignment.tenant_id == tenant_id,
                EmployeeSalaryAssignment.employee_id == employee_id,
                EmployeeSalaryAssignment.effective_from <= target_date
            )
            .order_by(EmployeeSalaryAssignment.version.desc())
        )
        return res.scalars().first()
