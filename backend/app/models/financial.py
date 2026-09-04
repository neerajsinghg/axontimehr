import enum
import uuid
from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Numeric,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class ExpenseCategoryStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ExpenseClaimStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RETURNED = "RETURNED"
    REIMBURSEMENT_PENDING = "REIMBURSEMENT_PENDING"
    REIMBURSED = "REIMBURSED"
    CANCELLED = "CANCELLED"


class ExpenseItemStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ReimbursementMethod(str, enum.Enum):
    PAYROLL = "PAYROLL"
    BANK_TRANSFER = "BANK_TRANSFER"
    MANUAL = "MANUAL"
    OTHER = "OTHER"


class ReimbursementTaxability(str, enum.Enum):
    TAXABLE = "TAXABLE"
    NON_TAXABLE = "NON_TAXABLE"
    PARTIALLY_TAXABLE = "PARTIALLY_TAXABLE"


class ReimbursementStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class InterestType(str, enum.Enum):
    NO_INTEREST = "NO_INTEREST"
    FLAT = "FLAT"
    REDUCING_BALANCE = "REDUCING_BALANCE"


class LoanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISBURSED = "DISBURSED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InstallmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    WAIVED = "WAIVED"
    CANCELLED = "CANCELLED"


class SalaryAdvanceStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DISBURSED = "DISBURSED"
    RECOVERED = "RECOVERED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class RecoveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    RECOVERED = "RECOVERED"
    CANCELLED = "CANCELLED"


class FinancialTransactionType(str, enum.Enum):
    EXPENSE_REIMBURSEMENT = "EXPENSE_REIMBURSEMENT"
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    LOAN_REPAYMENT = "LOAN_REPAYMENT"
    SALARY_ADVANCE = "SALARY_ADVANCE"
    SALARY_ADVANCE_RECOVERY = "SALARY_ADVANCE_RECOVERY"
    ADJUSTMENT = "ADJUSTMENT"
    REVERSAL = "REVERSAL"


class TransactionDirection(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    max_amount = Column(Numeric(14, 2), nullable=True)
    requires_receipt = Column(Boolean, nullable=False, default=True)
    requires_approval = Column(Boolean, nullable=False, default=True)
    taxable = Column(Boolean, nullable=False, default=False)
    status = Column(Enum(ExpenseCategoryStatus, native_enum=False), nullable=False, default=ExpenseCategoryStatus.ACTIVE)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="idx_expense_cat_tenant_code"),
    )


class ExpensePolicy(Base):
    __tablename__ = "expense_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("expense_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    grade = Column(String(50), nullable=True)
    daily_limit = Column(Numeric(14, 2), nullable=True)
    monthly_limit = Column(Numeric(14, 2), nullable=True)
    currency = Column(String(3), nullable=False, default="INR")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    category = relationship("ExpenseCategory", foreign_keys=[category_id])


class ExpenseReceipt(Base):
    __tablename__ = "expense_receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_signature = Column(String(100), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class ExpenseClaim(Base):
    __tablename__ = "expense_claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_number = Column(String(50), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=False)
    total_amount = Column(Numeric(14, 2), nullable=False, default=0.00)
    approved_amount = Column(Numeric(14, 2), nullable=False, default=0.00)
    currency = Column(String(3), nullable=False, default="INR")
    status = Column(Enum(ExpenseClaimStatus, native_enum=False), nullable=False, default=ExpenseClaimStatus.DRAFT, index=True)
    approval_instance_id = Column(UUID(as_uuid=True), ForeignKey("approval_instances.id"), nullable=True)
    reimbursed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    items = relationship("ExpenseItem", back_populates="claim", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "claim_number", name="idx_expense_claim_tenant_number"),
    )


class ExpenseItem(Base):
    __tablename__ = "expense_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("expense_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("expense_categories.id"), nullable=False)
    expense_date = Column(Date, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    merchant = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    receipt_file_id = Column(UUID(as_uuid=True), ForeignKey("expense_receipts.id"), nullable=True)
    project_code = Column(String(50), nullable=True)
    cost_center = Column(String(50), nullable=True)
    status = Column(Enum(ExpenseItemStatus, native_enum=False), nullable=False, default=ExpenseItemStatus.PENDING)
    rejection_reason = Column(Text, nullable=True)

    claim = relationship("ExpenseClaim", back_populates="items")
    category = relationship("ExpenseCategory", foreign_keys=[category_id])
    receipt = relationship("ExpenseReceipt", foreign_keys=[receipt_file_id])


class Reimbursement(Base):
    __tablename__ = "reimbursements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("expense_claims.id", ondelete="CASCADE"), nullable=False, unique=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    payment_method = Column(Enum(ReimbursementMethod, native_enum=False), nullable=False, default=ReimbursementMethod.PAYROLL)
    taxability = Column(Enum(ReimbursementTaxability, native_enum=False), nullable=False, default=ReimbursementTaxability.NON_TAXABLE)
    status = Column(Enum(ReimbursementStatus, native_enum=False), nullable=False, default=ReimbursementStatus.PENDING)
    payroll_period_id = Column(UUID(as_uuid=True), ForeignKey("payroll_periods.id"), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    claim = relationship("ExpenseClaim", foreign_keys=[claim_id])
    employee = relationship("Employee", foreign_keys=[employee_id])


class LoanType(Base):
    __tablename__ = "loan_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    max_amount = Column(Numeric(14, 2), nullable=False, default=100000.00)
    min_service_months = Column(Integer, nullable=False, default=6)
    max_salary_multiple = Column(Numeric(5, 2), nullable=False, default=3.00)
    interest_rate = Column(Numeric(5, 2), nullable=False, default=0.00)
    interest_type = Column(Enum(InterestType, native_enum=False), nullable=False, default=InterestType.NO_INTEREST)
    status = Column(String(20), nullable=False, default="ACTIVE")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="idx_loan_type_tenant_code"),
    )


class LoanPolicy(Base):
    __tablename__ = "loan_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_type_id = Column(UUID(as_uuid=True), ForeignKey("loan_types.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    max_active_loans = Column(Integer, nullable=False, default=1)
    allow_prepayment = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class EmployeeLoan(Base):
    __tablename__ = "employee_loans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_number = Column(String(50), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_type_id = Column(UUID(as_uuid=True), ForeignKey("loan_types.id"), nullable=False)
    principal_amount = Column(Numeric(14, 2), nullable=False)
    approved_principal = Column(Numeric(14, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False, default=0.00)
    interest_type = Column(Enum(InterestType, native_enum=False), nullable=False, default=InterestType.NO_INTEREST)
    tenure_months = Column(Integer, nullable=False)
    monthly_installment = Column(Numeric(14, 2), nullable=False, default=0.00)
    status = Column(Enum(LoanStatus, native_enum=False), nullable=False, default=LoanStatus.DRAFT, index=True)
    approval_instance_id = Column(UUID(as_uuid=True), ForeignKey("approval_instances.id"), nullable=True)
    disbursed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    loan_type = relationship("LoanType", foreign_keys=[loan_type_id])
    installments = relationship("LoanInstallment", back_populates="loan", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "loan_number", name="idx_loan_tenant_number"),
    )


class LoanInstallment(Base):
    __tablename__ = "loan_installments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("employee_loans.id", ondelete="CASCADE"), nullable=False, index=True)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    principal_amount = Column(Numeric(14, 2), nullable=False)
    interest_amount = Column(Numeric(14, 2), nullable=False, default=0.00)
    total_amount = Column(Numeric(14, 2), nullable=False)
    paid_amount = Column(Numeric(14, 2), nullable=False, default=0.00)
    remaining_amount = Column(Numeric(14, 2), nullable=False)
    status = Column(Enum(InstallmentStatus, native_enum=False), nullable=False, default=InstallmentStatus.PENDING)
    payroll_employee_id = Column(UUID(as_uuid=True), ForeignKey("payroll_employees.id"), nullable=True)

    loan = relationship("EmployeeLoan", back_populates="installments")


class SalaryAdvance(Base):
    __tablename__ = "salary_advances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    advance_number = Column(String(50), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    approved_amount = Column(Numeric(14, 2), nullable=False)
    recovery_months = Column(Integer, nullable=False, default=1)
    monthly_recovery_amount = Column(Numeric(14, 2), nullable=False)
    status = Column(Enum(SalaryAdvanceStatus, native_enum=False), nullable=False, default=SalaryAdvanceStatus.PENDING)
    approval_instance_id = Column(UUID(as_uuid=True), ForeignKey("approval_instances.id"), nullable=True)
    disbursed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    recoveries = relationship("AdvanceRecovery", back_populates="advance", cascade="all, delete-orphan")


class AdvanceRecovery(Base):
    __tablename__ = "advance_recoveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    advance_id = Column(UUID(as_uuid=True), ForeignKey("salary_advances.id", ondelete="CASCADE"), nullable=False, index=True)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    recovered_amount = Column(Numeric(14, 2), nullable=False, default=0.00)
    status = Column(Enum(RecoveryStatus, native_enum=False), nullable=False, default=RecoveryStatus.PENDING)
    payroll_employee_id = Column(UUID(as_uuid=True), ForeignKey("payroll_employees.id"), nullable=True)

    advance = relationship("SalaryAdvance", back_populates="recoveries")


class EmployeeFinancialTransaction(Base):
    __tablename__ = "employee_financial_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    transaction_type = Column(Enum(FinancialTransactionType, native_enum=False), nullable=False)
    reference_id = Column(String(100), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    direction = Column(Enum(TransactionDirection, native_enum=False), nullable=False)
    transaction_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    cost_center = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    department = relationship("Department", foreign_keys=[department_id])
