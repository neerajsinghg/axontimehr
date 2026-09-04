"""phase3 hrms tables

Revision ID: 0005_phase3_hrms_tables
Revises: 0004_add_mobile_otp
Create Date: 2026-09-01 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0005_phase3_hrms_tables'
down_revision: Union[str, None] = '0004_add_mobile_otp'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Companies
    op.add_column('companies', sa.Column('legal_name', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('display_name', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('phone', sa.String(50), nullable=True))
    op.add_column('companies', sa.Column('website', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('address', sa.String(500), nullable=True))
    op.add_column('companies', sa.Column('city', sa.String(100), nullable=True))
    op.add_column('companies', sa.Column('state', sa.String(100), nullable=True))
    op.add_column('companies', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('companies', sa.Column('postal_code', sa.String(20), nullable=True))
    op.add_column('companies', sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'))
    op.add_column('companies', sa.Column('currency', sa.String(10), nullable=False, server_default='USD'))
    op.add_column('companies', sa.Column('date_format', sa.String(20), nullable=False, server_default='YYYY-MM-DD'))
    op.add_column('companies', sa.Column('fiscal_year_start', sa.String(20), nullable=False, server_default='01-01'))
    op.add_column('companies', sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'))

    # 2. Branches
    op.add_column('branches', sa.Column('address', sa.String(500), nullable=True))
    op.add_column('branches', sa.Column('postal_code', sa.String(20), nullable=True))
    op.add_column('branches', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('branches', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('branches', sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'))
    op.add_column('branches', sa.Column('phone', sa.String(50), nullable=True))
    op.add_column('branches', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('branches', sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'))
    op.create_index('idx_branch_tenant_code', 'branches', ['organization_id', 'code'], unique=True)

    # 3. Departments
    op.add_column('departments', sa.Column('description', sa.String(500), nullable=True))
    op.add_column('departments', sa.Column('parent_department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True))
    op.add_column('departments', sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'))
    op.create_index('idx_dept_tenant_code', 'departments', ['organization_id', 'code'], unique=True)

    # 4. Designations
    op.add_column('designations', sa.Column('description', sa.String(500), nullable=True))
    op.add_column('designations', sa.Column('level', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('designations', sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'))
    op.create_index('idx_desig_tenant_code', 'designations', ['organization_id', 'code'], unique=True)

    # 5. Users
    op.add_column('users', sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True))

    # 6. Employees
    op.add_column('employees', sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))
    op.add_column('employees', sa.Column('middle_name', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('display_name', sa.String(200), nullable=True))
    op.add_column('employees', sa.Column('gender', sa.String(20), nullable=True))
    op.add_column('employees', sa.Column('personal_email', sa.String(255), nullable=True))
    op.add_column('employees', sa.Column('personal_phone', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('emergency_contact', sa.String(500), nullable=True))
    op.add_column('employees', sa.Column('address_line1', sa.String(255), nullable=True))
    op.add_column('employees', sa.Column('address_line2', sa.String(255), nullable=True))
    op.add_column('employees', sa.Column('city', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('state', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('postal_code', sa.String(20), nullable=True))
    op.add_column('employees', sa.Column('date_of_confirmation', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('date_of_leaving', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('employee_category', sa.String(50), nullable=True, server_default='PERMANENT'))
    op.add_column('employees', sa.Column('manager_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='SET NULL'), nullable=True))
    
    op.create_index('idx_emp_desig', 'employees', ['designation_id'])
    op.create_index('idx_emp_branch', 'employees', ['branch_id'])
    op.create_index('idx_emp_manager', 'employees', ['manager_id'])
    op.create_index('idx_emp_tenant_code', 'employees', ['organization_id', 'employee_id'], unique=True)
    op.create_index('idx_emp_user', 'employees', ['user_id'], unique=True)

    # 7. Employee Documents
    op.create_table(
        'employee_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('storage_key', sa.String(500), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('verification_status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('idx_doc_emp', 'employee_documents', ['employee_id'])
    op.create_index('idx_doc_org', 'employee_documents', ['organization_id'])

    # 8. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(255), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('idx_audit_tenant', 'audit_logs', ['tenant_id'])
    op.create_index('idx_audit_actor', 'audit_logs', ['actor_id'])
    op.create_index('idx_audit_entity', 'audit_logs', ['entity_type', 'entity_id'])

def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('employee_documents')
    
    op.drop_index('idx_emp_user', table_name='employees')
    op.drop_index('idx_emp_tenant_code', table_name='employees')
    op.drop_index('idx_emp_manager', table_name='employees')
    op.drop_index('idx_emp_branch', table_name='employees')
    op.drop_index('idx_emp_desig', table_name='employees')

    op.drop_column('employees', 'manager_id')
    op.drop_column('employees', 'employee_category')
    op.drop_column('employees', 'date_of_leaving')
    op.drop_column('employees', 'date_of_confirmation')
    op.drop_column('employees', 'postal_code')
    op.drop_column('employees', 'country')
    op.drop_column('employees', 'state')
    op.drop_column('employees', 'city')
    op.drop_column('employees', 'address_line2')
    op.drop_column('employees', 'address_line1')
    op.drop_column('employees', 'emergency_contact')
    op.drop_column('employees', 'personal_phone')
    op.drop_column('employees', 'personal_email')
    op.drop_column('employees', 'gender')
    op.drop_column('employees', 'display_name')
    op.drop_column('employees', 'middle_name')
    op.drop_column('employees', 'user_id')

    op.drop_column('users', 'tenant_id')

    op.drop_index('idx_desig_tenant_code', table_name='designations')
    op.drop_column('designations', 'status')
    op.drop_column('designations', 'level')
    op.drop_column('designations', 'description')

    op.drop_index('idx_dept_tenant_code', table_name='departments')
    op.drop_column('departments', 'status')
    op.drop_column('departments', 'parent_department_id')
    op.drop_column('departments', 'description')

    op.drop_index('idx_branch_tenant_code', table_name='branches')
    op.drop_column('branches', 'status')
    op.drop_column('branches', 'email')
    op.drop_column('branches', 'phone')
    op.drop_column('branches', 'timezone')
    op.drop_column('branches', 'longitude')
    op.drop_column('branches', 'latitude')
    op.drop_column('branches', 'postal_code')
    op.drop_column('branches', 'address')

    op.drop_column('companies', 'status')
    op.drop_column('companies', 'fiscal_year_start')
    op.drop_column('companies', 'date_format')
    op.drop_column('companies', 'currency')
    op.drop_column('companies', 'timezone')
    op.drop_column('companies', 'postal_code')
    op.drop_column('companies', 'country')
    op.drop_column('companies', 'state')
    op.drop_column('companies', 'city')
    op.drop_column('companies', 'address')
    op.drop_column('companies', 'website')
    op.drop_column('companies', 'phone')
    op.drop_column('companies', 'email')
    op.drop_column('companies', 'display_name')
    op.drop_column('companies', 'legal_name')
