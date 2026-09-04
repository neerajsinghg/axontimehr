from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Company, Branch, Department, Designation
from app.schemas.organization import (
    CompanyCreate, CompanyUpdate,
    BranchCreate, BranchUpdate,
    DepartmentCreate, DepartmentUpdate,
    DesignationCreate, DesignationUpdate
)

class OrganizationService:
    # --- Company / Organization ---
    @staticmethod
    async def get_company(db: AsyncSession, company_id: UUID) -> Company:
        res = await db.execute(select(Company).where(Company.id == company_id))
        company = res.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        return company

    @staticmethod
    async def get_or_create_default_company(db: AsyncSession) -> Company:
        res = await db.execute(select(Company).limit(1))
        company = res.scalar_one_or_none()
        if not company:
            company = Company(
                name="AxonTime HR Corp",
                code="AXONTIME",
                legal_name="AxonTime HR Corp Inc.",
                display_name="AxonTime HR",
                timezone="UTC",
                currency="USD",
                status="ACTIVE",
                is_active=True
            )
            db.add(company)
            await db.commit()
            await db.refresh(company)
        return company

    @staticmethod
    async def update_company(db: AsyncSession, company_id: UUID, payload: CompanyUpdate) -> Company:
        company = await OrganizationService.get_company(db, company_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(company, key, val)
        await db.commit()
        await db.refresh(company)
        return company

    # --- Branch ---
    @staticmethod
    async def get_branches(db: AsyncSession, tenant_id: UUID) -> List[Branch]:
        res = await db.execute(select(Branch).where(Branch.organization_id == tenant_id).order_by(Branch.name.asc()))
        return list(res.scalars().all())

    @staticmethod
    async def get_branch(db: AsyncSession, tenant_id: UUID, branch_id: UUID) -> Branch:
        res = await db.execute(select(Branch).where(Branch.id == branch_id, Branch.organization_id == tenant_id))
        branch = res.scalar_one_or_none()
        if not branch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
        return branch

    @staticmethod
    async def create_branch(db: AsyncSession, tenant_id: UUID, payload: BranchCreate) -> Branch:
        # Check duplicate code within tenant
        dup = await db.execute(select(Branch).where(Branch.organization_id == tenant_id, Branch.code == payload.code))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Branch code '{payload.code}' already exists in organization.")
        
        branch = Branch(
            organization_id=tenant_id,
            **payload.model_dump()
        )
        db.add(branch)
        await db.commit()
        await db.refresh(branch)
        return branch

    @staticmethod
    async def update_branch(db: AsyncSession, tenant_id: UUID, branch_id: UUID, payload: BranchUpdate) -> Branch:
        branch = await OrganizationService.get_branch(db, tenant_id, branch_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(branch, key, val)
        await db.commit()
        await db.refresh(branch)
        return branch

    @staticmethod
    async def delete_branch(db: AsyncSession, tenant_id: UUID, branch_id: UUID) -> bool:
        branch = await OrganizationService.get_branch(db, tenant_id, branch_id)
        await db.delete(branch)
        await db.commit()
        return True

    # --- Department ---
    @staticmethod
    async def get_departments(db: AsyncSession, tenant_id: UUID) -> List[Department]:
        res = await db.execute(select(Department).where(Department.organization_id == tenant_id).order_by(Department.name.asc()))
        return list(res.scalars().all())

    @staticmethod
    async def get_department(db: AsyncSession, tenant_id: UUID, department_id: UUID) -> Department:
        res = await db.execute(select(Department).where(Department.id == department_id, Department.organization_id == tenant_id))
        dept = res.scalar_one_or_none()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        return dept

    @staticmethod
    async def create_department(db: AsyncSession, tenant_id: UUID, payload: DepartmentCreate) -> Department:
        dup = await db.execute(select(Department).where(Department.organization_id == tenant_id, Department.code == payload.code))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Department code '{payload.code}' already exists in organization.")
        
        dept = Department(
            organization_id=tenant_id,
            **payload.model_dump()
        )
        db.add(dept)
        await db.commit()
        await db.refresh(dept)
        return dept

    @staticmethod
    async def update_department(db: AsyncSession, tenant_id: UUID, department_id: UUID, payload: DepartmentUpdate) -> Department:
        dept = await OrganizationService.get_department(db, tenant_id, department_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(dept, key, val)
        await db.commit()
        await db.refresh(dept)
        return dept

    @staticmethod
    async def delete_department(db: AsyncSession, tenant_id: UUID, department_id: UUID) -> bool:
        dept = await OrganizationService.get_department(db, tenant_id, department_id)
        await db.delete(dept)
        await db.commit()
        return True

    # --- Designation ---
    @staticmethod
    async def get_designations(db: AsyncSession, tenant_id: UUID) -> List[Designation]:
        res = await db.execute(select(Designation).where(Designation.organization_id == tenant_id).order_by(Designation.level.asc(), Designation.name.asc()))
        return list(res.scalars().all())

    @staticmethod
    async def get_designation(db: AsyncSession, tenant_id: UUID, designation_id: UUID) -> Designation:
        res = await db.execute(select(Designation).where(Designation.id == designation_id, Designation.organization_id == tenant_id))
        desig = res.scalar_one_or_none()
        if not desig:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Designation not found")
        return desig

    @staticmethod
    async def create_designation(db: AsyncSession, tenant_id: UUID, payload: DesignationCreate) -> Designation:
        dup = await db.execute(select(Designation).where(Designation.organization_id == tenant_id, Designation.code == payload.code))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Designation code '{payload.code}' already exists in organization.")
        
        desig = Designation(
            organization_id=tenant_id,
            **payload.model_dump()
        )
        db.add(desig)
        await db.commit()
        await db.refresh(desig)
        return desig

    @staticmethod
    async def update_designation(db: AsyncSession, tenant_id: UUID, designation_id: UUID, payload: DesignationUpdate) -> Designation:
        desig = await OrganizationService.get_designation(db, tenant_id, designation_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(desig, key, val)
        await db.commit()
        await db.refresh(desig)
        return desig

    @staticmethod
    async def delete_designation(db: AsyncSession, tenant_id: UUID, designation_id: UUID) -> bool:
        desig = await OrganizationService.get_designation(db, tenant_id, designation_id)
        await db.delete(desig)
        await db.commit()
        return True
