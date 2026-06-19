"""Add registrar requirements and documents tables

Revision ID: 5b9c3e2f4a16
Revises: 4a8f2c1d9e05
Create Date: 2026-05-05 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b9c3e2f4a16'
down_revision = '4a8f2c1d9e05'
branch_labels = None
depends_on = None


def upgrade():
    # registrar_requirements
    op.create_table(
        'registrar_requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('registrar_id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(length=200), nullable=False),
        sa.Column('document_title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['registrar_id'], ['registrars.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_registrar_requirements_registrar_id'), 'registrar_requirements', ['registrar_id'], unique=False)

    # registrar_documents
    op.create_table(
        'registrar_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('registrar_requirement_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('file_size', sa.BigInteger(), server_default='0', nullable=False),
        sa.Column('mime_type', sa.String(length=100), server_default='application/octet-stream', nullable=False),
        sa.Column('status', sa.String(length=30), server_default='pending', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending','submitted','completed','rejected')", name='chk_registrar_document_status'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['registrar_requirement_id'], ['registrar_requirements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_registrar_documents_company_id'), 'registrar_documents', ['company_id'], unique=False)
    op.create_index(op.f('ix_registrar_documents_registrar_requirement_id'), 'registrar_documents', ['registrar_requirement_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_registrar_documents_registrar_requirement_id'), table_name='registrar_documents')
    op.drop_index(op.f('ix_registrar_documents_company_id'), table_name='registrar_documents')
    op.drop_table('registrar_documents')
    
    op.drop_index(op.f('ix_registrar_requirements_registrar_id'), table_name='registrar_requirements')
    op.drop_table('registrar_requirements')
