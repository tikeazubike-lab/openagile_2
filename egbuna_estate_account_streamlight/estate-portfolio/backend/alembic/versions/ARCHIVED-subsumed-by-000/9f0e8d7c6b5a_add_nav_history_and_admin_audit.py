"""Add nav_history and admin_audit tables for F-007

Revision ID: 9f0e8d7c6b5a
Revises: a1b2c3d4e5f6
Create Date: 2026-07-08 14:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9f0e8d7c6b5a'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'nav_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('snapshot_date', sa.Date(), unique=True, nullable=False, index=True),
        sa.Column('total_value', sa.Numeric(18, 4), nullable=False),
        sa.Column('total_cost', sa.Numeric(18, 4), nullable=False),
        sa.Column('gain_loss', sa.Numeric(18, 4), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        'admin_audit',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(50), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('performed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('admin_audit')
    op.drop_table('nav_history')
