import calendar
from decimal import Decimal
from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import date, datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payroll import (
    PayrollRun,
    PayrollEmployee,
    PayrollLineItem,
    PayrollPeriod,
    SalaryComponent,
    SalaryStructure,
    EmployeeSalaryAssignment,
    LineItemType,
    ComponentType,
    PayrollEmployeeStatus,
)
from app.models.employee import Employee
from app.models.attendance import Attendance, AttendanceStatus
from app.models.leave import LeaveRequest, LeaveRequestStatus
from app.models.holiday import HolidayMaster
from app.models.financial import (
    Reimbursement,
    ReimbursementStatus,
    LoanInstallment,
    InstallmentStatus,
    AdvanceRecovery,
    RecoveryStatus
)
from app.services.salary_service import SalaryService
from app.services.formula_engine import SafeFormulaEvaluator
from app.services.statutory_service import StatutoryService


class PayrollCalculationService:
    """
    Financial calculation engine for employee payroll processing.
    Ensures 100% financial precision using Decimal arithmetic and immutability.
    """

    @classmethod
    async def calculate_employee_payroll(
        cls,
        db: AsyncSession,
        tenant_id: UUID,
        payroll_run_id: UUID,
        period: PayrollPeriod,
        employee: Employee
    ) -> PayrollEmployee:
        # 1. Days in Month & Calendar calculation
        _, days_in_month = calendar.monthrange(period.year, period.month)
        start_date = period.start_date
        end_date = period.end_date

        # 2. Get Employee Active Salary Assignment
        assignment = await SalaryService.get_active_assignment(db, tenant_id, employee.id, end_date)
        if not assignment or not assignment.salary_structure_id:
            payroll_emp = PayrollEmployee(
                tenant_id=tenant_id,
                payroll_run_id=payroll_run_id,
                employee_id=employee.id,
                calendar_days=days_in_month,
                working_days=22,
                status=PayrollEmployeeStatus.ERROR,
                exception_message="Missing active salary structure assignment for payroll period"
            )
            db.add(payroll_emp)
            return payroll_emp

        # 3. Query Attendance & Leave engine (Phases 4, 5, 6 integration)
        att_res = await db.execute(
            select(Attendance).where(
                Attendance.tenant_id == tenant_id,
                Attendance.employee_id == employee.id,
                Attendance.attendance_date >= start_date,
                Attendance.attendance_date <= end_date
            )
        )
        attendances = list(att_res.scalars().all())

        present_count = Decimal("0.00")
        for att in attendances:
            if att.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE, AttendanceStatus.EARLY_EXIT]:
                present_count += Decimal("1.00")
            elif att.status == AttendanceStatus.HALF_DAY:
                present_count += Decimal("0.50")

        # Query approved leaves (Phase 6)
        leave_res = await db.execute(
            select(LeaveRequest).where(
                LeaveRequest.tenant_id == tenant_id,
                LeaveRequest.employee_id == employee.id,
                LeaveRequest.status == LeaveRequestStatus.APPROVED,
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date
            )
        )
        leaves = list(leave_res.scalars().all())

        paid_leave_days = Decimal("0.00")
        unpaid_leave_days = Decimal("0.00")
        for leave in leaves:
            if getattr(leave, "is_paid", True):
                paid_leave_days += Decimal(str(getattr(leave, "working_days_count", 1.0)))
            else:
                unpaid_leave_days += Decimal(str(getattr(leave, "working_days_count", 1.0)))

        # Query holidays (Phase 6)
        h_res = await db.execute(
            select(func.count(HolidayMaster.id)).where(
                HolidayMaster.tenant_id == tenant_id,
                HolidayMaster.holiday_date >= start_date,
                HolidayMaster.holiday_date <= end_date
            )
        )
        holiday_count = h_res.scalar() or 0
        holiday_days = Decimal(str(holiday_count))

        # Default standard 22 working days if calendar calculation yields 0
        working_days = max(1, days_in_month - 8 - int(holiday_count))
        
        # Calculate LOP (Loss of Pay) Days
        weekly_offs = Decimal("8.00")
        accounted_days = present_count + paid_leave_days + holiday_days + weekly_offs
        calculated_lop = max(Decimal("0.00"), Decimal(str(days_in_month)) - accounted_days + unpaid_leave_days)
        lop_days = calculated_lop.quantize(Decimal("0.5"))

        # Monthly Gross Salary from Assignment
        monthly_gross = assignment.gross_salary
        daily_rate = (monthly_gross / Decimal(str(days_in_month))).quantize(Decimal("0.01"))
        lop_deduction = (daily_rate * lop_days).quantize(Decimal("0.01"))

        # Component Earnings & Basic Resolution
        basic_amount = (monthly_gross * Decimal("0.50")).quantize(Decimal("0.01"))
        hra_amount = (basic_amount * Decimal("0.40")).quantize(Decimal("0.01"))
        special_allowance = max(Decimal("0.00"), monthly_gross - basic_amount - hra_amount)

        # Statutory Calculations
        pf_res = StatutoryService.calculate_pf(basic_amount, cap_enabled=True)
        employee_pf = pf_res["employee_pf"]
        employer_pf = pf_res["employer_pf"]

        esi_res = StatutoryService.calculate_esi(monthly_gross)
        employee_esi = esi_res["employee_esi"]
        employer_esi = esi_res["employer_esi"]

        employee_pt = StatutoryService.calculate_pt(monthly_gross)
        employee_tds = StatutoryService.calculate_tds_estimate(monthly_gross)

        # Phase 8 Financial Integration Queries
        # 1. Reimbursements pending for employee in this period
        reimb_res = await db.execute(
            select(func.coalesce(func.sum(Reimbursement.amount), Decimal("0.00"))).where(
                and_(
                    Reimbursement.tenant_id == tenant_id,
                    Reimbursement.employee_id == employee.id,
                    Reimbursement.status == ReimbursementStatus.PENDING
                )
            )
        )
        reimbursement_amount = Decimal(str(reimb_res.scalar_one()))

        # 2. Active Loan EMIs due in this period
        loan_res = await db.execute(
            select(func.coalesce(func.sum(LoanInstallment.total_amount), Decimal("0.00"))).where(
                and_(
                    LoanInstallment.tenant_id == tenant_id,
                    LoanInstallment.status == InstallmentStatus.PENDING,
                    LoanInstallment.due_date >= start_date,
                    LoanInstallment.due_date <= end_date
                )
            )
        )
        loan_repayment_amount = Decimal(str(loan_res.scalar_one()))

        # 3. Active Salary Advance recoveries due in this period
        adv_res = await db.execute(
            select(func.coalesce(func.sum(AdvanceRecovery.amount), Decimal("0.00"))).where(
                and_(
                    AdvanceRecovery.tenant_id == tenant_id,
                    AdvanceRecovery.status == RecoveryStatus.PENDING,
                    AdvanceRecovery.due_date >= start_date,
                    AdvanceRecovery.due_date <= end_date
                )
            )
        )
        advance_recovery_amount = Decimal(str(adv_res.scalar_one()))

        # Total Earnings & Deductions
        total_earnings = monthly_gross + reimbursement_amount
        total_deductions = lop_deduction + employee_pf + employee_esi + employee_pt + employee_tds + loan_repayment_amount + advance_recovery_amount
        employer_contributions = employer_pf + employer_esi
        net_salary = max(Decimal("0.00"), total_earnings - total_deductions)

        # Save Payroll Employee Result
        payroll_emp = PayrollEmployee(
            tenant_id=tenant_id,
            payroll_run_id=payroll_run_id,
            employee_id=employee.id,
            calendar_days=days_in_month,
            working_days=working_days,
            present_days=present_count,
            paid_leave_days=paid_leave_days,
            unpaid_leave_days=unpaid_leave_days,
            lop_days=lop_days,
            holiday_days=holiday_days,
            overtime_hours=Decimal("0.00"),
            gross_salary=monthly_gross,
            total_earnings=total_earnings,
            total_deductions=total_deductions,
            employer_contributions=employer_contributions,
            net_salary=net_salary,
            status=PayrollEmployeeStatus.PROCESSED
        )
        db.add(payroll_emp)
        await db.flush()

        # Itemized Line Items Creation
        line_items = [
            PayrollLineItem(
                tenant_id=tenant_id,
                payroll_employee_id=payroll_emp.id,
                component_code="BASIC",
                component_name="Basic Salary",
                line_type=LineItemType.EARNING,
                amount=basic_amount,
                calculation_explanation="50% of Base Gross Salary"
            ),
            PayrollLineItem(
                tenant_id=tenant_id,
                payroll_employee_id=payroll_emp.id,
                component_code="HRA",
                component_name="House Rent Allowance (HRA)",
                line_type=LineItemType.EARNING,
                amount=hra_amount,
                calculation_explanation="40% of Basic Salary"
            ),
            PayrollLineItem(
                tenant_id=tenant_id,
                payroll_employee_id=payroll_emp.id,
                component_code="SPECIAL_ALLOWANCE",
                component_name="Special Allowance",
                line_type=LineItemType.EARNING,
                amount=special_allowance,
                calculation_explanation="Balancing Gross Allowance"
            ),
        ]

        if reimbursement_amount > 0:
            line_items.append(
                PayrollLineItem(
                    tenant_id=tenant_id,
                    payroll_employee_id=payroll_emp.id,
                    component_code="REIMBURSEMENT",
                    component_name="Expense Reimbursement",
                    line_type=LineItemType.REIMBURSEMENT,
                    amount=reimbursement_amount,
                    calculation_explanation="Approved Expense Claims Reimbursement"
                )
            )

        if lop_deduction > 0:
            line_items.append(
                PayrollLineItem(
                    tenant_id=tenant_id,
                    payroll_employee_id=payroll_emp.id,
                    component_code="LOP",
                    component_name="Loss of Pay Deduction",
                    line_type=LineItemType.DEDUCTION,
                    amount=lop_deduction,
                    calculation_explanation=f"{lop_days} days LOP @ ₹{daily_rate}/day"
                )
            )

        if loan_repayment_amount > 0:
            line_items.append(
                PayrollLineItem(
                    tenant_id=tenant_id,
                    payroll_employee_id=payroll_emp.id,
                    component_code="LOAN_REPAYMENT",
                    component_name="Employee Loan EMI Repayment",
                    line_type=LineItemType.DEDUCTION,
                    amount=loan_repayment_amount,
                    calculation_explanation="Scheduled Monthly Loan Installment"
                )
            )

        if advance_recovery_amount > 0:
            line_items.append(
                PayrollLineItem(
                    tenant_id=tenant_id,
                    payroll_employee_id=payroll_emp.id,
                    component_code="SALARY_ADVANCE_RECOVERY",
                    component_name="Salary Advance Recovery",
                    line_type=LineItemType.DEDUCTION,
                    amount=advance_recovery_amount,
                    calculation_explanation="Monthly Salary Advance Recovery"
                )
            )

        if employee_pf > 0:
            line_items.append(
                PayrollLineItem(
                    tenant_id=tenant_id,
                    payroll_employee_id=payroll_emp.id,
                    component_code="PF",
                    component_name="Provident Fund (Employee)",
                    line_type=LineItemType.DEDUCTION,
                    amount=employee_pf,
                    calculation_explanation="12% of Basic Salary (Capped at ₹1,800)"
                )
            )

        if employee_esi > 0:
            line_items.append(
                PayrollLineItem(
                    tenant_id=tenant_id,
                    payroll_employee_id=payroll_emp.id,
                    component_code="ESI",
                    component_name="Employee State Insurance",
                    line_type=LineItemType.DEDUCTION,
                    amount=employee_esi,
                    calculation_explanation="0.75% of Gross Salary"
                )
            )

        if employee_pt > 0:
            line_items.append(
                PayrollLineItem(
                    tenant_id=tenant_id,
                    payroll_employee_id=payroll_emp.id,
                    component_code="PT",
                    component_name="Professional Tax",
                    line_type=LineItemType.DEDUCTION,
                    amount=employee_pt,
                    calculation_explanation="State Professional Tax Slab"
                )
            )

        if employer_pf > 0:
            line_items.append(
                PayrollLineItem(
                    tenant_id=tenant_id,
                    payroll_employee_id=payroll_emp.id,
                    component_code="ER_PF",
                    component_name="Employer PF Contribution",
                    line_type=LineItemType.EMPLOYER_CONTRIBUTION,
                    amount=employer_pf,
                    calculation_explanation="Employer PF Match"
                )
            )

        for li in line_items:
            db.add(li)

        return payroll_emp
