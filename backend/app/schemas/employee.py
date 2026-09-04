from datetime import date, datetime
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator
from app.schemas.organization import DepartmentResponse, DesignationResponse, BranchResponse

class ManagerSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    employee_id: str
    first_name: str
    last_name: str
    email: str
    designation_name: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_from_employee_model(cls, data: Any) -> Any:
        if hasattr(data, "id") and hasattr(data, "first_name"):
            desig_name = None
            if hasattr(data, "designation") and data.designation is not None:
                desig_name = getattr(data.designation, "name", None)
            return {
                "id": data.id,
                "employee_id": getattr(data, "employee_id", ""),
                "first_name": getattr(data, "first_name", ""),
                "last_name": getattr(data, "last_name", ""),
                "email": getattr(data, "email", ""),
                "designation_name": desig_name
            }
        return data

class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    is_active: bool
    is_verified: bool

class EmployeeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    employee_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    display_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    joining_date: date
    employment_type: str
    employee_category: Optional[str] = None
    status: str
    avatar_url: Optional[str] = None
    department: Optional[DepartmentResponse] = None
    designation: Optional[DesignationResponse] = None
    branch: Optional[BranchResponse] = None
    manager: Optional[ManagerSummary] = None
    user: Optional[UserSummary] = None

class EmployeeDetailResponse(EmployeeSummary):
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    personal_email: Optional[str] = None
    personal_phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    date_of_confirmation: Optional[date] = None
    date_of_leaving: Optional[date] = None

class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    gender: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    
    email: EmailStr = Field(...) # Work email
    personal_email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50) # Work phone
    personal_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact: Optional[str] = Field(None, max_length=500)
    
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)

    joining_date: date
    date_of_confirmation: Optional[date] = None
    employment_type: str = Field("FULL_TIME", max_length=50)
    employee_category: Optional[str] = Field("PERMANENT", max_length=50)
    status: str = Field("ACTIVE", max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)

    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    user_id: Optional[UUID] = None

    # Option to auto-create user login account
    create_user_account: bool = False
    user_password: Optional[str] = Field(None, min_length=8)

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    gender: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    
    email: Optional[EmailStr] = None
    personal_email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    personal_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact: Optional[str] = Field(None, max_length=500)
    
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)

    joining_date: Optional[date] = None
    date_of_confirmation: Optional[date] = None
    date_of_leaving: Optional[date] = None
    employment_type: Optional[str] = Field(None, max_length=50)
    employee_category: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)

    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    user_id: Optional[UUID] = None

class EmployeeStatusUpdate(BaseModel):
    status: str = Field(..., max_length=50, description="Status: ACTIVE, PROBATION, ON_NOTICE, ON_LEAVE, SUSPENDED, INACTIVE, TERMINATED, RESIGNED, RETIRED")
    date_of_leaving: Optional[date] = None

class EmployeeListResponse(BaseModel):
    success: bool = True
    data: List[EmployeeSummary]
    total: int
    page: int
    limit: int
    total_pages: int
    request_id: Optional[str] = None

class DepartmentStat(BaseModel):
    department_name: str
    count: int

class EmployeeStatsResponse(BaseModel):
    success: bool = True
    total_employees: int
    active_employees: int
    on_leave_employees: int
    inactive_employees: int
    departments_count: int
    by_department: List[DepartmentStat]
    request_id: Optional[str] = None

# --- Document Schemas ---
class EmployeeDocumentCreate(BaseModel):
    document_type: str = Field(..., max_length=50)
    file_name: str = Field(..., max_length=255)
    storage_key: str = Field(..., max_length=500)
    mime_type: Optional[str] = Field(None, max_length=100)
    file_size: Optional[int] = None
    expiry_date: Optional[date] = None

class EmployeeDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    employee_id: UUID
    document_type: str
    file_name: str
    storage_key: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: datetime
    verification_status: str
    expiry_date: Optional[date] = None

# --- Org Tree Schema ---
class OrgTreeNode(BaseModel):
    id: UUID
    employee_id: str
    name: str
    designation: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    direct_reports: List["OrgTreeNode"] = []

OrgTreeNode.model_rebuild()
