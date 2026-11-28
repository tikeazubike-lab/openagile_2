"""Phase 3A: add price_audits table

Revision ID: 4a8f2c1d9e05
Revises: 3f4739d78390
Create Date: 2026-04-30 15:14:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4a8f2c1d9e05'
down_revision: Union[str, None] = '3f4739d78390'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'price_audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('old_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('new_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('changed_at', sa.Date(), nullable=False),
        sa.Column('changed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_price_audits_company_id', 'price_audits', ['company_id'])
    op.create_index('ix_price_audits_changed_at', 'price_audits', ['changed_at'])


def downgrade() -> None:
    op.drop_index('ix_price_audits_changed_at', table_name='price_audits')
    op.drop_index('ix_price_audits_company_id', table_name='price_audits')
    op.drop_table('price_audits')
