from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.models.payroll import (
    ComponentType,
    CalculationType,
    SalaryAssignmentStatus,
    PayrollPeriodStatus,
    PayrollRunStatus,
    PayrollEmployeeStatus,
    LineItemType,
    AdjustmentType,
    AdjustmentStatus,
)


class SalaryComponentCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    component_type: ComponentType = ComponentType.EARNING
    calculation_type: CalculationType = CalculationType.FIXED
    percentage: Optional[float] = None
    fixed_amount: Optional[float] = None
    formula: Optional[str] = None
    taxable: bool = True
    included_in_ctc: bool = True
    affects_gross: bool = True
    affects_net: bool = True
    status: str = "ACTIVE"

    model_config = {"from_attributes": True, "use_enum_values": True}


class SalaryComponentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    component_type: ComponentType
    calculation_type: CalculationType
    percentage: Optional[float] = None
    fixed_amount: Optional[float] = None
    formula: Optional[str] = None
    taxable: bool
    included_in_ctc: bool
    affects_gross: bool
    affects_net: bool
    status: str
    created_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}


class SalaryStructureComponentItem(BaseModel):
    component_id: UUID
    calculation_type: CalculationType = CalculationType.FIXED
    amount: Optional[float] = None
    percentage: Optional[float] = None
    formula: Optional[str] = None

    model_config = {"from_attributes": True, "use_enum_values": True}


class SalaryStructureCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    components: List[SalaryStructureComponentItem] = []

    model_config = {"from_attributes": True, "use_enum_values": True}


class SalaryStructureComponentResponse(BaseModel):
    id: UUID
    component_id: UUID
    component_code: Optional[str] = None
    component_name: Optional[str] = None
    component_type: Optional[ComponentType] = None
    calculation_type: CalculationType
    amount: Optional[float] = None
    percentage: Optional[float] = None
    formula: Optional[str] = None

    model_config = {"from_attributes": True, "use_enum_values": True}


class SalaryStructureResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    status: str
    components: List[SalaryStructureComponentResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}


class EmployeeSalaryAssignmentCreate(BaseModel):
    employee_id: UUID
    salary_structure_id: UUID
    annual_ctc: float
    effective_from: date

    model_config = {"from_attributes": True, "use_enum_values": True}


class EmployeeSalaryAssignmentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    salary_structure_id: UUID
    structure_name: Optional[str] = None
    annual_ctc: float
    monthly_ctc: float
    gross_salary: float
    effective_from: date
    effective_to: Optional[date] = None
    version: int
    status: SalaryAssignmentStatus
    created_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayrollPeriodCreate(BaseModel):
    name: str = Field(..., max_length=100)
    year: int
    month: int
    start_date: date
    end_date: date
    pay_date: date

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayrollPeriodResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    year: int
    month: int
    start_date: date
    end_date: date
    pay_date: date
    status: PayrollPeriodStatus
    created_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayrollRunCreate(BaseModel):
    period_id: UUID
    organization_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayrollLineItemResponse(BaseModel):
    id: UUID
    component_code: str
    component_name: str
    line_type: LineItemType
    amount: float
    calculation_explanation: Optional[str] = None

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayrollEmployeeResponse(BaseModel):
    id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    calendar_days: int
    working_days: int
    present_days: float
    paid_leave_days: float
    unpaid_leave_days: float
    lop_days: float
    holiday_days: float
    overtime_hours: float
    gross_salary: float
    total_earnings: float
    total_deductions: float
    employer_contributions: float
    net_salary: float
    status: PayrollEmployeeStatus
    exception_message: Optional[str] = None
    line_items: List[PayrollLineItemResponse] = []

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayrollRunResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    period_id: UUID
    period_name: Optional[str] = None
    total_employees: int
    total_gross: float
    total_deductions: float
    total_net: float
    status: PayrollRunStatus
    approval_instance_id: Optional[UUID] = None
    locked_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    employees: List[PayrollEmployeeResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayrollAdjustmentCreate(BaseModel):
    employee_id: UUID
    adjustment_type: AdjustmentType
    amount: float
    reason: str
    payroll_period_id: Optional[UUID] = None

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayrollAdjustmentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None
    adjustment_type: AdjustmentType
    amount: float
    reason: str
    status: AdjustmentStatus
    created_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}


class PayslipResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    payroll_employee_id: UUID
    employee_id: UUID
    period_id: UUID
    period_name: str
    pdf_path: Optional[str] = None
    download_token: str
    download_count: int
    generated_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}
