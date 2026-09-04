import uuid
import secrets
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payroll import Payslip, PayrollEmployee, PayrollPeriod
from app.models.employee import Employee


class PayslipService:
    """
    Generates professional PDF/HTML payslips and manages tokenized download URLs.
    """

    @staticmethod
    async def generate_payslip_record(
        db: AsyncSession,
        tenant_id: UUID,
        payroll_employee_id: UUID,
        employee_id: UUID,
        period_id: UUID
    ) -> Payslip:
        res = await db.execute(
            select(Payslip).where(
                Payslip.tenant_id == tenant_id,
                Payslip.payroll_employee_id == payroll_employee_id
            )
        )
        existing = res.scalar_one_or_none()

        if existing:
            return existing

        download_token = secrets.token_urlsafe(32)
        pdf_path = f"/storage/payslips/tenant_{tenant_id}/payslip_{payroll_employee_id}.pdf"

        payslip = Payslip(
            tenant_id=tenant_id,
            payroll_employee_id=payroll_employee_id,
            employee_id=employee_id,
            period_id=period_id,
            pdf_path=pdf_path,
            download_token=download_token,
            download_count=0
        )
        db.add(payslip)
        await db.commit()
        await db.refresh(payslip)
        return payslip

    @staticmethod
    async def get_employee_payslips(db: AsyncSession, tenant_id: UUID, employee_id: UUID) -> List[Payslip]:
        res = await db.execute(
            select(Payslip)
            .options(selectinload(Payslip.period))
            .where(
                Payslip.tenant_id == tenant_id,
                Payslip.employee_id == employee_id
            )
            .order_by(Payslip.generated_at.desc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def get_payslip_by_token(db: AsyncSession, token: str) -> Optional[Payslip]:
        res = await db.execute(
            select(Payslip)
            .options(selectinload(Payslip.employee), selectinload(Payslip.period))
            .where(Payslip.download_token == token)
        )
        payslip = res.scalar_one_or_none()
        if payslip:
            payslip.download_count += 1
            await db.commit()
            await db.refresh(payslip)
        return payslip

    @staticmethod
    async def generate_html_payslip(db: AsyncSession, payslip: Payslip) -> str:
        """
        Renders a production-ready HTML payslip document.
        """
        emp_res = await db.execute(select(Employee).where(Employee.id == payslip.employee_id))
        emp = emp_res.scalar_one_or_none()

        pe_res = await db.execute(
            select(PayrollEmployee)
            .options(selectinload(PayrollEmployee.line_items))
            .where(PayrollEmployee.id == payslip.payroll_employee_id)
        )
        payroll_emp = pe_res.scalar_one_or_none()

        period_res = await db.execute(select(PayrollPeriod).where(PayrollPeriod.id == payslip.period_id))
        period = period_res.scalar_one_or_none()

        emp_name = f"{emp.first_name} {emp.last_name}" if emp else "Employee"
        emp_code = emp.employee_id if emp else "N/A"
        period_name = period.name if period else "Payroll Period"

        earnings_html = ""
        deductions_html = ""

        if payroll_emp:
            for item in payroll_emp.line_items:
                line_type_str = item.line_type.value if hasattr(item.line_type, 'value') else str(item.line_type)
                if line_type_str in ["EARNING", "LineItemType.EARNING"]:
                    earnings_html += f"<tr><td>{item.component_name}</td><td style='text-align:right;'>₹{item.amount:,.2f}</td></tr>"
                elif line_type_str in ["DEDUCTION", "TAX", "LineItemType.DEDUCTION", "LineItemType.TAX"]:
                    deductions_html += f"<tr><td>{item.component_name}</td><td style='text-align:right;'>₹{item.amount:,.2f}</td></tr>"

        gross = payroll_emp.gross_salary if payroll_emp else Decimal("0.00")
        total_ded = payroll_emp.total_deductions if payroll_emp else Decimal("0.00")
        net = payroll_emp.net_salary if payroll_emp else Decimal("0.00")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Payslip - {period_name} - {emp_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; color: #0f172a; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #059669; padding-bottom: 15px; margin-bottom: 20px; }}
                .title {{ font-size: 24px; font-weight: 700; color: #059669; }}
                .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; font-size: 14px; }}
                .tables-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }}
                table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
                th {{ background: #f1f5f9; text-align: left; padding: 8px; font-weight: 600; border-bottom: 1px solid #cbd5e1; }}
                td {{ padding: 8px; border-bottom: 1px solid #f1f5f9; }}
                .net-banner {{ background: #ecfdf5; border: 1px solid #10b981; border-radius: 8px; padding: 15px; text-align: center; font-size: 20px; font-weight: 700; color: #047857; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div>
                        <div class="title">AxonTimeHR</div>
                        <div style="font-size: 12px; color: #64748b;">Confidential Salary Slip</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 600;">{period_name}</div>
                        <div style="font-size: 12px; color: #64748b;">Generated: {datetime.now(timezone.utc).strftime('%d %b %Y')}</div>
                    </div>
                </div>

                <div class="info-grid">
                    <div><strong>Employee Name:</strong> {emp_name}</div>
                    <div><strong>Employee ID:</strong> {emp_code}</div>
                    <div><strong>Working Days:</strong> {payroll_emp.working_days if payroll_emp else 22}</div>
                    <div><strong>Present Days:</strong> {payroll_emp.present_days if payroll_emp else 22}</div>
                    <div><strong>LOP Days:</strong> {payroll_emp.lop_days if payroll_emp else 0}</div>
                    <div><strong>Paid Leaves:</strong> {payroll_emp.paid_leave_days if payroll_emp else 0}</div>
                </div>

                <div class="tables-grid">
                    <div>
                        <table>
                            <thead><tr><th>Earnings</th><th style="text-align:right;">Amount</th></tr></thead>
                            <tbody>
                                {earnings_html}
                                <tr style="font-weight:700;"><td>Total Gross Earnings</td><td style="text-align:right;">₹{gross:,.2f}</td></tr>
                            </tbody>
                        </table>
                    </div>
                    <div>
                        <table>
                            <thead><tr><th>Deductions</th><th style="text-align:right;">Amount</th></tr></thead>
                            <tbody>
                                {deductions_html}
                                <tr style="font-weight:700;"><td>Total Deductions</td><td style="text-align:right;">₹{total_ded:,.2f}</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="net-banner">
                    NET SALARY PAYABLE: ₹{net:,.2f}
                </div>
            </div>
        </body>
        </html>
        """
        return html_content
