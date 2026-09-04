import uuid
from datetime import date
from typing import Optional, List
from sqlalchemy import String, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        Index("idx_emp_org", "organization_id"),
        Index("idx_emp_status", "status"),
        Index("idx_emp_dept", "department_id"),
        Index("idx_emp_desig", "designation_id"),
        Index("idx_emp_branch", "branch_id"),
        Index("idx_emp_manager", "manager_id"),
        Index("idx_emp_tenant_code", "organization_id", "employee_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True)
    
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Contact
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True) # Work email
    personal_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Work phone
    personal_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Dates & Status
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    date_of_confirmation: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_of_leaving: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    employment_type: Mapped[str] = mapped_column(String(50), default="FULL_TIME", nullable=False)
    employee_category: Mapped[Optional[str]] = mapped_column(String(50), default="PERMANENT", nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    designation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("designations.id", ondelete="SET NULL"), nullable=True)
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="employees")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="employee")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees")
    designation: Mapped[Optional["Designation"]] = relationship("Designation", back_populates="employees")
    branch: Mapped[Optional["Branch"]] = relationship("Branch", back_populates="employees")
    
    manager: Mapped[Optional["Employee"]] = relationship("Employee", remote_side=[id], backref="direct_reports")
    documents: Mapped[List["EmployeeDocument"]] = relationship("EmployeeDocument", back_populates="employee", cascade="all, delete-orphan")

    @property
    def designation_name(self) -> Optional[str]:
        return self.designation.name if self.designation else None
