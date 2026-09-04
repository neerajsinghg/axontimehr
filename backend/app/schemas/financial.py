from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models.financial import (
    ExpenseCategoryStatus,
    ExpenseClaimStatus,
    ExpenseItemStatus,
    ReimbursementMethod,
    ReimbursementTaxability,
    ReimbursementStatus,
    InterestType,
    LoanStatus,
    InstallmentStatus,
    SalaryAdvanceStatus,
    RecoveryStatus,
    FinancialTransactionType,
    TransactionDirection
)


# --- Category & Policy Schemas ---
class ExpenseCategoryCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    max_amount: Optional[Decimal] = None
    requires_receipt: bool = True
    requires_approval: bool = True
    taxable: bool = False
    status: ExpenseCategoryStatus = ExpenseCategoryStatus.ACTIVE
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class ExpenseCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    max_amount: Optional[Decimal] = None
    requires_receipt: bool
    requires_approval: bool
    taxable: bool
    status: ExpenseCategoryStatus
    created_at: datetime
    updated_at: datetime


class ExpensePolicyCreate(BaseModel):
    category_id: UUID
    department_id: Optional[UUID] = None
    grade: Optional[str] = None
    daily_limit: Optional[Decimal] = None
    monthly_limit: Optional[Decimal] = None
    currency: str = "INR"


class ExpensePolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    category_id: UUID
    department_id: Optional[UUID] = None
    grade: Optional[str] = None
    daily_limit: Optional[Decimal] = None
    monthly_limit: Optional[Decimal] = None
    currency: str
    created_at: datetime


# --- Expense Claim & Item Schemas ---
class ExpenseItemCreate(BaseModel):
    category_id: UUID
    expense_date: date
    amount: Decimal
    merchant: str
    description: Optional[str] = None
    location: Optional[str] = None
    receipt_file_id: Optional[UUID] = None
    project_code: Optional[str] = None
    cost_center: Optional[str] = None


class ExpenseItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    claim_id: UUID
    category_id: UUID
    category_name: Optional[str] = None
    category_code: Optional[str] = None
    expense_date: date
    amount: Decimal
    merchant: str
    description: Optional[str] = None
    location: Optional[str] = None
    receipt_file_id: Optional[UUID] = None
    project_code: Optional[str] = None
    cost_center: Optional[str] = None
    status: ExpenseItemStatus
    rejection_reason: Optional[str] = None


class ExpenseClaimCreate(BaseModel):
    claim_date: date
    description: str
    currency: str = "INR"
    items: List[ExpenseItemCreate]


class ExpenseClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    claim_number: str
    employee_id: UUID
    employee_name: Optional[str] = None
    claim_date: date
    description: str
    total_amount: Decimal
    approved_amount: Decimal
    currency: str
    status: ExpenseClaimStatus
    approval_instance_id: Optional[UUID] = None
    reimbursed_at: Optional[datetime] = None
    items: List[ExpenseItemResponse] = []
    created_at: datetime
    updated_at: datetime


class ReceiptUploadResponse(BaseModel):
    id: UUID
    file_name: str
    file_path: str
    content_type: str
    file_size: int


class ReimbursementProcessRequest(BaseModel):
    payment_method: ReimbursementMethod = ReimbursementMethod.PAYROLL
    taxability: ReimbursementTaxability = ReimbursementTaxability.NON_TAXABLE
    payroll_period_id: Optional[UUID] = None


class ReimbursementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    claim_id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None
    amount: Decimal
    payment_method: ReimbursementMethod
    taxability: ReimbursementTaxability
    status: ReimbursementStatus
    payroll_period_id: Optional[UUID] = None
    processed_at: Optional[datetime] = None
    created_at: datetime


# --- Loan Schemas ---
class LoanTypeCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    max_amount: Decimal = Decimal("100000.00")
    min_service_months: int = 6
    max_salary_multiple: Decimal = Decimal("3.00")
    interest_rate: Decimal = Decimal("0.00")
    interest_type: InterestType = InterestType.NO_INTEREST


class LoanTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    max_amount: Decimal
    min_service_months: int
    max_salary_multiple: Decimal
    interest_rate: Decimal
    interest_type: InterestType
    status: str
    created_at: datetime


class EmployeeLoanCreate(BaseModel):
    loan_type_id: UUID
    principal_amount: Decimal
    tenure_months: int


class LoanInstallmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    loan_id: UUID
    installment_number: int
    due_date: date
    principal_amount: Decimal
    interest_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    status: InstallmentStatus


class EmployeeLoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    loan_number: str
    employee_id: UUID
    employee_name: Optional[str] = None
    loan_type_id: UUID
    loan_type_name: Optional[str] = None
    principal_amount: Decimal
    approved_principal: Decimal
    interest_rate: Decimal
    interest_type: InterestType
    tenure_months: int
    monthly_installment: Decimal
    status: LoanStatus
    approval_instance_id: Optional[UUID] = None
    disbursed_at: Optional[datetime] = None
    installments: List[LoanInstallmentResponse] = []
    created_at: datetime


class LoanPrepayRequest(BaseModel):
    amount: Decimal


class LoanPauseRequest(BaseModel):
    reason: str


# --- Salary Advance Schemas ---
class SalaryAdvanceCreate(BaseModel):
    amount: Decimal
    recovery_months: int = 1


class AdvanceRecoveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    advance_id: UUID
    installment_number: int
    due_date: date
    amount: Decimal
    recovered_amount: Decimal
    status: RecoveryStatus


class SalaryAdvanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    advance_number: str
    employee_id: UUID
    employee_name: Optional[str] = None
    amount: Decimal
    approved_amount: Decimal
    recovery_months: int
    monthly_recovery_amount: Decimal
    status: SalaryAdvanceStatus
    approval_instance_id: Optional[UUID] = None
    disbursed_at: Optional[datetime] = None
    recoveries: List[AdvanceRecoveryResponse] = []
    created_at: datetime


# --- Transaction & Report Schemas ---
class FinancialTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    transaction_type: FinancialTransactionType
    reference_id: str
    amount: Decimal
    currency: str
    direction: TransactionDirection
    transaction_date: datetime
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    cost_center: Optional[str] = None


class FinancialDashboardSummaryResponse(BaseModel):
    total_claims_count: int
    pending_claims_amount: Decimal
    approved_reimbursements_amount: Decimal
    total_active_loans_count: int
    outstanding_loans_principal: Decimal
    monthly_loan_recovery_expected: Decimal
    total_active_advances_count: int
    outstanding_advances_amount: Decimal
