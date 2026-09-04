import uuid
from typing import List, Optional, Tuple
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.financial import (
    LoanType,
    LoanPolicy,
    EmployeeLoan,
    LoanInstallment,
    InterestType,
    LoanStatus,
    InstallmentStatus,
    FinancialTransactionType,
    TransactionDirection
)
from app.models.employee import Employee
from app.models.payroll import EmployeeSalaryAssignment, SalaryAssignmentStatus
from app.schemas.financial import LoanTypeCreate, EmployeeLoanCreate
from app.services.workflow_service import WorkflowService
from app.services.financial_transaction_service import FinancialTransactionService
from app.services.audit_service import AuditService


class LoanService:

    @staticmethod
    async def create_loan_type(db: AsyncSession, tenant_id: uuid.UUID, data: LoanTypeCreate) -> LoanType:
        existing = await db.execute(
            select(LoanType).where(
                and_(LoanType.tenant_id == tenant_id, LoanType.code == data.code)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Loan type code '{data.code}' already exists."
            )

        lt = LoanType(
            tenant_id=tenant_id,
            code=data.code,
            name=data.name,
            description=data.description,
            max_amount=data.max_amount,
            min_service_months=data.min_service_months,
            max_salary_multiple=data.max_salary_multiple,
            interest_rate=data.interest_rate,
            interest_type=data.interest_type
        )
        db.add(lt)
        await db.commit()
        await db.refresh(lt)
        return lt

    @staticmethod
    async def get_loan_types(db: AsyncSession, tenant_id: uuid.UUID) -> List[LoanType]:
        res = await db.execute(
            select(LoanType).where(LoanType.tenant_id == tenant_id).order_by(LoanType.name)
        )
        ltypes = list(res.scalars().all())
        if not ltypes:
            default_ltypes = [
                LoanType(
                    tenant_id=tenant_id,
                    code="EMERGENCY",
                    name="Personal Emergency Loan",
                    description="Interest-free short term loan for personal family emergencies",
                    max_amount=Decimal("200000.00"),
                    min_service_months=3,
                    max_salary_multiple=Decimal("3.00"),
                    interest_rate=Decimal("0.00"),
                    interest_type=InterestType.NO_INTEREST,
                    status="ACTIVE"
                ),
                LoanType(
                    tenant_id=tenant_id,
                    code="VEHICLE",
                    name="Two-Wheeler / Bike Loan",
                    description="Concessional interest loan for purchasing two-wheelers for commute",
                    max_amount=Decimal("150000.00"),
                    min_service_months=6,
                    max_salary_multiple=Decimal("4.00"),
                    interest_rate=Decimal("5.00"),
                    interest_type=InterestType.REDUCING_BALANCE,
                    status="ACTIVE"
                ),
                LoanType(
                    tenant_id=tenant_id,
                    code="EQUIPMENT",
                    name="Laptop & Appliance Loan",
                    description="Subsidized loan for purchasing work appliances, laptops, and devices",
                    max_amount=Decimal("100000.00"),
                    min_service_months=6,
                    max_salary_multiple=Decimal("2.00"),
                    interest_rate=Decimal("3.00"),
                    interest_type=InterestType.FLAT,
                    status="ACTIVE"
                ),
                LoanType(
                    tenant_id=tenant_id,
                    code="EDUCATION",
                    name="Higher Education Loan",
                    description="Long term zero-interest support for employee upskilling & certifications",
                    max_amount=Decimal("300000.00"),
                    min_service_months=6,
                    max_salary_multiple=Decimal("5.00"),
                    interest_rate=Decimal("0.00"),
                    interest_type=InterestType.NO_INTEREST,
                    status="ACTIVE"
                )
            ]
            for lt in default_ltypes:
                db.add(lt)
            await db.commit()

            res_new = await db.execute(
                select(LoanType).where(LoanType.tenant_id == tenant_id).order_by(LoanType.name)
            )
            ltypes = list(res_new.scalars().all())

        return ltypes

    @staticmethod
    def calculate_schedule(
        principal: Decimal,
        annual_rate: Decimal,
        interest_type: InterestType,
        tenure_months: int,
        start_date: date
    ) -> Tuple[Decimal, List[dict]]:
        """
        Calculates repayment installments for FLAT or REDUCING_BALANCE interest.
        Returns (monthly_installment, installments_data_list).
        """
        installments = []
        p = principal
        n = tenure_months

        if interest_type == InterestType.NO_INTEREST or annual_rate == Decimal("0.00"):
            emi = (p / Decimal(n)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            rem = p
            for i in range(1, n + 1):
                p_amt = emi if i < n else rem
                due = start_date + timedelta(days=30 * i)
                rem -= p_amt
                installments.append({
                    "number": i,
                    "due_date": due,
                    "principal": p_amt,
                    "interest": Decimal("0.00"),
                    "total": p_amt,
                    "remaining": rem
                })
            return emi, installments

        elif interest_type == InterestType.FLAT:
            total_interest = (p * (annual_rate / Decimal("100.00")) * (Decimal(n) / Decimal("12.00"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            monthly_principal = (p / Decimal(n)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            monthly_interest = (total_interest / Decimal(n)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            emi = monthly_principal + monthly_interest

            rem = p
            for i in range(1, n + 1):
                p_amt = monthly_principal if i < n else rem
                due = start_date + timedelta(days=30 * i)
                rem -= p_amt
                installments.append({
                    "number": i,
                    "due_date": due,
                    "principal": p_amt,
                    "interest": monthly_interest,
                    "total": p_amt + monthly_interest,
                    "remaining": rem
                })
            return emi, installments

        else:  # REDUCING_BALANCE
            r = (annual_rate / Decimal("1200.00"))
            # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
            compound = (Decimal(1) + r) ** n
            emi = (p * r * compound / (compound - Decimal(1))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            rem = p
            for i in range(1, n + 1):
                i_amt = (rem * r).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                p_amt = emi - i_amt
                if i == n or rem - p_amt < Decimal("0.00"):
                    p_amt = rem
                rem -= p_amt
                due = start_date + timedelta(days=30 * i)
                installments.append({
                    "number": i,
                    "due_date": due,
                    "principal": p_amt,
                    "interest": i_amt,
                    "total": p_amt + i_amt,
                    "remaining": max(Decimal("0.00"), rem)
                })
            return emi, installments

    @staticmethod
    async def request_loan(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        data: EmployeeLoanCreate
    ) -> EmployeeLoan:
        # Resolve loan type
        lt_res = await db.execute(
            select(LoanType).where(
                and_(LoanType.id == data.loan_type_id, LoanType.tenant_id == tenant_id)
            )
        )
        lt = lt_res.scalar_one_or_none()
        if not lt or lt.status != "ACTIVE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or inactive loan type.")

        if data.principal_amount > lt.max_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested amount {data.principal_amount} exceeds loan limit of {lt.max_amount}."
            )

        # Check salary multiple eligibility
        sal_res = await db.execute(
            select(EmployeeSalaryAssignment).where(
                and_(
                    EmployeeSalaryAssignment.tenant_id == tenant_id,
                    EmployeeSalaryAssignment.employee_id == employee_id,
                    EmployeeSalaryAssignment.status == SalaryAssignmentStatus.ACTIVE
                )
            )
        )
        sal = sal_res.scalars().first()
        monthly_gross = Decimal(str(sal.monthly_ctc)) if sal else Decimal("50000.00")
        max_allowed = monthly_gross * lt.max_salary_multiple

        if data.principal_amount > max_allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested amount exceeds eligible limit of {max_allowed} ({lt.max_salary_multiple}x monthly salary)."
            )

        loan_number = f"LOAN-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
        emi, schedule_items = LoanService.calculate_schedule(
            principal=data.principal_amount,
            annual_rate=lt.interest_rate,
            interest_type=lt.interest_type,
            tenure_months=data.tenure_months,
            start_date=date.today()
        )

        loan = EmployeeLoan(
            tenant_id=tenant_id,
            loan_number=loan_number,
            employee_id=employee_id,
            loan_type_id=data.loan_type_id,
            principal_amount=data.principal_amount,
            approved_principal=data.principal_amount,
            interest_rate=lt.interest_rate,
            interest_type=lt.interest_type,
            tenure_months=data.tenure_months,
            monthly_installment=emi,
            status=LoanStatus.SUBMITTED
        )
        db.add(loan)
        await db.flush()

        for item in schedule_items:
            inst = LoanInstallment(
                tenant_id=tenant_id,
                loan_id=loan.id,
                installment_number=item["number"],
                due_date=item["due_date"],
                principal_amount=item["principal"],
                interest_amount=item["interest"],
                total_amount=item["total"],
                paid_amount=Decimal("0.00"),
                remaining_amount=item["total"],
                status=InstallmentStatus.PENDING
            )
            db.add(inst)

        instance = await WorkflowService.start_approval_instance(
            db, tenant_id, "EMPLOYEE_LOAN", loan.id, employee_id
        )
        loan.approval_instance_id = instance.id

        await db.commit()
        
        res_full = await db.execute(
            select(EmployeeLoan)
            .options(selectinload(EmployeeLoan.installments))
            .where(EmployeeLoan.id == loan.id)
        )
        return res_full.scalar_one()

    @staticmethod
    async def approve_loan(db: AsyncSession, tenant_id: uuid.UUID, loan_id: uuid.UUID) -> EmployeeLoan:
        res = await db.execute(
            select(EmployeeLoan).where(
                and_(EmployeeLoan.id == loan_id, EmployeeLoan.tenant_id == tenant_id)
            )
        )
        loan = res.scalar_one_or_none()
        if not loan or loan.status not in (LoanStatus.SUBMITTED, LoanStatus.UNDER_REVIEW):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan not found or not pending approval.")

        loan.status = LoanStatus.APPROVED
        await db.commit()

        res_full = await db.execute(
            select(EmployeeLoan)
            .options(selectinload(EmployeeLoan.installments))
            .where(EmployeeLoan.id == loan.id)
        )
        return res_full.scalar_one()

    @staticmethod
    async def disburse_loan(db: AsyncSession, tenant_id: uuid.UUID, loan_id: uuid.UUID) -> EmployeeLoan:
        res = await db.execute(
            select(EmployeeLoan).where(
                and_(EmployeeLoan.id == loan_id, EmployeeLoan.tenant_id == tenant_id)
            )
        )
        loan = res.scalar_one_or_none()
        if not loan or loan.status != LoanStatus.APPROVED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan not approved or already disbursed.")

        loan.status = LoanStatus.ACTIVE
        loan.disbursed_at = datetime.now(timezone.utc)

        await FinancialTransactionService.record_transaction(
            db=db,
            tenant_id=tenant_id,
            employee_id=loan.employee_id,
            transaction_type=FinancialTransactionType.LOAN_DISBURSEMENT,
            reference_id=str(loan.id),
            amount=loan.approved_principal,
            direction=TransactionDirection.CREDIT
        )

        await db.commit()

        res_full = await db.execute(
            select(EmployeeLoan)
            .options(selectinload(EmployeeLoan.installments))
            .where(EmployeeLoan.id == loan.id)
        )
        return res_full.scalar_one()

    @staticmethod
    async def prepay_loan(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        loan_id: uuid.UUID,
        amount: Decimal
    ) -> EmployeeLoan:
        res = await db.execute(
            select(EmployeeLoan)
            .options(selectinload(EmployeeLoan.installments))
            .where(and_(EmployeeLoan.id == loan_id, EmployeeLoan.tenant_id == tenant_id))
        )
        loan = res.scalar_one_or_none()
        if not loan or loan.status != LoanStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan is not active for prepayment.")

        rem_prepay = amount
        for inst in sorted(loan.installments, key=lambda x: x.installment_number):
            if inst.status == InstallmentStatus.PENDING:
                due = inst.total_amount - inst.paid_amount
                if rem_prepay >= due:
                    inst.paid_amount += due
                    inst.remaining_amount = Decimal("0.00")
                    inst.status = InstallmentStatus.PAID
                    rem_prepay -= due
                else:
                    inst.paid_amount += rem_prepay
                    inst.remaining_amount -= rem_prepay
                    inst.status = InstallmentStatus.PARTIALLY_PAID
                    rem_prepay = Decimal("0.00")
                    break

        all_paid = all(i.status == InstallmentStatus.PAID for i in loan.installments)
        if all_paid:
            loan.status = LoanStatus.COMPLETED

        await FinancialTransactionService.record_transaction(
            db=db,
            tenant_id=tenant_id,
            employee_id=loan.employee_id,
            transaction_type=FinancialTransactionType.LOAN_REPAYMENT,
            reference_id=str(loan.id),
            amount=amount,
            direction=TransactionDirection.DEBIT
        )

        await db.commit()

        res_full = await db.execute(
            select(EmployeeLoan)
            .options(selectinload(EmployeeLoan.installments))
            .where(EmployeeLoan.id == loan.id)
        )
        return res_full.scalar_one()
