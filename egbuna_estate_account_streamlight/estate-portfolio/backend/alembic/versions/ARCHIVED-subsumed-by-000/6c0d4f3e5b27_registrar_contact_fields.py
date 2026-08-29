"""registrar_contact_fields

Revision ID: 6c0d4f3e5b27
Revises: 5b9c3e2f4a16
Create Date: 2026-05-13 21:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c0d4f3e5b27'
down_revision = '5b9c3e2f4a16'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'registrar_contact_fields',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('registrar_id', sa.Integer(), nullable=False),
        sa.Column('field_type', sa.String(length=20), nullable=False),
        sa.Column('field_value', sa.Text(), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=True),
        sa.Column('sort_order', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['registrar_id'], ['registrars.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_registrar_contact_fields_registrar', 'registrar_contact_fields', ['registrar_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))


def downgrade() -> None:
    op.drop_index('idx_registrar_contact_fields_registrar', table_name='registrar_contact_fields', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_table('registrar_contact_fields')
