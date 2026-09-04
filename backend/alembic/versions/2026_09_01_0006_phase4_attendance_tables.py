"""phase4_attendance_tables

Revision ID: 0006_phase4_attendance_tables
Revises: 0005_phase3_hrms_tables
Create Date: 2026-09-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0006_phase4_attendance_tables'
down_revision = '0005_phase3_hrms_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. shifts table
    op.create_table(
        'shifts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('shift_type', sa.String(50), nullable=False, server_default='FIXED'),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('grace_period_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('late_threshold_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('early_exit_threshold_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('minimum_work_minutes', sa.Integer(), nullable=False, server_default='480'),
        sa.Column('break_duration_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('is_overnight', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('tenant_id', 'code', name='idx_shift_tenant_code')
    )
    op.create_index('idx_shifts_tenant_id', 'shifts', ['tenant_id'])

    # 2. employee_shift_assignments table
    op.create_table(
        'employee_shift_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('shift_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shifts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('weekly_offs', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_esa_tenant_id', 'employee_shift_assignments', ['tenant_id'])
    op.create_index('idx_esa_emp_id', 'employee_shift_assignments', ['employee_id'])
    op.create_index('idx_esa_shift_id', 'employee_shift_assignments', ['shift_id'])

    # 3. attendances table
    op.create_table(
        'attendances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('shift_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shifts.id', ondelete='SET NULL'), nullable=True),
        sa.Column('attendance_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('first_check_in', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_check_out', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_work_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_break_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('overtime_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('late_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('early_exit_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('worked_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('attendance_source', sa.String(50), nullable=False, server_default='WEB'),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('tenant_id', 'employee_id', 'attendance_date', name='idx_att_tenant_emp_date')
    )
    op.create_index('idx_att_tenant_id', 'attendances', ['tenant_id'])
    op.create_index('idx_att_emp_id', 'attendances', ['employee_id'])
    op.create_index('idx_att_date', 'attendances', ['attendance_date'])
    op.create_index('idx_att_tenant_date', 'attendances', ['tenant_id', 'attendance_date'])
    op.create_index('idx_att_tenant_status_date', 'attendances', ['tenant_id', 'status', 'attendance_date'])

    # 4. attendance_events table
    op.create_table(
        'attendance_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attendance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('attendances.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source', sa.String(50), nullable=False, server_default='WEB'),
        sa.Column('device_reference', sa.String(255), nullable=True),
        sa.Column('location_reference', sa.String(255), nullable=True),
        sa.Column('verification_reference', sa.String(255), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    op.create_index('idx_att_event_att_id', 'attendance_events', ['attendance_id'])

    # 5. attendance_regularizations table
    op.create_table(
        'attendance_regularizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attendance_date', sa.Date(), nullable=False),
        sa.Column('requested_check_in', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requested_check_out', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('approved_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_reg_tenant_id', 'attendance_regularizations', ['tenant_id'])
    op.create_index('idx_reg_emp_id', 'attendance_regularizations', ['employee_id'])
    op.create_index('idx_reg_status', 'attendance_regularizations', ['status'])

    # 6. holidays table
    op.create_table(
        'holidays',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('branches.id', ondelete='CASCADE'), nullable=True),
        sa.Column('holiday_name', sa.String(150), nullable=False),
        sa.Column('holiday_date', sa.Date(), nullable=False),
        sa.Column('holiday_type', sa.String(50), nullable=False, server_default='COMPANY'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('tenant_id', 'branch_id', 'holiday_date', name='idx_holiday_tenant_branch_date')
    )
    op.create_index('idx_holiday_tenant_id', 'holidays', ['tenant_id'])
    op.create_index('idx_holiday_date', 'holidays', ['holiday_date'])

def downgrade() -> None:
    op.drop_table('holidays')
    op.drop_table('attendance_regularizations')
    op.drop_table('attendance_events')
    op.drop_table('attendances')
    op.drop_table('employee_shift_assignments')
    op.drop_table('shifts')
