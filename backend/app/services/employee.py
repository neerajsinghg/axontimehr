import math
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.organization import Department, Designation, Branch
from app.models.user import User
from app.models.document import EmployeeDocument
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeStatusUpdate,
    EmployeeDocumentCreate, OrgTreeNode
)
from app.core.security import hash_password, generate_secure_token

class EmployeeService:
    @staticmethod
    async def get_employees_paginated(
        db: AsyncSession,
        tenant_id: Optional[UUID] = None,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        department_id: Optional[UUID] = None,
        branch_id: Optional[UUID] = None,
        designation_id: Optional[UUID] = None,
        status: Optional[str] = None,
        manager_id: Optional[UUID] = None
    ) -> Tuple[List[Employee], int, int]:
        query = select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.designation),
            selectinload(Employee.branch),
            selectinload(Employee.manager).selectinload(Employee.designation),
            selectinload(Employee.user)
        )
        count_query = select(func.count(Employee.id))

        if tenant_id:
            query = query.where(Employee.organization_id == tenant_id)
            count_query = count_query.where(Employee.organization_id == tenant_id)

        # Apply search
        if search:
            search_pattern = f"%{search}%"
            filter_cond = or_(
                Employee.first_name.ilike(search_pattern),
                Employee.last_name.ilike(search_pattern),
                Employee.email.ilike(search_pattern),
                Employee.employee_id.ilike(search_pattern)
            )
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)

        if department_id:
            query = query.where(Employee.department_id == department_id)
            count_query = count_query.where(Employee.department_id == department_id)

        if branch_id:
            query = query.where(Employee.branch_id == branch_id)
            count_query = count_query.where(Employee.branch_id == branch_id)

        if designation_id:
            query = query.where(Employee.designation_id == designation_id)
            count_query = count_query.where(Employee.designation_id == designation_id)

        if manager_id:
            query = query.where(Employee.manager_id == manager_id)
            count_query = count_query.where(Employee.manager_id == manager_id)

        if status and status != "ALL":
            query = query.where(Employee.status == status)
            count_query = count_query.where(Employee.status == status)

        # Count total matching
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # Apply pagination
        offset = (page - 1) * limit
        query = query.order_by(Employee.employee_id.asc()).offset(offset).limit(limit)

        result = await db.execute(query)
        employees = list(result.scalars().all())
        total_pages = math.ceil(total / limit) if limit > 0 else 1

        return employees, total, total_pages

    @staticmethod
    async def get_employee_by_id(db: AsyncSession, employee_id: UUID, tenant_id: Optional[UUID] = None) -> Employee:
        query = (
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.designation),
                selectinload(Employee.branch),
                selectinload(Employee.manager).selectinload(Employee.designation),
                selectinload(Employee.user),
                selectinload(Employee.documents)
            )
            .where(Employee.id == employee_id)
        )
        if tenant_id:
            query = query.where(Employee.organization_id == tenant_id)

        res = await db.execute(query)
        emp = res.scalar_one_or_none()
        if not emp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return emp

    @staticmethod
    async def create_employee(db: AsyncSession, tenant_id: UUID, payload: EmployeeCreate) -> Employee:
        # Check unique employee_id within tenant
        dup_code = await db.execute(select(Employee).where(Employee.organization_id == tenant_id, Employee.employee_id == payload.employee_id))
        if dup_code.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Employee ID '{payload.employee_id}' already exists in organization.")

        # Check unique email within tenant
        dup_email = await db.execute(select(Employee).where(Employee.organization_id == tenant_id, Employee.email == payload.email))
        if dup_email.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Employee with email '{payload.email}' already exists.")

        # Validate manager if provided
        if payload.manager_id:
            mgr_res = await db.execute(select(Employee).where(Employee.id == payload.manager_id, Employee.organization_id == tenant_id))
            if not mgr_res.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected manager does not exist in this organization.")

        # Optionally resolve or create user account
        user_id = payload.user_id
        if not user_id and payload.email:
            existing_user_res = await db.execute(select(User).where(User.email == payload.email))
            existing_user = existing_user_res.scalar_one_or_none()
            if existing_user:
                emp_linked = await db.execute(select(Employee).where(Employee.user_id == existing_user.id))
                if not emp_linked.scalar_one_or_none():
                    user_id = existing_user.id
            elif payload.create_user_account:
                pwd = payload.user_password or "AxonTime@123"
                new_user = User(
                    email=payload.email,
                    password_hash=hash_password(pwd),
                    first_name=payload.first_name,
                    last_name=payload.last_name,
                    is_active=True,
                    is_verified=True,
                    tenant_id=tenant_id
                )
                db.add(new_user)
                await db.flush()
                user_id = new_user.id

        emp = Employee(
            organization_id=tenant_id,
            user_id=user_id,
            employee_id=payload.employee_id,
            first_name=payload.first_name,
            middle_name=payload.middle_name,
            last_name=payload.last_name,
            display_name=payload.display_name or f"{payload.first_name} {payload.last_name}",
            gender=payload.gender,
            date_of_birth=payload.date_of_birth,
            email=payload.email,
            personal_email=payload.personal_email,
            phone=payload.phone,
            personal_phone=payload.personal_phone,
            emergency_contact=payload.emergency_contact,
            address_line1=payload.address_line1,
            address_line2=payload.address_line2,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            postal_code=payload.postal_code,
            joining_date=payload.joining_date,
            date_of_confirmation=payload.date_of_confirmation,
            employment_type=payload.employment_type,
            employee_category=payload.employee_category,
            status=payload.status,
            avatar_url=payload.avatar_url,
            department_id=payload.department_id,
            designation_id=payload.designation_id,
            branch_id=payload.branch_id,
            manager_id=payload.manager_id
        )
        db.add(emp)
        await db.commit()
        return await EmployeeService.get_employee_by_id(db, emp.id, tenant_id)

    @staticmethod
    async def update_employee(db: AsyncSession, tenant_id: UUID, employee_id: UUID, payload: EmployeeUpdate) -> Employee:
        emp = await EmployeeService.get_employee_by_id(db, employee_id, tenant_id)

        # Validate manager cycle if updating manager
        if payload.manager_id is not None:
            if payload.manager_id == employee_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An employee cannot report to themselves.")
            
            # Check hierarchy cycle: follow manager chain up
            curr_mgr_id = payload.manager_id
            visited = {employee_id}
            while curr_mgr_id:
                if curr_mgr_id in visited:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reporting manager selection: hierarchy cycle detected.")
                visited.add(curr_mgr_id)
                res = await db.execute(select(Employee.manager_id).where(Employee.id == curr_mgr_id))
                curr_mgr_id = res.scalar()

        update_data = payload.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(emp, key, val)

        await db.commit()
        return await EmployeeService.get_employee_by_id(db, employee_id, tenant_id)

    @staticmethod
    async def update_employee_status(db: AsyncSession, tenant_id: UUID, employee_id: UUID, payload: EmployeeStatusUpdate) -> Employee:
        emp = await EmployeeService.get_employee_by_id(db, employee_id, tenant_id)
        emp.status = payload.status
        if payload.date_of_leaving:
            emp.date_of_leaving = payload.date_of_leaving
        await db.commit()
        return await EmployeeService.get_employee_by_id(db, employee_id, tenant_id)

    @staticmethod
    async def soft_delete_employee(db: AsyncSession, tenant_id: UUID, employee_id: UUID) -> bool:
        emp = await EmployeeService.get_employee_by_id(db, employee_id, tenant_id)
        emp.status = "TERMINATED"
        emp.date_of_leaving = datetime.now(timezone.utc).date()
        await db.commit()
        return True

    @staticmethod
    async def get_employee_stats(db: AsyncSession, tenant_id: Optional[UUID] = None) -> Dict[str, Any]:
        count_q = select(func.count(Employee.id))
        if tenant_id:
            count_q = count_q.where(Employee.organization_id == tenant_id)

        total = (await db.execute(count_q)).scalar() or 0

        active_q = count_q.where(Employee.status == "ACTIVE")
        active = (await db.execute(active_q)).scalar() or 0

        leave_q = count_q.where(Employee.status == "ON_LEAVE")
        on_leave = (await db.execute(leave_q)).scalar() or 0

        inactive_q = count_q.where(Employee.status.in_(["INACTIVE", "TERMINATED", "SUSPENDED"]))
        inactive = (await db.execute(inactive_q)).scalar() or 0

        dept_count_q = select(func.count(Department.id))
        if tenant_id:
            dept_count_q = dept_count_q.where(Department.organization_id == tenant_id)
        depts_count = (await db.execute(dept_count_q)).scalar() or 0

        dept_breakdown_query = (
            select(Department.name, func.count(Employee.id))
            .join(Employee, Employee.department_id == Department.id, isouter=True)
        )
        if tenant_id:
            dept_breakdown_query = dept_breakdown_query.where(Department.organization_id == tenant_id)
        dept_breakdown_query = dept_breakdown_query.group_by(Department.name)
        
        dept_res = await db.execute(dept_breakdown_query)
        dept_stats = [
            {"department_name": row[0] or "Unassigned", "count": row[1]}
            for row in dept_res.all()
        ]

        return {
            "total_employees": total,
            "active_employees": active,
            "on_leave_employees": on_leave,
            "inactive_employees": inactive,
            "departments_count": depts_count,
            "by_department": dept_stats
        }

    # --- Document Metadata ---
    @staticmethod
    async def add_document(db: AsyncSession, tenant_id: UUID, employee_id: UUID, payload: EmployeeDocumentCreate, uploaded_by: Optional[UUID] = None) -> EmployeeDocument:
        await EmployeeService.get_employee_by_id(db, employee_id, tenant_id)
        doc = EmployeeDocument(
            organization_id=tenant_id,
            employee_id=employee_id,
            uploaded_by=uploaded_by,
            **payload.model_dump()
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def get_documents(db: AsyncSession, tenant_id: UUID, employee_id: UUID) -> List[EmployeeDocument]:
        await EmployeeService.get_employee_by_id(db, employee_id, tenant_id)
        res = await db.execute(select(EmployeeDocument).where(EmployeeDocument.employee_id == employee_id, EmployeeDocument.organization_id == tenant_id))
        return list(res.scalars().all())

    @staticmethod
    async def delete_document(db: AsyncSession, tenant_id: UUID, employee_id: UUID, document_id: UUID) -> bool:
        res = await db.execute(select(EmployeeDocument).where(EmployeeDocument.id == document_id, EmployeeDocument.employee_id == employee_id, EmployeeDocument.organization_id == tenant_id))
        doc = res.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        await db.delete(doc)
        await db.commit()
        return True
