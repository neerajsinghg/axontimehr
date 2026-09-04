from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.salary_service import SalaryService
from app.schemas.payroll import (
    SalaryComponentCreate,
    SalaryComponentResponse,
    SalaryStructureCreate,
    SalaryStructureResponse,
    EmployeeSalaryAssignmentCreate,
    EmployeeSalaryAssignmentResponse,
)

router = APIRouter(prefix="/salary", tags=["Salary & Compensation"])


@router.get("/components", response_model=List[SalaryComponentResponse])
async def get_components(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SalaryService.get_components(db, current_user.tenant_id)


@router.post("/components", response_model=SalaryComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(
    data: SalaryComponentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SalaryService.create_component(db, current_user.tenant_id, data)


@router.post("/components/seed", response_model=List[SalaryComponentResponse])
async def seed_default_components(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SalaryService.seed_default_components(db, current_user.tenant_id)


@router.get("/structures", response_model=List[SalaryStructureResponse])
async def get_structures(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    structures = await SalaryService.get_structures(db, current_user.tenant_id)
    response = []
    for s in structures:
        comp_items = []
        for c in s.components:
            has_c = "component" in c.__dict__ and c.component
            comp_items.append({
                "id": c.id,
                "component_id": c.component_id,
                "component_code": c.component.code if has_c else None,
                "component_name": c.component.name if has_c else None,
                "component_type": c.component.component_type.value if has_c and hasattr(c.component.component_type, 'value') else (str(c.component.component_type) if has_c else ""),
                "calculation_type": c.calculation_type.value if hasattr(c.calculation_type, 'value') else str(c.calculation_type),
                "amount": float(c.amount) if c.amount is not None else None,
                "percentage": float(c.percentage) if c.percentage is not None else None,
                "formula": c.formula
            })
        response.append({
            "id": s.id,
            "tenant_id": s.tenant_id,
            "code": s.code,
            "name": s.name,
            "description": s.description,
            "status": s.status,
            "components": comp_items,
            "created_at": s.created_at
        })
    return response


@router.post("/structures", response_model=SalaryStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_structure(
    data: SalaryStructureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    s = await SalaryService.create_structure(db, current_user.tenant_id, data)
    comp_items = []
    for c in s.components:
        has_c = "component" in c.__dict__ and c.component
        comp_items.append({
            "id": c.id,
            "component_id": c.component_id,
            "component_code": c.component.code if has_c else None,
            "component_name": c.component.name if has_c else None,
            "component_type": c.component.component_type.value if has_c and hasattr(c.component.component_type, 'value') else (str(c.component.component_type) if has_c else ""),
            "calculation_type": c.calculation_type.value if hasattr(c.calculation_type, 'value') else str(c.calculation_type),
            "amount": float(c.amount) if c.amount is not None else None,
            "percentage": float(c.percentage) if c.percentage is not None else None,
            "formula": c.formula
        })
    return {
        "id": s.id,
        "tenant_id": s.tenant_id,
        "code": s.code,
        "name": s.name,
        "description": s.description,
        "status": s.status,
        "components": comp_items,
        "created_at": s.created_at
    }


@router.post("/assignments", response_model=EmployeeSalaryAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_salary(
    data: EmployeeSalaryAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assign = await SalaryService.assign_employee_salary(db, current_user.tenant_id, data)
    has_struct = "structure" in assign.__dict__ and assign.structure
    return {
        "id": assign.id,
        "tenant_id": assign.tenant_id,
        "employee_id": assign.employee_id,
        "salary_structure_id": assign.salary_structure_id,
        "structure_name": assign.structure.name if has_struct else None,
        "annual_ctc": float(assign.annual_ctc),
        "monthly_ctc": float(assign.monthly_ctc),
        "gross_salary": float(assign.gross_salary),
        "effective_from": assign.effective_from,
        "effective_to": assign.effective_to,
        "version": assign.version,
        "status": assign.status.value if hasattr(assign.status, 'value') else str(assign.status),
        "created_at": assign.created_at
    }


@router.get("/assignments/{employee_id}", response_model=Optional[EmployeeSalaryAssignmentResponse])
async def get_assignment(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assign = await SalaryService.get_active_assignment(db, current_user.tenant_id, employee_id)
    if not assign:
        return None
    has_struct = "structure" in assign.__dict__ and assign.structure
    return {
        "id": assign.id,
        "tenant_id": assign.tenant_id,
        "employee_id": assign.employee_id,
        "salary_structure_id": assign.salary_structure_id,
        "structure_name": assign.structure.name if has_struct else None,
        "annual_ctc": float(assign.annual_ctc),
        "monthly_ctc": float(assign.monthly_ctc),
        "gross_salary": float(assign.gross_salary),
        "effective_from": assign.effective_from,
        "effective_to": assign.effective_to,
        "version": assign.version,
        "status": assign.status.value if hasattr(assign.status, 'value') else str(assign.status),
        "created_at": assign.created_at
    }
