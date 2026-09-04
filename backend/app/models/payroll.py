import enum
import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Date,
    Integer,
    Numeric,
    Text,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class ComponentType(str, enum.Enum):
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"
    EMPLOYER_CONTRIBUTION = "EMPLOYER_CONTRIBUTION"
    REIMBURSEMENT = "REIMBURSEMENT"
    TAX = "TAX"


class CalculationType(str, enum.Enum):
    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"
    FORMULA = "FORMULA"
    VARIABLE = "VARIABLE"


class SalaryAssignmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"


class PayrollPeriodStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    LOCKED = "LOCKED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PayrollRunStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    LOCKED = "LOCKED"
    PAID = "PAID"


class PayrollEmployeeStatus(str, enum.Enum):
    PROCESSED = "PROCESSED"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LineItemType(str, enum.Enum):
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"
    EMPLOYER_CONTRIBUTION = "EMPLOYER_CONTRIBUTION"
    TAX = "TAX"
    REIMBURSEMENT = "REIMBURSEMENT"


class AdjustmentType(str, enum.Enum):
    ARREARS = "ARREARS"
    BONUS = "BONUS"
    INCENTIVE = "INCENTIVE"
    DEDUCTION = "DEDUCTION"
    CORRECTION = "CORRECTION"


class AdjustmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class SalaryComponent(Base):
    __tablename__ = "salary_components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    component_type = Column(SQLEnum(ComponentType), nullable=False, default=ComponentType.EARNING)
    calculation_type = Column(SQLEnum(CalculationType), nullable=False, default=CalculationType.FIXED)
    percentage = Column(Numeric(5, 2), nullable=True)
    fixed_amount = Column(Numeric(14, 2), nullable=True)
    formula = Column(String(255), nullable=True)
    taxable = Column(Boolean, default=True)
    included_in_ctc = Column(Boolean, default=True)
    affects_gross = Column(Boolean, default=True)
    affects_net = Column(Boolean, default=True)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    components = relationship("SalaryStructureComponent", back_populates="structure", cascade="all, delete-orphan")


class SalaryStructureComponent(Base):
    __tablename__ = "salary_structure_components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    structure_id = Column(UUID(as_uuid=True), ForeignKey("salary_structures.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    component_id = Column(UUID(as_uuid=True), ForeignKey("salary_components.id"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    calculation_type = Column(SQLEnum(CalculationType), nullable=False, default=CalculationType.FIXED)
    amount = Column(Numeric(14, 2), nullable=True)
    percentage = Column(Numeric(5, 2), nullable=True)
    formula = Column(String(255), nullable=True)

    structure = relationship("SalaryStructure", back_populates="components")
    component = relationship("SalaryComponent")


class EmployeeSalaryAssignment(Base):
    __tablename__ = "employee_salary_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    salary_structure_id = Column(UUID(as_uuid=True), ForeignKey("salary_structures.id"), nullable=False) if hasattr(uuid, "uuid4") else Column(String)
    annual_ctc = Column(Numeric(14, 2), nullable=False, default=0.0)
    monthly_ctc = Column(Numeric(14, 2), nullable=False, default=0.0)
    gross_salary = Column(Numeric(14, 2), nullable=False, default=0.0)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    version = Column(Integer, default=1)
    status = Column(SQLEnum(SalaryAssignmentStatus), default=SalaryAssignmentStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee")
    structure = relationship("SalaryStructure")


class PayrollPeriod(Base):
    __tablename__ = "payroll_periods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    name = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    status = Column(SQLEnum(PayrollPeriodStatus), default=PayrollPeriodStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    period_id = Column(UUID(as_uuid=True), ForeignKey("payroll_periods.id"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True) if hasattr(uuid, "uuid4") else Column(String)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=True) if hasattr(uuid, "uuid4") else Column(String)
    total_employees = Column(Integer, default=0)
    total_gross = Column(Numeric(14, 2), default=0.0)
    total_deductions = Column(Numeric(14, 2), default=0.0)
    total_net = Column(Numeric(14, 2), default=0.0)
    status = Column(SQLEnum(PayrollRunStatus), default=PayrollRunStatus.PROCESSING)
    approval_instance_id = Column(UUID(as_uuid=True), ForeignKey("approval_instances.id"), nullable=True) if hasattr(uuid, "uuid4") else Column(String)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    period = relationship("PayrollPeriod")
    payroll_employees = relationship("PayrollEmployee", back_populates="payroll_run", cascade="all, delete-orphan")


class PayrollEmployee(Base):
    __tablename__ = "payroll_employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    payroll_run_id = Column(UUID(as_uuid=True), ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)

    calendar_days = Column(Integer, default=30)
    working_days = Column(Integer, default=22)
    present_days = Column(Numeric(5, 2), default=0.0)
    paid_leave_days = Column(Numeric(5, 2), default=0.0)
    unpaid_leave_days = Column(Numeric(5, 2), default=0.0)
    lop_days = Column(Numeric(5, 2), default=0.0)
    holiday_days = Column(Numeric(5, 2), default=0.0)
    overtime_hours = Column(Numeric(5, 2), default=0.0)

    gross_salary = Column(Numeric(14, 2), default=0.0)
    total_earnings = Column(Numeric(14, 2), default=0.0)
    total_deductions = Column(Numeric(14, 2), default=0.0)
    employer_contributions = Column(Numeric(14, 2), default=0.0)
    net_salary = Column(Numeric(14, 2), default=0.0)

    status = Column(SQLEnum(PayrollEmployeeStatus), default=PayrollEmployeeStatus.PROCESSED)
    exception_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    payroll_run = relationship("PayrollRun", back_populates="payroll_employees")
    employee = relationship("Employee")
    line_items = relationship("PayrollLineItem", back_populates="payroll_employee", cascade="all, delete-orphan")


class PayrollLineItem(Base):
    __tablename__ = "payroll_line_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    payroll_employee_id = Column(UUID(as_uuid=True), ForeignKey("payroll_employees.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    component_code = Column(String(50), nullable=False)
    component_name = Column(String(100), nullable=False)
    line_type = Column(SQLEnum(LineItemType), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False, default=0.0)
    calculation_explanation = Column(Text, nullable=True)

    payroll_employee = relationship("PayrollEmployee", back_populates="line_items")


class PayrollAdjustment(Base):
    __tablename__ = "payroll_adjustments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    adjustment_type = Column(SQLEnum(AdjustmentType), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    reason = Column(Text, nullable=False)
    payroll_period_id = Column(UUID(as_uuid=True), ForeignKey("payroll_periods.id"), nullable=True) if hasattr(uuid, "uuid4") else Column(String)
    approval_instance_id = Column(UUID(as_uuid=True), ForeignKey("approval_instances.id"), nullable=True) if hasattr(uuid, "uuid4") else Column(String)
    status = Column(SQLEnum(AdjustmentStatus), default=AdjustmentStatus.PENDING)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) if hasattr(uuid, "uuid4") else Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    employee = relationship("Employee")


class StatutoryRule(Base):
    __tablename__ = "statutory_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    rule_code = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    rule_config = Column(JSON, nullable=False)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) if hasattr(uuid, "uuid4") else Column(String, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    payroll_employee_id = Column(UUID(as_uuid=True), ForeignKey("payroll_employees.id"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    period_id = Column(UUID(as_uuid=True), ForeignKey("payroll_periods.id"), nullable=False, index=True) if hasattr(uuid, "uuid4") else Column(String)
    pdf_path = Column(String(500), nullable=True)
    download_token = Column(String(100), nullable=False, index=True)
    download_count = Column(Integer, default=0)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    employee = relationship("Employee")
    period = relationship("PayrollPeriod")
