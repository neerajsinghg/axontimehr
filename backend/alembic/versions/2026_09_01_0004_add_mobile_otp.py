"""add mobile otp

Revision ID: 0004_add_mobile_otp
Revises: 0003_add_auth_user_tables
Create Date: 2026-09-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0004_add_mobile_otp'
down_revision: Union[str, None] = '0003_add_auth_user_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))
    op.create_index('idx_users_phone', 'users', ['phone_number'], unique=True)

    op.create_table(
        'mobile_otps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('otp_code', sa.String(10), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.create_index('idx_mobile_otp_phone', 'mobile_otps', ['phone_number'])

def downgrade() -> None:
    op.drop_index('idx_mobile_otp_phone', table_name='mobile_otps')
    op.drop_table('mobile_otps')
    op.drop_index('idx_users_phone', table_name='users')
    op.drop_column('users', 'phone_number')
