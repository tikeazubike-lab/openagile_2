"""Make admin_audit.performed_by nullable for automated audit entries

Revision ID: b0c1d2e3f4a5
Revises: 9f0e8d7c6b5a
Create Date: 2026-07-15 18:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b0c1d2e3f4a5'
down_revision: Union[str, None] = '9f0e8d7c6b5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('admin_audit', 'performed_by',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade() -> None:
    op.alter_column('admin_audit', 'performed_by',
                    existing_type=sa.Integer(),
                    nullable=False)
