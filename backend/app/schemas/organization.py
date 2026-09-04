from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, EmailStr

# --- Organization / Company Schemas ---
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    domain: Optional[str] = Field(None, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    timezone: str = Field("UTC", max_length=50)
    currency: str = Field("INR", max_length=10)
    date_format: str = Field("YYYY-MM-DD", max_length=20)
    fiscal_year_start: str = Field("01-01", max_length=20)

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, max_length=10)
    date_format: Optional[str] = Field(None, max_length=20)
    fiscal_year_start: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class CompanyResponse(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str
    is_active: bool

# --- Branch Schemas ---
class BranchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = Field("UTC", max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    status: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class BranchResponse(BranchBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    status: str
    is_active: bool

# --- Department Schemas ---
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    parent_department_id: Optional[UUID] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_department_id: Optional[UUID] = None
    status: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    status: str
    is_active: bool

# --- Designation Schemas ---
class DesignationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    level: int = Field(1, ge=1, le=100)

class DesignationCreate(DesignationBase):
    pass

class DesignationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    level: Optional[int] = Field(None, ge=1, le=100)
    status: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class DesignationResponse(DesignationBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    status: str
    is_active: bool
