from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.payroll_service import PayrollService
from app.schemas.payroll import (
    PayrollPeriodCreate,
    PayrollPeriodResponse,
    PayrollRunCreate,
    PayrollRunResponse,
    PayrollAdjustmentCreate,
    PayrollAdjustmentResponse,
)

router = APIRouter(prefix="/payroll", tags=["Payroll Management"])


@router.get("/periods", response_model=List[PayrollPeriodResponse])
async def get_periods(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    periods = await PayrollService.get_periods(db, current_user.tenant_id)
    return [
        {
            "id": p.id,
            "tenant_id": p.tenant_id,
            "name": p.name,
            "year": p.year,
            "month": p.month,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "pay_date": p.pay_date,
            "status": p.status.value if hasattr(p.status, 'value') else str(p.status),
            "created_at": p.created_at
        }
        for p in periods
    ]


@router.post("/periods", response_model=PayrollPeriodResponse, status_code=status.HTTP_201_CREATED)
async def create_period(
    data: PayrollPeriodCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    p = await PayrollService.create_period(db, current_user.tenant_id, data)
    return {
        "id": p.id,
        "tenant_id": p.tenant_id,
        "name": p.name,
        "year": p.year,
        "month": p.month,
        "start_date": p.start_date,
        "end_date": p.end_date,
        "pay_date": p.pay_date,
        "status": p.status.value if hasattr(p.status, 'value') else str(p.status),
        "created_at": p.created_at
    }


@router.post("/runs", response_model=PayrollRunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    data: PayrollRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        run = await PayrollService.create_payroll_run(db, current_user.tenant_id, data)
        return _format_payroll_run_response(run)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/runs/{run_id}/calculate", response_model=PayrollRunResponse)
async def calculate_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        run = await PayrollService.calculate_payroll_run(db, current_user.tenant_id, run_id)
        return _format_payroll_run_response(run)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/runs/{run_id}/approve", response_model=PayrollRunResponse)
async def submit_approval(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        run = await PayrollService.submit_for_approval(db, current_user.tenant_id, run_id, current_user.id)
        return _format_payroll_run_response(run)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/runs/{run_id}/lock", response_model=PayrollRunResponse)
async def lock_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        run = await PayrollService.lock_payroll_run(db, current_user.tenant_id, run_id)
        return _format_payroll_run_response(run)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/runs/{run_id}/mark-paid", response_model=PayrollRunResponse)
async def mark_paid(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        run = await PayrollService.mark_payroll_paid(db, current_user.tenant_id, run_id)
        return _format_payroll_run_response(run)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/adjustments", response_model=List[PayrollAdjustmentResponse])
async def get_adjustments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    adj_list = await PayrollService.get_adjustments(db, current_user.tenant_id)
    return [
        {
            "id": a.id,
            "tenant_id": a.tenant_id,
            "employee_id": a.employee_id,
            "employee_name": f"{a.employee.first_name} {a.employee.last_name}" if a.employee else None,
            "adjustment_type": a.adjustment_type.value if hasattr(a.adjustment_type, 'value') else str(a.adjustment_type),
            "amount": float(a.amount),
            "reason": a.reason,
            "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
            "created_at": a.created_at
        }
        for a in adj_list
    ]


@router.post("/adjustments", response_model=PayrollAdjustmentResponse, status_code=status.HTTP_201_CREATED)
async def create_adjustment(
    data: PayrollAdjustmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    a = await PayrollService.create_adjustment(db, current_user.tenant_id, current_user.id, data)
    return {
        "id": a.id,
        "tenant_id": a.tenant_id,
        "employee_id": a.employee_id,
        "employee_name": f"{a.employee.first_name} {a.employee.last_name}" if a.employee else None,
        "adjustment_type": a.adjustment_type.value if hasattr(a.adjustment_type, 'value') else str(a.adjustment_type),
        "amount": float(a.amount),
        "reason": a.reason,
        "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
        "created_at": a.created_at
    }


def _format_payroll_run_response(run) -> dict:
    emp_list = []
    if "payroll_employees" in run.__dict__ and run.payroll_employees:
        for pe in run.payroll_employees:
            line_items = []
            if "line_items" in pe.__dict__ and pe.line_items:
                for li in pe.line_items:
                    line_items.append({
                        "id": li.id,
                        "component_code": li.component_code,
                        "component_name": li.component_name,
                        "line_type": li.line_type.value if hasattr(li.line_type, 'value') else str(li.line_type),
                        "amount": float(li.amount),
                        "calculation_explanation": li.calculation_explanation
                    })
            emp_list.append({
                "id": pe.id,
                "employee_id": pe.employee_id,
                "employee_name": f"{pe.employee.first_name} {pe.employee.last_name}" if "employee" in pe.__dict__ and pe.employee else None,
                "employee_code": getattr(pe.employee, 'employee_id', None) if "employee" in pe.__dict__ and pe.employee else None,
                "calendar_days": pe.calendar_days,
                "working_days": pe.working_days,
                "present_days": float(pe.present_days),
                "paid_leave_days": float(pe.paid_leave_days),
                "unpaid_leave_days": float(pe.unpaid_leave_days),
                "lop_days": float(pe.lop_days),
                "holiday_days": float(pe.holiday_days),
                "overtime_hours": float(pe.overtime_hours),
                "gross_salary": float(pe.gross_salary),
                "total_earnings": float(pe.total_earnings),
                "total_deductions": float(pe.total_deductions),
                "employer_contributions": float(pe.employer_contributions),
                "net_salary": float(pe.net_salary),
                "status": pe.status.value if hasattr(pe.status, 'value') else str(pe.status),
                "exception_message": pe.exception_message,
                "line_items": line_items
            })

    return {
        "id": run.id,
        "tenant_id": run.tenant_id,
        "period_id": run.period_id,
        "period_name": run.period.name if "period" in run.__dict__ and run.period else None,
        "total_employees": run.total_employees,
        "total_gross": float(run.total_gross),
        "total_deductions": float(run.total_deductions),
        "total_net": float(run.total_net),
        "status": run.status.value if hasattr(run.status, 'value') else str(run.status),
        "approval_instance_id": run.approval_instance_id,
        "locked_at": run.locked_at,
        "paid_at": run.paid_at,
        "employees": emp_list,
        "created_at": run.created_at
    }
