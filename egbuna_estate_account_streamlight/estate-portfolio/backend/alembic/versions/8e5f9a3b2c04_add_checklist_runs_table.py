"""Add checklist_runs table for F-TD-001

Revision ID: 8e5f9a3b2c04
Revises: 7d4e8f2a1c03
Create Date: 2026-07-05 10:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = '8e5f9a3b2c04'
down_revision: Union[str, None] = '7d4e8f2a1c03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'checklist_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('results_json', JSONB(), nullable=False),
        sa.Column('signoff_markdown', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_checklist_runs_admin_id'), 'checklist_runs', ['admin_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_checklist_runs_admin_id'), table_name='checklist_runs')
    op.drop_table('checklist_runs')