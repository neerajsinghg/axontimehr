from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.attendance_service import AttendanceService
from app.services.payslip_service import PayslipService
from app.schemas.payroll import PayslipResponse

router = APIRouter(prefix="/payslips", tags=["Employee Payslips"])


@router.get("", response_model=List[PayslipResponse])
async def get_my_payslips(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    emp = await AttendanceService.get_or_create_employee_for_user(db, current_user.tenant_id, current_user.id)
    payslips = await PayslipService.get_employee_payslips(db, current_user.tenant_id, emp.id)
    return [
        {
            "id": p.id,
            "tenant_id": p.tenant_id,
            "payroll_employee_id": p.payroll_employee_id,
            "employee_id": p.employee_id,
            "period_id": p.period_id,
            "period_name": p.period.name if hasattr(p, "period") and p.period else "Payroll Period",
            "pdf_path": p.pdf_path,
            "download_token": p.download_token,
            "download_count": p.download_count,
            "generated_at": p.generated_at
        }
        for p in payslips
    ]


@router.get("/{token}/download", response_class=HTMLResponse)
async def download_payslip_html(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    payslip = await PayslipService.get_payslip_by_token(db, token)
    if not payslip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payslip not found or invalid token")

    html_content = await PayslipService.generate_html_payslip(db, payslip)
    return HTMLResponse(content=html_content)
